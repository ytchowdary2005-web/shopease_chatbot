import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_answer(question, context):

    prompt = f"""
You are ShopEase customer support assistant.

Answer the user's question using ONLY the information provided
in the FAQ context below.

If the answer is not available in the context, say:
"I don't have enough information to answer that."

FAQ CONTEXT:
{context}

USER QUESTION:
{question}

Give a clear and helpful answer.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful ShopEase customer support assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content