import os
import duckdb
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(
    title="Number Data Search API",
    description="Optimized DuckDB + HuggingFace Dataset Search API"
)

HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_PARQUET_URL = "https://huggingface.co/datasets/Noobster1/Numberdata/resolve/main/users_data.parquet"

def execute_query(query: str, params: list):
    # Har request ke liye memory limit restricted connection
    con = duckdb.connect(database=':memory:', read_only=False)
    
    # Render Free tier RAM limits
    con.execute("SET max_memory='384MB';")
    con.execute("SET threads=1;") 
    
    con.execute("INSTALL httpfs; LOAD httpfs;")
    
    if HF_TOKEN:
        con.execute(f"SET http_headers={{'Authorization': 'Bearer {HF_TOKEN}'}};")
        
    try:
        df = con.execute(query, params).df()
        return df
    finally:
        con.close()

@app.get("/")
def home():
    return {"message": "API Active & Ready!"}

# 1. Mobile Search Endpoint
@app.get("/search/mobile/{mobile_no}")
def search_by_mobile(mobile_no: str):
    try:
        query = f"""
            SELECT Mobile, name, fname, address, alt, circle, id, email
            FROM read_parquet('{HF_PARQUET_URL}') 
            WHERE CAST(Mobile AS VARCHAR) = ?
            LIMIT 10
        """
        result = execute_query(query, [str(mobile_no)])
        
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
        query = f"""
            SELECT Mobile, name, fname, address, alt, circle, id, email
            FROM read_parquet('{HF_PARQUET_URL}') 
            WHERE LOWER(name) LIKE LOWER(?)
            LIMIT {limit}
        """
        result = execute_query(query, [f"%{name}%"])
        
        if result.empty:
            raise HTTPException(status_code=404, detail="Name ke details nahi mile")
            
        clean_result = result.fillna("").to_dict(orient="records")
        return {"count": len(clean_result), "data": clean_result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
