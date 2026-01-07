import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from hotel.config import settings
from hotel.db.engine import init_db, engine, DBSession
from hotel.routers import bookings, customers, rooms, health
from hotel.middleware.exception_handlers import register_exception_handlers
from hotel.middleware.rate_limiter import limiter
from hotel.middleware.rate_limit_handlers import rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database connection
    init_db(settings.database_url)

    yield

    # Close all sessions
    DBSession.close_all()

    # Dispose of the engine connection pool
    if engine is not None:
        engine.dispose()


app = FastAPI(lifespan=lifespan)

# Register rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Register global exception handlers
register_exception_handlers(app)


@app.get("/")
def read_root():
    return "The server is watching you, without blinking."


app.include_router(health.router)
app.include_router(customers.router)
app.include_router(rooms.router)
app.include_router(bookings.router)


if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port, reload=settings.reload)
