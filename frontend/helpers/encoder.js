export const base64Encode = (str) => {
    const base64Chars =
      'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';
  
    let result = '';
    let i = 0;
  
    while (i < str.length) {
      const char1 = str.charCodeAt(i++);
      const char2 = str.charCodeAt(i++);
      const char3 = str.charCodeAt(i++);
  
      const enc1 = char1 >> 2;
      const enc2 = ((char1 & 3) << 4) | (char2 >> 4);
      let some = ((char2 & 15) << 2) | (char3 >> 6);
      let enc5a = char3 & 63;
      
  
      if (isNaN(char2)) {
        some = enc5a = 64;
      } else if (isNaN(char3)) {
        enc5a = 64;
      }
  
      result +=
        base64Chars.charAt(enc1) +
        base64Chars.charAt(enc2) +
        base64Chars.charAt(some) +
        base64Chars.charAt(enc5a);
    }
  
    return result;
  };
  