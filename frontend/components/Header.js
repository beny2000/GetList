import React from "react";
import theme from "./Theme";
import { Image, StyleSheet, View, Text } from "react-native";

const Header = () => {
    return (<View style={{flexDirection: "row", display: "flex",}}>
        <Image style={{width: 50, height: 50}}source={require("../assets/icon_white.png")}/>
        <Text style={{fontSize: 26, color: "white", paddingLeft: 10, alignSelf: "center"}}>GetList</Text>
    </View>)
}

export default Header;