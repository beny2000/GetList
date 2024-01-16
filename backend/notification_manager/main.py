
import os
import requests
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from lib_db import DatabaseInterface
from requests.exceptions import ConnectionError, HTTPError
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
from .models import SearchNearby


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

try:
    db = DatabaseInterface(os.environ.get('DB_HOST'), os.environ.get('APP_DB'))  
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

def send_push_message(token, message, extra=None):
    """
    Sends a push notification to the specified device token with the provided message and optional extra data.

    Parameters:
    - token (str): The device token to which the push notification will be sent.
    - message (str): The message content of the push notification.
    - extra (dict, optional): Additional data to include in the push notification. Defaults to None.

    Raises:
    - Exception: If there is an error during the process of publishing or validating the push notification.
    ```

    """
    try:
        response = PushClient().publish(
            PushMessage(to=token,
                        body=message,
                        data=extra))
    except Exception as ex:
       logging.error(f"Error: Failed to publish push notification. {ex}")
       raise ex

    try:
        # We got a response back, but we don't know whether it's an error yet.
        # This call raises errors so we can handle them with normal exception
        # flows.
        response.validate_response()
    except DeviceNotRegisteredError:
        # Mark the push token as inactive
        #from notifications.models import PushToken
       # PushToken.objects.filter(token=token).update(active=False)
       pass
    except Exception as exc:
        # Encountered some other per-notification error.
        logging.error(f"Error: Failed to validate push notification. {e}")
        raise exc
       


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url='/docs')

@app.get("/api/send_push")
async def send_push(token: str):
    """
    Send push notification.

    Parameters:
    - **token** (str): The user's device token.

    Returns:
    - **str**: "OK" if successful.

    Raises:
    - **HTTPException**: If an error occurs during the process.
    """
    try:
        send_push_message(token, "hello")
        return "OK"
    except Exception as e:
        logging.error(f"Error: Failed to send notification. {e}")
        raise HTTPException(status_code=500, detail="Server error")

@app.post("/api/search_nearby")
async def search_nearby(body: SearchNearby):
    """
    Search for nearby items.

    Parameters:
    - **body** (SearchNearby): Object containing location, list_id, and radius.

    Returns:
    - A list of combined items and locations.

    Raises:
    - **HTTPException**: If an error occurs during the process.
    """
    try:
        print(body)
        items = db.find_nearby_items(body.list_id, float(body.location.latitude), float(body.location.longitude), body.radius)
        print(items)
        if items and len(items) == 1 and len(items[0]["stores"]) == 1:
            send_push_message(body.token, f'{items[0]["item"]} was found at {items[0]["stores"][0]["name"]} near you')
            return "OK"
        
        if items and len(items) == 1 and len(items[0]["stores"]) > 1:
            send_push_message(body.token, f'{items[0]["item"]} was found at {len(items[0]["stores"])} stores near you')
            return "OK"
        

        if items and len(items) > 1:
            send_push_message(body.token, f'{len(items)} items found near you')
            return "OK"

    except Exception as e:
        logging.error(f"Error: Failed to find nearby items. {e}")
        raise HTTPException(status_code=500, detail="Server error")

   