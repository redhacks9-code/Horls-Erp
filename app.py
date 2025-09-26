
import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

DB_PATH = "hotel_erp.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    # Bookings
    c.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        client_name TEXT,
        hotel TEXT,
        room_type TEXT,
        rooms INTEGER,
        nights INTEGER,
        purchase_price REAL,
        selling_price REAL,
        total_cost REAL,
        total_selling REAL,
        profit REAL,
        employee_responsible TEXT,
        created_at TEXT
    )""")
    # Employees
    c.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        job_title TEXT,
        salary REAL,
        advance REAL
    )""")
    # Payments
    c.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER,
        amount REAL,
        method TEXT,
        date TEXT,
        note TEXT
    )""")
    # Vouchers (archive)
    c.execute("""
    CREATE TABLE IF NOT EXISTS vouchers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER,
        type TEXT,
        amount REAL,
        created_at TEXT,
        pdf_html TEXT
    )""")
    conn.commit()
    conn.close()

def insert_booking(data):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    INSERT INTO bookings (company, client_name, hotel, room_type, rooms, nights, purchase_price, selling_price, total_cost, total_selling, profit, employee_responsible, created_at)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        data['company'], data['client_name'], data['hotel'], data['room_type'],
        data['rooms'], data['nights'], data['purchase_price'], data['selling_price'],
        data['total_cost'], data['total_selling'], data['profit'], data['employee_responsible'],
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()

def get_table(name):
    conn = get_conn()
    df = pd.read_sql_query(f"SELECT * FROM {name}", conn)
    conn.close()
    return df

def create_voucher(booking):
    # Return a simple HTML string representing a printable voucher
    html = f"""
    <html><body>
    <h2>Voucher / Booking Invoice</h2>
    <p><strong>Company:</strong> {booking['company']}</p>
    <p><strong>Client:</strong> {booking['client_name']}</p>
    <p><strong>Hotel:</strong> {booking['hotel']} - {booking['room_type']}</p>
    <p><strong>Rooms x Nights:</strong> {booking['rooms']} x {booking['nights']}</p>
    <p><strong>Total Selling:</strong> {booking['total_selling']}</p>
    <p><strong>Paid:</strong> {booking.get('paid', 0)}</p>
    <p><strong>Remaining:</strong> {float(booking['total_selling']) - float(booking.get('paid', 0))}</p>
    <hr/>
    <p>Generated: {datetime.utcnow().isoformat()}</p>
    </body></html>
    """
    return html

st.set_page_config(page_title="Hotel ERP - Streamlit", layout="wide")
st.title("Hotel Booking ERP (Streamlit) — Basic Web Version")

init_db()

menu = ["Dashboard","Bookings","Employees","Payments","Vouchers","ERP Summary","Download"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Dashboard":
    st.header("Quick Overview")
    bookings = get_table("bookings")
    payments = get_table("payments")
    employees = get_table("employees")
    st.metric("Total Bookings", len(bookings))
    st.metric("Total Employees", len(employees))
    st.metric("Total Payments", payments['amount'].sum() if not payments.empty else 0)
    st.dataframe(bookings)

elif choice == "Bookings":
    st.header("Bookings")
    with st.form("new_booking"):
        company = st.text_input("Company (leave empty if individual)")
        client_name = st.text_input("Client name")
        hotel = st.text_input("Hotel name")
        room_type = st.text_input("Room type")
        rooms = st.number_input("Rooms", min_value=1, value=1)
        nights = st.number_input("Nights", min_value=1, value=1)
        purchase_price = st.number_input("Purchase price (per room/night)", min_value=0.0, format="%.2f")
        selling_price = st.number_input("Selling price (per room/night)", min_value=0.0, format="%.2f")
        employee_responsible = st.text_input("Employee responsible")
        submitted = st.form_submit_button("Create booking")
        if submitted:
            total_cost = rooms * nights * purchase_price
            total_selling = rooms * nights * selling_price
            profit = total_selling - total_cost
            data = {
                'company': company, 'client_name': client_name, 'hotel': hotel, 'room_type': room_type,
                'rooms': rooms, 'nights': nights, 'purchase_price': purchase_price, 'selling_price': selling_price,
                'total_cost': total_cost, 'total_selling': total_selling, 'profit': profit,
                'employee_responsible': employee_responsible
            }
            insert_booking(data)
            st.success("Booking created.")
    st.subheader("All bookings")
    st.dataframe(get_table("bookings"))

elif choice == "Employees":
    st.header("Employees")
    with st.form("new_employee"):
        name = st.text_input("Name")
        job = st.text_input("Job title")
        salary = st.number_input("Salary", min_value=0.0, format="%.2f")
        advance = st.number_input("Advance (savings / loan)", min_value=0.0, format="%.2f")
        submit_emp = st.form_submit_button("Add employee")
        if submit_emp:
            conn = get_conn()
            c = conn.cursor()
            c.execute("INSERT INTO employees (name, job_title, salary, advance) VALUES (?,?,?,?)",
                      (name, job, salary, advance))
            conn.commit()
            conn.close()
            st.success("Employee added")
    st.dataframe(get_table("employees"))

elif choice == "Payments":
    st.header("Record Payments")
    bookings = get_table("bookings")
    if bookings.empty:
        st.info("No bookings yet.")
    else:
        booking_id = st.selectbox("Select booking", bookings['id'].tolist())
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        method = st.selectbox("Method", ["Cash","Bank Transfer","Card","Other"])
        note = st.text_input("Note")
        if st.button("Record payment"):
            conn = get_conn()
            c = conn.cursor()
            c.execute("INSERT INTO payments (booking_id, amount, method, date, note) VALUES (?,?,?,?,?)",
                      (booking_id, amount, method, datetime.utcnow().isoformat(), note))
            conn.commit()
            conn.close()
            st.success("Payment recorded.")
    st.subheader("Payments")
    st.dataframe(get_table("payments"))

elif choice == "Vouchers":
    st.header("Create / Archive Vouchers")
    bookings = get_table("bookings")
    if not bookings.empty:
        bsel = st.selectbox("Booking", bookings['id'].tolist())
        booking_row = bookings[bookings['id']==bsel].iloc[0].to_dict()
        # calculate paid
        payments = get_table("payments")
        paid = payments[payments['booking_id']==bsel]['amount'].sum() if not payments.empty else 0
        booking_row['paid'] = paid
        st.write(booking_row)
        if st.button("Generate Voucher (HTML) and Archive"):
            html = create_voucher(booking_row)
            conn = get_conn()
            c = conn.cursor()
            c.execute("INSERT INTO vouchers (booking_id, type, amount, created_at, pdf_html) VALUES (?,?,?,?,?)",
                      (bsel, "booking_voucher", booking_row['total_selling'], datetime.utcnow().isoformat(), html))
            conn.commit()
            conn.close()
            st.success("Voucher created and archived.")
    st.subheader("Archived vouchers")
    st.dataframe(get_table("vouchers"))

elif choice == "ERP Summary":
    st.header("ERP Summary")
    bookings = get_table("bookings")
    payments = get_table("payments")
    employees = get_table("employees")
    total_revenue = bookings['total_selling'].sum() if not bookings.empty else 0
    total_costs = bookings['total_cost'].sum() if not bookings.empty else 0
    total_profit = bookings['profit'].sum() if not bookings.empty else 0
    st.metric("Total Revenue", f"{total_revenue:.2f}")
    st.metric("Total Costs", f"{total_costs:.2f}")
    st.metric("Total Profit", f"{total_profit:.2f}")
    st.subheader("Open liabilities by employee (Bookings assigned)")
    if not bookings.empty:
        df = bookings.groupby('employee_responsible').agg({'total_selling':'sum','profit':'sum','id':'count'}).reset_index()
        df.columns = ['Employee','Total Selling','Total Profit','Bookings Count']
        st.dataframe(df)
    else:
        st.info("No bookings to show.")

elif choice == "Download":
    st.header("Download app (zip)")
    st.write("This package contains a runnable Streamlit app. Run: pip install -r requirements.txt ; streamlit run app.py")
    with open("hotel_erp.db","rb") as f:
        st.download_button("Download sample DB (hotel_erp.db)", f, file_name="hotel_erp.db")
    with open("package.zip","rb") as f:
        st.download_button("Download app package (hotel_erp_streamlit.zip)", f, file_name="hotel_erp_streamlit.zip")
