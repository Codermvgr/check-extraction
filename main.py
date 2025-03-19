import streamlit as st
from database import init_db, authenticate_user, insert_cheque_details, fetch_cheque_details, fetch_data_from_db, create_user
from extract import extract_text_from_image
import json
import os
import tempfile
import numpy as np
from PIL import Image, ImageChops
from pdf2image import convert_from_path
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
import plotly.express as px

# ---------------------------
# Section 1: Initialization
# ---------------------------
init_db()

# ---------------------------
# Section 2: Authentication Landing Page
# ---------------------------
def auth_page():
    st.title("Welcome to Cheque Extraction and Analytics App!")
    st.image("back-ground.webp", caption="Cheque Data Made Simple", use_container_width=True)
    st.markdown("""
        ### About This Application
        This app simplifies cheque processing and provides insightful analytics:
        - Extracts data from uploaded **PDFs or images** of cheques.
        - Saves the extracted details (e.g., bank name, IFSC code, cheque number, etc.) to a database.
        - Offers **visual analytics** like bar charts and pie charts to track cheque details by bank or amount distribution.
        - Enables efficient and organized cheque data management.
        
        ### Get Started
        Please sign up or sign in to continue.
    """)
    auth_option = st.radio("Select an option:", ["Sign In", "Sign Up"])
    if auth_option == "Sign In":
        login()
    else:
        signup()

# ---------------------------
# Section 3: Login Functionality
# ---------------------------
def login():
    st.subheader("Sign In")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Sign In")
    if submit:
        if authenticate_user(username, password):
            st.success("Login successful")
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
        else:
            st.error("Invalid credentials")

# ---------------------------
# Section 4: Signup Functionality
# ---------------------------
def signup():
    st.subheader("Sign Up")
    with st.form("signup_form"):
        username = st.text_input("Choose a Username")
        password = st.text_input("Choose a Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Sign Up")
    if submit:
        if password != confirm_password:
            st.error("Passwords do not match. Please try again.")
        else:
            # create_user should return True if the account was created successfully
            if create_user(username, password):
                st.success("Account created successfully! Please sign in.")
            else:
                st.error("Username already exists or an error occurred. Please try a different username.")

# ---------------------------
# Section 5: Home (Main App) Page
# ---------------------------
def home():
    background_css = """
    <style>
        body {
            background-color: #C0C0C0;  /* Silver color */
        }
    </style>
    """
    st.markdown(background_css, unsafe_allow_html=True)
    st.title("Welcome to Cheque Extraction and Analytics App! 👋")
    st.image("back-ground.webp", caption="Cheque Data Made Simple", use_container_width=True)
    st.markdown("**[GitHub Repository](https://github.com/Codermvgr/check-extraction)**")
    st.markdown("""
        ### About This Application
        This app simplifies cheque processing and provides insightful analytics:
        - Extracts data from uploaded **PDFs or images** of cheques.
        - Saves the extracted details (e.g., bank name, IFSC code, cheque number, etc.) to a database.
        - Offers **visual analytics** like bar charts and pie charts to track cheque details by bank or amount distribution.
        - Enables efficient and organized cheque data management.
        
        ### Features
        - **Data Extraction**: Upload cheque images or PDF files to extract details.
        - **Analytics Dashboard**: View cheque data in tabular format and generate visualizations.
        - **Secure Login**: Only registered users can access the application.
        
        ### How to Use
        1. Go to the **Extract Data** section to upload a cheque file.
        2. Review and save extracted data to the database.
        3. Navigate to **View Data** to analyze saved cheque details and generate insights.
    """)

# ---------------------------
# Section 6: Extract Data
# ---------------------------
def extract_data():
    st.title("Extract Data")
    uploaded_file = st.file_uploader("Upload a PDF or Image", type=["pdf", "png", "jpg", "jpeg"])
    if uploaded_file:
        file_type = "pdf" if uploaded_file.type == "application/pdf" else "image"
        st.write(f"Processing {file_type.upper()} file...")
        is_data_extracted = [False]   # Initialize as False
        is_data_saved = [False]         # Initialize as False
        if 'page_index' not in st.session_state:
            st.session_state['page_index'] = 0 
        if "pdf" in file_type:
            images = pdf_to_images(uploaded_file)
            col1, col2, col3 = st.columns([1, 5, 1])  # Navigation buttons for PDF pages
            with col1:
                if st.button('Previous'):
                    if st.session_state['page_index'] > 0:
                        st.session_state['page_index'] -= 1
            with col2:
                total_pages = len(images)
                st.markdown(f"<p style='text-align: center; font-weight: bold;'>Page {st.session_state['page_index'] + 1} of {total_pages}</p>", unsafe_allow_html=True)
            with col3:
                if st.button('Next'):
                    if st.session_state['page_index'] < len(images) - 1:
                        st.session_state['page_index'] += 1

            is_data_extracted = [False] * len(images)  # Initialize as False for all pages
            is_data_saved = [False] * len(images)        # Initialize as False for all pages
            image = images[st.session_state['page_index']]
            cropped_image = crop_cheque_area(image)
            st.image(cropped_image, caption=f"Cheque - Page {st.session_state['page_index'] + 1}")
            output_dir = "extracted_images"
            image_path = os.path.join(output_dir, f"page_{st.session_state['page_index'] + 1}.jpg")
        elif "image" in file_type or file_type in ["image/png", "image/jpeg"]:
            image = Image.open(uploaded_file)
            st.image(image, caption="Cheque Image", use_container_width=True)
            image_path = uploaded_file
        else:
            st.error("Unsupported file type")
            return

        extracted_text = extract_text_from_image(image_path)
        if extracted_text:
            is_data_extracted[st.session_state['page_index']] = True
            # print('pdf here')
            # insert_cheque_details(extracted_text)
            show_cheque_details(extracted_text)

