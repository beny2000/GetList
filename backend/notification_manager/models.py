from pydantic import BaseModel


class GeoLocation(BaseModel):
    latitude: str
    longitude: str


class SearchNearby(BaseModel):
    location: GeoLocation
    list_id: str
    radius: int = 10000
    token: str