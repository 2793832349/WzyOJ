�import axios from 'axios';
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
        '恭喜你找到了开发者写的一个脑残Bug（认真的），请联系开发者，谢谢！'
      );
      return Promise.reject(error.response);
    } else if (error.response.status === 403) {
      if (!store.getters.loggedIn) {
        if (!['login', 'register'].includes(router.currentRoute.value.name)) {
          window.$message.warning('请先登录');
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
      window.$message.error('身份校验失败');
      return Promise.reject('身份校验失败');
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
      window.$message.error('服务器错误');
      return Promise.reject('服务器错误');
    } else {
      return Promise.reject(reason);
    }
  }
);

export default Axios;
�"(6b457f522aa10499b55789fae01ec35627afe7b620file:///root/frontend-naive/src/plugins/axios.js:file:///root/frontend-naive