�7<script setup>
import { ref } from 'vue';
import Axios from '@/plugins/axios';
import { difficultyOptions } from '@/plugins/consts';
import MdEditor from '@/components/MdEditor.vue';
import router from '@/router';
import { useRoute } from 'vue-router';

const route = useRoute(),
  message = useMessage();
const id = route.params.id;

const problem = ref({
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
});
const fileList = ref([]);

if (id) {
  Axios.get(`/problem/${id}/`).then(res => {
    res.tags = res.tags.map(tag => tag.id);
    problem.value = res;
    fileList.value = res.files.map(file => ({
      name: file,
      status: 'finished',
    }));
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
  let req;
  if (id) req = Axios.put(`/problem/${id}/`, { ...problem.value, files });
  else req = Axios.post('/problem/', { ...problem.value, files });
  req
    .then(res => {
      if (!id) router.push({ name: 'problem_detail', params: { id: res.id } });
      else message.success('修改成功');
    })
    .finally(() => {
      submiting.value = false;
    });
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
</script>

<template>
  <n-space vertical size="large">
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
      <h2>数据范围</h2>
      <MdEditor v-model:content="problem.hint" />
    </div>
    <!-- 附件功能已隐藏 -->
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
</template>
� *cascade08�� *cascade08�� *cascade08��*cascade08��*cascade08�� *cascade08��*cascade08�� *cascade08��*cascade08�� *cascade08��*cascade08�� *cascade08�� *cascade08��*cascade08�� *cascade08�� *cascade08�� *cascade08��*cascade08�� *cascade08�� *cascade08���� *cascade08�� *cascade08��*cascade08�� *cascade08��# *cascade08�#�$*cascade08�$�$ *cascade08�$�$*cascade08�$�$ *cascade08�$�$*cascade08�$�$ *cascade08�$�$*cascade08�$�$ *cascade08�$�$ *cascade08�$�7 *cascade08"(205b1bab434999c48e066e66385ba65f03f104f42=file:///root/frontend-naive/src/pages/problem/edit/detail.vue:file:///root/frontend-naive