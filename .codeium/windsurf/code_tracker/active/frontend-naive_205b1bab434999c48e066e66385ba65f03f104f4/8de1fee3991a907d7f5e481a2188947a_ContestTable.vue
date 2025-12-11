©<script setup>
import { h } from 'vue';
import router from '@/router';
import store from '@/store';
import { NButton, NIcon, NTag, NTime } from 'naive-ui';
import { CheckCircleTwotone } from '@vicons/antd';
import { difficulty, difficultyColor } from '@/plugins/consts';
import { RouterLink } from 'vue-router';

defineProps({
  data: {
    type: Array,
    default: [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

const columns = [
  {
    title: 'Â∑≤Âä†ÂÖ•',
    render(row) {
      return h(
        NIcon,
        {
          style: 'margin-top: 5px; margin-left: 5px',
          size: '20',
          color: '#27AE60',
        },
        { default: () => (row.joined ? h(CheckCircleTwotone) : '') }
      );
    },
    width: 100,
  },
  {
    title: 'ID',
    render(row) {
      const routeName = row.problem_list_mode ? 'problemset_detail' : 'contest_detail';
      return h(
        RouterLink,
        { to: { name: routeName, params: { id: row.id } } },
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
    title: 'Ê†áÈ¢ò',
    render(row) {
      const routeName = row.problem_list_mode ? 'problemset_detail' : 'contest_detail';
      return h(
        RouterLink,
        { to: { name: routeName, params: { id: row.id } } },
        {
          default: () =>
            h(
              NButton,
              {
                text: true,
                size: 'small',
              },
              { default: () => row.title }
            ),
        }
      );
    },
  },
  {
    title: 'Êó∂Èó¥',
    render(row) {
      if (row.problem_list_mode) return '-';
      const start_time = new Date(row.start_time),
        end_time = new Date(row.end_time),
        current_time = new Date();
      const start = Number(start_time),
        end = Number(end_time),
        current = Number(current_time);
      const startYear = start_time.getFullYear(),
        endYear = end_time.getFullYear(),
        currentYear = current_time.getFullYear();
      const racing = start < current && current < end,
        sameStartYear = startYear === currentYear,
        sameEndYear = endYear === currentYear;
      return [
        h(NTime, {
          format: sameStartYear ? 'MM-dd HH:mm' : 'yyyy-MM-dd HH:mm',
          time: start,
        }),
        h('span', { style: 'margin: 0 5px' }, '~'),
        h(NTime, {
          format: sameEndYear ? 'MM-dd HH:mm' : 'yyyy-MM-dd HH:mm',
          time: end,
        }),
        racing
          ? h(
              NTag,
              { type: 'success', bordered: false, style: 'margin-left: 5px' },
              { default: () => 'ËøõË°å‰∏≠' }
            )
          : start > current
          ? h(
              NTag,
              { type: 'warning', bordered: false, style: 'margin-left: 5px' },
              { default: () => 'Êú™ÂºÄÂßã' }
            )
          : h(
              NTag,
              { type: 'error', bordered: false, style: 'margin-left: 5px' },
              { default: () => 'Â∑≤ÁªìÊùü' }
            ),
      ];
    },
  },
];
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
© ©Å*cascade08
Åµ µ∂*cascade08
∂∑ ∑∏*cascade08
∏∫ ∫Ω*cascade08
Ω≠
 ≠
Ö*cascade08
Öπ π∫*cascade08
∫ª ªº*cascade08
ºæ æ¡*cascade08
¡© "(205b1bab434999c48e066e66385ba65f03f104f42;file:///root/frontend-naive/src/components/ContestTable.vue:file:///root/frontend-naive