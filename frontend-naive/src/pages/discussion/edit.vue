<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useMessage } from 'naive-ui';
import Axios from '@/plugins/axios';
import router from '@/router';
import store from '@/store';
import MdEditor from '@/components/MdEditor.vue';
import Captcha from '../../components/captcha.vue';

const route = useRoute();
const message = useMessage();
const id = route.params.id;

const isEditMode = computed(() => !!id);

const canPublishDiscussion = computed(() => {
  const user = store.state.user || {};
  const perms = user.permissions || [];
  return Boolean(
    user.is_staff
    || user.is_superuser
    || perms.includes('problem')
    || perms.includes('class')
  );
});

const discussion = ref({
  related_content_type: 'none',
  related_content_id: null,
  title: '',
  content: '',
  captcha: '',
});
const captchaRef = ref(null);

if (!isEditMode.value) {
  if (route.query.related_problem__id) {
    discussion.value.related_content_type = 'problem';
    discussion.value.related_content_id = route.query.related_problem__id;
  } else if (route.query.related_contest__id) {
    discussion.value.related_content_type = 'contest';
    discussion.value.related_content_id = route.query.related_contest__id;
  }
}

const loadingDetail = ref(false);
const loadDiscussionForEdit = async () => {
  if (!isEditMode.value) return;
  loadingDetail.value = true;
  try {
    const res = await Axios.get(`/discussion/${id}/edit/`);
    discussion.value = {
      related_content_type: res.related_content_type ?? 'none',
      related_content_id: res.related_content_id ?? null,
      title: res.title ?? '',
      content: res.content ?? '',
      captcha: '',
    };
  } catch (err) {
    message.error(err?.data?.detail || err?.response?.data?.detail || '加载讨论失败');
  } finally {
    loadingDetail.value = false;
  }
};

onMounted(loadDiscussionForEdit);

const submiting = ref(false);
const submit = async () => {
  if (!canPublishDiscussion.value) {
    message.error('仅教师可发布讨论');
    return;
  }
  if (!discussion.value.title) {
    message.warning('讨论标题不能为空');
    return;
  }
  if (
    discussion.value.related_content_type !== 'none'
    && isNaN(parseInt(discussion.value.related_content_id))
  ) {
    message.warning('关联内容ID不能为空');
    return;
  }
  if (!(await captchaRef.value.checkCaptcha())) return;

  submiting.value = true;
  try {
    let res;
    if (isEditMode.value) {
      res = await Axios.post(`/discussion/${id}/edit/`, discussion.value);
      message.success('修改成功');
      router.push({ name: 'discussion_detail', params: { id: res.id || id } });
    } else {
      res = await Axios.post('/discussion/', discussion.value);
      message.success('创建成功');
      router.push({ name: 'discussion_detail', params: { id: res.id } });
    }
  } finally {
    submiting.value = false;
  }
};
</script>

<template>
  <h1>
    <n-space style="align-items: center" size="large">
      {{ isEditMode ? '编辑讨论' : '创建讨论' }}
    </n-space>
  </h1>

  <n-divider />

  <n-spin :show="loadingDetail">
    <n-space vertical size="large">
      <div>
        <h2>讨论标题</h2>
        <n-input
          v-model:value="discussion.title"
          placeholder="请输入标题"
          size="large"
        />
      </div>
      <div>
        <h2>关联内容</h2>
        <n-space vertical size="large">
          <n-radio-group
            v-model:value="discussion.related_content_type"
            name="radiogroup"
          >
            <n-space>
              <n-radio :value="'none'">无</n-radio>
              <n-radio :value="'problem'">题目</n-radio>
              <n-radio :value="'contest'">比赛（题单）</n-radio>
            </n-space>
          </n-radio-group>
          <n-input
            v-model:value="discussion.related_content_id"
            v-if="discussion.related_content_type !== 'none'"
            :placeholder="`请输入${
              discussion.related_content_type === 'problem'
                ? '问题'
                : '比赛（题单）'
            }ID`"
          />
        </n-space>
      </div>
      <div>
        <h2>讨论正文</h2>
        <MdEditor v-model:content="discussion.content" />
      </div>
    </n-space>
  </n-spin>

  <n-divider />

  <Captcha
    scene="discussion"
    v-model:captcha="discussion.captcha"
    ref="captchaRef"
  />

  <n-divider />

  <n-alert v-if="!canPublishDiscussion" type="warning" :show-icon="false" style="margin-bottom: 16px">
    仅教师可发布讨论
  </n-alert>

  <n-space>
    <n-button
      type="primary"
      size="large"
      @click="submit"
      :loading="submiting"
      :disabled="submiting || !canPublishDiscussion || loadingDetail"
    >
      保存
    </n-button>
  </n-space>
</template>
