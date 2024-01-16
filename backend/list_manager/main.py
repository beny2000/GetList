
import os
import logging
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from lib_db import DatabaseInterface
from .models import GeoLocation, EditListItem, SearchNearby, Location

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
print(os.environ.get('MODEL_MANAGER_HOST'))
try:
    db = DatabaseInterface(os.environ.get('DB_HOST'), os.environ.get('APP_DB'))
    # "http://model_manager:8082/api/tag_item"
    places_api_key = os.environ.get('API_KEY', "")
    model_manager_url = f"{os.environ.get('MODEL_MANAGER_HOST')}/api/tag_item"
    # http://notification_manager:8083/api/search_nearby"
    notification_manager_url = f"{os.environ.get('NOTIFICATION_MANAGER_HOST')}/api/search_nearby"
except Exception as ex:
    logging.error(f"Error: Missing environment variable. {ex}")
    raise ex

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url='/docs')


@app.post("/api/geolocation")
async def geo_location(body: GeoLocation):  # TODO encrpt token
   """
   Geolocation endpoint to send data to a notification manager.

   Parameters:
   - **body** (GeoLocation): Object containing latitude, longitude, list_id, radius, and token.

   Returns:
   - **str**: "OK" if successful.

   Raises:
   - **HTTPException**: If an error occurs during the process.
   """
   try:
      requests.post(
      notification_manager_url,
      json={
         "location": {
         "latitude": body.location.latitude,
         "longitude": body.location.longitude
         },
         "list_id": body.list_id,
         "radius": body.radius,
         "token": body.token
      })
   except Exception as e:
      logging.error(f"Error geo_location failed. {e}")
      raise HTTPException(status_code=500, detail="Server error")
   return "OK"

@app.get("/api/create_list")
async def create_list(list_id: str):
   try:
      list_exists = db.find_one("lists", {"list_id": list_id})
      print(list_exists)
      if not list_exists:
         db.insert_one("lists", {"list_id": list_id, "items": []})

      return "OK"
   except Exception as e:
      logging.error(f"Error get_list failed. {e}")
      raise HTTPException(status_code=500, detail="Server error")


@app.get("/api/get_list")
async def get_list(list_id: str):
   """
   Retrieve a list based on the provided list_id.

   Parameters:
   - **list_id** (str): The ID of the list.

   Returns:
   - A list of documents with '_id' replaced by 'id', or raises a server error if unsuccessful.
   """
   try:
      return db.find_all("lists", {"list_id": list_id})
   except Exception as e:
      logging.error(f"Error get_list failed. {e}")
      raise HTTPException(status_code=500, detail="Server error")


@app.post("/api/items_nearby")
async def items_nearby(body: SearchNearby):
   """
   Find nearby items and locations by type given a point and list ID.

   Parameters:
   - **body** (SearchNearby): Object containing location, list_id, and radius.

   Returns:
   - A list of combined items and locations, or raises a server error if unsuccessful.
   """
   try:
      return db.find_nearby_items(body.list_id, float(body.location.latitude), float(body.location.longitude), body.radius)
   except Exception as e:
      logging.error(f"Error items_nearby failed. {e}")
      raise HTTPException(status_code=500, detail="Server error")


@app.post("/api/add_list_item")
async def add_list_item(item: EditListItem):
   """
   Add an item to the 'items' list within a specified collection and list.

   Parameters:
   - **item** (EditListItem): Object containing item, list_id, and optional id.

   Returns:
   - **str**: "OK" if successful.

   Raises:
   - **HTTPException**: If an error occurs during the process.
   """
   
   try:
      tag = requests.get(f"{model_manager_url}?item={item.item}").json()

      if "grocery" in tag or "supermarket" in tag:
         tag = "grocery_or_supermarket"

      db.push_to_items_list('lists', item.list_id, {
         "item": item.item,
         "tag": tag,
         "id": str(abs(hash(item.item)))})
      return "OK"
   except Exception as e:
      logging.error(f"Error add_list_item failed. {e}")
      raise HTTPException(status_code=500, detail="Server error")


@app.post("/api/remove_list_item")
async def remove_from_items_list(item: EditListItem):
   """
   Remove items from the 'items' list within a specified collection and list based on a given criteria.

   Parameters:
   - **item** (EditListItem): Object containing item and list_id.

   Returns:
   - **str**: "OK" if successful.

   Raises:
   - **HTTPException**: If an error occurs during the process.
   """
   try:
      db.remove_from_items_list('lists', item.list_id, item.item)
      return "OK"
   except Exception as e:
      logging.error(f"Error remove_list_item failed. {e}")
      raise HTTPException(status_code=500, detail="Server error")


@app.post("/api/update_list_item")
async def update_item_in_list(item: EditListItem):
   """
   Update an item within the 'items' list in a specified collection and list.

   Parameters:
   - **item** (EditListItem): Object containing item, list_id, and id.

   Returns:
   - **str**: "OK" if successful.

   Raises:
   - **HTTPException**: If an error occurs during the process.
   """
   try:
      db.update_item_in_list('lists', item.list_id, item.id, {
         "item": item.item,
         "tag": requests.get(f"{model_manager_url}?item={item.item}").json(),
         "id": str(abs(hash(item.item)))})
      return "OK"
   except Exception as e:
      logging.error(f"Error update_list_item failed. {e}")
      raise HTTPException(status_code=500, detail="Server error")


@app.post("/api/load_locations")  # 43.810056,-79.459944
async def load_locations(geo_location: Location):
   """
   Load locations based on the provided geo-location.

   Parameters:
   - **geo_location** Location object containing latitude and longitude.

   Returns:
   - **str**: "OK" if successful.
   """
   url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={geo_location.latitude}%2C{geo_location.longitude}&type=store&key={places_api_key}&rankby=distance"

   response = requests.request("GET", url)

   data = response.json()
   docs = []
   for doc in data["results"]:
      docs.append({
         "types": doc["types"],
         "name": doc["name"],
         "vicinity": doc["vicinity"],
         "placeId": doc["place_id"],
         "location": {
               "type": "Point",
               "coordinates": [
                  doc["geometry"]["location"]["lat"],
                  doc["geometry"]["location"]["lng"]
               ]
         }
      })

   db.insert_many("locations", docs)
   db.get_database()["locations"].create_index([("location", "2dsphere")])

   return "OK"
