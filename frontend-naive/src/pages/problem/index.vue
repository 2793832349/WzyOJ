<script setup>
import { computed, ref, watch } from 'vue';
import Axios from '@/plugins/axios';

import store from '@/store';
import { difficultyOptions } from '@/plugins/consts';
import ProblemTable from '@/components/ProblemTable.vue';
import { useRoute } from 'vue-router';
import { BookmarksOutline, AddOutline, SearchOutline, CloudUploadOutline } from '@vicons/ionicons5';
import { _writeSearchToQuery } from '@/plugins/utils';

const route = useRoute();

const tagsOptions = ref([]);

Axios.get('/problem/tag/').then(res => {
  tagsOptions.value = res.map(item => ({
    label: item.name,
    value: item.id,
  }));
});

const pagination = ref({ pageSize: 20, page: 1, count: 0 });
const search = ref({
  search: '',
  difficulty: null,
  tags: [],
});
const data = ref([]);
const loading = ref(false);

const writeSearchToQuery = _writeSearchToQuery(search.value, pagination.value, route);

const canManageProblem = computed(() => {
  return store.state.user.permissions.includes('problem');
});

const hasActiveFilter = computed(() => {
  return !!search.value.search || search.value.tags.length > 0 || search.value.difficulty !== null;
});

const pageSolvedCount = computed(() => {
  return data.value.filter(item => item.solved).length;
});

const pageAccepted = computed(() => {
  return data.value.reduce((sum, item) => sum + Number(item.accepted_count || 0), 0);
});

const pageSubmissions = computed(() => {
  return data.value.reduce((sum, item) => sum + Number(item.submission_count || 0), 0);
});

const hydroImportModalVisible = ref(false);
const hydroImportFileList = ref([]);
const hydroImportLoading = ref(false);

const hojImportModalVisible = ref(false);
const hojImportFileList = ref([]);
const hojImportLoading = ref(false);

const closeHydroImportModal = () => {
  if (hydroImportLoading.value) return;
  hydroImportModalVisible.value = false;
};

