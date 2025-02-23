import gradio as gr
import time

def upload_file(file, notes):
    """Handles file upload and provides status update with delay before switching pages."""
    if file is not None:
        status = f"✅ File '{file.name}' uploaded successfully!\n\n📌 Notes: {notes if notes else 'No additional notes'}"
    else:
        status = "❌ No file uploaded."

    time.sleep(2)  # Delay before switching pages
    return status, gr.update(visible=False), gr.update(visible=True)

def navigate_home():
    """Returns to the home page by toggling visibility."""
    return gr.update(visible=True), gr.update(visible=False)

def search_action(query):
    """Handles search action."""
    return f"Searching for: {query}"

with gr.Blocks(css="""
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css');
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;600;700&display=swap');

    * {
        font-family: 'Manrope', sans-serif !important;
        font-size: 16px !important;
    }

    .logo {
        font-family: 'Arial', sans-serif !important;
        color: white !important;
        font-size: 40px !important;
        font-weight: bold !important;
    }

    .top-bar {
        display: flex;
        align-items: center;
        background-color: #cc0000;
        padding: 10px 20px;
        height: 110px;
    }

    .search-box-container {
        gap: 10px;
        display: flex;
        flex-grow: 1;
    }

    .search-box {
        width: 300px !important;
        height: 50px !important;
        border-radius: 20px !important;
        border: 1px solid #ddd !important;
        padding: 5px 15px !important;
        font-size: 14px !important;
    }

    .profile-section {
        display: flex;
        align-items: center;
        margin-left: 50px;
    }

    .profile-name {
        font-size: 16px;
        font-weight: bold;
        margin-right: 20px;
    }

    .logout-button-container {
        position: fixed;
        bottom: 20px;
        left: 20px;
        width: 160px;
    }

    .sidebar-item {
        font-size: 18px !important;
        padding: 10px 0;
    }

    .active {
        font-weight: bold;
    }

    .upload-button {
        background-color: #555555 !important; /* Dark grey */
        color: white !important;
        font-size: 16px !important;
        padding: 12px 20px !important;
        border-radius: 5px !important;
    }

    .status-box {
        height: 300px !important; /* Increased height */
        font-size: 14px !important;
        padding: 10px !important;
    }

    .reclassify-button {
        width: 160px !important;
    }
""") as demo:

    # Top Navigation Bar
    with gr.Row(elem_classes="top-bar"):
        gr.HTML("<span class='logo'>NOMURA</span>")

        with gr.Row(elem_classes="search-box-container", equal_height=True):
            search_input = gr.Textbox(placeholder="Search...", show_label=False, elem_classes="search-box")
            search_button = gr.Button("Search")

        with gr.Row(elem_classes="profile-section"):
            gr.HTML("""<button class="profile-button"><i class="fas fa-user-circle"></i></button>""")
            gr.HTML("<span class='profile-name'>Welcome back!<br><b>Xavier Lee</b></span>")

    # Define home and classification pages
    home_page = gr.Column(visible=True)
    classification_page = gr.Column(visible=False)

    # Home Page
    with home_page:
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("<div class='sidebar-item active'>Home</div>")
                gr.HTML("<div class='sidebar-item'>Search</div>")
                gr.HTML("<div class='sidebar-item'>Saved Documents</div>")
                gr.HTML("<div class='sidebar-item'>Settings</div>")

            with gr.Column(scale=4):
                gr.Markdown("### Upload your Document(s) here")
                file_uploader = gr.File(label="Upload your document", type="filepath")
                notes= gr.Textbox(placeholder="Write any comments you have about your document(s) here.")            
                upload_button = gr.Button("Upload Document(s)", elem_classes="upload-button")
                reset_button = gr.Button("Reset")
                output_text = gr.Textbox(label="Upload Status", interactive=False, elem_classes="status-box")

                # Link button to file upload
                upload_button.click(
                    upload_file, 
                    inputs=[file_uploader, notes], 
                    outputs=[output_text, home_page, classification_page]
                )

    # Classification Page
    with classification_page:
        gr.Markdown("### Classification Page")
        gr.Image("/mnt/data/image.png", elem_id="uploaded-image")
        reclassify_button = gr.Button("Reclassify", elem_classes="reclassify-button")

        # Button to return to home page
        reclassify_button.click(navigate_home, outputs=[home_page, classification_page])

    # Logout Button
    with gr.Row(elem_classes="logout-button-container"):
        logout_button = gr.Button("Log out")

    # Search Button Action
    search_button.click(lambda query: f"Searching for: {query}", inputs=[search_input], outputs=[])


demo.launch()

