�2<script setup>
import { h, ref } from 'vue';
import router from '@/router';
import store from '@/store';
import { NButton, NIcon, NSpace, NAvatar, NTag, NSelect, useMessage, useDialog } from 'naive-ui';
import { RouterLink } from 'vue-router';
import Axios from '@/plugins/axios';

const props = defineProps({
  data: {
    type: Array,
    default: [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['refresh']);
const message = useMessage();
const dialog = useDialog();

// 角色选项
const roleOptions = [
  { label: '学生', value: 'student' },
  { label: '教师', value: 'teacher' },
  { label: '管理员', value: 'admin' },
];

// 根据权限判断角色
const getUserRole = (user) => {
  // 如果是超级用户或管理员，直接返回管理员
  if (user.is_superuser || user.is_staff) {
    return 'admin';
  }
  
  if (!user.permissions || user.permissions.length === 0) {
    return 'student';
  }
  // 如果有任何管理权限，视为管理员
  if (user.permissions.includes('site_setting') || 
      user.permissions.includes('user') ||
      user.permissions.includes('submission') ||
      user.permissions.includes('discussion')) {
    return 'admin';
  }
  // 如果有题目、比赛权限，视为教师
  if (user.permissions.includes('problem') || user.permissions.includes('contest')) {
    return 'teacher';
  }
  return 'student';
};

// 根据角色获取权限列表
const getPermissionsByRole = (role) => {
  switch (role) {
    case 'admin':
      return ['site_setting', 'user', 'problem', 'submission', 'discussion', 'contest'];
    case 'teacher':
      return ['problem', 'contest'];
    case 'student':
    default:
      return [];
  }
};

// 更新用户角色
const updateUserRole = (userId, newRole) => {
  const permissions = getPermissionsByRole(newRole);
  
  Axios.patch(`/user/${userId}/`, { permissions })
    .then(() => {
      message.success('角色更新成功');
      emit('refresh');
    })
    .catch((err) => {
      message.error(err.response?.data?.error || '角色更新失败');
    });
};

// 切换用户封禁状态
const toggleUserActive = (userId, isActive, username) => {
  const action = isActive ? '封禁' : '解封';
  const actionType = isActive ? 'warning' : 'success';
  
  dialog[actionType]({
    title: `${action}用户`,
    content: `确定要${action}用户 "${username}" 吗？`,
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: () => {
      return new Promise((resolve, reject) => {
        Axios.post(`/user/${userId}/toggle-active/`)
          .then(() => {
            message.success(`${action}成功`);
            emit('refresh');
            resolve();
          })
          .catch((err) => {
            message.error(err.response?.data?.error || `${action}失败`);
            reject();
          });
      });
    }
  });
};

// 检查当前用户是否是管理员
const isAdmin = () => {
  return store.state.user.is_superuser || 
         store.state.user.is_staff ||
         (store.state.user.permissions && 
          (store.state.user.permissions.includes('user') || 
           store.state.user.permissions.includes('site_setting')));
};

const columns = [
  {
    title: 'ID',
    render(row) {
      return h(
        RouterLink,
        { to: { name: 'user_detail', params: { id: row.id } } },
        {
          default: () =>
            h(
              NButton,
              {
                text: true,
                size: 'small',
              },
              { default: () => row.id }
            ),
        }
      );
    },
  },
  {
    title: '用户名',
    render(row) {
      return h(
        RouterLink,
        { to: { name: 'user_detail', params: { id: row.id } } },
        {
          default: () =>
            h(
              NSpace,
              {
                style: {
                  display: 'inline-flex',
                },
              },
              {
                default: () => [
                  row.avatar
                    ? h(NAvatar, {
                        src: row.avatar,
                        size: 'small',
                        round: true,
                      })
                    : null,
                  h(
                    NButton,
                    {
                      text: true,
                      size: 'small',
                      style: {
                        marginTop: '6px',
                      },
                    },
                    { default: () => row.username }
                  ),
                ],
              }
            ),
        }
      );
    },
  },
  {
    title: '角色',
    render(row) {
      const role = getUserRole(row);
      const roleText = role === 'admin' ? '管理员' : role === 'teacher' ? '教师' : '学生';
      const roleType = role === 'admin' ? 'error' : role === 'teacher' ? 'success' : 'info';
      
      return h(NTag, { type: roleType, size: 'small' }, { default: () => roleText });
    },
  },
  {
    title: '状态',
    render(row) {
      if (!row.is_active) {
        return h(NTag, { type: 'error', size: 'small' }, { default: () => '已封禁' });
      }
      return h(NTag, { type: 'success', size: 'small' }, { default: () => '正常' });
    },
  },
  {
    title: '操作',
    render(row) {
      if (!isAdmin()) {
        return null;
      }
      
      // 不能修改自己的权限
      if (row.id === store.state.user.id) {
        return h('span', { style: 'color: #999' }, '当前用户');
      }
      
      return h(NSpace, {}, {
        default: () => [
          h(NSelect, {
            value: getUserRole(row),
            options: roleOptions,
            size: 'small',
            style: 'width: 100px',
            onUpdateValue: (value) => updateUserRole(row.id, value),
          }),
          h(NButton, {
            size: 'small',
            type: row.is_active ? 'warning' : 'success',
            disabled: row.is_superuser,
            onClick: () => toggleUserActive(row.id, row.is_active, row.username),
          }, {
            default: () => row.is_active ? '封禁' : '解封'
          })
        ]
      });
    },
  },
];
</script>

<template>
  <n-spin :show="loading">
    <n-data-table :columns="columns" :data="data" :bordered="false" />
  </n-spin>
</template>

<style lang="scss" scoped>
:deep(a) {
  text-decoration: none;
}
</style>
�2"(4c939b463a4d54455b4d86fe5d7a7a58edde9bde28file:///root/frontend-naive/src/components/UserTable.vue:file:///root/frontend-naive