<script setup>
import { ref } from 'vue';
import Axios from '@/plugins/axios';
import { useMessage } from 'naive-ui';

const fileInput = ref(null);
const uploading = ref(false);
const results = ref([]);
const message = useMessage();

const handleUpload = async () => {
  if (!fileInput.value.files.length) {
    message.warning('请选择压缩包文件');
    return;
  }
  const formData = new FormData();
  formData.append('file', fileInput.value.files[0]);
  uploading.value = true;
  try {
    const res = await Axios.post('/problem/import-hoj-zip/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    results.value = res.results || [];
    message.success('导入完成');
  } catch (e) {
    message.error('导入失败');
  } finally {
    uploading.value = false;
  }
};
</script>

<template>
  <n-card title="批量导入 HOJ 题库压缩包" style="margin-bottom: 24px">
    <n-space vertical>
      <input ref="fileInput" type="file" accept=".zip" />
      <n-button :loading="uploading" type="primary" @click="handleUpload">上传并导入</n-button>
      <div v-if="results.length">
        <h4>导入结果：</h4>
        <ul>
          <li v-for="r in results" :key="r.problem_id || r.root || r.zip">
            <span v-if="r.ok">✔ 题目ID: {{ r.problem_id }} 导入成功</span>
            <span v-else style="color: red">✘ {{ r.error }}</span>
          </li>
        </ul>
      </div>
    </n-space>
  </n-card>
</template>
