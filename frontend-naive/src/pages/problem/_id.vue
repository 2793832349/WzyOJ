<script setup>
import { ref, watch } from 'vue';
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
import { MemoryOutlined, AccessTimeOutlined } from '@vicons/material';
import Captcha from '../../components/captcha.vue';

const route = useRoute(),
  message = useMessage();
const id = route.params.id,
  problemData = ref({});

const loadData = () => {
  Axios.get(`/problem/${id}/`)
    .then(res => {
      res.files = res.files.map(file => ({
        name: file,
        status: 'finished',
      }));
      problemData.value = res;
    })
    .catch(() => {
      message.error('题目不存在或暂时无法查看！');
      router.push({ name: 'problem_list' });
    });
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
    problem_id: id,
    source: blocklyCode.value,
    language,
    _is_hidden: blocklySubmitData.value._is_hidden,
    captcha: blocklySubmitData.value.captcha,
  })
    .then(res => {
      store.commit('setSubmitLanguage', language);
      router.push({ name: 'submission_detail', params: { id: res.id } });
    })
    .finally(() => {
      submiting.value = false;
    });
};

loadData();

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
  Axios.get(`/problem/${id}/blockly-draft/`)
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
    Axios.put(`/problem/${id}/blockly-draft/`, { workspace_xml: val })
      .finally(() => {
        blocklyDraftSaving.value = false;
      });
  }, 1000);
});

