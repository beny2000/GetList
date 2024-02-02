import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  Pressable,
  FlatList,
  TextInput,
  RefreshControl,
  StyleSheet,
} from "react-native";
import axios from "axios";
import Ionicons from "@expo/vector-icons/Ionicons";
import theme from "../components/Theme";
import Swipe from "../components/Swipe";
import Constants from "expo-constants";
import { base64Encode } from "../helpers/encoder";
import { api } from "../helpers/api";

const DEV_LIST_ID = base64Encode(Constants.deviceName);

const ItemList = ({ navigation }) => {
  const [items, setItems] = useState([]);
  const [newItem, setNewItem] = useState("");
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async (id) => {
    try {
      const response = await api.getList();

      const items = response[0].items.map((item) => ({
        id: item.id,
        item: item.item,
      }));
      setItems(items);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const removeItem = async (item) => {
    try {
      api.removeListItem(
        { item: item.item },
      );

      setItems((prevItems) =>
        prevItems.filter((ele) => ele.item !== item.item)
      );

      fetchData();
    } catch (error) {
      console.error("Error deleting Item:", error);
    }
  };

  const addItem = async () => {
    if (!newItem == "") {
      try {
        api.addListItem(
          { item: newItem },
        );
        setItems((prev) => [
          ...prev,
          {
            item: newItem,
            id: base64Encode(newItem)
          },
        ]);
        fetchData();
        setNewItem("");
      } catch (error) {
        console.error("Error adding Item:", error);
      }
    }
  };

  const updateItem = async (item) => {
    if (!item.item == "") {
      try {
        api.updateListItem(
          { item: item.item, id: item.id },
        );
        fetchData();
      } catch (error) {
        console.error("Error updating Item:", error);
      }
    }
  };

  const handleNewItemTextChange = (inputText) => {
    setNewItem(inputText);
  };

  const handleItemTextChange = (newItem, id) => {
    setItems((prev) =>
      prev.map((ele) => (ele.id === id ? { ...ele, item: text } : ele))
    );
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchData();
    setRefreshing(false);
  };

  const renderItem = ({ item }) => (
    <View style={styles.itemView}>
      <View style={styles.itemDiv}>
        <TextInput
          onBlur={() => updateItem(item)}
          onSubmitEditing={() => updateItem(item)}
          onChangeText={(text) => handleItemTextChange(text, item.id)}
          value={item.item}
          style={styles.item}
        />
      </View>

      <Pressable
        style={{ alignSelf: "center" }}
        onPress={() => removeItem(item)}
      >
        <Ionicons name="trash-outline" size={23} color={theme.colors.primary} />
      </Pressable>
    </View>
  );


  useEffect(() => {
    fetchData();
  }, []);

  return (
    <Swipe leftAction={() => navigation.navigate("Nearby")}>
      <View style={{ marginLeft: 16 }}>
        <View style={styles.inputDiv}>
          <TextInput
            //style={{ height: 40, borderColor: 'gray', borderWidth: 1, marginBottom: 10, padding: 10 }}
            style={styles.input}
            placeholder="Add Item"
            onChangeText={handleNewItemTextChange}
            value={newItem}
            onSubmitEditing={addItem}
          />
          <Pressable
            style={styles.addBtn}
            color={theme.colors.primary}
            onPress={addItem}
          >
            <Ionicons name="add-outline" size={32} color="#fff" />
          </Pressable>
        </View>
        <FlatList
          keyboardDismissMode="on-drag"
          data={items}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderItem}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={handleRefresh}
              colors={["#4285F4"]}
            />
          }
        />
      </View>
    </Swipe>
  );
};

const styles = StyleSheet.create({
  input: {
    height: "61%",
    borderColor: theme.colors.primary,
    borderWidth: 1,
    marginBottom: 10,
    marginTop: 10,
    padding: 10,
    color: theme.colors.primary,
    borderRadius: 5,
    backgroundColor: "rgba(132, 96, 126, 0.1)",
    width: "84%",
  },
  item: {
    fontSize: theme.fonts.size.text,
    color: theme.colors.primary,
    height: 40,
    marginRight: 16,
    width: "74%",
  },
  itemView: {
    marginRight: 11,
    flexDirection: "row",
    justifyContent: "left",
    padding: 5,
    display: "flex",
    justifyContent: "space-between",
  },
  itemUnderline: {
    borderBottomWidth: 1,
    borderBottomColor: "black",
  },
  inputDiv: {
    display: "flex",
    flexDirection: "row",
    justifyContent: "space-between",
  },
  addBtn: {
    padding: 3,
    marginRight: 8,
    paddingTop: 4,
    borderRadius: 5,
    height: "60%",
    backgroundColor: theme.colors.primary,
    marginTop: 10,
  },
  strikethrough: {
    textDecorationLine: "line-through",
  },
  itemDiv: {
    display: "inline-block",
    display: "flex",
    flexDirection: "row",
    justifyContent: "space-between",
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.primary,
    width: "87%",
  },
});

export default ItemList;
