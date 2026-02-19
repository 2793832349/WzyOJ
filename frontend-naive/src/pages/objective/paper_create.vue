<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import router from '@/router';
import Axios from '@/plugins/axios';
import MdEditor from '@/components/MdEditor.vue';

const route = useRoute();
const message = useMessage();
const saving = ref(false);
const loading = ref(false);
const importingPdf = ref(false);
const importingImage = ref(false);
const importingImageMode = ref('');
const importingImageQuestionIndex = ref(-1);
const pdfInputRef = ref(null);
const imageInputRef = ref(null);

const pastedImageName = ref('');
const pastedImagePreview = ref('');
const pastedImageScope = ref('paper');
const imageImportMode = ref('paper');
const imageImportQuestionIndex = ref(-1);
const activeQuestionIndex = ref(-1);

const id = computed(() => route.params.id);
const isEdit = computed(() => !!id.value);

const typeOptions = [
  { label: '单选题', value: 'single' },
  { label: '多选题', value: 'multiple' },
  { label: '判断题', value: 'judge' },
];

const judgeOptions = [
  { key: 'T', text: '正确' },
  { key: 'F', text: '错误' },
];

const createDefaultOptions = () => [
  { key: 'A', text: '' },
  { key: 'B', text: '' },
  { key: 'C', text: '' },
  { key: 'D', text: '' },
];

const createQuestion = (order = 1) => ({
  title: '',
  content: '',
  question_type: 'single',
  options: createDefaultOptions(),
  correct_answers: [],
  explanation: '',
  difficulty: 0,
  score: 2,
  order,
});

const form = ref({
  title: '',
  description: '',
  pass_score: 60,
  _is_hidden: false,
  questions: [createQuestion(1)],
});

const revokePastedPreview = () => {
  if (pastedImagePreview.value) {
    URL.revokeObjectURL(pastedImagePreview.value);
    pastedImagePreview.value = '';
  }
};

const setPastedImagePreview = (file, scope = 'paper') => {
  revokePastedPreview();
  pastedImageName.value = file?.name || 'clipboard-image.png';
  pastedImagePreview.value = URL.createObjectURL(file);
  pastedImageScope.value = scope === 'question' ? 'question' : 'paper';
};

const normalizeOptionKeys = question => {
  question.options = (question.options || []).map((item, idx) => ({
    key: String(item?.key || String.fromCharCode(65 + idx)).toUpperCase().trim(),
    text: String(item?.text || ''),
  }));
};

const syncQuestionType = question => {
  if (question.question_type === 'judge') {
    question.options = [...judgeOptions];
    if (!['T', 'F'].includes(question.correct_answers?.[0])) {
      question.correct_answers = ['T'];
    }
    return;
  }

  if (!Array.isArray(question.options) || question.options.length < 2) {
    question.options = createDefaultOptions();
  }
  normalizeOptionKeys(question);

  if (!Array.isArray(question.correct_answers)) {
    question.correct_answers = [];
  }

  if (question.question_type === 'single' && question.correct_answers.length > 1) {
    question.correct_answers = [question.correct_answers[0]];
  }
};

const normalizeImportedQuestion = (item, idx) => {
  const q = {
    title: String(item?.title || '').trim(),
    content: String(item?.content || '').trim(),
    question_type: String(item?.question_type || 'single').toLowerCase(),
    options: Array.isArray(item?.options) ? item.options : [],
    correct_answers: Array.isArray(item?.correct_answers) ? item.correct_answers : [],
    explanation: String(item?.explanation || '').trim(),
    difficulty: Number(item?.difficulty || 0),
    score: Number(item?.score || 2),
    order: idx + 1,
  };

  if (q.question_type === 'judge') {
    q.options = [...judgeOptions];
    q.correct_answers = [String(q.correct_answers?.[0] || 'T').toUpperCase()];
  } else {
    q.options = q.options.map((opt, i) => ({
      key: String(opt?.key || String.fromCharCode(65 + i)).toUpperCase(),
      text: String(opt?.text || ''),
    }));
    if (q.options.length < 2) {
      q.options = createDefaultOptions();
    }
    q.correct_answers = q.correct_answers.map(i => String(i).toUpperCase());
    if (q.question_type === 'single' && q.correct_answers.length > 1) {
      q.correct_answers = [q.correct_answers[0]];
    }
  }

  return q;
};

