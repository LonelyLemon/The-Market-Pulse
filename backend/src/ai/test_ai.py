import numpy
import textwrap

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from langchain_text_splitters import CharacterTextSplitter

"""
Here is the simplified flow of the RAG-implementation process:
- Step 1: Configuring the knowledge base
- Step 2: Implementing indexing section
- Step 3: Implementing retriever
- Step 4: Implementing generator (Prompt Builder)
- Step 5: Implementing main RAG pipeline
"""

#-------------------------------------
#   1. Knowledge Base ( Database )
#-------------------------------------

documents = [
    "MarketPulse is a FinTech dashboard designed for real-time arbitrage monitoring.",
    "The application backend is built using Python and FastAPI.",
    "MarketPulse uses a PostgreSQL database with SQLAlchemy for ORM.",
    "The 4 phases of development are: Dashboard, Sentiment Analyzer, Arbitrage Monitor, and Paper Trading Engine.",
    "To start the server, run the command: 'uvicorn main:app --reload' on port 8000.",
    "The sentiment analysis module uses the DeepEval library for testing metrics.",
    "Git branches should be named 'feature/feature-name' or 'fix/bug-name'.",
]

#------------------
#   2. Indexing
#------------------

vectorizer = TfidfVectorizer()
doc_vector = vectorizer.fit_transform([vectorizer])

print(f"Database indexed: {len(documents)} documents ready.")

#-------------------
#   3. Retriever
#-------------------

def retrieve(query, top_k=2):
    """
    1. Convert user query to a vector.
    2. Calculate similarity (Eg: Cosine) between query and all docs.
    3. Return the top_k most similar documents.
    """

    query_vector = vectorizer.transform([query])

    similarity = cosine_similarity(query_vector, doc_vector).flatten()

    # Sort by score (descending) and get top_k indices
    top_indices = similarity.argsort()[::-1][:top_k]

    results = []
    for idx in top_indices:
        # Only return when there is some similarity (score > 0)
        if similarity[idx] > 0:
            results.append(documents[idx], similarity[idx])

    return results

#-------------------
#   4. Generator
#-------------------

def generate_rag_response(query, retrieved_docs):
    """
    This simulates the LLM part. In a real app, you would send 
    this 'SYSTEM PROMPT' to GPT-4 or Claude.
    """

    if not retrieved_docs:
        return "Sorry, I can't retrieve any related information"
    
    context_text = "\n".join([f"{score} - {doc}" for doc, score in retrieved_docs])

    SYSTEM_PROMPT = f"""
    You are a helpful assistant for TheMarketPulse.

    CONTEXT: {context_text}

    QUERY: {query}

    ANSWER:
    """

    return SYSTEM_PROMPT

#--------------------------
#   5. Main RAG Pipeline
#--------------------------

def run_rag_pipeline(user_query):
    print(f"🔎 User asks: '{user_query}'")
    
    # Step 1: Retrieve
    results = retrieve(user_query)
    print(f"Found {len(results)} relevant documents.")
    
    # Step 2: Augment & Generate
    prompt = generate_rag_response(user_query, results)
    
    print("\n" + "="*40)
    print(" What the LLMs see (The RAG Prompt):")
    print("="*40)
    print(textwrap.dedent(prompt))
    print("="*40 + "\n")

# --- Test Runs ---
# Test 1: Technical stack question
run_rag_pipeline("What database does MarketPulse use?")

# Test 2: Project management question
run_rag_pipeline("How should I name my git branches?")

# Test 3: Irrelevant question (Hallucination check)
run_rag_pipeline("What is the weather in Tokyo?")