<script setup>
import { computed, h } from 'vue';
import router from '@/router';
import store from '@/store';
import { NButton, NIcon, NProgress, NTag } from 'naive-ui';
import { CheckCircleTwotone } from '@vicons/antd';
import { difficulty, difficultyBadgeStyle } from '@/plugins/consts';
import { RouterLink } from 'vue-router';

const props = defineProps({
  data: {
    type: Array,
    default: [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  showSolved: {
    type: Boolean,
    default: true,
  },
  showSubmitStats: {
    type: Boolean,
    default: true,
  },
});

const passRate = row => {
  const accepted = Number(row.accepted_count || 0);
  const submissions = Number(row.submission_count || 0);
  if (!submissions) return 0;
  return Math.min(100, Math.round((accepted / submissions) * 100));
};

const solvedColumn = {
  title: '状态',
  width: 100,
  align: 'center',
  render(row) {
    if (!row.solved) {
      return h('span', { class: 'state-dot state-dot-muted' }, '待过');
    }
    return h(
      NButton,
      {
        text: true,
        size: 'small',
        class: 'state-btn state-btn-pass',
        onClick() {
          router.push({
            name: 'submission_index',
            query: { user__username: store.state.user.username },
          });
        },
      },
      {
        default: () => [
          h(NIcon, { size: 15, color: '#138a4f' }, { default: () => h(CheckCircleTwotone) }),
          h('span', { class: 'state-pass' }, '已过'),
        ],
      }
    );
  },
};

const baseColumns = [
  {
    title: 'ID',
    width: 120,
    render(row) {
      return h(
        RouterLink,
        { to: { name: 'problem_detail', params: { id: row.id } } },
        {
          default: () =>
            h(
              NButton,
              {
                text: true,
                size: 'small',
                class: 'id-btn',
              },
              {
                default: () => h('span', { class: 'id-text' }, `#${row.id}${row.is_hidden ? ' *' : ''}`),
              }
            ),
        }
      );
    },
  },
  {
    title: '标题',
    minWidth: 320,
    render(row) {
      return h(
        RouterLink,
        { to: { name: 'problem_detail', params: { id: row.id } }, class: 'title-link' },
        {
          default: () => [
            h('span', { class: 'title-main' }, row.title),
            row.is_hidden ? h(NTag, { size: 'tiny', type: 'warning', bordered: false }, { default: () => '隐藏' }) : null,
          ],
        }
      );
    },
  },
  {
    title: '难度',
    width: 130,
    render(row) {
      const diffValue = Number(row.difficulty ?? 0);
      const style = difficultyBadgeStyle[diffValue] || difficultyBadgeStyle[0];
      return h(
        RouterLink,
        { to: { name: 'problem_list', query: { difficulty: diffValue } } },
        {
          default: () =>
            h(
              NTag,
              {
                size: 'small',
                bordered: false,
                style,
                class: 'difficulty-badge',
              },
              { default: () => difficulty[diffValue] || difficulty[0] }
            ),
        }
      );
    },
  },
];

const submitStatsColumn = {
  title: '通过率 / 数据',
  minWidth: 220,
  render(row) {
    const accepted = Number(row.accepted_count || 0);
    const submissions = Number(row.submission_count || 0);
    const rate = passRate(row);

    return h('div', { class: 'stats-cell' }, [
      h('div', { class: 'stats-top' }, [
        h('strong', { class: 'stats-rate' }, `${rate}%`),
        h('span', { class: 'stats-count' }, `${accepted} / ${submissions}`),
      ]),
      h(NProgress, {
        percentage: rate,
        showIndicator: false,
        height: 7,
        color: rate >= 60 ? '#138a4f' : rate >= 30 ? '#f0a020' : '#d03050',
        railColor: '#e6edf7',
      }),
    ]);
  },
};

const columns = computed(() => {
  const cols = [];
  if (props.showSolved) cols.push(solvedColumn);
  cols.push(...baseColumns);
  if (props.showSubmitStats) cols.push(submitStatsColumn);
  return cols;
});

const rowClassName = row => {
  return row.solved ? 'problem-row-solved' : '';
};
</script>

<template>
  <n-spin :show="loading">
    <n-data-table
      :columns="columns"
      :data="data"
      :row-class-name="rowClassName"
      :bordered="false"
      :single-line="false"
      size="large"
    />
  </n-spin>
</template>

<style lang="scss" scoped>
:deep(a) {
  text-decoration: none;
}

:deep(.n-data-table-th) {
  font-size: 13px;
  letter-spacing: 0.01em;
}

:deep(.n-data-table-td) {
  padding-top: 15px;
  padding-bottom: 15px;
}

:deep(.n-data-table-tr:nth-child(2n + 1):not(.problem-row-solved) .n-data-table-td) {
  background: rgba(246, 250, 255, 0.65);
}

:deep(.id-text) {
  display: inline-flex;
  align-items: center;
  height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid #c7d9f2;
  background: linear-gradient(180deg, #f7fbff 0%, #ecf4ff 100%);
  font-family: 'SourceCodePro', monospace;
  font-size: 13px;
  color: #2a4d77;
  font-weight: 600;
}

:deep(.title-link) {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

:deep(.title-main) {
  color: #11263f;
  font-weight: 700;
  font-size: 15px;
}

:deep(.difficulty-badge) {
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

:deep(.difficulty-badge:hover) {
  transform: translateY(-1px);
}

:deep(.state-dot) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 52px;
  height: 26px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

:deep(.state-dot-muted) {
  color: #7f8fa7;
  background: linear-gradient(180deg, #eef3f9 0%, #e7edf6 100%);
  border: 1px solid #dbe5f2;
}

:deep(.state-btn) {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

:deep(.state-btn-pass) {
  padding: 3px 8px;
  border-radius: 999px;
  background: rgba(19, 138, 79, 0.1);
  border: 1px solid rgba(19, 138, 79, 0.22);
}

:deep(.state-pass) {
  color: #138a4f;
  font-size: 12px;
  font-weight: 700;
}

:deep(.stats-cell) {
  min-width: 160px;
}

:deep(.stats-top) {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 8px;
}

:deep(.stats-rate) {
  font-size: 18px;
  color: #15365f;
}

:deep(.stats-count) {
  font-size: 12px;
  color: #5e7693;
}

:deep(.problem-row-solved .n-data-table-td) {
  background: rgba(22, 163, 74, 0.08) !important;
}
</style>
