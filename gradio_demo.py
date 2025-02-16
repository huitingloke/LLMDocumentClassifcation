import gradio as gr
import os
from PyPDF2 import PdfReader

def navigate_home():
    """Returns to the home page by toggling visibility."""
    return gr.update(visible=True), gr.update(visible=False)

def navigate_classification():
    """Returns to the classification page by toggling visibility."""
    return gr.update(visible=True), gr.update(visible=False)

def navigate_search():
    """Returns to the search page by toggling visibility."""
    return gr.update(visible=True), gr.update(visible=False)

def navigate_savedDocuments():
    """Returns to the search page by toggling visibility."""
    return gr.update(visible=True), gr.update(visible=False)

def show_page(page):
    return {
        "home": [gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)],
        "classification": [gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)],
        "search": [gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)],
        "savedDocuments": [gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)],
    }[page]

def upload_file(file, notes):
    if file is not None:
        file_path = file.name  # Save file path for reuse
        file_name = os.path.basename(file.name)  # Extract just the file name
        status = f"✅ File '{file_name}' uploaded successfully!\n\n📌 Notes: {notes if notes else 'No additional notes'}"
        return status, file_path, gr.update(visible=False), gr.update(visible=True)
    else:
        return "❌ No file uploaded.", None

## For now, document preview only supports PDF files ##
def preview_document(file):
    """Extracts text preview from PDF files (first page only)."""
    if file is None:
        return "No file uploaded."
    
    if file.name.endswith(".pdf"):
        with open(file.name, "rb") as f:  # Open the file explicitly
            reader = PdfReader(f)
            text = reader.pages[0].extract_text() if reader.pages else "Empty PDF"
        return text[:500]  # Show only first 500 characters
    
    return "Unsupported file type."


