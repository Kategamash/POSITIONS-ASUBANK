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
    # Идемпотентный seed (контролируется AUTO_SEED, по умолчанию включён).
    import os

    if str(os.getenv("AUTO_SEED", "true")).lower() in ("1", "true", "yes"):
        try:
            from app.seed_data import seed_default_data

            seed_default_data()
        except Exception as exc:  # noqa: BLE001
            import logging

            logging.getLogger(__name__).warning("Авто-seed пропущен: %s", exc)


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
        "system": "POSITIONS-ASUBANK",
        "version": "1.0.0",
        "documentation": "/docs",
    }


@app.get("/health", tags=["Служебное"])
def health():
    return {"status": "ok"}
