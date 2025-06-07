"""FastAPI application entry point."""
from fastapi import FastAPI

from .routers import all_routers

app = FastAPI(
    title="Ted OS Backend API",
    description="Ted OS의 비즈니스 로직을 제공하는 API 서버",
    version="0.1.0",
)

for router in all_routers:
    app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
