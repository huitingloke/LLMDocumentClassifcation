from ollama import ChatResponse, chat
from pypdf import PdfReader
import os
from docx import Document
import time


folder_path = "./document_parsing"
model_list = ["deepseek-r1:7b", "llama3.1", "phi4:14b"]

def list_files_in_folder(folder_path):
    final_list = []
    # Loop through all files and directories in the specified folder
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # Join the root directory and the file name to get the full path
            file_path = os.path.join(root, file)
            final_list.append(file_path)
    return final_list

def extract_text(file):
    if file.lower().endswith(".pdf") or ".pdf" in file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    
    elif file.lower().endswith('.docx') or ".docx" in file:
        document = Document(file)
        text = ""
        for para in document.paragraphs:
            text += para.text
        return text
    else:
        return "Unsupported file type"

prompt = """
    Given the following document text, classify it into one of the following categories:

    **Level 1 Categories**: 
    - internal
    - external

    If the document falls under "internal", further classify it into:
    **Level 2 Categories (Internal)**: 
    - Constitution
    - Contracts
    - T&Cs
    - Privacy Policy
    - Own Financial Data & Reports

    If the document falls under "external", further classify it into:
    **Level 2 Categories (External)**: 
    - Regulation
    - Notices, News
    - Financial Data/Reports
    - Client Info

    Please return the classification in the following JSON format:
    {
      "level_1_category": "internal",
      "level_2_category": "Constitution"
    }

    Do not elaborate on anything in your response. I only want the JSON response.

    **Document Text**:
    """

with open("results.txt", "w", encoding="utf-8") as the_file:

    for file in list_files_in_folder(folder_path):
        print(file)

        document_text = extract_text(file)
        document_text = document_text.replace("\n", " ").split(" ")
        document_text = " ".join(document_text[0:250])

        print(document_text)

        the_file.write(f"File: {file}\n\nDocument text snippet: {document_text}\n\n")

        for model in model_list:

            start_time = time.time()

            print(model)

            the_file.write(f"Model: {model}\n")
            the_file.write(f"----------------------------------------\n")

            response: ChatResponse = chat(model=model, messages=[
            {
                'role': 'user',
                'content': f"{prompt}: {document_text}",
            },
            ])
            
            the_file.write(f"""
            MODEL: {model}
            {response['message']['content']}\n\n""")

            end_time = time.time()
            elapsed_time = end_time - start_time
            the_file.write(f"Time taken: {elapsed_time:.2f} seconds\n\n")
            print(response.message.content)
            # print(response["created_at"])