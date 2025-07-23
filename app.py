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
    # Each row: 62 columns
    row = ["-"] * 62

    # Find all flights in the text (split by 'Depart\n', skip the first empty chunk)
    flights = re.split(r"(?=Depart\s*\n)", text)[1:]

    for i, flight in enumerate(flights[:4]):
        base = 10 + i * 7  # where this flight's info starts

        # Date (look for 'Depart\nMon - Jul 28' or 'Depart\nMon\n-\nJul\n28')
        date_match = re.search(r"Depart\s*\n([A-Za-z]{3})\s*-?\s*([A-Za-z]{3})\s*(\d{1,2})", flight)
        dow, mon, day = (date_match.groups() if date_match else ("", "", ""))
        if dow and mon and day:
            row[base] = format_date(dow, mon, day)
        else:
            row[base] = "-"

        # Airline (main carrier, skip "Jazz", "Rouge", "Cityline" etc.)
        airline_match = re.search(r"([A-Za-z\s]+?)\n\d{2,4}", flight)
        airline = airline_match.group(1).strip() if airline_match else "-"
        # Remove unwanted words (add/remove as per your carriers)
        for suffix in ["Jazz", "Rouge", "Cityline", "Ltd", "Gmbh", "Airlines", "Airways"]:
            if airline.lower().endswith(suffix.lower()):
                airline = airline[:-(len(suffix))].strip()
        row[base+1] = title_case(airline)

        # Flight #: "1675" or "AC 1675" (look for 2-4 digits after airline)
        flight_num = re.search(r"\n(\d{2,4})\n", flight)
        if flight_num:
            code = "AC" if "Air Canada" in airline else ""
            row[base+2] =
