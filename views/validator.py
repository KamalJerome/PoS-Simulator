# validator.py
import streamlit as st
import mysql.connector
import pandas as pd

# Connect to the MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mypass",
    database="blockchain_db"
)
cursor = conn.cursor()

# Function to add or update a validator
def add_or_update_validator(validator_id, stake):
    cursor.execute("REPLACE INTO validators (id, stake) VALUES (%s, %s)", (validator_id, stake))
    conn.commit()
    st.success(f"Added/updated {validator_id} with stake {stake}")

# Function to list all validators in a table format using pandas
def list_validators():
    cursor.execute("SELECT id, stake FROM validators")
    validators = cursor.fetchall()
    
    # Create a pandas DataFrame
    df = pd.DataFrame(validators, columns=["ID", "Stake"])
    
    # Display the DataFrame as a table
    st.write("### List of Validators")
    st.dataframe(df)

# Streamlit UI
st.title("Blockchain - PoS Validators CRUD")

# Add or Update Validator Form
with st.form(key="validator_form"):
    validator_id = st.text_input("Validator ID")
    stake = st.number_input("Stake", min_value=0)
    submit_button = st.form_submit_button("Add/Update Validator")
    if submit_button:
        add_or_update_validator(validator_id, stake)

# View Validators
if st.button("View All Validators"):
    list_validators()

# Close the database connection when done
cursor.close()
conn.close()
