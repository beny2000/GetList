import axios from 'axios';
import Constants from "expo-constants";
import { base64Encode } from "./encoder";


class Api {
  static instance = null;

  constructor() {
    if (Api.instance) {
      return Api.instance;
    }

    this.baseURL = 'https://fresh-cow-rightly.ngrok-free.app';
    this.token = null;
    this.clientId = base64Encode(Constants.deviceName);;
    
    Api.instance = this;
  }

  static getInstance() {
    if (!Api.instance) {
      Api.instance = new Api();
    }

    return Api.instance;
  }

  async getToken() {
    try {

      const response = await axios.get(`${this.baseURL}/api/token?client_id=${this.clientId}`);
      this.token = response.data.access_token;
      console.log(`Token: ${this.token}`);
      return this.token;
    } catch (error) {
      console.error('Error fetching token:', error);
      throw error;
    }
  }

  async apiCallWithRetry(config, retryCount = 3) {
    try {
      if (!this.token) {
        this.token = await this.getToken();
      }

      console.log("CI", this.clientId)
      const response = await axios({
        ...config,
        headers: {
          Authorization: `Bearer ${this.token}`,
          ...(config.headers || {}),
        },
        baseURL: this.baseURL,
      });

      return response.data;
    } catch (error) {
      if (error.response && error.response.status === 401 && retryCount > 0) {
        // Token may have expired, refresh and retry
        await this.getToken();
        return this.apiCallWithRetry(config, retryCount - 1);
      }

      console.error('API call failed:', error);
      throw error;
    }
  }

  async geoLocation(body) {
    const config = {
      method: 'post',
      url: '/api/geolocation',
      data: body,
    };

    this.apiCallWithRetry(config);
  }

  async createList() {
    const config = {
      method: 'get',
      url: '/api/create_list',
    };

    this.apiCallWithRetry(config);
  }

  async getList() {
    const config = {
      method: 'get',
      url: '/api/get_list',
    };

    return this.apiCallWithRetry(config);
  }

  async itemsNearby(body) {
    const config = {
      method: 'post',
      url: '/api/items_nearby',
      data: body,
    };

    return this.apiCallWithRetry(config);
  }

  async addListItem(item) {
    const config = {
      method: 'post',
      url: '/api/add_list_item',
      data: item,
    };

    return this.apiCallWithRetry(config);
  }

  async removeListItem(item) {
    const config = {
      method: 'post',
      url: '/api/remove_list_item',
      data: item,
    };

    return this.apiCallWithRetry(config);
  }

  async updateListItem(item) {
    const config = {
      method: 'post',
      url: '/api/update_list_item',
      data: item,
    };

    return this.apiCallWithRetry(config);
  }
}

export const api = new Api();
