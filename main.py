from fastapi import FastAPI, Request
import time

from src.routes import contacts, health, auth, users
from src.core.error_handlers import init_exception_handlers


# Створюємо додаток (ASGI-додаток на базі Starlette)
app = FastAPI(
    title="Contacts Service API",
    description="API for contact management with JWT authentication: CRUD, search, birthdays.",
    version="2.0.0",
)

init_exception_handlers(app)  # Підключення глобальних хендлерів

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(health.router, prefix="/system")


# Middleware для вимірювання часу обробки запиту
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)  
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)  # додаємо в headers
    return response


# uvicorn main:app --reload
# http://127.0.0.1:8000/docs


""" 
{
  "first_name": "Hello",
  "last_name": "Test_1",
  "email": "hello@example.com",
  "phone": "+380501112233",
  "birthday": "1991-10-05",
  "extra": "friend"
}

"""
