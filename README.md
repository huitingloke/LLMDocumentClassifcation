# FYPDocumentSorter

## Description

KIV

## Setup

* Clone the repository
* Create a new terminal window and from there, create a new virtual environment with the command `virtualenv env`
* Activate the environment
    * Mac: `source env/bin/activate`
    * Windows: `env\Scripts\activate`
* Install the requirements with the command `pip install -r requirements.txt`
* Create a folder called `chromadb_persistent_storage` and another one called `document_parsing` 
* Run the application with the command `python gradio_demo.py`

## Schema Note (to be updated)

* `doc_type`: `str` -- Type of documents -- Risk, Compliance, Contract, Regulation, Onboarding, Client engagement
    * `level`: `int` -- 1 means internal/external, 2 means 
* `doc_id`: `str` -- UUID4 generation of unique document ID
* `date_uploaded`: `datetime` - Date the document was uploaded


> [!IMPORTANT]  
> Do not nest the folders within each other.

> [!NOTE]  
> The assistance of ChatGPT and Cody were used to aid in the programming of this repository. 
