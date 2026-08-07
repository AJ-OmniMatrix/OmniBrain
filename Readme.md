# OmniBrain 🧠
**Autonomous Agentic Memory | Local RAG & Zero-Dependency Disk Persistence**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://omnibrainweb.streamlit.app/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Gemini API](https://img.shields.io/badge/Powered%20by-Google%20Gemini-orange)](https://deepmind.google/technologies/gemini/)

OmniBrain is a resilient, autonomous governance agent and universal second brain. It features zero-dependency local JSON disk persistence, multimodal ingestion (PDF, YouTube, Web), and intelligent RAG-based strategic planning. 

🚀 **[Live Demo: Try OmniBrain Here](https://omnibrainweb.streamlit.app/)**

---

## ✨ Key Features

* **Multimodal Ingestion Pipeline:** Natively parses and indexes unstructured text, massive PDF documents (with in-memory caching for zero-lag processing), web pages, and YouTube video transcripts.
* **Intelligent YouTube Parsing:** Automatically extracts `[MM:SS]` timestamps and embeds them as clickable direct-to-video links in the AI's responses.
* **Resilient LLM Routing Engine:** Built-in dynamic fallback cycling between `gemini-3.5-flash`, `gemini-3.5-flash-lite`, and `gemini-3.6-flash` to guarantee 100% uptime during server traffic spikes.
* **Strategic Planning Agents:** Dedicated agentic workflows to scan the decentralized brain for hidden deadlines, construct 7-day tactical roadmaps, and build 30-day overarching strategies.
* **Human-in-the-Loop Governance:** Autonomous agents propose schedule locks and deadline tracking, which must pass through a strict UI approval gate before finalizing.
* **Zero-Dependency Persistence:** Uses a lightweight, robust JSON disk-backing system, bypassing the need for heavy vector databases while maintaining full session continuity.

---

## 🛠️ Architecture & Tech Stack

* **Frontend:** Streamlit (Custom Dark Theme UI)
* **LLM Engine:** Google Generative AI SDK (`google-genai`)
* **Document Processing:** `pypdf`, `trafilatura`
* **Video Processing:** `youtube-transcript-api` (with resilient URL/shortlink routing)
* **Storage:** Local Disk JSON Persistence 

---

## 💻 Local Setup & Installation

To run this project locally, follow these steps:

### 1. Clone the repository
```bash
git clone [https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git)
cd YOUR_REPO_NAME
