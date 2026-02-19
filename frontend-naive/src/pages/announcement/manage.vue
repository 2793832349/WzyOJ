<script setup>
import { computed, h, ref } from 'vue';
import { useRouter } from 'vue-router';
import Axios from '@/plugins/axios';
import { NButton, NSpace, NTag } from 'naive-ui';
import { AddOutline } from '@vicons/ionicons5';

const router = useRouter();
const message = useMessage();

const loading = ref(false);
const saving = ref(false);
const showEditor = ref(false);
const data = ref([]);
const editingId = ref(null);

const pagination = ref({
  page: 1,
  pageSize: 10,
  count: 0,
});

const form = ref({
  title: '',
  content: '',
  is_published: true,
  is_pinned: false,
  order: 0,
  start_time_value: null,
  end_time_value: null,
});

const modalTitle = computed(() => (editingId.value ? '编辑公告' : '新增公告'));

const toTimestamp = value => {
  if (!value) return null;
  const ts = Date.parse(value);
  return Number.isNaN(ts) ? null : ts;
};

const toISOString = ts => {
  if (!ts) return null;
  return new Date(ts).toISOString();
};

const resetForm = () => {
  editingId.value = null;
  form.value = {
    title: '',
    content: '',
    is_published: true,
    is_pinned: false,
    order: 0,
    start_time_value: null,
    end_time_value: null,
  };
};

const fillForm = row => {
  editingId.value = row.id;
  form.value = {
    title: row.title || '',
    content: row.content || '',
    is_published: !!row.is_published,
    is_pinned: !!row.is_pinned,
    order: row.order || 0,
    start_time_value: toTimestamp(row.start_time),
    end_time_value: toTimestamp(row.end_time),
  };
};

const getRows = res => {
  if (Array.isArray(res)) {
    pagination.value.count = res.length;
    return res;
  }
  pagination.value.count = res.count || 0;
  return res.results || [];
};

const loadData = () => {
  loading.value = true;
  Axios.get('/announcement/', {
    params: {
      limit: pagination.value.pageSize,
      offset: (pagination.value.page - 1) * pagination.value.pageSize,
    },
  })
    .then(res => {
      data.value = getRows(res);
    })
    .finally(() => {
      loading.value = false;
    });
};

const openCreate = () => {
  resetForm();
  showEditor.value = true;
};

const openEdit = row => {
  fillForm(row);
  showEditor.value = true;
};

