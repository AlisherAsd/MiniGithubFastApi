import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.models import Project

DATABASE_URL = "sqlite+aiosqlite:///db.sqlite"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def add_test_project():
    async with async_session() as session:
        project = Project(name="testproject", description="testdescription")
        session.add(project)
        await session.commit()
        await session.refresh(project)
        print(f"Создан проект: {project.name}")

asyncio.run(add_test_project())