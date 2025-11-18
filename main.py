import os
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import create_document, get_documents

app = FastAPI(title="Christian Events API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    type: str
    start_date: datetime
    end_date: Optional[datetime] = None
    location_name: Optional[str] = None
    latitude: float
    longitude: float
    city: Optional[str] = None
    country: Optional[str] = None
    url: Optional[str] = None


@app.get("/")
def read_root():
    return {"message": "Christian Events API running"}


@app.get("/api/events")
def list_events(
    start: Optional[datetime] = Query(None, description="ISO datetime >= this"),
    end: Optional[datetime] = Query(None, description="ISO datetime <= this"),
    types: Optional[str] = Query(None, description="Comma-separated list of event types"),
    q: Optional[str] = Query(None, description="Free-text search in title/description/location"),
    limit: int = Query(200, ge=1, le=1000),
):
    """Return events filtered by date range, type, and search query."""
    from pymongo import ASCENDING
    from bson.regex import Regex

    filter_dict: dict = {}

    # Type filter
    if types:
        type_list = [t.strip() for t in types.split(",") if t.strip()]
        if type_list:
            filter_dict["type"] = {"$in": type_list}

    # Date filters
    if start or end:
        date_filter = {}
        if start:
            date_filter["$gte"] = start
        if end:
            date_filter["$lte"] = end
        filter_dict["start_date"] = date_filter

    # Text-like search (simple contains using regex OR across fields)
    if q:
        regex = Regex(q, "i")
        filter_dict["$or"] = [
            {"title": regex},
            {"description": regex},
            {"location_name": regex},
            {"city": regex},
            {"country": regex},
        ]

    docs = get_documents("event", filter_dict, limit)

    # Normalize ObjectId and datetime to ISO
    def normalize(doc):
        doc["id"] = str(doc.pop("_id")) if "_id" in doc else None
        for k in ["start_date", "end_date", "created_at", "updated_at"]:
            if doc.get(k) and isinstance(doc[k], datetime):
                doc[k] = doc[k].isoformat()
        return doc

    items = [normalize(d) for d in docs]
    return {"items": items, "count": len(items)}


@app.post("/api/events", status_code=201)
def create_event(payload: EventCreate):
    # Validate minimal fields already handled by Pydantic
    event_id = create_document("event", payload.model_dump())
    return {"id": event_id}


@app.get("/test")
def test_database():
    """Health check for database connectivity and schema visibility"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
