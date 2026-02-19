<script setup>
import { ref, watch, computed } from 'vue';
import Axios from '@/plugins/axios';
import config from '../../config';
import router from '@/router';
import store from '@/store';
import { useRoute } from 'vue-router';
import MdEditor from '@/components/MdEditor.vue';
import { languageOptions } from '@/plugins/consts';
import CodeMirror from '@/components/CodeMirror.vue';
import CodeWithCard from '@/components/CodeWithCard.vue';
import BlocklyEditor from '@/components/BlocklyEditor.vue';
import { MemoryOutlined, AccessTimeOutlined, ArrowBackOutlined, ArrowForwardOutlined } from '@vicons/material';
import Captcha from '../../components/captcha.vue';

const route = useRoute(),
  message = useMessage();
const id = computed(() => route.params.id),
  problemData = ref({}),
  prevProblemId = ref(null),
  nextProblemId = ref(null);

const INDENT_STORAGE_KEY = 'online_compiler_indent_size';
const indentOptions = [
  { label: '2 空格', value: 2 },
  { label: '4 空格', value: 4 },
  { label: '8 空格', value: 8 },
];

const loadIndentSize = () => {
  if (typeof window === 'undefined') return 4;
  const raw = Number(window.localStorage.getItem(INDENT_STORAGE_KEY));
  return [2, 4, 8].includes(raw) ? raw : 4;
};

const compilerIndentSize = ref(loadIndentSize());
watch(compilerIndentSize, val => {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(INDENT_STORAGE_KEY, String(val));
});

const getLeetCodeStarter = (language) => {
  if (problemData.value?.judge_mode !== 'leetcode') return '';
  const templates = problemData.value?.leetcode_templates || {};
  const langTpl = templates?.[language];
  return typeof langTpl?.starter === 'string' ? langTpl.starter : '';
};

const loadData = () => {
  Axios.get(`/problem/${id.value}/`)
    .then(res => {
      res.files = res.files.map(file => ({
        name: file,
        status: 'finished',
      }));
      problemData.value = res;
      applyStarterIfNeeded();
    })
    .catch(() => {
      if (route.name !== 'problem_detail') return;
      message.error('题目不存在或暂时无法查看！');
      router.push({ name: 'problem_list' });
    });
};

const loadAdjacentProblems = () => {
  Axios.get(`/problem/${id.value}/adjacent/`)
    .then(res => {
      prevProblemId.value = res.prev;
      nextProblemId.value = res.next;
    })
    .catch(() => {
      prevProblemId.value = null;
      nextProblemId.value = null;
    });
};

const goToPrevProblem = () => {
  if (prevProblemId.value) {
    router.push({ name: 'problem_detail', params: { id: prevProblemId.value } });
  }
};

const goToNextProblem = () => {
  if (nextProblemId.value) {
    router.push({ name: 'problem_detail', params: { id: nextProblemId.value } });
  }
};

const submitBlockly = async () => {
  if (!blocklyCode.value) {
    message.warning('代码不能为空');
    return;
  }
  if (!(await blocklyCaptchaRef.value.checkCaptcha())) return;
  submiting.value = true;
  const language = 'cpp';
  Axios.post('/submission/', {
    problem_id: id.value,
    source: blocklyCode.value,
    language,
    _is_hidden: blocklySubmitData.value._is_hidden,
    captcha: blocklySubmitData.value.captcha,
  })
    .then(res => {
      if (!res?.id) {
        message.error('提交返回异常，请稍后重试');
        return;
      }
      store.commit('setSubmitLanguage', language);
      router.push(`/submission/${res.id}/`);
    })
    .finally(() => {
      submiting.value = false;
    });
};

loadData();
loadAdjacentProblems();

watch(id, (newId) => {
  if (route.name !== 'problem_detail') return;
  if (!newId) return;
  loadData();
  loadAdjacentProblems();
  loadBlocklyDraft();
});


const blocklyWorkspaceXml = ref(''),
  blocklyCode = ref(''),
  blocklyDraftLoaded = ref(false),
  blocklyDraftSaving = ref(false);

const blocklySubmitData = ref({
  _is_hidden: false,
  captcha: '',
});

const blocklyCaptchaRef = ref(null);
let blocklySaveTimer = null;

