import streamlit as st
import requests

# Set page configuration to define the app's appearance and behavior
st.set_page_config(
    page_title="Image Upload and Comment",
    page_icon="📷",
    layout="centered",  # Can be "centered" or "wide"
    initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
)

# Display the title of the app
st.title("Upload an Image and Add Comments")

# Create a form to collect user inputs
with st.form(key='upload_form'):
    # Allow the user to upload an image file
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    # Use columns to organize the layout: image preview on the left, comments on the right
    col1, col2 = st.columns(2)

    with col1:
        # If an image has been uploaded, display a preview
        if uploaded_file is not None:
            st.image(uploaded_file, caption='Preview Image', use_column_width=True)

    with col2:
        # Provide a text area for the user to enter comments
        comments = st.text_area("Enter your comments here...")

    # Add a submit button to the form
    submit_button = st.form_submit_button(label='Submit')

# Handle form submission
if submit_button:
    # Check that both an image and comments have been provided
    if uploaded_file is not None and comments:
        # Prepare the data to send to the backend API
        files = {'image': uploaded_file.getvalue()}
        data = {'comments': comments}

        # Simulate sending data to backend API
        # Note: Since the API endpoint is a placeholder, the actual request is commented out
        # Replace 'http://api.example.com/upload' with your actual API endpoint
        # response = requests.post('http://api.example.com/upload', files=files, data=data)

        # Display a success message to the user
        st.success('Your image and comments have been submitted successfully!')
    else:
        # Prompt the user to provide both an image and comments
        st.warning('Please upload an image and enter comments before submitting.')
