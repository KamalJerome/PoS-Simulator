import streamlit as st

# --- PAGE SETUP ---
txn = st.Page(
    "views/txn.py",
    title="Transaction QR Generator",
    icon=":material/receipt_long:",
    default=True,
)
crud = st.Page(
    "views/validator.py",
    title="Blockchain Validators",
    icon=":material/gavel:",
)
pos = st.Page(
    "views/posValidator.py",
    title="PoS Transaction Validation",
    icon=":material/fact_check:",
)


# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Proof-of-Work Simulator": [txn, crud, pos],
    }
)

# --- RUN NAVIGATION ---
pg.run()