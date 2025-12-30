#  Tanzisstant – Modular Intelligent Assistant

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)
![Groq](https://img.shields.io/badge/Groq-Llama3-orange)
![License](https://img.shields.io/badge/License-MIT-green)

**Tanzisstant** is a professional, role-based AI assistant built with a focus on **modular architecture** and **persistent memory**. Powered by Meta's **Llama 3** (via Groq), it delivers lightning-fast, context-aware responses with a custom-styled UI.

Unlike simple chatbot scripts, Nexus AI uses **Object-Oriented Programming (OOP)** to separate concerns between UI, Logic, Memory, and System Tools.

---

## ✨ Key Features

- **🎭 Dynamic Role Switching**  
  Instantly switch personas (e.g., *Senior Coder, Tutor, Career Mentor*) with unique system prompts.

- **🧠 Persistent Memory**  
  Retains conversation context across sessions using a JSON-based storage engine.

- **⚡ Real-Time Streaming**  
  Uses Groq's high-speed inference to stream Llama 3 responses instantly.

- **🛠 System Command Handler**  
  Execute local commands directly from chat (e.g., `open google`, `open notepad`).

- **🎨 Custom UI**  
  A heavily styled Streamlit interface featuring dark mode, glassmorphism effects, and a custom control center.

---

## 🏗️ Project Architecture

The project follows a **modular design pattern** to ensure scalability and maintainability:

```text
📂 nexus-ai/
│
├── 📄 app.py            # Main Entry Point & UI Logic (Streamlit)
├── 📄 roles.py          # RoleManager Class (Persona Definitions)
├── 📄 memory.py         # MemoryManager Class (JSON Persistence)
├── 📄 commands.py       # CommandHandler Class (System Tools)
├── 📄 .env              # API Keys (Security)
└── 📄 chat_history.json # Local Database for Context

🚀 Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/yourusername/nexus-ai.git
cd nexus-ai

2️⃣ Install Dependencies
pip install streamlit groq python-dotenv

3️⃣ Configure API Key

Create a .env file in the root directory:

GROQ_API_KEY=gsk_your_actual_key_here


Get a free key from:
👉 Groq Console

4️⃣ Run the Application
streamlit run app.py

🕹️ Usage Guide

Launch the App
Run the Streamlit command above.

Select a Role
Choose a persona from the sidebar (e.g., Coding Assistant).

Chat Naturally
The assistant remembers previous conversations automatically.

System Commands
Try typing:

open google
open youtube
open notepad   # Windows only

🛠️ Tech Stack

Language: Python 3.10+

Frontend: Streamlit (Custom CSS)

LLM Engine: Llama 3.3 (via Groq API)

Architecture: Object-Oriented Programming (OOP)

State Management: Streamlit Session State + JSON Storage

🔮 Future Improvements

 Voice Input & Output (Speech-to-Text / Text-to-Speech)

 RAG (Retrieval-Augmented Generation) for PDF & document chat

 Dockerization for easy deployment

 Multi-user authentication

 Cloud-based memory storage

## 🤝 Connect

Created by **MD. Tanzir Hossain**  
[LinkedIn](https://www.linkedin.com/in/tanzirrabby/)


⭐ If you find this project useful, don’t forget to give it a star on GitHub!




