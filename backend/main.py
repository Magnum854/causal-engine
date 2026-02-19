# 必须在所有导入之前加载环境变量
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="因果推演引擎 API",
    description="基于大模型的因果推演引擎后端服务",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Vite 端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "因果推演引擎 API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 导入路由
from app.api import causal_router

app.include_router(causal_router.router, prefix="/api/v1", tags=["causal"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

