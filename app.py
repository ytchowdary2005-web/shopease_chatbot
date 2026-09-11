from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.rag import ask_question


app = FastAPI(title="ShopEase AI Assistant")


# Allow the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str


@app.get("/")
def home():
    return {"message": "ShopEase AI Assistant API is running"}


@app.post("/ask")
def ask(data: Question):

    answer = ask_question(data.question)

    return {
        "answer": answer
    }