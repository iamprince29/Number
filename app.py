import os
import duckdb
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(
    title="Number Data Search API",
    description="Optimized DuckDB + Hugging Face Search API"
)

HF_TOKEN = os.getenv("HF_TOKEN", "")
# Multi-part parquet direct URL support
HF_PARQUET_URL = "https://huggingface.co/datasets/Noobster1/Numberdata/resolve/main/users_data.parquet"

def execute_query(query: str, params: list):
    # Har query ke liye clean in-memory db setup
    con = duckdb.connect(database=':memory:', read_only=False)
    
    # 1. Enforce strict Memory limits for Render Free Tier (512MB RAM)
    con.execute("SET max_memory='384MB';")
    con.execute("SET threads=1;")
    
    # 2. HTTP & Parquet Memory Tweaks
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute("SET http_keep_alive=false;")
    con.execute("SET preserve_insertion_order=false;")
    
    if HF_TOKEN:
        con.execute(f"SET http_headers={{'Authorization': 'Bearer {HF_TOKEN}'}};")
        
    try:
        df = con.execute(query, params).df()
        return df
    finally:
        con.close()

@app.get("/")
def home():
    return {"status": "ok", "message": "API Active"}

@app.get("/search/mobile/{mobile_no}")
def search_by_mobile(mobile_no: str):
    try:
        # Avoid scanning unneeded data
        query = f"""
            SELECT Mobile, name, fname, address, alt, circle, id, email
            FROM read_parquet('{HF_PARQUET_URL}') 
            WHERE CAST(Mobile AS VARCHAR) = ?
            LIMIT 10
        """
        result = execute_query(query, [str(mobile_no)])
        
        if result.empty:
            raise HTTPException(status_code=404, detail="Mobile details not found")
            
        clean_result = result.fillna("").to_dict(orient="records")
        return {"count": len(clean_result), "data": clean_result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/name")
def search_by_name(
    name: str = Query(..., description="Name to search"),
    limit: int = Query(10, le=50)
):
    try:
        query = f"""
            SELECT Mobile, name, fname, address, alt, circle, id, email
            FROM read_parquet('{HF_PARQUET_URL}') 
            WHERE LOWER(name) LIKE LOWER(?)
            LIMIT {limit}
        """
        result = execute_query(query, [f"%{name}%"])
        
        if result.empty:
            raise HTTPException(status_code=404, detail="Name details not found")
            
        clean_result = result.fillna("").to_dict(orient="records")
        return {"count": len(clean_result), "data": clean_result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
