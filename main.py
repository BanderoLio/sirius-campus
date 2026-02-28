"""
Auth Service - микросервис аутентификации и управления пользователями проекта Кампус Сириус.

Это заглушка (stub) для демонстрации структуры сервиса.
В реальном проекте здесь будет подключение к PostgreSQL, JWT аутентификация и т.д.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Any, Dict
from enum import Enum

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr, Field
from fastapi.responses import JSONResponse


# ----- Константы -----
API_VERSION = "1.0.0"
API_PREFIX = "/api/v1"
SERVICE_PORT = 8001


# ----- Pydantic модели -----

class UserType(str, Enum):
    STUDENT = "student"
    EDUCATOR = "educator"


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


class User(BaseModel):
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    created_at: str
    updated_at: str


class StudentCreate(UserCreate):
    building: int
    entrance: int
    floor: int
    room: int
    is_adult: bool = False


class StudentUpdate(UserUpdate):
    building: Optional[int] = None
    entrance: Optional[int] = None
    floor: Optional[int] = None
    room: Optional[int] = None
    is_adult: Optional[bool] = None


class Student(BaseModel):
    userId: str
    building: int
    entrance: int
    floor: int
    room: int
    is_adult: bool = False
    created_at: str
    updated_at: str
    phone: Optional[str] = None


class EducatorCreate(UserCreate):
    is_night: bool = False


class EducatorUpdate(UserUpdate):
    is_night: Optional[bool] = None


class Educator(BaseModel):
    userId: str
    is_night: bool = False
    created_at: str
    updated_at: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserWithProfile(BaseModel):
    user: User
    profile: Any  # Student or Educator
    user_type: UserType


class PaginatedUsers(BaseModel):
    items: List[User]
    total: int
    page: int
    size: int
    pages: int


class ErrorResponse(BaseModel):
    error: Dict[str, Any]


# ----- In-memory "база данных" -----

# Хранилище пользователей
users_db: Dict[str, Dict[str, Any]] = {}

# Хранилище студентов
students_db: Dict[str, Student] = {}

# Хранилище воспитателей
educators_db: Dict[str, Educator] = {}

# Хранилище refresh токенов (token -> user_id)
refresh_tokens_db: Dict[str, str] = {}

# Счетчик для генерации ID
next_user_id = 1


def generate_user_id() -> str:
    """Генерирует UUID для пользователя"""
    return str(uuid.uuid4())


def generate_token() -> str:
    """Генерирует простой токен (заглушка)"""
    return uuid.uuid4().hex


def get_current_time_iso() -> str:
    """Возвращает текущее время в ISO формате"""
    return datetime.utcnow().isoformat() + "Z"


# ----- Вспомогательные функции -----

def create_error_response(code: str, message: str, status_code: int = 400) -> JSONResponse:
    """Создает стандартизированный ответ об ошибке"""
    trace_id = str(uuid.uuid4())
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "trace_id": trace_id,
                "details": None
            }
        },
        headers={"X-Trace-ID": trace_id, "X-Correlation-ID": trace_id}
    )


def verify_token(authorization: Optional[str]) -> Dict[str, Any]:
    """Проверяет токен и возвращает данные пользователя (заглушка)"""
    print(authorization)
    if not authorization:
        raise HTTPException(status_code=401, detail="Токен отсутствует")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Неверный формат токена")
    
    token = authorization[7:]
    
    # В заглушке принимаем любой токен, который начинается с "valid_"
    if token.startswith("valid_"):
        user_id = token[6:36] if len(token) >= 36 else str(uuid.uuid4())
        return {
            "user_id": user_id,
            "user_type": "student",
            "email": "user@example.com",
            "first_name": "Иван",
            "last_name": "Иванов"
        }
    
    raise HTTPException(status_code=401, detail="Токен недействителен")


# ----- Создание приложения -----

app = FastAPI(
    title="Auth Service API",
    description="Микросервис аутентификации и управления пользователями проекта Кампус Сириус",
    version=API_VERSION,
    docs_url=f"{API_PREFIX}/docs",
    redoc_url=f"{API_PREFIX}/redoc",
    openapi_url=f"{API_PREFIX}/openapi.json"
)


# ----- Middleware для добавления заголовков -----

@app.middleware("http")
async def add_trace_headers(request, call_next):
    """Добавляет trace_id и correlation_id к каждому запросу"""
    trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    
    response = await call_next(request)
    response.headers["X-Trace-ID"] = trace_id
    response.headers["X-Correlation-ID"] = correlation_id
    
    return response


# ----- Корневой эндпоинт -----

@app.get("/")
def root():
    """Корневой эндпоинт для проверки работоспособности"""
    return {
        "service": "Auth Service",
        "version": API_VERSION,
        "status": "running",
        "docs": f"{API_PREFIX}/docs"
    }


@app.get(f"{API_PREFIX}/health")
def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy"}


# ----- Публичные эндпоинты (без аутентификации) -----

@app.post(
    f"{API_PREFIX}/auth/register/student",
    response_model=UserWithProfile,
    status_code=201,
    tags=["Authentication", "Students"]
)
def register_student(data: StudentCreate):
    """Регистрация нового студента"""
    # Проверяем, не занят ли email
    for user in users_db.values():
        if user["email"] == data.email:
            raise HTTPException(status_code=409, detail="Пользователь с таким email уже существует")
    
    # Генерируем ID
    user_id = generate_user_id()
    now = get_current_time_iso()
    
    # Создаем пользователя
    user = User(
        id=user_id,
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        created_at=now,
        updated_at=now
    )
    
    users_db[user_id] = {
        "id": user_id,
        "email": data.email,
        "password_hash": f"hashed_{data.password}",  # В реальном проекте - хэширование
        "first_name": data.first_name,
        "last_name": data.last_name,
        "created_at": now,
        "updated_at": now
    }
    
    # Создаем профиль студента
    student = Student(
        userId=user_id,
        building=data.building,
        entrance=data.entrance,
        floor=data.floor,
        room=data.room,
        is_adult=data.is_adult,
        created_at=now,
        updated_at=now
    )
    
    students_db[user_id] = student
    
    return UserWithProfile(
        user=user,
        profile=student,
        user_type=UserType.STUDENT
    )


@app.post(
    f"{API_PREFIX}/auth/register/educator",
    response_model=UserWithProfile,
    status_code=201,
    tags=["Authentication", "Educators"]
)
def register_educator(data: EducatorCreate):
    """Регистрация нового воспитателя"""
    # Проверяем, не занят ли email
    for user in users_db.values():
        if user["email"] == data.email:
            raise HTTPException(status_code=409, detail="Пользователь с таким email уже существует")
    
    # Генерируем ID
    user_id = generate_user_id()
    now = get_current_time_iso()
    
    # Создаем пользователя
    user = User(
        id=user_id,
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        created_at=now,
        updated_at=now
    )
    
    users_db[user_id] = {
        "id": user_id,
        "email": data.email,
        "password_hash": f"hashed_{data.password}",
        "first_name": data.first_name,
        "last_name": data.last_name,
        "created_at": now,
        "updated_at": now
    }
    
    # Создаем профиль воспитателя
    educator = Educator(
        userId=user_id,
        is_night=data.is_night,
        created_at=now,
        updated_at=now
    )
    
    educators_db[user_id] = educator
    
    return UserWithProfile(
        user=user,
        profile=educator,
        user_type=UserType.EDUCATOR
    )


@app.post(
    f"{API_PREFIX}/auth/login",
    response_model=TokenResponse,
    tags=["Authentication"]
)
def login(data: UserLogin):
    """Вход в систему"""
    # Ищем пользователя по email
    user = None
    for u in users_db.values():
        if u["email"] == data.email:
            user = u
            break
    
    if not user:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    
    # Проверяем пароль (в заглушке просто сравниваем)
    if user["password_hash"] != f"hashed_{data.password}":
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    
    # Генерируем токены
    access_token = f"valid_{uuid.uuid4().hex}"
    refresh_token = generate_token()
    
    # Сохраняем refresh токен
    refresh_tokens_db[refresh_token] = user["id"]
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@app.post(
    f"{API_PREFIX}/auth/refresh",
    response_model=TokenResponse,
    tags=["Authentication"]
)
def refresh_token(data: RefreshTokenRequest):
    """Обновление access токена"""
    refresh_token = data.refresh_token
    
    if refresh_token not in refresh_tokens_db:
        raise HTTPException(status_code=401, detail="Refresh токен недействителен или истек")
    
    user_id = refresh_tokens_db[refresh_token]
    
    if user_id not in users_db:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    
    # Генерируем новые токены
    access_token = f"valid_{uuid.uuid4().hex}"
    new_refresh_token = generate_token()
    
    # Инвалидируем старый refresh токен и создаем новый
    del refresh_tokens_db[refresh_token]
    refresh_tokens_db[new_refresh_token] = user_id
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@app.post(
    f"{API_PREFIX}/auth/logout",
    status_code=204,
    tags=["Authentication"]
)
def logout(data: RefreshTokenRequest, authorization: Optional[str] = Header(None)):
    """Выход из системы"""
    # Удаляем refresh токен
    if data.refresh_token in refresh_tokens_db:
        del refresh_tokens_db[data.refresh_token]
    
    return None


# ----- Защищенные эндпоинты (требуют аутентификации) -----

def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Получает текущего пользователя из токена"""
    return verify_token(authorization)