const applyImportedDraft = (res, sourceName) => {
  const draft = res?.draft || {};
  const rawQuestions = Array.isArray(draft.questions) ? draft.questions : [];
  if (!rawQuestions.length) {
    message.warning('AI 未识别到题目，请检查内容后重试');
    return;
  }

  form.value.title = draft.title || form.value.title;
  form.value.description = draft.description || '';
  form.value.pass_score = Number(draft.pass_score || form.value.pass_score || 60);
  form.value.questions = rawQuestions.map((q, idx) => normalizeImportedQuestion(q, idx));

  const ignored = Number(res?.meta?.ignored_count || 0);
  if (ignored > 0) {
    message.warning(`${sourceName}导入完成：${form.value.questions.length} 题，忽略 ${ignored} 题（格式不完整）`);
  } else {
    message.success(`${sourceName}导入完成：${form.value.questions.length} 题`);
  }
};

const loadData = () => {
  if (!isEdit.value) return;

  loading.value = true;
  Axios.get(`/objective/paper/${id.value}/`)
    .then(res => {
      const items = Array.isArray(res.items) ? res.items : [];
      const questions = items.map((item, idx) =>
        normalizeImportedQuestion(
          {
            ...(item.question || {}),
            score: item.score,
            order: item.order,
          },
          idx
        )
      );

      form.value = {
        title: res.title || '',
        description: res.description || '',
        pass_score: Number(res.pass_score || 60),
        _is_hidden: !!res._is_hidden,
        questions: questions.length ? questions : [createQuestion(1)],
      };
    })
    .catch(() => {
      message.error('套卷不存在或没有编辑权限');
      router.push({ name: 'objective_paper_list' });
    })
    .finally(() => {
      loading.value = false;
    });
};

const addQuestion = () => {
  form.value.questions.push(createQuestion(form.value.questions.length + 1));
};

const removeQuestion = idx => {
  if (form.value.questions.length <= 1) {
    message.warning('至少保留一道题');
    return;
  }
  form.value.questions.splice(idx, 1);
  form.value.questions.forEach((q, i) => {
    q.order = i + 1;
  });
};

const addOption = idx => {
  const q = form.value.questions[idx];
  normalizeOptionKeys(q);
  const nextKey = String.fromCharCode(65 + q.options.length);
  q.options.push({ key: nextKey, text: '' });
};

const removeOption = (qIdx, optIdx) => {
  const q = form.value.questions[qIdx];
  if (q.options.length <= 2) {
    message.warning('选择题至少保留两个选项');
    return;
  }
  const removedKey = q.options[optIdx]?.key;
  q.options.splice(optIdx, 1);
  normalizeOptionKeys(q);
  q.correct_answers = (q.correct_answers || []).filter(x => x !== removedKey);
};

const buildPayload = () => {
  const payload = {
    title: form.value.title,
    description: form.value.description,
    pass_score: Number(form.value.pass_score || 0),
    _is_hidden: !!form.value._is_hidden,
    questions: [],
  };

  payload.questions = form.value.questions.map((item, idx) => {
    const q = JSON.parse(JSON.stringify(item));
    q.order = idx + 1;

    if (q.question_type === 'judge') {
      q.options = [...judgeOptions];
      q.correct_answers = [q.correct_answers?.[0] || 'T'];
    } else {
      normalizeOptionKeys(q);
      if (q.question_type === 'single' && q.correct_answers.length > 1) {
        q.correct_answers = [q.correct_answers[0]];
      }
    }

    q.title = '';
    q.score = Number(q.score || 2);
    q.difficulty = Number(q.difficulty || 0);
    return q;
  });

  return payload;
};

