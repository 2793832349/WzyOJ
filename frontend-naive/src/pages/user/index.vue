<script setup>
import { ref, watch } from 'vue';
import Axios from '@/plugins/axios';
import { useMessage } from 'naive-ui';

import store from '@/store';
import UserTable from '@/components/UserTable.vue';
import { useRoute } from 'vue-router';
import { AddOutline } from '@vicons/ionicons5';
import { _writeSearchToQuery } from '@/plugins/utils';

const route = useRoute();

const pagination = ref({ pageSize: 20, page: 1, count: 0 }),
  search = ref(''),
  data = ref([]),
  loading = ref(false);

const showCreateUser = ref(false);
const createUserForm = ref({ username: '', password: '', role: 'student' });
const createUserLoading = ref(false);
const message = useMessage();

const roleOptions = [
  { label: '学生', value: 'student' },
  { label: '教师', value: 'teacher' },
  { label: '管理员', value: 'admin' },
];

const getPermissionsByRole = role => {
  switch (role) {
    case 'admin':
      return [
        'site_setting',
        'user',
        'problem',
        'submission',
        'discussion',
        'contest',
        'class',
      ];
    case 'teacher':
      return ['problem', 'contest', 'class'];
    case 'student':
    default:
      return [];
  }
};

const submitCreateUser = () => {
  if (!createUserForm.value.username || !createUserForm.value.password) {
    message.error('用户名或密码不能为空');
    return;
  }
  createUserLoading.value = true;
  Axios.post('/user/', {
    username: createUserForm.value.username,
    password: createUserForm.value.password,
    permissions: getPermissionsByRole(createUserForm.value.role),
  })
    .then(() => {
      message.success('创建成功');
      showCreateUser.value = false;
      createUserForm.value = { username: '', password: '', role: 'student' };
      handleQueryChange();
    })
    .finally(() => {
      createUserLoading.value = false;
    });
};
const writeSearchToQuery = () => {
  const _search = { search: search.value };
  _writeSearchToQuery(_search, pagination.value, route)();
};

const handleQueryChange = () => {
  if (route.name !== 'user_list') return;

  if (route.query.search) search.value = route.query.search;
  for (const key in pagination.value) {
    if (route.query[key]) pagination.value[key] = parseInt(route.query[key]);
  }

  loading.value = true;
  Axios.get('/user/', {
    params: {
      limit: pagination.value.pageSize,
      offset: (pagination.value.page - 1) * pagination.value.pageSize,
      search: search.value,
    },
  })
    .then(res => {
      pagination.value.count = res.count;
      data.value = res.results;
    })
    .finally(() => {
      loading.value = false;
    });
};

watch(() => route.query, handleQueryChange);
handleQueryChange();
</script>

<template>
  <n-layout>
    <h1>用户列表</h1>
    <n-layout-content>
      <div style="display: inline-block">
        <n-form inline>
          <n-form-item label="用户ID/名称">
            <n-input
              v-model:value="search"
              @keydown.enter="writeSearchToQuery"
            />
          </n-form-item>
          <n-form-item>
            <n-button type="primary" @click="writeSearchToQuery">搜索</n-button>
          </n-form-item>
        </n-form>
      </div>
      <n-button
        style="float: right; margin-top: 25px"
        type="primary"
        v-if="store.state.user.permissions.includes('user')"
        @click="showCreateUser = true"
      >
        <template #icon>
          <n-icon :component="AddOutline" />
        </template>
        创建用户
      </n-button>
    </n-layout-content>
    <n-layout-content>
      <UserTable :data="data" :loading="loading" @refresh="handleQueryChange" />
    </n-layout-content>
    <n-layout-content>
      <div style="margin-top: 30px; text-align: center">
        <n-pagination
          v-model:page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :item-count="pagination.count"
          show-size-picker
          show-quick-jumper
          :page-sizes="[10, 20, 50]"
          @update:page="writeSearchToQuery"
          @update:page-size="
            pageSize => {
              pagination.pageSize = pageSize;
              pagination.page = 1;
              writeSearchToQuery();
            }
          "
        />
      </div>
    </n-layout-content>
    <n-modal v-model:show="showCreateUser" preset="card" title="创建用户" style="width: min(92vw, 420px)">
      <n-form>
        <n-form-item label="初始角色">
          <n-select v-model:value="createUserForm.role" :options="roleOptions" />
        </n-form-item>
        <n-form-item label="用户名">
          <n-input v-model:value="createUserForm.username" />
        </n-form-item>
        <n-form-item label="密码">
          <n-input v-model:value="createUserForm.password" type="password" />
        </n-form-item>
        <n-form-item>
          <n-space>
            <n-button type="primary" :loading="createUserLoading" @click="submitCreateUser">创建</n-button>
            <n-button @click="showCreateUser = false" :disabled="createUserLoading">取消</n-button>
          </n-space>
        </n-form-item>
      </n-form>
    </n-modal>
  </n-layout>
</template>
