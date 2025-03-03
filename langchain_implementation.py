from ollama import ChatResponse, chat
import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import OpenAI 
from dotenv import dotenv_values

config = dotenv_values(".env")  
OPENAI_API_KEY = config["OPENAI_API_KEY"]

prompt_template = """
Given the following document text, classify it into one of the following categories:

Level 1 Categories: 
- internal
- external

If the document falls under internal, further classify it into:
Level 2 Categories (Internal): 
- Constitution
- Contracts
- T&Cs
- Privacy Policy
- Own Financial Data & Reports

If the document falls under external, further classify it into:
Level 2 Categories (External): 
- Regulation
- Notices, News
- Financial Data/Reports
- Client Info

Respond ONLY with a valid JSON object, with no other text. The JSON object must have the following structure:

{{
    "level_1_category": "internal" OR "external",
    "level_2_category": "[topic]"
}}

Document text:
{document_text}
"""

def generate_response_with_langchain(document_text: str, chosen_model="gpt3.5-turbo") -> dict:

    response = ""

    if chosen_model == "gpt3.5-turbo":
        if OPENAI_API_KEY:
            llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
            chain = LLMChain(prompt=PromptTemplate(input_variables=["document_text"], template=prompt_template), llm=llm)
            response = chain.run(document_text=document_text)
        else:
            return "Error: OPENAI_API_KEY environment variable not set."

    elif chosen_model == "llama3.1:8b" or chosen_model == "deepseek-r1:7b":

        response: ChatResponse = chat(model=chosen_model, messages=[
            {
                'role': 'user',
                'content': prompt_template + document_text,
            },
        ])
        response = response['message']['content']
    
    try:
        # Attempt to find the start and end of the JSON object
        response = str(response)
        start = response.find('{')
        end = response.rfind('}') + 1
        if start != -1 and end > start:
            json_response = response[start:end]
            return json.loads(json_response)
        else:
            print(f"Error: Could not find valid JSON in response: {response}")
            return {"error": "Invalid response format - JSON not found"}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}, Response: {response}")
        return {"error": "Invalid JSON format"}
    except Exception as e:
        print(f"An unexpected error occurred: {e}, Response: {response}")
        return {"error": "An unexpected error occurred"}
        