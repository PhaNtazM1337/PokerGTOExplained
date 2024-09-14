import streamlit as st
import requests

st.set_page_config(
    page_title="Image Upload and Comment",
    page_icon="📷",
    layout="centered",  
    initial_sidebar_state="auto",  
)

st.title("Upload an Image and Add Comments")

with st.form(key='upload_form'):
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    col1, col2 = st.columns(2)

    with col1:
        if uploaded_file is not None:
            st.image(uploaded_file, caption='Preview Image', use_column_width=True)

    with col2:
        comments = st.text_area("Enter your comments here...")

    submit_button = st.form_submit_button(label='Submit')


if submit_button:
    if uploaded_file is not None and comments:
        data = {'comments': comments}
        response = requests.post('http://127.0.0.1:5000/upload', files={'image': uploaded_file}, data = data)
        st.success('Your image and comments have been submitted successfully!')
    else:
        st.warning('Please upload an image and enter comments before submitting.')
