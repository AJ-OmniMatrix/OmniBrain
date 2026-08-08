"""
agent_core.py -- all agent logic, separated from the Streamlit UI.
Includes weighted concept retrieval, robust JSON parsing, event system, and the 4-call Planner->Critic->Finalizer pipeline.
"""

import json
import re
import datetime
import copy
from collections import Counter

_generate_fn = None  # injected by app.py: a callable(contents) -> object with .text

def configure(generate_fn):
    global _generate_fn
    _generate_fn = generate_fn

def _call_llm(prompt: str) -> str:
    if _generate_fn is None:
        raise RuntimeError("agent_core.configure(generate_fn) must be called before use")
    return _generate_fn(prompt).text

def safe_json_parse(text: str) -> dict:
    match = re.search(r'(\{.*?\})', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
    cleaned = text.strip().strip("```json").strip("```").strip()
    return json.loads(cleaned)

# ============================================================
# EVENT SYSTEM
# ============================================================

class MemoryEvent:
    ADDED = "MEMORY_ADDED"
    UPDATED = "MEMORY_UPDATED"

_event_handlers = {}

def on(event: str, handler):
    _event_handlers.setdefault(event, []).append(handler)

def emit(event: str, payload: dict):
    for handler in _event_handlers.get(event, []):
        handler(payload)

# ============================================================
# STRUCTURED CONCEPT RETRIEVAL (Weighted Scoring)
# ============================================================

STOPWORDS = {"the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with",
             "is", "are", "this", "that", "from", "by", "at", "be", "was", "were",
             "it", "as", "your", "you", "will", "can"}

def extract_keywords(text: str, top_n: int = 6) -> list[str]:
    words = [w.strip('.,!?()[]:;"\'').lower() for w in (text or "").split()]
    words = [w for w in words if len(w) > 3 and w not in STOPWORDS]
    return [w for w, _ in Counter(words).most_common(top_n)]

def structured_retrieve(memories: list[dict], window_days: int = 7):
    cutoff = datetime.date.today() - datetime.timedelta(days=window_days)
    recent = [copy.deepcopy(m) for m in memories if datetime.date.fromisoformat(m["date"]) >= cutoff]
    
    for m in recent:
        m["_concepts"] = [c.lower() for c in m.get("concepts", [])]
        m["_keywords"] = extract_keywords((m.get("summary", "") or "") + " " + (m.get("title", "") or ""))

    all_concepts = Counter(c for m in recent for c in m["_concepts"])
    focus_concepts = [w for w, c in all_concepts.most_common(6) if c >= 1]

    scored = []
    for m in recent:
        concept_overlap = len(set(m["_concepts"]) & set(focus_concepts))
        keyword_overlap = len(set(m["_keywords"]) & set(focus_concepts))
        recency_bonus = 1
        
        score = (3 * concept_overlap) + (1 * keyword_overlap) + recency_bonus
        reason = f"Weighted Score {score} (Concepts: {concept_overlap}, Keywords: {keyword_overlap})"
        scored.append({**m, "_score": score, "_reason": reason})
    
    scored.sort(key=lambda x: -x["_score"])
    return scored, focus_concepts

# ============================================================
# DETERMINISTIC CONFIDENCE
# ============================================================

def assess_confidence(critic_result: dict) -> dict:
    n = len(critic_result.get("issues", []))
    if n == 0:
        return {"level": "High", "needs_approval": False, "reason": "No unsupported claims found"}
    elif n <= 2:
        return {"level": "Medium", "needs_approval": True,
                "reason": f"{n} unsupported claim(s) found and corrected"}
    else:
        return {"level": "Low", "needs_approval": True,
                "reason": f"{n} unsupported claims found -- review recommended"}

# ============================================================
# PERCEPTION AGENT
# ============================================================

def perception_scan(new_memory: dict) -> list[dict] | None:
    prompt = f"""You are the Perception Agent. A new memory was just ingested.
Scan ONLY this memory for hidden deadlines, exam dates, or due dates.
Return JSON only: {{"found": true/false, "items": [{{"description": "...", "date": "..."}}]}}
Memory: {new_memory.get('title')} -- {new_memory.get('summary')}"""
    try:
        raw = _call_llm(prompt)
        parsed = safe_json_parse(raw)
    except Exception:
        return None
    if parsed.get("found") and parsed.get("items"):
        return parsed["items"]
    return None

# ============================================================
# PLANNER -> CRITIC -> FINALIZER
# ============================================================

def plan(context: str) -> dict:
    prompt = f"""You are the Planning Agent. Produce JSON only.
Use ONLY the memories below. Include an 'evidence' key mapping tasks to memory titles.
{{"goal": "...", "tasks": ["..."], "evidence": {{"Task Name": ["Memory Title"]}}, "missing": [...]}}
Memories:\n{context}"""
    return safe_json_parse(_call_llm(prompt))

def critic_and_reflect(draft_json: dict, context: str) -> dict:
    prompt = f"""You are the Critic Agent. Check the DRAFT against the SOURCE memories.
Return JSON only:
{{"issues": ["unsupported claims, empty list if none"],
  "improvement": "one concrete suggestion to strengthen the roadmap, or empty string if none"}}
SOURCE:\n{context}
DRAFT:\n{json.dumps(draft_json)}"""
    result = safe_json_parse(_call_llm(prompt))
    result["confidence"] = assess_confidence(result)
    return result

def finalize(draft_json: dict, critic_result: dict) -> str:
    prompt = f"""You are the Finalizer. Combine the PLAN and CRITIC FEEDBACK into a clear
final roadmap. Mention any uncertainty from 'missing' or unresolved issues. Never invent facts.
PLAN:\n{json.dumps(draft_json)}
CRITIC:\n{json.dumps(critic_result)}"""
    return _call_llm(prompt)

def generate_roadmap(memories: list[dict], window_days: int = 7) -> dict:
    scored, focus = structured_retrieve(memories, window_days=window_days)
    context = "\n".join(f"- [{m['date']}] {m['title']}: {m['summary']}" for m in scored)

    draft = plan(context)
    critic = critic_and_reflect(draft, context)
    final_text = finalize(draft, critic)

    return {
        "plan": draft,
        "critic": critic,
        "final": final_text,
        "retrieval_trace": scored,
        "focus_concepts": focus,
    }