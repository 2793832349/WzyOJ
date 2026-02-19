<script setup>
import AppHeader from './AppHeader.vue';
import NaiveMessage from './components/naiveMessage.vue';
import { config, setSiteSettings } from './config';
import { darkTheme, zhCN, dateZhCN } from 'naive-ui';
import store from './store';
import hljs from 'highlight.js/lib/core';
import c from 'highlight.js/lib/languages/c';
import cpp from 'highlight.js/lib/languages/cpp';
import python from 'highlight.js/lib/languages/python';
import Axios from '@/plugins/axios';

hljs.registerLanguage('c', c);
hljs.registerLanguage('cpp', cpp);
hljs.registerLanguage('python', python);
hljs.registerLanguage('python3', python);

Axios.get('/site_settings/').then(res => {
  setSiteSettings(res);
  store.commit('updateDisplaySettings', res.displaySettings);
});

Axios.get('/user/info/').then(res => {
  if (res.id) store.commit('setUser', res);
  else store.commit('logout');
});
</script>

<template>
  <n-config-provider
    :locale="zhCN"
    :date-locale="dateZhCN"
    :theme="store.getters.theme === 'dark' ? darkTheme : null"
    :hljs="hljs"
  >
    <n-global-style />

    <n-message-provider>
      <NaiveMessage />
      <n-notification-provider>
        <n-dialog-provider>
          <n-layout class="app-shell">
            <n-layout-header bordered class="app-header">
              <AppHeader />
            </n-layout-header>

            <n-layout-content class="app-content">
              <div class="app-content-inner">
                <RouterView />
              </div>
            </n-layout-content>

            <n-layout-footer class="app-footer" v-if="config.footer.useFooter">
              {{ config.name }} Powered By
              <n-button text>Wangzyy</n-button>
              <span>&nbsp;</span>
              <a
                href="https://beian.miit.gov.cn/"
                target="_blank"
                style="text-decoration: none"
                v-if="config.footer.icp"
              >
                <n-button text>
                  {{ config.footer.icp }}
                </n-button>
              </a>
            </n-layout-footer>
          </n-layout>
        </n-dialog-provider>
      </n-notification-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: transparent;
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 120;
  padding: 10px 16px;
  backdrop-filter: blur(16px);
  background: rgba(255, 255, 255, 0.75);
  border-bottom: 1px solid #dbe5f0;
}

.app-content {
  padding: 24px 0 8px;
}

.app-content-inner {
  width: min(1440px, 94vw);
  margin: 0 auto;
}

.app-footer {
  margin-top: 24px;
  text-align: center;
  padding: 14px 10px 20px;
  color: #64748b;
}

@media (max-width: 768px) {
  .app-header {
    padding: 8px 10px;
  }

  .app-content {
    padding-top: 14px;
  }

  .app-content-inner {
    width: 96vw;
  }
}
</style>
