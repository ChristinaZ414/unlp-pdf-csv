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

    # Extract traveler name
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

    # Booking reference
    booking_match = re.search(r"Booking Reference\s+([A-Z0-9]{6})", text)
    if not booking_match:
        booking_match = re.search(r"Airline Confirmation: [A-Z]+ - ([A-Z0-9]{6})", text)
    if booking_match:
        row[6] = booking_match.group(1)

    # Ticket number
    ticket_match = re.search(r"Ticket #\s*(\d{13})", text)
    if not ticket_match:
        ticket_match = re.search(r"TKT (\d{13})", text)
    if ticket_match:
        row[7] = ticket_match.group(1)

    # Find flight blocks by splitting on 'Origin\n'
    flight_blocks = re.split(r'Origin\n', text)[1:]

    airline_codes = {
        "Air Canada": "AC",
        "Westjet": "WS",
        "Lufthansa": "LH",
        "Porter": "PD",
        "United": "UA"
    }

    for i, block in enumerate(flight_blocks[:4]):
        base = 10 + i * 7

        # Airline name
        airline_match = re.search(r'(Air Canada(?: Rouge)?|Westjet|Deutsche Lufthansa AG|United Airlines|Porter Airlines)', block)
        airline = airline_match.group(1).replace("Rouge", "").strip() if airline_match else "-"
        row[base+1] = title_case(airline)

        # Flight number (3-4 digits)
        flight_num_match = re.search(r'(?:^|\n)(\d{3,4})\n', block)
        flight_num = flight_num_match.group(1) if flight_num_match else "-"
        airline_code = airline_codes.get(airline, "")
        if airline_code != "-" and flight_num != "-":
            row[base+2] = f"{airline
