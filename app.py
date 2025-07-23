import streamlit as st
import pdfplumber

st.title("Raw PDF Text Viewer")

uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    st.text_area("Extracted Text", text, height=600)