const beforeLeave = tabName => {
  if (tabName === 'submission') {
    router.push({
      name: 'submission_list',
      query: { problem__id: id },
    });
    return false;
  } else if (tabName === 'discussion') {
    router.push({
      name: 'discussion_list',
      query: { related_problem__id: id },
    });
    return false;
  } else if (tabName === 'edit') {
    router.push({
      name: 'problem_edit',
      params: { id },
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
  captchaRef = ref(null),
  submiting = ref(false);

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
  if (!(await captchaRef.value.checkCaptcha())) return;
  submiting.value = true;
  Axios.post('/submission/', { problem_id: id, ...submitData.value })
    .then(res => {
      store.commit('setSubmitLanguage', submitData.value.language);
      router.push({ name: 'submission_detail', params: { id: res.id } });
    })
    .finally(() => {
      submiting.value = false;
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

   Axios.post(`/problem/${id}/tutor/`, {
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
  const description = getTextOrPlaceholder(
    pd.description,
    '多个自然段之间空一行。\n\n这样题面会更美观。'
  );
  const inputFormat = getTextOrPlaceholder(
    pd.input_format,
    '第一行一个整数 $n$。\n\n接下来一行 $n$ 个整数，表示.....。'
  );
  const outputFormat = getTextOrPlaceholder(
    pd.output_format,
    '输出一个整数，表示.....。'
  );

  let md = '';
  if (rawBackground) {
    md += `## 题目背景\n\n${rawBackground}\n\n`;
  }
  md += `## 题目描述\n\n${description}\n\n## 输入格式 \n\n${inputFormat}\n\n## 输出格式\n\n${outputFormat}\n\n## 样例\n\n`;

  const samples = Array.isArray(pd.samples) ? pd.samples : [];
  const validSamples = samples
    .filter(item => item && (item.input || item.output))
    .map(item => ({
      index: item.index,
      input: normalizeCodeText(item.input),
      output: normalizeCodeText(item.output),
    }))
    .filter(item => item.input.trim() || item.output.trim());

  if (validSamples.length) {
    validSamples.forEach((item, i) => {
      const idx = item.index || i + 1;
      md += `\`\`\`input${idx}\n${item.input}\n\`\`\`\n\n`;
      md += `\`\`\`output${idx}\n${item.output}\n\`\`\`\n\n`;

      const explanation = normalizeCodeText(
        item.explain ?? item.explanation ?? item.analysis ?? ''
      ).trim();
      if (explanation) {
        md += `### 解释#${idx}\n\n${explanation}\n\n`;
      }
    });
  } else {
    md += `\`\`\`input1\n5\n1 2 3 4 5\n\`\`\`\n\n`;
    md += `\`\`\`output1\n15\n\`\`\`\n\n`;
    md += `\`\`\`input2\n10\n1 2 3 4 5 6 7 8 9 10\n\`\`\`\n\n`;
    md += `\`\`\`output2\n55\n\`\`\`\n\n`;
  }

  // 只有当题目有 hint（数据范围）时才添加数据范围部分
  const hint = (pd.hint ?? '').toString().trim();
  if (hint) {
    md += `## 数据范围\n\n${hint}\n`;
  }

  return md;
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
  const url = `/api/problem/${id}/file/${file.name}/`;
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', file.name);
  document.body.appendChild(link);
  link.click();
};
</script>

<template>
  <h1>#{{ problemData.id }}&ensp;{{ problemData.title }}</h1>
  <n-layout has-sider>
    <n-layout-content>
      <n-tabs
        type="line"
        size="large"
        :tabs-padding="20"
        @before-leave="beforeLeave"
      >
        <n-tab-pane name="description" tab="题目描述">
          <n-space vertical size="large">
            <div />

            <div>
              <n-space size="small">
                <n-tag :bordered="false">
                  {{ problemData.time_limit }} ms
                  <template #icon>
                    <n-icon :component="AccessTimeOutlined" />
                  </template>
                </n-tag>
                <n-tag :bordered="false">
                  {{ problemData.memory_limit }} MB
                  <template #icon>
                    <n-icon :component="MemoryOutlined" />
                  </template>
                </n-tag>
                <n-tag v-for="item in problemData.tags" :key="item.id">
                  {{ item.name }}
                </n-tag>
                <n-button size="small" @click="copyProblemMarkdown">
                  复制 Markdown
                </n-button>
              </n-space>
            </div>

            <div v-if="problemData.background">
              <h2>题目背景</h2>
              <n-card class="description">
                <MdEditor :content="problemData.background" previewOnly />
              </n-card>
            </div>

            <div v-if="problemData.description">
              <h2>题目描述</h2>
              <n-card class="description">
                <MdEditor :content="problemData.description" previewOnly />
              </n-card>
            </div>

            <div v-if="problemData.input_format">
              <h2>输入格式</h2>
              <n-card class="description">
                <MdEditor :content="problemData.input_format" previewOnly />
              </n-card>
            </div>

            <div v-if="problemData.output_format">
              <h2>输出格式</h2>
              <n-card class="description">
                <MdEditor :content="problemData.output_format" previewOnly />
              </n-card>
            </div>

            <div
              v-if="
                problemData.samples &&
                problemData.samples.some(item => item.input || item.output)
              "
            >
              <h2>样例</h2>
              <div
                v-for="item in problemData.samples"
                :key="item.index"
                style="width: 100%"
              >
                <n-row v-if="item.input || item.output" :gutter="12">
                  <n-col :span="11">
                    <h3>
                      样例输入 #{{ item.index }}
                      <n-button
                        size="small"
                        class="copy-button"
                        @click="event => copy(item.input)"
                      >
                        复制
                      </n-button>
                    </h3>
                    <CodeWithCard :code="item.input" />
                  </n-col>
                  <n-col :span="2"></n-col>
                  <n-col :span="11">
                    <h3>
                      样例输出 #{{ item.index }}
                      <n-button
                        size="small"
                        class="copy-button"
                        @click="event => copy(item.output)"
                      >
                        复制
                      </n-button>
                    </h3>
                    <CodeWithCard :code="item.output" />
                  </n-col>
                </n-row>
              </div>
            </div>

            <div v-if="problemData.hint">
              <h2>提示/数据范围</h2>
              <n-card class="description">
                <MdEditor :content="problemData.hint" previewOnly />
              </n-card>
            </div>
            <div v-if="problemData.files && problemData.files.length">
              <h2>文件</h2>
              <n-upload
                abstract
                :default-file-list="problemData.files || []"
                :show-remove-button="false"
                show-download-button
                @download="downloadProblemFile"
              >
                <n-card>
                  <n-upload-file-list />
                </n-card>
              </n-upload>
            </div>
          </n-space>
        </n-tab-pane>
        <n-tab-pane
          name="submit"
          tab="提交"
          :disabled="!problemData.allow_submit"
        >
          <n-row>
            <n-col :span="16" style="padding: 0 25px">
              <CodeMirror
                v-model:code="submitData.source"
                :language="submitData.language"
              />
            </n-col>
            <n-col :span="8" style="padding: 0 25px">
              <n-space vertical size="large" class="submit-setting">
                <div>
                  <h3>语言</h3>
                  <n-select
                    v-model:value="submitData.language"
                    size="large"
                    :options="languageOptions"
                  />
                </div>
                <div>
                  <h3>是否隐藏</h3>
                  <n-switch
                    v-model:value="submitData._is_hidden"
                    size="large"
                  />
                </div>
                <Captcha
                  scene="submission"
                  v-model:captcha="submitData.captcha"
                  ref="captchaRef"
                />
                <n-button
                  type="primary"
                  size="large"
                  style="width: 100%; margin-top: 10px"
                  @click="submit"
                  :loading="submiting"
                  :disabled="submiting"
                >
                  提交
                </n-button>
              </n-space>
            </n-col>
          </n-row>
        </n-tab-pane>
        <n-tab-pane
          name="blockly"
          tab="积木"
          :disabled="!problemData.allow_submit"
        >
          <n-row :gutter="12">
            <n-col :span="16" style="padding: 0 25px">
              <BlocklyEditor
                v-model:workspaceXml="blocklyWorkspaceXml"
                v-model:code="blocklyCode"
              />
            </n-col>
            <n-col :span="8" style="padding: 0 25px">
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
                <Captcha
                  scene="submission"
                  v-model:captcha="blocklySubmitData.captcha"
                  ref="blocklyCaptchaRef"
                />
                <n-button
                  type="primary"
                  size="large"
                  style="width: 100%; margin-top: 10px"
                  @click="submitBlockly"
                  :loading="submiting"
                  :disabled="submiting"
                >
                  提交（C++）
                </n-button>
              </n-space>
            </n-col>
          </n-row>
        </n-tab-pane>
        <n-tab-pane name="tutor" tab="AI助教">
          <n-row :gutter="16">
            <n-col :span="10" style="padding: 0 25px">
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
                  <n-button type="primary" @click="askTutor" :loading="tutorLoading" :disabled="tutorLoading">
                    获取提示
                  </n-button>
                  <n-button @click="startNewTutorSession" :disabled="tutorLoading">
                    新会话
                  </n-button>
                  <n-button
                    @click="clearTutor"
                    :disabled="tutorLoading"
                  >
                    清空
                  </n-button>
                </n-space>
                <n-alert type="info">
                  AI 只会给思路与引导，不会直接提供可 AC 的完整代码。
                </n-alert>
              </n-space>
            </n-col>
            <n-col :span="14" style="padding: 0 25px">
              <n-card title="AI 提示" :content-style="{ padding: '0 20px' }">
                <div v-if="tutorMessages.length">
                  <n-space vertical size="large" style="padding: 12px 0">
                    <div v-for="(m, idx) in tutorMessages" :key="idx">
                      <h3 v-if="m.role === 'user'">我</h3>
                      <h3 v-else>AI</h3>
                      <div v-if="m.role === 'user'" style="white-space: pre-wrap">
                        {{ m.content }}
                        <div v-if="m.error" style="margin-top: 8px">
                          <n-tag type="warning">报错</n-tag>
                          <div style="white-space: pre-wrap; margin-top: 6px">
                            {{ m.error }}
                          </div>
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
        <n-tab-pane
          name="discussion"
          tab="讨论"
          :disabled="problemData.hide_discussions"
        />
        <n-tab-pane
          name="edit"
          tab="修改题目"
          v-if="store.state.user.permissions.includes('problem')"
        />
      </n-tabs>
    </n-layout-content>
  </n-layout>
</template>

<style lang="scss" scoped>
.n-layout-content,
.n-layout-sider {
  margin: 20px !important;
}

.description {
  :deep(.n-card__content) {
    padding: 0 20px !important;
    margin: 0 10px !important;
  }
}

.copy-button {
  margin-left: 10px;
}

.submit-setting {
  h3 {
    margin: 10px 0;
  }
}
</style>
