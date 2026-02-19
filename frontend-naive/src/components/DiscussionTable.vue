<script setup>
import { computed, h } from 'vue';
import { NButton, NTime } from 'naive-ui';
import { RouterLink } from 'vue-router';
import store from '@/store';

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

const canEditRow = (row) => {
  const user = store.state.user || {};
  if (user.is_staff || user.is_superuser) return true;
  return canPublishDiscussion.value && user.id === row?.author?.id;
};

const columns = [
  {
    title: 'ID',
    render(row) {
      return h(
        RouterLink,
        { to: { name: 'discussion_detail', params: { id: row.id } } },
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
    title: '标题',
    render(row) {
      return h(
        RouterLink,
        { to: { name: 'discussion_detail', params: { id: row.id } } },
        {
          default: () =>
            h(
              NButton,
              {
                size: 'small',
                text: true,
              },
              { default: () => row.title }
            ),
        }
      );
    },
  },
  {
    title: '作者',
    render(row) {
      return h(
        RouterLink,
        { to: { name: 'user_detail', params: { id: row.author.id } } },
        {
          default: () =>
            h(
              NButton,
              {
                text: true,
                size: 'small',
              },
              { default: () => row.author.username }
            ),
        }
      );
    },
  },
  {
    title: '关联内容',
    render(row) {
      if (row.related_problem) {
        return h(
          RouterLink,
          {
            to: {
              name: 'problem_detail',
              params: { id: row.related_problem.id },
            },
          },
          {
            default: () =>
              h(
                NButton,
                {
                  text: true,
                  size: 'small',
                },
                {
                  default: () => row.related_problem.title,
                }
              ),
          }
        );
      } else if (row.related_contest) {
        return h(
          RouterLink,
          {
            to: {
              name: 'contest_detail',
              params: { id: row.related_contest.id },
            },
          },
          {
            default: () =>
              h(
                NButton,
                {
                  text: true,
                  size: 'small',
                },
                { default: () => row.related_contest.title }
              ),
          }
        );
      }
      return '-';
    },
  },
  {
    title: '回复数',
    render(row) {
      return row.reply_count;
    },
  },
  {
    title: '最近回复时间',
    render(row) {
      return h(NTime, {
        time: new Date(row.latest_reply_time),
      });
    },
  },
  {
    title: '操作',
    width: 92,
    render(row) {
      if (!canEditRow(row)) return '-';
      return h(
        RouterLink,
        { to: { name: 'discussion_edit', params: { id: row.id } } },
        {
          default: () =>
            h(
              NButton,
              {
                text: true,
                size: 'small',
              },
              { default: () => '编辑' }
            ),
        }
      );
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
