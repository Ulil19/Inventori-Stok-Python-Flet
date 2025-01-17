# db_connection.py
import mysql.connector

def create_connection():
    try:
        # Membuat koneksi ke database MySQL
        koneksi_db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="uas_mad"
        )
        return koneksi_db
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
