import datetime
from flask import Flask, request, jsonify
import uuid
import chromadb
from pypdf import PdfReader
import sys # To view print messages from the same console
import openai
from dotenv import load_dotenv
import json
load_dotenv()

app = Flask(__name__)

client = chromadb.PersistentClient(path="./chromadb_persistent_storage/")
collection = client.get_or_create_collection(
    name="document_storage", 
)

@app.route("/test", methods=["GET"])
def test():
    return "Hello World"



@app.route("/extract_text", methods=["POST"])
def extract_text(pdf_file):
    # Get the uploaded PDF file from the request
    pdf_file = request.files.get("pdf_file")
    if not pdf_file:
        return jsonify({"error": "No PDF file provided"}), 400    
    #Extract Text from PDF Files
    text = ""
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        text += page.extract_text()
    # USE MODEL HERE TO CLASSIFY TEXT INTO CATEGORIES
    # WE WILL NOT RETURN TEXT HERE AND WILL INSTEAD LINK TO THE FUNCTION TO STORE TEXT. CURRENTLY, WE WILL RETURN TEXT TO PROVE THE FUNCTION WORKS

    return text

def classify_documents(document_text):
    prompt = f"""
    Given the following document text, classify it into one of the following categories:

    **Level 1 Categories**: 
    - internal
    - external

    If the document falls under "internal", further classify it into:
    **Level 2 Categories (Internal)**: 
    - Constitution
    - Contracts (with employees and external clients)
    - T&Cs
    - Privacy Policy
    - Own Financial Data & Reports

    If the document falls under "external", further classify it into:
    **Level 2 Categories (External)**: 
    - Regulation
    - Notices, News
    - Financial Data/Reports
    - Client Info (for onboarding etc.)

    Please return the classification in the following JSON format:
    ```json
    {
      "level_1_category": "internal",
      "level_2_category": "Constitution"
    }
    ```

    **Document Text**:
    {document_text}
    """
    
    # Call OpenAI's GPT API to get classification result
    response = openai.Completion.create(
        engine="text-davinci-003",  # or any other OpenAI model you want to use
        prompt=prompt,
        max_tokens=150,  # Adjust length if needed
        temperature=0.7  # Adjust creativity
    )

    return response['choices'][0]['text'].strip()  # Return the raw result (JSON)



@app.route("/store_documents", methods=["POST"])
def store_documents():
    data = request.get_json(force=True) # For testing purposes, not safe for production
    print(data, file=sys.stderr)

    documents = data.get("document", None) # Should be a list
    metadatas = data.get("metadata", None) # Should be a list with objects inside, each object containing metadata
    
    if not documents:
        return jsonify({"error": "No documents provided"}), 400
    # Can submit multiple documents in one shot but prefer not to as we want to do some preprocessing first
    # Will be slightly slower but overall still more efficient
    for i in range (len(documents)):

        date = datetime.datetime.now()
        new_metadata = metadatas[i]
        new_metadata["date"] = date.timestamp() # Converts to epoch time

        print(documents[i], new_metadata, file=sys.stderr)
        collection.add(
            documents=documents[i],
            metadatas=[new_metadata],
            ids=[str(uuid.uuid4())], # Every document requires a unique ID
        )
    
    return jsonify({"message": "Documents stored successfully"}), 200 # Turns the response into a JSON output!

@app.route("/extract_and_classify", methods=["POST"])
def extract_and_classify():
    pdf_file = request.files.get("pdf_file")
    if not pdf_file:
        return jsonify({"error": "No PDF file provided"}), 400

    # Step 1: Extract text from the PDF file
    text = extract_text(pdf_file)

    # Step 2: Classify the document using OpenAI
    classification_result = classify_documents(text)

    # Step 3: Parse the classification result (which is in JSON format)
    try:
        result_json = json.loads(classification_result)
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse classification result"}), 400

    # Step 4: Prepare metadata (including classification result)
    metadata = {
        "classification_result": result_json,  # Include the classification result
        "date": datetime.datetime.now().timestamp()  # Timestamp for when the document is processed
    }

    # Step 5: Store the document and metadata in the database using the store_documents function
    documents = [text]  # Text extracted from the document
    store_documents_data = {
        "document": documents,
        "metadata": [metadata]
    }

    # Call the existing store_documents function
    return store_documents(store_documents_data)

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




@app.route("/admin", methods=["POST"]) # THIS FUNCTION CURRENTLY DOES NOT WORK, PLEASE DO NOT ACCESS
def admin():
    data = request.get_json(force=True) # For testing purposes, not safe for production
    print(data, file=sys.stderr)

    checker = data.get("checker", None)

    if not checker:
        return jsonify({"error": "No checker provided"}), 400
    
    elif checker == "viewTop":
        print(numpy_array:=collection.peek(), file=sys.stderr)   
        d = dict(enumerate(numpy_array.flatten(), 1))
        return d

# To run the app: flask --app main run [--debug] OR python[3] main.py
@app.route("/delete_collection", methods=["POST"]) # NOTE: THIS FUNCTION IS FOR TESTING PURPOSES. YOU MUST INPUT THE PASSWORD CORRECTLY TO USE IT. 
def delete_collection():
    data = request.get_json(force=True) # For testing purposes, not safe for production
    print(data, file=sys.stderr)

    password = data.get("password", None)

    if not password or password != "verysafeandsecurepassword":
        return jsonify({"error": "Incorrect password"}), 400
    client.delete_collection(name="document_storage")

    


if __name__ == "__main__":
    app.run(debug=True)