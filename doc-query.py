import streamlit as st
import openai
import fitz  # PyMuPDF
import requests
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Directory to save uploaded PDFs
UPLOAD_DIR = Path("uploaded-docs")
UPLOAD_DIR.mkdir(exist_ok=True)

# Function to save uploaded file
def save_uploaded_file(uploaded_file):
    save_path = UPLOAD_DIR / uploaded_file.name
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return save_path

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Function to query OpenAI GPT-4
def query_openai(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )
    return response['choices'][0]['message']['content'].strip()

# Function to search in a public dataset (Wikipedia API as an example)
def search_wikipedia(query):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        'action': 'query',
        'list': 'search',
        'srsearch': query,
        'format': 'json'
    }
    response = requests.get(url, params=params).json()
    search_results = response.get('query', {}).get('search', [])
    if search_results:
        first_result = search_results[0]
        title = first_result['title']
        snippet = first_result['snippet']
        return f"{title}: {snippet}"
    else:
        return "No relevant information found on Wikipedia."

# Streamlit App
st.title("Document Query and Public Dataset Search")

# Upload Document
uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

if uploaded_file is not None:
    pdf_path = save_uploaded_file(uploaded_file)
    document_text = extract_text_from_pdf(pdf_path)
    st.write("Extracted Text from Document:")
    st.write(document_text)

    question = st.text_input("Ask a question about the document:")

    if st.button("Get Answer"):
        if question:
            prompt = f"Document Text: {document_text}\n\nQuestion: {question}\nAnswer:"
            answer = query_openai(prompt)
            if "in the context provided is not defined." in answer or "The document does not provide information" in answer or answer.strip() == "":
                st.write("Answer not found in the document. Searching in public datasets...")
                public_answer = search_wikipedia(question)
                st.write("Answer from Wikipedia:")
                st.write(public_answer)
            else:
                st.write("Answer from Document:")
                st.write(answer)
        else:
            st.write("Please ask a question.")