const loadBlocklyDraft = () => {
  Axios.get(`/problem/${id.value}/blockly-draft/`)
    .then(res => {
      blocklyDraftLoaded.value = false;
      blocklyWorkspaceXml.value = res?.workspace_xml ?? '';
      setTimeout(() => {
        blocklyDraftLoaded.value = true;
      }, 0);
    })
    .catch(() => {
      blocklyDraftLoaded.value = true;
    });
};

loadBlocklyDraft();

watch(blocklyWorkspaceXml, val => {
  if (!blocklyDraftLoaded.value) return;
  if (blocklySaveTimer) clearTimeout(blocklySaveTimer);
  blocklySaveTimer = setTimeout(() => {
    blocklyDraftSaving.value = true;
    Axios.put(`/problem/${id.value}/blockly-draft/`, { workspace_xml: val })
      .finally(() => {
        blocklyDraftSaving.value = false;
      });
  }, 1000);
});

const beforeLeave = tabName => {
  if (tabName === 'submission') {
    router.push({
      name: 'submission_list',
      query: { problem__id: id.value },
    });
    return false;
  } else if (tabName === 'discussion') {
    router.push({
      name: 'discussion_list',
      query: { related_problem__id: id.value },
    });
    return false;
  } else if (tabName === 'edit') {
    router.push({
      name: 'problem_edit',
      params: { id: id.value },
    });
    return false;
  }
  return true;
};

const submitData = ref({
    source: '',
    language: store.getters.defaultSubmitLanguage,
    _is_hidden: false,
    captcha: '',
  }),
  submitTabCaptchaRef = ref(null),
  captchaRef = ref(null),
  submiting = ref(false);

const runInput = ref(''),
  runing = ref(false),
  runResult = ref({
    ok: true,
    phase: '',
    output: '',
    error: '',
    exit_code: 0,
    wrapped: false,
  });

const applyStarterIfNeeded = () => {
  const starter = getLeetCodeStarter(submitData.value.language);
  if (!starter) return;
  if (!submitData.value.source || !submitData.value.source.trim()) {
    submitData.value.source = starter;
  }
};

watch(() => submitData.value.language, () => {
  applyStarterIfNeeded();
});

 const tutorQuestion = ref(''),
   tutorRuntimeError = ref(''),
   tutorAnswer = ref(''),
   tutorSessionId = ref(''),
   tutorMessages = ref([]),
   tutorLoading = ref(false);

const submit = async () => {
  if (!submitData.value.source) {
    message.warning('代码不能为空');
    return;
  }
  const activeCaptchaRef = submitTabCaptchaRef.value || captchaRef.value;
  if (!activeCaptchaRef || !(await activeCaptchaRef.checkCaptcha())) return;
  submiting.value = true;
  Axios.post('/submission/', { problem_id: id.value, ...submitData.value })
    .then(res => {
      if (!res?.id) {
        message.error('提交返回异常，请稍后重试');
        return;
      }
      store.commit('setSubmitLanguage', submitData.value.language);
      router.push(`/submission/${res.id}/`);
    })
    .finally(() => {
      submiting.value = false;
    });
};