const validatePayload = payload => {
  if (!payload.title.trim()) {
    message.warning('请填写套卷标题');
    return false;
  }

  if (!Array.isArray(payload.questions) || !payload.questions.length) {
    message.warning('至少添加一道题');
    return false;
  }

  for (let i = 0; i < payload.questions.length; i++) {
    const q = payload.questions[i];
    const label = `第 ${i + 1} 题`;

    if (!String(q.content || '').trim()) {
      message.warning(`${label}：请填写题干`);
      return false;
    }

    if (!Array.isArray(q.correct_answers) || !q.correct_answers.length) {
      message.warning(`${label}：请设置正确答案`);
      return false;
    }

    if (q.question_type !== 'judge') {
      if (!Array.isArray(q.options) || q.options.length < 2) {
        message.warning(`${label}：至少需要两个选项`);
        return false;
      }
      const keys = new Set((q.options || []).map(opt => String(opt.key || '').toUpperCase()));
      if ((q.correct_answers || []).some(ans => !keys.has(String(ans || '').toUpperCase()))) {
        message.warning(`${label}：正确答案必须在选项中`);
        return false;
      }
    }
  }

  return true;
};

const parseRequestError = err => {
  const status = err?.response?.status;
  const data = err?.response?.data;

  const normalizeErrorText = value => {
    if (value === null || value === undefined) return '';
    if (typeof value === 'string') return value.trim();
    if (Array.isArray(value)) {
      return value.map(item => normalizeErrorText(item)).filter(Boolean).join('；');
    }
    if (typeof value === 'object') {
      const prefer = value.error || value.detail || value.message;
      if (prefer) return normalizeErrorText(prefer);
      const pairs = Object.entries(value)
        .map(([k, v]) => {
          const text = normalizeErrorText(v);
          return text ? `${k}: ${text}` : '';
        })
        .filter(Boolean);
      if (pairs.length) return pairs.join('；');
      try {
        return JSON.stringify(value);
      } catch (_e) {
        return '';
      }
    }
    return String(value);
  };

  const detail = normalizeErrorText(data);
  if (detail) return detail;
  if (status === 504) return 'AI 识别超时，请稍后重试';
  if (status === 502) return 'AI 服务暂时不可用，请稍后重试';
  if (status === 413) return '文件过大，请压缩后重试';
  if (status === 415) return '文件类型不支持，请换图片后重试';
  if (status === 400) return '400 Bad Request（后端未返回详细错误）';
  return '请求失败，请稍后重试';
};

const triggerPdfImport = () => {
  if (importingPdf.value) return;
  pdfInputRef.value?.click();
};

const triggerImageImport = (mode = 'paper', questionIndex = -1) => {
  if (importingImage.value) return;
  imageImportMode.value = mode;
  imageImportQuestionIndex.value = Number.isInteger(questionIndex) ? questionIndex : -1;
  imageInputRef.value?.click();
};

const triggerPaperImageImport = () => {
  triggerImageImport('paper', -1);
};

const triggerQuestionImageImport = idx => {
  triggerImageImport('question', idx);
};

const setActiveQuestion = idx => {
  activeQuestionIndex.value = Number.isInteger(idx) ? idx : -1;
};

const getPasteTarget = () => {
  if (imageImportMode.value === 'question' && Number.isInteger(imageImportQuestionIndex.value) && imageImportQuestionIndex.value >= 0) {
    return { mode: 'question', questionIndex: imageImportQuestionIndex.value };
  }
  if (Number.isInteger(activeQuestionIndex.value) && activeQuestionIndex.value >= 0) {
    return { mode: 'question', questionIndex: activeQuestionIndex.value };
  }
  return null;
};

