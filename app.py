import streamlit as st
import openai
from youtube_transcript_api import YouTubeTranscriptApi
from pypdf import PdfReader
import trafilatura
import os
import datetime

# --- UI CONFIGURATION (Claude Style) ---
st.set_page_config(page_title="OmniBrain", page_icon="🧠", layout="centered")

st.markdown("""
    <style>
        .block-container { max-width: 850px; padding-top: 2rem; }
        .stChatMessage { padding: 1rem; border-radius: 0.5rem; }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.title("OmniBrain")
st.caption("Your autonomous, second digital brain with Agentic Planners & Timestamp Search.")

# Gemini API Key
GEMINI_API_KEY = "AQ.Ab8RN6LTGFn-WK_Ua7T-GbxJ_HDEVu4RvMsIZJGdB_qdL2asyg"

client = openai.OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# --- STATE INITIALIZATION ---
if "memories" not in st.session_state:
    st.session_state.memories = []
    
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hello! I am OmniBrain. I store your memories date-wise, generate planners, find exact video timestamps, and scan for deadlines autonomously (with human approval required)."}
    ]

if "pending_proposal" not in st.session_state:
    st.session_state.pending_proposal = None

# --- SIDEBAR: INGESTION PIPELINE ---
with st.sidebar:
    st.header("📥 Add Knowledge")
    source_type = st.selectbox("Format", ["Text Paste", "PDF File", "YouTube URL", "Website URL"])
    title = st.text_input("Title / Context")
    memory_date = st.date_input("Date", datetime.date.today())
    
    content_text = ""
    transcript_data = [] 
    yt_video_id = ""
    
    if source_type == "Text Paste":
        content_text = st.text_area("Paste text here...")
    elif source_type == "PDF File":
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")
        if uploaded_file:
            reader = PdfReader(uploaded_file)
            content_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif source_type == "YouTube URL":
        yt_url = st.text_input("YouTube Link", placeholder="https://youtube.com/...")
        if yt_url:
            try:
                yt_video_id = yt_url.split("v=")[-1].split("&")[0].split("/")[-1]
                ytt_api = YouTubeTranscriptApi()
                fetched = ytt_api.fetch(yt_video_id)
                for t in fetched:
                    t_text = t.get('text', '') if isinstance(t, dict) else getattr(t, 'text', '')
                    t_start = t.get('start', 0) if isinstance(t, dict) else getattr(t, 'start', 0)
                    transcript_data.append({"text": t_text, "start": t_start})
                content_text = " ".join([t["text"] for t in transcript_data])
            except Exception as e:
                st.error(f"Could not read video transcript: {e}")
    elif source_type == "Website URL":
        web_url = st.text_input("Website Link", placeholder="https://...")
        if web_url:
            try:
                downloaded = trafilatura.fetch_url(web_url)
                if downloaded:
                    content_text = trafilatura.extract(downloaded) or ""
            except:
                st.error("Could not read website.")

    if st.button("Save to Brain", use_container_width=True) and content_text and title:
        with st.spinner("Processing memory..."):
            prompt = f"Summarize and extract 3 key concepts from this text. \n\nText:\n{content_text[:30000]}"
            res = client.chat.completions.create(model="gemini-3.6-flash", messages=[{"role": "user", "content": prompt}])
            
            st.session_state.memories.append({
                "title": title,
                "type": source_type,
                "date": str(memory_date),
                "summary": res.choices[0].message.content,
                "raw": content_text[:30000],
                "transcript": transcript_data,
                "video_id": yt_video_id
            })
            st.success(f"Saved: {title} ({memory_date})")

    st.divider()
    st.caption(f"🧠 Memories Stored: {len(st.session_state.memories)}")
    
    # --- AGENTIC TOOLS: PLANNERS & DATE SUMMARIES ---
    st.subheader("🤖 Agentic Tools")
    
    selected_range_days = st.slider("Summarize past X days", 1, 30, 7)
    if st.button("📅 Generate Date-Wise Planner & Brief", use_container_width=True):
        cutoff_date = datetime.date.today() - datetime.timedelta(days=selected_range_days)
        filtered_memories = [m for m in st.session_state.memories if datetime.datetime.strptime(m['date'], "%Y-%m-%d").date() >= cutoff_date]
        
        if not filtered_memories:
            st.warning("No memories found in this date range.")
        else:
            memory_dump = "\n".join([f"Date: {m['date']} | [{m['type']}] {m['title']}: {m['summary']}" for m in filtered_memories])
            sys_prompt = f"You are OmniBrain's Planner Agent. Review the user's date-wise stored memories below and build a structured Action Plan, Reminders list, and Date-Wise Summary:\n\n{memory_dump}"
            
            res = client.chat.completions.create(model="gemini-3.6-flash", messages=[{"role": "system", "content": sys_prompt}])
            st.session_state.chat_history.append({"role": "user", "content": f"Generate a planner & summary for the last {selected_range_days} days."})
            st.session_state.chat_history.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()

    st.divider()
    st.subheader("🤖 Autonomous Deadline Agent")
    
    if st.button("🔍 Scan Memories for Hidden Deadlines", use_container_width=True):
        with st.spinner("Agent scanning text for dates and tasks..."):
            all_raw_text = "\n".join([f"Title: {m['title']} | Date: {m['date']} | Content: {m['raw']}" for m in st.session_state.memories])
            
            scan_prompt = f"""You are OmniBrain's Autonomous Deadline Agent. 
            Scan the following stored memories, identify any upcoming dates, exams, or practicals, and extract them into a structured reminder list.
            
            Memories:
            {all_raw_text if all_raw_text else "No memories found."}
            """
            
            scan_res = client.chat.completions.create(model="gemini-3.6-flash", messages=[{"role": "user", "content": scan_prompt}])
            st.session_state.pending_proposal = scan_res.choices[0].message.content
            st.success("Agent detected pending tasks!")
            st.rerun()

# --- MAIN UI: CONVERSATIONAL INTERFACE ---
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# --- NON-CONSENSUAL ACTION SAFEGUARD: ACTION PROPOSAL DISPLAY ---
if st.session_state.pending_proposal:
    with st.container():
        st.markdown("### ⚠️ Agent Action Proposal (Requires Approval)")
        st.info("The agent autonomously scanned your memories and proposed the following action plan:")
        st.write(st.session_state.pending_proposal)
        
        col_app, col_rej = st.columns(2)
        with col_app:
            if st.button("✅ Approve & Lock Plan"):
                st.session_state.chat_history.append({"role": "assistant", "content": f"**[Action Executed by User Approval]**\n\n{st.session_state.pending_proposal}"})
                st.session_state.pending_proposal = None
                st.success("Reminders locked into system!")
                st.rerun()
        with col_rej:
            if st.button("❌ Reject"):
                st.session_state.pending_proposal = None
                st.warning("Action discarded safely.")
                st.rerun()

# Chat Input & Exact Keyword Timestamp Search
if user_query := st.chat_input("Ask your brain anything (e.g., 'reverse string')..."):
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Searching transcripts and memories..."):
            
            # 1. Exact keyword timestamp matching in YouTube transcripts
            timestamp_results_html = ""
            keyword_searched = user_query.lower()
            
            for m in st.session_state.memories:
                if m["type"] == "YouTube URL" and m["transcript"]:
                    matching_hits = []
                    for chunk in m["transcript"]:
                        if keyword_searched in chunk["text"].lower():
                            seconds = int(chunk["start"])
                            mins, secs = divmod(seconds, 60)
                            timestamp_link = f"https://www.youtube.com/watch?v={m['video_id']}&t={seconds}s"
                            matching_hits.append(f"- [{mins:02d}:{secs:02d}]({timestamp_link}): \"...{chunk['text']}...\"")
                    
                    if matching_hits:
                        timestamp_results_html += f"\n\n**Found in Video: '{m['title']}'**\n" + "\n".join(matching_hits[:5])

            # 2. General LLM Synthesis across all stored text
            memory_context = "\n---\n".join([f"Date: {m['date']} | Source: {m['title']} ({m['type']})\nData: {m['raw']}" for m in st.session_state.memories])
            
            final_prompt = f"""You are OmniBrain, the user's second digital brain. Answer their query using the provided memory context. Be specific and conversational.
            
            User Query: {user_query}
            
            Memories:
            {memory_context if st.session_state.memories else "No memories stored yet."}"""
            
            res = client.chat.completions.create(model="gemini-3.6-flash", messages=[{"role": "user", "content": final_prompt}])
            answer = res.choices[0].message.content
            
            # Timestamp formatting or explicit fallback message
            if timestamp_results_html:
                answer += "\n\n### ⏱️ Exact Timestamp Links:\n" + timestamp_results_html
            elif any(m["type"] == "YouTube URL" for m in st.session_state.memories):
                if len(user_query.split()) <= 4: # Short keyword lookup
                    answer += f"\n\n*Note: There was no word like '{user_query}' found in the transcript of your saved videos, so you need to watch another video for that.*"

            st.markdown(answer, unsafe_allow_html=True)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})