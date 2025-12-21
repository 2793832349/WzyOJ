<template>
  <div v-if="problem">
    <h1>#{{ problem.id }} {{ problem.display_title }}</h1>
    
    <n-space style="margin-bottom: 20px">
      <n-button
        size="small"
        :color="difficultyColor[problem.difficulty || 0]"
        style="cursor: default"
      >
        {{ difficultyMap[problem.difficulty || 0] }}
      </n-button>
      <n-tag type="info">时间限制: {{ problem.time_limit }}ms</n-tag>
      <n-tag type="info">内存限制: {{ problem.memory_limit }}MB</n-tag>
      <n-tag type="success">班级专属题目</n-tag>
    </n-space>

    <n-card title="题目描述" v-if="problem.description">
      <div style="white-space: pre-wrap">{{ problem.description }}</div>
    </n-card>

    <n-card title="输入格式" v-if="problem.input_format" style="margin-top: 16px">
      <div style="white-space: pre-wrap">{{ problem.input_format }}</div>
    </n-card>

    <n-card title="输出格式" v-if="problem.output_format" style="margin-top: 16px">
      <div style="white-space: pre-wrap">{{ problem.output_format }}</div>
    </n-card>

    <n-card title="样例" v-if="problem.samples && problem.samples.length > 0" style="margin-top: 16px">
      <n-tabs type="line" animated>
        <n-tab-pane
          v-for="(sample, index) in problem.samples"
          :key="index"
          :name="'sample_' + index"
          :tab="'样例 #' + (index + 1)"
        >
          <n-grid :cols="2" :x-gap="12">
            <n-gi>
              <h4>输入</h4>
              <n-input
                :value="sample.input"
                type="textarea"
                :rows="10"
                readonly
                style="font-family: monospace"
              />
            </n-gi>
            <n-gi>
              <h4>输出</h4>
              <n-input
                :value="sample.output"
                type="textarea"
                :rows="10"
                readonly
                style="font-family: monospace"
              />
            </n-gi>
          </n-grid>
        </n-tab-pane>
      </n-tabs>
    </n-card>

    <n-card title="数据范围" v-if="problem.hint" style="margin-top: 16px">
      <div style="white-space: pre-wrap">{{ problem.hint }}</div>
    </n-card>

    <n-card title="提交代码" style="margin-top: 16px">
      <n-alert type="info" style="margin-bottom: 16px">
        提示：班级专属题目的提交功能正在开发中，请稍后再试。
      </n-alert>
      
      <n-form label-placement="top">
        <n-form-item label="选择语言">
          <n-select
            v-model:value="submission.language"
            :options="languageOptions"
            placeholder="请选择编程语言"
          />
        </n-form-item>
        <n-form-item label="代码">
          <n-input
            v-model:value="submission.code"
            type="textarea"
            placeholder="请输入代码..."
            :rows="15"
            :disabled="true"
          />
        </n-form-item>
      </n-form>
      
      <n-space>
        <n-button type="primary" disabled>
          提交（开发中）
        </n-button>
        <n-button @click="$router.push({ name: 'class_detail', params: { id: classId } })">
          返回班级
        </n-button>
      </n-space>
    </n-card>
  </div>
  <div v-else>
    <n-spin size="large" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useMessage } from 'naive-ui';
import Axios from '@/plugins/axios';
import { difficulty as difficultyMap, difficultyColor } from '@/plugins/consts';

const route = useRoute();
const message = useMessage();

const classId = route.params.id;
const problemId = route.params.problemId;
const problem = ref(null);

const submission = ref({
  language: 'cpp',
  code: '',
});

const languageOptions = [
  { label: 'C++', value: 'cpp' },
  { label: 'C', value: 'c' },
  { label: 'Python', value: 'python' },
  { label: 'Java', value: 'java' },
];

// 获取题目详情
const fetchProblem = () => {
  Axios.get(`class/class-problem/${problemId}/`)
    .then(res => {
      problem.value = res;
    })
    .catch(() => {
      message.error('获取题目详情失败');
    });
};

onMounted(() => {
  fetchProblem();
});
</script>
