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
    return text.title().replace("’", "'") if text else "-"

def format_time(t):
    # Input: '08:25', Output: '0825'
    if not t or not re.match(r"\d{2}:\d{2}", t):
        return "-"
    return t.replace(":", "")

def format_date(dow, mon, day):
    # Input: 'Mon', 'Jul', '28' -> 'Monday July 28'
    try:
        dt = datetime.strptime(f"{dow} {mon} {day}", "%a %b %d")
        return dt.strftime("%A %B %-d")
    except Exception:
        return "-"

def extract_flights(text):
    row = ["-"] * 62
    flights = re.split(r"(?=Depart\s*\n)", text)[1:]

    for i, flight in enumerate(flights[:4]):
        base = 10 + i * 7

        # Date (e.g. 'Depart\nMon - Jul 28')
        date_match = re.search(r"Depart\s*\n([A-Za-z]{3})\s*-?\s*([A-Za-z]{3})\s*(\d{1,2})", flight)
        if date_match:
            dow, mon, day = date_match.groups()
            row[base] = format_date(dow, mon, day)
        else:
            row[base] = "-"

        # Airline (main carrier only)
        airline_match = re.search(r"([A-Za-z\s]+?)\n\d{2,4}", flight)
        airline = airline_match.group(1).strip() if airline_match else "-"
        for suffix in ["Jazz", "Rouge", "Cityline", "Ltd", "Gmbh", "Airlines", "Airways"]:
            if airline.lower().endswith(suffix.lower()):
                airline = airline[:-(len(suffix))].strip()
        row[base+1] = title_case(airline)

        # Flight # (with airline code if needed)
        flight_num = re.search(r"\n(\d{2,4})\n", flight)
        if flight_num:
            code = "AC" if "Air Canada" in airline else ""
            row[base+2] = f"{code} {flight_num.group(1)}".strip() if code else flight_num.group(1)
        else:
            row[base+2] = "-"

        # From City
        from_match = re.search(r"Origin\n([A-Za-z\s'\-]+)", flight)
        from_city = from_match.group(1).strip() if from_match else "-"
        from_code = re.search(r"\(([A-Za-z]{3})\)", flight)
        from_val = f"{title_case(from_city)} ({from_code.group(1).upper()})" if from_city != "-" and from_code else title_case(from_city)
        row[base+3] = from_val

        # To City
        to_match = re.search(r"Destination\n([A-Za-z\s',\-\(\)]+)", flight)
        to_city = to_match.group(1).strip() if to_match else "-"
        to_code = re.search(r"Destination.*\(([A-Za-z]{3})\)", flight)
        to_val = f"{title_case(to_city)} ({to_code.group(1).upper()})" if to_city != "-" and to_code else title_case(to_city)
        row[base+4] = to_val

        # Departure Time
        dep_time_match = re.search(r"Depart\s*\n(?:[A-Za-z]{3} - [A-Za-z]{3} \d{1,2}\n)?(\d{2}:\d{2})", flight)
        dep_time = format_time(dep_time_match.group(1)) if dep_time_match else "-"
        row[base+5] = dep_time

        # Arrival Time
        arr_time_match = re.search(r"Arrive\s*\n(?:[A-Za-z]{3} - [A-Za-z]{3} \d{1,2}\n)?(\d{2}:\d{2})", flight)
        arr_time = format_time(arr_time_match.group(1)) if arr_time_match else "-"
        row[base+6] = arr_time

    return row

st.title("UNLP Travel PDF to Extraction Grid CSV")

uploaded_file = st.file_uploader("Upload a Travel PDF", type="pdf")

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    row = extract_flights(text)

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
