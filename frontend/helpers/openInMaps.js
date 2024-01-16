import { Linking } from 'react-native';

const openInMaps = (coords, placeId) => {
  const mapUrl = `https://www.google.com/maps/search/?api=1&query=${coords[0]},${coords[1]}&query_place_id=${placeId}`;

  Linking.openURL(mapUrl).catch((err) =>
    console.error('Error opening in Google Maps:', err)
  );
};

export default openInMaps;
