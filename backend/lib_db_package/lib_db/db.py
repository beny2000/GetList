import logging
import pymongo
import requests
import os

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

places_api_key = os.environ.get('API_KEY', "")



class DatabaseInterface:
    """ Interface for MongoDB database for Location List application servers """

    # "mongodb://172.17.0.1:27017/", "appDb"
    def __init__(self, connection_string, database_name):
        self.client = pymongo.MongoClient(connection_string)
        self.database = self.client[database_name]

    def get_database(self):
        """
        Returns the client for the given database.
        :return: The database client
        """
        return self.database

    def get_client(self):
        """
        Returns the client for the given mongo database.
        :return: The client
        """
        return self.client

    # Generic DB methods

    def find_one(self, collection_name: str, filter_criteria: dict):
        """
        Find a single document in the specified collection based on the provided filter criteria.

        :param collection_name: The name of the MongoDB collection.
        :param filter_criteria: A dictionary specifying the filter criteria.
        :return: The found document with '_id' replaced by 'id', or None if an error occurs.
        """
        try:
            collection = self.database[collection_name]
            document = collection.find_one(filter_criteria)

            if document:
                document["id"] = str(document["_id"])
                del document["_id"]

            return document
        except Exception as e:
            logging.error(f"Error find failed. {e}")
            return None

    def find_all(self, collection_name: str, filter_criteria: dict = None):
        """
        Find all documents in the specified collection based on optional filter criteria.

        :param collection_name: The name of the MongoDB collection.
        :param filter_criteria: (Optional) A dictionary specifying the filter criteria.
        :return: A list of documents with '_id' replaced by 'id', or None if an error occurs.
        """
        try:
            collection = self.database[collection_name]
            docs = list(collection.find(filter_criteria)
                        ) if filter_criteria else list(collection.find())
            for doc in docs:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
            return docs
        except Exception as e:
            logging.error(f"Error find_all failed. {e}")
            return None

    def insert_one(self, collection_name: str, document: dict):
        """
        Insert a single document into the specified collection.

        :param collection_name: The name of the MongoDB collection.
        :param document: The document to be inserted.
        :return: The inserted document ID, or None if an error occurs.
        """
        try:
            collection = self.database[collection_name]
            result = collection.insert_one(document)
            return result.inserted_id
        except Exception as e:
            logging.error(f"Error insert_one failed. {e}")
            return None

    def insert_many(self, collection_name: str, documents: dict):
        """
        Insert multiple documents into the specified collection.

        :param collection_name: The name of the MongoDB collection.
        :param documents: A list of documents to be inserted.
        :return: A list of inserted document IDs, or None if an error occurs.
        """
        try:
            collection = self.database[collection_name]
            result = collection.insert_many(documents)
            return result.inserted_ids
        except Exception as e:
            logging.error(f"Error insert many failed. {e}")
            return None

    def update_one(self, collection_name: str, filter_criteria: dict, update: dict):
        """
        Update a single document in the specified collection based on the provided filter criteria.

        :param collection_name: The name of the MongoDB collection.
        :param filter_criteria: A dictionary specifying the filter criteria.
        :param update: A dictionary specifying the update operation.
        :return: The number of modified documents, or None if an error occurs.
        """
        try:
            collection = self.database[collection_name]
            result = collection.update_one(filter_criteria, update)
            return result.modified_count
        except Exception as e:
            logging.error(f"Error update_one failed. {e}")
            return None

    def upsert_one(self, collection_name: str, filter_criteria: dict, update: dict):
        """
        Update or insert a single document in the specified collection based on the provided filter criteria.

        :param collection_name: The name of the MongoDB collection.
        :param filter_criteria: A dictionary specifying the filter criteria.
        :param update: A dictionary specifying the update operation.
        :return: The upserted document ID, or None if an error occurs.
        """
        try:
            collection = self.database[collection_name]
            result = collection.update_one(
                filter_criteria, {"$set": update}, upsert=True)
            return result.upserted_id
        except Exception as e:
            logging.error(f"Error upsert_one failed. {e}")
            return None

    def delete_one(self, collection_name: str, filter_criteria: dict):
        """
        Delete a single document from the specified collection based on the provided filter criteria.

        :param collection_name: The name of the MongoDB collection.
        :param filter_criteria: A dictionary specifying the filter criteria.
        :return: The number of deleted documents, or None if an error occurs.
        """
        try:
            collection = self.database[collection_name]
            result = collection.delete_one(filter_criteria)
            return result.deleted_count
        except Exception as e:
            logging.error(f"Error delete_one failed. {e}")
            return None

    # Specific DB methods

    def push_to_items_list(self, collection_name: str, list_id: str, item: dict):
        """
        Add an item to the 'items' list within a specified collection and list.

        :param collection_name: The name of the MongoDB collection.
        :param list_id: The ID of the list.
        :param item: The item to be added to the 'items' list.
        :return: The number of modified documents, or None if an error occurs.
        """
        try:
            collection = self.database[collection_name]
            update_operation = {"$push": {"items": item}}
            result = collection.update_one(
                {'list_id': list_id}, update_operation)
            return result.modified_count
        except Exception as e:
            logging.error(f"Error push_to_items_list failed. {e}")
            return None

    def remove_from_items_list(self, collection_name: str, list_id: str, criteria: str):
        """
        Remove items from the 'items' list within a specified collection and list based on a given criteria.

        :param collection_name: The name of the MongoDB collection.
        :param list_id: The ID of the list.
        :param criteria: The criteria for removing items (e.g., item name).
        :return: The number of modified documents, or None if an error occurs.
        """
        try:
            collection = self.database[collection_name]
            update_operation = {"$pull": {"items": {"item": criteria}}}
            result = collection.update_one(
                {'list_id': list_id}, update_operation)
            return result.modified_count
        except Exception as e:
            logging.error(f"Error remove_to_items_list failed. {e}")
            return None

    def update_item_in_list(self, collection_name: str, list_id: str, item_id: str, new_item: dict):
        """
        Update an item within the 'items' list in a specified collection and list.

        :param collection_name: The name of the MongoDB collection.
        :param list_id: The ID of the list.
        :param item_id: The ID of the item to be updated.
        :param new_item: The new values for the item.
        :return: The number of modified documents, or None if an error occurs.
        """
        try:
            collection = self.database[collection_name]
            filter_criteria = {**{'list_id': list_id}, "items.id": item_id}
            update_operation = {
                "$set": {f"items.$.{key}": value for key, value in new_item.items()}}
            result = collection.update_one(filter_criteria, update_operation)
            return result.modified_count
        except Exception as e:
            logging.error(f"Error update_item_in_list failed. {e}")
            return None

    def find_nearby_locations(self, collection_name: str, reference_location, radius: int):
        """
        Find nearby locations in a specified collection based on a reference location and radius.

        :param collection_name: The name of the MongoDB collection.
        :param reference_location: The reference location coordinates [latitude, longitude].
        :param radius: The radius (in meters) for finding nearby locations.
        :return: A list of nearby locations with '_id' replaced by 'id', or None if an error occurs.
        """
        try:
            collection = self.database[collection_name]

            query = {
                "location": {
                    "$near": {
                        "$geometry": {
                            "type": 'Point',
                            "coordinates": reference_location
                        },
                        "$maxDistance": radius
                    }
                }
            }

            docs = list(collection.find(query))

            if len(docs) == 0:
                logging.info("Found no nearby locations, checking if new locations should be loaded")
                query["location"]["$near"]["$maxDistance"] = 3000
                locs = list(collection.find(query))

                if len(locs) == 0:
                    logging.info("Loading new locations from Places API")
                    self.load_locations(reference_location[0], reference_location[1])
                    docs = list(collection.find(query))

            for doc in docs:
                doc["id"] = str(doc["_id"])
                del doc["_id"]

            return docs
        except Exception as e:
            logging.error(f"Error find_nearby_locations failed. {e}")
            return None

    def find_nearby_items(self, list_id: str, latitude: float, longitude: float, radius: int = 1000):
        """
        Find nearby items and locations by type given a point and list ID.

        :param list_id: The ID of the list.
        :param latitude: The latitude of the reference location.
        :param longitude: The longitude of the reference location.
        :param radius: The radius (in meters) for finding nearby locations. Default is 1000 meters.
        :return: A list of combined items and locations.
        """
        try:
            locations = self.find_nearby_locations(
                "locations",
                [latitude, longitude],
                radius)

            user_list = self.find_one("lists", {"list_id": list_id})
            items_found = []

            for item in user_list["items"]:
                for location in locations:
                    if location["types"][0] in item["tag"]:
                        items_found.append(
                            {"item": item["item"], "store": location["name"],
                                "id": item["id"], "location": {
                                    "address": location["vicinity"],
                                    "placeId": location["placeId"],
                                    "coords": location["location"]["coordinates"],
                                    }}
                        )

            combined_items = {}
            for item in items_found:
                item_name = item["item"]
                item_id = item["id"]
                store = item["store"]
                location = item["location"]

                if item_name not in combined_items:
                    combined_items[item_name] = {"item": item_name, "id": item_id, "stores": [
                        {"name": store, "location": location}]}
                else:
                    combined_items[item_name]["stores"].append(
                        {"name": store, "location": location})

            return list(combined_items.values())
        except Exception as e:
            logging.error(f"Error find_nearby_items failed. {e}")
            return None

    
    def load_locations(self, latitude: str, longitude: str):
        """
        Load locations based on the provided geo-location.

        Parameters:
        - **geo_location** Location object containing latitude and longitude.

        Returns:
        - **str**: "OK" if successful.
        """
        try:
            url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude}%2C{longitude}&type=store&radius=50000&key={places_api_key}"

            response = requests.request("GET", url)
            store_types = [
                "atm",
                "bakery",
                "bank",
                "bar",
                "beauty_salon",
                "bicycle_store",
                "book_store",
                "cafe",
                "car_rental",
                "car_repair",
                "car_wash",
                "clothing_store",
                "convenience_store",
                "department_store",
                "drugstore",
                "electronics_store",
                "florist",
                "furniture_store",
                "gas_station",
                "hair_care",
                "hardware_store",
                "home_goods_store",
                "jewelry_store",
                "liquor_store",
                "pet_store",
                "pharmacy",
                "shoe_store",
                "shopping_mall",
                "store",
                "grocery_or_supermarket"
            ]
            data = response.json()
            docs = []

            for doc in data["results"]:
                if any(value in store_types for value in doc["types"]):
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

            logging.info(f"Found {len(data['results'])} inserted {len(docs)}")

            if len(docs) > 0:
                self.insert_many("locations", docs)
                self.database["locations"].create_index([("location", "2dsphere")])
            return len(docs)
        
        except Exception as e:
            logging.error(f"Error load_locations failed. {e}")
            return None