import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Hotel Booking ERP", layout="wide")

# Load existing data (example from CSV)
try:
    bookings = pd.read_csv("data/Bookings.csv")
except FileNotFoundError:
    bookings = pd.DataFrame(columns=["BookingID","Date","HotelCode","RoomType","Rooms","Nights","CustomerCode","EmployeeCode"])

st.title("📑 Hotel Booking ERP")

with st.form("new_booking"):
    st.subheader("Add New Booking")
    booking_id = st.text_input("Booking ID")
    booking_date = st.date_input("Booking Date", date.today())
    hotel_code = st.text_input("Hotel Code")
    room_type = st.selectbox("Room Type", ["ثنائي","ثلاثي","رباعي","خماسي"])
    rooms = st.number_input("No. of Rooms",1)
    nights = st.number_input("Nights",1)
    customer_code = st.text_input("Customer Code")
    employee_code = st.text_input("Employee Code")

    submitted = st.form_submit_button("Save Booking")
    if submitted:
        ppl_per_room = {"ثنائي":2,"ثلاثي":3,"رباعي":4,"خماسي":5}.get(room_type,1)
        no_guests = ppl_per_room * rooms

        new_row = {
            "BookingID": booking_id,
            "Date": booking_date,
            "HotelCode": hotel_code,
            "RoomType": room_type,
            "Rooms": rooms,
            "Nights": nights,
            "CustomerCode": customer_code,
            "EmployeeCode": employee_code
        }
        bookings = pd.concat([bookings, pd.DataFrame([new_row])], ignore_index=True)
        bookings.to_csv("data/Bookings.csv", index=False)
        st.success(f"Booking saved with {no_guests} guests.")

st.subheader("Existing Bookings")
st.dataframe(bookings)