const handleHydroImport = async () => {
  const fileInfo = hydroImportFileList.value[0];
  const rawFile = fileInfo?.file;
  const uploadFile = rawFile?.file || rawFile;
  if (!uploadFile) {
    window.$message.warning('请先选择 Hydro 导出 zip 文件');
    return;
  }

  hydroImportLoading.value = true;
  try {
    const formData = new FormData();
    formData.append('file', uploadFile);

    const res = await Axios.post('/problem/import-hydro/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    const successCount = Number(res?.imported_count || 0);
    const failedCount = Number(res?.failed_count || 0);
    if (failedCount > 0) {
      const firstFailed = Array.isArray(res?.failed) ? res.failed[0] : null;
      const tip = firstFailed
        ? `，首个失败：${firstFailed.root || '-'} ${firstFailed.error || ''}`
        : '';
      window.$message.warning(`导入完成：成功 ${successCount}，失败 ${failedCount}${tip}`);
    } else {
      window.$message.success(`导入完成：成功 ${successCount} 题`);
    }

    if (successCount > 0) {
      hydroImportModalVisible.value = false;
      hydroImportFileList.value = [];
      handleQueryChange();
    }
  } finally {
    hydroImportLoading.value = false;
  }
};

const closeHojImportModal = () => {
  if (hojImportLoading.value) return;
  hojImportModalVisible.value = false;
};

const handleHojImport = async () => {
  const fileInfo = hojImportFileList.value[0];
  const rawFile = fileInfo?.file;
  const uploadFile = rawFile?.file || rawFile;
  if (!uploadFile) {
    window.$message.warning('请先选择 HOJ 导出 zip 文件');
    return;
  }

  hojImportLoading.value = true;
  try {
    const formData = new FormData();
    formData.append('file', uploadFile);

    const res = await Axios.post('/problem/import-hoj/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    const successCount = Number(res?.imported_count || 0);
    const failedCount = Number(res?.failed_count || 0);
    if (failedCount > 0) {
      const firstFailed = Array.isArray(res?.failed) ? res.failed[0] : null;
      const tip = firstFailed
        ? `，首个失败：${firstFailed.root || '-'} ${firstFailed.error || ''}`
        : '';
      window.$message.warning(`导入完成：成功 ${successCount}，失败 ${failedCount}${tip}`);
    } else {
      window.$message.success(`导入完成：成功 ${successCount} 题`);
    }

    if (successCount > 0) {
      hojImportModalVisible.value = false;
      hojImportFileList.value = [];
      handleQueryChange();
    }
  } finally {
    hojImportLoading.value = false;
  }
};

const handleQueryChange = () => {
  if (route.name !== 'problem_list') return;

  search.value.search = route.query.search || '';
  search.value.difficulty =
    (route.query.difficulty && parseInt(route.query.difficulty)) || null;

  const tags = [];
  if (route.query.tags) {
    for (const tag of route.query.tags.split(',')) {
      tags.push(parseInt(tag));
    }
  }
  search.value.tags = tags;

  for (const key in pagination.value) {
    if (route.query[key]) pagination.value[key] = parseInt(route.query[key]);
  }

  loading.value = true;
  Axios.get('/problem/', {
    params: {
      limit: pagination.value.pageSize,
      offset: (pagination.value.page - 1) * pagination.value.pageSize,
      search: search.value.search,
      difficulty: search.value.difficulty,
      tags: search.value.tags.join(','),
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
  <div class="problem-list-page">
    <div class="bg-glow bg-glow-left" />
    <div class="bg-glow bg-glow-right" />

    <section class="hero-shell">
      <div class="hero-grid">
        <div class="hero-main">
          <div class="hero-title-row">
            <h1>题目列表</h1>
            <n-tag v-if="hasActiveFilter" size="small" type="warning" :bordered="false">筛选中</n-tag>
          </div>
          <p>按难度、标签和关键词快速定位目标题，集中刷题并实时追踪通过表现。</p>

          <div class="hero-chips">
            <span class="hero-chip">累计提交 {{ pageSubmissions }}</span>
            <span class="hero-chip">累计通过 {{ pageAccepted }}</span>
            <span class="hero-chip">当前页 {{ data.length }} 题</span>
          </div>
        </div>

        <aside class="hero-side">
          <n-space v-if="canManageProblem" class="hero-actions" :size="10" wrap>
            <router-link :to="{ name: 'tag_edit' }">
              <n-button secondary>
                <template #icon>
                  <n-icon :component="BookmarksOutline" />
                </template>
                标签管理
              </n-button>
            </router-link>
            <n-button tertiary type="warning" @click="hydroImportModalVisible = true">
              <template #icon>
                <n-icon :component="CloudUploadOutline" />
              </template>
              导入 Hydro
            </n-button>
            <n-button tertiary type="info" @click="hojImportModalVisible = true">
              <template #icon>
                <n-icon :component="CloudUploadOutline" />
              </template>
              导入 HOJ
            </n-button>
            <router-link :to="{ name: 'problem_create' }">
              <n-button type="primary">
                <template #icon>
                  <n-icon :component="AddOutline" />
                </template>
                创建题目
              </n-button>
            </router-link>
          </n-space>
        </aside>
      </div>

      <div class="metrics-grid">
        <div class="metric-card metric-card-blue">
          <span class="metric-label">题目总数</span>
          <strong>{{ pagination.count }}</strong>
        </div>
        <div class="metric-card metric-card-green">
          <span class="metric-label">当前页已通过</span>
          <strong>{{ pageSolvedCount }}</strong>
        </div>
      </div>
    </section>

    <n-card class="filter-card" :bordered="false">
      <div class="filter-header">
        <div>
          <h3>筛选控制台</h3>
          <p>设置检索条件后点击搜索，分页与筛选会同步到地址栏。</p>
        </div>
      </div>

      <n-form label-placement="top">
        <div class="filter-grid">
          <n-form-item label="题目 ID / 名称">
            <n-input
              v-model:value="search.search"
              placeholder="输入关键词后回车"
              @keydown.enter="writeSearchToQuery"
            />
          </n-form-item>

          <n-form-item label="题目标签">
            <n-select
              v-model:value="search.tags"
              :options="tagsOptions"
              clearable
              filterable
              multiple
              placeholder="请选择标签"
              :max-tag-count="1"
              :disabled="!tagsOptions.length"
            />
          </n-form-item>

          <n-form-item label="题目难度">
            <n-select
              v-model:value="search.difficulty"
              :options="[{ label: '全部', value: null }].concat(difficultyOptions)"
              placeholder="请选择难度"
            />
          </n-form-item>

          <n-form-item label="操作" class="action-item">
            <n-space :size="10">
              <n-button type="primary" @click="writeSearchToQuery">
                <template #icon>
                  <n-icon :component="SearchOutline" />
                </template>
                搜索
              </n-button>
              <n-button
                v-if="hasActiveFilter"
                strong
                secondary
                @click="
                  () => {
                    search.search = '';
                    search.tags = [];
                    search.difficulty = null;
                    writeSearchToQuery();
                  }
                "
              >
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
            <span class="table-title">题目结果</span>
            <p class="table-subtitle">点击标题可进入详情，状态列可快速跳转提交记录。</p>
          </div>
          <span class="table-meta">第 {{ pagination.page }} / {{ Math.max(1, Math.ceil(pagination.count / pagination.pageSize)) }} 页</span>
        </div>
      </template>

      <ProblemTable :data="data" :loading="loading" />

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


    <n-modal
      v-model:show="hydroImportModalVisible"
      preset="card"
      title="导入 Hydro 题目"
      :mask-closable="!hydroImportLoading"
      style="width: min(92vw, 620px)"
      @after-leave="hydroImportFileList = []"
    >
      <n-space vertical :size="12">
        <n-alert type="info" :show-icon="false">
          支持 Hydro 导出 zip（单题或多题目录）。会自动创建题目并导入测试点（.in + .out/.ans）。
        </n-alert>

        <n-upload
          v-model:file-list="hydroImportFileList"
          :default-upload="false"
          :max="1"
          accept=".zip,application/zip"
        >
          <n-upload-dragger>
            <div style="font-size: 14px; color: #3f5878">点击或拖拽 Hydro zip 到这里</div>
          </n-upload-dragger>
        </n-upload>
      </n-space>

      <template #footer>
        <n-space justify="end">
          <n-button :disabled="hydroImportLoading" @click="closeHydroImportModal">取消</n-button>
          <n-button type="primary" :loading="hydroImportLoading" @click="handleHydroImport">
            开始导入
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <n-modal
      v-model:show="hojImportModalVisible"
      preset="card"
      title="导入 HOJ 题目"
      :mask-closable="!hojImportLoading"
      style="width: min(92vw, 620px)"
      @after-leave="hojImportFileList = []"
    >
      <n-space vertical :size="12">
        <n-alert type="info" :show-icon="false">
          支持 HOJ 导出 zip（包含 problem_*.json 与测试数据目录）。系统会解析 JSON 并导入测试点。
        </n-alert>

        <n-upload
          v-model:file-list="hojImportFileList"
          :default-upload="false"
          :max="1"
          accept=".zip,application/zip"
        >
          <n-upload-dragger>
            <div style="font-size: 14px; color: #3f5878">点击或拖拽 HOJ 导出 zip 到这里</div>
          </n-upload-dragger>
        </n-upload>
      </n-space>

      <template #footer>
        <n-space justify="end">
          <n-button :disabled="hojImportLoading" @click="closeHojImportModal">取消</n-button>
          <n-button type="primary" :loading="hojImportLoading" @click="handleHojImport">
            开始导入
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<style scoped>
.problem-list-page {
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
  opacity: 0.36;
  z-index: 0;
  pointer-events: none;
}

.bg-glow-left {
  left: -120px;
  top: 90px;
  width: 220px;
  height: 220px;
  background: #4cc2ff;
}

.bg-glow-right {
  right: -140px;
  top: 20px;
  width: 260px;
  height: 260px;
  background: #2d6cf5;
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
  border: 1px solid rgba(14, 92, 201, 0.25);
  background:
    radial-gradient(circle at 15% 0%, rgba(111, 197, 255, 0.45) 0%, rgba(111, 197, 255, 0) 40%),
    linear-gradient(130deg, #0f4586 0%, #0c62b6 42%, #1b7fce 100%);
  box-shadow: 0 18px 36px -20px rgba(10, 57, 110, 0.6);
}

.hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(240px, 1fr);
  gap: 16px;
}

.hero-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.hero-main h1 {
  margin: 0;
  font-size: 44px;
  line-height: 1;
  letter-spacing: -0.02em;
  color: #ffffff;
}

.hero-main p {
  margin: 10px 0 0;
  max-width: 680px;
  color: rgba(236, 246, 255, 0.9);
  font-size: 15px;
  line-height: 1.55;
}

.hero-chips {
  margin-top: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hero-chip {
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.16);
  border: 1px solid rgba(255, 255, 255, 0.26);
  color: #f4f9ff;
  font-size: 12px;
  font-weight: 600;
}

.hero-side {
  display: flex;
  justify-content: flex-end;
  align-items: flex-end;
}

.hero-actions {
  justify-content: flex-end;
}

.metrics-grid {
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.metric-card {
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid transparent;
  backdrop-filter: blur(2px);
}

.metric-card-blue {
  background: rgba(211, 233, 255, 0.86);
  border-color: rgba(211, 233, 255, 0.9);
}

.metric-card-green {
  background: rgba(210, 243, 225, 0.9);
  border-color: rgba(210, 243, 225, 0.95);
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
  grid-template-columns: 1.3fr 1fr 1fr auto;
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

.table-card :deep(.n-data-table) {
  border-radius: 14px;
  overflow: hidden;
}

.table-card :deep(.n-data-table-th) {
  background: linear-gradient(180deg, #ecf4ff 0%, #e5f0ff 100%);
  color: #16335b;
  font-weight: 700;
}

.table-card :deep(.n-data-table-td) {
  border-bottom-color: #e8eef7;
}

.table-card :deep(.n-data-table-tr:hover .n-data-table-td) {
  background: #eef6ff;
}

@media (max-width: 1180px) {
  .hero-grid {
    grid-template-columns: 1fr;
  }

  .hero-side {
    justify-content: flex-start;
  }

  .hero-actions {
    justify-content: flex-start;
  }

  .filter-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 760px) {
  .problem-list-page {
    padding: 12px 12px 20px;
  }

  .hero-shell {
    padding: 16px;
  }

  .hero-main h1 {
    font-size: 34px;
  }

  .metrics-grid,
  .filter-grid {
    grid-template-columns: 1fr;
  }
}
</style>
