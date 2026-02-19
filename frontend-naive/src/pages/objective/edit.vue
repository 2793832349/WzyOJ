<script setup>
import { computed, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import router from '@/router';
import Axios from '@/plugins/axios';
import MdEditor from '@/components/MdEditor.vue';

const route = useRoute();
const message = useMessage();

const id = computed(() => route.params.id);
const isEdit = computed(() => !!id.value);
const saving = ref(false);
const loading = ref(false);

const typeOptions = [
  { label: '单选题', value: 'single' },
  { label: '多选题', value: 'multiple' },
  { label: '判断题', value: 'judge' },
];

const createDefaultOptions = () => [
  { key: 'A', text: '' },
  { key: 'B', text: '' },
  { key: 'C', text: '' },
  { key: 'D', text: '' },
];

const question = ref({
  title: '',
  content: '',
  question_type: 'single',
  options: createDefaultOptions(),
  correct_answers: [],
  explanation: '',
  difficulty: 0,
  _is_hidden: false,
});

const isJudge = computed(() => question.value.question_type === 'judge');

const judgeOptions = [
  { key: 'T', text: '正确' },
  { key: 'F', text: '错误' },
];

watch(
  () => question.value.question_type,
  type => {
    if (type === 'judge') {
      question.value.options = judgeOptions;
      if (!['T', 'F'].includes(question.value.correct_answers?.[0])) {
        question.value.correct_answers = ['T'];
      }
      return;
    }

    if (!Array.isArray(question.value.options) || question.value.options.length < 2) {
      question.value.options = createDefaultOptions();
    }

    if (!Array.isArray(question.value.correct_answers)) {
      question.value.correct_answers = [];
    }

    if (type === 'single' && question.value.correct_answers.length > 1) {
      question.value.correct_answers = [question.value.correct_answers[0]];
    }
  }
);

const normalizeOptionKeys = () => {
  question.value.options = (question.value.options || []).map((item, idx) => ({
    key: String(item?.key || String.fromCharCode(65 + idx)).toUpperCase().trim(),
    text: String(item?.text || ''),
  }));
};

const addOption = () => {
  normalizeOptionKeys();
  const nextKey = String.fromCharCode(65 + question.value.options.length);
  question.value.options.push({ key: nextKey, text: '' });
};

const removeOption = idx => {
  if (question.value.options.length <= 2) {
    message.warning('至少保留两个选项');
    return;
  }
  const removedKey = question.value.options[idx]?.key;
  question.value.options.splice(idx, 1);
  normalizeOptionKeys();
  question.value.correct_answers = (question.value.correct_answers || []).filter(x => x !== removedKey);
};

const loadData = () => {
  if (!isEdit.value) return;
  loading.value = true;
  Axios.get(`/objective/${id.value}/`)
    .then(res => {
      question.value = {
        title: res.title || '',
        content: res.content || '',
        question_type: res.question_type || 'single',
        options: Array.isArray(res.options) ? res.options : [],
        correct_answers: Array.isArray(res.correct_answers) ? res.correct_answers : [],
        explanation: res.explanation || '',
        difficulty: Number.isFinite(res.difficulty) ? res.difficulty : 0,
        _is_hidden: !!res._is_hidden,
      };
      if (!question.value.options.length && question.value.question_type !== 'judge') {
        question.value.options = createDefaultOptions();
      }
      normalizeOptionKeys();
    })
    .catch(() => {
      message.error('题目不存在或没有编辑权限');
      router.push({ name: 'objective_list' });
    })
    .finally(() => {
      loading.value = false;
    });
};

const buildPayload = () => {
  normalizeOptionKeys();
  const payload = {
    title: '',
    content: question.value.content,
    question_type: question.value.question_type,
    options: question.value.options,
    correct_answers: question.value.correct_answers,
    explanation: question.value.explanation,
    difficulty: Number(question.value.difficulty || 0),
    _is_hidden: !!question.value._is_hidden,
  };

  if (isJudge.value) {
    payload.options = judgeOptions;
    payload.correct_answers = [question.value.correct_answers?.[0] || 'T'];
  }

  if (payload.question_type === 'single' && Array.isArray(payload.correct_answers) && payload.correct_answers.length > 1) {
    payload.correct_answers = [payload.correct_answers[0]];
  }

  return payload;
};

const save = () => {
  if (!String(question.value.content || '').trim()) {
    message.warning('请填写题干');
    return;
  }

  if (!isJudge.value && (!Array.isArray(question.value.options) || question.value.options.length < 2)) {
    message.warning('至少需要两个选项');
    return;
  }

  if (!Array.isArray(question.value.correct_answers) || !question.value.correct_answers.length) {
    message.warning('请设置正确答案');
    return;
  }

  saving.value = true;
  const payload = buildPayload();
  const req = isEdit.value
    ? Axios.put(`/objective/${id.value}/`, payload)
    : Axios.post('/objective/', payload);

  req
    .then(res => {
      message.success(isEdit.value ? '保存成功' : '创建成功');
      router.push({ name: 'objective_detail', params: { id: res.id || id.value } });
    })
    .finally(() => {
      saving.value = false;
    });
};

watch(id, loadData, { immediate: true });
</script>

<template>
  <n-spin :show="loading">
    <n-space vertical size="large">
      <n-page-header @back="router.push({ name: 'objective_list' })">
        <template #title>{{ isEdit ? `编辑客观题 #${id}` : '创建客观题' }}</template>
      </n-page-header>

      <n-card :bordered="false">
        <n-form label-placement="left" label-width="110" size="large">
          <n-form-item label="题型">
            <n-select v-model:value="question.question_type" :options="typeOptions" style="width: 220px" />
          </n-form-item>

          <n-form-item label="难度">
            <n-input-number v-model:value="question.difficulty" :min="0" :max="10" />
          </n-form-item>

          <n-form-item label="是否隐藏">
            <n-switch v-model:value="question._is_hidden" />
          </n-form-item>

          <n-form-item label="题干">
            <MdEditor v-model:content="question.content" />
          </n-form-item>

          <n-form-item label="选项">
            <n-space vertical style="width: 100%">
              <template v-if="isJudge">
                <n-alert type="info" :show-icon="false">判断题固定为 T=正确 / F=错误</n-alert>
                <n-space vertical>
                  <div v-for="opt in judgeOptions" :key="opt.key">{{ opt.key }}. {{ opt.text }}</div>
                </n-space>
              </template>

              <template v-else>
                <n-space
                  v-for="(opt, idx) in question.options"
                  :key="`${idx}-${opt.key}`"
                  align="start"
                  style="width: 100%"
                >
                  <n-input v-model:value="opt.key" style="width: 90px" placeholder="Key" />
                  <n-input
                      v-model:value="opt.text"
                      type="textarea"
                      :autosize="{ minRows: 2, maxRows: 8 }"
                      style="flex: 1"
                      placeholder="选项内容（支持 Markdown，如 ```cpp ... ```）"
                    />
                  <n-button tertiary type="error" @click="removeOption(idx)">删除</n-button>
                </n-space>
                <n-button dashed @click="addOption">添加选项</n-button>
              </template>
            </n-space>
          </n-form-item>

          <n-form-item label="正确答案">
            <n-space vertical style="width: 100%">
              <n-radio-group
                v-if="question.question_type === 'single' || isJudge"
                :value="question.correct_answers[0] || null"
                @update:value="val => (question.correct_answers = val ? [val] : [])"
              >
                <n-space>
                  <n-radio
                    v-for="opt in (isJudge ? judgeOptions : question.options)"
                    :key="`single-${opt.key}`"
                    :value="String(opt.key || '').toUpperCase()"
                  >
                    {{ String(opt.key || '').toUpperCase() }}
                  </n-radio>
                </n-space>
              </n-radio-group>

              <n-checkbox-group v-else v-model:value="question.correct_answers">
                <n-space>
                  <n-checkbox
                    v-for="opt in question.options"
                    :key="`multi-${opt.key}`"
                    :value="String(opt.key || '').toUpperCase()"
                  >
                    {{ String(opt.key || '').toUpperCase() }}
                  </n-checkbox>
                </n-space>
              </n-checkbox-group>
            </n-space>
          </n-form-item>

          <n-form-item label="解析">
            <MdEditor v-model:content="question.explanation" />
          </n-form-item>

          <n-form-item>
            <n-space>
              <n-button type="primary" :loading="saving" @click="save">保存</n-button>
              <n-button @click="router.push({ name: 'objective_list' })">取消</n-button>
            </n-space>
          </n-form-item>
        </n-form>
      </n-card>
    </n-space>
  </n-spin>
</template>
