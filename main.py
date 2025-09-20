"""
Simple starter script for students:
- optional debugger attach (debugpy)
- connects to MySQL using env vars
- creates a table, inserts a row, queries it
"""

import os
import time
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# -------- Debugger (optional) --------
def maybe_attach_debugger():
    """Attach debugpy if DEBUG=1, waiting for VS Code attach."""
    debug_flag = os.getenv("DEBUG", "0")
    if debug_flag == "1":
        try:
            import debugpy  # noqa: F401
        except ImportError:
            print("debugpy not installed? Run: pip install debugpy")
            return
        import debugpy

        host = "0.0.0.0"
        port = 5678
        print(f"[debug] Listening for debugger on {host}:{port} ...")
        debugpy.listen((host, port))
        # Wait for debugger to attach before running the rest
        debugpy.wait_for_client()
        print("[debug] Debugger attached.")

# -------- Database helpers --------
def get_db_connection():
    """Create a connection using environment variables."""
    host = os.getenv("MYSQL_HOST", "localhost")
    port = int(os.getenv("MYSQL_PORT", "3306"))
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "example")
    database = os.getenv("MYSQL_DATABASE", "appdb")

    return mysql.connector.connect(
        host=host, port=port, user=user, password=password, database=database
    )

def ensure_table(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB;
            """
        )
    conn.commit()

def insert_student(conn, name: str):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO students (name) VALUES (%s)", (name,))
    conn.commit()

def fetch_students(conn):
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT id, name, created_at FROM students ORDER BY id DESC LIMIT 5;")
        return cur.fetchall()

# -------- Main --------
def main():
    load_dotenv()           # read .env if present
    maybe_attach_debugger() # attach if DEBUG=1

    # MySQL can take a few seconds to be ready the first time
    for attempt in range(10):
        try:
            conn = get_db_connection()
            if conn.is_connected():
                break
        except Error as e:
            print(f"Waiting for DB... ({attempt+1}/10): {e}")
            time.sleep(2)
    else:
        raise SystemExit("Could not connect to MySQL. Is the container healthy?")

    try:
        ensure_table(conn)
        insert_student(conn, "Ada Lovelace")
        rows = fetch_students(conn)
        print("Latest students:")
        for r in rows:
            print(f"- #{r['id']:>3} {r['name']} @ {r['created_at']}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()