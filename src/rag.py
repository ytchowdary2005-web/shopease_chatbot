from src.data_loader import load_faqs
from src.embeddings import create_embeddings
from src.vector_store import create_vector_store
from src.llm import generate_answer



# Load FAQ data
df = load_faqs()

# Create text for embedding
texts = (
    df["question"] + " " + df["answer"]
).tolist()

# Create embeddings
embeddings = create_embeddings(texts)

# Create FAISS vector store
index = create_vector_store(embeddings)


def search_faq(question, top_k=3):

    query_embedding = create_embeddings([question])

    distances, indices = index.search(
        query_embedding.astype("float32"),
        top_k
    )

    results = df.iloc[indices[0]]

    return results


def ask_question(question):

    # Handle basic conversational messages
    q = question.lower().strip()

    if q in ["hi", "hello", "hey", "hii", "hiii"]:
        return "Hello! 👋 How can I help you with your ShopEase order?"

    if q in ["bye", "goodbye", "see you", "see you later"]:
        return "Goodbye! 👋 Have a great day!"

    if q in ["thanks", "thank you", "thankyou", "thx"]:
        return "You're welcome! 😊 I'm happy to help."

    if q in ["good morning"]:
        return "Good morning! ☀️ How can I help you today?"

    if q in ["good afternoon"]:
        return "Good afternoon! 😊 How can I help you today?"

    if q in ["good evening"]:
        return "Good evening! 🌙 How can I help you today?"

    if q in ["who are you", "what are you"]:
        return "I'm the ShopEase AI Assistant. 🤖 I can help you with orders, shipping, returns, refunds, payments, and more."

    # Search FAQs for normal questions
    results = search_faq(question)

    context = "\n\n".join(
        f"Question: {row['question']}\nAnswer: {row['answer']}"
        for _, row in results.iterrows()
    )

    answer = generate_answer(question, context)

    return answer