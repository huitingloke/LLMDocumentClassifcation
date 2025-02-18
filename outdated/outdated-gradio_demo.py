import gradio as gr
from pypdf import PdfReader
from gpt4all import GPT4All
import chromadb
import uuid
from pypdf import PdfReader
import sys # To view print messages from the same console
import datetime

client = chromadb.PersistentClient(path="./chromadb_persistent_storage/")
collection = client.get_or_create_collection(
    name="document_storage", 
)
# Initialize model here so it doesn't refresh every time a query is performed
model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf") # downloads / loads a 4.66GB LLM
categorizing_prompt = """
Please categorize the following text and output the result in a JSON format. The classification should be based on whether the document is internal or external to a business context. Do not summarize any of the text. 

- If the document is **internal**, it should be classified into one of the following types:
  - Constitution
  - Contracts (with employees or external clients)
  - T&Cs (Terms and Conditions)
  - Privacy Policy
  - Own Financial Data & Reports
  
- If the document is **external**, it should be classified into one of the following types:
  - Regulation
  - Notices
  - News
  - Financial Data/Reports
  - Client Info (e.g., for onboarding)

Please follow standard business data classification practices and provide the result in this format:

```json
{
  "class": "<internal OR external>",
  "type": "<relevant document type>"
}
```

Make sure that your classification is based on the content of the document. If the document doesn't clearly fit within the categories, classify it based on its intended audience or usage. If necessary, provide the most reasonable category based on the text provided. You should only provide the JSON output and no other commentary."""

def extract_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def categorize_text(text):
    
    with model.chat_session():
        final_prompt = categorizing_prompt + text[:5000] # Context token limit currently 
    return model.generate(final_prompt, max_tokens=256)

def upload_documents_func(metadata:dict, text:str):
    collection.add(
        documents=[text],
        metadatas=[metadata],
        ids=[str(uuid.uuid4())]
    )
    print(metadata, text)
    return True

with gr.Blocks() as application:
    gr.Markdown("""
    # Visualization of Database
    """)
    with gr.Row():
        pdf_file = gr.File(label="Upload PDF", file_types=[".pdf", ".html", ".csv", ".json"])
        pdf_content = gr.Textbox(label="PDF Content")

        pdf_file.upload(extract_text, inputs=pdf_file, outputs=pdf_content)

    with gr.Row():
        categorize = gr.Button("Categorize")
        categorizing_output = gr.TextArea(label="Categorizing Output")

        categorize.click(categorize_text, inputs=pdf_content, outputs=categorizing_output)
    
    with gr.Row():

        upload_documents = gr.Button("Upload Documents")
        upload_output = gr.TextArea(label="Uploaded Object")

        upload_documents.click(upload_documents_func, inputs=[categorizing_output, pdf_content], outputs=upload_output)

application.launch(debug=True)