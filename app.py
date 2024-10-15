import streamlit as st
from lambda_handler import main
from ui.theme import apply_dark_theme

st.sidebar.title("Navigation")
# theme_toggle = st.sidebar.checkbox("Dark Mode", value=False)
# # Apply the dark theme if toggle is activated
# if theme_toggle:
#     apply_dark_theme(theme_toggle)

page = st.sidebar.radio("Go to", ["Upload File", "About"])

# Page logic
if page == "Upload File":
    st.title("Upload Your File")
    uploaded_files = st.file_uploader("Drag and drop or select files", type=['png', 'jpeg'], accept_multiple_files=True)

    if uploaded_files:
        st.write(f"{len(uploaded_files)} file(s) uploaded successfully!")
        
        # Show file details for each uploaded file
        for uploaded_file in uploaded_files:
            file_details = {
                "filename": uploaded_file.name, 
                "filetype": uploaded_file.type, 
                "filesize": uploaded_file.size
            }
            # st.write(file_details)
            st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)

        # Pass all uploaded images to the main function at once
        output_file = main(uploaded_files)

        # Provide a download link for the output Excel file
        if output_file:
            st.write("Download the processed Excel file:")
            st.download_button(
                label="Download Excel",
                data=output_file,
                file_name="output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

elif page == "About":
    st.title("About")
    st.write("""Welcome to the Textract Document Processing App! This application is designed to help users easily extract and process text and data from images using Amazon Textract, a powerful machine learning-based document analysis service provided by AWS.

With this app, users can:

Upload Image Files: Upload PNG or JPEG files that contain scanned forms or documents.
Automatic Text Extraction: The app uses Textract to analyze the images and identify key-value pairs from structured forms.
Download Processed Data: Once processed, the app generates an Excel file that contains all extracted key-value pairs, making it easy to review and work with the data.
This app provides a simple drag-and-drop interface for image uploads and generates downloadable Excel files, allowing users to work with extracted text in a structured, easy-to-use format. Whether you're processing invoices, contracts, or any other type of form, this app automates the process and eliminates the need for manual data entry.

We aim to make document processing faster, more efficient, and accessible to everyone. Let us handle the heavy lifting, so you can focus on what matters most!""")


