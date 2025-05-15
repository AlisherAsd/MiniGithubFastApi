from sqlalchemy.ext.asyncio import create_async_engine
from models import User, Project
import asyncio

async def init_db():
    # Подключение к базе данных
    engine = create_async_engine("sqlite+aiosqlite:///db.sqlite")
    
    # Создание таблиц
    async with engine.begin() as conn:
        await conn.run_sync(User.metadata.create_all)
        await conn.run_sync(Project.metadata.create_all)
    
    print("База данных успешно инициализирована!")

if __name__ == "__main__":
    asyncio.run(init_db()) 