def crop_cheque_area(image):
    gray = image.convert("L")
    bbox = ImageChops.invert(gray).getbbox()  # Get bounding box of non-white areas
    if bbox:
        cropped_image = image.crop(bbox)
        return cropped_image
    return image  # Fallback to original image if bbox is not found

def pdf_to_images(uploaded_file):
    poppler_path = r"C:\Program Files\poppler-24.08.0\Library\bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getbuffer())
        pdf_path = tmp_file.name   # Convert the uploaded file to an absolute path

    print("PDF path:", pdf_path)
    images = convert_from_path(pdf_path=pdf_path, dpi=300, poppler_path=poppler_path)

    output_dir = "extracted_images"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    else:
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
    for i, image in enumerate(images):
        output_path = os.path.join(output_dir, f"page_{i+1}.jpg")
        image.save(output_path, "JPEG")
        print(f"Saved: {output_path}")
    return images

def show_cheque_details(extracted_text):
    try:
        cheque_details = json.loads(extracted_text)
        st.success("Data extracted successfully!")
    except json.JSONDecodeError:
        st.error("Failed to parse extracted data as JSON.")
        st.stop()

    col1, col2 = st.columns(2)
    with col1:
        bank_name = st.text_input("Bank Name", value=cheque_details.get("bank_name", ""))
        ifsc_code = st.text_input("IFSC Code", value=cheque_details.get("ifsc_code", ""))
        bank_account_no = st.text_input("Bank Account Number", value=cheque_details.get("bank_account_number", ""))
    with col2:
        payee_name = st.text_input("Payee Name", value=cheque_details.get("payee_name", ""))
        cheque_date = st.text_input("Cheque Date", value=cheque_details.get("cheque_date", ""))
        cheque_no = st.text_input("Cheque Number", value=cheque_details.get("cheque_no", ""))
        amount = st.text_input("Amount", value=cheque_details.get("amount", "").replace(",", ""))

    if st.button("Save Data"):
        try:
            updated_cheque_details = {
                "payee_name": payee_name,
                "cheque_date": cheque_date,
                "cheque_no": cheque_no,
                "bank_account_no": bank_account_no,
                "bank_name": bank_name,
                "amount": amount,
                "ifsc_code": ifsc_code,
            }
            print("here")
            insert_cheque_details(updated_cheque_details)
            st.success("Cheque details saved successfully!")
        except:
            print("Data not inserted into table")

# ---------------------------
# Section 7: View Data
# ---------------------------
def view_data():
    st.title("Cheque Data from Database")
    st.write("Below is the extracted cheque data retrieved from the database:")
    try:
        data = fetch_data_from_db()
        if not data.empty:
            st.write(f"**Total Records: {len(data)}**")
            st.dataframe(data.reset_index(drop=True), use_container_width=True)
        else:
            st.warning("No data found in the database.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")

    if st.sidebar.button("View All Cheque Data"):
        data = fetch_cheque_details()
        if data:
            st.write("Cheque Data:")
            for row in data:
                st.json({
                    "Payee Name": row[1],
                    "Cheque Number": row[2],
                    "Amount": row[3],
                    "Bank Account Number": row[4],
                    "Bank Name": row[5],
                    "IFSC Code": row[6],
                    "Cheque Date": row[7]
                })
        else:
            st.info("No cheque details found.")

# ---------------------------
# Section 8: Analytics
# ---------------------------
def get_column_names():
    return ['amount', 'payee_name', 'bank_name', 'date']

def plot_bar_chart(values, labels):
    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_xlabel('Banks')
    ax.set_ylabel('Total Amount')
    ax.set_title('Top 5 Banks by Total Amount')
    return fig

