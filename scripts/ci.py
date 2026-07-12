#!/usr/bin/env python3
"""Repository-native validation command dispatcher (no Node runtime required)."""
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COMMANDS={
 "validate":["validate_repository.py","validate_markdown.py","validate_serialized.py","validate_versions.py","generate_skill_catalog.py --check","validate_framework.py","sync_base_framework.py --check","sync_workflow_contract.py --check","validate_workflow_integration.py","validate_package_conventions.py","sync_skills_lock.py --check","generate_behavioral_cases.py --check","generate_report_schemas.py --check","validate_report_schemas.py","generate_reference_catalog.py --check","validate_reference_freshness.py","validate_routing.py","run_static_evals.py","validate_security_evals.py","test_security_redaction.py","test_evaluation_context.py","test_mutation_regression.py","test_workflow_persistence.py","test_workflow_replay.py","test_validate_ci_permissions.py","mutation_regression.py","package_check.py","validate_ci.py"],
 "validate:framework":["validate_framework.py","sync_base_framework.py --check"],
 "validate:routing":["validate_routing.py"],
 "eval:static":["run_static_evals.py"],
 "eval:deterministic":["run_deterministic_evals.py --adapter mock","validate_report_schemas.py","validate_reference_freshness.py"],
 "eval:composition":["run_composition_evals.py"],
 "package:check":["package_check.py"],
 "catalog":["generate_skill_catalog.py --check"],
}
def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument('command',choices=[*COMMANDS,'eval:all','eval:behavioral']); args=parser.parse_args()
    if args.command=='eval:behavioral': print('DEPRECATED: eval:behavioral is an alias for deterministic routing/contract/context evaluations; use eval:deterministic.')
    command='eval:deterministic' if args.command=='eval:behavioral' else args.command
    items=COMMANDS['eval:static']+COMMANDS['eval:deterministic']+COMMANDS['eval:composition'] if command=='eval:all' else COMMANDS[command]
    for item in items:
        result=subprocess.run([sys.executable,'scripts/'+item.split()[0],*item.split()[1:]],cwd=ROOT)
        if result.returncode: return result.returncode
    return 0
if __name__=='__main__': raise SystemExit(main())
