import { createRouter, createWebHistory } from 'vue-router';
import config from '../config';
import store from '@/store';
import NProgress from 'nprogress';
import 'nprogress/nprogress.css';

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/pages/home.vue'),
    meta: {
      title: '首页',
      cate: 'home',
    },
  },
  {
    path: '/user/login/',
    name: 'login',
    component: () => import('@/pages/user/login.vue'),
    meta: {
      title: '登录',
      cate: 'login',
    },
  },
  {
    path: '/user/register/',
    name: 'register',
    component: () => import('@/pages/user/register.vue'),
    meta: {
      title: '注册',
      cate: 'register',
      requiredAdmin: !config.allowRegister,
      permission: 'user',
    },
  },
  {
    path: '/user/',
    name: 'user_list',
    component: () => import('@/pages/user/index.vue'),
    meta: {
      title: '用户列表',
      cate: 'user',
      requiredLogin: true,
    },
  },
  {
    path: '/user/:id/',
    name: 'user_detail',
    component: () => import('@/pages/user/_id.vue'),
    meta: {
      title: '用户详情 #{id}',
      cate: 'user',
      requiredLogin: true,
    },
  },
  {
    path: '/user/settings/',
    name: 'user_settings',
    component: () => import('@/pages/user/settings.vue'),
    meta: {
      title: '个人设置',
      cate: 'user',
      requiredLogin: true,
    },
  },
  {
    path: '/user/:id/edit/',
    name: 'user_edit',
    component: () => import('@/pages/user/settings.vue'),
    meta: {
      title: '编辑用户 #{id}',
      cate: 'user',
      requiredLogin: true,
      requiredAdmin: true,
      permission: 'user',
    },
  },
  {
    path: '/problem/',
    name: 'problem_list',
    component: () => import('@/pages/problem/index.vue'),
    meta: {
      title: '题目列表',
      cate: 'problem',
    },
  },
  {
    path: '/problem/:id/',
    name: 'problem_detail',
    component: () => import('@/pages/problem/_id.vue'),
    meta: {
      title: '题目详情 #{id}',
      cate: 'problem',
      requiredLogin: true,
    },
  },
  {
    path: '/problem/tag/',
    name: 'tag_edit',
    component: () => import('@/pages/problem/tag.vue'),
    meta: {
      title: '标签管理',
      cate: 'problem',
      requiredLogin: true,
      requiredAdmin: true,
      permission: 'problem',
    },
  },
  {
    path: '/problem/create/',
    name: 'problem_create',
    component: () => import('@/pages/problem/edit.vue'),
    meta: {
      title: '创建题目',
      cate: 'problem',
      requiredLogin: true,
      requiredAdmin: true,
      permission: 'problem',
    },
  },
  {
    path: '/problem/:id/edit/',
    name: 'problem_edit',
    component: () => import('@/pages/problem/edit.vue'),
    meta: {
      title: '编辑题目 #{id}',
      cate: 'problem',
      requiredLogin: true,
      requiredAdmin: true,
      permission: 'problem',
    },
  },
  {
    path: '/contest/',
    name: 'contest_list',
    component: () => import('@/pages/contest/index.vue'),
    meta: {
      title: '比赛列表',
      cate: 'contest',
      requiredLogin: true,
    },
  },
  {
    path: '/contest/:id/',
    name: 'contest_detail',
    component: () => import('@/pages/contest/_id.vue'),
    meta: {
      title: '比赛详情 #{id}',
      cate: 'contest',
      requiredLogin: true,
    },
  },
  {
    path: '/contest/create/',
    name: 'contest_create',
    component: () => import('@/pages/contest/edit.vue'),
    meta: {
      title: '创建比赛',
      cate: 'contest',
      requiredLogin: true,
      requiredAdmin: true,
      permission: 'contest',
    },
  },
  {
    path: '/contest/:id/edit/',
    name: 'contest_edit',
    component: () => import('@/pages/contest/edit.vue'),
    meta: {
      title: '编辑比赛 #{id}',
      cate: 'contest',
      requiredLogin: true,
      requiredAdmin: true,
      permission: 'contest',
    },
  },
  {
    path: '/battle/',
    name: 'battle_lobby',
    component: () => import('@/pages/battle/index.vue'),
    meta: {
      title: '对战',
      cate: 'battle',
      requiredLogin: true,
    },
  },
  {
    path: '/battle/leaderboard/',
    name: 'battle_leaderboard',
    component: () => import('@/pages/battle/leaderboard.vue'),
    meta: {
      title: '对战排行榜',
      cate: 'battle',
      requiredLogin: true,
    },
  },
  {
    path: '/battle/:id/',
    name: 'battle_room',
    component: () => import('@/pages/battle/_id.vue'),
    meta: {
      title: '对战房间',
      cate: 'battle',
      requiredLogin: true,
    },
  },
  {
    path: '/problemset/',
    name: 'problemset_list',
    component: () => import('@/pages/problemset/index.vue'),
    meta: {
      title: '题单列表',
      cate: 'problemset',
      requiredLogin: true,
    },
  },
  {
    path: '/problemset/:id/',
    name: 'problemset_detail',
    component: () => import('@/pages/problemset/_id.vue'),
    meta: {
      title: '题单详情 #{id}',
      cate: 'problemset',
      requiredLogin: true,
    },
  },
  {
    path: '/problemset/create/',
    name: 'problemset_create',
    component: () => import('@/pages/problemset/edit.vue'),
    meta: {
      title: '创建题单',
      cate: 'problemset',
      requiredLogin: true,
      requiredAdmin: true,
      permission: 'contest',
    },
  },
  {
    path: '/problemset/:id/edit/',
    name: 'problemset_edit',
    component: () => import('@/pages/problemset/edit.vue'),
    meta: {
      title: '编辑题单 #{id}',
      cate: 'problemset',
      requiredLogin: true,
      requiredAdmin: true,
      permission: 'contest',
    },
  },
  {
    path: '/course/',
    name: 'course_list',
    component: () => import('@/pages/course/index.vue'),
    meta: {
      title: '课程',
      cate: 'course',
      requiredLogin: true,
    },
  },
  {
    path: '/course/:id/',
    name: 'course_detail',
    component: () => import('@/pages/course/_id.vue'),
    meta: {
      title: '课程 #{id}',
      cate: 'course',
      requiredLogin: true,
    },
  },
  {
    path: '/course/:id/live/',
    name: 'course_live',
    component: () => import('@/pages/course/live.vue'),
    meta: {
      title: '直播课堂',
      cate: 'course',
      requiredLogin: true,
    },
  },
  {
    path: '/course/create/',
    name: 'course_create',
    component: () => import('@/pages/course/edit.vue'),
    meta: {
      title: '创建课程',
      cate: 'course',
      requiredLogin: true,
      requiredAdmin: true,
      permission: 'class',
    },
  },
  {
    path: '/course/:id/edit/',
    name: 'course_edit',
    component: () => import('@/pages/course/edit.vue'),
    meta: {
      title: '编辑课程 #{id}',
      cate: 'course',
      requiredLogin: true,
      requiredAdmin: true,
      permission: 'class',
    },
  },
  {
    path: '/submission/',
    name: 'submission_list',
    component: () => import('@/pages/submission/index.vue'),
    meta: {
      title: '提交列表',
      cate: 'submission',
      requiredLogin: true,
    },
  },
  {
    path: '/submission/:id/',
    name: 'submission_detail',
    component: () => import('@/pages/submission/_id.vue'),
    meta: {
      title: '提交详情 #{id}',
      cate: 'submission',
      requiredLogin: true,
    },
  },
  {
    path: '/discussion/',
    name: 'discussion_list',
    component: () => import('@/pages/discussion/index.vue'),
    meta: {
      title: '讨论列表',
      cate: 'discussion',
      requiredLogin: true,
    },
  },
  {
    path: '/discussion/:id/',
    name: 'discussion_detail',
    component: () => import('@/pages/discussion/_id.vue'),
    meta: {
      title: '讨论详情 #{id}',
      cate: 'discussion',
      requiredLogin: true,
    },
  },
  {
    path: '/discussion/create/',
    name: 'discussion_create',
    component: () => import('@/pages/discussion/edit.vue'),
    meta: {
      title: '创建讨论',
      cate: 'discussion',
      requiredLogin: true,
    },
  },
  {
    path: '/site_settings/',
    name: 'site_settings',
    component: () => import('@/pages/settings.vue'),
    meta: {
      title: '站点设置',
      requiredLogin: true,
      requiredAdmin: true,
      permission: 'site_setting',
    },
  },
  {
    path: '/class/',
    name: 'class_list',
    component: () => import('@/pages/class/index.vue'),
    meta: {
      title: '我的班级',
      cate: 'class',
      requiredLogin: true,
    },
  },
  {
    path: '/class/:id/',
    name: 'class_detail',
    component: () => import('@/pages/class/_id.vue'),
    meta: {
      title: '班级详情 #{id}',
      cate: 'class',
      requiredLogin: true,
    },
  },
  {
    path: '/class/:id/problem/:problemId/',
    name: 'class_problem_detail',
    component: () => import('@/pages/class/problem/_id.vue'),
    meta: {
      title: '班级题目 #{problemId}',
      cate: 'class',
      requiredLogin: true,
    },
  },
  {
    path: '/tools/excalidraw/',
    name: 'tools_excalidraw',
    component: () => import('@/pages/tools/excalidraw.vue'),
    meta: {
      title: '画板（Excalidraw）',
      cate: 'tools',
      requiredLogin: true,
      requiredAdmin: true,
      permission: 'problem',
    },
  },
  {
    path: '/tools/contest-batch-judge/',
    name: 'tools_contest_batch_judge',
    component: () => import('@/pages/tools/contest_batch_judge.vue'),
    meta: {
      title: '比赛批量上传评测',
      cate: 'tools',
      requiredLogin: true,
      requiredAdmin: true,
      permission: 'contest',
    },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

NProgress.configure({
  showSpinner: false,
});

router.beforeEach((to, from, next) => {
  NProgress.start();
  if (
    !['home', 'login', 'register'].includes(to.name) &&
    !store.getters.loggedIn
  ) {
    window.$message.warning('请先登录');
    next({ name: 'login', query: { next: to.path } });
  } else if (
    to.meta.requiredAdmin &&
    !store.state.user.permissions.includes(to.meta.permission)
  ) {
    window.$message.error('您没有权限访问该页面');
    NProgress.done();
  } else next();
});

router.afterEach(to => {
  if (to.meta.title) {
    const title = to.meta.title.replace(/\{(.+?)\}/g, (match, p1) => {
      return to.params[p1];
    });
    document.title = `${title} - ${config.title}`;
  } else {
    document.title = config.title;
  }
  NProgress.done();
});

export { router };
export default router;
