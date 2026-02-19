<script setup>
import { ref, onMounted } from 'vue';
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
  is_free: true,
});

const loadCourse = () => {
  if (id) {
    Axios.get(`/course/course/${id}/`).then((res) => {
      course.value = {
        title: res.title,
        description: res.description,
        is_hidden: res.is_hidden,
        is_free: res.is_free,
      };
      if (!res.is_free) {
        loadRedeemCodes();
      }
    });
  }
};

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

// 兑换码管理
const redeemCodes = ref([]);
const loadingCodes = ref(false);
const showCodeModal = ref(false);
const codeForm = ref({ count: 1, max_uses: 1, note: '' });
const generatingCodes = ref(false);
const generatedCodes = ref([]);

const loadRedeemCodes = async () => {
  if (!id) return;
  loadingCodes.value = true;
  try {
    const res = await Axios.get('/course/redeem-codes/', { params: { course_id: id } });
    redeemCodes.value = res.results || res;
  } catch (err) {
    console.error('Load redeem codes error:', err);
  } finally {
    loadingCodes.value = false;
  }
};

const openGenerateCodeModal = () => {
  codeForm.value = { count: 1, max_uses: 1, note: '' };
  generatedCodes.value = [];
  showCodeModal.value = true;
};

const generateCodes = async () => {
  generatingCodes.value = true;
  try {
    const res = await Axios.post('/course/redeem-codes/generate/', {
      course_id: id,
      count: codeForm.value.count,
      note: codeForm.value.note,
    });
    generatedCodes.value = res.codes;
    message.success(`成功生成 ${res.count} 个兑换码`);
    loadRedeemCodes();
  } catch (err) {
    message.error('生成兑换码失败');
  } finally {
    generatingCodes.value = false;
  }
};

const deleteRedeemCode = async (code) => {
  if (!confirm(`确定要删除兑换码 ${code.code} 吗？`)) return;
  try {
    await Axios.delete(`/course/redeem-codes/${code.id}/`);
    message.success('兑换码已删除');
    loadRedeemCodes();
  } catch (err) {
    message.error('删除失败');
  }
};

const copyCode = (code) => {
  navigator.clipboard.writeText(code);
  message.success('已复制到剪贴板');
};

onMounted(() => {
  loadCourse();
});
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
      <h2>状态设置</h2>
      <n-space>
        <n-switch v-model:value="course.is_hidden">
          <template #checked>隐藏</template>
          <template #unchecked>公开</template>
        </n-switch>
        <n-switch v-model:value="course.is_free" @update:value="(v) => { if (!v && id) loadRedeemCodes(); }">
          <template #checked>免费</template>
          <template #unchecked>付费</template>
        </n-switch>
      </n-space>
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

  <!-- 兑换码管理（仅编辑模式且为付费课程） -->
  <template v-if="id && !course.is_free">
    <n-divider />
    <n-card title="兑换码管理">
      <template #header-extra>
        <n-button type="primary" size="small" @click="openGenerateCodeModal">生成兑换码</n-button>
      </template>
      
      <n-spin :show="loadingCodes">
        <n-table v-if="redeemCodes.length > 0" :bordered="false" :single-line="false">
          <thead>
            <tr>
              <th>兑换码</th>
              <th>使用次数</th>
              <th>状态</th>
              <th>备注</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="code in redeemCodes" :key="code.id">
              <td>
                <n-space align="center">
                  <code>{{ code.code }}</code>
                  <n-button size="tiny" @click="copyCode(code.code)">复制</n-button>
                </n-space>
              </td>
              <td>{{ code.used_count }} / {{ code.max_uses }}</td>
              <td>
                <n-tag :type="code.is_valid ? 'success' : 'error'" size="small">
                  {{ code.is_valid ? '有效' : '已失效' }}
                </n-tag>
              </td>
              <td>{{ code.note || '-' }}</td>
              <td>{{ new Date(code.created_at).toLocaleString() }}</td>
              <td>
                <n-button size="tiny" type="error" @click="deleteRedeemCode(code)">删除</n-button>
              </td>
            </tr>
          </tbody>
        </n-table>
        <n-empty v-else description="暂无兑换码，点击上方按钮生成" />
      </n-spin>
    </n-card>
  </template>

  <!-- 生成兑换码弹窗 -->
  <n-modal v-model:show="showCodeModal" preset="dialog" title="生成兑换码">
    <n-form :model="codeForm" label-placement="left" label-width="100px">
      <n-form-item label="生成数量">
        <n-input-number v-model:value="codeForm.count" :min="1" :max="100" />
      </n-form-item>
      <n-form-item label="每码使用次数">
        <n-input-number v-model:value="codeForm.max_uses" :min="1" disabled />
        <span style="margin-left: 8px; color: #999">每个兑换码只能使用一次</span>
      </n-form-item>
      <n-form-item label="备注">
        <n-input v-model:value="codeForm.note" placeholder="可选，如：某某班级" />
      </n-form-item>
    </n-form>
    
    <!-- 生成结果 -->
    <div v-if="generatedCodes.length > 0" style="margin-top: 16px">
      <n-divider>生成的兑换码</n-divider>
      <n-space vertical>
        <n-space v-for="code in generatedCodes" :key="code.id" align="center">
          <code>{{ code.code }}</code>
          <n-button size="tiny" @click="copyCode(code.code)">复制</n-button>
        </n-space>
      </n-space>
    </div>
    
    <template #action>
      <n-button @click="showCodeModal = false">关闭</n-button>
      <n-button type="primary" :loading="generatingCodes" @click="generateCodes">生成</n-button>
    </template>
  </n-modal>
</template>
