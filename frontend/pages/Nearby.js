import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  Pressable,
  Platform,
  FlatList,
  RefreshControl,
  StyleSheet,
} from "react-native";
import axios from "axios";
import * as Location from "expo-location";
import { CheckBox } from "react-native-elements";
import { Dropdown } from "react-native-element-dropdown";
import Ionicons from "@expo/vector-icons/Ionicons";
import theme from "../components/Theme";
import Swipe from "../components/Swipe";
import openInMaps from "../helpers/openInMaps";
import Constants from "expo-constants";
import { base64Encode } from "../helpers/encoder";

const DEV_LIST_ID = base64Encode(Constants.deviceName)

const Nearby = ({ navigation }) => {
  const [location, setLocation] = useState(null);
  const [items, setItems] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  const getNearbyItems = async (location) => {
    try {
      const response = await axios.post(
        `https://www.get-list.com/api/items_nearby`,
        { list_id: DEV_LIST_ID, location: location },
        { headers: { "ngrok-skip-browser-warning": "69420" } }
      );

      // Merge items from API with existing items maintaining there options state
      setItems((prev) =>
        response?.data?.map((ele) => {
          const index = prev?.findIndex((prevEle) => prevEle.id === ele.id);
          return index !== -1
            ? prev[index]
            : { ...ele, options: { isChecked: false } };
        })
      );
    } catch (error) {
      console.error("Error fetching nearby items:", error);
    }
  };

  const getCurrentLocation = async () => {
    let location = null;

    try {
      if (Platform.OS === "web") {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            location = {
              latitude: position.coords.latitude,
              longitude: position.coords.longitude,
            };
            setLocation(location);
          },
          (error) => {
            console.error("Error getting location:", error);
          }
        );
      } else {
        const { status } = await Location.requestForegroundPermissionsAsync();

        if (status !== "granted") {
          console.warn("Permission to access location was denied");
          return;
        }
        location = await Location.getCurrentPositionAsync({});
        setLocation(location.coords);
      }
    } catch (error) {
      console.log("Error getting location:", error);
    }
  };

  const toggleCheckBox = (item) => {
    setItems((prev) =>
      prev.map((ele) =>
        item.id === ele.id
          ? { ...ele, options: { isChecked: !ele.options.isChecked } }
          : ele
      )
    );
  };

  const handleRefresh = () => {
    setRefreshing(true);
    getCurrentLocation();
    setRefreshing(false);
  };

  const renderItem = ({ item }) => (
    <View style={styles.item}>
      <CheckBox
        checked={item.options.isChecked}
        onIconPress={() => toggleCheckBox(item)}
        containerStyle={styles.checkbox}
        uncheckedIcon={
          <Ionicons
            onPress={() => toggleCheckBox(item)}
            name="square-outline"
            size={23}
            color={theme.colors.primary}
          />
        }
        checkedIcon={
          <Ionicons
            onPress={() => toggleCheckBox(item)}
            name="checkbox"
            size={23}
            color={theme.colors.primary}
          />
        }
      />
      <Dropdown
        style={styles.picker}
        placeholder={item.item}
        data={item.stores}
        labelField={"name"}
        valueField={"name"}
        onChange={(i) => {
          openInMaps(i["placeId"]);
        }}
        onChangeText={() => {}}
        searchField={"name"}
        itemTextStyle={{ color: theme.colors.primary }}
        placeholderStyle={{ color: theme.colors.primary, fontWeight: "bold" }}
        selectedTextStyle={{ color: theme.colors.primary }}
        renderItem={(store) => (
          <Pressable
            onPress={() => openInMaps(store.location.coords, store.location.placeId)}
            style={styles.pickerItem}
          >
            <Ionicons name="basket" size={23} color={theme.colors.primary} />
            <Text style={styles.pickerItemText}>{store.name}</Text>
          </Pressable>
        )}
        renderRightIcon={() => (
          <>
            <Ionicons name="chevron-down" size={18} color={theme.colors.primary} />
            <Ionicons name="location-sharp" size={23} color={theme.colors.primary} />
          </>
        )}
      />
    </View>
  );

 
  useEffect(() => {
    getCurrentLocation();
  }, []);

  useEffect(() => {
    const delay = 10000; //10 sec
    const timeoutId = setTimeout(getCurrentLocation, delay);
    return () => clearTimeout(timeoutId);
  });

  useEffect(() => {
    if (location != null) {
      getNearbyItems(location);
    }
  }, [location]);

  const renderNoItem = () => (
    <Text style={styles.noItem}>No items found nearby</Text>
  );

  return (
    <Swipe rightAction={() => navigation.navigate("List")}> 
      <View>
        {items?.length > 0 ? (
          <FlatList
            data={items}
            keyExtractor={(item) => item.id.toString()}
            renderItem={renderItem}
            refreshControl={
              <RefreshControl
                refreshing={refreshing}
                onRefresh={handleRefresh}
                colors={[theme.colors.primary]}
              />
            }
          />
        ) : (
          <FlatList
            data={[{ _: "_" }]}
            keyExtractor={() => Math.random()}
            renderItem={renderNoItem}
            refreshControl={
              <RefreshControl
                refreshing={refreshing}
                onRefresh={handleRefresh}
                colors={[theme.colors.primary]} // Customize the loading indicator color
              />
            }
          />
        )}
      </View>
    </Swipe>
  );
};

const styles = StyleSheet.create({
  item: {
    flexDirection: "row",
    padding: 8,
    marginRight: 20,
  },
  itemText: {
    alignSelf: "center",
    padding: 10,
    paddingLeft: 0,
    width: "30%",
    color: theme.colors.primary,
    fontSize: theme.fonts.size.text,
  },
  noItem: {
    padding: 10,
    paddingBottom: "90%",
    fontSize:  theme.fonts.size.text,
    color: theme.colors.primary,
  },
  picker: {
    width: "90%",
    color: theme.colors.primary,
    borderWidth: 0,
    borderBottomWidth: 1,
    borderColor: theme.colors.primary,
    marginRight: 16,
  },
  pickerItem: {
    flexDirection: "row",
    padding: 10,
  },
  pickerItemText: {
    color: theme.colors.primary,
    fontSize: 16,
    marginLeft: 10,
  },
  checkbox: {
    marginTop: 8,
    padding: 0,
    color: theme.colors.primary,
    backgroundColor: "transparent",
  },
});

export default Nearby;
