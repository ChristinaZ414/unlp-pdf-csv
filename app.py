import streamlit as st
import pdfplumber

st.title("Raw PDF Text Extractor")

uploaded_file = st.file_uploader("Upload a Travel PDF", type="pdf")

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    st.text_area("Extracted PDF Text", text, height=600)
