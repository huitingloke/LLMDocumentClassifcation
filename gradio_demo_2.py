import gradio as gr

def upload_file(file, notes):
    if file is not None:
        return f"File '{file.name}' uploaded successfully with notes: {notes}"
    return "No file uploaded."

with gr.Blocks(css="""
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css');
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;600;700&display=swap');

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

    /* Search box */
    .search-box {
        display: flex;
        align-items: center;
        position: relative;
        z-index: 10;
    }

    .search-box input {
        width: 596px;
        padding: 8px;
        border-radius: 25px;
        border: 1px solid #ddd;
    }

    .search-box i {
        position: absolute;
        left: 10px;
        color: #aaa;
        font-size: 20px;
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
        display: flex;
        justify-content: flex-start;
        position: absolute;
        bottom: 20px;
        left: 20px;
        width: 10%;
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

""") as demo:

    # Top Bar
    with gr.Row(elem_classes="top-bar"):
        gr.Markdown("**NOMURA**", elem_classes="logo")

        # Search box with search icon
        gr.HTML("""
            <div class="search-box">               
                <input type="text" placeholder="Search..." />
                <i class="fas fa-search"></i>  <!-- Search icon -->
            </div>
        """)

        # Profile section in the top-right corner
        gr.HTML("""
            <div class="profile-section">             
                <span class="profile-name">Welcome back!<br>Rabia Israr</span>
                <i class="fas fa-user-circle"></i>  <!-- Profile icon -->
            </div>
        """)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Home")
            gr.Markdown("### Search")
            gr.Markdown("### Saved Documents")
            gr.Markdown("### Settings")

        with gr.Column(scale=4):
            gr.Markdown("### Upload your Document(s) here")
            file_uploader = gr.File(label="Upload your document", type="filepath")
            notes = gr.Textbox(placeholder="Write any comments you have about your document(s) here.")
            upload_button = gr.Button("Upload Document(s)")
            reset_button = gr.Button("Reset")

            output_text = gr.Textbox(label="Upload Status", interactive=False)
            upload_button.click(upload_file, inputs=[file_uploader, notes], outputs=output_text)

    # Log out button container at the bottom-left of the page
    with gr.Row(elem_classes="logout-button-container"):
        gr.Button("Log out")

demo.launch()
