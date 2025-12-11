ü<script setup>
import { h } from 'vue';
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

const columns = [
  {
    title: 'åæ¬¡',
    render(row, index) {
      return `# ${index + 1}`;
    },
    width: 100,
  },
  {
    title: 'ç”¨æˆ·',
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
    title: props.isProblemSet ? 'ACæ•°é‡' : 'æ€»åˆ†',
    render(row) {
      if (props.isProblemSet && row.ac_count !== undefined) {
        return `${row.ac_count} é¢˜`;
      }
      return row.score;
    },
  },
  {
    title: 'æäº¤è¿‡çš„é¢˜ç›®',
    render(row) {
      return h(
        NSpace,
        {},
        {
          default: () => {
            const res = [];
            for (const item of row.problems) {
              res.push(
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
                      `åˆ†æ•°ï¼š${item.score}`,
                      h('br'),
                      `çŠ¶æ€ï¼š${judgeStatus.getDisplay(item.status)}`,
                      h('br'),
                      'æ—¶é—´ï¼š',
                      h(NTime, {
                        time: Number(new Date(item.time)),
                      }),
                    ],
                  }
                )
              );
            }
            return res;
          },
        }
      );
    },
  },
];
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
— *cascade08—¹*cascade08¹Ç *cascade08Ç‰	*cascade08‰	Š	 *cascade08Š		*cascade08	‘	 *cascade08‘	Ò	*cascade08Ò	×	 *cascade08×	Ş	*cascade08Ş	ü *cascade08"(205b1bab434999c48e066e66385ba65f03f104f42;file:///root/frontend-naive/src/components/RankingTable.vue:file:///root/frontend-naive