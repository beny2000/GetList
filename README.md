# Location List App
The Location List app is a feature-rich shopping list application designed to enhance your shopping experience. Leveraging advanced technologies and a user-friendly interface, the app integrates seamlessly with your daily routine, providing smart reminders and location-based assistance. Download and install the `.apk` file to try the app!

## Features
### List Management
The list_manager server serves as the backbone of the app, offering comprehensive list management functionalities. Users can effortlessly create, edit, and remove items from their shopping lists.

### Nearby Item Notifications
The notification_manager server ensures users are promptly notified when items on their shopping list are detected near their current location. Stay informed about nearby stores that might have what you need.

### Store Type Classification
Powered by the model_manager server, the app employs a machine learning model (BERT) to classify items on your list by their corresponding store types. This enables the app to intelligently suggest relevant nearby stores for your shopping needs.

### Geospatial Search
The MongoDB database, equipped with geospatial search functionality, enhances location-based features. It efficiently handles the geolocation data of stores and items, providing a seamless experience for users.

### React Native Frontend
The frontend, built in React Native, offers a clean and intuitive user interface. Users can conveniently manage their shopping lists and view items that are nearby, making the app a valuable companion during shopping trips.

## Technologies Used
Backend Technologies: Python, FastAPI, Docker

Frontend Technologies: JavaScript, React Native, Expo

API Integration: Google Places API

Machine Learning: BERT (Bidirectional Encoder Representations from Transformers)

Database: MongoDB with Geospatial Search

DevOps: Docker for containerization

## Getting Started
To run the app locally, you'll need to start the backend and frontend respectively
1. Clone the repo ``

### Starting the backend
1. In the `docker-compose.yml` input your `NGROK_AUTHTOKEN` and `--domain` from [ngrok](https://ngrok.com/)
1. Run `docker compose up` to start backend servers, database and ngrok proxy

### Starting the frontend
1. Open another terminal
2. Run `npm install` to install dependencies
3. Run `npm start` to start the expo dev server

### Using the app
After starting the backend and frontend servers you can open the app in the following ways:
- Download the expo app on your android and scan the QR code shown in the terminal to open the app
- In the terminal, press `w` to open the web app
- Start an android emulator, then in the terminal, press `a` to open the app in the emulator
- Connect an android device with USB debugging mode enabled to your machine, then in the terminal, press `a` to open the app on your device# GetList
