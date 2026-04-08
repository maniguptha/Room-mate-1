import pymysql

try:
    conn = pymysql.connect(host='localhost', user='root', password='')
    cursor = conn.cursor()
    cursor.execute('DROP DATABASE IF EXISTS staymatch;')
    cursor.execute('CREATE DATABASE staymatch;')
    conn.commit()
    conn.close()
    print("Database reset successfully.")
except Exception as e:
    print(f"Error resetting DB: {e}")
