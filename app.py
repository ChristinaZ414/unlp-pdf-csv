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
    return text.title().replace("’", "'").replace("`", "'") if text else "-"

def format_time(t):
    if not t or not re.match(r"\d{1,2}:\d{2}", t):
        return "-"
    parts = t.split(":")
    return parts[0].zfill(2) + parts[1]

def format_date(dow, mon, day):
    try:
        dt = datetime.strptime(f"{dow} {mon} {day}", "%a %b %d")
        return dt.strftime("%A %B %-d")
    except Exception:
        return "-"

def extract_fields(text):
    row = ["-"] * 62
    try:
        # Name
        name_match = re.search(r"For:\s*([A-Z/ ]+)", text)
        if not name_match:
            name_match = re.search(r"Passenger\s*([A-Z/ ]+)", text)
        if name_match:
            full = name_match.group(1).replace("MS", "").replace("MR", "").replace("MRS", "").strip()
            if "/" in full:
                last, first = full.split("/", 1)
                row[3] = (first.title().strip() + " " + last.title().strip()).replace("  ", " ").strip()
            else:
                row[3] = full.title().strip()

        # Booking Ref
        booking_match = re.search(r"Air Canada - ([A-Z0-9]{6})", text)
        if not booking_match:
            booking_match = re.search(r"Booking Reference\s+([A-Z0-9]{6})", text)
        if booking_match:
            row[6] = booking_match.group(1)

        # Ticket #
        ticket_match = re.search(r"Ticket #\s*(\d{13})", text)
        if not ticket_match:
            ticket_match = re.search(r"TKT (\d{13})", text)
        if ticket_match:
            row[7] = ticket_match.group(1)

        # Flights
        flight_blocks = re.split(r'Origin\n', text)[1:]
        for idx, block in enumerate(flight_blocks[:4]):
            base = 10 + idx * 7

            # Airline
            airline = "-"
            air_line_block = re.search(r'(Air Canada(?: Rouge)?|Westjet|Deutsche Lufthansa AG|United Airlines|Porter Airlines)', block)
            if air_line_block:
                airline = air_line_block.group(1).replace("Rouge", "").strip()
            row[base+1] = title_case(airline)

            # Flight #
            flight_num = re.search(r'(?:^|\n)(\d{3,4})\n', block)
            if not flight_num:
                flight_num = re.search(r'(?:Flight|Fl) #\s*(\d{3,4})', block)
            if flight_num:
                code = ""
                if "Air Canada" in airline:
                    code = "AC"
                elif "Westjet" in airline:
                    code = "WS"
                elif "Lufthansa" in airline:
                    code = "LH"
                elif "Porter" in airline:
                    code = "PD"
                elif "United" in airline:
                    code = "UA"
                if code:
                    row[base+2] = f"{code} {flight_num.group(1)}"
                else:
                    row[base+2] = flight_num.group(1)

            # FROM CITY
            lines = block.split('\n')
            from_city = lines[0].strip() if lines else "-"
            from_code = re.search(r'\(([A-Z]{3})\)', block)
            from_val = f"{title_case(from_city)} ({from_code.group(1)})" if from_city != "-" and from_code else title_case(from_city)
            row[base+3] = from_val

            # TO CITY
            to_city_match = re.search(r'Destination\n([A-Za-z\',\. \-()]+)', block)
            to_city = to_city_match.group(1).strip() if to_city_match else "-"
            to_code = re.search(r'Destination.*\(([A-Z]{3})\)', block)
            if to_code:
                to_val = f"{title_case(to_city)} ({to_code.group(1)})"
            else:
                to_val = title_case(to_city)
            row[base+4] = to_val

            # DATE
            date_match = re.search(r'Depart\n([A-Za-z]{3}) - ([A-Za-z]{3}) (\d{1,2})', block)
            if date_match:
                dow, mon, day = date_match.groups()
                row[base] = format_date(dow, mon, day)
            else:
                row[base] = "-"

            # DEPART TIME
            dep_time_match = re.search(r'Arpt [^\n]*\n(\d{1,2}:\d{2})', block)
            if not dep_time_match:
                dep_time_match = re.search(r'Depart\s*[A-Za-z \-]*\n(\d{1,2}:\d{2})', block)
            if dep_time_match:
                row[base+5] = format_time(dep_time_match.group(1))

            # ARRIVAL TIME
            arr_time_match = re.search(r'\n(\d{1,2}:\d{2})\n', block)
            if not arr_time_match:
                arr_time_match = re.search(r'Arrive[^\n]*\n(\d{1,2}:\d{2})', block)
            if arr_time_match:
