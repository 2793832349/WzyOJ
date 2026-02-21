<script setup>
import { computed, h, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import router from '@/router';
import Axios from '@/plugins/axios';
import store from '@/store';
import { AddOutline, BookOutline, SearchOutline } from '@vicons/ionicons5';
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

const totalPages = computed(() => {
  const count = Number(pagination.value.count || 0);
  const pageSize = Number(pagination.value.pageSize || 20);
  return Math.max(1, Math.ceil(count / pageSize));
});

const writeSearchToQuery = _writeSearchToQuery(search.value, pagination.value, route);

const formatTime = value => {
  if (!value) return '-';
  try {
    return new Date(value).toLocaleString();
  } catch (_) {
    return value;
  }
};

const columns = [
  {
    title: 'ID',
    key: 'id',
    width: 90,
    render: row => h('span', { class: 'id-pill' }, `#${row.id}`),
  },
  {
    title: '套卷标题',
    key: 'title',
    minWidth: 280,
    render: row =>
      h(
        'a',
        {
          href: 'javascript:void(0)',
          onClick: () => router.push({ name: 'objective_paper_detail', params: { id: row.id } }),
          class: 'subject-link',
        },
        row.title
      ),
  },
  {
    title: '题目数',
    key: 'question_count',
    width: 100,
    render: row => h('span', { class: 'num-cell' }, row.question_count || 0),
  },
  {
    title: '总分',
    key: 'total_score',
    width: 100,
    render: row => h('span', { class: 'num-cell score-main' }, row.total_score || 0),
  },
  {
    title: '及格分',
    key: 'pass_score',
    width: 100,
    render: row => h('span', { class: 'num-cell score-pass' }, row.pass_score || 0),
  },
  {
    title: '更新时间',
    key: 'update_time',
    width: 190,
    render: row => h('span', { class: 'time-cell' }, formatTime(row.update_time)),
  },
  {
    title: '操作',
    key: 'actions',
    width: 110,
    render: row =>
      h(
        'a',
        {
          href: 'javascript:void(0)',
          class: 'action-link',
          onClick: () => router.push({ name: 'objective_paper_detail', params: { id: row.id } }),
        },
        '进入套卷'
      ),
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
  <n-layout class="paper-page">
    <section class="hero-panel">
      <div class="hero-main">
        <n-tag size="small" :bordered="false" type="info" round>
          <template #icon>
            <n-icon :component="BookOutline" />
          </template>
          客观题
        </n-tag>
        <h1>客观题套卷</h1>
        <p>按套训练更接近真实考试流程，支持整卷答题、统一判分与讲评复盘。</p>
      </div>

      <div class="hero-actions">
        <n-button quaternary @click="router.push({ name: 'objective_list' })">返回客观题</n-button>
        <router-link :to="{ name: 'objective_paper_create' }" v-if="canManage">
          <n-button type="primary" class="create-btn">
            <template #icon>
              <n-icon :component="AddOutline" />
            </template>
            一次创建套卷
          </n-button>
        </router-link>
      </div>
    </section>

    <n-card class="filter-card" :bordered="false">
      <div class="filter-row">
        <n-form inline>
          <n-form-item label="套卷ID/名称">
            <n-input
              v-model:value="search.search"
              placeholder="输入关键词"
              clearable
              @keydown.enter="writeSearchToQuery"
            />
          </n-form-item>
          <n-form-item>
            <n-button type="primary" @click="writeSearchToQuery">
              <template #icon>
                <n-icon :component="SearchOutline" />
              </template>
              搜索
            </n-button>
          </n-form-item>
        </n-form>

        <div class="meta-tags">
          <n-tag round :bordered="false" type="success">当前第 {{ pagination.page }} / {{ totalPages }} 页</n-tag>
          <n-tag round :bordered="false" type="info">共 {{ pagination.count }} 套</n-tag>
        </div>
      </div>
    </n-card>

    <n-card class="table-card" :bordered="false">
      <template #header>套卷列表</template>
      <template #header-extra>
        <span class="header-extra">按更新时间自动排序</span>
      </template>

      <n-data-table
        :columns="columns"
        :data="data"
        :loading="loading"
        :bordered="false"
        striped
        class="paper-table"
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
  </n-layout>
</template>

<style scoped>
.paper-page {
  --hero-bg-start: #edf4ff;
  --hero-bg-end: #f8fbff;
  --hero-border: #d9e6ff;
  --primary-text: #1e3a8a;
  --muted-text: #5b6b88;
  --surface-bg: #ffffff;
  --surface-border: #e7edf7;
  --table-head-bg: #f2f7ff;

  display: flex;
  flex-direction: column;
  gap: 16px;
}

.hero-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 24px;
  border-radius: 18px;
  border: 1px solid var(--hero-border);
  background: linear-gradient(135deg, var(--hero-bg-start), var(--hero-bg-end));
}

.hero-main h1 {
  margin: 10px 0 6px;
  font-size: 34px;
  line-height: 1.15;
  color: #1f2e4d;
  letter-spacing: 0.3px;
}

.hero-main p {
  margin: 0;
  color: var(--muted-text);
  font-size: 14px;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.create-btn {
  box-shadow: 0 10px 20px rgba(32, 119, 255, 0.2);
}

.filter-card,
.table-card {
  border-radius: 16px;
  border: 1px solid var(--surface-border);
  background: var(--surface-bg);
}

.filter-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.meta-tags {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-extra {
  font-size: 12px;
  color: #7b8eaf;
}

.paper-table :deep(.n-data-table-th) {
  background: var(--table-head-bg) !important;
  color: var(--primary-text) !important;
  font-weight: 700 !important;
}

.subject-link {
  color: #1f4bc7;
  font-weight: 700;
  text-decoration: none;
}

.subject-link:hover {
  color: #1740ad;
  text-decoration: underline;
}

.id-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 48px;
  padding: 4px 10px;
  border-radius: 999px;
  background: #eef4ff;
  border: 1px solid #d3e3ff;
  color: #3159ad;
  font-weight: 700;
}

.num-cell {
  font-weight: 700;
  color: #2f3f5a;
}

.score-main {
  color: #1d4ed8;
}

.score-pass {
  color: #059669;
}

.time-cell {
  color: #677b9f;
  font-size: 13px;
}

.action-link {
  color: #0f8d55;
  font-weight: 700;
  text-decoration: none;
}

.action-link:hover {
  color: #0a6f43;
  text-decoration: underline;
}

.pager-wrap {
  margin-top: 18px;
  display: flex;
  justify-content: center;
}

@media (max-width: 900px) {
  .hero-panel {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-main h1 {
    font-size: 28px;
  }

  .hero-actions {
    width: 100%;
    display: grid;
    grid-template-columns: 1fr;
  }

  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }

  .meta-tags {
    width: 100%;
    justify-content: space-between;
  }

  .pager-wrap {
    overflow-x: auto;
    justify-content: flex-start;
  }
}
</style>
