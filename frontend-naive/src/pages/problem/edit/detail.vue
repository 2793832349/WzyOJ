<script setup>
import { ref } from 'vue';
import Axios from '@/plugins/axios';
import { difficultyOptions } from '@/plugins/consts';
import MdEditor from '@/components/MdEditor.vue';
import router from '@/router';
import { useRoute } from 'vue-router';
import { useStore } from 'vuex';

const route = useRoute(),
  message = useMessage(),
  store = useStore();
const id = route.params.id;

const getToken = () => {
  return store.state.user.token || '';
};

const createDefaultLeetcodeTemplates = () => ({
  c: { prepend: '', append: '', starter: '' },
  cpp: { prepend: '', append: '', starter: '' },
  python3: { prepend: '', append: '', starter: '' },
});

const normalizeLeetcodeTemplates = (raw) => {
  const base = createDefaultLeetcodeTemplates();
  if (!raw || typeof raw !== 'object') return base;
  ['c', 'cpp', 'python3'].forEach((lang) => {
    const item = raw[lang] || {};
    base[lang] = {
      prepend: String(item.prepend || ''),
      append: String(item.append || ''),
      starter: String(item.starter || ''),
    };
  });
  return base;
};
const applyLeetcodeTemplatePreset = () => {
  problem.value.leetcode_templates = {
    c: {
      prepend: `#include <stdio.h>

// TODO: 按题目定义函数签名
int solve(int n) {
    return 0;
}
`,
      append: `
int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    printf("%d\\n", solve(n));
    return 0;
}
`,
      starter: `int solve(int n) {
    // TODO
    return 0;
}
`,
    },
    cpp: {
      prepend: `#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    // TODO: 按题目修改参数与返回值
    int solve(int n) {
        return 0;
    }
};
`,
      append: ``,
      starter: `class Solution {
public:
    int solve(int n) {
        // TODO
        return 0;
    }
};
`,
    },
    python3: {
      prepend: `class Solution:\n    def solve(self, n):\n        return 0\n`,
      append: ``,
      starter: `class Solution:\n    def solve(self, n):\n        # TODO\n        return 0\n`,
    },
  };
  message.success('已填充 LeetCode 默认模板，请按题目函数签名调整。');
};

const createDefaultProblem = () => ({
  title: '',
  background: '',
  description: '',
  input_format: '',
  output_format: '',
  samples: [
    { input: '', output: '' },
    { input: '', output: '' },
    { input: '', output: '' },
  ],
  tags: [],
  hint: '',
  memory_limit: 128,
  time_limit: 1000,
  _is_hidden: false,
  _hide_submissions: false,
  _hide_discussions: false,
  _allow_submit: true,
  judge_mode: 'acm',
  leetcode_templates: createDefaultLeetcodeTemplates(),
});

const normalizeProblem = (raw) => ({
  ...createDefaultProblem(),
  ...raw,
  samples: Array.isArray(raw?.samples) && raw.samples.length ? raw.samples : createDefaultProblem().samples,
  tags: Array.isArray(raw?.tags) ? raw.tags : [],
  leetcode_templates: normalizeLeetcodeTemplates(raw?.leetcode_templates),
});

const problem = ref(createDefaultProblem());
const fileList = ref([]);

if (id) {
  Axios.get(`/problem/${id}/`)
    .then(res => {
      const normalized = normalizeProblem({
        ...res,
        tags: (res.tags || []).map(tag => (typeof tag === 'object' ? tag.id : tag)),
      });
      problem.value = normalized;
      fileList.value = (res.files || []).map(file => ({
        name: file,
        status: 'finished',
      }));
    })
    .catch(() => {
      message.error('题目不存在或暂时无法查看！');
      router.push({ name: 'problem_list' });
    });
}

const tagsOptions = ref([]);
Axios.get('/problem/tag/').then(res => {
  tagsOptions.value = res.map(tag => ({ label: tag.name, value: tag.id }));
});

