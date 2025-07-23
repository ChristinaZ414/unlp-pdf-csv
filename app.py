import streamlit as st
import pdfplumber
import pandas as pd

# 62 headers (order and names match your extraction grid)
headers = [
    'PDF ITINERARY', 'APPROVED', 'TM NUMBER', 'TRAVELER NAME', 'ROLE', 'EMAIL ADDRESS',
    'BOOKING REF 1', 'TICKET NUMBER 1', 'BOOKING REF 2', 'TICKET NUMBER 2',
    'DATE', 'AIRLINE', 'FLIGHT #', 'FROM CITY', 'TO CITY', 'DEPARTURE TIME', 'ARRIVAL TIME',
    'DATE', 'AIRLINE', 'FLIGHT #', 'FROM CITY', 'TO CITY', 'DEPARTURE TIME', 'ARRIVAL TIME',
    'DATE', 'AIRLINE', 'FLIGHT #', 'FROM CITY', 'TO CITY', 'DEPARTURE TIME', 'ARRIVAL TIME',
    'DATE', 'AIRLINE', 'FLIGHT #', 'FROM CITY', 'TO CITY', 'DEPARTURE TIME', 'ARRIVAL TIME',
    'DATE', 'TIME', 'DETAILS     CODE ', 'DESTINATION', 'DETAILS CODE        PLUS TEXT',
    'DATE', 'TIME', 'DETAILS     CODE ', 'DESTINATION', 'DETAILS CODE        PLUS TEXT',
    'DATE', 'TIME', 'DETAILS     CODE ', 'DESTINATION', 'DETAILS CODE        PLUS TEXT',
    'DATE', 'TIME', 'DETAILS     CODE ', 'DESTINATION', 'DETAILS CODE        PLUS TEXT',
    'ADDRESS CODE', 'IN DATE', 'OUT DATE', 'ADDRESS PLUS TEXT'
]

st.title("UNLP Travel PDF to Extraction Grid CSV")

uploaded_file = st.file_uploader("Upload a Travel PDF", type="pdf")

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    # Extraction logic placeholder: fill in here based on your PDF’s layout and data rules
    row = ["-" for _ in range(62)]  # default row: 62 hyphens
    row[0] = "PDF Uploaded"  # Example marker for column 1 (PDF ITINERARY)

    # You’ll add actual field extraction logic to fill each column here

    df = pd.DataFrame([row], columns=headers)
    st.write("Preview of extracted CSV row:")
    st.dataframe(df)

    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="extraction_grid.csv",
        mime='text/csv'
    )
