from pypdf import PdfReader
import chromadb
import uuid
import datetime
from docx import Document
import time
import langchain_implementation
import database_implementation
import pandas as pd
import sqlite3

conn = sqlite3.connect('file_storage.db')
conn.execute('''CREATE TABLE IF NOT EXISTS files (
            id TEXT PRIMARY KEY,
            filename TEXT,
            filedata BLOB
        );''')
conn.commit()

length_of_text = 6000
# Category Tag choices
choices = [
    "Regulation",
    "Notices, News",
    "Financial Data/Reports",
    "Client Info",
    "Constitution",
    "Contracts",
    "T&Cs",
    "Privacy Policy",
    "Own Financial Data & Reports",
]

client = chromadb.PersistentClient(path="./chromadb_persistent_storage/")

# FOR TESTING PURPOSES
client.delete_collection("document_storage")
collection = client.get_or_create_collection(
    name="document_storage", 
)

def extract_text(file):
    """Extracts text preview from PDF, DOCX, CSV, and XLSX files."""
    if file is None:
        return "No file uploaded."
    
    file_name = file.name.lower()

    # PDF Preview
    if file_name.endswith(".pdf"):
        try:
            with open(file.name, "rb") as f:
                reader = PdfReader(f)
                text = reader.pages[0].extract_text() if reader.pages else "Empty PDF"
            return text[:500] , gr.update(visible=False), gr.update(visible=True) # Show only first 500 characters
        except Exception as e:
            return f"Error reading PDF: {e}", gr.update(visible=False), gr.update(visible=True)

    elif file.name.lower().endswith(".docx") or file.name.endswith(".doc"):
        print("Filetype: Word", file.name)
        document = Document(file)
        text = ""
        for para in document.paragraphs:
            text += para.text
        return text[:500]

    # CSV Preview
    elif file_name.endswith(".csv"):
        try:
            df = pd.read_csv(file.name, nrows=5)  # Read first 5 rows
            return df.to_string(index=False)
        except Exception as e:
            return f"Error reading CSV: {e}"

    # Excel (XLSX) Preview
    elif file_name.endswith(".xlsx"):
        try:
            df = pd.read_excel(file.name, engine="openpyxl", nrows=5)
            return df.to_string(index=False), gr.update(visible=False), gr.update(visible=True)
        except Exception as e:
            return f"Error reading XLSX: {e}", gr.update(visible=False), gr.update(visible=True)

    return "Unsupported file type."


def search_by_tag_and_query(search_input, filters_contentType, filters_authors, filters_postedAt):
    content_type = filters_contentType
    authors = filters_authors.split(",")
    postedAt = filters_postedAt # change to be date object

    results = collection.query(
        query_texts=[search_input],
        n_results=9999999,
        where={"level2": filters_contentType}, # may not work if it is searching a list
        include=["documents", "metadatas"],
    )
    return results

"""def retrieve_search(query, num_results):

    print(f"Retrieving search results...: QUERY: {query}; NUM_RESULTS: {num_results}")
    results = ""
    num_results = int(num_results)
    collection_retrieval = collection.query(
        query_texts=[query],
        n_results=num_results,
    )

    if collection_retrieval:
        for item in collection_retrieval:
            print(item)
    return collection_retrieval if collection_retrieval else "No results found.""" 

def process_file(file_uploader, notes="", chosen_model="gpt3.5-turbo"):

    start_time = time.time()
    if file_uploader is not None:
        metadata = {}
        text = extract_text(file_uploader)

        if text == "WIP" or text == "Unsupported file type":
            return "Work in Progress"

        metadata["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        metadata["source"] = ""
        metadata["comments"] = notes or "NA"

        classified = langchain_implementation.generate_response(document_text=text)
        metadata["level1"] = classified["level_1_category"]
        metadata["level2"] = classified["level_2_category"]
        metadata["model"] = chosen_model
        uploaded_id = uuid.uuid4()
 
        database_storage = database_implementation.store_file(conn, uploaded_id, file_uploader)

        collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[uploaded_id],
        )

        print(metadata, uploaded_id)

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")
        
        return f"File '{file_uploader.name}' uploaded successfully with these comments: {notes}"
    
    return "No file uploaded."
