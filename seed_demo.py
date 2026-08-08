import json
import datetime

STORAGE_FILE = "brain_storage.json"
today = datetime.date.today()

mock_memories = [
    {
        "title": "C++ Advanced Pointers & Memory Management",
        "type": "Text Paste",
        "date": str(today - datetime.timedelta(days=1)),
        "summary": "Covered stack vs heap allocation, smart pointers, and memory leaks in C++.",
        "concepts": ["C++", "Memory Management", "Pointers"],
        "raw": "Lecture Notes: C++ Memory Allocation. Always use std::unique_ptr for single ownership.",
        "transcript": [],
        "video_id": ""
    },
    {
        "title": "Digital Electronics Lab Assignment 2",
        "type": "PDF Document",
        "date": str(today - datetime.timedelta(days=2)),
        "summary": "Logic gate minimization using Karnaugh Maps and flip-flop circuit design.",
        "concepts": ["Digital Electronics", "K-Maps", "Circuits"],
        "raw": "Digital Electronics Assignment 2: Design 4-bit synchronous counter. Submission Portal Closes: August 11.",
        "transcript": [],
        "video_id": ""
    }
]

with open(STORAGE_FILE, "w", encoding="utf-8") as f:
    json.dump(mock_memories, f, indent=4)

print(f"[+] SUCCESS: Seeded {len(mock_memories)} memories with concepts into {STORAGE_FILE}!")