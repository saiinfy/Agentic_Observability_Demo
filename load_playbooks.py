"""
This script loads incident response playbooks into an Oracle database and generates vector embeddings for each issue description.

Workflow:
1. Connects to the Oracle database using provided credentials.
2. Declares the VECTOR bind type for the embedding column.
3. Defines a list of playbooks, each with an issue, action, and success flag.
4. For each playbook:
    - Generates a vector embedding for the issue text using the embedding utility.
    - Inserts the playbook data and embedding into the 'incident_playbooks' table.
5. Commits the transaction and closes the database connection.
6. Prints a success message upon completion.

Requirements:
    - oracledb Python package
    - agents.embedding_utils.generate_embedding function
    - Oracle database with 'incident_playbooks' table and VECTOR column

Usage:
    python load_playbooks.py
"""

import oracledb
from agents.embedding_utils import generate_embedding
from config.settings import DB_HOST, DB_PASSWORD

conn = oracledb.connect(
    user="system",
    password=DB_PASSWORD,
    host=DB_HOST,
    port=1521,
    service_name="FREEPDB1"
)

cursor = conn.cursor()

# 🔹 IMPORTANT: declare VECTOR bind type
cursor.setinputsizes(embedding=oracledb.DB_TYPE_VECTOR)

playbooks = [
    {"issue": "Payments are slow after deployment", "action": "Rollback recent release", "success": 1},
    {"issue": "Users cannot login after configuration change", "action": "Revert authentication configuration", "success": 1},
    {"issue": "Payments are slow after deployment", "action": "Scale database vertically", "success": 0},
    {"issue": "Intermittent timeouts during peak load", "action": "Restart application servers", "success": 0},
]

for pb in playbooks:
    embedding = generate_embedding(pb["issue"])

    cursor.execute(
        """
        INSERT INTO incident_playbooks
        (issue_text, action_taken, success, embedding)
        VALUES (:issue, :action, :success, :embedding)
        """,
        issue=pb["issue"],
        action=pb["action"],
        success=pb["success"],
        embedding=embedding,
    )

conn.commit()
cursor.close()
conn.close()

print("Playbooks inserted successfully.")
