<script setup>
import JSZip from 'jszip';
import { computed, h, onBeforeUnmount, ref, watch, resolveComponent } from 'vue';
import Axios from '@/plugins/axios';

const message = useMessage();

const contestId = ref('');
const studentMatch = ref('student_id');
const useProblemIdDir = ref(false);
const freopenPolicy = ref('ignore');

const selectedZipFile = ref(null);
const zipProblemDirs = ref([]);
const mappingRows = ref([]);

const contestProblems = ref([]);
const loadingContestProblems = ref(false);

const uploading = ref(false);
const uploadRef = ref(null);

const created = ref([]);
const errors = ref([]);

const submissionDetailMap = ref({});

const polling = ref(false);
let pollTimer = null;

const canUpload = computed(() => {
  if (!contestId.value) return false;
  return true;
});

const resetResult = () => {
  created.value = [];
  errors.value = [];
  submissionDetailMap.value = {};
};

const buildProblemDirsFromZip = async (zipFile) => {
  try {
    const zip = await new JSZip().loadAsync(zipFile);
    const keys = new Set();
    for (const name of Object.keys(zip.files)) {
      if (!name || name.endsWith('/')) continue;
      const parts = name.split('/').filter(Boolean);
      if (parts.length < 2) continue;
      keys.add(parts[1]);
    }
    const list = Array.from(keys).sort();
    if (!list.length) return null;
    return list;
  } catch (e) {
    return null;
  }
};

const problemOptions = computed(() => {
  return (contestProblems.value || []).map(p => ({
    label: `${p.id} - ${p.title}`,
    value: p.id,
  }));
});

const mergeMappingRows = (dirs) => {
  const current = new Map(mappingRows.value.map(r => [r.dir, r]));
  const merged = [];
  for (const dir of dirs) {
    const existing = current.get(dir);
    merged.push(existing || { dir, problemId: null });
  }
  mappingRows.value = merged;
};

const canStartUpload = computed(() => {
  if (!contestId.value) return false;
  if (!selectedZipFile.value) return false;
  if (useProblemIdDir.value) return true;
  if (!mappingRows.value.length) return false;
  return mappingRows.value.every(r => Number.isInteger(r.problemId) && r.problemId > 0);
});

const buildProblemMapObject = () => {
  const obj = {};
  for (const r of mappingRows.value) {
    obj[r.dir] = r.problemId;
  }
  return obj;
};

const fetchContestProblems = async (id) => {
  if (!id) return;
  loadingContestProblems.value = true;
  try {
    const res = await Axios.get(`/contest/${id}/`);
    contestProblems.value = res?.problems || [];
  } catch (e) {
    contestProblems.value = [];
  } finally {
    loadingContestProblems.value = false;
  }
};

watch(
  () => contestId.value,
  (v) => {
    contestProblems.value = [];
    if (!v) return;
    fetchContestProblems(v);
  }
);

const fetchSubmissionDetail = async submissionId => {
  const id = String(submissionId);
  try {
    const data = await Axios.get(`/submission/${id}/`);
    submissionDetailMap.value[id] = data;
  } catch (e) {
    // ignore
  }
};

const isJudgingStatus = s => {
  // -4 pending, -3 judging
  return s === -4 || s === -3;
};

const refreshAll = async () => {
  const ids = created.value.map(i => i.submission_id);
  for (const id of ids) {
    await fetchSubmissionDetail(id);
  }
};

const startPolling = () => {
  if (polling.value) return;
  polling.value = true;
  pollTimer = setInterval(async () => {
    const ids = created.value.map(i => i.submission_id);
    if (!ids.length) return;

    let anyJudging = false;
    for (const id of ids) {
      const detail = submissionDetailMap.value[String(id)];
      if (!detail) {
        anyJudging = true;
        continue;
      }
      if (isJudgingStatus(detail.status)) {
        anyJudging = true;
      }
    }

    await refreshAll();

    if (!anyJudging) {
      stopPolling();
    }
  }, 2000);
};

const stopPolling = () => {
  polling.value = false;
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
};

onBeforeUnmount(() => {
  stopPolling();
});

