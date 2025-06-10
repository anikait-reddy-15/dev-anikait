from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from database.service import get_db

router = APIRouter()

# API endpoint to get all users (read-only)
@router.get("/items/")
async def read_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute("SELECT * FROM your_table")
    rows = result.fetchall()
    return rows