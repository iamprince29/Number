import os
import duckdb
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(title="Number Details API")

# Hugging Face Access Token (Agar repo private hai)
HF_TOKEN = os.getenv("HF_TOKEN", "")

def get_duckdb_con():
    con = duckdb.connect(database=':memory:')
    
    # 1. HuggingFace Extension LOAD karna
    con.execute("INSTALL hf; LOAD hf;")
    
    # 2. Private Dataset ke liye Token set karna (Agar dataset Public hai toh token optionally ignore hoga)
    if HF_TOKEN:
        con.execute(f"SET hf_token='{HF_TOKEN}';")
        
    return con

@app.get("/")
def home():
    return {"message": "API Active! Go to /docs to test endpoints."}

@app.get("/search/mobile/{mobile_no}")
def get_by_mobile(mobile_no: str):
    try:
        con = get_duckdb_con()
        
        # 'hf://datasets/Noobster1/Numberdata/*.parquet' direct use karo
        query = """
            SELECT Mobile, name, fname, address, alt, circle, id, email
            FROM 'hf://datasets/Noobster1/Numberdata/*.parquet'
            WHERE CAST(Mobile AS VARCHAR) = ?
            LIMIT 5
        """
        result = con.execute(query, [str(mobile_no)]).df()
        con.close()
        
        if result.empty:
            raise HTTPException(status_code=404, detail="Mobile number not found")
            
        clean_result = result.fillna("").to_dict(orient="records")
        return {"count": len(clean_result), "data": clean_result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/name")
def search_by_name(name: str = Query(..., description="Name to search"), limit: int = Query(10, le=50)):
    try:
        con = get_duckdb_con()
        
        query = f"""
            SELECT Mobile, name, fname, address, alt, circle, id, email
            FROM 'hf://datasets/Noobster1/Numberdata/*.parquet'
            WHERE LOWER(name) LIKE LOWER(?)
            LIMIT {limit}
        """
        result = con.execute(query, [f"%{name}%"]).df()
        con.close()
        
        clean_result = result.fillna("").to_dict(orient="records")
        return {"count": len(clean_result), "data": clean_result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
