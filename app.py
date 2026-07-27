import os
import duckdb
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(
    title="Number Data Search API",
    description="DuckDB + HuggingFace Dataset Powered Search API"
)

# Hugging Face Access Token
HF_TOKEN = os.getenv("HF_TOKEN", "")

# HuggingFace Dataset Direct URL (Agar file ka naam kuch aur hai jaise data.parquet, toh yahan change kar lena)
# Agar multiple files hain toh wildcard allow karne ki command niche add kar di hai
HF_PARQUET_URL = "https://huggingface.co/datasets/Noobster1/Numberdata/resolve/main/data.parquet"

def get_duckdb_con():
    con = duckdb.connect(database=':memory:')
    con.execute("INSTALL httpfs; LOAD httpfs;")
    
    # Ye line httpfs ko asterisks (*) allow karne ki permission de degi
    con.execute("SET allow_asterisks_in_http_paths = true;")
    
    if HF_TOKEN:
        con.execute(f"SET http_headers={{'Authorization': 'Bearer {HF_TOKEN}'}};")
        
    return con

@app.get("/")
def home():
    return {"message": "API Active! Go to /docs to test endpoints."}

# 1. Mobile Number Search Endpoint
@app.get("/search/mobile/{mobile_no}")
def search_by_mobile(mobile_no: str):
    try:
        con = get_duckdb_con()
        
        query = f"""
            SELECT Mobile, name, fname, address, alt, circle, id, email
            FROM read_parquet('{HF_PARQUET_URL}') 
            WHERE CAST(Mobile AS VARCHAR) = ?
            LIMIT 10
        """
        
        result = con.execute(query, [str(mobile_no)]).df()
        con.close()
        
        if result.empty:
            raise HTTPException(status_code=404, detail="Mobile number ke details nahi mile")
            
        clean_result = result.fillna("").to_dict(orient="records")
        return {"count": len(clean_result), "data": clean_result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. Name Search Endpoint
@app.get("/search/name")
def search_by_name(
    name: str = Query(..., description="Name to search"),
    limit: int = Query(10, le=50)
):
    try:
        con = get_duckdb_con()
        
        query = f"""
            SELECT Mobile, name, fname, address, alt, circle, id, email
            FROM read_parquet('{HF_PARQUET_URL}') 
            WHERE LOWER(name) LIKE LOWER(?)
            LIMIT {limit}
        """
        
        result = con.execute(query, [f"%{name}%"]).df()
        con.close()
        
        if result.empty:
            raise HTTPException(status_code=404, detail="Name ke details nahi mile")
            
        clean_result = result.fillna("").to_dict(orient="records")
        return {"count": len(clean_result), "data": clean_result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
