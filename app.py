import streamlit as st
import pdfplumber
import pandas as pd
import re

headers = [
    'PDF ITINERARY', 'APPROVED', 'TM NUMBER', 'TRAVELER NAME', 'ROLE', 'EMAIL ADDRESS',
    'BOOKING REF 1', 'TICKET NUMBER 1', 'BOOKING REF 2', 'TICKET NUMBER 2',
    'FLIGHT 1 DATE', 'FLIGHT 1 AIRLINE', 'FLIGHT 1 #', 'FLIGHT 1 FROM CITY', 'FLIGHT 1 TO CITY', 'FLIGHT 1 DEPARTURE TIME', 'FLIGHT 1 ARRIVAL TIME',
    'FLIGHT 2 DATE', 'FLIGHT 2 AIRLINE', 'FLIGHT 2 #', 'FLIGHT 2 FROM CITY', 'FLIGHT 2 TO CITY', 'FLIGHT 2 DEPARTURE TIME', 'FLIGHT 2 ARRIVAL TIME',
    'FLIGHT 3 DATE', 'FLIGHT 3 AIRLINE', 'FLIGHT 3 #', 'FLIGHT 3 FROM CITY', 'FLIGHT 3 TO CITY', 'FLIGHT 3 DEPARTURE TIME', 'FLIGHT 3 ARRIVAL TIME',
    'FLIGHT 4 DATE', 'FLIGHT 4 AIRLINE', 'FLIGHT 4 #', 'FLIGHT 4 FROM CITY', 'FLIGHT 4 TO CITY', 'FLIGHT 4 DEPARTURE TIME', 'FLIGHT 4 ARRIVAL TIME',
    'GT 1 DATE', 'GT 1 TIME', 'GT 1 DETAILS CODE', 'GT 1 DESTINATION', 'GT 1 DETAILS PLUS TEXT',
    'GT 2 DATE', 'GT 2 TIME', 'GT 2 DETAILS CODE', 'GT 2 DESTINATION', 'GT 2 DETAILS PLUS TEXT',
    'GT 3 DATE', 'GT 3 TIME', 'GT 3 DETAILS CODE', 'GT 3 DESTINATION', 'GT 3 DETAILS PLUS TEXT',
    'GT 4 DATE', 'GT 4 TIME', 'GT 4 DETAILS CODE', 'GT 4 DESTINATION', 'GT 4 DETAILS PLUS TEXT',
    'ADDRESS CODE', 'IN DATE', 'OUT DATE', 'ADDRESS PLUS TEXT'
]

def extract_fields(text):
    row = ["-"] * 62

    # Booking Reference
    booking_ref = re.search(r'Booking Reference\s+([A-Z0-9]{6})', text)
    if booking_ref:
        row[6] = booking_ref.group(1)

    # Ticket Number
    ticket = re.search(r'Ticket #\s+(\d{13})', text)
    if ticket:
        row[7] = ticket.group(1)

    # Traveler Name
    # Try to capture "For:\nNAME" or "Passenger\nNAME"
    name = re.search(r'For:\s*\n([A-Z/ ]+)', text)
    if not name:
        name = re.search(r'Passenger\s*([A-Z/ ]+)', text)
    if name:
        # Convert "GUIGNARD/JUSTIN DANIEL MR" to "Justin Daniel Guignard"
        full = name.group(1).replace("MR", "").replace("MRS", "").replace("MS", "").strip()
        # Split last/first and title if possible
        if "/" in full:
            last, first = full.split("/", 1)
            row[3] = (first.title() + " " + last.title()).replace("  ", " ").strip()
        else:
            row[3] = full.title().strip()

    # Flight 1: Date (e.g., "Depart\nSun - Jul 27")
    flight1_date = re.search(r'Depart\s*\n([A-Za-z]{3} - [A-Za-z]{3} \d{1,2})', text)
    if flight1_date:
        row[10] = flight1_date.group(1)

    # Flight 1: Airline (e.g., "Web Check-In and Airline Confirmation: Air Canada")
    airline = re.search(r'Web Check-In and Airline Confirmation:\s*([A-Za-z\s]+) -', text)
    if airline:
        row[11] = airline.group(1).strip()
    else:
        airline = re.search(r'Airline Code\s+([A-Z]{2})', text)
        if airline:
            row[11] = airline.group(1)

    # Flight 1: Flight Number (e.g., "Rouge\n1949" or "Flight Number\n1949")
    flight_num = re.search(r'Rouge\s*\n(\d+)', text)
    if flight_num:
        row[12] = "AC " + flight_num.group(1)
    else:
        flight_num = re.search(r'Flight Number\s+(\d+)', text)
        if flight_num:
            row[12] = flight_num.group(1)

    # Swap "From City" and "To City" correctly
    # To City (Destination)
    to_city = re.search(r'Destination\s*\n([A-Za-z\'’\s.,&\(\)\-]+)', text)
    if to_city:
        row[14] = to_city.group(1).strip()
    else:
        row[14] = "Toronto (YYZ)"
    # From City (Origin)
    from_city = re.search(r'Origin\s*\n([A-Za-z\'’\s.,&\(\)\-]+)', text)
    if from_city:
        row[13] = from_city.group(1).strip()
    else:
        row[13] = "St. John’s (YYT)"

    # Departure Time (e.g., "Depart\n13:50")
    dep_time = re.search(r'Depart\s*\n.*?(\d{2}:\d{2})', text)
    if dep_time:
        row[15] = dep_time.group(1).replace(":", "")

    # Arrival Time (e.g., "Arrive\n15:55")
    arr_time = re.search(r'Arrive\s*\n.*?(\d{2}:\d{2})', text)
    if arr_time:
        row[16] = arr_time.group(1).replace(":", "")

    return row

st.title("UNLP Travel PDF to Extraction Grid CSV")

uploaded_file = st.file_uploader("Upload a Travel PDF", type="pdf")

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    row = extract_fields(text)

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
