#!/usr/bin/env python3
"""Optional, ownership-safe local persistence for `.ai-workflow` state."""
from __future__ import annotations

import json
import os
import shutil
import socket
import tempfile
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator


LOCK_WAIT_SECONDS = 5.0
LOCK_POLL_SECONDS = 0.05
MIN_STALE_LOCK_AGE_SECONDS = 30.0
LEGACY_STALE_LOCK_AGE_SECONDS = 300.0
LOCK_METADATA = "owner.json"


class LockTimeoutError(TimeoutError):
    """A bounded optional persistence lock could not be acquired."""


class WorkflowPersistenceError(RuntimeError):
    """A safe persistence-only failure."""


@dataclass(frozen=True)
class PersistenceOutcome:
    attempted: bool
    succeeded: bool
    status: str
    reason_code: str | None = None
    safe_message: str | None = None
    stale_lock_recovered: bool = False


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
        temporary = Path(handle.name)
    try:
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _metadata(owner_id: str) -> dict[str, Any]:
    return {"schema_version": 1, "owner_id": owner_id, "pid": os.getpid(), "hostname": socket.gethostname(), "created_at": _utc_now().isoformat()}


def _read_metadata(lock: Path) -> dict[str, Any] | None:
    try:
        value = json.loads((lock / LOCK_METADATA).read_text(encoding="utf-8"))
        if not isinstance(value, dict) or value.get("schema_version") != 1 or not isinstance(value.get("owner_id"), str) or not isinstance(value.get("pid"), int) or not isinstance(value.get("hostname"), str) or not isinstance(value.get("created_at"), str):
            return None
        datetime.fromisoformat(value["created_at"].replace("Z", "+00:00"))
        return value
    except (OSError, ValueError, json.JSONDecodeError):
        return None


def _age_seconds(lock: Path, metadata: dict[str, Any] | None, now: datetime) -> float | None:
    try:
        if metadata:
            created = datetime.fromisoformat(metadata["created_at"].replace("Z", "+00:00"))
            return max(0.0, (now - created).total_seconds())
        return max(0.0, now.timestamp() - lock.stat().st_mtime)
    except (OSError, ValueError, TypeError):
        return None


