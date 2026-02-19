<script setup>
import { computed, h, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import router from '@/router';
import Axios from '@/plugins/axios';
import store from '@/store';
import { AddOutline } from '@vicons/ionicons5';
import { _writeSearchToQuery } from '@/plugins/utils';

const route = useRoute();

const canManage = computed(() => {
  const perms = store.state.user?.permissions || [];
  return perms.includes('problem');
});

const pagination = ref({ pageSize: 20, page: 1, count: 0 });
const search = ref({ search: '' });
const data = ref([]);
const loading = ref(false);

const writeSearchToQuery = _writeSearchToQuery(search.value, pagination.value, route);

const columns = [
  { title: 'ID', key: 'id', width: 80 },
  {
    title: '套卷标题',
    key: 'title',
    render: row => h(
      'a',
      {
        href: 'javascript:void(0)',
        onClick: () => router.push({ name: 'objective_paper_detail', params: { id: row.id } }),
        style: 'color: #1e40af; text-decoration: none; font-weight: 600;',
      },
      row.title
    ),
  },
  { title: '题目数', key: 'question_count', width: 90 },
  { title: '总分', key: 'total_score', width: 90 },
  { title: '及格分', key: 'pass_score', width: 90 },
  {
    title: '更新时间',
    key: 'update_time',
    width: 190,
    render: row => new Date(row.update_time).toLocaleString(),
  },
];

const loadData = () => {
  search.value.search = route.query.search || '';
  for (const key in pagination.value) {
    if (route.query[key]) pagination.value[key] = parseInt(route.query[key]);
  }

  loading.value = true;
  Axios.get('/objective/paper/', {
    params: {
      limit: pagination.value.pageSize,
      offset: (pagination.value.page - 1) * pagination.value.pageSize,
      search: search.value.search,
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
    <h1>客观题套卷</h1>
    <n-layout-content>
      <n-space align="center" justify="space-between">
        <n-form inline>
          <n-form-item label="套卷ID/名称">
            <n-input v-model:value="search.search" @keydown.enter="writeSearchToQuery" />
          </n-form-item>
          <n-form-item>
            <n-button type="primary" @click="writeSearchToQuery">搜索</n-button>
          </n-form-item>
          <n-form-item>
            <n-button @click="router.push({ name: 'objective_list' })">返回客观题</n-button>
          </n-form-item>
        </n-form>

        <router-link :to="{ name: 'objective_paper_create' }" v-if="canManage">
          <n-button type="primary">
            <template #icon>
              <n-icon :component="AddOutline" />
            </template>
            一次创建套卷
          </n-button>
        </router-link>
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
