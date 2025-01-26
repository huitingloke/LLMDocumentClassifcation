import datetime
from flask import Flask, request
import uuid
import chromadb
from pypdf import PdfReader
import sys # To view print messages from the same console

app = Flask(__name__)

client = chromadb.PersistentClient(path="./chromadb_persistent_storage/")
collection = client.get_or_create_collection(
    name="document_storage", 
)

@app.route("/test", methods=["GET"])
def test():
    return "Hello World"

@app.route("/extract_text", methods=["POST"])
def extract_text(pdf_file:str):
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        text += page.extract

    # USE MODEL HERE TO CLASSIFY TEXT INTO CATEGORIES
    # WE WILL NOT RETURN TEXT HERE AND WILL INSTEAD LINK TO THE FUNCTION TO STORE TEXT. CURRENTLY, WE WILL RETURN TEXT TO PROVE THE FUNCTION WORKS

    return text

@app.route("/store_documents", methods=["POST"])
def store_documents():
    data = request.get_json(force=True) # For testing purposes, not safe for production
    print(data, file=sys.stderr)

    documents = data.get("documents", None) # Should be a list
    metadatas = data.get("metadata", None) # Should be a list with objects inside, each object containing metadata
    
    if not documents:
        return False

    # Can submit multiple documents in one shot but prefer not to as we want to do some preprocessing first
    # Will be slightly slower but overall still more efficient
    for i in range (len(documents)):

        date = datetime.datetime.now()
        new_metadata = metadatas[i]
        new_metadata += {
            "date": date.timestamp() # Converts to epoch time
        }
        

        collection.add(
        documents=documents[i],
        metadatas=[new_metadata],
        ids=[uuid.uuid4()], # Every document requires a unique ID
    )
    
    return collection.count() # Temporary return value to test if the function works

@app.route("/retrieve_documents", methods=["POST"])
def retrieve_documents():
    data = request.get_json(force=True) # For testing purposes, not safe for production
    query = data.get("query", None)
    if not query:
        return False
    
    results = collection.query(
        query_texts=[query],
        n_results=10,
    )

    # Explanation: Embedding databases have their own algorithms to classify and retrieve documents based on their
    # proximity in vector space, but we need an LLM to classify the text for its metadata. Technically, you could
    # just go by the vector space distance, but that may not provide all necessary information.
    return results

# To run the app: flask --app main run [--debug] OR python[3] main.py

if __name__ == "__main__":
    app.run(debug=True)