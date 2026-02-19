<script setup>
import { computed, h, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import router from '@/router';
import Axios from '@/plugins/axios';
import store from '@/store';
import { AddOutline, LayersOutline } from '@vicons/ionicons5';
import { _writeSearchToQuery } from '@/plugins/utils';

const route = useRoute();

const typeOptions = [
  { label: '全部', value: null },
  { label: '单选题', value: 'single' },
  { label: '多选题', value: 'multiple' },
  { label: '判断题', value: 'judge' },
];

const typeLabelMap = {
  single: '单选题',
  multiple: '多选题',
  judge: '判断题',
};

const canManage = computed(() => {
  const perms = store.state.user?.permissions || [];
  return perms.includes('problem');
});

const pagination = ref({ pageSize: 20, page: 1, count: 0 });
const search = ref({
  search: '',
  question_type: null,
});
const data = ref([]);
const loading = ref(false);

const writeSearchToQuery = _writeSearchToQuery(search.value, pagination.value, route);

const summarizeContent = content => String(content || '').replace(/\s+/g, ' ').trim();

const columns = computed(() => {
  const startIndex = (pagination.value.page - 1) * pagination.value.pageSize;
  const baseColumns = [
    {
      title: '序号',
      key: 'display_index',
      width: 80,
      render: (_row, index) => startIndex + index + 1,
    },
    {
      title: '题干',
      key: 'content',
      render: row => h(
        'a',
        {
          href: 'javascript:void(0)',
          onClick: () => router.push({ name: 'objective_detail', params: { id: row.id } }),
          style: 'color: #1e40af; text-decoration: none; font-weight: 600; display: inline-block; max-width: 520px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;',
          title: summarizeContent(row.content) || row.title || '',
        },
        summarizeContent(row.content) || row.title || ''
      ),
    },
    {
      title: '题型',
      key: 'question_type',
      width: 110,
      render: row => typeLabelMap[row.question_type] || row.question_type,
    },
    { title: '难度', key: 'difficulty', width: 90 },
    { title: '通过', key: 'accepted_count', width: 90 },
    { title: '提交', key: 'submission_count', width: 90 },
  ];

  if (canManage.value) {
    baseColumns.push({
      title: '操作',
      key: 'actions',
      width: 120,
      render: row => h(
        'a',
        {
          href: 'javascript:void(0)',
          onClick: () => router.push({ name: 'objective_edit', params: { id: row.id } }),
          style: 'color: #0f766e; text-decoration: none; font-weight: 600;',
        },
        '编辑'
      ),
    });
  }

  return baseColumns;
});

const loadData = () => {
  search.value.search = route.query.search || '';
  search.value.question_type = route.query.question_type || null;
  for (const key in pagination.value) {
    if (route.query[key]) pagination.value[key] = parseInt(route.query[key]);
  }

  loading.value = true;
  Axios.get('/objective/', {
    params: {
      limit: pagination.value.pageSize,
      offset: (pagination.value.page - 1) * pagination.value.pageSize,
      search: search.value.search,
      question_type: search.value.question_type || undefined,
    },
  })
    .then(res => {
      pagination.value.count = res.count;
      data.value = res.results || [];
    })
    .finally(() => {
      loading.value = false;
    });
};

watch(() => route.query, loadData);
loadData();
</script>

<template>
  <n-layout>
    <h1>客观题</h1>
    <n-layout-content>
      <n-space align="center" justify="space-between">
        <n-form inline>
          <n-form-item label="题目ID/名称">
            <n-input v-model:value="search.search" @keydown.enter="writeSearchToQuery" />
          </n-form-item>
          <n-form-item label="题型">
            <n-select
              v-model:value="search.question_type"
              :options="typeOptions"
              style="min-width: 150px"
              placeholder="全部题型"
            />
          </n-form-item>
          <n-form-item>
            <n-button type="primary" @click="writeSearchToQuery">搜索</n-button>
          </n-form-item>
        </n-form>

        <n-space>
          <n-button @click="router.push({ name: 'objective_paper_list' })">
            <template #icon><n-icon :component="LayersOutline" /></template>
            查看套卷
          </n-button>
          <router-link :to="{ name: 'objective_create' }" v-if="canManage">
            <n-button type="primary">
              <template #icon>
                <n-icon :component="AddOutline" />
              </template>
              创建客观题
            </n-button>
          </router-link>
          <router-link :to="{ name: 'objective_paper_create' }" v-if="canManage">
            <n-button type="success">
              <template #icon>
                <n-icon :component="LayersOutline" />
              </template>
              一次创建套卷
            </n-button>
          </router-link>
        </n-space>
      </n-space>
    </n-layout-content>

    <n-layout-content style="margin-top: 16px">
      <n-data-table :columns="columns" :data="data" :loading="loading" :bordered="false" striped />
    </n-layout-content>

    <n-layout-content>
      <div style="margin-top: 24px; text-align: center">
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
  </n-layout>
</template>
