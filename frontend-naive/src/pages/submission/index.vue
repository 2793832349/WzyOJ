<script setup>
import { computed, ref, watch } from 'vue';
import Axios from '@/plugins/axios';

import { languageOptions, statusOptions, judgeStatus } from '@/plugins/consts';
import SubmissionTable from '@/components/SubmissionTable.vue';
import { useRoute } from 'vue-router';
import { SearchOutline, RefreshOutline } from '@vicons/ionicons5';
import { _writeSearchToQuery } from '@/plugins/utils';

const route = useRoute();

const pagination = ref({ pageSize: 20, page: 1, count: 0 });
const search = ref({
  user__username: '',
  problem__id: '',
  language: null,
  status: null,
});
const data = ref([]);
const loading = ref(false);

const writeSearchToQuery = _writeSearchToQuery(search.value, pagination.value, route);

const hasActiveFilter = computed(() => {
  return !!search.value.user__username || !!search.value.problem__id || !!search.value.language || search.value.status !== null;
});

const currentPageCount = computed(() => data.value.length);
const acceptedCount = computed(() => data.value.filter(item => item.status === judgeStatus.ACCEPTED).length);
const judgingCount = computed(() =>
  data.value.filter(
    item => item.status === judgeStatus.PENDING || item.status === judgeStatus.JUDGING
  ).length
);
const totalPage = computed(() => Math.max(1, Math.ceil(pagination.value.count / pagination.value.pageSize)));

const resetFilters = () => {
  search.value.user__username = '';
  search.value.problem__id = '';
  search.value.language = null;
  search.value.status = null;
  writeSearchToQuery();
};

