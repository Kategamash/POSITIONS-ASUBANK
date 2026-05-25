from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, accounts, currencies, positions, corrections, payments, admin, integration

app = FastAPI(
    title="ПОЗИЦИИ-АСУБАНК",
    description=(
        "Автоматизированная мидл-офис система для ведения позиций по счетам ностро "
        "и операционной отчётности. Команда №2."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(currencies.router)
app.include_router(accounts.router)
app.include_router(positions.router)
app.include_router(corrections.router)
app.include_router(payments.router)
app.include_router(admin.router)
app.include_router(integration.router)


@app.get("/", tags=["Служебное"])
def root():
    return {
        "система": "ПОЗИЦИИ-АСУБАНК",
        "версия": "1.0.0",
        "документация": "/docs",
    }


@app.get("/health", tags=["Служебное"])
def health():
    return {"статус": "ok"}
