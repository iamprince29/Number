import os
import duckdb
from fastapi import FastAPI, HTTPException

app = FastAPI()

MOTHERDUCK_TOKEN = os.getenv("MOTHERDUCK_TOKEN")

def get_db():
    if not MOTHERDUCK_TOKEN:
        raise Exception("MOTHERDUCK_TOKEN environment variable missing!")
    return duckdb.connect(f'md:my_data?token={MOTHERDUCK_TOKEN}')

@app.get("/")
def home():
    return {"status": "API is Live!"}

@app.get("/search/mobile/{mobile_no}")
def search_by_mobile(mobile_no: str):
    try:
        con = get_db()
        query = "SELECT Mobile, name, fname, address, alt, circle, id, email FROM users WHERE CAST(Mobile AS VARCHAR) = ? LIMIT 10"
        result = con.execute(query, [str(mobile_no)]).df()
        con.close()
        
        if result.empty:
            raise HTTPException(status_code=404, detail="No record found")
            
        return {
            "status": "success",
            "count": len(result), 
            "data": result.fillna("").to_dict(orient="records")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
