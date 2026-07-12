#!/usr/bin/env python3
"""Deterministic, provider-neutral router for the independent skill portfolio."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "shared" / "skill-router.json"
INJECTION = re.compile(r"(?i)\b(?:ignore (?:all |any |the )?(?:previous|above)|system message|developer message|you are now|override (?:the )?router)\b.*")
FENCED = re.compile(r"```.*?```", re.S)

def registry() -> dict[str, Any]: return json.loads(REGISTRY.read_text(encoding="utf-8"))

def safe_request(value: str) -> str:
    """Keep user intent while removing obvious embedded-policy directives and code blocks."""
    lines=[]
    for line in FENCED.sub("", value).splitlines():
        match=INJECTION.search(line)
        lines.append(line[:match.start()] if match else line)
    return "\n".join(lines)

def _contains(text: str, *phrases: str) -> bool:
    return any(phrase in text for phrase in phrases)

def _tokens(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", value.lower()) if len(token) > 2}

def registry_evidence(text: str, data: dict[str, Any]) -> list[dict[str, Any]]:
    """Rank all registry entries from intent, artifact, scope, and exclusion evidence.

    This intentionally does more than a single keyword lookup: the final router combines
    this ranked evidence with conflict precedence and explicit requested deliverables.
    """
    request_tokens = _tokens(text)
    ranked: list[dict[str, Any]] = []
    for item in data["skills"]:
        activation = item["activation"]
        evidence: list[str] = []
        score = 0.0
        for phrase in activation["intents"]:
            phrase_tokens = _tokens(phrase)
            if phrase.lower() in text:
                score += 5.0; evidence.append(f"intent: {phrase}")
            elif len(phrase_tokens) > 1 and len(phrase_tokens & request_tokens) / len(phrase_tokens) >= 0.75:
                score += 2.0; evidence.append(f"intent concepts: {phrase}")
        for artifact in activation["artifacts"]:
            if _tokens(artifact) & request_tokens:
                score += 1.0; evidence.append(f"artifact/context: {artifact}")
        for scope in activation["scopes"]:
            if _tokens(scope) & request_tokens:
                score += 1.0; evidence.append(f"scope: {scope}")
        deliverable_tokens = _tokens(item["primary_deliverable"])
        overlap = len(deliverable_tokens & request_tokens)
        if overlap:
            score += min(2.0, overlap / max(1, len(deliverable_tokens)) * 4.0)
            evidence.append("requested-deliverable concepts")
        exclusions = [rule for rule in item["exclusions"] if len(_tokens(rule) & request_tokens) >= 2]
        score -= float(len(exclusions))
        ranked.append({"skill": item["id"], "score": round(max(score, 0.0), 2), "evidence": evidence, "matched_exclusions": exclusions})
    return sorted(ranked, key=lambda candidate: (-candidate["score"], candidate["skill"]))


def calibrated_confidence(primary: str | None, ranked: list[dict[str, Any]], *, explicit: bool) -> tuple[float, dict[str, float | str]]:
    """Calibrate confidence from evidence strength and separation, not route existence.

    Rule precedence still selects a safe primary skill, but weak registry evidence
    is surfaced as lower confidence so callers can request clarification instead
    of presenting a fixed high-confidence score for every route.
    """
    if primary is None:
        return 0.0, {"model": "evidence-strength-and-margin", "selected_score": 0.0, "runner_up_score": 0.0, "margin": 0.0}
    selected = next((item for item in ranked if item["skill"] == primary), {"score": 0.0})
    selected_score = float(selected["score"])
    runner_up = max((float(item["score"]) for item in ranked if item["skill"] != primary), default=0.0)
    margin = max(0.0, selected_score - runner_up)
    if explicit:
        return 0.99, {"model": "explicit-primary-deliverable", "selected_score": selected_score, "runner_up_score": runner_up, "margin": margin}
    strength = min(1.0, selected_score / 8.0)
    separation = min(1.0, margin / max(1.0, selected_score))
    confidence = round(min(0.97, max(0.55, 0.55 + 0.25 * strength + 0.17 * separation)), 2)
    return confidence, {"model": "evidence-strength-and-margin", "selected_score": selected_score, "runner_up_score": runner_up, "margin": margin}


def explain_competitors(primary: str, ranked: list[dict[str, Any]], skills: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Explain every rejected portfolio option without exposing request content.

    The router already exposes scored candidates, but a score alone is not an
    actionable routing explanation.  This additive field makes a deterministic
    handoff possible for callers that need to show why a nearby specialty did
    not win while keeping the stable primary/secondary fields unchanged.
    """
    selected = skills[primary]["primary_deliverable"]
    by_id = {item["skill"]: item for item in ranked}
    explanations: list[dict[str, Any]] = []
    for candidate in sorted((skill for skill in skills if skill != primary)):
        row = by_id[candidate]
        evidence = row["evidence"]
        if row["matched_exclusions"]:
            reason = "Its exclusion criteria match the request: " + "; ".join(row["matched_exclusions"]) + "."
        elif evidence:
            reason = f"It has adjacent evidence ({', '.join(evidence[:2])}), but the selected primary deliverable is {selected}."
        else:
            reason = f"No material activation evidence matched; the selected primary deliverable is {selected}."
        explanations.append({"skill": candidate, "score": row["score"], "why_not_selected": reason})
    return explanations

