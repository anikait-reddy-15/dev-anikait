import pyodbc
import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


DATABASE_URL = os.getenv("PROD_DATABASE_URL")
if not DATABASE_URL:
    logger.error("PROD_DATABASE_URL environment variable is not set")
    raise ValueError("PROD_DATABASE_URL is required")

print(pyodbc.drivers())
# exit()

server = 'tcp:theprotrail.database.windows.net,1433'
database='Protrail'
username = 'AIUser'
password = 'RefractAI@2025'
driver = '{ODBC Driver 17 for SQL Server}' 


# Connect to the MSSQL server
connection_string = f"""
    DRIVER={driver};
    SERVER={server};
    DATABASE={database};
    UID={username};
    PWD={password};
    Encrypt=yes;
    TrustServerCertificate=no;
    Connection Timeout=30;
"""
print(connection_string)
# exit()

try:
    # Connect to the MSSQL server
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("""
        SELECT TABLE_SCHEMA, TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME;
    """)
    tables = cursor.fetchall()
    logger.info(f"Total tables: {len(tables)}")

    print("\n=== Database Schema ===\n")

    # Loop through tables and get column info for AIAPIResponses
    for schema, table in tables:
        if table == "AIAPIResponses":
            print(f"Table: {schema}.{table}")
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
                ORDER BY ORDINAL_POSITION;
            """, (schema, table))
            columns = cursor.fetchall()
            for col in columns:
                name, dtype, nullable, char_len = col
                details = f"{dtype}"
                if char_len and char_len != -1:  # Handle max length for varchar(max)
                    details += f"({char_len})"
                nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                print(f"  - {name}: {details} {nullable_str}")
            print()

except pyodbc.Error as e:
    logger.error(f"Database error: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
finally:
    # Clean up
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
    logger.debug("Database connection closed")