const runCode = () => {
  if (!submitData.value.source || !submitData.value.source.trim()) {
    message.warning('代码不能为空');
    return;
  }

  runing.value = true;
  runResult.value = {
    ok: true,
    phase: '',
    output: '',
    error: '',
    exit_code: 0,
    wrapped: false,
  };

  Axios.post('/submission/debug/', {
    problem_id: id.value,
    language: submitData.value.language,
    source: submitData.value.source,
    input: runInput.value,
  })
    .then(res => {
      runResult.value = {
        ok: !!res?.ok,
        phase: res?.phase || '',
        output: res?.output || '',
        error: res?.error || '',
        exit_code: Number.isInteger(res?.exit_code) ? res.exit_code : 0,
        wrapped: !!res?.wrapped,
      };
    })
    .catch(() => {
      runResult.value = {
        ok: false,
        phase: 'system',
        output: '',
        error: '运行失败，请稍后重试',
        exit_code: -1,
        wrapped: false,
      };
    })
    .finally(() => {
      runing.value = false;
    });
};

 const askTutor = async () => {
   if (!tutorQuestion.value.trim()) {
     message.warning('请输入你的问题');
     return;
   }
   tutorLoading.value = true;

   const q = tutorQuestion.value;
   const err = tutorRuntimeError.value;
   tutorMessages.value.push({
     role: 'user',
     content: q,
     error: err,
     time: Date.now(),
   });

   Axios.post(`/problem/${id.value}/tutor/`, {
     question: tutorQuestion.value,
     language: submitData.value.language,
     code: submitData.value.source,
     error: tutorRuntimeError.value,
     session_id: tutorSessionId.value,
   })
     .then(res => {
      tutorAnswer.value = res.content;
      if (res.session_id) tutorSessionId.value = res.session_id;
      tutorMessages.value.push({
        role: 'assistant',
        content: res.content,
        time: Date.now(),
      });
      tutorQuestion.value = '';
     })
     .finally(() => {
       tutorLoading.value = false;
     });
 };

 const clearTutor = () => {
   tutorQuestion.value = '';
   tutorRuntimeError.value = '';
   tutorAnswer.value = '';
 };

 const startNewTutorSession = () => {
   tutorSessionId.value = '';
   tutorMessages.value = [];
   clearTutor();
 };

const getTextOrPlaceholder = (val, placeholder) => {
  const s = (val ?? '').toString().trim();
  return s ? s : placeholder;
};

const normalizeCodeText = (val) => {
  if (val === null || val === undefined) return '';
  return val.toString().replace(/\r\n/g, '\n').trimEnd();
};

const generateProblemMarkdown = () => {
  const pd = problemData.value || {};

  const rawBackground = (pd.background ?? '').toString().trim();
  const rawDescription = (pd.description ?? '').toString().trim();
  const rawInputFormat = (pd.input_format ?? '').toString().trim();
  const rawOutputFormat = (pd.output_format ?? '').toString().trim();
  const rawHint = (pd.hint ?? '').toString().trim();

  const samples = Array.isArray(pd.samples) ? pd.samples : [];
  const validSamples = samples
    .filter(item => item && (item.input || item.output))
    .map(item => ({
      index: item.index,
      input: normalizeCodeText(item.input),
      output: normalizeCodeText(item.output),
      explanation: normalizeCodeText(
        item.explain ?? item.explanation ?? item.analysis ?? ''
      ).trim(),
    }))
    .filter(item => item.input.trim() || item.output.trim());

  let md = '';

  if (rawBackground) {
    md += `## 题目背景\n\n${rawBackground}\n\n`;
  }

  if (rawDescription) {
    md += `## 题目描述\n\n${rawDescription}\n\n`;
  }

  if (rawInputFormat) {
    md += `## 输入格式\n\n${rawInputFormat}\n\n`;
  }

  if (rawOutputFormat) {
    md += `## 输出格式\n\n${rawOutputFormat}\n\n`;
  }

  if (validSamples.length) {
    md += `## 样例\n\n`;
    validSamples.forEach((item, i) => {
      const idx = item.index || i + 1;
      md += `\`\`\`input${idx}\n${item.input}\n\`\`\`\n\n`;
      md += `\`\`\`output${idx}\n${item.output}\n\`\`\`\n\n`;

      if (item.explanation) {
        md += `### 解释#${idx}\n\n${item.explanation}\n\n`;
      }
    });
  }

  if (rawHint) {
    md += `## 数据范围\n\n${rawHint}\n`;
  }

  return md.trimEnd() + '\n';
};

const copy = (text, event = undefined) => {
  if (event) event.stopPropagation();
  const input = document.createElement('textarea');
  input.value = text;
  document.body.appendChild(input);
  input.select();
  document.execCommand('copy');
  document.body.removeChild(input);
  message.success('复制成功');
};

const copyProblemMarkdown = (event) => {
  copy(generateProblemMarkdown(), event);
};

const downloadProblemFile = file => {
  const url = `/api/problem/${id.value}/file/${file.name}/`;
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', file.name);
  document.body.appendChild(link);
  link.click();
};
</script>


