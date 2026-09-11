from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.rag import ask_question

app = FastAPI(title="ShopEase AI Assistant")

# Allow frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Question(BaseModel):
    question: str


@app.get("/api")
def home():
    return {"message": "ShopEase AI Assistant API is running"}


@app.post("/ask")
def ask(data: Question):
    answer = ask_question(data.question)

    return {
        "answer": answer
    }


# Serve frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")