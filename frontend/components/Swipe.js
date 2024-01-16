import React from "react";
import {
  View,
  PanResponder,
} from "react-native";


const Swipe = ({children, leftAction, rightAction}) => {
    const panResponder = React.useRef(
      PanResponder.create({
        onStartShouldSetPanResponder: () => true,
        onPanResponderMove: (event, gestureState) => {
          if (gestureState.dx > 50 && rightAction) {
            rightAction();
          } else if (gestureState.dx < -50 && leftAction){
            leftAction();
          }
        },
        onPanResponderRelease: () => {
          // Reset any necessary state
        },
      })
    ).current;
  
    return (
      <View style={{ flex: 1 }} {...panResponder.panHandlers}>
        {children}
      </View>
    );
  };

export default Swipe;