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

# --- DIRECT AUTHENTICATION & MODEL FALLBACK CONFIGURATION ---
try:
    API_KEY = "AQ.Ab8RN6IgO2Z2uwDMDY08l4Rq5iCCBQ7kKDAhU963KX0FgJzEzA"
    client = genai.Client(api_key=API_KEY)
    
    # Priority list of models to prevent 503 bottlenecks
    FALLBACK_MODELS = ['gemini-3.5-flash', 'gemini-2.5-flash', 'gemini-2.5-flash-lite']
except Exception as e:
    st.error(f"🚨 Authentication Error: {e}")
    st.stop()

def safe_generate(contents):
    """Automatically rotates through model endpoints if a 503 overload occurs."""
    last_error = None
    for model_id in FALLBACK_MODELS:
        try:
            res = client.models.generate_content(model=model_id, contents=contents)
            return res
        except Exception as e:
            last_error = e
            continue
    raise last_error

# --- STATE INITIALIZATION WITH DISK BACKING ---
if "memories" not in st.session_state:
    st.session_state.memories = load_persisted_memories()
    
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Welcome to OmniBrain. I am your autonomous agent. My memory layer features disk-backed JSON persistence, localized RAG filtering, and human-in-the-loop safety gates."}
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
                reader = PdfReader(uploaded_file)
                content_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        elif source_type == "YouTube Video":
            yt_url = st.text_input("YouTube URL")
            if yt_url:
                try:
                    yt_video_id = yt_url.split("v=")[-1].split("&")[0].split("/")[-1]
                    ytt_api = YouTubeTranscriptApi()
                    fetched = ytt_api.fetch(yt_video_id)
                    for t in fetched:
                        transcript_data.append({"text": t.get('text', ''), "start": t.get('start', 0)})
                    content_text = " ".join([t["text"] for t in transcript_data])
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
                prompt = f"Extract 3 key structural concepts from this data. \n\nData:\n{content_text[:15000]}"
                try:
                    res = client.models.generate_content(model=MODEL_ID, contents=prompt)
                    
                    new_memory = {
                        "title": title,
                        "type": source_type,
                        "date": str(memory_date),
                        "summary": res.text,
                        "raw": content_text[:15000],
                        "transcript": transcript_data,
                        "video_id": yt_video_id
                    }
                    
                    st.session_state.memories.append(new_memory)
                    save_persisted_memories(st.session_state.memories) 
                    st.success(f"Successfully Indexed & Persisted: {title}")
                except Exception as e:
                    st.warning(f"⚠️ API Error: {e}")

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
            dump = "\n".join([f"Date: {m['date']} | {m['title']}: {m['summary']}" for m in st.session_state.memories])
            sys_prompt = f"You are a Tactical Planning Agent. Analyze this data and build a strict, actionable 7-day Weekly Roadmap: {dump}"
            try:
                res = client.models.generate_content(model=MODEL_ID, contents=sys_prompt)
                st.session_state.chat_history.append({"role": "assistant", "content": f"**🗓️ 7-Day Tactical Roadmap:**\n\n{res.text}"})
                st.rerun()
            except Exception as e:
                st.warning(f"⚠️ Generation failed. (Details: {e})")

with col2:
    if st.button("Generate Monthly Strategy", use_container_width=True):
        if not st.session_state.memories:
            st.warning("Brain is empty.")
        else:
            dump = "\n".join([f"Date: {m['date']} | {m['title']}: {m['summary']}" for m in st.session_state.memories])
            sys_prompt = f"You are a Strategic Planning Agent. Analyze this data and build a high-level 30-day Monthly Strategy: {dump}"
            try:
                res = client.models.generate_content(model=MODEL_ID, contents=sys_prompt)
                st.session_state.chat_history.append({"role": "assistant", "content": f"**🗺️ 30-Day Strategic Plan:**\n\n{res.text}"})
                st.rerun()
            except Exception as e:
                st.warning(f"⚠️ Generation failed. (Details: {e})")

with col3:
    if st.button("Scan Hidden Deadlines", use_container_width=True):
        with st.spinner("Perception Agent Scanning..."):
            dump = "\n".join([f"{m['title']} ({m['date']}): {m['raw'][:500]}" for m in st.session_state.memories])
            scan_prompt = f"Scan this data strictly for hidden dates, exams, or deadlines. Output a prioritized reminder list: {dump}"
            try:
                scan_res = client.models.generate_content(model=MODEL_ID, contents=scan_prompt)
                st.session_state.pending_proposal = scan_res.text
                st.rerun()
            except Exception as e:
                st.warning(f"⚠️ Generation failed. (Details: {e})")

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
            
            timestamps_html = ""
            query_lower = user_query.lower()
            relevant_context = []
            
            for m in st.session_state.memories:
                if m["type"] == "YouTube Video" and m["transcript"]:
                    hits = []
                    for chunk in m["transcript"]:
                        if query_lower in chunk["text"].lower():
                            seconds = int(chunk["start"])
                            mins, secs = divmod(seconds, 60)
                            link = f"https://www.youtube.com/watch?v={m['video_id']}&t={seconds}s"
                            hits.append(f"- [{mins:02d}:{secs:02d}]({link}): \"...{chunk['text']}...\"")
                    if hits:
                        timestamps_html += f"\n**Found in: '{m['title']}'**\n" + "\n".join(hits[:5])
                
                if query_lower in m["raw"].lower() or query_lower in m["summary"].lower():
                    relevant_context.append(f"Source: {m['title']}\nData: {m['summary']}")

            if not relevant_context:
                 relevant_context = [f"Source: {m['title']}\nData: {m['summary']}" for m in st.session_state.memories]

            context = "\n---\n".join(relevant_context)
            prompt = f"Answer the user query based ONLY on this context: {context}\n\nQuery: {user_query}"
            
            try:
                res = client.models.generate_content(model=MODEL_ID, contents=prompt)
                answer = res.text
                
                if timestamps_html:
                    answer += "\n\n### ⏱️ Localized Video Timestamps:\n" + timestamps_html

                st.markdown(answer, unsafe_allow_html=True)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.warning(f"⚠️ Connection to the Neural Graph failed. (Details: {e})")