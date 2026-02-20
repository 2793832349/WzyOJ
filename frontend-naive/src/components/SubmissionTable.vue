<script setup>
import { h, computed, ref, watch, onMounted, onUnmounted } from 'vue';
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

const MOBILE_BREAKPOINT = 900;
const isMobile = ref(false);

const rejudgingIds = ref(new Set());
let pollingInterval = null;

const canRejudge = computed(() => {
  return (
    store.state.user.permissions &&
    store.state.user.permissions.includes('submission')
  );
});

const statusTagStyle = status => ({
  backgroundColor: judgeStatus.getColorClass(status) || '#64748b',
  color: '#ffffff',
  borderColor: 'transparent',
});

const formatCreateTime = val => {
  const date = new Date(val);
  if (Number.isNaN(date.getTime())) return '-';
  return date.toLocaleString('zh-CN', { hour12: false });
};

const updateViewport = () => {
  if (typeof window === 'undefined') return;
  isMobile.value = window.innerWidth <= MOBILE_BREAKPOINT;
};

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

watch(
  () => props.data,
  newData => {
    if (rejudgingIds.value.size === 0) return;

    const idsToRemove = [];
    for (const id of rejudgingIds.value) {
      const submission = newData.find(s => s.id === id);
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

const cleanup = () => {
  stopPolling();
  rejudgingIds.value.clear();
};

onMounted(() => {
  updateViewport();
  window.addEventListener('resize', updateViewport, { passive: true });
});

onUnmounted(() => {
  cleanup();
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', updateViewport);
  }
});

const rejudge = id => {
  Axios.post(`/submission/${id}/rejudge/`).then(() => {
    message.success('已开始重新评测');
    rejudgingIds.value.add(id);
    startPolling();
    emit('refresh');

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
        return config.languages[row.language] || row.language;
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

  if (canRejudge.value) {
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
    <div class="submission-table-wrap">
      <template v-if="isMobile">
        <n-empty v-if="!data.length" description="暂无提交记录" class="mobile-empty" />

        <div v-else class="mobile-list">
          <n-card
            v-for="row in data"
            :key="row.id"
            size="small"
            class="mobile-item"
            :bordered="false"
          >
            <div class="mobile-item-head">
              <router-link
                :to="{ name: 'submission_detail', params: { id: row.id } }"
                class="mobile-id"
              >
                #{{ row.id }}{{ row.is_hidden ? '*' : '' }}
              </router-link>
              <n-tag size="small" :bordered="false" :style="statusTagStyle(row.status)">
                {{ judgeStatus.getDisplay(row.status) }}
              </n-tag>
            </div>

            <router-link
              :to="{ name: 'problem_detail', params: { id: row.problem.id } }"
              class="mobile-problem"
            >
              {{ row.problem.title }}
            </router-link>

            <div class="mobile-meta-grid">
              <div class="meta-block">
                <span>分数</span>
                <strong :style="{ color: judgeStatus.getColorClass(row.status) || '#1f2937' }">
                  {{ row.score }}
                </strong>
              </div>
              <div class="meta-block">
                <span>用时</span>
                <strong>{{ noTime.includes(row.status) ? '-' : formatTime(row.execute_time) }}</strong>
              </div>
              <div class="meta-block">
                <span>内存</span>
                <strong>{{ noMemory.includes(row.status) ? '-' : formatSize(row.execute_memory) }}</strong>
              </div>
              <div class="meta-block">
                <span>语言</span>
                <strong>{{ config.languages[row.language] || row.language }}</strong>
              </div>
            </div>

            <div class="mobile-item-footer">
              <router-link
                :to="{ name: 'user_detail', params: { id: row.user.id } }"
                class="mobile-user"
              >
                @{{ row.user.username }}
              </router-link>
              <span class="mobile-time">{{ formatCreateTime(row.create_time) }}</span>
            </div>

            <div v-if="canRejudge" class="mobile-item-actions">
              <n-button size="small" type="warning" @click="rejudge(row.id)">重新评测</n-button>
            </div>
          </n-card>
        </div>
      </template>

      <template v-else>
        <n-data-table
          :columns="columns"
          :data="data"
          :bordered="false"
          :single-line="false"
          :scroll-x="1180"
        />
      </template>
    </div>
  </n-spin>
</template>

<style lang="scss" scoped>
.submission-table-wrap {
  width: 100%;
}

.mobile-empty {
  padding: 28px 0;
}

.mobile-list {
  display: grid;
  gap: 10px;
}

.mobile-item {
  border-radius: 14px;
  border: 1px solid #dbe7f6;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  box-shadow: 0 10px 22px -20px rgba(25, 61, 112, 0.45);
}

.mobile-item-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.mobile-id {
  font-size: 15px;
  font-weight: 800;
  color: #16355f;
  text-decoration: none;
}

.mobile-problem {
  display: block;
  margin-top: 6px;
  font-size: 15px;
  font-weight: 700;
  color: #0f2d52;
  text-decoration: none;
}

.mobile-meta-grid {
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.meta-block {
  padding: 8px 10px;
  border-radius: 10px;
  background: #f3f8ff;
  border: 1px solid #e2ecfb;
}

.meta-block span {
  display: block;
  font-size: 12px;
  color: #6881a3;
}

.meta-block strong {
  display: block;
  margin-top: 2px;
  font-size: 14px;
  color: #102138;
}

.mobile-item-footer {
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.mobile-user {
  font-size: 13px;
  color: #1d4f92;
  text-decoration: none;
  font-weight: 600;
}

.mobile-time {
  font-size: 12px;
  color: #6d8099;
}

.mobile-item-actions {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}

:deep(a) {
  text-decoration: none;
}

:deep(.n-data-table) {
  border-radius: 14px;
  overflow: hidden;
}

:deep(.n-data-table-th) {
  background: linear-gradient(180deg, #ecf4ff 0%, #e5f0ff 100%);
  color: #16335b;
  font-weight: 700;
}

:deep(.n-data-table-td) {
  border-bottom-color: #e8eef7;
}

:deep(.n-data-table-tr:hover .n-data-table-td) {
  background: #eef6ff;
}

@media (max-width: 560px) {
  .mobile-meta-grid {
    grid-template-columns: 1fr;
  }

  .mobile-item-footer {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
