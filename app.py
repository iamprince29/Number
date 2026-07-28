import os
import duckdb
from fastapi import FastAPI, HTTPException, Query

app = FastAPI()

# Environment variable se MotherDuck token retrieve kar rahe hain
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
        # MotherDuck se database connect kar rahe hain
        con = duckdb.connect(f"md:my_data?motherduck_token={MOTHERDUCK_TOKEN}")
        
        # User search query
        result = con.execute(
            "SELECT * FROM users WHERE Mobile = ? LIMIT 10", [mobile]
        ).fetchall()
        
        cols = [desc[0] for desc in con.description]
        con.close()
        
        return {
            "status": "success", 
            "count": len(result),
            "data": [dict(zip(cols, row)) for row in result]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
