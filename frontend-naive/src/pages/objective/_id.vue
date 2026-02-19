<script setup>
import { computed, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import router from '@/router';
import Axios from '@/plugins/axios';
import store from '@/store';
import MdEditor from '@/components/MdEditor.vue';

const route = useRoute();
const message = useMessage();

const id = computed(() => route.params.id);
const loading = ref(false);
const question = ref({
  options: [],
  question_type: 'single',
});

const canManage = computed(() => {
  const perms = store.state.user?.permissions || [];
  return perms.includes('problem');
});

const typeLabelMap = {
  single: '单选题',
  multiple: '多选题',
  judge: '判断题',
};

const selectedSingle = ref(null);
const selectedMultiple = ref([]);
const submitting = ref(false);
const submitResult = ref(null);

const isMultiple = computed(() => question.value.question_type === 'multiple');
const isJudge = computed(() => question.value.question_type === 'judge');

const normalizedOptions = computed(() => {
  const rows = Array.isArray(question.value.options) ? question.value.options : [];
  return rows.map(item => ({
    key: String(item?.key || '').trim().toUpperCase(),
    text: String(item?.text || ''),
  }));
});

const currentAnswers = computed(() => {
  if (isMultiple.value) return selectedMultiple.value;
  return selectedSingle.value ? [selectedSingle.value] : [];
});

const loadData = () => {
  loading.value = true;
  submitResult.value = null;
  selectedSingle.value = null;
  selectedMultiple.value = [];

  Axios.get(`/objective/${id.value}/`)
    .then(res => {
      question.value = {
        ...res,
        options: Array.isArray(res.options) ? res.options : [],
      };
    })
    .catch(() => {
      if (route.name !== 'objective_detail') return;
      message.error('题目不存在或你没有权限查看');
      router.push({ name: 'objective_list' });
    })
    .finally(() => {
      loading.value = false;
    });
};

const submitAnswer = () => {
  const answers = currentAnswers.value;
  if (!answers.length) {
    message.warning('请先作答后再提交');
    return;
  }
  submitting.value = true;
  Axios.post(`/objective/${id.value}/submit/`, { answers })
    .then(res => {
      submitResult.value = res;
      if (res.is_correct) {
        message.success('回答正确');
      } else {
        message.warning('回答错误，请查看解析');
      }
      loadData();
    })
    .finally(() => {
      submitting.value = false;
    });
};

watch(id, () => {
  if (route.name !== 'objective_detail') return;
  loadData();
});

loadData();
</script>

<template>
  <n-spin :show="loading">
    <n-space vertical size="large">
      <n-page-header @back="router.push({ name: 'objective_list' })">
        <template #title>
          客观题 #{{ question.id }}
        </template>
        <template #subtitle>
          {{ typeLabelMap[question.question_type] || question.question_type }}
        </template>
        <template #extra>
          <n-space>
            <n-tag :bordered="false" type="info">难度 {{ question.difficulty }}</n-tag>
            <n-tag :bordered="false" type="success">通过 {{ question.accepted_count }}</n-tag>
            <n-tag :bordered="false" type="warning">提交 {{ question.submission_count }}</n-tag>
            <n-button
              v-if="canManage"
              @click="router.push({ name: 'objective_edit', params: { id: question.id } })"
            >
              编辑
            </n-button>
          </n-space>
        </template>
      </n-page-header>

      <n-card :title="question.title" :bordered="false">
        <MdEditor :content="question.content || ''" previewOnly />
      </n-card>

      <n-card title="作答" :bordered="false">
        <n-radio-group
          v-if="!isMultiple"
          v-model:value="selectedSingle"
          style="width: 100%"
        >
          <n-space vertical>
            <n-radio
              v-for="opt in normalizedOptions"
              :key="opt.key"
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

        <n-checkbox-group v-else v-model:value="selectedMultiple" style="width: 100%">
          <n-space vertical>
            <n-checkbox
              v-for="opt in normalizedOptions"
              :key="opt.key"
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

        <n-space style="margin-top: 16px">
          <n-button type="primary" :loading="submitting" @click="submitAnswer">提交答案</n-button>
        </n-space>
      </n-card>

      <n-card v-if="submitResult" title="结果" :bordered="false">
        <n-alert :type="submitResult.is_correct ? 'success' : 'error'" :show-icon="false">
          {{ submitResult.is_correct ? '回答正确' : '回答错误' }}
        </n-alert>
        <n-space vertical style="margin-top: 12px">
          <div>
            你的答案：{{ (submitResult.selected_answers || []).join(', ') || '-' }}
          </div>
          <div>
            正确答案：{{ (submitResult.correct_answers || []).join(', ') || '-' }}
          </div>
        </n-space>
        <n-divider />
        <h3>题目解析</h3>
        <MdEditor :content="submitResult.explanation || question.explanation || '暂无解析'" previewOnly />
      </n-card>

      <n-card v-else-if="canManage" title="参考答案（仅管理员可见）" :bordered="false">
        <div>
          正确答案：{{ (question.correct_answers || []).join(', ') || '-' }}
        </div>
        <n-divider />
        <h3>题目解析</h3>
        <MdEditor :content="question.explanation || '暂无解析'" previewOnly />
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
