import mysql.connector

try:
    db = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="dhilipk2006",
        database="shopping_db"
    )

    print("Database Connected Successfully!")

except mysql.connector.Error as err:
    print("Error:", err)