const applyImportedSingleQuestion = (res, questionIndex) => {
  const draft = res?.draft || {};
  const rawQuestions = Array.isArray(draft.questions) ? draft.questions : [];
  if (!rawQuestions.length) {
    message.warning('AI 未识别到题目，请检查图片内容后重试');
    return;
  }

  const normalized = normalizeImportedQuestion(rawQuestions[0], questionIndex + 1);
  if (questionIndex >= 0 && questionIndex < form.value.questions.length) {
    const oldOrder = form.value.questions[questionIndex]?.order || questionIndex + 1;
    form.value.questions[questionIndex] = {
      ...form.value.questions[questionIndex],
      ...normalized,
      order: oldOrder,
    };
  } else {
    form.value.questions.push({
      ...normalized,
      order: form.value.questions.length + 1,
    });
  }

  const extraCount = Math.max(0, rawQuestions.length - 1);
  if (extraCount > 0) {
    message.warning(`单题导入完成，已填充第 ${questionIndex + 1} 题（另外识别到 ${extraCount} 题未使用）`);
  } else {
    message.success(`单题导入完成，已填充第 ${questionIndex + 1} 题`);
  }
};

const runImageImport = (file, mode = imageImportMode.value, questionIndex = imageImportQuestionIndex.value) => {
  if (!file) return;

  const fd = new FormData();
  fd.append('file', file);
  fd.append('title', form.value.title || '');
  fd.append('pass_score', String(form.value.pass_score || 60));

  importingImage.value = true;
  importingImageMode.value = mode === 'question' ? 'question' : 'paper';
  importingImageQuestionIndex.value = Number.isInteger(questionIndex) ? questionIndex : -1;
  Axios.post('/objective/paper/import-image/', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 600000,
  })
    .then(res => {
      if (mode === 'question') {
        const safeIndex = Number.isInteger(questionIndex) && questionIndex >= 0 ? questionIndex : -1;
        applyImportedSingleQuestion(res, safeIndex);
      } else {
        applyImportedDraft(res, '图片');
      }
    })
    .catch(err => {
      console.error('[objective import-image error]', err?.response?.status, err?.response?.data, err);
      message.error(parseRequestError(err));
    })
    .finally(() => {
      importingImage.value = false;
      importingImageMode.value = '';
      importingImageQuestionIndex.value = -1;
      imageImportMode.value = 'paper';
      imageImportQuestionIndex.value = -1;
    });
};

const onImageSelected = event => {
  const file = event?.target?.files?.[0];
  if (!file) return;

  setPastedImagePreview(file, imageImportMode.value);
  runImageImport(file);

  if (event?.target) event.target.value = '';
};

const onPdfSelected = event => {
  const file = event?.target?.files?.[0];
  if (!file) return;

  const fd = new FormData();
  fd.append('file', file);
  fd.append('title', form.value.title || '');
  fd.append('pass_score', String(form.value.pass_score || 60));

  importingPdf.value = true;
  Axios.post('/objective/paper/import-pdf/', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 600000,
  })
    .then(res => {
      applyImportedDraft(res, 'PDF');
    })
    .catch(err => {
      message.error(parseRequestError(err));
    })
    .finally(() => {
      importingPdf.value = false;
      if (event?.target) event.target.value = '';
    });
};

const onPasteImage = event => {
  if (importingImage.value) return;

  const target = getPasteTarget();

  const clipboardItems = event?.clipboardData?.items || [];
  let imageFile = null;
  for (const item of clipboardItems) {
    if (item?.type?.startsWith('image/')) {
      imageFile = item.getAsFile();
      break;
    }
  }

  if (!imageFile) return;
  event.preventDefault();

  if (!target) {
    message.warning('请先点选要填充的题目，再使用 Ctrl/Cmd + V 粘贴截图');
    return;
  }

  const file = new File([imageFile], imageFile.name || `clipboard-${Date.now()}.png`, {
    type: imageFile.type || 'image/png',
  });

  setPastedImagePreview(file, 'question');
  runImageImport(file, 'question', target.questionIndex);
};