const submiting = ref(false);
const submit = () => {
  if (!problem.value['title']) {
    message.warning(`题目标题不能为空`);
    return;
  }
  submiting.value = true;
  const files = fileList.value
    .filter(file => file.status === 'finished')
    .map(file => file.name);
  const payload = {
    ...problem.value,
    leetcode_templates: normalizeLeetcodeTemplates(problem.value.leetcode_templates),
    files,
  };
  let req;
  if (id) req = Axios.put(`/problem/${id}/`, payload);
  else req = Axios.post('/problem/', payload);
  req
    .then(res => {
      if (!id) router.push({ name: 'problem_detail', params: { id: res.id } });
      else message.success('修改成功');
    })
    .finally(() => {
      submiting.value = false;
    });
};

const handleUploadFinish = ({ file, event }) => {
  const response = JSON.parse(event.target.response);
  if (response.name) {
    message.success('上传成功');
    file.name = response.name;
    file.status = 'finished';
  } else {
    message.error('上传失败');
    file.status = 'error';
  }
};

const removeFile = (file) => {
  // Don't use leading slash - let Axios prepend the baseURL
  const url = `problem/${id}/file/${encodeURIComponent(file.name)}`;
  console.log('Deleting file with URL:', url);
  console.log('Axios baseURL:', Axios.defaults.baseURL);
  console.log('Full URL should be:', Axios.defaults.baseURL + '/' + url);
  
  Axios.delete(url)
    .then(() => {
      message.success('删除成功');
      // Remove from fileList
      const index = fileList.value.findIndex(f => f.name === file.name);
      if (index !== -1) {
        fileList.value.splice(index, 1);
      }
    })
    .catch((error) => {
      console.error('Delete failed:', error);
      console.error('Error config:', error.config);
      console.error('Request URL:', error.config?.url);
      console.error('Request baseURL:', error.config?.baseURL);
      console.error('Request method:', error.config?.method);
      message.error('删除失败');
    });
};

const deleteProblem = () => {
  Axios.delete(`/problem/${id}/`).then(() => {
    message.success('删除成功！');
    router.push({ name: 'problem_list' });
  });
};

const showImportModal = ref(false);
const importText = ref('');

