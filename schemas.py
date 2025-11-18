"""
Database Schemas for the personal website

Each Pydantic model represents a collection in MongoDB. The collection name is the lowercase of the class name.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class TripLocation(BaseModel):
    country_code: str = Field(..., description="ISO A3 country code (e.g., DEU, IRL)")
    country_name: str = Field(..., description="Human readable country name")
    city: Optional[str] = Field(None, description="City or region name")
    lat: Optional[float] = Field(None, description="Latitude for map marker")
    lon: Optional[float] = Field(None, description="Longitude for map marker")


class Trip(BaseModel):
    """
    Collection name: "trip"
    Represents a single travel entry used for the travel map and timeline.
    """

    title: str = Field(..., description="Trip title")
    date_text: str = Field(..., description="Exact date or descriptive text if not remembered")
    people: List[str] = Field(default_factory=list, description="People who joined the trip")
    description: Optional[str] = Field(None, description="Free form description")

    # One trip can span multiple locations/countries (e.g., Interrail)
    locations: List[TripLocation] = Field(default_factory=list, description="Locations touched in this trip")

    # Media
    photo_placeholders: List[str] = Field(default_factory=list, description="List of photo placeholders (captions)")
    video_urls: List[HttpUrl] = Field(default_factory=list, description="List of YouTube or other video URLs")
