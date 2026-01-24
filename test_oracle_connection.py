"""
This script tests connectivity to an Oracle database using the oracledb Python package.

Steps performed:
1. Establishes a connection to the Oracle database with the provided credentials and connection details.
2. Prints a success message upon successful connection.
3. Executes a simple SQL query to retrieve the current database time (SYSDATE).
4. Prints the result of the query.
5. Closes the cursor and the database connection.

Usage:
    python test_oracle_connection.py

Requirements:
    - oracledb Python package must be installed.
    - Network access to the Oracle database instance.
"""

import oracledb
from config.settings import DB_HOST, DB_PASSWORD

# Establish connection to the Oracle database
connection = oracledb.connect(
    user="system",
    password=DB_PASSWORD,
    host= DB_HOST,
    port=1521,
    service_name="FREEPDB1"
)

print("Connected to Oracle successfully!")

# Create a cursor and execute a test query
cursor = connection.cursor()
cursor.execute("SELECT sysdate FROM dual")
print("DB Time:", cursor.fetchone())

# Clean up resources
cursor.close()
connection.close()