const parseImportText = () => {
  const text = importText.value.trim();
  if (!text) {
    message.warning('请输入题目内容');
    return;
  }

  const lines = text.split('\n');
  let title = '';
  let background = '';
  let description = '';
  let inputFormat = '';
  let outputFormat = '';
  let hint = '';
  const samples = [];

  let currentSection = '';
  let currentContent = [];
  let inFencedSampleBlock = false;

  const sectionMap = {
    '题目背景': 'background',
    '题目描述': 'description',
    '输入格式': 'input_format',
    '输出格式': 'output_format',
    '提示': 'hint',
    '说明/提示': 'hint',
    '数据范围': 'hint',
  };

  const saveCurrentSection = () => {
    let content = currentContent.join("\n");
    // 去掉代码块标记 ```（仅移除标记行，不删除正文首行空格）
    content = content.replace(/^```[^\n]*\n?/gm, "").replace(/\n?```\s*$/gm, "");
    // 仅清理空行，保留每行前导空格
    content = content.replace(/^\n+/, "").replace(/\n+$/, "");
    
    if (currentSection === 'background') background = content;
    else if (currentSection === 'description') description = content;
    else if (currentSection === 'input_format') inputFormat = content;
    else if (currentSection === 'output_format') outputFormat = content;
    else if (currentSection === 'hint') hint = content;
    else if (currentSection.startsWith('sample_input_')) {
      const idx = parseInt(currentSection.replace('sample_input_', '')) - 1;
      if (!samples[idx]) samples[idx] = { input: '', output: '' };
      samples[idx].input = content;
    } else if (currentSection.startsWith('sample_output_')) {
      const idx = parseInt(currentSection.replace('sample_output_', '')) - 1;
      if (!samples[idx]) samples[idx] = { input: '', output: '' };
      samples[idx].output = content;
    }
    currentContent = [];
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // fenced code block 样例 (```input1 / ```output1)
    if (inFencedSampleBlock) {
      if (/^```\s*$/.test(line)) {
        saveCurrentSection();
        currentSection = '';
        inFencedSampleBlock = false;
        continue;
      }
      if (currentSection) {
        currentContent.push(line);
      }
      continue;
    }

    const fencedSampleMatch = line.match(/^```\s*(input|output)\s*#?(\d+)\s*$/i);
    if (fencedSampleMatch) {
      saveCurrentSection();
      const sampleType = fencedSampleMatch[1].toLowerCase();
      const sampleIndex = fencedSampleMatch[2];
      currentSection = `sample_${sampleType}_${sampleIndex}`;
      inFencedSampleBlock = true;
      continue;
    }
    
    // 解析标题 (# P14360 [CSP-J 2025] 多边形)
    const titleMatch = line.match(/^#\s+(?:P\d+\s+)?(.+)$/);
    if (titleMatch && !title) {
      title = titleMatch[1].trim();
      continue;
    }

    // 解析三级标题 (### 输入 #1 或 ### 输出 #1)
    const sampleInputMatch = line.match(/^###\s+输入\s*#?(\d+)/);
    const sampleOutputMatch = line.match(/^###\s+输出\s*#?(\d+)/);
    if (sampleInputMatch) {
      saveCurrentSection();
      currentSection = `sample_input_${sampleInputMatch[1]}`;
      continue;
    }
    if (sampleOutputMatch) {
      saveCurrentSection();
      currentSection = `sample_output_${sampleOutputMatch[1]}`;
      continue;
    }

    // 解析二级标题
    const sectionMatch = line.match(/^##\s+(.+)$/);
    if (sectionMatch) {
      saveCurrentSection();
      const sectionName = sectionMatch[1].trim();
      
      if (sectionMap[sectionName]) {
        currentSection = sectionMap[sectionName];
      } else {
        currentSection = '';
      }
      continue;
    }

    // 普通内容行
    if (currentSection) {
      currentContent.push(line);
    }
  }
  
  // 保存最后一个section
  saveCurrentSection();

  // 填充数据
  if (title) problem.value.title = title;
  if (background) problem.value.background = background;
  if (description) problem.value.description = description;
  if (inputFormat) problem.value.input_format = inputFormat;
  if (outputFormat) problem.value.output_format = outputFormat;
  if (hint) problem.value.hint = hint;
  
  // 填充样例，确保至少有3个
  if (samples.length > 0) {
    while (samples.length < 3) {
      samples.push({ input: '', output: '' });
    }
    problem.value.samples = samples;
  }

  showImportModal.value = false;
  importText.value = '';
  message.success('导入成功！');
};
</script>

<template>
  <n-space vertical size="large">
    <div>
      <n-button type="info" @click="showImportModal = true">
        从文本导入题目
      </n-button>
    </div>
    <div>
      <h2>题目标题</h2>
      <n-input
        v-model:value="problem.title"
        placeholder="请输入标题"
        size="large"
      />
    </div>
    <div>
      <h2>题目背景</h2>
      <MdEditor v-model:content="problem.background" />
    </div>
    <div>
      <h2>题目描述</h2>
      <MdEditor v-model:content="problem.description" />
    </div>
    <div>
      <h2>题目输入</h2>
      <MdEditor v-model:content="problem.input_format" />
    </div>
    <div>
      <h2>题目输出</h2>
      <MdEditor v-model:content="problem.output_format" />
    </div>
    <div>
      <h2>标签</h2>
      <n-select
        v-model:value="problem.tags"
        multiple
        filterable
        placeholder="请选择标签"
        :options="tagsOptions"
      />
    </div>
    <div>
      <h2>样例</h2>
      <n-tabs type="line" animated>
        <n-tab-pane
          v-for="(item, index) in problem.samples"
          :key="index"
          :name="'sample_' + String(index + 1)"
          :tab="'样例 #' + String(index + 1)"
          display-directive="show:lazy"
        >
          <n-row>
            <n-col :span="11">
              <h3>样例输入 #{{ index + 1 }}</h3>
              <n-input v-model:value="item.input" type="textarea" :rows="10" />
            </n-col>
            <n-col :span="2"></n-col>
            <n-col :span="11">
              <h3>样例输出 #{{ index + 1 }}</h3>
              <n-input v-model:value="item.output" type="textarea" :rows="10" />
            </n-col>
          </n-row>
        </n-tab-pane>
      </n-tabs>
    </div>
    <div>
      <h2>提示/数据范围</h2>
      <MdEditor v-model:content="problem.hint" />
    </div>
    <div v-if="id">
      <h2>附件</h2>
      <n-upload
        :action="`/api/problem/${id}/file/`"
        :headers="{ Authorization: `Bearer ${getToken()}` }"
        :file-list="fileList"
        @update:file-list="fileList = $event"
        @finish="handleUploadFinish"
        show-download-button
        :on-remove="removeFile"
      >
        <n-button>上传附件</n-button>
      </n-upload>
    </div>
    <div v-else>
      <h2>附件</h2>
      <n-alert type="info">
        请先创建题目，然后在编辑时上传附件
      </n-alert>
    </div>
    <div>
      <h2>运行限制</h2>
      <n-row style="padding: 0 1px">
        <n-col :span="4">
          <h3>运行内存</h3>
          <n-input-number
            v-model:value="problem.memory_limit"
            button-placement="both"
            style="text-align: center"
            :min="1"
            :max="2048"
          >
            <template #suffix> MB </template>
          </n-input-number>
        </n-col>
        <n-col :span="1"></n-col>
        <n-col :span="4">
          <h3>运行时间</h3>
          <n-input-number
            v-model:value="problem.time_limit"
            button-placement="both"
            style="text-align: center"
            :step="500"
            :min="1"
            :max="10000"
          >
            <template #suffix> ms </template>
          </n-input-number>
        </n-col>
      </n-row>
    </div>
    <div>
      <h2>判题模式</h2>
      <n-select
        v-model:value="problem.judge_mode"
        :options="[{ label: 'ACM（标准输入输出）', value: 'acm' }, { label: 'LeetCode（函数模式）', value: 'leetcode' }]"
        placeholder="请选择判题模式"
      />
      <n-alert v-if="problem.judge_mode === 'leetcode'" type="info" style="margin-top: 12px">
        LeetCode 模式下，用户提交代码会自动插入“前置代码 + 用户代码 + 后置代码”再判题。
      </n-alert>
    </div>

    <div v-if="problem.judge_mode === 'leetcode'">
      <h2>LeetCode 模板配置</h2>
      <n-space style="margin-bottom: 12px">
        <n-button type="primary" secondary @click="applyLeetcodeTemplatePreset">
          一键填充默认模板
        </n-button>
        <n-button @click="problem.leetcode_templates = createDefaultLeetcodeTemplates()">
          清空模板
        </n-button>
      </n-space>
      <n-alert type="warning" style="margin-bottom: 12px">
        默认模板仅用于快速开始，请根据题目函数签名和输入输出规则修改。
      </n-alert>
      <n-tabs type="line" animated>
        <n-tab-pane name="tpl-c" tab="C" display-directive="show:lazy">
          <h3>前置代码（prepend）</h3>
          <n-input v-model:value="problem.leetcode_templates.c.prepend" type="textarea" :rows="8" />
          <h3 style="margin-top: 12px">后置代码（append）</h3>
          <n-input v-model:value="problem.leetcode_templates.c.append" type="textarea" :rows="8" />
          <h3 style="margin-top: 12px">编辑器默认代码（starter）</h3>
          <n-input v-model:value="problem.leetcode_templates.c.starter" type="textarea" :rows="6" />
        </n-tab-pane>
        <n-tab-pane name="tpl-cpp" tab="C++" display-directive="show:lazy">
          <h3>前置代码（prepend）</h3>
          <n-input v-model:value="problem.leetcode_templates.cpp.prepend" type="textarea" :rows="8" />
          <h3 style="margin-top: 12px">后置代码（append）</h3>
          <n-input v-model:value="problem.leetcode_templates.cpp.append" type="textarea" :rows="8" />
          <h3 style="margin-top: 12px">编辑器默认代码（starter）</h3>
          <n-input v-model:value="problem.leetcode_templates.cpp.starter" type="textarea" :rows="6" />
        </n-tab-pane>
        <n-tab-pane name="tpl-py" tab="Python3" display-directive="show:lazy">
          <h3>前置代码（prepend）</h3>
          <n-input v-model:value="problem.leetcode_templates.python3.prepend" type="textarea" :rows="8" />
          <h3 style="margin-top: 12px">后置代码（append）</h3>
          <n-input v-model:value="problem.leetcode_templates.python3.append" type="textarea" :rows="8" />
          <h3 style="margin-top: 12px">编辑器默认代码（starter）</h3>
          <n-input v-model:value="problem.leetcode_templates.python3.starter" type="textarea" :rows="6" />
        </n-tab-pane>
      </n-tabs>
    </div>

    <div>
      <h2>其它设置</h2>
      <n-row style="padding: 0 1px">
        <n-col :span="4">
          <h3>难度设置</h3>
          <n-select
            v-model:value="problem.difficulty"
            :options="difficultyOptions"
            placeholder="请选择难度"
          />
        </n-col>
        <n-col :span="1"></n-col>
        <n-col :span="4">
          <h3>是否隐藏</h3>
          <n-switch v-model:value="problem._is_hidden" />
        </n-col>
        <n-col :span="1"></n-col>
        <n-col :span="4">
          <h3>是否允许提交</h3>
          <n-switch v-model:value="problem._allow_submit" />
        </n-col>
        <n-col :span="1"></n-col>
        <n-col :span="4">
          <h3>是否隐藏提交</h3>
          <n-switch v-model:value="problem._hide_submissions" />
        </n-col>
        <n-col :span="1"></n-col>
        <n-col :span="4">
          <h3>是否隐藏讨论</h3>
          <n-switch v-model:value="problem._hide_discussions" />
        </n-col>
      </n-row>
    </div>
  </n-space>
  <n-divider />

  <n-space>
    <n-button
      type="primary"
      size="large"
      @click="submit"
      :loading="submiting"
      :disabled="submiting"
    >
      保存
    </n-button>
    <n-popconfirm @positive-click="deleteProblem" v-if="id">
      <template #trigger>
        <n-button type="error" size="large"> 删除 </n-button>
      </template>
      您确认要删除题目 {{ problem.title }} 吗？该操作不可撤销。
    </n-popconfirm>
  </n-space>

  <n-modal v-model:show="showImportModal" preset="dialog" title="从文本导入题目">
    <n-alert type="info" style="margin-bottom: 16px">
      支持洛谷格式的题目文本，会自动识别 ## 题目描述、## 输入格式、## 输出格式、## 样例输入、## 样例输出、## 说明/提示 等章节。
    </n-alert>
    <n-input
      v-model:value="importText"
      type="textarea"
      placeholder="请粘贴题目内容..."
      :rows="15"
    />
    <template #action>
      <n-button @click="showImportModal = false">取消</n-button>
      <n-button type="primary" @click="parseImportText">导入</n-button>
    </template>
  </n-modal>
</template>
