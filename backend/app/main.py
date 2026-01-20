from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.app.database import Base, engine, SessionLocal
from backend.app import models
from backend.app.routers import cabins, devices, events, integrations, people, reservations, users

app = FastAPI(title="Keike Stay Web")

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

templates = Jinja2Templates(directory="frontend/templates")

app.include_router(cabins.router)
app.include_router(people.router)
app.include_router(reservations.router)
app.include_router(devices.router)
app.include_router(events.router)
app.include_router(users.router)
app.include_router(integrations.router)


@app.get("/")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/cabanas")
def cabanas(request: Request):
    return templates.TemplateResponse("cabanas.html", {"request": request})


@app.get("/pessoas")
def pessoas(request: Request):
    return templates.TemplateResponse("pessoas.html", {"request": request})


@app.get("/reservas")
def reservas(request: Request):
    return templates.TemplateResponse("reservas.html", {"request": request})


@app.get("/dispositivos")
def dispositivos(request: Request):
    return templates.TemplateResponse("dispositivos.html", {"request": request})


@app.get("/automacao")
def automacao(request: Request):
    return templates.TemplateResponse("automacao.html", {"request": request})


@app.get("/usuarios")
def usuarios(request: Request):
    return templates.TemplateResponse("usuarios.html", {"request": request})
