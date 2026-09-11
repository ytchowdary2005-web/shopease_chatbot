# 🛍️ ShopEase AI Customer Support Chatbot

A RAG-based AI customer support chatbot for an e-commerce platform. The system retrieves relevant information from a structured FAQ dataset and uses an LLM to generate concise and helpful responses.

## 🚀 Features

- 💬 Natural-language customer support
- 🔎 Semantic FAQ retrieval using FAISS
- 🧠 Sentence Transformer embeddings
- 🤖 GPT-OSS-20B for response generation
- 📦 Order and delivery support
- 🔄 Returns and refunds assistance
- 💳 Payment-related support
- 📦 Damaged and defective product support
- 👋 Handles basic conversations such as greetings and thanks
- ❓ Avoids inventing answers when information is unavailable
- ⚡ FastAPI backend
- 🌐 HTML, CSS, and JavaScript frontend
- ✨ Typing animation and suggested questions

## 🏗️ Architecture

```text
User Question
      ↓
Sentence Transformer
      ↓
Query Embedding
      ↓
FAISS Vector Search
      ↓
Relevant FAQ Results
      ↓
Context
      ↓
GPT-OSS-20B
      ↓
Final Answer

🛠️ Tech Stack
    Python
    FastAPI
    FAISS
    Sentence Transformers
    GPT-OSS-20B
    Groq API
    Pandas
    HTML
    CSS
    JavaScript
📁 Project Structure    

    shopease-chatbot/
    │
    ├── data/
    │   └── shopease_faqs.csv
    │
    ├── frontend/
    │   ├── index.html
    │   ├── script.js
    │   └── style.css
    │
    ├── src/
    │   ├── data_loader.py
    │   ├── embeddings.py
    │   ├── vector_store.py
    │   ├── rag.py
    │   └── llm.py
    │
    ├── .gitignore
    ├── app.py
    ├── requirements.txt
    └── README.md

## Setup (in VS Code)

### 1. Open the project

Open the `shopease_chatbot` folder in VS Code (`File > Open Folder`).

### 2. Install dependencies

Open a terminal in VS Code (`` Ctrl+` ``) and run:

```bash
pip install -r requirements.txt


### 3.Start the backend

From the project root, run:

python -m uvicorn app:app --reload

Leave this terminal running.

Visit http://127.0.0.1:8000 in a browser. You should see:

{"message":"ShopEase AI Assistant API is running"}


### 4.Run the frontend

Open the frontend folder in VS Code, right-click index.html, and select Open with Live Server.

It will open in your browser, usually at:

http://127.0.0.1:5500

### 5.Test it

Enter a question in the chatbot and click Send.

Example questions:

How can I cancel my order?
How can I track my order?
What is the return policy?
How can I get a refund?
I received a damaged product. What should I do?