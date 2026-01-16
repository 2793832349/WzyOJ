<script setup>
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import Axios from '@/plugins/axios';
import router from '@/router';
import MdEditor from '@/components/MdEditor.vue';

const route = useRoute();
const message = useMessage();
const id = route.params.id;

const course = ref({
  title: '',
  description: '',
  is_hidden: false,
});

if (id) {
  Axios.get(`/course/course/${id}/`).then((res) => {
    course.value = {
      title: res.title,
      description: res.description,
      is_hidden: res.is_hidden,
    };
  });
}

const submitting = ref(false);
const submit = () => {
  if (!course.value.title) {
    message.warning('课程标题不能为空');
    return;
  }
  submitting.value = true;
  const req = id ? Axios.patch(`/course/course/${id}/`, course.value) : Axios.post('/course/course/', course.value);
  req
    .then((res) => {
      message.success('保存成功');
      const cid = id || res.id;
      router.push({ name: 'course_detail', params: { id: cid } });
    })
    .finally(() => {
      submitting.value = false;
    });
};

const deleteCourse = () => {
  Axios.delete(`/course/course/${id}/`).then(() => {
    message.success('删除成功');
    router.push({ name: 'course_list' });
  });
};
</script>

<template>
  <h1>
    <n-space style="align-items: center" size="large">
      {{ id ? '编辑' : '创建' }}课程 {{ id ? ` #${id}` : '' }}
      <n-button v-if="id" @click="router.push({ name: 'course_detail', params: { id } })" style="display: flex; align-items: center">
        返回
      </n-button>
    </n-space>
  </h1>

  <n-divider />

  <n-space vertical size="large">
    <div>
      <h2>课程名称</h2>
      <n-input v-model:value="course.title" placeholder="请输入课程名称" size="large" />
    </div>
    <div>
      <h2>课程描述</h2>
      <MdEditor v-model:content="course.description" />
    </div>
    <div>
      <h2>隐藏</h2>
      <n-switch v-model:value="course.is_hidden" />
    </div>
  </n-space>

  <n-divider />

  <n-space>
    <n-button type="primary" size="large" @click="submit" :loading="submitting" :disabled="submitting">
      保存
    </n-button>
    <n-popconfirm @positive-click="deleteCourse" v-if="id">
      <template #trigger>
        <n-button type="error" size="large">删除</n-button>
      </template>
      您确认要删除课程 {{ course.title }} 吗？该操作不可撤销。
    </n-popconfirm>
  </n-space>
</template>
