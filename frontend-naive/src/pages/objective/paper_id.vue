<script setup>
import { computed, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import router from '@/router';
import Axios from '@/plugins/axios';
import MdEditor from '@/components/MdEditor.vue';
import store from '@/store';

const route = useRoute();
const message = useMessage();

const id = computed(() => route.params.id);
const loading = ref(false);
const submitting = ref(false);
const paper = ref({ items: [] });
const answers = ref({});
const result = ref(null);

const canManage = computed(() => {
  const perms = store.state.user?.permissions || [];
  return perms.includes('problem');
});

const typeLabelMap = {
  single: '单选题',
  multiple: '多选题',
  judge: '判断题',
};

const normalizeOptions = options => {
  const rows = Array.isArray(options) ? options : [];
  return rows.map(item => ({
    key: String(item?.key || '').trim().toUpperCase(),
    text: String(item?.text || ''),
  }));
};

const setAnswer = (questionId, value) => {
  answers.value[String(questionId)] = value;
};

const loadData = () => {
  if (!id.value) return;

  loading.value = true;
  result.value = null;
  answers.value = {};

  Axios.get(`/objective/paper/${id.value}/`)
    .then(res => {
      paper.value = {
        ...res,
        items: Array.isArray(res.items) ? res.items : [],
      };

      for (const item of paper.value.items) {
        const q = item.question || {};
        if (q.question_type === 'multiple') {
          answers.value[String(q.id)] = [];
        } else {
          answers.value[String(q.id)] = null;
        }
      }
    })
    .catch(() => {
      message.error('套卷不存在或你没有权限查看');
      router.push({ name: 'objective_paper_list' });
    })
    .finally(() => {
      loading.value = false;
    });
};

const buildSubmitPayload = () => {
  const payload = {};
  for (const item of paper.value.items || []) {
    const q = item.question || {};
    const key = String(q.id);
    const val = answers.value[key];
    if (q.question_type === 'multiple') {
      payload[key] = Array.isArray(val) ? val : [];
    } else {
      payload[key] = val ? [val] : [];
    }
  }
  return payload;
};

const submitPaper = () => {
  const payload = buildSubmitPayload();
  const unanswered = [];

  for (const [idx, item] of (paper.value.items || []).entries()) {
    const q = item.question || {};
    if (!(payload[String(q.id)] || []).length) {
      unanswered.push(`第${idx + 1}题`);
    }
  }

  if (unanswered.length) {
    message.warning(`还有 ${unanswered.length} 道题未作答`);
    return;
  }

  submitting.value = true;
  Axios.post(`/objective/paper/${id.value}/submit/`, { answers: payload })
    .then(res => {
      result.value = res;
      if (res.is_pass) {
        message.success(`提交成功，得分 ${res.total_score}/${res.max_score}`);
      } else {
        message.warning(`提交成功，得分 ${res.total_score}/${res.max_score}`);
      }
    })
    .finally(() => {
      submitting.value = false;
    });
};

watch(id, loadData, { immediate: true });
</script>

<template>
  <n-spin :show="loading">
    <n-space vertical size="large">
      <n-page-header @back="router.push({ name: 'objective_paper_list' })">
        <template #title>套卷 #{{ paper.id }}</template>
        <template #subtitle>{{ paper.title }}</template>
        <template #extra>
          <n-space>
            <n-tag :bordered="false" type="info">题目 {{ paper.question_count || (paper.items || []).length }}</n-tag>
            <n-tag :bordered="false" type="warning">总分 {{ paper.total_score || 0 }}</n-tag>
            <n-tag :bordered="false" type="success">及格 {{ paper.pass_score || 0 }}</n-tag>
            <n-button v-if="canManage" @click="router.push({ name: 'objective_paper_edit', params: { id: paper.id } })">编辑套卷</n-button>
            <n-button v-if="canManage" @click="router.push({ name: 'objective_paper_create' })">再建一套</n-button>
          </n-space>
        </template>
      </n-page-header>

      <n-card v-if="paper.description" title="套卷说明" :bordered="false">
        <MdEditor :content="paper.description" previewOnly />
      </n-card>

      <n-card
        v-for="(item, idx) in paper.items"
        :key="item.id"
        :title="`第 ${idx + 1} 题`"
        :bordered="false"
      >
        <n-space vertical style="width: 100%">
          <n-tag size="small" type="info" :bordered="false">
            {{ typeLabelMap[item.question?.question_type] || item.question?.question_type }} · {{ item.score }} 分
          </n-tag>

          <MdEditor :content="item.question?.content || ''" previewOnly />

          <n-radio-group
            v-if="item.question?.question_type !== 'multiple'"
            :value="answers[String(item.question?.id)]"
            @update:value="val => setAnswer(item.question?.id, val)"
          >
            <n-space vertical>
              <n-radio
                v-for="opt in normalizeOptions(item.question?.options)"
                :key="`${item.id}-${opt.key}`"
                :value="opt.key"
              >
                <div class="option-render">
                  <span class="option-key">{{ opt.key }}.</span>
                  <div class="option-content">
                    <MdEditor :content="opt.text || ''" previewOnly />
                  </div>
                </div>
              </n-radio>
            </n-space>
          </n-radio-group>

          <n-checkbox-group
            v-else
            :value="answers[String(item.question?.id)]"
            @update:value="val => setAnswer(item.question?.id, val)"
          >
            <n-space vertical>
              <n-checkbox
                v-for="opt in normalizeOptions(item.question?.options)"
                :key="`${item.id}-${opt.key}`"
                :value="opt.key"
              >
                <div class="option-render">
                  <span class="option-key">{{ opt.key }}.</span>
                  <div class="option-content">
                    <MdEditor :content="opt.text || ''" previewOnly />
                  </div>
                </div>
              </n-checkbox>
            </n-space>
          </n-checkbox-group>
        </n-space>
      </n-card>

      <n-space>
        <n-button type="primary" :loading="submitting" @click="submitPaper">提交整卷</n-button>
      </n-space>

      <n-card v-if="result" title="提交结果" :bordered="false">
        <n-alert :show-icon="false" :type="result.is_pass ? 'success' : 'warning'">
          得分 {{ result.total_score }}/{{ result.max_score }}，及格线 {{ result.pass_score }}
        </n-alert>

        <n-table style="margin-top: 12px">
          <thead>
            <tr>
              <th>题目</th>
              <th>你的答案</th>
              <th>正确答案</th>
              <th>得分</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in result.detail || []" :key="row.question_id">
              <td>{{ row.title || `题目#${row.question_id}` }}</td>
              <td>{{ (row.selected_answers || []).join(', ') || '-' }}</td>
              <td>{{ (row.correct_answers || []).join(', ') || '-' }}</td>
              <td>{{ row.earned_score }}/{{ row.score }}</td>
            </tr>
          </tbody>
        </n-table>
      </n-card>
    </n-space>
  </n-spin>
</template>

<style scoped>
.option-render {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  width: 100%;
}

.option-key {
  flex: 0 0 auto;
  line-height: 28px;
  font-weight: 600;
}

.option-content {
  flex: 1;
  min-width: 0;
}

.option-content :deep(.n-card.md-editor-card) {
  border: none !important;
  box-shadow: none !important;
  background: transparent !important;
}

.option-content :deep(.md-editor),
.option-content :deep(.md-editor-v3) {
  background: transparent !important;
}

.option-content :deep(.md-editor-previewOnly .md-editor-preview),
.option-content :deep(.md-editor-content .md-editor-preview-wrapper) {
  padding: 0 !important;
}

.option-content :deep(article) {
  margin: 0 !important;
}

.option-content :deep(p:first-child) {
  margin-top: 0 !important;
}

.option-content :deep(p:last-child) {
  margin-bottom: 0 !important;
}
</style>