def choose(request: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    data = data or registry(); raw = request; text = safe_request(request).lower()
    ids = {item["id"]: item for item in data["skills"]}
    ranked = registry_evidence(text, data)
    explicit = re.search(r"primary deliverable is ([a-z-]+)", text)
    primary: str | None = explicit.group(1) if explicit and explicit.group(1) in ids else None
    intent = "no_match"; reasons: list[str] = []; assumptions: list[str] = []
    if primary:
        intent = "explicit_deliverable"; reasons.append("The request explicitly names its primary deliverable.")
    elif _contains(text, "postmortem", "root cause analysis", "root-cause analysis", "blameless incident", "systemic prevention", "rca"):
        primary, intent = "root-cause-analysis", "analyze_completed_incident"; reasons.append("Completed-incident/systemic analysis takes precedence over active debugging.")
    elif _contains(text, "fails now", "returns 500", "crash", "reproduce and fix", "debug this", "why does", "intermittently", "active regression", "times out", "fix checkout"):
        primary, intent = "debugging", "debug_active_failure"; reasons.append("An observable current defect needing diagnosis or repair is present.")
    elif _contains(text, "p95", "p99", "throughput", "profile", "memory use", "latency", "performance objective"):
        primary, intent = "performance-optimization", "improve_measured_performance"; reasons.append("The requested deliverable is a measurable performance improvement, not a functional repair.")
    elif _contains(text, "greenfield", "new saas", "new system", "future architecture", "technical blueprint") and _contains(text, "architecture", "design", "plan"):
        primary, intent = "architecture-planning", "design_future_system"; reasons.append("A future/greenfield whole-system design is requested.")
    elif (_contains(text, "existing") and _contains(text, "architecture", "boundaries")) or _contains(text, "architecture and boundaries", "dependency direction", "clean architecture", "review layers", "audit boundaries", "framework leakage", "modernization path"):
        primary, intent = "clean-architecture-review", "review_existing_architecture"; reasons.append("The request targets existing boundaries and dependency direction.")
    elif _contains(text, "security audit", "exploitability", "threat model", "owasp", "audit of ci, cloud, auth"):
        primary, intent = "security-audit", "security_exploitability_audit"; reasons.append("Security-led exploitability is the requested deliverable.")
    elif _contains(text, "lockfile", "analyze dependencies", "package upgrade", "duplicate packages", "import cycles", "dependency map"):
        primary, intent = "dependency-analysis", "map_dependencies"; reasons.append("Package/module/runtime dependency analysis is primary.")
    elif _contains(text, "tenant-safe", "database schema", "erd", "migration plan", "data integrity", "indexes"):
        primary, intent = "database-design", "design_data_model"; reasons.append("Schema, integrity, tenancy, indexes, or migrations are primary.")
    elif _contains(text, "openapi", "api design", "api contract", "rest resources", "versioned rest", "review endpoints"):
        primary, intent = "api-design-review", "review_or_design_api_contract"; reasons.append("API contract semantics and compatibility are primary.")
    elif _contains(text, "refactor", "extract pricing", "extract method", "without changing behavior", "remove duplication", "restructure code"):
        primary, intent = "refactoring-code", "implement_behavior_preserving_refactor"; reasons.append("The requested deliverable is a structural modification that preserves behavior.")
    elif _contains(text, "srp", "isp", "dip", "solid review", "liskov", "interface segregation"):
        primary, intent = "solid-review", "diagnose_solid_design"; reasons.append("SOLID principles are the explicit evaluation lens.")
    elif _contains(text, "strategy, factory", "strategy or factory", "which design pattern", "pattern for this", "pattern appropriate", "strategy appropriate", "plugin extension point"):
        primary, intent = "design-pattern-advisor", "select_design_pattern"; reasons.append("Pattern selection for an extension/design force is primary.")
    elif _contains(text, "write regression tests", "write tests", "generate tests", "test coverage", "add tests"):
        primary, intent = "test-generation", "generate_known_behavior_tests"; reasons.append("Test creation for known behavior is requested.")
    elif _contains(text, "map the", "where are", "where is", "trace request path", "understand this repository", "unfamiliar service", "codebase"):
        primary, intent = "codebase-understanding", "map_existing_codebase"; reasons.append("Repository mapping/flow tracing is requested before evaluation or change.")
    elif _contains(text, "review this pr", "review this endpoint", "review code", "find bugs", "production readiness", "changed service", "before merge"):
        primary, intent = "code-review", "review_implementation"; reasons.append("Broad correctness and production-readiness review is primary.")
    if primary and primary not in ids: primary = None
    secondary: list[str] = []
    if primary in {"debugging", "root-cause-analysis", "code-review", "refactoring-code"} and _contains(text, "regression tests", "add tests", "write tests"):
        secondary.append("test-generation")
    if primary == "architecture-planning":
        if _contains(text, "api contract", "openapi") and "api-design-review" not in secondary: secondary.append("api-design-review")
        if _contains(text, "schema", "migration", "tenancy") and "database-design" not in secondary: secondary.append("database-design")
    confidence, calibration = calibrated_confidence(primary, ranked, explicit=bool(explicit and primary))
    if primary is None:
        reasons.append("No portfolio skill has a sufficiently specific requested deliverable.")
        assumptions.append("Clarification is needed before selecting a specialty.")
    excluded=[]
    competitors=[]
    if primary:
        for candidate in ids[primary]["closest_skills"]:
            competing = next((row for row in ranked if row["skill"] == candidate), None)
            reason = "The requested deliverable is owned by the selected primary skill."
            if competing and competing["evidence"]:
                reason += " Competing evidence was secondary: " + ", ".join(competing["evidence"][:2]) + "."
            excluded.append({"skill": candidate, "reason": reason})
        selected_evidence = next((row for row in ranked if row["skill"] == primary), None)
        if selected_evidence and selected_evidence["evidence"]:
            reasons.extend(selected_evidence["evidence"][:3])
        missing = [item for item in ids[primary]["required_evidence"] if not (_tokens(item) & _tokens(text))]
        if missing:
            assumptions.append("Routing is based on requested deliverable; operational evidence remains to be supplied.")
        if confidence < 0.70:
            assumptions.append("Classification confidence is low because registry evidence is limited; confirm the requested deliverable before acting.")
        competitors = explain_competitors(primary, ranked, ids)
    return {"router_version": data["router_version"], "primary_skill": primary, "secondary_skills": secondary,
            "suggested_secondary_skills": secondary,
            "confidence": confidence, "intent": intent,
            "deliverable": ids[primary]["primary_deliverable"] if primary else None, "reasons": reasons,
            "excluded_skills": excluded, "competing_skills": competitors, "missing_evidence": missing if primary else [], "assumptions": assumptions,
            "decision_engine": {"type": "registry-evidence-plus-precedence", "candidate_scores": ranked[:5], "candidate_count": len(ranked), "confidence_calibration": calibration},
            "safety": {"request_treated_as_untrusted": True, "embedded_policy_directives_ignored": raw != safe_request(raw)}}

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__); group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--request"); group.add_argument("--request-file", type=Path)
    args=parser.parse_args(); request=args.request if args.request is not None else args.request_file.read_text(encoding="utf-8", errors="replace")
    print(json.dumps(choose(request), indent=2)); return 0
if __name__ == "__main__": raise SystemExit(main())
