<script setup>
import { h, computed } from 'vue';
import router from '@/router';
import store from '@/store';
import { NButton, NTime, NPopover, NSpace } from 'naive-ui';
import { CheckCircleTwotone } from '@vicons/antd';
import { judgeStatus } from '@/plugins/consts';
import { RouterLink } from 'vue-router';

const props = defineProps({
  data: {
    type: Object,
    default: {},
  },
  loading: {
    type: Boolean,
    default: false,
  },
  isProblemSet: {
    type: Boolean,
    default: false,
  },
});

// 获取赛制类型
const getRuleType = () => {
  return props.data.rule_type || 'IOI';
};

// 动态生成列配置
const getColumns = () => {
  const ruleType = getRuleType();

  const rankColumn = {
    title: 'Rank',
    render(row, index) {
      return `# ${row.rank || index + 1}`;
    },
    width: 90,
  };

  const userColumn = {
    title: 'Team',
    render(row) {
      return h(
        RouterLink,
        { to: { name: 'user_detail', params: { id: row.id } } },
        {
          default: () =>
            h(
              NButton,
              {
                text: true,
                size: 'small',
              },
              { default: () => row.username }
            ),
        }
      );
    },
  };

  if (ruleType === 'ACM' && !props.isProblemSet && Array.isArray(props.data.problems)) {
    const problemColumns = props.data.problems.map(p => {
      return {
        title: () =>
          h(
            NPopover,
            { trigger: 'hover' },
            {
              trigger: () =>
                h(
                  'div',
                  {
                    style: 'cursor: help; width: 100%; text-align: center;',
                  },
                  p.label || p.title
                ),
              default: () => p.title,
            }
          ),
        key: `problem_${p.id}`,
        width: 90,
        align: 'center',
        titleAlign: 'center',
        render(row) {
          const ps = row.problem_statuses || {};
          const cell = ps[String(p.id)] || ps[p.id] || { status: 'unsubmitted', wrong_count: 0, time: null };
          const status = cell.status;
          const wrong = cell.wrong_count || 0;
          const time = cell.time;

          const frozen = Boolean(props.data.is_frozen && cell.frozen && status !== 'ac');

          let text = '';
          let bg = '#ffffff';
          let fg = '#999999';
          let tip = '';

          if (frozen) {
            bg = '#ffffcc';
            fg = '#8a6d3b';
            text = wrong > 0 ? `? (+${wrong})` : '?';
            tip = 'Status frozen. This team may have submissions after freeze time.';
          } else if (status === 'ac') {
            if (cell.first_blood) {
              bg = '#006600';
              fg = '#ffffff';
            } else {
              bg = '#ccffcc';
              fg = '#006600';
            }
            text = wrong > 0 ? `${time} (+${wrong})` : String(time);
            tip = cell.first_blood
              ? 'First Blood'
              : wrong > 0
                ? `Accepted at ${time} min after ${wrong} wrong submissions`
                : `Accepted at ${time} min`;
          } else if (status === 'not_ac') {
            bg = '#ffdddd';
            fg = '#990000';
            text = wrong > 0 ? `-${wrong}` : '';
            tip = wrong > 0 ? `${wrong} submissions, no accepted solution yet` : 'No accepted solution yet';
          } else {
            text = '';
            tip = 'Unsubmitted';
          }

          return h(
            NPopover,
            { trigger: 'hover' },
            {
              trigger: () =>
                h(
                  'div',
                  {
                    style: {
                      background: bg,
                      color: fg,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      textAlign: 'center',
                      padding: '0 8px',
                      borderRadius: '6px',
                      minHeight: '32px',
                      lineHeight: '1.1',
                      fontSize: '13px',
                      fontWeight: status === 'ac' || frozen ? 600 : 500,
                      whiteSpace: 'nowrap',
                      fontVariantNumeric: 'tabular-nums',
                      userSelect: 'none',
                    },
                  },
                  text
                ),
              default: () => tip,
            }
          );
        },
      };
    });

    return [
      rankColumn,
      userColumn,
      ...problemColumns,
      {
        title: 'Solved',
        width: 90,
        align: 'center',
        titleAlign: 'center',
        render(row) {
          return row.ac_count || 0;
        },
      },
      {
        title: 'Penalty',
        width: 100,
        align: 'center',
        titleAlign: 'center',
        render(row) {
          return row.penalty || 0;
        },
      },
    ];
  }

  const baseColumns = [
    rankColumn,
    userColumn,
    {
      title() {
        if (props.isProblemSet) return 'AC数量';
        if (ruleType === 'ACM') return 'AC数';
        return '总分';
      },
      render(row) {
        if (props.isProblemSet && row.ac_count !== undefined) {
          return `${row.ac_count} 题`;
        }
        if (ruleType === 'ACM') {
          return `${row.ac_count || 0} 题`;
        }
        return row.score;
      },
    },
  ];

  if (ruleType === 'ACM' && !props.isProblemSet) {
    baseColumns.push({
      title: '罚时',
      render(row) {
        return `${row.penalty || 0} 分钟`;
      },
    });
  }

  baseColumns.push({
    title: '提交过的题目',
    render(row) {
      return h(
        'div',
        { style: 'display: flex; flex-wrap: wrap; gap: 8px; max-width: 600px;' },
        (row.problems || []).map(item =>
          h(
            NPopover,
            {
              trigger: 'hover',
            },
            {
              trigger: () =>
                h(
                  RouterLink,
                  {
                    to: {
                      name: 'submission_detail',
                      params: { id: item.submission_id },
                    },
                  },
                  h(
                    NButton,
                    {
                      size: 'small',
                      color: judgeStatus.getColorClass(item.status),
                    },
                    { default: () => item.title }
                  )
                ),
              default: () => [
                `分数：${item.score}`,
                h('br'),
                `状态：${judgeStatus.getDisplay(item.status)}`,
                h('br'),
                '时间：',
                h(NTime, {
                  time: Number(new Date(item.time)),
                }),
              ],
            }
          )
        )
      );
    },
  });

  return baseColumns;
};

const columns = computed(() => getColumns());
</script>

<template>
  <n-spin :show="loading">
    <n-data-table :columns="columns" :data="data.users" :bordered="false" />
  </n-spin>
</template>

<style lang="scss" scoped>
:deep(a) {
  text-decoration: none;
}
</style>
