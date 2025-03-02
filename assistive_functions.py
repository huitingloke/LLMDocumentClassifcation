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

length_of_text = 4000
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

    # PDF Preview
    if file.endswith(".pdf"):
        try:
            with open(file, "rb") as f:
                reader = PdfReader(f)
                text = reader.pages[0].extract_text() if reader.pages else "Empty PDF"
            return text[:length_of_text]
        except Exception as e:
            return f"Error reading PDF: {e}"

    elif file.endswith(".docx") or file.endswith(".doc"):
        print("Filetype: Word", file)
        document = Document(file)
        text = ""
        for para in document.paragraphs:
            text += para.text
        return text[:length_of_text]

    # CSV Preview
    elif file.endswith(".csv"):
        try:
            df = pd.read_csv(file, nrows=5)  # Read first 5 rows
            return df.to_string(index=False)
        except Exception as e:
            return f"Error reading CSV: {e}"

    # Excel (XLSX) Preview
    elif file.endswith(".xlsx"):
        try:
            df = pd.read_excel(file, engine="openpyxl", nrows=5)
            return df.to_string(index=False),
        except Exception as e:
            return f"Error reading XLSX: {e}"

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
 
def process_file(file_uploader, notes="", chosen_model="gpt3.5-turbo"):

    start_time = time.time()
    if file_uploader is not None:
        metadata = {}
        text = extract_text(file_uploader)

        if not text:
            return "Unsupported file type."
        
        if len(text) > length_of_text:
            text = text[:length_of_text]

        metadata["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        metadata["source"] = ""
        metadata["comments"] = notes or "NA"

        classified = langchain_implementation.generate_response_with_langchain(document_text=text, chosen_model=chosen_model)
        
        metadata["level1"] = classified["level_1_category"]
        metadata["level2"] = classified["level_2_category"]
        metadata["model"] = chosen_model
        uploaded_id = str(uuid.uuid4())
 
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
        
        return metadata, uploaded_id
    
    return "No file uploaded."

"""print("-------------------")
print(process_file("contract_11.docx", "test_document1"))
print("-------------------")
print(process_file("Detailed_Board_Meeting_Financial_Summary.pdf", "test_document2"))
print("-------------------")
print(process_file("ByteShield_CyberSecurity_Privacy_Policy.pdf", "test_document3"))
print("-------------------")"""