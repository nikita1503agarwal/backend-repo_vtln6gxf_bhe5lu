import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Trip, TripLocation

app = FastAPI(title="Personal Site API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Personal Site Backend Ready"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response


# Request model for incoming trip creation
class TripCreate(BaseModel):
    title: str
    date_text: str
    people: List[str] = []
    description: Optional[str] = None
    locations: List[TripLocation] = []
    photo_placeholders: List[str] = []
    video_urls: List[str] = []


@app.post("/api/trips")
def create_trip(trip: TripCreate):
    validated = Trip(**trip.model_dump())
    inserted_id = create_document("trip", validated)
    return {"id": inserted_id}


@app.get("/api/trips")
def list_trips():
    docs = get_documents("trip", {}, None)
    for d in docs:
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
    return {"items": docs}


@app.get("/api/trips/{trip_id}")
def get_trip(trip_id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    try:
        doc = db["trip"].find_one({"_id": ObjectId(trip_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Trip not found")
        doc["id"] = str(doc.pop("_id"))
        return doc
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid trip id")


@app.post("/api/seed")
def seed_trips():
    """Seed initial trips if collection is empty or titles missing."""
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    existing_titles = set([d.get("title") for d in get_documents("trip")])

    seed_data: List[Trip] = [
        Trip(
            title="Den Haag, Niederlande",
            date_text="Mai 2019 (genauer Zeitraum nicht mehr erinnerlich)",
            people=["gesamte Schulklasse"],
            description="Klassenausflug ans Meer, Strandbesuch und kleine Stadttour.",
            locations=[TripLocation(country_code="NLD", country_name="Niederlande", city="Den Haag", lat=52.0705, lon=4.3007)],
            photo_placeholders=["Strandbild", "Gruppenfoto Klasse", "Häuser in Den Haag"],
            video_urls=[],
        ),
        Trip(
            title="Dublin, Irland",
            date_text="Juli 2019",
            people=["ich", "meine Mutter", "meine Schwester Shelly"],
            description="Besuch bei meiner Schwester, die dort als Au-Pair gearbeitet hat; Natur und Stadt.",
            locations=[TripLocation(country_code="IRL", country_name="Irland", city="Dublin", lat=53.3498, lon=-6.2603)],
            photo_placeholders=["Familienfoto", "Natur Dublin"],
            video_urls=[],
        ),
        Trip(
            title="Hurghada, Ägypten",
            date_text="Oktober 2019 (genaues Datum nicht mehr verfügbar)",
            people=["ich", "meine Mutter"],
            description="Abenteuerurlaub mit Quad-Tour, Kameltour und Wüstenausflug.",
            locations=[TripLocation(country_code="EGY", country_name="Ägypten", city="Hurghada", lat=27.2579, lon=33.8116)],
            photo_placeholders=["Quad", "Wüste", "Kamele"],
            video_urls=[],
        ),
        Trip(
            title="Warschau, Polen",
            date_text="17.–21. April 2023",
            people=["Chris Lammel", "Kiran Odell", "Leon Morgenschweiß", "Anton Pfaff", "ich"],
            description="Städtetrip, Nachtleben, Shooting-Range (Pistole), Fotos auf Hochhäusern.",
            locations=[TripLocation(country_code="POL", country_name="Polen", city="Warschau", lat=52.2297, lon=21.0122)],
            photo_placeholders=["Hochhaus"],
            video_urls=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
        ),
        Trip(
            title="Budapest, Ungarn",
            date_text="23.–29. Juni 2024",
            people=["Peter Rentler", "Jeremy Penzien", "Luca Malik", "ich"],
            description="Urlaub mit Online-Freundesgruppe, Stadt, Bootstour, Luxusrestaurant, Club.",
            locations=[TripLocation(country_code="HUN", country_name="Ungarn", city="Budapest", lat=47.4979, lon=19.0402)],
            photo_placeholders=["Gruppenfoto", "Bootstour", "Restaurant", "Club"],
            video_urls=[],
        ),
        Trip(
            title="Frankreich – Monaco – Italien (Mehrländer-Reise)",
            date_text="10.–22. August 2024",
            people=["Anton Pfaff", "Chris Lammel", "Kiran Odell", "ich"],
            description="Zug/Interrail-Reise, Strand, Meer, Sightseeing, Städte und Natur.",
            locations=[
                TripLocation(country_code="FRA", country_name="Frankreich", city="Aix-en-Provence", lat=43.5297, lon=5.4474),
                TripLocation(country_code="FRA", country_name="Frankreich", city="Nizza", lat=43.7102, lon=7.2620),
                TripLocation(country_code="MCO", country_name="Monaco", city="Monaco", lat=43.7384, lon=7.4246),
                TripLocation(country_code="ITA", country_name="Italien", city="Bonassola", lat=44.1799, lon=9.5835),
                TripLocation(country_code="ITA", country_name="Italien", city="Mailand", lat=45.4642, lon=9.1900),
            ],
            photo_placeholders=["Aix-en-Provence", "Nizza", "Monaco", "Bonassola", "Mailand", "Gruppenfoto"],
            video_urls=[],
        ),
        Trip(
            title="Gáldar, Gran Canaria (Spanien)",
            date_text="14.–17. November 2024",
            people=["Kiran O’Dell", "ich"],
            description="Inseltrip mit Rollerfahrten, Natur, mein erstes eigenes Urlaubsvideo.",
            locations=[TripLocation(country_code="ESP", country_name="Spanien", city="Gáldar (Gran Canaria)", lat=28.1445, lon=-15.6504)],
            photo_placeholders=["Natur Gran Canaria", "Stadt Gáldar"],
            video_urls=["https://youtu.be/SGeLnxvfIsI"],
        ),
        Trip(
            title="Ukkel, Belgien",
            date_text="Dezember 2024 (genauer Zeitraum nicht mehr verfügbar)",
            people=["Luca Malic", "Peter Rändler", "Jeremy Penzien", "ich"],
            description="Airbnb-Aufenthalt, Stadt, Ausflüge, Video.",
            locations=[TripLocation(country_code="BEL", country_name="Belgien", city="Ukkel", lat=50.8020, lon=4.3572)],
            photo_placeholders=["Airbnb", "Stadt Ukkel"],
            video_urls=["https://youtu.be/kO34SsLgHoY"],
        ),
        Trip(
            title="Cúbelles & Barcelona, Spanien",
            date_text="1.–6. September 2025",
            people=["Leon Morgenschweiß", "Chris Lammel", "Kiran Odell", "Anton Pfaff", "ich", "Louis Schäfer", "Fabian Stork", "Patrick Mauler"],
            description="Unterkunft in Cúbelles, tägliche Mietwagenfahrten nach Barcelona, Strand, Stadt, Nachtleben.",
            locations=[
                TripLocation(country_code="ESP", country_name="Spanien", city="Cúbelles", lat=41.1950, lon=1.6364),
                TripLocation(country_code="ESP", country_name="Spanien", city="Barcelona", lat=41.3874, lon=2.1686),
            ],
            photo_placeholders=["Gruppenfoto", "Strand Cúbelles", "Barcelona Stadt", "Nachtleben"],
            video_urls=["https://youtu.be/1ZJsD6BcUNo"],
        ),
        Trip(
            title="Montenegro (Bucht von Kotor & Rundreise)",
            date_text="Datum nicht exakt erinnerlich",
            people=["Kiran O’Dell", "ich"],
            description="Mietwagen-Rundreise durch ganz Montenegro, Landschaften, Straßen, Küstenorte, Airbnb in Dobrota.",
            locations=[
                TripLocation(country_code="MNE", country_name="Montenegro", city="Kotor (Bucht)", lat=42.4247, lon=18.7712),
                TripLocation(country_code="MNE", country_name="Montenegro", city="Dobrota", lat=42.4576, lon=18.7684),
            ],
            photo_placeholders=["Bucht von Kotor", "Landschaft Montenegro", "Airbnb Dobrota"],
            video_urls=["https://youtu.be/i6UApGouaDE"],
        ),
        Trip(
            title="Brüssel, Belgien",
            date_text="Datum nicht dokumentiert",
            people=[],
            description="Städtetrip nach Brüssel.",
            locations=[TripLocation(country_code="BEL", country_name="Belgien", city="Brüssel", lat=50.8503, lon=4.3517)],
            photo_placeholders=["Brüssel Stadt"],
            video_urls=["https://youtu.be/kO34SsLgHoY"],
        ),
    ]

    inserted = 0
    for t in seed_data:
        if t.title not in existing_titles:
            create_document("trip", t)
            inserted += 1

    return {"inserted": inserted}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
