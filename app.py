import streamlit as st
from lambda_handler import main
from ui.theme import apply_dark_theme
import boto3
from collections import defaultdict
from openpyxl import Workbook, load_workbook
from io import BytesIO

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



def get_kv_map(image):
    """
    Analyze the document using AWS Textract to get key-value pairs.
    """
    client = boto3.client('textract')
    
    # Read the image bytes
    image_bytes = image.read()
    
    # Analyze the document using Textract
    response = client.analyze_document(
        Document={'Bytes': image_bytes}, 
        FeatureTypes=['FORMS']
    )

    # Get the text blocks
    blocks = response['Blocks']

    # Initialize key, value, and block maps
    key_map = {}
    value_map = {}
    block_map = {}
    
    for block in blocks:
        block_id = block['Id']
        block_map[block_id] = block
        if block['BlockType'] == "KEY_VALUE_SET":
            if 'KEY' in block['EntityTypes']:
                key_map[block_id] = block
            else:
                value_map[block_id] = block

    return key_map, value_map, block_map

def get_kv_relationship(key_map, value_map, block_map):
    """
    Map the key-value relationships from the blocks.
    """
    kvs = defaultdict(list)
    for block_id, key_block in key_map.items():
        value_block = find_value_block(key_block, value_map)
        key = get_text(key_block, block_map)
        val = get_text(value_block, block_map)
        kvs[key].append(val)
    return kvs

def find_value_block(key_block, value_map):
    """
    Find the value block associated with the key block.
    """
    for relationship in key_block['Relationships']:
        if relationship['Type'] == 'VALUE':
            for value_id in relationship['Ids']:
                value_block = value_map[value_id]
    return value_block

def get_text(result, blocks_map):
    """
    Extract text from a block of text.
    """
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    word = blocks_map[child_id]
                    if word['BlockType'] == 'WORD':
                        text += word['Text'] + ' '
                    if word['BlockType'] == 'SELECTION_ELEMENT':
                        if word['SelectionStatus'] == 'SELECTED':
                            text += 'X'
    return text.strip()

def write_kvs_to_excel(kvs, ws):
    """
    Write key-value pairs into the existing worksheet.
    """
    for key, values in kvs.items():
        for value in values:
            ws.append([key, value])

def process_images(images):
    """
    Process multiple images and create a single Excel file.
    """
    # Create a new workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Key-Value Pairs"

    # Add headers
    ws.append(["Key", "Value"])

    # Process each image
    for image in images:
        key_map, value_map, block_map = get_kv_map(image)
        kvs = get_kv_relationship(key_map, value_map, block_map)
        write_kvs_to_excel(kvs, ws)

    # Save the workbook to a BytesIO object
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return output

def main(images):
    output_file = process_images(images)
    return output_file

