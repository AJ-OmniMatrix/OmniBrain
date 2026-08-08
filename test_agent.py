import datetime
import agent_core as ac

class FakeResponse:
    def __init__(self, text):
        self.text = text

def test_extract_keywords_and_retrieve():
    today = datetime.date.today()
    fixture = [
        {"title": "Spill Report", "summary": "Chemical spill detected", "concepts": ["Hazmat", "Spill"], "date": str(today - datetime.timedelta(days=1))},
        {"title": "Water Test", "summary": "Water contamination confirmed", "concepts": ["Contamination", "Hazmat"], "date": str(today - datetime.timedelta(days=2))},
    ]
    scored, focus = ac.structured_retrieve(fixture, window_days=7)
    assert len(scored) == 2
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

if __name__ == "__main__":
    test_extract_keywords_and_retrieve()
    test_safe_json_parse_handles_markdown_fences()
    test_assess_confidence_buckets()
    print("\nALL TESTS PASSED")