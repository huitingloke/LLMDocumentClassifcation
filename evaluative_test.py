from ollama import ChatResponse, chat
from pypdf import PdfReader
import os
from docx import Document
import time
import json


folder_path = "Data"
model_list = ["llama3.1"]

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
    - Internal
    - External

    If the document falls under "Internal", further classify it into:
    **Level 2 Categories (Internal)**: 
    - Employee Contracts
    - Third Party Contracts
    - T&Cs
    - Privacy Policy
    - Own Financial Data & Reports

    If the document falls under "External", further classify it into:
    **Level 2 Categories (External)**: 
    - Regulations, Notices
    - News
    - External Financial Data, Reports
    - Client Info
    - Compliance

    Please return the classification in the following JSON format:
    {
      "level_1_category": "Internal",
      "level_2_category": "Compliance"
    }

    Do not elaborate on anything in your response. I only want the JSON response.

    **Document Text**:
    """

docs_parsed = 0
l1_correct = 0
l2_correct = 0

with open("results.txt", "w", encoding="utf-8") as the_file:

    for file in list_files_in_folder(folder_path):
        print(file)

        document_text = extract_text(file)
        if document_text == "Unsupported file type":
            continue
        document_text = document_text.replace("\n", " ").split(" ")
        document_text = " ".join(document_text[0:250])

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

            print(file.split("\\")[-3])
            print(file.split("\\")[-2])
            response_json = json.loads(response.message.content)
            print(response_json["level_1_category"])
            print(response_json["level_2_category"])
            if file.split("\\")[-2] == response_json["level_2_category"]:
                l2_correct += 1
            if file.split("\\")[-3] == response_json["level_1_category"]:
                l1_correct += 1

            end_time = time.time()
            elapsed_time = end_time - start_time
            the_file.write(f"Time taken: {elapsed_time:.2f} seconds\n\n")
            print(response.message.content)
            # print(response["created_at"])
        docs_parsed += 1
        if l1_correct != 0:
            the_file.write(f"Correctly classified level 1: {l1_correct} / {docs_parsed}")
            the_file.write(f"Correctly classified level 2: {l2_correct} / {l1_correct}")
            the_file.write(f"Accuracy level 1: {l1_correct/docs_parsed*100}%\n")
            the_file.write(f"Accuracy level 2: {l2_correct/l1_correct*100}%\n")
            print(f"Correctly classified level 1: {l1_correct} / {docs_parsed}")
            print(f"Correctly classified level 2: {l2_correct} / {l1_correct}")
            print(f"Accuracy level 1: {l1_correct/docs_parsed*100}%")
            print(f"Accuracy level 2: {l2_correct/l1_correct*100}%")
        else:
            the_file.write(f"Correctly classified level 1: {l1_correct} / {docs_parsed}")
            the_file.write(f"Correctly classified level 2: 0")
            the_file.write(f"Accuracy level 1: {l1_correct/docs_parsed*100}%\n")
            the_file.write(f"Accuracy level 2: 0%\n")
            print(f"Correctly classified level 1: {l1_correct} / {docs_parsed}")
            print(f"Correctly classified level 2: 0")
            print(f"Accuracy level 1: {l1_correct/docs_parsed*100}%")
            print(f"Accuracy level 2: 0%")
