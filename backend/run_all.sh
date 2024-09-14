#!/bin/bash
# Run Flask backend in the backend folder
python backend/app.py &

# Run Streamlit frontend in the frontend folder
streamlit run ../frontend/main.py &