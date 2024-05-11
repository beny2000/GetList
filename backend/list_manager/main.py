
import os
import logging
import requests
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from lib_db import DatabaseInterface
from .models import GeoLocation, EditListItem, SearchNearby, Location
from datetime import datetime, timedelta
from jose import jwt


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

ALGORITHM = "HS256"

try:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    TOKEN_EXPIRY = int(os.environ.get('TOKEN_EXPIRY_MINUTES'))
    db = DatabaseInterface(os.environ.get('DB_HOST'), os.environ.get('APP_DB'))
    places_api_key = os.environ.get('API_KEY', "")
    model_manager_url = f"{os.environ.get('MODEL_MANAGER_HOST')}/api/tag_item"
    notification_manager_url = f"{os.environ.get('NOTIFICATION_MANAGER_HOST')}/api/search_nearby"
except Exception as ex:
    logging.error(f"Error: Missing environment variable. {ex}")
    raise ex

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_client(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        client_id: str = payload.get("sub")

        if client_id is None:
            raise credentials_exception

    except jwt.JWTError:
        raise credentials_exception
    return client_id


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
print(os.getcwd())
app.mount("/code/app/static", StaticFiles(directory="/code/app/static"), name="/code/app/static")

@app.get("/", include_in_schema=False)
def root():
    with open("/code/app/static/index.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

@app.get("/api/token")
async def generate_token(client_id: str):
    # Generate an access token with expiration
    expires_delta = timedelta(minutes=TOKEN_EXPIRY)
    token_data = {"sub": client_id, "exp": datetime.utcnow() + expires_delta}  # You can customize this based on your needs
    data = token_data.copy()
    access_token = jwt.encode(data, SECRET_KEY, algorithm="HS256")

    return {"access_token": access_token, "expires_in": TOKEN_EXPIRY * 60}

@app.post("/api/geolocation")
async def geo_location(body: GeoLocation, client_id: dict = Depends(get_client)):  # TODO encrpt token
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
            "list_id": client_id,
            "radius": body.radius,
            "token": body.token
         }
      )
   except Exception as e:
      logging.error(f"Error geo_location failed. {e}")
      raise HTTPException(status_code=500, detail="Server error")
   return "OK"

@app.get("/api/create_list")
async def create_list(client_id: dict = Depends(get_client)):
   try:
      list_exists = db.find_one("lists", {"list_id": client_id})
      print(list_exists)
      if not list_exists:
         db.insert_one("lists", {"list_id": client_id, "items": []})

      return "OK"
   except Exception as e:
      logging.error(f"Error get_list failed. {e}")
      raise HTTPException(status_code=500, detail="Server error")


@app.get("/api/get_list")
async def get_list(client_id: dict = Depends(get_client)):
   """
   Retrieve a list based on the provided list_id.

   Parameters:
   - **list_id** (str): The ID of the list.

   Returns:
   - A list of documents with '_id' replaced by 'id', or raises a server error if unsuccessful.
   """

   try:
      return db.find_all("lists", {"list_id": client_id})
   except Exception as e:
      logging.error(f"Error get_list failed. {e}")
      raise HTTPException(status_code=500, detail="Server error")


@app.post("/api/items_nearby")
async def items_nearby(body: SearchNearby, client_id: dict = Depends(get_client)):
   """
   Find nearby items and locations by type given a point and list ID.

   Parameters:
   - **body** (SearchNearby): Object containing location, list_id, and radius.

   Returns:
   - A list of combined items and locations, or raises a server error if unsuccessful.
   """
   try:
      d = db.find_nearby_items(client_id, float(body.location.latitude), float(body.location.longitude), body.radius)
      print("LL", d)
      return d
   except Exception as e:
      logging.error(f"Error items_nearby failed. {e}")
      raise HTTPException(status_code=500, detail="Server error")


@app.post("/api/add_list_item")
async def add_list_item(item: EditListItem, client_id: dict = Depends(get_client) ):
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

      db.push_to_items_list('lists', client_id, {
         "item": item.item,
         "tag": tag,
         "id": str(abs(hash(item.item)))})
      return "OK"
   except Exception as e:
      logging.error(f"Error add_list_item failed. {e}")
      raise HTTPException(status_code=500, detail="Server error")


@app.post("/api/remove_list_item")
async def remove_from_items_list(item: EditListItem, client_id: dict = Depends(get_client)):
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
      db.remove_from_items_list('lists', client_id, item.item)
      return "OK"
   except Exception as e:
      logging.error(f"Error remove_list_item failed. {e}")
      raise HTTPException(status_code=500, detail="Server error")


@app.post("/api/update_list_item")
async def update_item_in_list(item: EditListItem, client_id: dict = Depends(get_client)):
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
      db.update_item_in_list('lists', client_id, item.id, {
         "item": item.item,
         "tag": requests.get(f"{model_manager_url}?item={item.item}").json(),
         "id": str(abs(hash(item.item)))})
      return "OK"
   except Exception as e:
      logging.error(f"Error update_list_item failed. {e}")
      raise HTTPException(status_code=500, detail="Server error")


@app.post("/api/load_locations")  # 43.810056,-79.459944
async def load_locations(geo_location: Location, client_id: dict = Depends(get_client)):
   """
   Load locations based on the provided geo-location.

   Parameters:
   - **geo_location** Location object containing latitude and longitude.

   Returns:
   - **str**: "OK" if successful.
   """
   try:
      db.load_locations(geo_location.latitude, geo_location.longitude)
      return "OK"
   except Exception as e:
      logging.error(f"Error load_locations failed. {e}")
      raise HTTPException(status_code=500, detail="Server error")

   
