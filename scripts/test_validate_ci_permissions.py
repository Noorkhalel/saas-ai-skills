#!/usr/bin/env python3
from __future__ import annotations
import sys, unittest, yaml
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import validate_ci

POLICY={"default_permissions":{"contents":"read"},"exceptions":[]}
class PermissionPolicyTests(unittest.TestCase):
    def errors(self, doc): return validate_ci.validate_workflow('fixture.yml',doc,POLICY)
    def test_valid_and_empty_permissions(self):
        self.assertEqual([],self.errors({'on':{'workflow_dispatch':None},'permissions':{'contents':'read'},'jobs':{'test':{'runs-on':'ubuntu'}}}))
        self.assertEqual([],self.errors({'on':{'workflow_dispatch':None},'permissions':{},'jobs':{'test':{'runs-on':'ubuntu'}}}))
    def test_unapproved_and_broad_permissions_fail(self):
        self.assertTrue(self.errors({'permissions':{'contents':'read','issues':'write'},'jobs':{'test':{}}}))
        self.assertTrue(self.errors({'permissions':'write-all','jobs':{'test':{}}}))
        self.assertTrue(self.errors({'permissions':{'contents':'read'},'jobs':{'test':{'permissions':{'contents':'read','id-token':'write'}}}}))
    def test_exact_exception_and_unsafe_event_rules(self):
        policy={"default_permissions":{"contents":"read"},"exceptions":[{"workflow":"release.yml","job":"publish","permission":"packages","access":"write","justification":"publish"}]}
        document={'on':{'workflow_dispatch':None},'permissions':{'contents':'read'},'jobs':{'publish':{'permissions':{'contents':'read','packages':'write'}}}}
        self.assertEqual([],validate_ci.validate_workflow('release.yml',document,policy))
        self.assertTrue(validate_ci.validate_workflow('unsafe.yml',{True:{'pull_request_target':None},'permissions':{'contents':'write'},'jobs':{'test':{}}},POLICY))
    def test_yaml_alias_permissions_are_resolved_structurally(self):
        document=yaml.safe_load('permissions: &safe\n  contents: read\njobs:\n  test:\n    permissions: *safe\n')
        self.assertEqual([],self.errors(document))

if __name__=='__main__': unittest.main(verbosity=2)