def plot_pie_chart(values, labels):
    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.set_title('Top 5 Banks Share by Amount')
    return fig

def analytics_page():
    st.title("Analytics Dashboard")
    rows = fetch_data_from_db()  # Fetch stored cheque details
    if rows:
        columns = get_column_names()  # Dynamically get column names for the DataFrame
        df = pd.DataFrame(rows, columns=columns)
        sort_by = st.selectbox("Sort by", ["Amount", "Payee Name", "Bank Name", "Date"])
        sort_order = st.radio("Sort order", ("Ascending", "Descending"))
        if sort_by == "Amount":
            df_sorted = df.sort_values(by="amount", ascending=(sort_order == "Ascending"))
        elif sort_by == "Payee Name":
            df_sorted = df.sort_values(by="payee_name", ascending=(sort_order == "Ascending"))
        elif sort_by == "Bank Name":
            df_sorted = df.sort_values(by="bank_name", ascending=(sort_order == "Ascending"))
        elif sort_by == "Date":
            df_sorted = df.sort_values(by="date", ascending=(sort_order == "Ascending"))
        st.subheader(f"Sorted Data: {sort_by} ({sort_order})")
        st.dataframe(df_sorted)
        if "amount" in df.columns:
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
            df.dropna(subset=["amount"], inplace=True)
            top_5_banks = df.groupby("bank_name")["amount"].sum().nlargest(5)
            bar_chart = plot_bar_chart(top_5_banks.values, top_5_banks.index)
            pie_chart = plot_pie_chart(top_5_banks.values, top_5_banks.index)
            st.pyplot(bar_chart)
            st.pyplot(pie_chart)
    else:
        st.error("No cheque details found in the database.")
    
    cheque_data = fetch_cheque_details()
    if cheque_data:
        df = pd.DataFrame(cheque_data)
        st.write(df)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download CSV", data=csv, file_name="cheque_data.csv", mime="text/csv"
        )
    else:
        st.write("No cheque details found in the database.")

def display_analytics():
    st.title("Cheque Analytics")
    cheque_data = fetch_data_from_db()
    st.subheader("Cheque Data")
    st.dataframe(cheque_data)
    st.subheader("Total Cheque Amounts per Bank")
    bank_amounts = cheque_data.groupby('Bank Name')['Amount'].sum().reset_index()

    bank_amounts['Amount'] = pd.to_numeric(bank_amounts['Amount'], errors='coerce')

    bank_amounts = bank_amounts.dropna(subset=['Amount'])

    bank_amounts = bank_amounts.sort_values(by='Amount')
    fig, ax = plt.subplots()
    ax.bar(bank_amounts['Bank Name'], bank_amounts['Amount'], color='skyblue')
    ax.set_xlabel('Bank Name')
    ax.set_ylabel('Total Cheque Amount')
    ax.set_title('Total Cheque Amounts per Bank')
    y_ticks = np.linspace(bank_amounts['Amount'].min(), bank_amounts['Amount'].max(), num=5)
    ax.set_yticks(y_ticks) 
    plt.xticks(rotation=45, ha='right')  # Rotate labels for better visibility
    plt.tight_layout()
    st.pyplot(fig)
    st.subheader("Cheque Amount Distribution per Bank")
    bank_amounts = cheque_data.groupby('Bank Name')['Amount'].sum()
    print(bank_amounts)
    fig = px.pie(bank_amounts, names=bank_amounts.index, values=bank_amounts.values, title="Cheque Amount Distribution")
    st.plotly_chart(fig)
    st.subheader("Cheque Amounts Over Time")
    cheque_data.rename(columns={'Cheque Date': 'Date'}, inplace=True)

    cheque_data['Date'] = pd.to_datetime(cheque_data['Date'])
    time_series = cheque_data.groupby('Date')['Amount'].sum().reset_index()
    fig, ax = plt.subplots()
    ax.plot(time_series['Date'], time_series['Amount'], marker='o', color='green')
    ax.set_xlabel('Date')
    ax.set_ylabel('Cheque Amount')
    ax.set_title('Cheque Amounts Over Time')
    st.pyplot(fig)

# ---------------------------
# Main Navigation
# ---------------------------
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# If not logged in, show the auth landing page (home + login/signup)
if not st.session_state['logged_in']:
    auth_page()
else:
    # Once logged in, show the main home page and sidebar navigation
    with st.sidebar:
        menu = option_menu(menu_title="Navigation",options=["Home", "Extract Data", "View Data", "Analytics Dashboard"])
    
    if menu == "Home":
        home()
    elif menu == "Extract Data":
        extract_data()
    elif menu == "View Data":
        view_data()
    elif menu == "Analytics Dashboard":
        display_analytics()
