# get_database_schema.py (modified for CLI use)
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from database.service import get_db

async def print_schema():
    async for db in get_db():
        from sqlalchemy import text

        table_query = text("""
            SELECT TABLE_SCHEMA, TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_SCHEMA, TABLE_NAME;
        """)

        result = await db.execute(table_query)
        tables = result.fetchall()

        schema_info = {}

        for table_schema, table_name in tables:
            column_query = text("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = :schema AND TABLE_NAME = :table
                ORDER BY ORDINAL_POSITION;
            """)
            column_result = await db.execute(
                column_query,
                {"schema": table_schema, "table": table_name}
            )
            columns = column_result.fetchall()
            schema_info[f"{table_schema}.{table_name}"] = [
                {
                    "name": col[0],
                    "type": col[1],
                    "nullable": col[2],
                    "max_length": col[3]
                }
                for col in columns
            ]

        import pprint
        pprint.pprint(schema_info)

if __name__ == "__main__":
    asyncio.run(print_schema())
