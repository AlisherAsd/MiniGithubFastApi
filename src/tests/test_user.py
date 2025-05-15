import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.models import User

DATABASE_URL = "sqlite+aiosqlite:///db.sqlite"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def add_test_user():
    async with async_session() as session:
        user = User(login="testuser", password="testpass", email="testuser@example.com")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        print(f"Создан пользователь: {user.login}")

asyncio.run(add_test_user())