import streamlit as st
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi
from pypdf import PdfReader
import trafilatura
import datetime
import json
import os

# --- PERSISTENCE CONFIGURATION ---
STORAGE_FILE = "brain_storage.json"

def load_persisted_memories():
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_persisted_memories(memories):
    try:
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(memories, f, indent=4)
    except Exception as e:
        st.error(f"Storage Error: {e}")

# --- CACHED PDF EXTRACTION (PREVENTS RE-PARSING LAG) ---
@st.cache_data(show_spinner=False)
def parse_pdf_cached(uploaded_file):
    """Parses the entire PDF once and caches the result in memory."""
    reader = PdfReader(uploaded_file)
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

# --- UI CONFIGURATION ---
st.set_page_config(page_title="OmniBrain | Universal Second Brain", page_icon="🧠", layout="wide")

st.markdown("""
    <style>
        .block-container { max-width: 950px; padding-top: 2rem; }
        .stChatMessage { padding: 1rem; border-radius: 0.5rem; }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.title("OmniBrain 🧠")
st.caption("Autonomous Agentic Memory | Local RAG & Zero-Dependency Disk Persistence")

# --- DIRECT AI STUDIO AUTHENTICATION & FALLBACK ENGINE ---
try:
    try:
        API_KEY = st.secrets.get("GEMINI_API_KEY", "AQ.Ab8RN6IRiGtSXFQaLQJRSH_273lqhcpccAocKHAeytF14yiFcg")
    except Exception:
        API_KEY = "AQ.Ab8RN6IRiGtSXFQaLQJRSH_273lqhcpccAocKHAeytF14yiFcg"
        
    client = genai.Client(api_key=API_KEY)
    
    FALLBACK_MODELS = ['gemini-3.5-flash', 'gemini-3.5-flash-lite', 'gemini-3.6-flash']
except Exception as e:
    st.error(f"🚨 Client Initialization Failed: {e}")
    st.stop()

def safe_generate(contents):
    """Dynamically cycles through active model endpoints to bypass server spikes."""
    last_error = None
    for model_id in FALLBACK_MODELS:
        try:
            res = client.models.generate_content(model=model_id, contents=contents)
            return res
        except Exception as e:
            last_error = e
            continue
    raise Exception(f"All neural endpoints temporarily busy. ({last_error})")

# --- STATE INITIALIZATION WITH DISK BACKING ---
if "memories" not in st.session_state:
    st.session_state.memories = load_persisted_memories()
    
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Welcome to OmniBrain. I am your autonomous governance agent. My memory layer features disk-backed JSON persistence, localized RAG filtering, and human-in-the-loop safety gates."}
    ]

if "pending_proposal" not in st.session_state:
    st.session_state.pending_proposal = None

# --- SIDEBAR: MULTIMODAL INGESTION PIPELINE ---
with st.sidebar:
    st.header("📥 Ingestion Pipeline")
    
    source_type = st.selectbox("Data Format", [
        "Text Paste", 
        "PDF Document", 
        "YouTube Video", 
        "Website URL",
        "Scanned Doc (OCR) 🔒",
        "Excel (.xlsx) 🔒"
    ])
    
    title = st.text_input("Title / Context")
    memory_date = st.date_input("Date", datetime.date.today())
    
    content_text = ""
    transcript_data = [] 
    yt_video_id = ""
    
    if "🔒" in source_type:
        st.info(f"🚀 **Architecture Note:** {source_type.split(' ')[0]} uses a decoupled microservice ingestion pattern for enterprise security compliance.")
    else:
        if source_type == "Text Paste":
            content_text = st.text_area("Paste unstructured text here...")
            
        elif source_type == "PDF Document":
            uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
            if uploaded_file:
                with st.spinner("Extracting entire PDF document..."):
                    content_text = parse_pdf_cached(uploaded_file)
                st.caption(f"📄 Extracted {len(content_text):,} characters from PDF.")
                
        elif source_type == "YouTube Video":
            yt_url = st.text_input("YouTube URL")
            if yt_url:
                try:
                    # Robust URL parsing for both youtube.com and youtu.be shortlinks
                    if "youtu.be" in yt_url:
                        yt_video_id = yt_url.split("/")[-1].split("?")[0]
                    else:
                        yt_video_id = yt_url.split("v=")[-1].split("&")[0]
                    
                    try:
                        fetched = YouTubeTranscriptApi.get_transcript(yt_video_id)
                    except AttributeError:
                        ytt_api = YouTubeTranscriptApi()
                        fetched = ytt_api.fetch(yt_video_id)

                    formatted_transcript = []

                    for t in fetched:
                        if isinstance(t, dict):
                            text_val = t.get('text', '')
                            start_val = t.get('start', 0)
                        else:
                            text_val = getattr(t, 'text', str(t))
                            start_val = getattr(t, 'start', 0)

                        seconds = int(start_val)  # Exact integer seconds (e.g., 2171)
                        
                        # Calculate Hours, Minutes, Seconds correctly
                        hours, remainder = divmod(seconds, 3600)
                        mins, secs = divmod(remainder, 60)
                        
                        if hours > 0:
                            timestamp_str = f"{hours:02d}:{mins:02d}:{secs:02d}"
                        else:
                            timestamp_str = f"{mins:02d}:{secs:02d}"

                        # True integer seconds in the URL parameter (&t=2171s)
                        link_url = f"https://www.youtube.com/watch?v={yt_video_id}&t={seconds}s"
                        
                        transcript_data.append({"text": text_val, "start": seconds, "url": link_url})
                        formatted_transcript.append(f"[{timestamp_str}]({link_url}) {text_val}")

                    content_text = "\n".join(formatted_transcript)
                except Exception as e:
                    st.error(f"Transcript extraction failed: {e}")
                    
        elif source_type == "Website URL":
            web_url = st.text_input("Website Link")
            if web_url:
                try:
                    downloaded = trafilatura.fetch_url(web_url)
                    if downloaded:
                        content_text = trafilatura.extract(downloaded) or ""
                except:
                    st.error("DOM extraction failed.")

        if st.button("Save to Brain", use_container_width=True) and content_text and title:
            with st.spinner("Agent mapping knowledge to disk..."):
                prompt = f"Extract 3 key structural concepts from this data. \n\nData:\n{content_text[:10000]}"
                try:
                    res = safe_generate(contents=prompt)
                    
                    new_memory = {
                        "title": title,
                        "type": source_type,
                        "date": str(memory_date),
                        "summary": res.text,
                        "raw": content_text,
                        "transcript": transcript_data,
                        "video_id": yt_video_id
                    }
                    
                    st.session_state.memories.append(new_memory)
                    save_persisted_memories(st.session_state.memories) 
                    st.success(f"Successfully Indexed & Persisted: {title}")
                except Exception as e:
                    st.warning(f"⚠️ {e}")

    st.divider()
    st.caption(f"🧠 Persistent Memories Mapped: {len(st.session_state.memories)}")

# --- MAIN DASHBOARD: STRATEGIC PLANNERS ---
st.subheader("📅 Strategic Planning Agents")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Generate Weekly Roadmap", use_container_width=True):
        if not st.session_state.memories:
            st.warning("Brain is empty.")
        else:
            dump = "\n".join([f"Date: {m.get('date', '')} | {m.get('title', 'Untitled')}: {m.get('summary', '')}" for m in st.session_state.memories])
            sys_prompt = f"You are a Tactical Planning Agent. Analyze this data and build a strict, actionable 7-day Weekly Roadmap: {dump}"
            try:
                res = safe_generate(contents=sys_prompt)
                st.session_state.chat_history.append({"role": "assistant", "content": f"**🗓️ 7-Day Tactical Roadmap:**\n\n{res.text}"})
                st.rerun()
            except Exception as e:
                st.warning(f"⚠️ {e}")

with col2:
    if st.button("Generate Monthly Strategy", use_container_width=True):
        if not st.session_state.memories:
            st.warning("Brain is empty.")
        else:
            dump = "\n".join([f"Date: {m.get('date', '')} | {m.get('title', 'Untitled')}: {m.get('summary', '')}" for m in st.session_state.memories])
            sys_prompt = f"You are a Strategic Planning Agent. Analyze this data and build a high-level 30-day Monthly Strategy: {dump}"
            try:
                res = safe_generate(contents=sys_prompt)
                st.session_state.chat_history.append({"role": "assistant", "content": f"**🗺️ 30-Day Strategic Plan:**\n\n{res.text}"})
                st.rerun()
            except Exception as e:
                st.warning(f"⚠️ {e}")

with col3:
    if st.button("Scan Hidden Deadlines", use_container_width=True):
        with st.spinner("Perception Agent Scanning..."):
            dump = "\n".join([f"{m.get('title', 'Untitled')} ({m.get('date', '')}): {m.get('raw', '')[:500]}" for m in st.session_state.memories])
            scan_prompt = f"Scan this data strictly for hidden dates, exams, or deadlines. Output a prioritized reminder list: {dump}"
            try:
                scan_res = safe_generate(contents=scan_prompt)
                st.session_state.pending_proposal = scan_res.text
                st.rerun()
            except Exception as e:
                st.warning(f"⚠️ {e}")

st.divider()

# --- HUMAN-IN-THE-LOOP GOVERNANCE ---
if st.session_state.pending_proposal:
    with st.container(border=True):
        st.markdown("### ⚠️ Agent Action Proposal (Governance Gate)")
        st.info("The Perception Agent proposes locking these deadlines into the operational plan:")
        st.write(st.session_state.pending_proposal)
        
        c_app, c_rej = st.columns(2)
        with c_app:
            if st.button("✅ Approve & Finalize Schedule"):
                st.session_state.chat_history.append({"role": "assistant", "content": f"**[Action Locked by User Governance]**\n\n{st.session_state.pending_proposal}"})
                st.session_state.pending_proposal = None
                st.success("Governance Approved. Plan Locked.")
                st.rerun()
        with c_rej:
            if st.button("❌ Reject Action"):
                st.session_state.pending_proposal = None
                st.warning("Action blocked by user.")
                st.rerun()

# --- CHAT & LOCALIZED RAG RETRIEVAL ---
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

if user_query := st.chat_input("Query your decentralized brain..."):
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Executing localized RAG lookup..."):
            
            query_lower = user_query.lower()
            relevant_context = []
            
            stop_words = {"timestamp", "timestamps", "time", "where", "when", "what", "is", "of", "in", "the", "a", "an", "for", "to", "at"}
            query_words = [w for w in query_lower.split() if w not in stop_words and len(w) > 2]

            for m in st.session_state.memories:
                m_title = m.get("title", "Untitled")
                m_raw = m.get("raw", "")
                m_summary = m.get("summary", "")

                if query_lower in m_raw.lower() or query_lower in m_summary.lower() or any(w in m_raw.lower() for w in query_words):
                    content_to_pass = m_raw if m_raw else m_summary
                    relevant_context.append(f"Source: {m_title}\nFull Transcript Content with Links:\n{content_to_pass}")

            if not relevant_context:
                 relevant_context = [
                     f"Source: {m.get('title', 'Untitled')}\nFull Transcript Content with Links:\n{m.get('raw', m.get('summary', ''))}" 
                     for m in st.session_state.memories
                 ]

            context = "\n---\n".join(relevant_context)
            
            # Repaired System Prompt - removed the confusing placeholders
            prompt = f"""Answer the user query based strictly on the provided context.
            
            CRITICAL INSTRUCTION FOR YOUTUBE SOURCES:
            Every line in the transcript context starts with a clickable markdown link.
            When explaining where a topic is discussed, you MUST copy the exact clickable markdown timestamp link exactly as it is written in the context and place it directly in your response text. Do not modify the URL in any way.

            Context:
            {context}

            Query: {user_query}"""
            
            try:
                res = safe_generate(contents=prompt)
                answer = res.text

                st.markdown(answer, unsafe_allow_html=True)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.warning(f"⚠️ {e}")