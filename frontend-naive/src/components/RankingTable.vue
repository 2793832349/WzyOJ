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
  const baseColumns = [
    {
      title: '名次',
      render(row, index) {
        return `# ${index + 1}`;
      },
      width: 100,
    },
    {
      title: '用户',
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
    },
    {
      title() {
        const ruleType = getRuleType();
        if (props.isProblemSet) return 'AC数量';
        if (ruleType === 'ACM') return 'AC数';
        return '总分';
      },
      render(row) {
        const ruleType = getRuleType();
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

  // 只在 ACM 比赛模式（非题单）显示罚时列
  const ruleType = getRuleType();
  if (ruleType === 'ACM' && !props.isProblemSet) {
    baseColumns.push({
      title: '罚时',
      render(row) {
        return `${row.penalty || 0} 分钟`;
      },
    });
  }

  // 添加"提交过的题目"列
  baseColumns.push({
    title: '提交过的题目',
    render(row) {
      return h(
        'div',
        { style: 'display: flex; flex-wrap: wrap; gap: 8px; max-width: 600px;' },
        row.problems.map(item => 
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
