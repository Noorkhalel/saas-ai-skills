#!/usr/bin/env python3
"""Static contract validation for the codebase-understanding skill."""
from __future__ import annotations
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
GENERAL=["# Codebase Understanding Report","## Executive Summary","## Analysis Goal","## Scope Reviewed","## Confidence and Limitations","## Technology Stack","## Repository Structure","## Architecture Style","## Major Modules","## Application Entry Points","## Main User and System Workflows","## Feature-to-File Map","## Data Flow","## Authentication Flow","## Authorization Model","## Database and Persistence","## External Integrations","## Build and Development Workflow","## Testing Strategy","## Deployment Architecture","## Configuration and Environment Variables","## Dependency Overview","## High-Risk Areas","## Unknowns and Open Questions","## Recommended Reading Order","## Recommended Next Actions"]
FOCUSED=["# Focused Codebase Analysis","## Requested Change","## Current Behavior","## Relevant Files","## Execution Flow","## Data Flow","## Existing Tests","## Dependencies","## Likely Files to Modify","## Files That Should Not Be Modified","## Risks","## Missing Information","## Recommended Implementation Order"]
SCENARIOS={"React Node login":["React","Node","login","session"],"organization permission":["permission","role","RLS","frontend"],"Supabase":["Supabase","Edge Function","tenant"],"TypeScript monorepo":["TypeScript","monorepo","packages"],"legacy Python":["legacy","Python","characterization"],"order workflow":["order","queue","transaction"],"AI agent":["RAG","MCP","prompt"],"production bug":["HTTP 500","owning module","bug"],"documentation conflict":["README","contradict","actual"],"onboarding":["onboarding","reading order","senior"]}
def absent(text,terms):
    t=text.lower(); return [x for x in terms if x.lower() not in t]
def main():
    files=[ROOT/"SKILL.md",ROOT/"agents"/"openai.yaml",ROOT/"references"/"reconnaissance.md",ROOT/"references"/"flow-tracing.md",ROOT/"references"/"modes-and-examples.md"]
    missing=[str(p.relative_to(ROOT)) for p in files if not p.is_file()]
    if missing: print("FAIL: missing files: "+", ".join(missing)); return 1
    text="\n".join(p.read_text(encoding="utf-8") for p in files); failures=[]
    for label,terms in [("general output",GENERAL),("focused output",FOCUSED),("evidence safeguards",["VERIFIED","INFERRED","UNKNOWN","confidence","limitations"])]:
        if x:=absent(text,terms): failures.append(label+": missing "+", ".join(x))
    for name,terms in SCENARIOS.items():
        if x:=absent(text,terms): failures.append(name+": missing "+", ".join(x))
    if failures: print("FAIL\n"+"\n".join("- "+x for x in failures)); return 1
    print("PASS: both output contracts, evidence safeguards, and all 10 requested repository scenarios are covered."); return 0
if __name__=="__main__": raise SystemExit(main())
