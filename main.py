"""
六一儿童节 - 王梦郝专属网站后端
FastAPI 服务：提供静态页面 + 愿望收集 API
"""
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Children's Day for 王梦郝")

# CORS 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据文件路径
BASE_DIR = Path(__file__).parent
WISHES_FILE = BASE_DIR / "wishes.json"

# 北京时间时区
CST = timezone(timedelta(hours=8))


def load_wishes() -> list:
    if not WISHES_FILE.exists():
        return []
    with open(WISHES_FILE, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def save_wishes(wishes: list):
    with open(WISHES_FILE, "w", encoding="utf-8") as f:
        json.dump(wishes, f, ensure_ascii=False, indent=2)


@app.post("/api/wish")
async def receive_wish(request: Request):
    """接收王梦郝的愿望"""
    try:
        body = await request.json()
        wish_text = body.get("wish", "").strip()
        if not wish_text:
            return JSONResponse({"ok": False, "msg": "愿望不能为空哦~"}, status_code=400)

        wishes = load_wishes()
        wish_record = {
            "id": len(wishes) + 1,
            "wish": wish_text,
            "time": datetime.now(CST).strftime("%Y-%m-%d %H:%M:%S"),
        }
        wishes.append(wish_record)
        save_wishes(wishes)

        return {"ok": True, "msg": "愿望已收到！", "id": wish_record["id"]}
    except Exception as e:
        return JSONResponse({"ok": False, "msg": str(e)}, status_code=500)


@app.get("/api/wishes")
async def get_wishes(password: str = ""):
    """查看所有愿望（供用户查看，简单密码保护）"""
    if password != "wangmenghao520":
        return JSONResponse({"ok": False, "msg": "密码不对哦~"}, status_code=403)

    wishes = load_wishes()
    return {"ok": True, "wishes": wishes, "total": len(wishes)}


@app.get("/api/wishes/latest")
async def get_latest_wish():
    """获取最新一条愿望"""
    wishes = load_wishes()
    if not wishes:
        return {"ok": True, "wish": None}
    return {"ok": True, "wish": wishes[-1]}


# 静态文件挂载
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
