<script setup>
import { computed, h } from 'vue';
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
  ThunderboltOutlined,
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
  SchoolOutline,
} from '@vicons/ionicons5';
import config from './config';

const route = useRoute();

const renderIcon = icon => {
  return () =>
    h(NIcon, null, {
      default: () => h(icon),
    });
};

const baseUserOptions = [
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

const userOptions = computed(() => {
  const permissions = store.state.user?.permissions || [];
  const options = [...baseUserOptions];
  if (permissions.includes('site_setting')) {
    options.splice(2, 0, {
      label: '站点设置',
      key: 'site_settings',
      icon: renderIcon(ControlOutlined),
    });
  }
  return options;
});

const canSeeToolsNav = computed(() => {
  const permissions = store.state.user?.permissions || [];
  return (
    permissions.includes('problem') ||
    permissions.includes('site_setting') ||
    permissions.includes('contest')
  );
});

const toolsOptions = [
  {
    label: '画板（Excalidraw）',
    key: 'tools_excalidraw',
  },
  {
    label: '比赛批量上传评测',
    key: 'tools_contest_batch_judge',
  },
];

const handleToolsSelect = key => {
  router.push({ name: key });
};

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
      <router-link :to="{ name: 'battle_lobby' }" v-if="store.getters.loggedIn">
        <n-button
          :tertiary="route.meta.cate === 'battle'"
          :quaternary="route.meta.cate !== 'battle'"
        >
          <template #icon>
            <n-icon :component="ThunderboltOutlined" />
          </template>
          对战
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
      <router-link :to="{ name: 'course_list' }" v-if="store.getters.loggedIn">
        <n-button
          :tertiary="route.meta.cate === 'course'"
          :quaternary="route.meta.cate !== 'course'"
        >
          <template #icon>
            <n-icon :component="SchoolOutline" />
          </template>
          课程
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
      <router-link :to="{ name: 'book_list' }" v-if="store.getters.loggedIn">
        <n-button
          :tertiary="route.meta.cate === 'book'"
          :quaternary="route.meta.cate !== 'book'"
        >
          <template #icon>
            <n-icon :component="BookOutline" />
          </template>
          电子书
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

      <n-dropdown
        v-if="store.getters.loggedIn && canSeeToolsNav"
        trigger="hover"
        :options="toolsOptions"
        @select="handleToolsSelect"
      >
        <n-button
          :tertiary="route.meta.cate === 'tools'"
          :quaternary="route.meta.cate !== 'tools'"
        >
          工具导航
        </n-button>
      </n-dropdown>
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
