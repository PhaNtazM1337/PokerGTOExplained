# import streamlit as st
# import requests

# st.set_page_config(
#     page_title="Image Upload and Comment",
#     page_icon="📷",
#     layout="centered",  
#     initial_sidebar_state="auto",  
# )

# st.title("Upload an Image and Add Comments")

# with st.form(key='upload_form'):
#     uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
#     col1, col2 = st.columns(2)

#     with col1:
#         if uploaded_file is not None:
#             st.image(uploaded_file, caption='Preview Image', use_column_width=True)

#     with col2:
#         comments = st.text_area("Enter your comments here...")

#     submit_button = st.form_submit_button(label='Submit')


# if submit_button:
#     if uploaded_file is not None and comments:
#         data = {'comments': comments}
#         response = requests.post('http://127.0.0.1:5000/upload', files={'image': uploaded_file}, data = data)
#         st.success('Your image and comments have been submitted successfully!')
#     else:
#         st.warning('Please upload an image and enter comments before submitting.')

import streamlit as st
import requests

# Set page configuration
st.set_page_config(
    page_title="Image Upload, Type Selection, and Comment",
    page_icon="📷",
    layout="centered",
    initial_sidebar_state="auto",
)

# Title of the app
st.title("Upload an Image, Select Type, and Add Comments")

# Form for uploading image, selecting type, and adding comments
with st.form(key='upload_form'):
    # File uploader widget
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    # Type selection radio button (Type 1 or Type 2)
    image_type = st.radio("Select Image Type:", ('Game', 'GTO'))

    # Display uploaded image in the first column
    col1, col2 = st.columns(2)

    with col1:
        if uploaded_file is not None:
            st.image(uploaded_file, caption='Preview Image', use_column_width=True)

    # Comments text area in the second column
    with col2:
        comments = st.text_area("Enter your comments here...")

    # Submit button
    submit_button = st.form_submit_button(label='Submit')

# When the form is submitted
if submit_button:
    if uploaded_file is not None and comments:
        # Determine if the image is Type 1 or Type 2 (send as True/False)
        is_game = image_type == 'Game'

        # Prepare the form data
        data = {'comments': comments, 'is_game': is_game}

        # Send image and form data to the backend
        response = requests.post('http://127.0.0.1:5000/upload', files={'image': uploaded_file}, data=data)

        if response.status_code == 200:
            st.success('Your image, type, and comments have been submitted successfully!')
        else:
            st.error('Error submitting the image and data. Please try again.')
    else:
        st.warning('Please upload an image and enter comments before submitting.')

