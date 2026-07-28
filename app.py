import os
import duckdb
from fastapi import FastAPI, HTTPException, Query

app = FastAPI()

MOTHERDUCK_TOKEN = os.getenv("MOTHERDUCK_TOKEN")

@app.get("/")
def home():
    return {"status": "API is Live!"}

@app.get("/search")
def search_mobile(mobile: str = Query(...)):
    if not MOTHERDUCK_TOKEN:
        raise HTTPException(
            status_code=500, 
            detail="MOTHERDUCK_TOKEN environment variable missing"
        )
        
    try:
        con = duckdb.connect(f"md:my_data?motherduck_token={MOTHERDUCK_TOKEN}")
        
        # Clean mobile input
        clean_mobile = mobile.strip()
        search_pattern = f"%{clean_mobile}%"
        
        # Column casting + LIKE query for flexible matching
        query = """
            SELECT * FROM my_data.users 
            WHERE TRY_CAST(Mobile AS VARCHAR) LIKE ? 
            LIMIT 10
        """
        
        result = con.execute(query, [search_pattern]).fetchall()
        cols = [desc[0] for desc in con.description]
        con.close()
        
        if not result:
            return {"status": "success", "count": 0, "message": "Details not found", "data": []}
            
        return {
            "status": "success", 
            "count": len(result),
            "data": [dict(zip(cols, row)) for row in result]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
