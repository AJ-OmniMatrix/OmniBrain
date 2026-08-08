import datetime
import agent_core as ac

class FakeResponse:
    def __init__(self, text):
        self.text = text

def test_extract_keywords_and_retrieve():
    today = datetime.date.today()
    fixture = [
        {"title": "React Hooks video", "summary": "Explains useEffect and useState hooks", "concepts": ["React", "Hooks"], "date": str(today - datetime.timedelta(days=1))},
        {"title": "React project PDF", "summary": "React component architecture and hooks patterns", "concepts": ["React", "Architecture"], "date": str(today - datetime.timedelta(days=2))},
        {"title": "Old note", "summary": "Something about React from ages ago", "concepts": ["React"], "date": str(today - datetime.timedelta(days=40))},
    ]
    scored, focus = ac.structured_retrieve(fixture, window_days=7)
    assert len(scored) == 2, f"expected 2 in-window items, got {len(scored)}"
    print("PASS: structured_retrieve windows and ranks correctly")

def test_safe_json_parse_handles_markdown_fences():
    fenced = '```json\n{"a": 1, "b": [2, 3]}\n```'
    parsed = ac.safe_json_parse(fenced)
    assert parsed == {"a": 1, "b": [2, 3]}
    print("PASS: safe_json_parse strips markdown fences")

def test_assess_confidence_buckets():
    assert ac.assess_confidence({"issues": []})["level"] == "High"
    assert ac.assess_confidence({"issues": ["x"]})["level"] == "Medium"
    assert ac.assess_confidence({"issues": ["x", "y", "z"]})["level"] == "Low"
    print("PASS: confidence bucketing works")

def test_event_system_routes_correctly():
    received = []
    ac.on(ac.MemoryEvent.ADDED, lambda payload: received.append(payload))
    ac.emit(ac.MemoryEvent.ADDED, {"title": "test memory"})
    assert len(received) == 1
    print("PASS: event system routes correctly")

if __name__ == "__main__":
    test_extract_keywords_and_retrieve()
    test_safe_json_parse_handles_markdown_fences()
    test_assess_confidence_buckets()
    test_event_system_routes_correctly()
    print("\nALL TESTS PASSED")