<template>
  <div class="problem-page">
    <section class="problem-hero">
      <div class="hero-orb hero-orb-a" />
      <div class="hero-orb hero-orb-b" />
      <div class="problem-hero-main">
        <n-tag :bordered="false" type="info" round>题目 #{{ problemData.id }}</n-tag>
        <h1 class="problem-title">{{ problemData.title }}</h1>
        <n-space size="small" class="hero-meta">
          <n-tag :bordered="false" type="success">
            {{ problemData.time_limit }} ms
            <template #icon>
              <n-icon :component="AccessTimeOutlined" />
            </template>
          </n-tag>
          <n-tag :bordered="false" type="warning">
            {{ problemData.memory_limit }} MB
            <template #icon>
              <n-icon :component="MemoryOutlined" />
            </template>
          </n-tag>
          <n-tag v-for="item in problemData.tags" :key="item.id">{{ item.name }}</n-tag>
        </n-space>
      </div>
      <n-space class="problem-hero-actions">
        <n-button :disabled="!prevProblemId" @click="goToPrevProblem">
          <template #icon>
            <n-icon :component="ArrowBackOutlined" />
          </template>
          上一题
        </n-button>
        <n-button :disabled="!nextProblemId" @click="goToNextProblem">
          下一题
          <template #icon>
            <n-icon :component="ArrowForwardOutlined" />
          </template>
        </n-button>
      </n-space>
    </section>

    <n-card class="problem-tabs-card" :bordered="false">
      <n-tabs type="line" size="large" :tabs-padding="20" @before-leave="beforeLeave">
        <n-tab-pane name="description" tab="题目描述">
          <div class="description-pane">
            <div class="description-toolbar">
              <n-space size="small">
                <n-button size="small" @click="copyProblemMarkdown">复制 Markdown</n-button>
              </n-space>
            </div>

            <section v-if="problemData.background" class="problem-section">
              <h2>题目背景</h2>
              <n-card class="content-card">
                <MdEditor :content="problemData.background" previewOnly />
              </n-card>
            </section>

            <section v-if="problemData.description" class="problem-section">
              <h2>题目描述</h2>
              <n-card class="content-card">
                <MdEditor :content="problemData.description" previewOnly />
              </n-card>
            </section>

            <section v-if="problemData.input_format" class="problem-section">
              <h2>输入格式</h2>
              <n-card class="content-card">
                <MdEditor :content="problemData.input_format" previewOnly />
              </n-card>
            </section>

            <section v-if="problemData.output_format" class="problem-section">
              <h2>输出格式</h2>
              <n-card class="content-card">
                <MdEditor :content="problemData.output_format" previewOnly />
              </n-card>
            </section>

            <section
              v-if="problemData.samples && problemData.samples.some(item => item.input || item.output)"
              class="problem-section"
            >
              <h2>样例</h2>
              <n-space vertical size="large">
                <n-card
                  v-for="item in problemData.samples"
                  :key="item.index"
                  v-show="item.input || item.output"
                  class="sample-card"
                >
                  <div class="sample-grid">
                    <div class="sample-col sample-block">
                      <h3>
                        样例输入 #{{ item.index }}
                        <n-button size="small" class="copy-button" @click="event => copy(item.input)">复制</n-button>
                      </h3>
                      <CodeWithCard :code="item.input" />
                    </div>
                    <div class="sample-col sample-block">
                      <h3>
                        样例输出 #{{ item.index }}
                        <n-button size="small" class="copy-button" @click="event => copy(item.output)">复制</n-button>
                      </h3>
                      <CodeWithCard :code="item.output" />
                    </div>
                  </div>
                </n-card>
              </n-space>
            </section>

            <section v-if="problemData.hint" class="problem-section">
              <h2>提示/数据范围</h2>
              <n-card class="content-card">
                <MdEditor :content="problemData.hint" previewOnly />
              </n-card>
            </section>

            <section v-if="problemData.files && problemData.files.length" class="problem-section">
              <h2>文件</h2>
              <n-upload
                abstract
                :default-file-list="problemData.files || []"
                :show-remove-button="false"
                show-download-button
                @download="downloadProblemFile"
              >
                <n-card class="content-card">
                  <n-upload-file-list />
                </n-card>
              </n-upload>
            </section>

            <section class="problem-section compiler-section">
              <h2>在线编译器</h2>
              <n-alert v-if="problemData.judge_mode === 'leetcode'" type="info" style="margin-bottom: 12px">
                当前题目为 LeetCode 函数模式：请只填写函数实现，系统会自动拼接模板后判题。
              </n-alert>
              <n-alert v-if="!problemData.allow_submit" type="warning" style="margin-bottom: 12px">
                当前题目暂不可提交，但可以使用在线运行功能调试代码。
              </n-alert>
              <n-row :gutter="16" class="panel-row">
                <n-col :span="16">
                  <n-card class="panel-card" :bordered="false">
                    <CodeMirror
                  v-model:code="submitData.source"
                  :language="submitData.language"
                  :tab-size="compilerIndentSize"
                  :indent-unit="compilerIndentSize"
                  :indent-with-tab="false"
                  :autofocus="false"
                />
                  </n-card>
                </n-col>
                <n-col :span="8">
                  <n-card class="panel-card" :bordered="false">
                    <n-space vertical size="large" class="submit-setting">
                      <div>
                        <h3>缩进</h3>
                        <n-select v-model:value="compilerIndentSize" size="large" :options="indentOptions" />
                      </div>
                      <div>
                        <h3>语言</h3>
                        <n-select v-model:value="submitData.language" size="large" :options="languageOptions" />
                      </div>
                      <div>
                        <h3>自定义输入</h3>
                        <n-input
                          v-model:value="runInput"
                          type="textarea"
                          :rows="4"
                          :placeholder="problemData.judge_mode === 'leetcode' ? 'LeetCode 模式通常不需要 stdin，若模板支持可填写。' : '输入程序运行时的 stdin 内容'"
                        />
                      </div>
                      <div v-if="problemData.judge_mode === 'leetcode'">
                        <n-alert type="info" :show-icon="false" class="run-tip">
                          点击“运行代码”时会自动拼接当前题目的 LeetCode 模板再执行。
                        </n-alert>
                      </div>
                      <n-space>
                        <n-button
                          size="large"
                          type="default"
                          @click="runCode"
                          :loading="runing"
                          :disabled="runing || submiting"
                        >
                          运行代码
                        </n-button>
                        <n-button
                          type="primary"
                          size="large"
                          class="run-submit-btn"
                          @click="submit"
                          :loading="submiting"
                          :disabled="submiting || runing || !problemData.allow_submit"
                        >
                          提交
                        </n-button>
                      </n-space>
                      <div class="run-result" v-if="runing || runResult.phase || runResult.error || runResult.output">
                        <h3>运行结果</h3>
                        <n-tag v-if="runing" type="info">运行中...</n-tag>
                        <n-tag v-else-if="runResult.ok" type="success">运行成功</n-tag>
                        <n-tag v-else type="error">
                          {{ runResult.phase === 'compile' ? '编译错误' : '运行失败' }}
                        </n-tag>
                        <n-tag v-if="runResult.wrapped" type="warning" style="margin-left: 8px">LeetCode 模板已拼接</n-tag>
                        <div v-if="runResult.error" class="run-result-block">
                          <h4>错误输出</h4>
                          <CodeWithCard :code="runResult.error" />
                        </div>
                        <div class="run-result-block" v-if="runResult.output">
                          <h4>标准输出</h4>
                          <CodeWithCard :code="runResult.output" />
                        </div>
                        <div class="run-result-block" v-if="!runing && !runResult.error && !runResult.output">
                          <CodeWithCard code="(无输出)" />
                        </div>
                      </div>
                      <div>
                        <h3>是否隐藏</h3>
                        <n-switch v-model:value="submitData._is_hidden" size="large" />
                      </div>
                      <Captcha scene="submission" v-model:captcha="submitData.captcha" ref="captchaRef" />
                    </n-space>
                  </n-card>
                </n-col>
              </n-row>
            </section>
          </div>
        </n-tab-pane>

        <n-tab-pane name="submit" tab="提交" :disabled="!problemData.allow_submit">
          <n-row :gutter="16" class="panel-row">
            <n-col :span="16">
              <n-card class="panel-card" :bordered="false">
                <CodeMirror
                  v-model:code="submitData.source"
                  :language="submitData.language"
                  :tab-size="compilerIndentSize"
                  :indent-unit="compilerIndentSize"
                  :indent-with-tab="false"
                  :autofocus="false"
                />
              </n-card>
            </n-col>
            <n-col :span="8">
              <n-card class="panel-card" :bordered="false">
                <n-space vertical size="large" class="submit-setting">
                  <div>
                    <h3>缩进</h3>
                    <n-select v-model:value="compilerIndentSize" size="large" :options="indentOptions" />
                  </div>
                  <div>
                    <h3>语言</h3>
                    <n-select v-model:value="submitData.language" size="large" :options="languageOptions" />
                  </div>
                  <div>
                    <h3>自定义输入</h3>
                    <n-input
                      v-model:value="runInput"
                      type="textarea"
                      :rows="4"
                      :placeholder="problemData.judge_mode === 'leetcode' ? 'LeetCode 模式通常不需要 stdin，若模板支持可填写。' : '输入程序运行时的 stdin 内容'"
                    />
                  </div>
                  <div v-if="problemData.judge_mode === 'leetcode'">
                    <n-alert type="info" :show-icon="false" class="run-tip">
                      点击“运行代码”时会自动拼接当前题目的 LeetCode 模板再执行。
                    </n-alert>
                  </div>
                  <n-space>
                    <n-button
                      size="large"
                      type="default"
                      @click="runCode"
                      :loading="runing"
                      :disabled="runing || submiting"
                    >
                      运行代码
                    </n-button>
                    <n-button
                      type="primary"
                      size="large"
                      class="run-submit-btn"
                      @click="submit"
                      :loading="submiting"
                      :disabled="submiting || runing || !problemData.allow_submit"
                    >
                      提交
                    </n-button>
                  </n-space>
                  <div class="run-result" v-if="runing || runResult.phase || runResult.error || runResult.output">
                    <h3>运行结果</h3>
                    <n-tag v-if="runing" type="info">运行中...</n-tag>
                    <n-tag v-else-if="runResult.ok" type="success">运行成功</n-tag>
                    <n-tag v-else type="error">
                      {{ runResult.phase === 'compile' ? '编译错误' : '运行失败' }}
                    </n-tag>
                    <n-tag v-if="runResult.wrapped" type="warning" style="margin-left: 8px">LeetCode 模板已拼接</n-tag>
                    <div v-if="runResult.error" class="run-result-block">
                      <h4>错误输出</h4>
                      <CodeWithCard :code="runResult.error" />
                    </div>
                    <div class="run-result-block" v-if="runResult.output">
                      <h4>标准输出</h4>
                      <CodeWithCard :code="runResult.output" />
                    </div>
                    <div class="run-result-block" v-if="!runing && !runResult.error && !runResult.output">
                      <CodeWithCard code="(无输出)" />
                    </div>
                  </div>
                  <div>
                    <h3>是否隐藏</h3>
                    <n-switch v-model:value="submitData._is_hidden" size="large" />
                  </div>
                  <Captcha scene="submission" v-model:captcha="submitData.captcha" ref="submitTabCaptchaRef" />
                </n-space>
              </n-card>
            </n-col>
          </n-row>
        </n-tab-pane>

        <n-tab-pane name="blockly" tab="积木" :disabled="!problemData.allow_submit">
          <n-row :gutter="16" class="panel-row">
            <n-col :span="16">
              <n-card class="panel-card" :bordered="false">
                <BlocklyEditor v-model:workspaceXml="blocklyWorkspaceXml" v-model:code="blocklyCode" />
              </n-card>
            </n-col>
            <n-col :span="8">
              <n-card class="panel-card" :bordered="false">
                <n-space vertical size="large" class="submit-setting">
                  <div>
                    <h3>生成的 C++（只读）</h3>
                    <CodeWithCard :code="blocklyCode" />
                  </div>
                  <div v-if="blocklyDraftSaving">
                    <n-tag type="info">草稿保存中...</n-tag>
                  </div>
                  <div>
                    <h3>是否隐藏</h3>
                    <n-switch v-model:value="blocklySubmitData._is_hidden" size="large" />
                  </div>
                  <Captcha scene="submission" v-model:captcha="blocklySubmitData.captcha" ref="blocklyCaptchaRef" />
                  <n-button
                    type="primary"
                    size="large"
                    class="submit-btn"
                    @click="submitBlockly"
                    :loading="submiting"
                    :disabled="submiting"
                  >
                    提交（C++）
                  </n-button>
                </n-space>
              </n-card>
            </n-col>
          </n-row>
        </n-tab-pane>

        <n-tab-pane name="tutor" tab="AI助教">
          <n-row :gutter="16" class="panel-row">
            <n-col :span="10">
              <n-card class="panel-card" :bordered="false">
                <n-space vertical size="large">
                  <div>
                    <h3>你卡在哪？</h3>
                    <n-input
                      v-model:value="tutorQuestion"
                      type="textarea"
                      :rows="6"
                      placeholder="描述你的思路、你认为哪里不对、你希望得到什么提示..."
                    />
                  </div>
                  <div>
                    <h3>报错信息（可选）</h3>
                    <n-input
                      v-model:value="tutorRuntimeError"
                      type="textarea"
                      :rows="4"
                      placeholder="粘贴编译错误/运行错误/输出不对等信息"
                    />
                  </div>
                  <n-space>
                    <n-button type="primary" @click="askTutor" :loading="tutorLoading" :disabled="tutorLoading">获取提示</n-button>
                    <n-button @click="startNewTutorSession" :disabled="tutorLoading">新会话</n-button>
                    <n-button @click="clearTutor" :disabled="tutorLoading">清空</n-button>
                  </n-space>
                  <n-alert type="info">AI 只会给思路与引导，不会直接提供可 AC 的完整代码。</n-alert>
                </n-space>
              </n-card>
            </n-col>
            <n-col :span="14">
              <n-card title="AI 提示" class="panel-card" :content-style="{ padding: '0 20px' }" :bordered="false">
                <div v-if="tutorMessages.length">
                  <n-space vertical size="large" style="padding: 12px 0">
                    <div v-for="(m, idx) in tutorMessages" :key="idx">
                      <h3 v-if="m.role === 'user'">我</h3>
                      <h3 v-else>AI</h3>
                      <div v-if="m.role === 'user'" style="white-space: pre-wrap">
                        {{ m.content }}
                        <div v-if="m.error" style="margin-top: 8px">
                          <n-tag type="warning">报错</n-tag>
                          <div style="white-space: pre-wrap; margin-top: 6px">{{ m.error }}</div>
                        </div>
                      </div>
                      <div v-else>
                        <MdEditor :content="m.content" previewOnly />
                      </div>
                    </div>
                  </n-space>
                </div>
                <div v-else>
                  <n-empty description="还没有对话" />
                </div>
              </n-card>
            </n-col>
          </n-row>
        </n-tab-pane>

        <n-tab-pane name="submission" tab="提交记录" />
        <n-tab-pane name="discussion" tab="讨论" :disabled="problemData.hide_discussions" />
        <n-tab-pane name="edit" tab="修改题目" v-if="store.state.user.permissions.includes('problem')" />
      </n-tabs>
    </n-card>
  </div>
