# backend/app.py
import os
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from backend import gemini_client
from dotenv import load_dotenv
load_dotenv()


DB = os.getenv("REVIEWS_DB", "reviews.db")
app = FastAPI()

def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rating INTEGER,
        review TEXT,
        user_response TEXT,
        summary TEXT,
        recommended_action TEXT,
        created_at TIMESTAMP
    )
    """)
    con.commit()
    con.close()

init_db()

class ReviewIn(BaseModel):
    rating: int
    review: str

class ReviewOut(BaseModel):
    id: int
    rating: int
    review: str
    user_response: Optional[str]
    summary: Optional[str]
    recommended_action: Optional[str]
    created_at: str

@app.post("/submit_review", response_model=ReviewOut)
def submit_review(payload: ReviewIn):
    if not (1 <= payload.rating <= 5):
        raise HTTPException(status_code=400, detail="rating must be 1-5")
    prompt = f"""You are a friendly assistant. The user review:
\"\"\"{payload.review}\"\"\"
Generate a short friendly reply thanking them, acknowledging the rating, and a next step if rating <=2. Return only the reply text."""
    user_response = gemini_client.generate_text(prompt)
    con = sqlite3.connect(DB)
    cur = con.cursor()
    created_at = datetime.utcnow().isoformat()
    cur.execute("INSERT INTO reviews (rating, review, user_response, created_at) VALUES (?, ?, ?, ?)",
                (payload.rating, payload.review, user_response, created_at))
    rid = cur.lastrowid
    con.commit()
    con.close()
    return ReviewOut(id=rid, rating=payload.rating, review=payload.review,
                     user_response=user_response, summary=None, recommended_action=None,
                     created_at=created_at)

@app.get("/reviews", response_model=List[ReviewOut])
def get_reviews(min_stars: int = 1, limit: int = 200):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT id, rating, review, user_response, summary, recommended_action, created_at FROM reviews WHERE rating >= ? ORDER BY id DESC LIMIT ?",
                (min_stars, limit))
    rows = cur.fetchall()
    con.close()
    out = []
    for r in rows:
        out.append(ReviewOut(id=r[0], rating=r[1], review=r[2], user_response=r[3], summary=r[4], recommended_action=r[5], created_at=r[6]))
    return out

@app.post("/admin/summarize/{review_id}", response_model=ReviewOut)
def summarize_review(review_id: int):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT id, rating, review, user_response, summary, recommended_action, created_at FROM reviews WHERE id = ?",
                (review_id,))
    r = cur.fetchone()
    if not r:
        raise HTTPException(status_code=404)
    if r[4] and r[5]:
        con.close()
        return ReviewOut(id=r[0], rating=r[1], review=r[2], user_response=r[3], summary=r[4], recommended_action=r[5], created_at=r[6])
    review_text = r[2]
    sum_prompt = f"Summarize this customer review in one short sentence: \"\"\"{review_text}\"\"\""
    summary = gemini_client.generate_text(sum_prompt)
    action_prompt = f"Given the review: \"\"\"{review_text}\"\"\". Recommend a single actionable next step for the business."
    action = gemini_client.generate_text(action_prompt)
    cur.execute("UPDATE reviews SET summary = ?, recommended_action = ? WHERE id = ?", (summary, action, review_id))
    con.commit()
    con.close()
    return ReviewOut(id=r[0], rating=r[1], review=r[2], user_response=r[3], summary=summary, recommended_action=action, created_at=r[6])
