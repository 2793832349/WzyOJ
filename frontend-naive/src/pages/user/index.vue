<script setup>
import { ref, watch } from 'vue';
import Axios from '@/plugins/axios';
import { useMessage } from 'naive-ui';

import store from '@/store';
import UserTable from '@/components/UserTable.vue';
import { useRoute } from 'vue-router';
import { AddOutline, CloudUploadOutline } from '@vicons/ionicons5';
import { _writeSearchToQuery } from '@/plugins/utils';

const route = useRoute();

const pagination = ref({ pageSize: 20, page: 1, count: 0 }),
  search = ref(''),
  data = ref([]),
  loading = ref(false);

const showCreateUser = ref(false);
const createUserForm = ref({ username: '', password: '', role: 'student' });
const createUserLoading = ref(false);

const showBulkImport = ref(false);
const bulkImportLoading = ref(false);
const bulkImportFile = ref(null);
const bulkImportResults = ref(null);

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

const submitBulkImport = () => {
  if (!bulkImportFile.value) {
    message.error('请选择CSV文件');
    return;
  }
  
  const formData = new FormData();
  formData.append('file', bulkImportFile.value);
  
  bulkImportLoading.value = true;
  Axios.post('/user/bulk-import/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
    .then(res => {
      bulkImportResults.value = res;
      message.success(`成功导入 ${res.created} 个用户`);
      if (res.failed > 0) {
        message.warning(`${res.failed} 个用户导入失败`);
      }
      bulkImportFile.value = null;
      handleQueryChange();
    })
    .catch(err => {
      message.error(err.response?.data?.error || '导入失败');
    })
    .finally(() => {
      bulkImportLoading.value = false;
    });
};

const closeBulkImport = () => {
  showBulkImport.value = false;
  bulkImportFile.value = null;
  bulkImportResults.value = null;
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
      <n-space style="float: right; margin-top: 25px" v-if="store.state.user.permissions.includes('user')">
        <n-button
          type="primary"
          @click="showBulkImport = true"
        >
          <template #icon>
            <n-icon :component="CloudUploadOutline" />
          </template>
          批量导入
        </n-button>
        <n-button
          type="primary"
          @click="showCreateUser = true"
        >
          <template #icon>
            <n-icon :component="AddOutline" />
          </template>
          创建用户
        </n-button>
      </n-space>
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
    <!-- 创建单个用户模态框 -->
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

    <!-- 批量导入用户模态框 -->
    <n-modal v-model:show="showBulkImport" preset="card" title="批量导入用户" style="width: min(92vw, 600px)">
      <n-tabs v-if="!bulkImportResults">
        <n-tab-pane name="import" tab="导入数据">
          <n-space vertical>
            <n-alert type="info">
              CSV 文件格式: <code>角色,用户名,密码</code><br/>
              支持的角色: <code>admin</code>, <code>teacher</code>, <code>student</code>, <code>guest</code>
            </n-alert>
            <n-alert type="warning">
              示例:<br/>
              <code>admin,admin1,password123</code><br/>
              <code>teacher,teacher1,password123</code><br/>
              <code>student,student1,password123</code>
            </n-alert>
            <div>
              <n-upload
                :file-list="bulkImportFile ? [{ name: bulkImportFile.name, status: 'finished' }] : []"
                action="#"
                :auto-upload="false"
                :max="1"
                accept=".csv"
                @update:file-list="files => bulkImportFile = files[0]?.file || null"
              >
                <n-upload-dragger>
                  <div style="margin-bottom: 12px">
                    <n-icon size="48" :depth="3" :component="CloudUploadOutline" />
                  </div>
                  <n-text style="font-size: 16px">
                    点击或拖拽CSV文件到此处
                  </n-text>
                  <n-p depth="3" style="margin: 8px 0 0 0">
                    请选择 UTF-8 编码的 CSV 文件
                  </n-p>
                </n-upload-dragger>
              </n-upload>
            </div>
            <n-space>
              <n-button type="primary" :loading="bulkImportLoading" @click="submitBulkImport">导入</n-button>
              <n-button @click="closeBulkImport" :disabled="bulkImportLoading">取消</n-button>
            </n-space>
          </n-space>
        </n-tab-pane>
        <n-tab-pane name="help" tab="使用说明">
          <n-space vertical>
            <n-text>
              <strong>格式说明:</strong><br/>
              每行代表一个用户,使用英文逗号分隔三个字段:<br/>
              1. 角色 (role): admin / teacher / student / guest<br/>
              2. 用户名 (username): 唯一标识符<br/>
              3. 密码 (password): 用户初始密码
            </n-text>
            <n-text>
              <strong>示例 CSV 内容:</strong><br/>
              <code>admin,admin1,password123<br/>
              teacher,teacher1,pass456<br/>
              student,student1,pass789<br/>
              student,student2,pass789</code>
            </n-text>
            <n-text>
              <strong>注意事项:</strong><br/>
              • 文件必须是 UTF-8 编码<br/>
              • 文件扩展名须为 .csv<br/>
              • 用户名不能重复<br/>
              • 如有导入失败的行,系统会返回具体的失败原因
            </n-text>
          </n-space>
        </n-tab-pane>
      </n-tabs>

      <!-- 导入结果 -->
      <n-space vertical v-if="bulkImportResults">
        <n-alert type="success">
          <strong>导入完成</strong><br/>
          成功: {{ bulkImportResults.created }} 个用户<br/>
          失败: {{ bulkImportResults.failed }} 个用户
        </n-alert>
        
        <n-collapse v-if="bulkImportResults.details && bulkImportResults.details.length > 0">
          <n-collapse-item title="详细结果" name="details">
            <n-list>
              <n-list-item v-for="(item, idx) in bulkImportResults.details" :key="idx">
                <template #prefix>
                  <n-tag
                    :type="item.status === 'success' ? 'success' : 'error'"
                    round
                  >
                    {{ item.status === 'success' ? '✓' : '✗' }}
                  </n-tag>
                </template>
                <div>
                  <div><strong>第 {{ item.row }} 行</strong></div>
                  <div v-if="item.username">用户名: {{ item.username }}</div>
                  <div v-if="item.role">角色: {{ item.role }}</div>
                  <div v-if="item.reason" style="color: #d03050;">
                    原因: {{ item.reason }}
                  </div>
                </div>
              </n-list-item>
            </n-list>
          </n-collapse-item>
        </n-collapse>

        <n-space>
          <n-button type="primary" @click="closeBulkImport">完成</n-button>
        </n-space>
      </n-space>
    </n-modal>
  </n-layout>
</template>
