<script setup>
import { computed, h, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { NTag } from 'naive-ui';
import router from '@/router';
import Axios from '@/plugins/axios';
import store from '@/store';
import { AddOutline, LayersOutline, SparklesOutline } from '@vicons/ionicons5';
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

const difficultyMeta = value => {
  const level = Number(value || 0);
  if (level <= 0) return { label: '未设定', type: 'default' };
  if (level <= 3) return { label: `L${level}`, type: 'success' };
  if (level <= 7) return { label: `L${level}`, type: 'warning' };
  return { label: `L${level}`, type: 'error' };
};

const currentTypeLabel = computed(() => {
  const item = typeOptions.find(x => x.value === search.value.question_type);
  return item?.label || '全部';
});

const totalPages = computed(() => Math.max(1, Math.ceil(pagination.value.count / pagination.value.pageSize || 1)));

const columns = computed(() => {
  const startIndex = (pagination.value.page - 1) * pagination.value.pageSize;
  const baseColumns = [
    {
      title: '序号',
      key: 'display_index',
      width: 84,
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
          class: 'subject-link',
          title: summarizeContent(row.content) || row.title || '',
        },
        summarizeContent(row.content) || row.title || ''
      ),
    },
    {
      title: '题型',
      key: 'question_type',
      width: 118,
      render: row => h(
        NTag,
        { size: 'small', type: row.question_type === 'multiple' ? 'warning' : row.question_type === 'judge' ? 'info' : 'success', bordered: false },
        { default: () => typeLabelMap[row.question_type] || row.question_type }
      ),
    },
    {
      title: '难度',
      key: 'difficulty',
      width: 106,
      render: row => {
        const meta = difficultyMeta(row.difficulty);
        return h(NTag, { size: 'small', type: meta.type, bordered: false }, { default: () => meta.label });
      },
    },
    {
      title: '通过',
      key: 'accepted_count',
      width: 96,
      render: row => h('span', { class: 'num-cell' }, row.accepted_count ?? 0),
    },
    {
      title: '提交',
      key: 'submission_count',
      width: 96,
      render: row => h('span', { class: 'num-cell' }, row.submission_count ?? 0),
    },
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
          class: 'edit-link',
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
  <n-layout class="objective-list-page">
    <section class="hero-panel">
      <div>
        <n-space align="center" size="small" class="hero-badge-row">
          <n-icon :component="SparklesOutline" />
          智能题库管理
        </n-space>
        <h1 class="hero-title">客观题</h1>
        <p class="hero-subtitle">支持单选/多选/判断题批量维护，移动端也可快速筛选与管理。</p>
      </div>
      <n-space class="hero-actions" wrap>
        <n-button @click="router.push({ name: 'objective_paper_list' })">
          <template #icon><n-icon :component="LayersOutline" /></template>
          查看套卷
        </n-button>
        <n-button v-if="canManage" type="primary" @click="router.push({ name: 'objective_create' })">
          <template #icon><n-icon :component="AddOutline" /></template>
          创建客观题
        </n-button>
        <n-button v-if="canManage" type="success" @click="router.push({ name: 'objective_paper_create' })">
          <template #icon><n-icon :component="LayersOutline" /></template>
          一次创建套卷
        </n-button>
      </n-space>
    </section>

    <n-card :bordered="false" class="filter-card">
      <n-form inline class="filter-form">
        <n-form-item label="题目ID/名称" class="filter-item">
          <n-input
            v-model:value="search.search"
            placeholder="例如：位运算 / 123"
            @keydown.enter="writeSearchToQuery"
          />
        </n-form-item>
        <n-form-item label="题型" class="filter-item type-item">
          <n-select
            v-model:value="search.question_type"
            :options="typeOptions"
            placeholder="全部题型"
          />
        </n-form-item>
        <n-form-item>
          <n-button type="primary" class="search-btn" @click="writeSearchToQuery">搜索</n-button>
        </n-form-item>
      </n-form>

      <n-space class="filter-meta" size="small" wrap>
        <n-tag :bordered="false" type="info">筛选：{{ currentTypeLabel }}</n-tag>
        <n-tag :bordered="false" type="success">本页 {{ data.length }} 题</n-tag>
        <n-tag :bordered="false">总计 {{ pagination.count }} 题</n-tag>
      </n-space>
    </n-card>

    <n-card :bordered="false" class="table-card">
      <template #header>题目列表</template>
      <template #header-extra>
        <n-tag :bordered="false" type="info">第 {{ pagination.page }} / {{ totalPages }} 页</n-tag>
      </template>
      <n-data-table
        class="objective-table"
        :columns="columns"
        :data="data"
        :loading="loading"
        :bordered="false"
        striped
      />
    </n-card>

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
  </n-layout>
</template>

<style scoped>
.objective-list-page {
  --panel-border: #dfe9f7;
  --panel-shadow: 0 12px 28px rgba(22, 78, 163, 0.08);
  width: 100%;
  max-width: 1300px;
  margin: 0 auto;
  padding: 14px 10px 24px;
}

.hero-panel {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 22px;
  border-radius: 20px;
  border: 1px solid var(--panel-border);
  background:
    radial-gradient(100% 120% at 100% 0%, rgba(59, 130, 246, 0.22) 0%, rgba(255, 255, 255, 0) 48%),
    radial-gradient(100% 120% at 0% 100%, rgba(16, 185, 129, 0.17) 0%, rgba(255, 255, 255, 0) 45%),
    linear-gradient(180deg, #f6fbff 0%, #ffffff 100%);
  box-shadow: var(--panel-shadow);
}

.hero-badge-row {
  color: #2563eb;
  font-weight: 700;
  font-size: 13px;
  margin-bottom: 6px;
}

.hero-title {
  margin: 0;
  font-size: 42px;
  line-height: 1.06;
  letter-spacing: 0.5px;
  color: #1e2f43;
}

.hero-subtitle {
  margin: 10px 0 0;
  color: #5a7088;
  font-size: 14px;
}

.hero-actions {
  align-content: flex-start;
}

.hero-actions :deep(.n-button) {
  border-radius: 11px;
  font-weight: 600;
}

.filter-card,
.table-card {
  margin-top: 14px;
  border: 1px solid var(--panel-border);
  border-radius: 18px;
  box-shadow: var(--panel-shadow);
}

.filter-form {
  gap: 8px 12px;
}

.filter-item {
  min-width: 220px;
}

.type-item {
  min-width: 160px;
}

.search-btn {
  min-width: 100px;
  border-radius: 10px;
  font-weight: 600;
}

.filter-meta {
  margin-top: 10px;
}

.table-card :deep(.n-card-header) {
  border-bottom: 1px solid #edf3fb;
}

.table-card :deep(.n-card-header__main) {
  font-weight: 700;
  color: #27405c;
}

.objective-table :deep(th) {
  font-weight: 700;
  color: #2b4663;
}

.objective-table :deep(.n-data-table-td) {
  border-color: #edf2f8;
}

.objective-table :deep(.n-data-table-tr:hover .n-data-table-td) {
  background: #f7fbff;
}

:deep(.subject-link) {
  color: #1f4cc9;
  text-decoration: none;
  font-weight: 700;
  display: inline-block;
  max-width: 520px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.subject-link:hover) {
  color: #163ca5;
}

:deep(.num-cell) {
  font-variant-numeric: tabular-nums;
  font-weight: 700;
  color: #2a3f59;
}

:deep(.edit-link) {
  color: #0f766e;
  text-decoration: none;
  font-weight: 700;
}

:deep(.edit-link:hover) {
  color: #0b5c56;
}

.pagination-wrap {
  margin-top: 14px;
  padding: 12px 10px;
  border-radius: 14px;
  border: 1px solid #e3ecf9;
  background: #fff;
  display: flex;
  justify-content: center;
}

@media (max-width: 900px) {
  .objective-list-page {
    padding: 8px 4px 16px;
  }

  .hero-panel {
    flex-direction: column;
    border-radius: 16px;
    padding: 14px;
  }

  .hero-title {
    font-size: 34px;
  }

  .hero-subtitle {
    line-height: 1.6;
  }

  .hero-actions {
    width: 100%;
  }

  .hero-actions :deep(.n-button) {
    width: 100%;
  }

  .filter-form {
    width: 100%;
  }

  .filter-item,
  .type-item {
    width: 100%;
    min-width: 0;
  }

  .filter-item :deep(.n-input),
  .filter-item :deep(.n-select),
  .type-item :deep(.n-input),
  .type-item :deep(.n-select),
  .search-btn {
    width: 100%;
  }

  .pagination-wrap {
    justify-content: flex-start;
    overflow-x: auto;
  }
}
</style>
