import os
import duckdb
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(
    title="Number Data Search API",
    description="DuckDB + HuggingFace Dataset Powered Search API"
)

# Hugging Face Access Token
HF_TOKEN = os.getenv("HF_TOKEN", "")

# Fix 1: Directly HTTPS link use karenge huggingface datasets ka
# Aggregated parquet structure ke liye direct URL set kar rahe hain
HF_DATASET_URI = "https://huggingface.co/datasets/Noobster1/Numberdata/resolve/main/*.parquet"

def get_duckdb_con():
    con = duckdb.connect(database=':memory:')
    
    # Fix 2: 'hf' ki jagah reliable 'httpfs' extension use karenge
    con.execute("INSTALL httpfs; LOAD httpfs;")
    
    # Hugging Face authentication header setup (Agar dataset private hai)
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
            FROM read_parquet('{HF_DATASET_URI}') 
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
            FROM read_parquet('{HF_DATASET_URI}') 
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
