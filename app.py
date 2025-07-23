import streamlit as st
import pdfplumber
import pandas as pd
import re
from datetime import datetime

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

def title_case(text):
    if not text or text == "-":
        return "-"
    return text.title().replace("’", "'").replace("`", "'")

def format_time(t):
    if not t or not re.match(r"\d{1,2}:\d{2}", t):
        return "-"
    h, m = t.split(":")
    return h.zfill(2) + m

def format_date(dow, mon, day):
    try:
        dt = datetime.strptime(f"{dow} {mon} {day}", "%a %b %d")
        return dt.strftime("%A %B %-d")
    except Exception:
        return "-"

def extract_fields(text):
    row = ["-"] * 62

    # Name
    name_match = re.search(r"For:\s*([A-Z/ ]+)", text)
    if not name_match:
        name_match = re.search(r"Passenger\s*([A-Z/ ]+)", text)
    if name_match:
        full = name_match.group(1).replace("MR", "").replace("MS", "").replace("MRS", "").strip()
        if "/" in full:
            last, first = full.split("/", 1)
            row[3] = f"{first.title().strip()} {last.title().strip()}"
        else:
            row[3] = full.title().strip()

    # Booking Reference
    booking_match = re.search(r"Booking Reference\s+([A-Z0-9]{6})", text)
    if booking_match:
        row[6] = booking_match.group(1)

    # Ticket Number
    ticket_match = re.search(r"Ticket #\s*(\d{13})", text)
    if ticket_match:
        row[7] = ticket_match.group(1)

    # Extract first flight block between "Origin" and next "Origin" or end
    flights = re.findall(r"Origin\n(.*?)(?=Origin\n|$)", text, re.DOTALL)
    if flights:
        block = flights[0]

        # Airline (first line)
        airline_match = re.match(r"([^\n]+)", block)
        airline = airline_match.group(1).strip() if airline_match else "-"
        row[11] = title_case(airline)

        # Flight Number (digits after airline)
        flight_num_match = re.search(r"\n(\d{3,4})", block)
        flight_num = flight_num_match.group(1) if flight_num_match else "-"
        row[12] = flight_num

        # From City and Code
        from_city_match = re.search(r"Origin\n([^\n]+)\n([^\n]+)\n\(([A-Z]{3})\)", text)
        if from_city_match:
            city = from_city_match.group(1).strip()
            code = from_city_match.group(3)
            row[13] = f"{title_case(city)} ({code})"

        # To City and Code
        to_city_match = re.search(r"Destination\n([^\n]+)\n([^\n]+)\n\(([A-Z]{3})\)", block)
        if to_city_match:
            city = to_city_match.group(1).strip()
            code = to_city_match.group(3)
            row[14] = f"{title_case(city)} ({code})"

        # Date
        dep_date_match = re.search(r"Depart\n([A-Za-z]{3}) - ([A-Za-z]{3}) (\d{1,2})", block)
        if dep_date_match:
            dow, mon, day = dep_date_match.groups()
            row[10] = format_date(dow, mon, day)

        # Departure Time
        dep_time_match = re.search(r"Depart\n[^\n]*\n(\d{1,2}:\d{2})", block)
        if dep_time_match:
            row[15] = format_time(dep_time_match.group(1))

        # Arrival Time
        arr_time_match = re.search(r"Arrive\n[^\n]*\n(\d{1,2}:\d{2})", block)
        if arr_time_match:
            row[16] = format_time(arr_time_match.group(1))

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
