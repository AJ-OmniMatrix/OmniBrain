import json
import datetime
import os

STORAGE_FILE = "brain_storage.json"
ATTACHMENT_DIR = "attachments"
today = datetime.date.today()

os.makedirs(ATTACHMENT_DIR, exist_ok=True)

# Create a fake image for the attachment bounty
dummy_image_path = os.path.join(ATTACHMENT_DIR, "sample_spill.jpg")
with open(dummy_image_path, "wb") as f:
    f.write(b"") # Empty byte file just to satisfy path existence

mock_memories = [
    {
        "title": "Sector 4 Chemical Spill",
        "type": "Text Paste",
        "date": str(today - datetime.timedelta(days=1)),
        "role_scope": "Investigator",
        "status": "Critical",
        "summary": "Detected 400 gallons of industrial runoff near the hospital water supply.",
        "concepts": ["Chemical Spill", "Water Contamination", "Hazmat"],
        "recommendations": "Dispatch hazmat team immediately. Shut off main valve.",
        "notes": "Witnesses reported a foul odor at 0400 hours.",
        "attachment": dummy_image_path,
        "raw": "Full text of the chemical spill incident report..."
    },
    {
        "title": "Hospital HVAC Compliance Check",
        "type": "PDF Document",
        "date": str(today - datetime.timedelta(days=2)),
        "role_scope": "Hospital Authority",
        "status": "Moderate",
        "summary": "Routine check of airborne filtration systems. Filters operating at 85% efficiency.",
        "concepts": ["Air Quality", "Hospital", "Maintenance"],
        "recommendations": "Schedule filter replacement by August 20th.",
        "notes": "No immediate risk to patients.",
        "attachment": None,
        "raw": "Routine compliance checklist for Hospital wing B..."
    },
    {
        "title": "Public Park Noise Violation",
        "type": "Text Paste",
        "date": str(today - datetime.timedelta(days=5)),
        "role_scope": "All",
        "status": "Resolved",
        "summary": "Construction crew operating heavy machinery past 10 PM ordinance.",
        "concepts": ["Noise Pollution", "Public Disturbance"],
        "recommendations": "Issue formal warning to contractor.",
        "notes": "Contractor apologized and ceased operations.",
        "attachment": None,
        "raw": "Complaint logged by residents regarding excessive noise."
    }
]

with open(STORAGE_FILE, "w", encoding="utf-8") as f:
    json.dump(mock_memories, f, indent=4)

print(f"[+] SUCCESS: Seeded {len(mock_memories)} Environment Reports into {STORAGE_FILE}!")