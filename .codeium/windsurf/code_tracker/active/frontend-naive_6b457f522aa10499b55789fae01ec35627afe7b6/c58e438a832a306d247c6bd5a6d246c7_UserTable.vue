µ2<script setup>
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

// è§’è‰²é€‰é¡¹
const roleOptions = [
  { label: 'å­¦ç”Ÿ', value: 'student' },
  { label: 'æ•™å¸ˆ', value: 'teacher' },
  { label: 'ç®¡ç†å‘˜', value: 'admin' },
];

// æ ¹æ®æƒé™åˆ¤æ–­è§’è‰²
const getUserRole = (user) => {
  // å¦‚æœæ˜¯è¶…çº§ç”¨æˆ·æˆ–ç®¡ç†å‘˜ï¼Œç›´æ¥è¿”å›ç®¡ç†å‘˜
  if (user.is_superuser || user.is_staff) {
    return 'admin';
  }
  
  if (!user.permissions || user.permissions.length === 0) {
    return 'student';
  }
  // å¦‚æœæœ‰ä»»ä½•ç®¡ç†æƒé™ï¼Œè§†ä¸ºç®¡ç†å‘˜
  if (user.permissions.includes('site_setting') || 
      user.permissions.includes('user') ||
      user.permissions.includes('submission') ||
      user.permissions.includes('discussion')) {
    return 'admin';
  }
  // å¦‚æœæœ‰é¢˜ç›®ã€æ¯”èµ›æƒé™ï¼Œè§†ä¸ºæ•™å¸ˆ
  if (user.permissions.includes('problem') || user.permissions.includes('contest')) {
    return 'teacher';
  }
  return 'student';
};

// æ ¹æ®è§’è‰²è·å–æƒé™åˆ—è¡¨
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

// æ›´æ–°ç”¨æˆ·è§’è‰²
const updateUserRole = (userId, newRole) => {
  const permissions = getPermissionsByRole(newRole);
  
  Axios.patch(`/user/${userId}/`, { permissions })
    .then(() => {
      message.success('è§’è‰²æ›´æ–°æˆåŠŸ');
      emit('refresh');
    })
    .catch((err) => {
      message.error(err.response?.data?.error || 'è§’è‰²æ›´æ–°å¤±è´¥');
    });
};

// åˆ‡æ¢ç”¨æˆ·å°ç¦çŠ¶æ€
const toggleUserActive = (userId, isActive, username) => {
  const action = isActive ? 'å°ç¦' : 'è§£å°';
  const actionType = isActive ? 'warning' : 'success';
  
  dialog[actionType]({
    title: `${action}ç”¨æˆ·`,
    content: `ç¡®å®šè¦${action}ç”¨æˆ· "${username}" å—ï¼Ÿ`,
    positiveText: 'ç¡®å®š',
    negativeText: 'å–æ¶ˆ',
    onPositiveClick: () => {
      return new Promise((resolve, reject) => {
        Axios.post(`/user/${userId}/toggle-active/`)
          .then(() => {
            message.success(`${action}æˆåŠŸ`);
            emit('refresh');
            resolve();
          })
          .catch((err) => {
            message.error(err.response?.data?.error || `${action}å¤±è´¥`);
            reject();
          });
      });
    }
  });
};

// æ£€æŸ¥å½“å‰ç”¨æˆ·æ˜¯å¦æ˜¯ç®¡ç†å‘˜
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
    title: 'ç”¨æˆ·å',
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
    title: 'è§’è‰²',
    render(row) {
      const role = getUserRole(row);
      const roleText = role === 'admin' ? 'ç®¡ç†å‘˜' : role === 'teacher' ? 'æ•™å¸ˆ' : 'å­¦ç”Ÿ';
      const roleType = role === 'admin' ? 'error' : role === 'teacher' ? 'success' : 'info';
      
      return h(NTag, { type: roleType, size: 'small' }, { default: () => roleText });
    },
  },
  {
    title: 'çŠ¶æ€',
    render(row) {
      if (!row.is_active) {
        return h(NTag, { type: 'error', size: 'small' }, { default: () => 'å·²å°ç¦' });
      }
      return h(NTag, { type: 'success', size: 'small' }, { default: () => 'æ­£å¸¸' });
    },
  },
  {
    title: 'æ“ä½œ',
    render(row) {
      if (!isAdmin()) {
        return null;
      }
      
      // ä¸èƒ½ä¿®æ”¹è‡ªå·±çš„æƒé™
      if (row.id === store.state.user.id) {
        return h('span', { style: 'color: #999' }, 'å½“å‰ç”¨æˆ·');
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
            default: () => row.is_active ? 'å°ç¦' : 'è§£å°'
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
¬ ¬·*cascade08
·ê ê†*cascade08
†ƒ ƒ*cascade08
Ç Çû*cascade08
ûş ş‚*cascade08
‚ƒ ƒ¶*cascade08
¶· ·¸*cascade08
¸» »Á*cascade08
ÁÚ Úé*cascade08
éğ ğÀ*cascade08
ÀÁ ÁÄ*cascade08
ÄË ËÍ*cascade08
ÍÓ Óö*cascade08
öù ùû*cascade08
û° °¶*cascade08
¶Ä ÄÆ*cascade08
ÆÌ ÌĞ*cascade08
Ğú ú€*cascade08
€‘ ‘®*cascade08
®µ µ»*cascade08
»Ñ Ñ×*cascade08
× Ğ*cascade08
ĞË/ Ë/Ù/*cascade08
Ù/µ2 "(6b457f522aa10499b55789fae01ec35627afe7b628file:///root/frontend-naive/src/components/UserTable.vue:file:///root/frontend-naive