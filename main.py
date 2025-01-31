import datetime
from flask import Flask, request, jsonify
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
def extract_text(pdf_file):

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

    return jsonify({"message": "Collection deleted successfully"}), 200


if __name__ == "__main__":
    app.run(debug=True)