</template>

<style lang="scss" scoped>
.problem-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.problem-hero {
  position: relative;
  overflow: hidden;
  border-radius: 24px;
  padding: 28px;
  background: linear-gradient(130deg, #1f4e79 0%, #2f6ba0 60%, #4b86bb 100%);
  box-shadow: 0 16px 40px rgba(31, 78, 121, 0.28);
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 14px;
}

.hero-orb {
  position: absolute;
  border-radius: 999px;
  pointer-events: none;
}

.hero-orb-a {
  width: 260px;
  height: 260px;
  right: -80px;
  top: -110px;
  background: radial-gradient(circle, rgba(191, 231, 255, 0.42) 0%, rgba(191, 231, 255, 0) 68%);
}

.hero-orb-b {
  width: 220px;
  height: 220px;
  left: -70px;
  bottom: -120px;
  background: radial-gradient(circle, rgba(189, 242, 212, 0.3) 0%, rgba(189, 242, 212, 0) 72%);
}

.problem-hero-main,
.problem-hero-actions {
  position: relative;
  z-index: 1;
}

.problem-title {
  margin: 14px 0;
  font-size: 40px;
  line-height: 1.12;
  color: #f8fafc;
  font-weight: 800;
}

.hero-meta :deep(.n-tag) {
  background: rgba(12, 33, 52, 0.26);
  border: 1px solid rgba(255, 255, 255, 0.22);
  color: #f8fafc;
}

.problem-hero-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.problem-hero-actions :deep(.n-button) {
  background: rgba(12, 33, 52, 0.24);
  border-color: rgba(226, 232, 240, 0.42);
}

.problem-hero-actions :deep(.n-button .n-button__content),
.problem-hero-actions :deep(.n-button .n-icon) {
  color: #eef6ff;
}

.problem-tabs-card {
  border-radius: 18px;
  border: 1px solid #d8e4f0;
  box-shadow: 0 14px 34px rgba(15, 23, 42, 0.08);
  background: linear-gradient(180deg, #f9fcff 0%, #f4f8fd 100%);
}

.problem-tabs-card :deep(.n-card__content) {
  background: transparent;
}

.description-pane {
  padding: 18px 10px 20px;
  border-radius: 16px;
  background: linear-gradient(180deg, rgba(255, 253, 248, 0.95) 0%, rgba(252, 248, 240, 0.92) 100%);
  border: 1px solid #e7decc;
}

.description-toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 12px;
}

.problem-section {
  margin-bottom: 20px;
}

.problem-section h2 {
  margin: 0 0 12px;
  font-size: 30px;
  font-weight: 800;
  color: #1e4d73;
  display: flex;
  align-items: center;
  gap: 10px;
}

.problem-section h2::before {
  content: '';
  width: 6px;
  height: 26px;
  border-radius: 999px;
  background: linear-gradient(180deg, #5fa7da 0%, #2f6ba0 100%);
}

.content-card,
.panel-card,
.sample-card {
  border-radius: 16px;
  border: 1px solid #e8decb;
  box-shadow: 0 8px 22px rgba(61, 78, 96, 0.08);
  background: #fffdf8;
}

.content-card :deep(.n-card__content) {
  padding: 12px 20px;
}

.content-card :deep(.md-editor-v3),
.content-card :deep(.md-editor-v3 .md-editor-preview-wrapper),
.content-card :deep(.md-editor-v3 .md-preview),
.content-card :deep(.md-editor-v3 .github-theme) {
  background: transparent !important;
}

.content-card :deep(.md-editor-v3 .md-preview) {
  font-size: 24px;
  line-height: 1.9;
  color: #26384a !important;
}

.content-card :deep(.md-editor-v3 .md-preview p),
.content-card :deep(.md-editor-v3 .md-preview li),
.content-card :deep(.md-editor-v3 .md-preview div) {
  color: #26384a !important;
}

.content-card :deep(.md-editor-v3 .md-preview code) {
  background: #eef2f6;
  border: 1px solid #dfe6ee;
  border-radius: 6px;
  padding: 2px 6px;
}

.content-card :deep(.md-editor-v3 .md-preview pre code) {
  background: transparent;
  border: none;
  padding: 0;
}

.sample-card :deep(.n-card__content) {
  padding: 12px;
}

.sample-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.sample-block {
  border-radius: 12px;
  border: 1px solid #e7dcc8;
  background: linear-gradient(180deg, #fffdfa 0%, #fff8ee 100%);
  padding: 12px;
}

.sample-col h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 10px;
  color: #22547f;
  font-size: 28px;
}

.copy-button {
  margin-left: auto;
}

.panel-row {
  padding: 8px 0 14px;
}

.submit-setting h3 {
  margin: 10px 0;
  color: #25567f;
}

.run-tip {
  margin-top: 2px;
}

.run-result {
  border-top: 1px solid #e8decb;
  padding-top: 10px;
}

.run-result-block {
  margin-top: 8px;
}

.run-result-block h4 {
  margin: 0 0 8px;
  color: #25567f;
}

.run-submit-btn {
  margin-top: 0;
}

.submit-btn {
  width: 100%;
  margin-top: 10px;
}

@media (max-width: 1200px) {
  .sample-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 900px) {
  .problem-hero {
    padding: 20px;
    border-radius: 18px;
    flex-direction: column;
    align-items: flex-start;
  }

  .problem-title {
    font-size: 30px;
  }

  .problem-section h2 {
    font-size: 24px;
  }

  .content-card :deep(.md-editor-v3 .md-preview) {
    font-size: 20px;
    line-height: 1.75;
  }

  .sample-col h3 {
    font-size: 22px;
  }
}
</style>
