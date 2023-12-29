# Import necessary libraries
from dotenv import load_dotenv
import streamlit as st
import os
import io
from PyPDF2 import PdfReader
import google.generativeai as genai
import base64
from PIL import Image

# Load environment variables from .env file
load_dotenv()

# # Load and display the logo
# logo = Image.open("logo.png")  # Replace with the path to your logo file
# st.image(logo, width=200) 

# st.set_page_config(page_title="PDFAnswer AI", layout="wide")

# Configure API key for Google Generative AI
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("Google API key not found. Please check your .env file.")
    st.stop()
genai.configure(api_key=api_key)

# Function to get responses from Gemini Pro model (text-only)
def get_gemini_response(input_prompt, input_text):
    model = genai.GenerativeModel('gemini-pro')  # Using text-only model
    response = model.generate_content([input_prompt, input_text])
    return response.text

# Function to extract text from a PDF
def extract_text_from_pdf(uploaded_file):
    if uploaded_file is not None:
        reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    else:
        st.warning("No file uploaded. Please upload a PDF file.")
        return None

# Function to display the uploaded PDF file
def display_pdf(uploaded_file):
    base64_pdf = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)

# Streamlit app setup
st.set_page_config(page_title="PDFAnswer AI")
st.header("This is Your PDFAnswer AI")
# App description
st.markdown("""
    This application allows you to upload a PDF document and provides an analysis of its content using the Google Gemini AI model.
    Simply upload a PDF, and ask your Question.
""")

# User input and file uploader
uploaded_file = st.file_uploader("Upload a PDF file from where you want answer", type=["pdf"])

# Display the uploaded PDF
if uploaded_file is not None:
    display_pdf(uploaded_file)

# Analysis button and user question
input_text = st.text_input("Enter your Question: ", key="input")
submit = st.button("Proceed with your question")

# Input prompt for the model
input_prompt = """
               You are an AI expert in reading and analyzing PDF documents.
               You will receive a PDF and you will have to extract and interpret information based on its content.
               """

# Process analysis on button click
if submit:
    pdf_text = extract_text_from_pdf(uploaded_file)
    if pdf_text:
        with st.spinner('Analyzing your PDF to find Answer'):
            response = get_gemini_response(input_prompt, pdf_text + "\n" + input_text)
            st.subheader("Analysis Result")
            st.write(response)