const handleQueryChange = (silent = false) => {
  if (route.name !== 'submission_list') return;

  search.value.user__username = route.query.user__username || '';
  search.value.problem__id = route.query.problem__id || '';
  search.value.language = route.query.language || null;
  search.value.status = route.query.status ? parseInt(route.query.status) : null;

  for (const key in pagination.value) {
    if (route.query[key]) pagination.value[key] = parseInt(route.query[key]);
  }

  if (silent !== true) loading.value = true;
  Axios.get('/submission/', {
    params: {
      limit: pagination.value.pageSize,
      offset: (pagination.value.page - 1) * pagination.value.pageSize,
      ...search.value,
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
  <div class="submission-page">
    <div class="bg-glow bg-glow-left" />
    <div class="bg-glow bg-glow-right" />

    <section class="hero-shell">
      <div class="hero-title-row">
        <h1>提交记录</h1>
        <n-tag v-if="hasActiveFilter" size="small" type="warning" :bordered="false">筛选中</n-tag>
      </div>
      <p>按用户、题目、语言和状态快速定位提交，移动端自动切换为卡片视图。</p>

      <div class="metrics-grid">
        <div class="metric-card metric-card-blue">
          <span class="metric-label">提交总数</span>
          <strong>{{ pagination.count }}</strong>
        </div>
        <div class="metric-card metric-card-green">
          <span class="metric-label">当前页条数</span>
          <strong>{{ currentPageCount }}</strong>
        </div>
        <div class="metric-card metric-card-emerald">
          <span class="metric-label">当前页 AC</span>
          <strong>{{ acceptedCount }}</strong>
        </div>
        <div class="metric-card metric-card-indigo">
          <span class="metric-label">评测中</span>
          <strong>{{ judgingCount }}</strong>
        </div>
      </div>
    </section>

    <n-card class="filter-card" :bordered="false">
      <div class="filter-header">
        <div>
          <h3>筛选控制台</h3>
          <p>输入条件后搜索，分页和筛选会自动同步到 URL。</p>
        </div>
      </div>

      <n-form label-placement="top">
        <div class="filter-grid">
          <n-form-item label="用户名称">
            <n-input
              v-model:value="search.user__username"
              placeholder="输入用户名"
              @keydown.enter="writeSearchToQuery"
            />
          </n-form-item>

          <n-form-item label="题目 ID">
            <n-input
              v-model:value="search.problem__id"
              type="number"
              placeholder="例如 1000"
              @keydown.enter="writeSearchToQuery"
            />
          </n-form-item>

          <n-form-item label="语言">
            <n-select
              v-model:value="search.language"
              :options="languageOptions"
              clearable
              placeholder="全部语言"
            />
          </n-form-item>

          <n-form-item label="状态">
            <n-select
              v-model:value="search.status"
              :options="statusOptions"
              clearable
              placeholder="全部状态"
            />
          </n-form-item>

          <n-form-item label="操作" class="action-item">
            <n-space :size="10" wrap>
              <n-button type="primary" @click="writeSearchToQuery">
                <template #icon>
                  <n-icon :component="SearchOutline" />
                </template>
                搜索
              </n-button>
              <n-button strong secondary @click="resetFilters">
                <template #icon>
                  <n-icon :component="RefreshOutline" />
                </template>
                重置
              </n-button>
            </n-space>
          </n-form-item>
        </div>
      </n-form>
    </n-card>

    <n-card class="table-card" :bordered="false">
      <template #header>
        <div class="table-header">
          <div>
            <span class="table-title">提交列表</span>
            <p class="table-subtitle">桌面端显示表格，手机端自动切换卡片布局。</p>
          </div>
          <span class="table-meta">第 {{ pagination.page }} / {{ totalPage }} 页</span>
        </div>
      </template>

      <SubmissionTable
        :data="data"
        :loading="loading"
        @refresh="handleQueryChange"
      />

      <div class="pager-wrap">
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
    </n-card>
  </div>
</template>

<style scoped>
.submission-page {
  position: relative;
  max-width: 1360px;
  margin: 0 auto;
  padding: 18px 20px 30px;
  overflow: hidden;
  font-family: 'Avenir Next', 'PingFang SC', 'Hiragino Sans GB', sans-serif;
}

.bg-glow {
  position: absolute;
  border-radius: 999px;
  filter: blur(60px);
  opacity: 0.35;
  z-index: 0;
  pointer-events: none;
}

.bg-glow-left {
  left: -120px;
  top: 100px;
  width: 220px;
  height: 220px;
  background: #58d9b6;
}

.bg-glow-right {
  right: -140px;
  top: 20px;
  width: 260px;
  height: 260px;
  background: #3b82f6;
}

.hero-shell,
.filter-card,
.table-card {
  position: relative;
  z-index: 1;
}

.hero-shell {
  margin-bottom: 16px;
  padding: 24px;
  border-radius: 20px;
  border: 1px solid rgba(17, 94, 89, 0.24);
  background:
    radial-gradient(circle at 15% 0%, rgba(170, 242, 225, 0.35) 0%, rgba(170, 242, 225, 0) 42%),
    linear-gradient(130deg, #0b5a72 0%, #0e7490 45%, #155e75 100%);
  box-shadow: 0 18px 36px -20px rgba(8, 52, 65, 0.6);
}

.hero-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.hero-shell h1 {
  margin: 0;
  font-size: 42px;
  line-height: 1;
  letter-spacing: -0.02em;
  color: #ffffff;
}

.hero-shell p {
  margin: 10px 0 0;
  color: rgba(236, 246, 255, 0.9);
  font-size: 15px;
  line-height: 1.55;
}

.metrics-grid {
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.metric-card {
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid transparent;
}

.metric-card-blue {
  background: rgba(211, 233, 255, 0.9);
  border-color: rgba(211, 233, 255, 0.9);
}

.metric-card-green {
  background: rgba(210, 243, 225, 0.92);
  border-color: rgba(210, 243, 225, 0.95);
}

.metric-card-emerald {
  background: rgba(211, 246, 225, 0.92);
  border-color: rgba(211, 246, 225, 0.95);
}

.metric-card-indigo {
  background: rgba(224, 231, 255, 0.92);
  border-color: rgba(224, 231, 255, 0.95);
}

.metric-label {
  display: block;
  font-size: 12px;
  color: #2a4567;
  margin-bottom: 6px;
}

.metric-card strong {
  font-size: 30px;
  line-height: 1;
  color: #102138;
}

.filter-card {
  margin-bottom: 14px;
  border-radius: 18px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  border: 1px solid #dce8f8;
  box-shadow: 0 12px 30px -24px rgba(24, 65, 120, 0.4);
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.filter-header h3 {
  margin: 0;
  font-size: 18px;
  color: #142945;
}

.filter-header p {
  margin: 5px 0 0;
  font-size: 13px;
  color: #637995;
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr)) auto;
  gap: 12px;
}

.action-item {
  align-self: end;
}

.table-card {
  border-radius: 20px;
  border: 1px solid #d5e5fa;
  background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%);
  box-shadow: 0 16px 34px -24px rgba(15, 65, 120, 0.45);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
}

.table-title {
  display: block;
  font-size: 18px;
  font-weight: 800;
  color: #15273f;
}

.table-subtitle {
  margin: 4px 0 0;
  font-size: 12px;
  color: #6b7f98;
}

.table-meta {
  margin-top: 2px;
  font-size: 13px;
  font-weight: 600;
  color: #3f628f;
}

.pager-wrap {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

@media (max-width: 1180px) {
  .filter-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 760px) {
  .submission-page {
    padding: 12px 12px 20px;
  }

  .hero-shell {
    padding: 16px;
  }

  .hero-shell h1 {
    font-size: 34px;
  }

  .metrics-grid,
  .filter-grid {
    grid-template-columns: 1fr;
  }

  .table-header {
    flex-direction: column;
  }

  .table-meta {
    margin-top: 0;
  }
}
</style>