const onZipChange = async ({ file }) => {
  const raw = file?.file;
  if (!raw) return;
  if (!raw.name?.toLowerCase().endsWith('.zip')) {
    message.error('请上传 .zip 文件');
    return;
  }
  if (!contestId.value) {
    message.error('请先填写比赛ID');
    setTimeout(() => {
      uploadRef.value?.clear?.();
    });
    return;
  }

  selectedZipFile.value = raw;
  const dirs = await buildProblemDirsFromZip(raw);
  if (!dirs) {
    message.error('无法从 zip 解析题目目录');
    return;
  }
  zipProblemDirs.value = dirs;
  if (!useProblemIdDir.value) {
    mergeMappingRows(dirs);
    message.info('已从 zip 解析题目目录，请为每个目录选择对应题目ID，然后点击“开始上传评测”');
  } else {
    message.info('已选择 zip，可直接点击“开始上传评测”');
  }
};

const startUpload = async () => {
  if (!canStartUpload.value) return;
  const raw = selectedZipFile.value;
  if (!raw) return;

  uploading.value = true;
  stopPolling();
  resetResult();

  try {
    const fd = new FormData();
    fd.append('file', raw);
    if (!useProblemIdDir.value) {
      fd.append('problem_map', JSON.stringify(buildProblemMapObject()));
    }
    fd.append('student_match', studentMatch.value);
    fd.append('freopen_policy', freopenPolicy.value);

    const res = await Axios.post(`/contest/${contestId.value}/batch-upload-submissions/`, fd, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    created.value = res.created || [];
    errors.value = res.errors || [];

    for (const item of created.value) {
      await fetchSubmissionDetail(item.submission_id);
    }

    if (created.value.length) {
      startPolling();
    }

    message.success('已创建提交并开始评测');
  } catch (e) {
    // error handled by interceptor
  } finally {
    uploading.value = false;
  }
};

const createdTableData = computed(() => {
  return created.value.map(i => {
    const detail = submissionDetailMap.value[String(i.submission_id)];
    return {
      ...i,
      status: detail?.status,
      score: detail?.score,
      language: detail?.language,
    };
  });
});

const statusText = status => {
  const mapping = {
    [-4]: 'pending',
    [-3]: 'judging',
    [-2]: 'compile error',
    [-1]: 'wrong answer',
    [0]: 'accepted',
    [1]: 'time limit exceeded',
    [2]: 'memory limit exceeded',
    [3]: 'runtime error',
    [4]: 'system error',
  };
  if (status === undefined || status === null) return '-';
  return mapping[status] ?? String(status);
};

const exportCsv = () => {
  const rows = createdTableData.value;
  if (!rows.length) {
    message.error('没有可导出的数据');
    return;
  }

  const headers = ['path', 'student', 'user_id', 'problem_id', 'submission_id', 'status', 'score', 'language'];
  const escape = v => {
    const s = v === undefined || v === null ? '' : String(v);
    if (/[",\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
    return s;
  };

  const lines = [headers.join(',')];
  for (const r of rows) {
    lines.push(headers.map(h => escape(r[h])).join(','));
  }

  const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `contest-${contestId.value || 'unknown'}-batch-result.csv`;
  a.click();
  URL.revokeObjectURL(url);
};

const createdColumns = [
  { title: '文件路径', key: 'path', ellipsis: { tooltip: true } },
  { title: '考号', key: 'student', width: 120 },
  { title: '题目ID', key: 'problem_id', width: 90 },
  { title: '提交ID', key: 'submission_id', width: 90 },
  {
    title: '状态',
    key: 'status',
    width: 140,
    render: row => statusText(row.status),
  },
  { title: '分数', key: 'score', width: 80 },
  { title: '语言', key: 'language', width: 100 },
];

const errorColumns = [
  { title: '文件路径', key: 'path', ellipsis: { tooltip: true } },
  { title: '错误', key: 'error', ellipsis: { tooltip: true } },
];

const mappingColumns = computed(() => {
  const NSelect = resolveComponent('n-select');
  const NInputNumber = resolveComponent('n-input-number');
  return [
    { title: '题目目录', key: 'dir', ellipsis: { tooltip: true } },
    {
      title: '题目ID',
      key: 'problemId',
      render: (row) => {
        if (problemOptions.value.length) {
          return h(NSelect, {
            value: row.problemId,
            options: problemOptions.value,
            filterable: true,
            clearable: true,
            placeholder: '选择题目',
            style: 'width: 260px',
            'onUpdate:value': (v) => {
              row.problemId = v;
            },
          });
        }
        return h(NInputNumber, {
          value: row.problemId,
          min: 1,
          placeholder: '题目ID',
          style: 'width: 260px',
          'onUpdate:value': (v) => {
            row.problemId = v;
          },
        });
      },
    },
  ];
});
</script>

<template>
  <n-card>
    <n-space vertical>
      <div style="font-size: 18px; font-weight: 600">比赛批量上传评测</div>

      <n-alert type="info" :bordered="false">
        zip 目录结构：考号/题目目录/代码文件（.c/.cpp/.cc/.cxx/.py）。
        推荐直接使用题目ID作为题目目录：考号/题目ID/代码文件。
      </n-alert>

      <n-space align="center" :wrap="true">
        <n-input v-model:value="contestId" placeholder="比赛ID (contest_id)" style="width: 220px" />
        <n-select
          v-model:value="studentMatch"
          style="width: 220px"
          :options="[
            { label: '按 student_id(学号/考号) 匹配用户', value: 'student_id' },
            { label: '按 username 匹配用户', value: 'username' },
          ]"
        />
        <n-switch v-model:value="useProblemIdDir">
          <template #checked>目录即题目ID</template>
          <template #unchecked>目录->题目ID映射</template>
        </n-switch>
        <n-select
          v-model:value="freopenPolicy"
          style="width: 220px"
          :options="[
            { label: 'freopen：忽略（自动去除并评测）', value: 'ignore' },
            { label: 'freopen：必须包含（没有则直接RE）', value: 'require' },
            { label: 'freopen：禁止包含（有则直接RE）', value: 'forbid' },
            { label: 'freopen：保留（按原样评测）', value: 'keep' },
          ]"
        />
        <n-button :disabled="!created.length" @click="refreshAll" :loading="uploading">
          刷新结果
        </n-button>
        <n-button :disabled="!created.length" @click="exportCsv">导出 CSV</n-button>
        <n-button v-if="polling" @click="stopPolling">停止轮询</n-button>
        <n-button v-else :disabled="!created.length" @click="startPolling">开始轮询</n-button>
      </n-space>

      <n-card size="small" title="题目目录映射" v-if="!useProblemIdDir">
        <n-space vertical>
          <n-alert type="info" :bordered="false">
            先选择 zip，系统会自动识别题目目录并生成映射表。你只需要为每个目录选择对应的题目ID。
          </n-alert>
          <n-spin :show="loadingContestProblems">
            <n-text depth="3">比赛题目数量：{{ contestProblems.length }}</n-text>
          </n-spin>
          <n-data-table
            v-if="mappingRows.length"
            :columns="mappingColumns"
            :data="mappingRows"
            :pagination="{ pageSize: 20 }"
            :bordered="false"
          />
          <n-empty v-else description="请先选择 zip 文件" />
        </n-space>
      </n-card>

      <n-card size="small" title="上传 zip 并创建提交">
        <n-space vertical>
          <n-upload
            ref="uploadRef"
            :max="1"
            accept="application/zip"
            :default-upload="false"
            :disabled="uploading"
            @change="onZipChange"
          >
            <n-button type="primary" :disabled="!canUpload" :loading="uploading">选择 zip</n-button>
          </n-upload>

          <n-button
            type="primary"
            :disabled="!canStartUpload"
            :loading="uploading"
            @click="startUpload"
          >
            开始上传评测
          </n-button>
        </n-space>
      </n-card>

      <n-divider />

      <n-card size="small" title="创建结果">
        <n-space vertical>
          <n-text depth="3">已创建：{{ created.length }}，失败：{{ errors.length }}</n-text>
          <n-data-table
            v-if="created.length"
            :columns="createdColumns"
            :data="createdTableData"
            :pagination="{ pageSize: 20 }"
            :bordered="false"
            :scroll-x="900"
          />
          <n-empty v-else description="暂无创建记录" />
        </n-space>
      </n-card>

      <n-card size="small" title="失败列表" v-if="errors.length">
        <n-data-table
          :columns="errorColumns"
          :data="errors"
          :pagination="{ pageSize: 20 }"
          :bordered="false"
        />
      </n-card>
    </n-space>
  </n-card>
</template>
