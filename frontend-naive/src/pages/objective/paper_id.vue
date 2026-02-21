<script setup>
import { computed, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import router from '@/router';
import Axios from '@/plugins/axios';
import MdEditor from '@/components/MdEditor.vue';
import store from '@/store';
import { AddOutline, CreateOutline, DocumentTextOutline } from '@vicons/ionicons5';

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

const typeTagMap = {
  single: 'info',
  multiple: 'warning',
  judge: 'success',
};

const totalQuestions = computed(() => (paper.value.items || []).length);
const answeredCount = computed(() => {
  let count = 0;
  for (const item of paper.value.items || []) {
    const q = item.question || {};
    const key = String(q.id);
    const val = answers.value[key];
    if (q.question_type === 'multiple') {
      if (Array.isArray(val) && val.length) count += 1;
    } else if (val) {
      count += 1;
    }
  }
  return count;
});
const progressPercent = computed(() => {
  if (!totalQuestions.value) return 0;
  return Math.round((answeredCount.value / totalQuestions.value) * 100);
});

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
    <div class="paper-detail-page">
      <section class="paper-hero">
        <div class="hero-left">
          <n-button quaternary @click="router.push({ name: 'objective_paper_list' })">返回套卷列表</n-button>
          <n-tag size="small" :bordered="false" round type="info">
            <template #icon>
              <n-icon :component="DocumentTextOutline" />
            </template>
            客观题套卷
          </n-tag>
          <h1>{{ paper.title || `套卷 #${paper.id || ''}` }}</h1>
          <p>整卷提交后统一判分，便于课堂测评、阶段练习与讲评复盘。</p>
        </div>

        <div class="hero-right">
          <div class="score-box">
            <div class="score-item">
              <span>题目</span>
              <strong>{{ paper.question_count || totalQuestions }}</strong>
            </div>
            <div class="score-item">
              <span>总分</span>
              <strong>{{ paper.total_score || 0 }}</strong>
            </div>
            <div class="score-item">
              <span>及格</span>
              <strong class="pass-line">{{ paper.pass_score || 0 }}</strong>
            </div>
          </div>
          <n-space>
            <n-button v-if="canManage" @click="router.push({ name: 'objective_paper_edit', params: { id: paper.id } })">
              <template #icon>
                <n-icon :component="CreateOutline" />
              </template>
              编辑套卷
            </n-button>
            <n-button v-if="canManage" @click="router.push({ name: 'objective_paper_create' })">
              <template #icon>
                <n-icon :component="AddOutline" />
              </template>
              新建套卷
            </n-button>
          </n-space>
        </div>
      </section>

      <n-card v-if="paper.description" class="desc-card" :bordered="false" title="套卷说明">
        <MdEditor :content="paper.description" previewOnly />
      </n-card>

      <n-card class="submit-card" :bordered="false">
        <div class="submit-row">
          <div class="progress-info">
            <h3>作答进度</h3>
            <p>已作答 {{ answeredCount }} / {{ totalQuestions }} 题，当前进度 {{ progressPercent }}%</p>
          </div>
          <n-button type="primary" size="large" :loading="submitting" @click="submitPaper">提交整卷</n-button>
        </div>
        <n-progress :percentage="progressPercent" :height="10" indicator-placement="inside" status="success" />
      </n-card>

      <n-card
        v-for="(item, idx) in paper.items"
        :key="item.id"
        :bordered="false"
        class="question-card"
      >
        <template #header>
          <div class="question-head">
            <div class="question-title">第 {{ idx + 1 }} 题</div>
            <div class="question-tags">
              <n-tag
                size="small"
                :bordered="false"
                :type="typeTagMap[item.question?.question_type] || 'default'"
              >
                {{ typeLabelMap[item.question?.question_type] || item.question?.question_type }}
              </n-tag>
              <n-tag size="small" :bordered="false" type="warning">{{ item.score }} 分</n-tag>
            </div>
          </div>
        </template>

        <div class="question-content">
          <MdEditor :content="item.question?.content || ''" previewOnly />
        </div>

        <div class="options-block">
          <n-radio-group
            v-if="item.question?.question_type !== 'multiple'"
            :value="answers[String(item.question?.id)]"
            @update:value="val => setAnswer(item.question?.id, val)"
          >
            <n-space vertical size="large">
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
            <n-space vertical size="large">
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
        </div>
      </n-card>

      <n-card v-if="result" :bordered="false" class="result-card">
        <template #header>提交结果</template>

        <n-alert :show-icon="false" :type="result.is_pass ? 'success' : 'warning'">
          得分 {{ result.total_score }}/{{ result.max_score }}，及格线 {{ result.pass_score }}
        </n-alert>

        <n-table class="result-table" style="margin-top: 12px">
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
    </div>
  </n-spin>
</template>

<style scoped>
.paper-detail-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.paper-hero {
  display: flex;
  align-items: stretch;
  justify-content: space-between;
  gap: 18px;
  padding: 22px;
  border-radius: 18px;
  border: 1px solid #d7e5ff;
  background: linear-gradient(135deg, #eff5ff, #f8fbff);
}

.hero-left {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.hero-left h1 {
  margin: 0;
  color: #1f2f4d;
  font-size: 32px;
  line-height: 1.2;
}

.hero-left p {
  margin: 0;
  color: #62789f;
  font-size: 14px;
}

.hero-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
}

.score-box {
  display: grid;
  grid-template-columns: repeat(3, minmax(90px, 1fr));
  gap: 10px;
}

.score-item {
  border-radius: 12px;
  padding: 10px 12px;
  background: #fff;
  border: 1px solid #dce8fb;
  text-align: center;
}

.score-item span {
  display: block;
  font-size: 12px;
  color: #6f83a8;
  margin-bottom: 4px;
}

.score-item strong {
  font-size: 22px;
  color: #223459;
}

.score-item .pass-line {
  color: #059669;
}

.desc-card,
.submit-card,
.question-card,
.result-card {
  border-radius: 16px;
  border: 1px solid #e7edf7;
}

.submit-card {
  background: linear-gradient(180deg, #ffffff, #f8fbff);
}

.submit-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.progress-info h3 {
  margin: 0;
  color: #1d3e7c;
  font-size: 18px;
}

.progress-info p {
  margin: 6px 0 0;
  color: #5f759f;
  font-size: 13px;
}

.question-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.question-title {
  font-weight: 800;
  color: #1f2f4d;
  font-size: 20px;
}

.question-tags {
  display: flex;
  align-items: center;
  gap: 8px;
}

.question-content {
  border-radius: 12px;
  padding: 8px 10px;
  background: #fcfdff;
  border: 1px solid #edf2fa;
}

.options-block {
  margin-top: 14px;
  padding: 14px;
  border-radius: 12px;
  background: #f9fbff;
  border: 1px solid #e8effb;
}

.option-render {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  width: 100%;
}

.option-key {
  flex: 0 0 auto;
  line-height: 28px;
  font-weight: 700;
  color: #365189;
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

.result-table :deep(th) {
  color: #1d3e7c;
  font-weight: 700;
}

@media (max-width: 1000px) {
  .paper-hero {
    flex-direction: column;
  }

  .hero-right {
    align-items: flex-start;
  }

  .score-box {
    width: 100%;
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .hero-left h1 {
    font-size: 24px;
  }

  .submit-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .question-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .score-box {
    grid-template-columns: 1fr;
  }

  .result-table {
    overflow-x: auto;
    display: block;
  }
}
</style>
