"""
app.py -- OmniBrain E.R.I.S. (Environmental Report Intelligence System)
Integrates Core, Advanced, and Elite Hackathon Bounties.
"""
import streamlit as st
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi
from pypdf import PdfReader
import trafilatura
import datetime
import json
import os
import base64

import agent_core as ac

STORAGE_FILE = "brain_storage.json"
ATTACHMENT_DIR = "attachments"

os.makedirs(ATTACHMENT_DIR, exist_ok=True)

def load_persisted_memories():
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception: return []
    return []

def save_persisted_memories(memories):
    try:
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(memories, f, indent=4, default=str)
    except Exception as e: st.error(f"Storage Error: {e}")

@st.cache_data(show_spinner=False)
def parse_pdf_cached(uploaded_file):
    reader = PdfReader(uploaded_file)
    return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

st.set_page_config(page_title="OmniBrain E.R.I.S.", page_icon="🌍", layout="wide")
st.markdown("""
    <style>
        .block-container { max-width: 1000px; padding-top: 2rem; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.title("OmniBrain E.R.I.S. 🌍")
st.caption("Environmental Report Intelligence System | Agentic Remediation & Governance")

# --- GEMINI AUTHENTICATION ---
API_KEY = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("🚨 No GEMINI_API_KEY found.")
    st.stop()

client = genai.Client(api_key=API_KEY)
FALLBACK_MODELS = ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.6-flash"]

def safe_generate(contents):
    last_error = None
    for model_id in FALLBACK_MODELS:
        try: return client.models.generate_content(model=model_id, contents=contents)
        except Exception as e:
            last_error = e; continue
    raise Exception(f"All endpoints busy. ({last_error})")

ac.configure(safe_generate)

# --- STATE & EVENT INIT ---
if "memories" not in st.session_state: st.session_state.memories = load_persisted_memories()
if "pending_proposal" not in st.session_state: st.session_state.pending_proposal = None
if "last_roadmap" not in st.session_state: st.session_state.last_roadmap = None

if "events_registered" not in st.session_state:
    def _handle_memory_added(new_memory: dict):
        items = ac.perception_scan(new_memory)
        if items: st.session_state.pending_proposal = items
    ac.on(ac.MemoryEvent.ADDED, _handle_memory_added)
    st.session_state.events_registered = True

# --- ADVANCED BOUNTY: ROLE-AWARE FILTERS ---
with st.sidebar:
    st.header("🔐 Role Simulation")
    current_role = st.selectbox("Current User Role", ["Admin", "Investigator", "Reviewer", "Hospital Authority"])
    st.divider()

    st.header("📥 Ingest Environment Report")
    source_type = st.selectbox("Data Source", ["Text Paste", "PDF Document", "YouTube Video", "Website URL"])
    title = st.text_input("Report Title")
    report_role = st.selectbox("Visibility Scope", ["All", "Admin", "Investigator", "Reviewer", "Hospital Authority"])
    memory_date = st.date_input("Date", datetime.date.today())
    
    # --- CORE BOUNTY: ATTACHMENTS ---
    evidence_file = st.file_uploader("Attach Evidence (Image/Doc) [Optional]")
    
    content_text = ""
    if source_type == "Text Paste": content_text = st.text_area("Paste report details...")
    elif source_type == "PDF Document":
        pdf_file = st.file_uploader("Upload PDF Report", type=["pdf"])
        if pdf_file: content_text = parse_pdf_cached(pdf_file)
    elif source_type == "YouTube Video":
        yt_url = st.text_input("YouTube Drone/Site Footage URL")
        if yt_url:
            try:
                video_id = yt_url.split("/")[-1].split("?")[0] if "youtu.be" in yt_url else yt_url.split("v=")[-1].split("&")[0]
                fetched = YouTubeTranscriptApi().fetch(video_id) if hasattr(YouTubeTranscriptApi(), 'fetch') else YouTubeTranscriptApi.get_transcript(video_id)
                content_text = "\n".join([f"[{int(t['start'])//60:02d}:{int(t['start'])%60:02d}] {t['text']}" for t in fetched])
            except Exception as e: st.error("Transcript failed.")

    if st.button("Save Report to E.R.I.S.", use_container_width=True) and content_text and title:
        with st.spinner("Agent auditing report & extracting metadata..."):
            
            # Save Attachment Core Bounty
            attachment_path = None
            if evidence_file:
                attachment_path = os.path.join(ATTACHMENT_DIR, evidence_file.name)
                with open(attachment_path, "wb") as f: f.write(evidence_file.getbuffer())

            # Elite Bounty Schema Extractor
            save_prompt = f"""Analyze this environmental report and extract metadata as JSON only:
{{"summary": "2-3 sentence summary", "concepts": ["hazard", "compliance", etc], "status": "Critical/Moderate/Resolved", "recommendations": "Actionable steps", "notes": "Extra context"}}
Content:\n{content_text[:10000]}"""
            try:
                parsed = ac.safe_json_parse(safe_generate(save_prompt).text)
                new_memory = {
                    "title": title, "type": source_type, "date": str(memory_date), "role_scope": report_role,
                    "summary": parsed.get("summary", ""), "concepts": parsed.get("concepts", []),
                    "status": parsed.get("status", "Unknown"), "recommendations": parsed.get("recommendations", ""),
                    "notes": parsed.get("notes", ""), "attachment": attachment_path, "raw": content_text
                }
                st.session_state.memories.append(new_memory)
                save_persisted_memories(st.session_state.memories)
                ac.emit(ac.MemoryEvent.ADDED, new_memory)
                st.success(f"Report Logged: {title}")
                st.rerun()
            except Exception as e: st.warning(f"⚠️ {e}")

# --- GOVERNANCE GATE (Agentic) ---
if st.session_state.pending_proposal:
    with st.container(border=True):
        st.warning("⚠️ Perception Agent detected urgent compliance deadlines in recent report!")
        for item in st.session_state.pending_proposal:
            st.write(f"- {item.get('description')} — **{item.get('date')}**")
        c1, c2 = st.columns(2)
        if c1.button("Approve Deadline Lock"):
            st.session_state.pending_proposal = None
            st.rerun()
        if c2.button("Dismiss"):
            st.session_state.pending_proposal = None
            st.rerun()

# --- ADVANCED BOUNTY: SCOPED RESULTS ---
visible_memories = [m for m in st.session_state.memories if m.get("role_scope", "All") in ["All", current_role]]
st.info(f"🛡️ **Role Filter Active:** Showing {len(visible_memories)} of {len(st.session_state.memories)} total reports accessible to `{current_role}`.")

# --- ROADMAP WORKFLOW ---
st.subheader("📅 Agentic Remediation Plan")
if st.button("Generate Remediation Roadmap", use_container_width=True):
    if not visible_memories: st.warning("No reports available for your role.")
    else:
        status = st.empty()
        status.write("🔄 Auditing reports...")
        try:
            st.session_state.last_roadmap = ac.generate_roadmap(visible_memories, window_days=7)
            status.write("✅ Retrieve → ✅ Plan → ✅ Critique → ✅ Finalize")
        except Exception as e: st.error(f"Planning failed: {e}")

if st.session_state.last_roadmap:
    result = st.session_state.last_roadmap
    with st.expander("🔍 Explainable Trace & Semantic Audit"):
        for m in result.get("retrieval_trace", []): st.caption(f"**{m['title']}** — *{m['_reason']}*")
    
    with st.expander("🧠 Plan → Critique Trace"):
        st.json(result["plan"])
        conf = result["critic"]["confidence"]
        st.markdown(f"**Confidence: {conf['level']}** — {conf['reason']}")

    if "evidence" in result["plan"]:
        st.markdown("### 📝 Mandated Tasks & Evidence Sources")
        for task, sources in result["plan"]["evidence"].items():
            st.info(f"**{task}**\n*Source Report:* {', '.join(sources)}")

    if result["critic"]["confidence"]["needs_approval"]:
        st.error("🚨 Critic flagged hallucinations in the remediation plan. Human review required.")
    
    st.markdown("### Final Approved Roadmap")
    st.markdown(result["final"])

# --- ELITE & CORE BOUNTIES: REPORTS & EXPORTS ---
st.subheader("📁 Environment Report Database")
if visible_memories:
    for d in visible_memories:
        with st.expander(f"{'🔴' if 'Critical' in d.get('status','') else '🟢'} {d['title']} ({d['date']})"):
            st.markdown(f"**Status:** {d.get('status', 'N/A')} | **Scope:** {d.get('role_scope', 'All')}")
            st.write(f"**Summary:** {d['summary']}")
            st.write(f"**Recommendations:** {d.get('recommendations', 'None')}")
            
            # CORE BOUNTY: Attachment Display
            if d.get("attachment") and os.path.exists(d["attachment"]):
                st.markdown("---")
                st.markdown("**📎 Attached Evidence:**")
                if d["attachment"].lower().endswith(('.png', '.jpg', '.jpeg')):
                    st.image(d["attachment"], width=300)
                else:
                    st.write(d["attachment"])
            
            # ELITE BOUNTY: Project-Specific Report Export
            html_report = f"""
            <html><body>
            <h2>Environmental Incident Report: {d['title']}</h2>
            <p><b>Date:</b> {d['date']}</p>
            <p><b>Status:</b> {d.get('status', 'N/A')}</p>
            <hr>
            <h3>Summary</h3><p>{d['summary']}</p>
            <h3>Agent Recommendations</h3><p>{d.get('recommendations', 'N/A')}</p>
            <h3>Field Notes</h3><p>{d.get('notes', 'N/A')}</p>
            <h3>Tags</h3><p>{', '.join(d.get('concepts', []))}</p>
            <hr>
            <p><i>Generated autonomously by OmniBrain E.R.I.S.</i></p>
            </body></html>
            """
            st.download_button(
                label="📄 Download Official Report (HTML)",
                data=html_report,
                file_name=f"ERIS_Report_{d['title'].replace(' ', '_')}.html",
                mime="text/html",
                key=d['title']
            )
else:
    st.caption("No reports accessible for your current role.")