with gr.Blocks(css="""
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css');
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;600;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css');

    * {
        font-family: 'Manrope', sans-serif !important;
        font-size: 16px !important;
    }

    /* Logo at top left hand corner */
    .logo {
        font-family: 'Arial', sans-serif !important;  /* Specify font */
        color: white !important;  /* Set text color to white */
        font-size: 40px !important;  /* Set logo font size */
        font-weight: bold !important;  /* Ensure bold font */
    }

    .top-bar {
        display: flex;
        align-items: center;  /* Align items at the center */
        justify-content: space-between;
        background-color: #cc0000;
        padding: 5px 20px;
        border-radius: 0px;
        height: 85px;
    }

    /* Style for the "Upload Document(s)" button */
    .gr-button {
        background-color: #cc0000 !important;
        color: white !important;
        border: none !important;
        font-size: 16px !important;
    }

    .gr-button:hover {
        background-color: #990000 !important;
    }

    /* Move the "Log out" button to the bottom left */   
    .logout-button-container {
        position: fixed;
        bottom: 20px;
        left: 20px;
        width: 160px;
    }

    /* Profile section in the top-right corner */
    .profile-section {
        display: flex;
        flex-direction: column;
        color: white;
        align-items: flex-end;
    }

    .profile-section i {
        font-size: 24px;
        margin-bottom: 5px;
    }

    .profile-section .profile-name {
        font-size: 16px;
        font-weight: bold;
        text-align: right;
    }
    
    .sidebar {
        background-color: #f8f8f8;
        padding: 20px;
        height: 100vh; /* Full height */
        width: 200px;
        font-weight: bold;
    }

    .sidebar-item {
        padding: 10px;
        font-size: 16px;
        color: black;
        cursor: pointer; /* Makes it look clickable */
    }

    .sidebar-item:hover {
        color: blue; /* Changes color on hover */
    }

    .search-button-container {
        width: 160px;
    }      

    .search-box {
        width: 800px;
    }   
    
""") as demo:

    # Top Bar
    with gr.Row(elem_classes="top-bar"):
        gr.Markdown("**NOMURA**", elem_classes="logo")

        # Profile section in the top-right corner
        gr.HTML("""
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
            <div class="profile-section">             
                <span class="profile-name">Welcome back!<br>Xavier Lee</span>
                <i class="fas fa-user-circle"></i>  <!-- Profile icon -->
            </div>
        """)


    # Define home and classification pages
    home_page = gr.Column(visible=True)
    classification_page = gr.Column(visible=False)
    search_page = gr.Column(visible=False)
    savedDocuments_page = gr.Column(visible=False)

    # HOME 
    with home_page:
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("<div class='nav-item' onclick='document.getElementById('home_btn').click()'>🏠 Home</div>")
                gr.HTML("<div class='nav-item' onclick='document.getElementById('search_btn').click()'>🔍 Search</div>")
                gr.HTML("<div class='sidebar-item' onclick='document.getElementById('savedDocs_btn').click()'>📂 Saved Documents</div>")
                gr.HTML("<div class='sidebar-item' onclick='document.getElementById('settings_btn').click()'>⚙️ Settings</div>")

            with gr.Column(scale=4):
                gr.Markdown("### Upload your Document(s) here")
                file_uploader = gr.File(label="Upload your document", type="filepath")
                chosen_model = gr.Dropdown(choices=["deepseek-r1:7b", "llama3.1", "phi4:14b"], label="Choose a model", value="deepseek-r1:7b")
                notes = gr.Textbox(placeholder="Write any comments you have about your document(s) here.", label="Comments")       
                upload_button = gr.Button("Upload Document(s)")
                output_text = gr.Textbox(label="Upload Status", interactive=False)
                classify_button = gr.Button("Classify Document(s)")

                # Link button to file upload
                upload_button.click(
                    fn=upload_file,
                    inputs=[file_uploader, notes],
                    outputs=[output_text, file_uploader] 
                )

                classify_button.click(navigate_classification, outputs=[classification_page, home_page])
                

    # CLASSIFICATION 
    with classification_page:
        ## Storing does not seem to work ##
        classification_file = gr.State()  # Store file path in state

        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("<div class='nav-item' onclick='document.getElementById('home_btn').click()'>🏠 Home</div>")
                gr.HTML("<div class='nav-item' onclick='document.getElementById('search_btn').click()'>🔍 Search</div>")
                gr.HTML("<div class='sidebar-item' onclick='document.getElementById('savedDocs_btn').click()'>📂 Saved Documents</div>")
                gr.HTML("<div class='sidebar-item' onclick='document.getElementById('settings_btn').click()'>⚙️ Settings</div>")

            with gr.Column(scale=3):
                gr.Markdown("### Document Preview")
                file_uploader = gr.File(label="Upload Document") # uploaded file from home page should show here
                document_preview = gr.Textbox(label="Document Preview", interactive=False)   
                file_uploader.change(preview_document, inputs=classification_file, outputs=document_preview)           

                with gr.Row():
                    reclassify_button = gr.Button("Reclassify", elem_classes="reclassify-button")
                    backtoHome_button = gr.Button("New classification", elem_classes="backtoHome-button") # reset all fields from prev page automatically

            with gr.Column(scale=1):
                gr.Markdown("### Classification Results")
                classification_contentType = gr.TextArea(label="Content type", interactive=False)
                classification_contentType = gr.TextArea(label="Author(s)", interactive=False)
                classification_contentType = gr.TextArea(label="Posted at", interactive=False)

            # Button to return to home page
            backtoHome_button.click(navigate_home, outputs=[home_page, classification_page])

            # Button to search page to test
            searchPage_button = gr.Button("Search", elem_classes="")
            searchPage_button.click(navigate_search, outputs=[search_page, classification_page])
        

    # SEARCH 
    with search_page:
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("<div class='nav-item' onclick='document.getElementById('home_btn').click()'>🏠 Home</div>")
                gr.HTML("<div class='nav-item' onclick='document.getElementById('search_btn').click()'>🔍 Search</div>")
                gr.HTML("<div class='sidebar-item' onclick='document.getElementById('savedDocs_btn').click()'>📂 Saved Documents</div>")
                gr.HTML("<div class='sidebar-item' onclick='document.getElementById('settings_btn').click()'>⚙️ Settings</div>")

            with gr.Column(scale=5):
                with gr.Row():
                    with gr.Column(): 
                        search_input = gr.Textbox(placeholder="Enter your search query", elem_classes="search-box")
                    
                    with gr.Column(): 
                        # filter by content type
                        filters_contentType = gr.Dropdown(choices=["Content Type(s)", "Option 1", "Option 2", "Option 3"], 
                      multiselect=True, elem_classes="filter-box", value="Content Type(s)")
                    with gr.Column(): 
                        # filter by author
                        filters_authors = gr.Dropdown(choices=["Author(s)", "Option 1", "Option 2", "Option 3"], 
                      multiselect=True, elem_classes="filter-box", value="Author(s)")
                    with gr.Column(): 
                        # filter by date
                        filters_postedAt = gr.Dropdown(choices=["Date(s)", "Option 1", "Option 2", "Option 3"], 
                      multiselect=True, elem_classes="filter-box", value="Date(s)")
                    
                    filters = filters_contentType + filters_authors + filters_postedAt

                    with gr.Column():
                        search_button = gr.Button("Search", elem_classes="search-button-container")

                search_documents_output = gr.TextArea(label="Search Results", interactive=False)


            ## TEMP hardcoded outputs ##
            search_button.click(lambda query, num=None: "Iterate through fake database.", 
                    inputs=[search_input, filters], 
                    outputs=search_documents_output)




    # SAVED DOCUMENTS
    with savedDocuments_page:
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("<div class='nav-item' onclick='document.getElementById('home_btn').click()'>🏠 Home</div>")
                gr.HTML("<div class='nav-item' onclick='document.getElementById('search_btn').click()'>🔍 Search</div>")
                gr.HTML("<div class='sidebar-item' onclick='document.getElementById('savedDocs_btn').click()'>📂 Saved Documents</div>")
                gr.HTML("<div class='sidebar-item' onclick='document.getElementById('settings_btn').click()'>⚙️ Settings</div>")
            
            gr.Markdown("### Saved Documents")



    # Log out button container at the bottom-left of the page
    with gr.Row(elem_classes="logout-button-container"):
        gr.Button("Log out")

    # Invisible helper buttons for routing
    home_btn = gr.Button(visible=False, elem_id="home_btn")
    search_btn = gr.Button(visible=False, elem_id="search_btn")
    savedDocs_btn = gr.Button(visible=False, elem_id="savedDocs_btn")
    settings_btn = gr.Button(visible=False, elem_id="settings_btn")


    home_btn.click(fn=show_page, inputs=[gr.State("home")], outputs=[home_page, classification_page, search_page, savedDocuments_page])
    search_btn.click(fn=show_page, inputs=[gr.State("search")], outputs=[home_page, classification_page, search_page, savedDocuments_page])
    savedDocs_btn.click(fn=show_page, inputs=[gr.State("savedDocuments")], outputs=[home_page, classification_page, search_page, savedDocuments_page])


# Inject JavaScript to trigger invisible buttons for navigation
with demo:
    gr.HTML("""
    <script>
    document.addEventListener("DOMContentLoaded", function () {
        document.getElementById("home_btn").style.display = "none";
        document.getElementById("search_btn").style.display = "none";
        document.getElementById("savedDocs_btn").style.display = "none";
        document.getElementById("settings_btn").style.display = "none";
    });
    </script>
    """)


if __name__ == "__main__":
    demo.launch()



    # home_btn = gr.Button(visible=False)
    # # classification_btn = gr.Button(visible=False)
    # upload_btn = gr.Button(visible=False)
    # savedDocs_btn = gr.Button(visible=False)

    # <script>
    #     function navigateTo(page) {
    #         if (page === 'home') { document.querySelector('button:nth-of-type(1)').click(); }
    #         if (page === 'search') { document.querySelector('button:nth-of-type(2)').click(); }
    #         if (page === 'savedDocuments') { document.querySelector('button:nth-of-type(3)').click(); }
    #     }
    # </script>