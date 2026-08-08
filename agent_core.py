"""
agent_core.py -- OmniBrain E.R.I.S. Core Logic
"""
import json
import re
import datetime
import copy
from collections import Counter

_generate_fn = None

def configure(generate_fn):
    global _generate_fn
    _generate_fn = generate_fn

def _call_llm(prompt: str) -> str:
    return _generate_fn(prompt).text

def safe_json_parse(text: str) -> dict:
    text = text.strip().strip("```json").strip("```").strip()
    start = text.find('{')
    end = text.rfind('}') + 1
    if start != -1 and end != 0:
        try:
            return json.loads(text[start:end])
        except Exception:
            pass
    # Fallback if no brackets are found or parsing fails
    return json.loads(text)

class MemoryEvent: ADDED = "MEMORY_ADDED"
_event_handlers = {}
def on(event, handler): _event_handlers.setdefault(event, []).append(handler)
def emit(event, payload):
    for h in _event_handlers.get(event, []): h(payload)

STOPWORDS = {"the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "is", "are", "this", "that"}

def extract_keywords(text: str, top_n=6):
    words = [w.strip('.,!?()[]:;"\'').lower() for w in (text or "").split()]
    words = [w for w in words if len(w) > 3 and w not in STOPWORDS]
    return [w for w, _ in Counter(words).most_common(top_n)]

def structured_retrieve(memories: list[dict], window_days: int = 7):
    cutoff = datetime.date.today() - datetime.timedelta(days=window_days)
    recent = [copy.deepcopy(m) for m in memories if datetime.date.fromisoformat(m.get("date", str(datetime.date.today()))) >= cutoff]
    
    for m in recent:
        m["_concepts"] = [c.lower() for c in m.get("concepts", [])]
        m["_keywords"] = extract_keywords((m.get("summary", "") or "") + " " + (m.get("title", "") or ""))
    
    all_concepts = Counter(c for m in recent for c in m["_concepts"])
    focus_concepts = [w for w, c in all_concepts.most_common(6) if c >= 1]
    
    scored = []
    for m in recent:
        c_overlap = len(set(m["_concepts"]) & set(focus_concepts))
        k_overlap = len(set(m["_keywords"]) & set(focus_concepts))
        score = (3 * c_overlap) + (1 * k_overlap) + 1
        scored.append({**m, "_score": score, "_reason": f"Semantic Match {score} (Concepts: {c_overlap}, KWs: {k_overlap})"})
    scored.sort(key=lambda x: -x["_score"])
    return scored, focus_concepts

def assess_confidence(critic_result: dict) -> dict:
    n = len(critic_result.get("issues", []))
    if n == 0: return {"level": "High", "needs_approval": False, "reason": "No hallucinations detected"}
    elif n <= 2: return {"level": "Medium", "needs_approval": True, "reason": f"{n} unsupported claims corrected"}
    else: return {"level": "Low", "needs_approval": True, "reason": "High hallucination rate. Manual review needed."}

def perception_scan(new_memory: dict) -> list[dict] | None:
    prompt = f"""Perception Agent: Scan this environmental report for urgent compliance deadlines or hazard review dates.
Return JSON only: {{"found": true/false, "items": [{{"description": "...", "date": "..."}}]}}
Report: {new_memory.get('title')} -- {new_memory.get('summary')}"""
    try:
        parsed = safe_json_parse(_call_llm(prompt))
        if parsed.get("found") and parsed.get("items"): return parsed["items"]
    except Exception: pass
    return None

def plan(context: str) -> dict:
    prompt = f"""Planning Agent: Produce an Environmental Remediation Plan in JSON only.
Use ONLY the reports below. Include 'evidence' mapping tasks to Report Titles.
{{"goal": "...", "tasks": ["..."], "evidence": {{"Task Name": ["Report Title"]}}, "missing": [...]}}
Reports:\n{context}"""
    return safe_json_parse(_call_llm(prompt))

def critic_and_reflect(draft_json: dict, context: str) -> dict:
    prompt = f"""Critic Agent: Check the Remediation DRAFT against the SOURCE reports.
Return JSON only: {{"issues": ["list of hallucinations"], "improvement": "one suggestion"}}
SOURCE:\n{context}\nDRAFT:\n{json.dumps(draft_json)}"""
    result = safe_json_parse(_call_llm(prompt))
    result["confidence"] = assess_confidence(result)
    return result

def finalize(draft_json: dict, critic_result: dict) -> str:
    prompt = f"""Finalizer Agent: Combine the PLAN and CRITIC FEEDBACK into a formal Environmental Remediation Roadmap.
PLAN:\n{json.dumps(draft_json)}\nCRITIC:\n{json.dumps(critic_result)}"""
    return _call_llm(prompt)

def generate_roadmap(memories: list[dict], window_days: int = 7) -> dict:
    scored, focus = structured_retrieve(memories, window_days=window_days)
    context = "\n".join(f"- [{m.get('date')}] {m.get('title')}: {m.get('summary')}" for m in scored)
    draft = plan(context)
    critic = critic_and_reflect(draft, context)
    final_text = finalize(draft, critic)
    return {"plan": draft, "critic": critic, "final": final_text, "retrieval_trace": scored, "focus_concepts": focus}