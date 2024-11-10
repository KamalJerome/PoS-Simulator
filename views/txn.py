# txn.py
import streamlit as st
import qrcode
from cryptography.fernet import Fernet
import io

# Function to generate a transaction QR code and return it as a PNG file
def generate_transaction_qr(buyer, seller, amount, transaction_name, key):
    transaction_details = f"{buyer},{seller},{amount},{transaction_name}"
    cipher = Fernet(key)
    encrypted_details = cipher.encrypt(transaction_details.encode())
    
    qr = qrcode.make(encrypted_details)

    # Save the QR code to an in-memory file
    img_io = io.BytesIO()
    qr.save(img_io, format="PNG")
    img_io.seek(0)
    
    return img_io

# Streamlit UI for entering transaction details
st.title("Transaction QR Code Generator")

# Input fields for transaction details
buyer = st.text_input("Buyer Name")
seller = st.text_input("Seller Name")
amount = st.number_input("Amount", min_value=0.01)
transaction_name = st.text_input("Transaction Name")

# Generate and download QR code
if st.button("Generate QR Code"):
    if buyer and seller and amount > 0 and transaction_name:
        # Generate encryption key
        key = Fernet.generate_key()

        # Generate the QR code
        qr_image = generate_transaction_qr(buyer, seller, amount, transaction_name, key)
        
        st.success("QR code generated for transaction.")
        st.text(f"Encryption key: {key.decode()}")

        # Show the generated QR code image
        st.image(qr_image, caption="Transaction QR Code", use_column_width=True)

        # Provide the download button for the QR code image
        st.download_button(
            label="Download QR Code",
            data=qr_image,
            file_name="transaction_qr.png",
            mime="image/png"
        )
    else:
        st.error("Please fill all the fields to generate the QR code.")
