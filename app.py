import streamlit as st
from textract.lambda_handler import main

# Navbar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Upload File", "About"])

# Page logic
if page == "Home":
    st.title("Welcome to the Streamlit App")
    st.write("Use the navbar to navigate to different sections.")

elif page == "Upload File":
    st.title("File Upload")
    uploaded_file = st.file_uploader("Drag and drop or select a file", type=['png', 'jpeg'])

    if uploaded_file is not None:
        st.write("File uploaded successfully!")
        file_details = {
            "filename": uploaded_file.name, 
            "filetype": uploaded_file.type, 
            "filesize": uploaded_file.size
        }
        st.write(file_details)

        # Pass the uploaded image to the main function
        output_file = main(uploaded_file)

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
    st.write("This is an example Streamlit app with a drag-and-drop file upload feature and a navbar.")

# Run the app with `streamlit run app.py`
