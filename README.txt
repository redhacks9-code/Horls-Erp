Hotel Booking ERP - Streamlit (Basic Web Version)
-------------------------------------------------

How to run:

1. Install dependencies:
   pip install -r requirements.txt

2. Run:
   streamlit run app.py

Notes:
- The app uses a local SQLite DB (hotel_erp.db). A sample empty DB is included.
- Voucher generation produces a simple HTML string stored in the vouchers table; you can open it in the DB or extend the app to render & export as PDF via browser print-to-PDF.

Files:
- app.py: Streamlit application
- requirements.txt
- hotel_erp.db: sample SQLite DB (empty)