const removeItem = row => {
  window.$dialog.warning({
    title: '删除公告',
    content: `确认删除「${row.title}」吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: () => {
      Axios.delete(`/announcement/${row.id}/`).then(() => {
        message.success('删除成功');
        loadData();
      });
    },
  });
};

const save = () => {
  if (!form.value.title.trim()) {
    message.warning('请填写公告标题');
    return;
  }
  if (!form.value.content.trim()) {
    message.warning('请填写公告内容');
    return;
  }

  const payload = {
    title: form.value.title,
    content: form.value.content,
    is_published: form.value.is_published,
    is_pinned: form.value.is_pinned,
    order: Number(form.value.order || 0),
    start_time: toISOString(form.value.start_time_value),
    end_time: toISOString(form.value.end_time_value),
  };

  if (payload.start_time && payload.end_time && payload.start_time > payload.end_time) {
    message.warning('开始时间不能晚于结束时间');
    return;
  }

  saving.value = true;
  const req = editingId.value
    ? Axios.patch(`/announcement/${editingId.value}/`, payload)
    : Axios.post('/announcement/', payload);

  req
    .then(() => {
      message.success(editingId.value ? '更新成功' : '创建成功');
      showEditor.value = false;
      loadData();
    })
    .finally(() => {
      saving.value = false;
    });
};

const formatTime = value => {
  if (!value) return '-';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '-';
  return date.toLocaleString('zh-CN', { hour12: false });
};

const columns = [
  {
    title: 'ID',
    key: 'id',
    width: 80,
  },
  {
    title: '标题',
    key: 'title',
    minWidth: 260,
  },
  {
    title: '状态',
    key: 'is_published',
    width: 110,
    render(row) {
      return h(
        NTag,
        { type: row.is_published ? 'success' : 'default', bordered: false },
        { default: () => (row.is_published ? '已发布' : '草稿') }
      );
    },
  },
  {
    title: '置顶',
    key: 'is_pinned',
    width: 90,
    render(row) {
      return row.is_pinned
        ? h(NTag, { type: 'warning', bordered: false }, { default: () => '置顶' })
        : '-';
    },
  },
  {
    title: '生效时间',
    key: 'active_range',
    minWidth: 260,
    render(row) {
      const start = formatTime(row.start_time);
      const end = formatTime(row.end_time);
      if (start === '-' && end === '-') return '-';
      return `${start} ~ ${end}`;
    },
  },
  {
    title: '排序',
    key: 'order',
    width: 90,
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    render(row) {
      return h(
        NSpace,
        { size: 8 },
        {
          default: () => [
            h(
              NButton,
              { size: 'small', onClick: () => openEdit(row) },
              { default: () => '编辑' }
            ),
            h(
              NButton,
              { size: 'small', type: 'error', onClick: () => removeItem(row) },
              { default: () => '删除' }
            ),
          ],
        }
      );
    },
  },
];

loadData();
</script>

<template>
  <n-layout class="announcement-manage-page">
    <section class="hero">
      <div>
        <p class="kicker">首页运营</p>
        <h1>公告管理</h1>
        <p class="subtitle">在首页展示通知，支持定时生效与置顶</p>
      </div>
      <n-space>
        <n-button @click="router.push({ name: 'home' })">返回首页</n-button>
        <n-button type="primary" @click="openCreate">
          <template #icon>
            <n-icon :component="AddOutline" />
          </template>
          新增公告
        </n-button>
      </n-space>
    </section>

    <section class="table-card">
      <n-data-table
        :columns="columns"
        :data="data"
        :loading="loading"
        :single-line="false"
      />
    </section>

    <div class="pager-wrap">
      <n-pagination
        v-model:page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :item-count="pagination.count"
        show-size-picker
        :page-sizes="[10, 20, 50]"
        @update:page="loadData"
        @update:page-size="
          pageSize => {
            pagination.pageSize = pageSize;
            pagination.page = 1;
            loadData();
          }
        "
      />
    </div>

    <n-modal v-model:show="showEditor" preset="card" :title="modalTitle" class="edit-modal">
      <n-form label-placement="left" label-width="88">
        <n-form-item label="标题" required>
          <n-input v-model:value="form.title" placeholder="请输入公告标题" maxlength="120" show-count />
        </n-form-item>

        <n-form-item label="内容" required>
          <n-input
            v-model:value="form.content"
            type="textarea"
            placeholder="请输入公告内容"
            :rows="8"
          />
        </n-form-item>

        <n-grid :cols="2" :x-gap="12">
          <n-form-item-gi label="置顶">
            <n-switch v-model:value="form.is_pinned" />
          </n-form-item-gi>
          <n-form-item-gi label="发布">
            <n-switch v-model:value="form.is_published" />
          </n-form-item-gi>
        </n-grid>

        <n-form-item label="排序">
          <n-input-number v-model:value="form.order" style="width: 100%" />
        </n-form-item>

        <n-form-item label="开始时间">
          <n-date-picker
            v-model:value="form.start_time_value"
            type="datetime"
            clearable
            style="width: 100%"
            placeholder="不填表示立即生效"
          />
        </n-form-item>

        <n-form-item label="结束时间">
          <n-date-picker
            v-model:value="form.end_time_value"
            type="datetime"
            clearable
            style="width: 100%"
            placeholder="不填表示长期有效"
          />
        </n-form-item>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showEditor = false">取消</n-button>
          <n-button type="primary" :loading="saving" @click="save">保存</n-button>
        </n-space>
      </template>
    </n-modal>
  </n-layout>
</template>

<style lang="scss" scoped>
.announcement-manage-page {
  padding: 8px 6px 16px;
  --line-color: #dbe5f3;
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 22px 24px;
  border-radius: 18px;
  background: linear-gradient(132deg, #0b4d6e 0%, #1d6e99 45%, #58a8c2 100%);
  color: #fff;
  margin-bottom: 16px;
}

.kicker {
  margin: 0;
  font-size: 13px;
  letter-spacing: 0.08em;
  opacity: 0.88;
}

.hero h1 {
  margin: 6px 0 2px;
  font-size: 34px;
  line-height: 1.1;
}

.subtitle {
  margin: 0;
  font-size: 14px;
  opacity: 0.94;
}

.table-card {
  border: 1px solid var(--line-color);
  border-radius: 14px;
  background: #fff;
  padding: 6px;
}

.pager-wrap {
  margin-top: 22px;
  display: flex;
  justify-content: center;
}

.edit-modal {
  width: min(760px, 92vw);
}

@media (max-width: 900px) {
  .hero {
    flex-direction: column;
    align-items: stretch;
    padding: 18px;
  }
}
</style>