@app.get(
    f"{API_PREFIX}/users/me",
    response_model=UserWithProfile,
    tags=["Users"]
)
def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Получение профиля текущего пользователя"""
    user_id = current_user["user_id"]
    
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    user_data = users_db[user_id]
    user = User(
        id=user_data["id"],
        email=user_data["email"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        created_at=user_data["created_at"],
        updated_at=user_data["updated_at"]
    )
    
    # Определяем тип пользователя и возвращаем профиль
    if user_id in students_db:
        return UserWithProfile(
            user=user,
            profile=students_db[user_id],
            user_type=UserType.STUDENT
        )
    elif user_id in educators_db:
        return UserWithProfile(
            user=user,
            profile=educators_db[user_id],
            user_type=UserType.EDUCATOR
        )
    
    # Пользователь без профиля
    return UserWithProfile(
        user=user,
        profile=None,
        user_type=UserType.STUDENT  # По умолчанию
    )


@app.patch(
    f"{API_PREFIX}/students/me",
    response_model=UserWithProfile,
    tags=["Students"]
)
def update_current_student(
    data: StudentUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Обновление профиля текущего студента"""
    user_id = current_user["user_id"]
    
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    if user_id not in students_db:
        raise HTTPException(status_code=403, detail="Текущий пользователь не является студентом")
    
    user_data = users_db[user_id]
    now = get_current_time_iso()
    
    # Обновляем данные пользователя
    if data.first_name:
        user_data["first_name"] = data.first_name
    if data.last_name:
        user_data["last_name"] = data.last_name
    if data.password:
        user_data["password_hash"] = f"hashed_{data.password}"
    
    user_data["updated_at"] = now
    users_db[user_id] = user_data
    
    # Обновляем данные студента
    student = students_db[user_id]
    if data.building is not None:
        student.building = data.building
    if data.entrance is not None:
        student.entrance = data.entrance
    if data.floor is not None:
        student.floor = data.floor
    if data.room is not None:
        student.room = data.room
    if data.is_adult is not None:
        student.is_adult = data.is_adult
    
    student.updated_at = now
    students_db[user_id] = student
    
    user = User(
        id=user_data["id"],
        email=user_data["email"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        created_at=user_data["created_at"],
        updated_at=user_data["updated_at"]
    )
    
    return UserWithProfile(
        user=user,
        profile=student,
        user_type=UserType.STUDENT
    )


@app.patch(
    f"{API_PREFIX}/educators/me",
    response_model=UserWithProfile,
    tags=["Educators"]
)
def update_current_educator(
    data: EducatorUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Обновление профиля текущего воспитателя"""
    user_id = current_user["user_id"]
    
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    if user_id not in educators_db:
        raise HTTPException(status_code=403, detail="Текущий пользователь не является воспитателем")
    
    user_data = users_db[user_id]
    now = get_current_time_iso()
    
    # Обновляем данные пользователя
    if data.first_name:
        user_data["first_name"] = data.first_name
    if data.last_name:
        user_data["last_name"] = data.last_name
    if data.password:
        user_data["password_hash"] = f"hashed_{data.password}"
    
    user_data["updated_at"] = now
    users_db[user_id] = user_data
    
    # Обновляем данные воспитателя
    educator = educators_db[user_id]
    if data.is_night is not None:
        educator.is_night = data.is_night
    
    educator.updated_at = now
    educators_db[user_id] = educator
    
    user = User(
        id=user_data["id"],
        email=user_data["email"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        created_at=user_data["created_at"],
        updated_at=user_data["updated_at"]
    )
    
    return UserWithProfile(
        user=user,
        profile=educator,
        user_type=UserType.EDUCATOR
    )


@app.get(
    f"{API_PREFIX}/users",
    response_model=PaginatedUsers,
    tags=["Users"]
)
def get_users(
    page: int = 1,
    size: int = 20,
    user_type: Optional[UserType] = None,
    building: Optional[int] = None,
    entrance: Optional[int] = None,
    floor: Optional[int] = None,
    room: Optional[int] = None,
    is_night: Optional[bool] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Получение списка пользователей с пагинацией"""
    users_list = []
    
    for user_id, user_data in users_db.items():
        # Применяем фильтры
        if user_type == UserType.STUDENT and user_id not in students_db:
            continue
        if user_type == UserType.EDUCATOR and user_id not in educators_db:
            continue
        
        if building and user_id in students_db:
            if students_db[user_id].building != building:
                continue
        if entrance and user_id in students_db:
            if students_db[user_id].entrance != entrance:
                continue
        if floor and user_id in students_db:
            if students_db[user_id].floor != floor:
                continue
        if room and user_id in students_db:
            if students_db[user_id].room != room:
                continue
        if is_night is not None and user_id in educators_db:
            if educators_db[user_id].is_night != is_night:
                continue
        
        user = User(
            id=user_data["id"],
            email=user_data["email"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            created_at=user_data["created_at"],
            updated_at=user_data["updated_at"]
        )
        users_list.append(user)
    
    total = len(users_list)
    pages = (total + size - 1) // size
    
    # Пагинация
    start = (page - 1) * size
    end = start + size
    items = users_list[start:end]
    
    return PaginatedUsers(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@app.get(
    f"{API_PREFIX}/users/{{user_id}}",
    response_model=UserWithProfile,
    tags=["Users"]
)
def get_user_by_id(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Получение пользователя по ID"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь с указанным ID не найден")
    
    user_data = users_db[user_id]
    user = User(
        id=user_data["id"],
        email=user_data["email"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        created_at=user_data["created_at"],
        updated_at=user_data["updated_at"]
    )
    
    # Определяем тип пользователя
    if user_id in students_db:
        return UserWithProfile(
            user=user,
            profile=students_db[user_id],
            user_type=UserType.STUDENT
        )
    elif user_id in educators_db:
        return UserWithProfile(
            user=user,
            profile=educators_db[user_id],
            user_type=UserType.EDUCATOR
        )
    
    return UserWithProfile(
        user=user,
        profile=None,
        user_type=UserType.STUDENT
    )


@app.get(
    f"{API_PREFIX}/students/{{user_id}}",
    response_model=Student,
    tags=["Students"]
)
def get_student_by_id(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Получение студента по ID"""
    if user_id not in students_db:
        raise HTTPException(status_code=404, detail="Студент с указанным ID не найден")
    
    return students_db[user_id]


@app.get(
    f"{API_PREFIX}/educators/{{user_id}}",
    response_model=Educator,
    tags=["Educators"]
)
def get_educator_by_id(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Получение воспитателя по ID"""
    if user_id not in educators_db:
        raise HTTPException(status_code=404, detail="Воспитатель с указанным ID не найден")
    
    return educators_db[user_id]


# ----- Запуск сервера -----

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
