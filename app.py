import streamlit as st
import pdfplumber

st.title("PDF Text Extraction Test")

uploaded_file = st.file_uploader("Upload a Travel PDF", type="pdf")

if uploaded_file:
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
        if text.strip():
            st.subheader("Extracted Text from PDF")
            st.text(text)
        else:
            st.write("No text could be extracted from this PDF. It may be a scanned image or not text-based.")
    except Exception as e:
        st.write("An error occurred during extraction:")
        st.write(str(e))
