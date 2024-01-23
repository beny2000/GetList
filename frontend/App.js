import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import ItemList from "./pages/List";
import Nearby from "./pages/Nearby";
import * as Notifications from "expo-notifications";
import * as Location from "expo-location";
import { Platform, StyleSheet, Button, Text } from "react-native";
import axios from "axios";
import Ionicons from "@expo/vector-icons/Ionicons";
import * as TaskManager from "expo-task-manager";
import theme from "./components/Theme";
import Header from "./components/Header";
import Constants from "expo-constants";
import { base64Encode } from "./helpers/encoder";


const DEV_LIST_ID = base64Encode(Constants.deviceName);
const LOCATION_TASK_NAME = "background-location-task";
const Tab = createBottomTabNavigator();

console.log("Device list id:", DEV_LIST_ID)

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: false,
    shouldSetBadge: false,
  }),
});


TaskManager.defineTask(LOCATION_TASK_NAME, async ({ data, error }) => {
  console.log("background", data, error);
  if (error) {
    // Error occurred - check `error.message` for more details.
    console.log(error);
    return;
  }
  if (data) {
    const { locations } = data;
    console.log("BACK", locations[0].coords.longitude);
    token = await Notifications.getExpoPushTokenAsync({
      projectId: Constants.expoConfig.extra.eas.projectId,
    });

    await axios.post(
      `https://www.get-list.com/api/geolocation`,
      {
        location: {
          latitude: locations[0].coords.latitude.toString(),
          longitude: locations[0].coords.longitude.toString(),
        },
        radius: 200,
        token: token.data,
        list_id: DEV_LIST_ID,
      }, { headers: { "ngrok-skip-browser-warning": "69420" } }
    );
  }
});


const requestPermissions = async () => {
  console.log("kk")
  const { status: foregroundStatus } = await Location.requestForegroundPermissionsAsync();
  console.log("FORE", foregroundStatus)
  if (foregroundStatus === 'granted') {
    const { status: backgroundStatus } = await Location.requestBackgroundPermissionsAsync();
    console.log("BACK", backgroundStatus)
    if (backgroundStatus === 'granted') {
      await Location.startLocationUpdatesAsync(LOCATION_TASK_NAME, {
        accuracy: Location.Accuracy.Balanced,
      });
    }
  }
};

async function registerForPushNotificationsAsync() {
  let token;

  if (Platform.OS === "android") {
    Notifications.setNotificationChannelAsync("default", {
      name: "default",
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: "#FF231F7C",
    });
  }

  if (Platform.OS !== "web") {
    const { status: existingStatus } =
      await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;

    if (existingStatus !== "granted") {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }
    if (finalStatus !== "granted") {
      alert("Failed to get push token for push notification!");
      return;
    }
    token = await Notifications.getExpoPushTokenAsync({
      projectId: Constants.expoConfig.extra.eas.projectId,
    });
    console.log("TOKEN", token.data);
  }

  return token.data;
}

const App = () => {
  const [expoPushToken, setExpoPushToken] = React.useState("");
  const [notification, setNotification] = React.useState(false);
  const notificationListener = React.useRef();
  const responseListener = React.useRef();
  const [initScreen, setInitScreen] = React.useState("List");

  React.useEffect(() => {
    const createList = async () => {
      await axios.get(
        `https://www.get-list.com/api/create_list?list_id=${DEV_LIST_ID}`,
        { headers: { "ngrok-skip-browser-warning": "69420" } }
      );
    }
    createList();
  }, []);

  React.useEffect(() => {

    requestPermissions().catch(e => {console.log("ERROR: " + e)});

    registerForPushNotificationsAsync().then((token) =>
      setExpoPushToken(token)
    );

    notificationListener.current =
      Notifications.addNotificationReceivedListener((notification) => {
        setNotification(notification);
      });

    responseListener.current =
      Notifications.addNotificationResponseReceivedListener((response) => {
        console.log(response);
        setInitScreen("Nearby")
      });

    return () => {
      Notifications.removeNotificationSubscription(
        notificationListener.current
      );
      Notifications.removeNotificationSubscription(responseListener.current);
    };
  }, []);
  
  console.log('gg', notification, initScreen);
  return (
    <NavigationContainer screenOptions={{tabBarStyle: styles.navbar}}>
      <Tab.Navigator screenOptions={{tabBarActiveTintColor: theme.colors.primary, headerStyle: {backgroundColor: theme.colors.primary}, headerTitle: Header}} initialRouteName={initScreen}>
        <Tab.Screen
          name="List"
          options={{
            tabBarIcon: ({ focused }) =>
              focused ? (
                <Ionicons 
                  name="list-circle-sharp" 
                  size={32} 
                  color={theme.colors.primary} 
                />
              ) : (
                <Ionicons
                  name="list-circle-outline"
                  size={32}
                  color={theme.colors.primary}
                />
              ),
          }}
          component={ItemList}
        />
        <Tab.Screen
          name="Nearby"
          component={Nearby}
          options={{
            tabBarIcon: ({ focused }) =>
              focused ? (
                <Ionicons name="location-sharp" size={32} color={theme.colors.primary} />
              ) : (
                <Ionicons name="location-outline" size={32} color={theme.colors.primary} />
              ),
          }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
};

const styles = StyleSheet.create({
  navbar: {
    padding: 10,
  },
});

export default App;
