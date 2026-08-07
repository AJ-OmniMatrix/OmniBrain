import json
import os
import datetime

STORAGE_FILE = "brain_storage.json"

today = datetime.date.today()

# Synthetic 7-day memory dataset with embedded hidden deadlines and study tasks
mock_memories = [
    {
        "title": "C++ Advanced Pointers & Memory Management",
        "type": "Text Paste",
        "date": str(today - datetime.timedelta(days=7)),
        "summary": "Covered stack vs heap allocation, smart pointers (unique_ptr, shared_ptr), and memory leaks in C++.",
        "raw": "Lecture Notes: C++ Memory Allocation. Always use std::unique_ptr for single ownership. Memory leak detection due before final lab submission on August 15.",
        "transcript": [],
        "video_id": ""
    },
    {
        "title": "Digital Electronics Lab Assignment 2",
        "type": "PDF Document",
        "date": str(today - datetime.timedelta(days=6)),
        "summary": "Logic gate minimization using Karnaugh Maps and flip-flop circuit design.",
        "raw": "Digital Electronics Assignment 2: Design 4-bit synchronous counter. Submission Portal Closes: August 11 at 11:59 PM. Late submissions lose 20% marks.",
        "transcript": [],
        "video_id": ""
    },
    {
        "title": "DBMS Mid-Term Exam Syllabus Breakdown",
        "type": "Text Paste",
        "date": str(today - datetime.timedelta(days=5)),
        "summary": "Syllabus covers ER Diagrams, Relational Algebra, Normalization (1NF to BCNF), and SQL Joins.",
        "raw": "DBMS Mid-Term Examination scheduled for August 14. Focus areas: BCNF decomposition and indexed query optimization. Review chapters 3, 4, and 7.",
        "transcript": [],
        "video_id": ""
    },
    {
        "title": "University Hostel Housing Renewal Notice",
        "type": "Website URL",
        "date": str(today - datetime.timedelta(days=4)),
        "summary": "Guidelines and fee payment details for annual student housing renewal.",
        "raw": "Hostel Housing Renewal Guidelines 2026: Online portal opens for room selection. Mandatory clearance form submission deadline: August 12.",
        "transcript": [],
        "video_id": ""
    },
    {
        "title": "Striver DSA - Operating Systems Core Concepts",
        "type": "YouTube Video",
        "date": str(today - datetime.timedelta(days=3)),
        "summary": "Process synchronization, semaphores, mutexes, and deadlocks in modern OS.",
        "raw": "[04:15](https://www.youtube.com/watch?v=EAR7De6Goz4&t=255s) Semaphores and Mutex explanation.\n[18:30](https://www.youtube.com/watch?v=EAR7De6Goz4&t=1110s) Deadlock prevention conditions.",
        "transcript": [
            {"text": "Semaphores and Mutex explanation.", "start": 255, "url": "https://www.youtube.com/watch?v=EAR7De6Goz4&t=255s"},
            {"text": "Deadlock prevention conditions.", "start": 1110, "url": "https://www.youtube.com/watch?v=EAR7De6Goz4&t=1110s"}
        ],
        "video_id": "EAR7De6Goz4"
    },
    {
        "title": "Hackathon Pitch Deck & Demo Polish Tasks",
        "type": "Text Paste",
        "date": str(today - datetime.timedelta(days=2)),
        "summary": "Key presentation steps: Live Streamlit demo, architecture slide, and judge QA strategy.",
        "raw": "Hackathon Presentation Checklist: Prepare live RAG demo. System pitch rehearsal scheduled for August 10 morning session.",
        "transcript": [],
        "video_id": ""
    },
    {
        "title": "React UI Configuration & Tailwind Setup",
        "type": "Text Paste",
        "date": str(today - datetime.timedelta(days=1)),
        "summary": "Frontend setup for dark-themed dashboard components and API integration.",
        "raw": "Frontend project build notes: Configured dark mode styles and state management hooks.",
        "transcript": [],
        "video_id": ""
    }
]

# Write directly to storage
with open(STORAGE_FILE, "w", encoding="utf-8") as f:
    json.dump(mock_memories, f, indent=4)

print(f"[+] SUCCESS: Seeded {len(mock_memories)} multi-day memories into {STORAGE_FILE}!")
print("You can now launch 'streamlit run app.py' to test all Strategic Planners.")