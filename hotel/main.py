from fastapi import FastAPI

from hotel.db.create_db import create_db
from hotel.db.engine import init_db
from hotel.routers import bookings, customers, rooms

app = FastAPI()


DB_FILE = "sqlite:///hotel.db"
# create_db(DB_FILE)


@app.on_event("startup")
async def startup_event():
    init_db(DB_FILE)


@app.get("/")
def read_root():
    return "The server is running."


app.include_router(customers.router)
app.include_router(rooms.router)
app.include_router(bookings.router)
