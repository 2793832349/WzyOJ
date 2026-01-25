<script setup>
import { h, computed, ref, watch, onUnmounted } from 'vue';
import config from '../config';
import { formatTime, formatSize } from '@/plugins/utils';
import { judgeStatus, noTime, noMemory } from '@/plugins/consts';
import { NButton, NTime, useMessage } from 'naive-ui';
import { RouterLink } from 'vue-router';
import store from '@/store';
import Axios from '@/plugins/axios';

const props = defineProps({
  data: {
    type: Array,
    default: [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['refresh']);
const message = useMessage();

const rejudgingIds = ref(new Set());
let pollingInterval = null;

const stopPolling = () => {
  if (pollingInterval) {
    clearInterval(pollingInterval);
    pollingInterval = null;
  }
};

const startPolling = () => {
  if (pollingInterval) return;
  pollingInterval = setInterval(() => {
    emit('refresh', true);
  }, 2000);
};

// Watch for data updates to check status of rejudging items
watch(
  () => props.data,
  newData => {
    if (rejudgingIds.value.size === 0) return;

    const idsToRemove = [];
    for (const id of rejudgingIds.value) {
      const submission = newData.find(s => s.id === id);
      // If submission is gone or status is no longer pending/judging, stop tracking
      if (
        !submission ||
        (submission.status !== judgeStatus.PENDING &&
          submission.status !== judgeStatus.JUDGING)
      ) {
        idsToRemove.push(id);
      }
    }

    idsToRemove.forEach(id => rejudgingIds.value.delete(id));

    if (rejudgingIds.value.size === 0) {
      stopPolling();
    }
  },
  { deep: true }
);

// Safety timeout cleanup
const cleanup = () => {
  stopPolling();
  rejudgingIds.value.clear();
};

onUnmounted(cleanup);

const rejudge = id => {
  Axios.post(`/submission/${id}/rejudge/`).then(() => {
    message.success('已开始重新评测');
    rejudgingIds.value.add(id);
    startPolling();
    emit('refresh');
    
    // Safety timeout: stop tracking this ID after 2 minutes
    setTimeout(() => {
      if (rejudgingIds.value.has(id)) {
        rejudgingIds.value.delete(id);
        if (rejudgingIds.value.size === 0) stopPolling();
      }
    }, 120000);
  });
};

const columns = computed(() => {
  const cols = [
    {
      title: 'ID',
      render(row) {
        return h(
          RouterLink,
          { to: { name: 'submission_detail', params: { id: row.id } } },
          {
            default: () =>
              h(
                NButton,
                {
                  text: true,
                  size: 'small',
                },
                { default: () => String(row.id) + (row.is_hidden ? '*' : '') }
              ),
          }
        );
      },
    },
    {
      title: '分数',
      render(row) {
        return h(
          RouterLink,
          { to: { name: 'submission_detail', params: { id: row.id } } },
          {
            default: () =>
              h(
                NButton,
                {
                  text: true,
                  size: 'small',
                  color: judgeStatus.getColorClass(row.status),
                },
                { default: () => row.score }
              ),
          }
        );
      },
    },
    {
      title: '状态',
      render(row) {
        return h(
          RouterLink,
          { to: { name: 'submission_detail', params: { id: row.id } } },
          {
            default: () =>
              h(
                NButton,
                {
                  size: 'small',
                  color: judgeStatus.getColorClass(row.status),
                },
                { default: () => judgeStatus.getDisplay(row.status) }
              ),
          }
        );
      },
    },
    {
      title: '题目',
      render(row) {
        return h(
          RouterLink,
          { to: { name: 'problem_detail', params: { id: row.problem.id } } },
          {
            default: () =>
              h(
                NButton,
                {
                  text: true,
                  size: 'small',
                },
                { default: () => row.problem.title }
              ),
          }
        );
      },
    },
    {
      title: '用户',
      render(row) {
        return h(
          RouterLink,
          { to: { name: 'user_detail', params: { id: row.user.id } } },
          {
            default: () =>
              h(
                NButton,
                {
                  text: true,
                  size: 'small',
                },
                { default: () => row.user.username }
              ),
          }
        );
      },
    },
    {
      title: '用时',
      render(row) {
        return noTime.includes(row.status) ? '-' : formatTime(row.execute_time);
      },
    },
    {
      title: '内存',
      render(row) {
        return noMemory.includes(row.status)
          ? '-'
          : formatSize(row.execute_memory);
      },
    },
    {
      title: '语言',
      render(row) {
        return config.languages[row.language];
      },
    },
    {
      title: '提交时间',
      render(row) {
        return h(NTime, {
          time: new Date(row.create_time),
        });
      },
    },
  ];

  if (
    store.state.user.permissions &&
    store.state.user.permissions.includes('submission')
  ) {
    cols.push({
      title: '操作',
      render(row) {
        return h(
          NButton,
          {
            size: 'small',
            type: 'warning',
            onClick: () => rejudge(row.id),
          },
          { default: () => '重新评测' }
        );
      },
    });
  }

  return cols;
});
</script>

<template>
  <n-spin :show="loading">
    <n-data-table :columns="columns" :data="data" :bordered="false" />
  </n-spin>
</template>

<style lang="scss" scoped>
:deep(a) {
  text-decoration: none;
}
</style>
