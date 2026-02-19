<script setup>
import { ref, watch, computed } from 'vue';
import Axios from '@/plugins/axios';
import store from '@/store';
import ContestTable from '@/components/ContestTable.vue';
import { useRoute } from 'vue-router';
import { AddOutline, SearchOutline, LibraryOutline, ListOutline } from '@vicons/ionicons5';
import { _writeSearchToQuery } from '@/plugins/utils';

const route = useRoute();

const pagination = ref({ pageSize: 20, page: 1, count: 0 });
const search = ref('');
const data = ref([]);
const loading = ref(false);

const totalProblemsets = computed(() => pagination.value.count || 0);
const currentPageCount = computed(() => data.value.length || 0);

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
      problem_list_mode: true,
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
  <n-layout class="problemset-page">
    <section class="problemset-hero">
      <div class="hero-text">
        <p class="hero-kicker">训练中心</p>
        <h1>题单列表</h1>
        <p class="hero-subtitle">按主题管理与练习题目集合</p>
      </div>
      <div class="hero-metrics">
        <div class="metric-card">
          <n-icon :component="LibraryOutline" />
          <span>{{ totalProblemsets }}</span>
          <small>题单总数</small>
        </div>
        <div class="metric-card">
          <n-icon :component="ListOutline" />
          <span>{{ currentPageCount }}</span>
          <small>当前页题单</small>
        </div>
      </div>
    </section>

    <section class="toolbar-card">
      <div class="toolbar-left">
        <n-form inline>
          <n-form-item label="题单 ID/名称">
            <n-input
              v-model:value="search"
              placeholder="输入题单 ID 或名称"
              @keydown.enter="handleQueryChange"
            />
          </n-form-item>
          <n-form-item>
            <n-button type="primary" @click="handleQueryChange">
              <template #icon>
                <n-icon :component="SearchOutline" />
              </template>
              搜索
            </n-button>
          </n-form-item>
        </n-form>
      </div>
      <router-link
        :to="{ name: 'problemset_create' }"
        v-if="store.state.user.permissions.includes('contest')"
      >
        <n-button type="primary" class="create-btn">
          <template #icon>
            <n-icon :component="AddOutline" />
          </template>
          创建题单
        </n-button>
      </router-link>
    </section>

    <n-layout-content class="table-wrap">
      <ContestTable :data="data" :loading="loading" />
    </n-layout-content>

    <n-layout-content>
      <div class="pagination-wrap">
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

<style lang="scss" scoped>
.problemset-page {
  padding: 8px 6px 16px;
  --line-color: #dbe5f3;
}

.problemset-hero {
  display: flex;
  justify-content: space-between;
  align-items: stretch;
  gap: 18px;
  padding: 22px 24px;
  border-radius: 18px;
  background: linear-gradient(135deg, #1d4f7f 0%, #2a699b 48%, #67a3d2 100%);
  color: #fff;
  margin-bottom: 16px;
}

.hero-kicker {
  margin: 0;
  font-size: 13px;
  letter-spacing: 0.08em;
  opacity: 0.86;
}

.hero-text h1 {
  margin: 6px 0 2px;
  font-size: 34px;
  line-height: 1.1;
}

.hero-subtitle {
  margin: 0;
  font-size: 14px;
  opacity: 0.92;
}

.hero-metrics {
  display: flex;
  gap: 10px;
}

.metric-card {
  min-width: 132px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.28);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px 10px;
}

.metric-card :deep(.n-icon) {
  font-size: 18px;
  margin-bottom: 2px;
}

.metric-card span {
  font-size: 24px;
  font-weight: 700;
  line-height: 1.2;
}

.metric-card small {
  font-size: 12px;
  opacity: 0.92;
}

.toolbar-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 18px 8px;
  border: 1px solid var(--line-color);
  border-radius: 14px;
  background: #fff;
  margin-bottom: 14px;
}

.create-btn {
  box-shadow: 0 8px 20px rgba(29, 151, 84, 0.24);
}

.table-wrap {
  border: 1px solid var(--line-color);
  border-radius: 14px;
  background: #fff;
  padding: 6px;
}

.pagination-wrap {
  margin-top: 22px;
  display: flex;
  justify-content: center;
}

@media (max-width: 900px) {
  .problemset-hero {
    flex-direction: column;
    padding: 18px;
  }

  .hero-metrics {
    width: 100%;
  }

  .metric-card {
    flex: 1;
  }

  .toolbar-card {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