def _pid_exists(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        # `os.kill(pid, 0)` is not a POSIX-style probe on Windows. Treat
        # unknown PIDs as active; callers can inject a platform-specific probe
        # where supported, and safety wins over automatic recovery.
        return pid == os.getpid()
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return True
    return True


def _quarantine(lock: Path, suffix: str) -> Path | None:
    candidate = lock.parent / f".state.lock.{suffix}.{uuid.uuid4().hex}"
    try:
        os.replace(lock, candidate)
        return candidate
    except OSError:
        return None


def _recover_stale_lock(lock: Path, *, now: datetime, hostname: str, pid_exists: Callable[[int], bool]) -> bool:
    """Recover only dead, old same-host locks or very old legacy locks."""
    metadata = _read_metadata(lock)
    age = _age_seconds(lock, metadata, now)
    if age is None:
        return False
    confirmed_dead = metadata and metadata["hostname"] == hostname and age >= MIN_STALE_LOCK_AGE_SECONDS and not pid_exists(metadata["pid"])
    legacy = metadata is None and age >= LEGACY_STALE_LOCK_AGE_SECONDS
    if not confirmed_dead and not legacy:
        return False
    quarantined = _quarantine(lock, "recovered")
    if quarantined is None:
        return False
    # Re-check after the atomic claim. Never delete a lock that changed owners.
    claimed = _read_metadata(quarantined)
    if confirmed_dead and (not claimed or claimed.get("owner_id") != metadata.get("owner_id")):
        try:
            os.replace(quarantined, lock)
        except OSError:
            pass
        return False
    if legacy and claimed is not None:
        try:
            os.replace(quarantined, lock)
        except OSError:
            pass
        return False
    shutil.rmtree(quarantined, ignore_errors=True)
    return True


def _release_owned_lock(lock: Path, owner_id: str) -> None:
    quarantined = _quarantine(lock, "release")
    if quarantined is None:
        return
    metadata = _read_metadata(quarantined)
    if metadata and metadata.get("owner_id") == owner_id:
        shutil.rmtree(quarantined, ignore_errors=True)
        return
    # Another owner replaced metadata: restore rather than deleting it.
    try:
        if not lock.exists():
            os.replace(quarantined, lock)
    except OSError:
        pass


@contextmanager
def state_lock(workflow_dir: Path, timeout_seconds: float = LOCK_WAIT_SECONDS, *, now: Callable[[], datetime] = _utc_now, pid_exists: Callable[[int], bool] = _pid_exists) -> Iterator[dict[str, Any]]:
    """Acquire a bounded local advisory lock with conservative stale recovery."""
    lock = workflow_dir / ".state.lock"
    deadline = time.monotonic() + timeout_seconds
    owner_id = uuid.uuid4().hex
    recovered = False
    workflow_dir.mkdir(parents=True, exist_ok=True)
    while True:
        try:
            lock.mkdir()
            try:
                atomic_write(lock / LOCK_METADATA, json.dumps(_metadata(owner_id), sort_keys=True) + "\n")
            except OSError:
                _release_owned_lock(lock, owner_id)
                raise WorkflowPersistenceError("lock metadata could not be written") from None
            break
        except FileExistsError:
            if not recovered:
                recovered = _recover_stale_lock(lock, now=now(), hostname=socket.gethostname(), pid_exists=pid_exists)
                if recovered:
                    continue
            if time.monotonic() >= deadline:
                raise LockTimeoutError("workflow persistence lock unavailable")
            time.sleep(LOCK_POLL_SECONDS)
    try:
        yield {"owner_id": owner_id, "stale_lock_recovered": recovered}
    finally:
        _release_owned_lock(lock, owner_id)


def _initial_state() -> dict[str, Any]:
    return {"schema_version": "1.0", "project": {"name": None, "repository_root": "."}, "runs": {}}


def update_state(workflow_dir: Path, skill: str, run: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    """Atomically update one run; callers decide whether failure is optional."""
    state_file = workflow_dir / "state.json"
    with state_lock(workflow_dir) as lock_info:
        state = _initial_state()
        invalid = False
        if state_file.exists():
            try:
                loaded = json.loads(state_file.read_text(encoding="utf-8"))
                if not isinstance(loaded, dict) or not isinstance(loaded.get("runs", {}), dict):
                    raise ValueError("unsupported state shape")
                state = loaded
            except (OSError, ValueError, json.JSONDecodeError):
                invalid = True
                backup = workflow_dir / f"state.invalid-{_utc_now().strftime('%Y%m%dT%H%M%SZ')}.json"
                shutil.copy2(state_file, backup)
        runs = dict(state.get("runs", {})); runs[skill] = run; state["runs"] = runs; state.setdefault("schema_version", "1.0")
        atomic_write(state_file, json.dumps(state, indent=2, sort_keys=True) + "\n")
        return state, bool(lock_info["stale_lock_recovered"] or invalid)


def persist_state_optional(workflow_dir: Path, skill: str, run: dict[str, Any]) -> PersistenceOutcome:
    """Turn persistence-only failures into safe status metadata for callers."""
    try:
        _, recovered_or_invalid = update_state(workflow_dir, skill, run)
        return PersistenceOutcome(True, True, "stale_lock_recovered" if recovered_or_invalid else "persisted", stale_lock_recovered=recovered_or_invalid)
    except LockTimeoutError:
        return PersistenceOutcome(True, False, "lock_timeout", "lock_timeout", "Workflow persistence is temporarily unavailable; primary result was returned.")
    except PermissionError:
        return PersistenceOutcome(True, False, "permission_denied", "permission_denied", "Workflow persistence is unavailable; primary result was returned.")
    except (OSError, TypeError, ValueError, json.JSONDecodeError, WorkflowPersistenceError):
        return PersistenceOutcome(True, False, "unavailable", "persistence_io_or_state_error", "Workflow persistence is unavailable; primary result was returned.")
