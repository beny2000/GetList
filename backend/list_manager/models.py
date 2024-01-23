from pydantic import BaseModel


class Location(BaseModel):
    """
    Represents the latitude and longitude coordinates of a location.

    - **latitude**: The latitude coordinate.
    - **longitude**: The longitude coordinate.
    """
    latitude: str
    longitude: str

class EditListItem(BaseModel):
    """
    Represents data for editing a list item.

    - **item**: The item to be edited.
    - **list_id**: The ID of the list containing the item.
    - **id** (optional): The ID of the item to be edited.
    """
    item: str
    list_id: str
    id: str = None

class SearchNearby(BaseModel):
    """
    Represents criteria for searching for items in nearby locations.

    - **location**: The location coordinates.
    - **list_id**: The ID of the list for the search.
    - **radius** (optional): The search radius in meters (default is 10000 meters).
    """
    location: Location
    list_id: str
    radius: int = 200

class GeoLocation(BaseModel):
    """
    Represents criteria for notifying on items in nearby locations with push notification token .

    - **location**: The location coordinates.
    - **list_id**: The ID of the list for the search.
    - **radius** (optional): The search radius in meters (default is 10000 meters).
    - **token**: The push notification token.
    """
    location: Location
    list_id: str
    radius: int = 10000
    token: str