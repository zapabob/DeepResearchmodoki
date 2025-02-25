from fastapi import APIRouter, HTTPException
import os
import json
from typing import List

router = APIRouter()

# Directory to store research results
RESEARCH_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "research_results")
if not os.path.exists(RESEARCH_DIR):
    os.makedirs(RESEARCH_DIR)

@router.get("/", response_model=List[str])
async def list_research_files():
    """リサーチ結果ファイルの一覧を返します"""
    try:
        files = os.listdir(RESEARCH_DIR)
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{filename}")
async def read_research_file(filename: str):
    """指定されたファイルの内容を返します"""
    filepath = os.path.join(RESEARCH_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="ファイルが存在しません")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_research_file(filename: str, content: dict):
    """新しいリサーチ結果ファイルを作成します"""
    filepath = os.path.join(RESEARCH_DIR, filename)
    if os.path.exists(filepath):
        raise HTTPException(status_code=400, detail="ファイルは既に存在します")
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        return {"message": "ファイルが作成されました", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{filename}")
async def update_research_file(filename: str, content: dict):
    """既存のリサーチ結果ファイルを更新します"""
    filepath = os.path.join(RESEARCH_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="ファイルが存在しません")
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        return {"message": "ファイルが更新されました", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{filename}")
async def delete_research_file(filename: str):
    """指定されたリサーチ結果ファイルを削除します"""
    filepath = os.path.join(RESEARCH_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="ファイルが存在しません")
    try:
        os.remove(filepath)
        return {"message": "ファイルが削除されました", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 