import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Sql@2020",
        database="university_dbs_project"
    )
    return conn