#!/usr/bin/env python3
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from replay_workflow import replay


class WorkflowReplayTests(unittest.TestCase):
    def _make(self) -> Path:
        root = Path(tempfile.mkdtemp()); workflow = root / ".ai-workflow"; (workflow / "artifacts").mkdir(parents=True); (workflow / "handoffs").mkdir()
        (workflow / "artifacts" / "debugging.md").write_text("safe artifact", encoding="utf-8")
        handoff = {"schema_version":"1.0","source_skill":"debugging","run_status":"completed","summary":"safe","topics":["bugs"],"findings":[],"decisions":[],"open_questions":[],"recommended_actions":[],"recommended_next_skills":[],"full_output_file":".ai-workflow/artifacts/debugging.md"}
        (workflow / "handoffs" / "debugging.json").write_text(json.dumps(handoff), encoding="utf-8")
        (workflow / "state.json").write_text(json.dumps({"schema_version":"1.0","runs":{"debugging":{"status":"completed","artifact_file":".ai-workflow/artifacts/debugging.md","handoff_file":".ai-workflow/handoffs/debugging.json"}}}), encoding="utf-8")
        return workflow
    def test_valid_workflow_replays_without_execution(self) -> None:
        self.assertTrue(replay(self._make())["valid"])
    def test_unsafe_artifact_path_is_rejected(self) -> None:
        workflow = self._make(); state = json.loads((workflow / "state.json").read_text(encoding="utf-8")); state["runs"]["debugging"]["artifact_file"] = "../outside.md"; (workflow / "state.json").write_text(json.dumps(state), encoding="utf-8")
        self.assertFalse(replay(workflow)["valid"])


if __name__ == "__main__": unittest.main(verbosity=2)
