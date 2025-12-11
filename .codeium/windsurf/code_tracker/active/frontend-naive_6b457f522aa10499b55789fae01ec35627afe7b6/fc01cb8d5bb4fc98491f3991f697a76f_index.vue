�<script setup>
import { ref, watch } from 'vue';
import Axios from '@/plugins/axios';
import store from '@/store';
import ContestTable from '@/components/ContestTable.vue';
import { useRoute } from 'vue-router';
import { AddOutline } from '@vicons/ionicons5';
import { _writeSearchToQuery } from '@/plugins/utils';

const route = useRoute();

const pagination = ref({ pageSize: 20, page: 1, count: 0 }),
  search = ref(''),
  data = ref([]),
  loading = ref(false);
const writeSearchToQuery = () => {
  const _search = { search: search.value };
  _writeSearchToQuery(_search, pagination.value, route)();
};

const handleQueryChange = () => {
  if (route.name !== 'problemset_list') return;

  if (route.query.search) search.value = route.query.search;
  for (const key in pagination.value) {
    if (route.query[key]) pagination.value[key] = parseInt(route.query[key]);
  }

  loading.value = true;
  Axios.get('/contest/', {
    params: {
      limit: pagination.value.pageSize,
      offset: (pagination.value.page - 1) * pagination.value.pageSize,
      search: search.value,
      problem_list_mode: true, // 只获取题单
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
    <h1>题单列表</h1>
    <n-layout-content>
      <div style="display: inline-block">
        <n-form inline>
          <n-form-item label="题单 ID/名称">
            <n-input
              v-model:value="search"
              @keydown.enter="handleQueryChange"
            />
          </n-form-item>
          <n-form-item>
            <n-button type="primary" @click="handleQueryChange">搜索</n-button>
          </n-form-item>
        </n-form>
      </div>
      <router-link
        :to="{ name: 'problemset_create' }"
        v-if="store.state.user.permissions.includes('contest')"
      >
        <n-button style="float: right; margin-top: 25px" type="primary">
          <template #icon>
            <n-icon :component="AddOutline" />
          </template>
          创建题单
        </n-button>
      </router-link>
    </n-layout-content>
    <n-layout-content>
      <ContestTable :data="data" :loading="loading" />
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
  </n-layout>
</template>
�"(6b457f522aa10499b55789fae01ec35627afe7b62:file:///root/frontend-naive/src/pages/problemset/index.vue:file:///root/frontend-naive