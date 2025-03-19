import sqlite3
import pandas as pd
# Initialize database
def init_db():
    conn = sqlite3.connect('extracted_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS extracted_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            extracted_text TEXT
        )
    ''')
    

    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES ( ?, ?)", ( 'admin', 'admin'))
    

    c.execute('''
        CREATE TABLE IF NOT EXISTS cheque_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payee_name TEXT,
            cheque_no TEXT,
            amount TEXT,
            bank_account_no TEXT,
            bank_name TEXT,
            ifsc_code TEXT,
            cheque_date TEXT
        )
    ''')

    conn.commit()
    conn.close()

def create_user(username, password):
    # Check if the user already exists
    conn = sqlite3.connect('extracted_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    if c.fetchone():
        conn.close()
        return False
    # Insert new user (ideally, hash the password before storing it)
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
    return True

# User authentication
def authenticate_user(username, password):
    conn = sqlite3.connect('extracted_data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    conn.close()
    return user


def insert_cheque_details(details):
    insert_query = """
        INSERT INTO cheque_details (
            payee_name, cheque_no, amount, bank_account_no, bank_name, ifsc_code, cheque_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    try:
        conn = sqlite3.connect('extracted_data.db')
        c = conn.cursor()
        c.execute(insert_query, (
            details["payee_name"],
            details["cheque_no"],
            details["amount"],
            details["bank_account_no"],
            details["bank_name"],
            details["ifsc_code"],
            details["cheque_date"]
        ))
        conn.commit()
        conn.close()
        print("Cheque details inserted successfully.")
    except Exception as e:
        print(f"Error inserting cheque details: {e}")


def fetch_cheque_details():
    select_query = "SELECT * FROM cheque_details"
    try:
        conn = sqlite3.connect('extracted_data.db')
        c = conn.cursor()
        c.execute(select_query)
        data = c.fetchall()   
        conn.close()       
        return data
    except Exception as e:
        print(f"Error fetching cheque details: {e}")
        return []
    
def fetch_data_from_db():
    # Connect to the SQLite database
    conn = sqlite3.connect('extracted_data.db')
    
    # Query to fetch cheque details
    query = """
    SELECT 
        payee_name AS "Payee Name", 
        bank_account_no AS "Bank Account Number", 
        cheque_no AS "Cheque Number", 
        amount AS "Amount", 
        bank_name AS "Bank Name", 
        ifsc_code AS "IFSC Code", 
        cheque_date AS "Cheque Date"
    FROM cheque_details
    """
    # Execute query and load into a DataFrame
    df = pd.read_sql_query(query, conn)
    
    # Close the connection
    conn.close()
    
    return df