const save = () => {
  const payload = buildPayload();
  if (!validatePayload(payload)) return;

  saving.value = true;
  const req = isEdit.value
    ? Axios.post(`/objective/paper/${id.value}/update-with-questions/`, payload)
    : Axios.post('/objective/paper/create-with-questions/', payload);

  req
    .then(res => {
      message.success(isEdit.value ? '套卷修改成功' : '套卷创建成功');
      router.push({ name: 'objective_paper_detail', params: { id: res.id } });
    })
    .catch(err => {
      message.error(parseRequestError(err));
    })
    .finally(() => {
      saving.value = false;
    });
};

watch(id, loadData, { immediate: true });

onMounted(() => {
  window.addEventListener('paste', onPasteImage);
});

onBeforeUnmount(() => {
  window.removeEventListener('paste', onPasteImage);
  revokePastedPreview();
});
</script>

<template>
  <n-spin :show="loading">
    <n-space vertical size="large">
      <n-page-header @back="router.push({ name: 'objective_paper_list' })">
        <template #title>{{ isEdit ? `编辑套卷 #${id}` : '一次创建套卷' }}</template>
        <template #subtitle>可手动录入，也可上传 PDF / 粘贴图片 用 AI 自动识别整套试卷</template>
      </n-page-header>

      <n-card :bordered="false">
        <n-form label-placement="left" label-width="110" size="large">
          <n-form-item label="套卷标题">
            <n-input v-model:value="form.title" placeholder="例如：C++ 一级模拟卷 A" />
          </n-form-item>
          <n-form-item label="套卷说明">
            <MdEditor v-model:content="form.description" />
          </n-form-item>
          <n-form-item label="及格分">
            <n-input-number v-model:value="form.pass_score" :min="0" />
          </n-form-item>
          <n-form-item label="是否隐藏">
            <n-switch v-model:value="form._is_hidden" />
          </n-form-item>

          <n-form-item v-if="!isEdit" label="AI导入PDF">
            <n-space>
              <input
                ref="pdfInputRef"
                type="file"
                accept="application/pdf,.pdf"
                style="display: none"
                @change="onPdfSelected"
              />
              <n-button type="info" :loading="importingPdf" @click="triggerPdfImport">
                上传 PDF 并识别题目
              </n-button>
              <n-text depth="3">识别后会覆盖当前题目列表，请先确认。</n-text>
            </n-space>
          </n-form-item>

          <n-form-item label="AI导入图片">
            <n-space vertical style="width: 100%">
              <n-space>
                <input
                  ref="imageInputRef"
                  type="file"
                  accept="image/*"
                  style="display: none"
                  @change="onImageSelected"
                />
                <n-button type="info" secondary :loading="importingImage && importingImageMode === 'paper'" :disabled="importingImage" @click="triggerPaperImageImport">
                  上传图片并导入整卷
                </n-button>
                <n-tag v-if="pastedImageName && pastedImageScope === 'paper'" type="success" :bordered="false">
                  {{ pastedImageName }}
                </n-tag>
              </n-space>

              <n-alert type="info" :show-icon="false">
                支持直接在本页按 <b>Ctrl/Cmd + V</b> 粘贴截图导入。也可在每道题里使用“识别填充本题”。
              </n-alert>

              <div v-if="pastedImagePreview && pastedImageScope === 'paper'" style="max-width: 360px; border: 1px solid #e5e7eb; border-radius: 8px; padding: 8px;">
                <img :src="pastedImagePreview" alt="pasted-preview" style="width: 100%; display: block; border-radius: 6px;" />
              </div>
            </n-space>
          </n-form-item>
        </n-form>
      </n-card>

      <n-card :bordered="false" title="题目列表">
        <n-space vertical :size="16">
          <n-card
            v-for="(q, idx) in form.questions"
            :key="idx"
            size="small"
            embedded
            :title="`第 ${idx + 1} 题`"
            @click="setActiveQuestion(idx)"
            @focusin="setActiveQuestion(idx)"
          >
            <n-form label-placement="left" label-width="90">
              <n-form-item label="题型">
                <n-select
                  v-model:value="q.question_type"
                  :options="typeOptions"
                  style="width: 180px"
                  @update:value="() => syncQuestionType(q)"
                />
              </n-form-item>

              <n-form-item label="分值">
                <n-input-number v-model:value="q.score" :min="1" />
              </n-form-item>

              <n-form-item label="难度">
                <n-input-number v-model:value="q.difficulty" :min="0" :max="10" />
              </n-form-item>

              <n-form-item label="识图填充">
                <n-button secondary type="info" :loading="importingImage && importingImageMode === 'question' && importingImageQuestionIndex === idx" :disabled="importingImage" @click="() => { setActiveQuestion(idx); triggerQuestionImageImport(idx); }">
                  上传图片识别并填充本题
                </n-button>
              </n-form-item>

              <n-form-item label="题干">
                <MdEditor v-model:content="q.content" />
              </n-form-item>

              <n-form-item label="选项">
                <n-space vertical style="width: 100%">
                  <template v-if="q.question_type === 'judge'">
                    <n-alert type="info" :show-icon="false">判断题固定为 T=正确 / F=错误</n-alert>
                    <div>T. 正确</div>
                    <div>F. 错误</div>
                  </template>

                  <template v-else>
                    <n-space
                      v-for="(opt, optIdx) in q.options"
                      :key="`${optIdx}-${opt.key}`"
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
                      <n-button tertiary type="error" @click="removeOption(idx, optIdx)">删除</n-button>
                    </n-space>
                    <n-button dashed @click="addOption(idx)">添加选项</n-button>
                  </template>
                </n-space>
              </n-form-item>

              <n-form-item label="正确答案">
                <n-space vertical style="width: 100%">
                  <n-radio-group
                    v-if="q.question_type === 'single' || q.question_type === 'judge'"
                    :value="q.correct_answers[0] || null"
                    @update:value="val => (q.correct_answers = val ? [val] : [])"
                  >
                    <n-space>
                      <n-radio
                        v-for="opt in (q.question_type === 'judge' ? judgeOptions : q.options)"
                        :key="`single-${idx}-${opt.key}`"
                        :value="String(opt.key || '').toUpperCase()"
                      >
                        {{ String(opt.key || '').toUpperCase() }}
                      </n-radio>
                    </n-space>
                  </n-radio-group>

                  <n-checkbox-group v-else v-model:value="q.correct_answers">
                    <n-space>
                      <n-checkbox
                        v-for="opt in q.options"
                        :key="`multi-${idx}-${opt.key}`"
                        :value="String(opt.key || '').toUpperCase()"
                      >
                        {{ String(opt.key || '').toUpperCase() }}
                      </n-checkbox>
                    </n-space>
                  </n-checkbox-group>
                </n-space>
              </n-form-item>

              <n-form-item label="解析">
                <MdEditor v-model:content="q.explanation" />
              </n-form-item>

              <n-form-item>
                <n-button tertiary type="error" @click="removeQuestion(idx)">删除本题</n-button>
              </n-form-item>
            </n-form>
          </n-card>
        </n-space>

        <n-space style="margin-top: 12px">
          <n-button dashed @click="addQuestion">添加一道题</n-button>
        </n-space>
      </n-card>

      <n-space>
        <n-button type="primary" :loading="saving" @click="save">{{ isEdit ? '保存修改' : '保存整套试卷' }}</n-button>
        <n-button @click="router.push({ name: 'objective_paper_list' })">取消</n-button>
      </n-space>
    </n-space>
  </n-spin>
</template>
