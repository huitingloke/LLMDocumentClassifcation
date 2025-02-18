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
* Run the Flask application with `flask --app main run`
    * You may choose to start it in the debug server by adding the `--debug` flag
    * If this does not work, use `python3 main.py` while `cd` into the home directory

## Current (Proposed) Schema

* `doc_type`: `str` -- Type of documents -- Risk, Compliance, Contract, Regulation, Onboarding, Client engagement
    * `level`: `int` -- 1 means internal/external, 2 means 
* `doc_id`: `str` -- UUID4 generation of unique document ID
* `date_uploaded`: `datetime` - Date the document was uploaded
* 