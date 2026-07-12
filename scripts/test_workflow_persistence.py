#!/usr/bin/env python3
from __future__ import annotations
import json, os, sys, tempfile, unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import workflow_state as state
import run_behavioral_evals as runner

class WorkflowPersistenceTests(unittest.TestCase):
    def metadata(self, owner, pid, host, age=0):
        return {"schema_version":1,"owner_id":owner,"pid":pid,"hostname":host,"created_at":(datetime.now(timezone.utc)-timedelta(seconds=age)).isoformat()}
    def test_lock_metadata_and_normal_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            workflow=Path(tmp)/'.ai-workflow'
            with state.state_lock(workflow) as info:
                metadata=json.loads((workflow/'.state.lock'/state.LOCK_METADATA).read_text())
                self.assertEqual(info['owner_id'],metadata['owner_id'])
            self.assertFalse((workflow/'.state.lock').exists())
    def test_active_and_different_host_locks_are_not_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            workflow=Path(tmp)/'.ai-workflow'; lock=workflow/'.state.lock'; lock.mkdir(parents=True)
            state.atomic_write(lock/state.LOCK_METADATA,json.dumps(self.metadata('other',os.getpid(),__import__('socket').gethostname(),1000)))
            with self.assertRaises(state.LockTimeoutError):
                with state.state_lock(workflow,timeout_seconds=.01): pass
            self.assertTrue(lock.exists())
            state.atomic_write(lock/state.LOCK_METADATA,json.dumps(self.metadata('other',999999,'different-host',1000)))
            with self.assertRaises(state.LockTimeoutError):
                with state.state_lock(workflow,timeout_seconds=.01): pass
            self.assertTrue(lock.exists())
    def test_confirmed_stale_lock_recovers_and_owner_mismatch_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            workflow=Path(tmp)/'.ai-workflow'; lock=workflow/'.state.lock'; lock.mkdir(parents=True)
            state.atomic_write(lock/state.LOCK_METADATA,json.dumps(self.metadata('dead',999999,__import__('socket').gethostname(),state.MIN_STALE_LOCK_AGE_SECONDS+1)))
            with state.state_lock(workflow,timeout_seconds=.1,pid_exists=lambda _:False) as info:
                self.assertTrue(info['stale_lock_recovered'])
            lock.mkdir(); state.atomic_write(lock/state.LOCK_METADATA,json.dumps(self.metadata('other',999999,__import__('socket').gethostname(),0)))
            state._release_owned_lock(lock,'not-owner')
            self.assertTrue(lock.exists())
    def test_optional_timeout_and_artifact_failure_preserve_primary_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(state,'update_state',side_effect=state.LockTimeoutError('x')):
                outcome=state.persist_state_optional(Path(tmp),'security-audit',{'status':'completed'})
            self.assertFalse(outcome.succeeded); self.assertEqual('lock_timeout',outcome.status); self.assertNotIn(str(Path(tmp)),outcome.safe_message or '')
        case=next(item for item in runner.load_cases() if item['id']=='security-audit-workflow-handoff-001')
        with patch.object(runner,'atomic_write',side_effect=PermissionError()):
            result=runner.evaluate(case,'contract')
        self.assertEqual('passed',result['status']); self.assertFalse(result['layers']['persistence']['succeeded'])

if __name__=='__main__': unittest.main(verbosity=2)
