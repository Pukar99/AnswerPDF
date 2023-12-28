import streamlit as st
import os
import fitz  # PyMuPDF
from PIL import Image
import base64
import google.generativeai as genai
from pytesseract import image_to_string  # For OCR

# Configure Google Generative AI with the API key
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to read PDF and extract text (with OCR for image-based PDFs)
def read_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
            # If text is empty, attempt OCR
            if not text:
                image_bytes = page.get_pixmap().tobytes("png")
                text += image_to_string(Image.open(io.BytesIO(image_bytes)))
    return text

# Function to call the AI model
def get_ai_response(input_text, image_data=None, prompt=None):
    model = genai.GenerativeModel('gemini-pro-vision')
    inputs = [input_text]
    if image_data:
        inputs.append(image_data[0])
    if prompt:
        inputs.append(prompt)
    response = model.generate_content(inputs)
    return response.text

# Streamlit app setup
st.set_page_config(page_title="Student PDF Reader and AI Assistant")
st.header("Student PDF Analysis Application")
st.write("Upload a PDF document and receive AI-driven insights, answers, or summaries.")

# File uploader widget (corrected placement)
uploaded_file = st.file_uploader("Upload a PDF document...", type=["pdf"])

if uploaded_file is not None:
    try:
        # Convert PDF for display
        base64_pdf = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)

        # Extract text from PDF
        pdf_text = read_pdf(uploaded_file)
        if pdf_text.strip() == "":
            st.warning("The PDF could not be processed. Please try a different file.")
        else:
            response = get_ai_response(pdf_text)
            st.subheader("AI Analysis Result")
            st.write(response)

    except Exception as e:
        st.error("An error occurred during analysis. Please try again.")
        st.write(f"Error: {str(e)}")  # Log error for debugging
