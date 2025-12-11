�,<script setup>
import { h } from 'vue';
import store from './store';
import router from './router';
import { useRoute } from 'vue-router';
import Axios from '@/plugins/axios';
import { NIcon } from 'naive-ui';
import {
  UserOutlined,
  UserAddOutlined,
  HomeOutlined,
  HourglassOutlined,
  ControlOutlined,
  CommentOutlined,
  TeamOutlined,
} from '@vicons/antd';
import {
  LogOutOutline,
  SettingsOutline,
  LogInOutline,
  BookOutline,
  TrophyOutline,
  PeopleOutline,
  SunnyOutline,
  MoonOutline,
  ListOutline,
} from '@vicons/ionicons5';
import config from './config';

const route = useRoute();

const renderIcon = icon => {
  return () =>
    h(NIcon, null, {
      default: () => h(icon),
    });
};

const userOptions = [
  {
    label: '个人主页',
    key: 'user_detail',
    icon: renderIcon(UserOutlined),
  },
  {
    label: '个人设置',
    key: 'user_settings',
    icon: renderIcon(SettingsOutline),
  },
  {
    label: '退出登录',
    key: 'logout',
    icon: renderIcon(LogOutOutline),
  },
];
if (store.state.user.permissions.includes('site_setting')) {
  userOptions.splice(2, 0, {
    label: '站点设置',
    key: 'site_settings',
    icon: renderIcon(ControlOutlined),
  });
}
const handleUserOptionSelect = key => {
  if (key === 'logout') {
    Axios.get('/user/logout/').then(() => {
      store.commit('logout');
      router.push({ name: 'login' });
    });
  } else if (key === 'user_detail') {
    router.push({ name: 'user_detail', params: { id: store.state.user.id } });
  } else {
    router.push({ name: key });
  }
};
</script>

<template>
  <div style="display: inline-block">
    <n-space size="small">
      <router-link :to="{ name: 'home' }">
        <n-button
          :tertiary="route.meta.cate === 'home'"
          :quaternary="route.meta.cate !== 'home'"
        >
          <template #icon>
            <n-icon :component="HomeOutlined" />
          </template>
          首页
        </n-button>
      </router-link>
      <router-link :to="{ name: 'problem_list' }">
        <n-button
          :tertiary="route.meta.cate === 'problem'"
          :quaternary="route.meta.cate !== 'problem'"
        >
          <template #icon>
            <n-icon :component="BookOutline" />
          </template>
          题目
        </n-button>
      </router-link>
      <router-link :to="{ name: 'contest_list' }">
        <n-button
          :tertiary="route.meta.cate === 'contest'"
          :quaternary="route.meta.cate !== 'contest'"
        >
          <template #icon>
            <n-icon :component="TrophyOutline" />
          </template>
          比赛
        </n-button>
      </router-link>
      <router-link :to="{ name: 'problemset_list' }">
        <n-button
          :tertiary="route.meta.cate === 'problemset'"
          :quaternary="route.meta.cate !== 'problemset'"
        >
          <template #icon>
            <n-icon :component="ListOutline" />
          </template>
          题单
        </n-button>
      </router-link>
      <router-link :to="{ name: 'class_list' }" v-if="store.getters.loggedIn">
        <n-button
          :tertiary="route.meta.cate === 'class'"
          :quaternary="route.meta.cate !== 'class'"
        >
          <template #icon>
            <n-icon :component="TeamOutlined" />
          </template>
          班级
        </n-button>
      </router-link>
      <router-link :to="{ name: 'submission_list' }">
        <n-button
          :tertiary="route.meta.cate === 'submission'"
          :quaternary="route.meta.cate !== 'submission'"
        >
          <template #icon>
            <n-icon :component="HourglassOutlined" />
          </template>
          提交
        </n-button>
      </router-link>
      <router-link
        :to="{ name: 'discussion_list' }"
        v-if="config.enableDiscussion"
      >
        <n-button
          :tertiary="route.meta.cate === 'discussion'"
          :quaternary="route.meta.cate !== 'discussion'"
        >
          <template #icon>
            <n-icon :component="CommentOutlined" />
          </template>
          讨论
        </n-button>
      </router-link>
      <router-link :to="{ name: 'user_list' }">
        <n-button
          :tertiary="route.meta.cate === 'user'"
          :quaternary="route.meta.cate !== 'user'"
        >
          <template #icon>
            <n-icon :component="PeopleOutline" />
          </template>
          用户
        </n-button>
      </router-link>
    </n-space>
  </div>
  <div style="display: inline; float: right">
    <n-space size="small" v-if="!store.getters.loggedIn">
      <router-link :to="{ name: 'register' }" v-if="config.allowRegister">
        <n-button
          :tertiary="route.meta.cate === 'register'"
          :quaternary="route.meta.cate !== 'register'"
        >
          <template #icon>
            <n-icon :component="UserAddOutlined" />
          </template>
          注册
        </n-button>
      </router-link>

      <router-link :to="{ name: 'login' }">
        <n-button
          :tertiary="route.meta.cate === 'login'"
          :quaternary="route.meta.cate !== 'login'"
        >
          <template #icon>
            <n-icon :component="LogInOutline" />
          </template>
          登录
        </n-button>
      </router-link>
    </n-space>
    <n-space size="small" v-else>
      <n-dropdown
        trigger="hover"
        :options="userOptions"
        size="large"
        @select="handleUserOptionSelect"
      >
        <n-button size="large" quaternary>
          欢迎回来，{{ store.state.user.username }}
        </n-button>
      </n-dropdown>
    </n-space>
  </div>
</template>

<style lang="scss" scoped>
a {
  text-decoration: none;
}
</style>
�,"(6b457f522aa10499b55789fae01ec35627afe7b62-file:///root/frontend-naive/src/AppHeader.vue:file:///root/frontend-naive