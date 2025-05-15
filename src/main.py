from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from starlette.middleware.sessions import SessionMiddleware
from .models import User, Project, File
import asyncio
import os

mock_bd = {
'projects_list': [
    {"id": 1, "name": "Проект 1", "description": "Описание проекта 1"},
    {"id": 2, "name": "Проект 2", "description": "Описание проекта 2"},
    {"id": 3, "name": "Проект 3", "description": "Описание проекта 3"}
],
'profile': {
    'name': '',
    'email': '',
    'password': '',
    'isAuth': False
},
'users': [
    {'id': 1, 'login': 'admin@gmail.com', 'password': "admin"}
]
}

app = FastAPI()

# Добавляем middleware для сессий
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-here")

# Путь к шаблонам
templates = Jinja2Templates(directory="src/templates")

# Для статических файлов (CSS, JS, изображения)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Подключение к базе данных
engine = create_async_engine("sqlite+aiosqlite:///db.sqlite")
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with async_session() as session:
        yield session

        
async def get_db():
    async with async_session() as session:
        yield session

# Инициализация базы данных
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(User.metadata.create_all)
        await conn.run_sync(Project.metadata.create_all)

# Странички

async def check_auth(request: Request):
    '''
    Проверяет, авторизован ли пользователь
    '''
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login", status_code=303)
    return True

@app.get("/projects", dependencies=[Depends(check_auth)])
async def projects(request: Request, db: AsyncSession = Depends(get_db)):
    '''
    Возвращает страницу с проектами
    '''
    result = await db.execute(select(Project))
    projects = result.scalars().all()
    return templates.TemplateResponse("projects.html", {"request": request, "projects": projects})

@app.get("/projects/new", dependencies=[Depends(check_auth)])
async def project_create(request: Request, db: AsyncSession = Depends(get_db)):
    '''
    Возвращает страницу с формой для создания проекта
    '''
    return templates.TemplateResponse("project_create.html", {"request": request})

@app.get("/projects/{project_id}", dependencies=[Depends(check_auth)])
async def project_detail(request: Request, project_id: int, db: AsyncSession = Depends(get_db)):
    '''
    Возвращает страницу с проектом
    '''
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    result = await db.execute(select(File).where(File.project_id == project_id))
    files = result.scalars().all()
    return templates.TemplateResponse("project_detail.html", {"request": request, "project": project, "files": files})

@app.get("/users", dependencies=[Depends(check_auth)])
async def users(request: Request, db: AsyncSession = Depends(get_db)):
    '''
    Возвращает список всех пользователей
    '''
    result = await db.execute(select(User))
    users = result.scalars().all()
    return templates.TemplateResponse("users.html", {"request": request, "users": users})

@app.get("/users/{user_id}", dependencies=[Depends(check_auth)])
async def user(request: Request, user_id: int, db: AsyncSession = Depends(get_db)):
    '''
    Возвращает страницу с пользователем
    '''
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    return templates.TemplateResponse("user.html", {"request": request, "user": user})

@app.get("/profile", dependencies=[Depends(check_auth)])
async def profile(request: Request, db: AsyncSession = Depends(get_db)):
    '''
    Возвращает страницу с профилем пользователя
    '''
    user_id = request.session.get("user_id")
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    return templates.TemplateResponse(
        "profile.html", 
        {"request": request, "profile": user}
    )

@app.get("/projects/{project_id}/file/{file_id}", dependencies=[Depends(check_auth)])
async def file(request: Request, project_id: int, file_id: int, db: AsyncSession = Depends(get_db)):
    '''
    Возвращает страницу с файлом
    '''
    result = await db.execute(select(File).where(File.id == file_id))
    file = result.scalar_one_or_none()
    return templates.TemplateResponse("file.html", {"request": request, "file": file})

@app.get("/projects/{project_id}/new_file", dependencies=[Depends(check_auth)])
async def file_create(request: Request, project_id: int, db: AsyncSession = Depends(get_db)):
    '''
    Возвращает страницу с формой для создания файла
    '''
    return templates.TemplateResponse("file_create.html", {"request": request, "project_id": project_id})

# Эти маршруты доступны без авторизации
@app.get("/register")
async def register(request: Request):
    '''
    Возвращает страницу с формой для регистрации
    '''
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login")
async def login(request: Request):
    '''
    Возвращает страницу с формой для входа
    '''
    return templates.TemplateResponse("login.html", {"request": request})

# Обработчики запросов

@app.post("/projects/{project_id}/new_file", dependencies=[Depends(check_auth)])
async def file_create_handle(request: Request, project_id: int, name: str = Form(...), text: str = Form(...), db: AsyncSession = Depends(get_db)):
    '''
    Создает новый файл
    '''
    file = File(name=name, text=text, project_id=project_id)
    db.add(file)
    await db.commit()
    await db.refresh(file)
    return RedirectResponse(url=f"/projects/{project_id}/file/{file.id}", status_code=303)


@app.patch("/projects/{project_id}/file/{file_id}", dependencies=[Depends(check_auth)])
async def file_update_handle(request: Request, project_id: int, file_id: int, text: str = Form(...), db: AsyncSession = Depends(get_db)):
    '''
    Обновляет текст файла
    '''
    result = await db.execute(select(File).where(File.id == file_id))
    file = result.scalar_one_or_none()
    file.text = text
    await db.commit()
    await db.refresh(file)
    return RedirectResponse(url=f"/projects/{project_id}/file/{file_id}", status_code=303)

@app.post("/projects/new")
async def project_create_handle(request: Request, name: str = Form(...), description: str = Form(...), db: AsyncSession = Depends(get_db)):
    '''
    Создает новый проект
    '''
    project = Project(name=name, description=description)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return RedirectResponse(url="/projects", status_code=303)

@app.post("/login")
async def login_handle(request: Request, login: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db)):
    '''
    Входит в систему
    '''
    # Ищем пользователя в БД
    result = await db.execute(
        select(User).where(User.login == login)
    )
    user = result.scalar_one_or_none()
    
    if user and user.password == password:  # В реальном приложении используйте хеширование паролей!
        # Сохраняем ID пользователя в сессии
        request.session["user_id"] = user.id
        return RedirectResponse(url="/profile", status_code=303)
    
    return templates.TemplateResponse(
        "login.html", 
        {"request": request, "error": "Неверный логин или пароль"}
    )

@app.post("/register")
async def register_handle(request: Request, login: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db)):
    '''
    Регистрирует нового пользователя
    '''
    result = await db.execute(select(User).where(User.login == login))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Пользователь с таким логином уже существует"})
    
    user = User(login=login, password=password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return RedirectResponse(url="/login", status_code=303)

@app.post("/logout")
async def logout(request: Request):
    '''
    Выходит из системы
    '''
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
