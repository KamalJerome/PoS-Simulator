# posValidator.py
import random
import mysql.connector
from pyzbar.pyzbar import decode
from PIL import Image
from cryptography.fernet import Fernet
import streamlit as st

# Connect to the MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mypass",
    database="blockchain_db"
)
cursor = conn.cursor()

# Function to calculate the total stake, excluding attempted validators
def calculate_total_stake(excluded_validators):
    if excluded_validators:  # Only add the NOT IN clause if there are validators to exclude
        placeholders = ",".join(['%s'] * len(excluded_validators))
        query = f"SELECT SUM(stake) FROM validators WHERE id NOT IN ({placeholders})"
        cursor.execute(query, tuple(excluded_validators))
    else:  # If no validators to exclude, just calculate the total stake for all validators
        query = "SELECT SUM(stake) FROM validators"
        cursor.execute(query)
    
    total_stake = cursor.fetchone()[0]
    return total_stake if total_stake else 0

# Function to select a validator based on weighted probability, excluding those in attempted list
def select_validator(attempted_validators):
    if attempted_validators:  # Only add the NOT IN clause if there are validators to exclude
        placeholders = ",".join(['%s'] * len(attempted_validators))
        query = f"SELECT id, stake FROM validators WHERE id NOT IN ({placeholders})"
        cursor.execute(query, tuple(attempted_validators))
    else:  # If no validators to exclude, query all validators
        query = "SELECT id, stake FROM validators"
        cursor.execute(query)
    
    validators = cursor.fetchall()
    
    # Calculate total stake after excluding attempted validators
    total_stake = sum(stake for _, stake in validators)
    if total_stake == 0:
        return None  # No validators left to choose from
    
    pick = random.uniform(0, total_stake)
    cumulative_stake = 0
    
    # Select a validator based on the weighted probability
    for validator_id, stake in validators:
        cumulative_stake += stake
        if pick <= cumulative_stake:
            return validator_id
    return None

# Function to penalize a validator by reducing their stake by 1%
def penalize_validator(validator_id):
    cursor.execute("SELECT stake FROM validators WHERE id = %s", (validator_id,))
    stake = cursor.fetchone()[0]
    new_stake = stake * 0.99  # Reduce stake by 1%
    cursor.execute("UPDATE validators SET stake = %s WHERE id = %s", (new_stake, validator_id))
    conn.commit()
    st.text(f"Validator {validator_id} penalized. New stake: {new_stake}")

# Function to reward a validator by increasing their stake by 10% of the transaction amount
def reward_validator(validator_id, transaction_amount):
    cursor.execute("SELECT stake FROM validators WHERE id = %s", (validator_id,))
    stake = cursor.fetchone()[0]
    bonus = transaction_amount * 0.10
    new_stake = stake + bonus
    cursor.execute("UPDATE validators SET stake = %s WHERE id = %s", (new_stake, validator_id))
    conn.commit()
    st.text(f"Validator {validator_id} rewarded. New stake: {new_stake}")

# Function to validate the transaction with a chance of failure
def validate_transaction(qr_image_path, key):
    failure_chance = 0.1  # Simulate failure rate
    attempted_validators = []  # Track validators that have attempted validation
    
    while True:
        chosen_validator = select_validator(attempted_validators)
        
        if not chosen_validator:
            st.text("Validation failed: all validators have been exhausted.")
            return  # Stop validation as no validators are left
        
        st.text(f"Chosen validator: {chosen_validator}")
        attempted_validators.append(chosen_validator)

        qr = decode(Image.open(qr_image_path))
        if qr:
            encrypted_data = qr[0].data
            cipher = Fernet(key)
            try:
                decrypted_data = cipher.decrypt(encrypted_data).decode()
                buyer, seller, amount_str, transaction_name = decrypted_data.split(',')
                transaction_amount = float(amount_str)
                
                # Simulate potential validation failure
                if random.random() < failure_chance:
                    st.text(f"Validator {chosen_validator} failed to validate the transaction.")
                    penalize_validator(chosen_validator)
                    continue  # Select a new validator
                else:
                    st.success("Transaction validated successfully")
                    st.text(f"Transaction Info: {decrypted_data}")
                    reward_validator(chosen_validator, transaction_amount)  # Reward the validator
                    return
            except Exception as e:
                st.text(f"Failed to decrypt QR code: {e}")
                return
        else:
            st.text("Invalid QR code.")
            return

# Streamlit UI
st.title("PoS Transaction Validator")

# Upload QR code image
qr_image = st.file_uploader("Upload Transaction QR Code", type="png")
key = st.text_input("Enter Encryption Key", type="password")

# Validate Transaction Button
if st.button("Validate Transaction"):
    if qr_image and key:
        validate_transaction(qr_image, key)
