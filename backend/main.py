# 必须在所有导入之前加载环境变量
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path

static_dir = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="因果推演引擎 API",
    description="基于大模型的因果推演引擎后端服务",
    version="1.0.0"
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://localhost:5174"
    ).split(",")
    if origin.strip()
]

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    if static_dir.is_dir():
        from fastapi.responses import FileResponse
        return FileResponse(static_dir / "index.html")
    return {"message": "因果推演引擎 API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 导入路由
from app.api import causal_router, v2_router

app.include_router(causal_router.router, prefix="/api/v1", tags=["causal"])
app.include_router(v2_router.router, prefix="/api/v2", tags=["causal-v2"])

if static_dir.is_dir():
    from fastapi.staticfiles import StaticFiles

    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
