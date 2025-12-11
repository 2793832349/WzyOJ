×import axios from 'axios';
import router from '@/router';
import store from '@/store';

export const Axios = axios.create({
  baseURL: '/api',
});

// Debug: Log the baseURL
console.log('Axios instance created with baseURL:', Axios.defaults.baseURL);

// Add request interceptor to log all requests and fix URL
Axios.interceptors.request.use(
  config => {
    console.log('Axios request interceptor BEFORE:', {
      method: config.method,
      url: config.url,
      baseURL: config.baseURL,
    });
    
    // If URL doesn't start with /, manually prepend baseURL
    if (config.url && !config.url.startsWith('/') && !config.url.startsWith('http')) {
      config.url = config.baseURL + '/' + config.url;
      config.baseURL = undefined; // Clear baseURL to prevent double prepending
      console.log('Axios request interceptor AFTER fix:', {
        url: config.url,
        baseURL: config.baseURL,
      });
    }
    
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

Axios.defaults.transformResponse = [
  (data, headers) => {
    if (
      typeof data === 'string' &&
      headers['content-type'] === 'application/json'
    ) {
      try {
        data = JSON.parse(data);
      } catch (e) {}
    }
    return data;
  },
];

Axios.interceptors.response.use(
  response => {
    return response.data;
  },
  async error => {
    if (!error.response) {
      window.$message.error(error.message);
      return Promise.reject(error.message);
    } else if (error.response.status === 405) {
      window.$message.info(
        'æ­å–œä½ æ‰¾åˆ°äº†å¼€å‘è€…å†™çš„ä¸€ä¸ªè„‘æ®‹Bugï¼ˆè®¤çœŸçš„ï¼‰ï¼Œè¯·è”ç³»å¼€å‘è€…ï¼Œè°¢è°¢ï¼'
      );
      return Promise.reject(error.response);
    } else if (error.response.status === 403) {
      if (!store.getters.loggedIn) {
        if (!['login', 'register'].includes(router.currentRoute.value.name)) {
          window.$message.warning('è¯·å…ˆç™»å½•');
          store.commit('logout');
          router.push({
            name: 'login',
            query: { next: router.options.history.location },
          });
        } else {
          return Promise.reject(error.response);
        }
      }
      if (error.response.data.message) {
        window.$message.error(error.response.data.message);
        return Promise.reject(error.response.data.message);
      }
      window.$message.error('èº«ä»½æ ¡éªŒå¤±è´¥');
      return Promise.reject('èº«ä»½æ ¡éªŒå¤±è´¥');
    } else if (error.response.status === 404) {
      return Promise.reject(error.response);
    }

    const reason =
      error.response.data.message ??
      error.response.data.detail ??
      error.response.data[0];
    if (error.response.status === 400) {
      if (reason) window.$message.error(reason);
      return Promise.reject(reason);
    } else if (error.response.status === 500) {
      window.$message.error('æœåŠ¡å™¨é”™è¯¯');
      return Promise.reject('æœåŠ¡å™¨é”™è¯¯');
    } else {
      return Promise.reject(reason);
    }
  }
);

export default Axios;
ü *cascade08üª *cascade08ª¶*cascade08¶ *cascade08–*cascade08–ó *cascade08ó÷*cascade08÷ù *cascade08ù„*cascade08„… *cascade08…†*cascade08†Š *cascade08Š‹*cascade08‹Œ *cascade08Œ*cascade08 *cascade08™*cascade08™š *cascade08š±*cascade08±¸ *cascade08¸¼*cascade08¼½ *cascade08½¿*cascade08¿Ë *cascade08ËÚ*cascade08Úë *cascade08ëí*cascade08íî *cascade08î…*cascade08…† *cascade08†Š*cascade08Š‹ *cascade08‹*cascade08 *cascade08³*cascade08³Ä *cascade08ÄÅ*cascade08ÅÆ *cascade08Æ*cascade08• *cascade08• *cascade08 ğ *cascade08ğ× *cascade08"(205b1bab434999c48e066e66385ba65f03f104f420file:///root/frontend-naive/src/plugins/axios.js:file:///root/frontend-naive