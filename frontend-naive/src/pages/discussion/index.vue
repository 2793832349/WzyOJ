<script setup>
import { computed, ref, watch } from 'vue';
import Axios from '@/plugins/axios';
import { AddOutline } from '@vicons/ionicons5';
import DiscussionTable from '@/components/DiscussionTable.vue';
import { useRoute } from 'vue-router';
import router from '@/router';
import store from '@/store';
import { _writeSearchToQuery } from '@/plugins/utils';

const route = useRoute();

const pagination = ref({ pageSize: 20, page: 1, count: 0 }),
  search = ref({
    search: route.query.search ?? '',
    related_problem__id: route.query.related_problem__id ?? '',
    related_contest__id: route.query.related_contest__id ?? '',
    author__username: route.query.author__username ?? '',
  }),
  data = ref([]),
  loading = ref(false);

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

const writeSearchToQuery = _writeSearchToQuery(search.value, pagination.value, route);

const handleQueryChange = () => {
  if (route.name !== 'discussion_list') return;

  for (const key in search.value) {
    search.value[key] = route.query[key] ?? '';
  }
  for (const key in pagination.value) {
    if (route.query[key]) pagination.value[key] = parseInt(route.query[key]);
  }

  loading.value = true;
  Axios.get('/discussion/', {
    params: {
      limit: pagination.value.pageSize,
      offset: (pagination.value.page - 1) * pagination.value.pageSize,
      ...search.value,
    },
  })
    .then(res => {
      pagination.value.count = res.count;
      data.value = res.results;
    })
    .finally(() => {
      loading.value = false;
    });
};

watch(() => route.query, handleQueryChange);
handleQueryChange();

const createDiscussion = () => {
  const query = {};
  if (search.value.related_problem__id) {
    query.related_problem__id = search.value.related_problem__id;
  } else if (search.value.related_contest__id) {
    query.related_contest__id = search.value.related_contest__id;
  }
  router.push({ name: 'discussion_create', query });
};
</script>

<template>
  <n-layout class="discussion-list-page">
    <div class="title-wrap">
      <h1 class="page-title">讨论列表</h1>
      <p class="page-subtitle">教师发布高质量题解与讨论，按题目、题单或作者快速检索。</p>
    </div>

    <n-layout-content class="toolbar-wrap">
      <n-form class="search-form" inline>
        <n-form-item label="标题" class="search-item">
          <n-input
            v-model:value="search.search"
            placeholder="请输入"
            @keydown.enter="writeSearchToQuery"
          />
        </n-form-item>
        <n-form-item label="关联题目ID" class="search-item">
          <n-input
            v-model:value="search.related_problem__id"
            type="number"
            placeholder="请输入"
            @keydown.enter="writeSearchToQuery"
          />
        </n-form-item>
        <n-form-item label="关联比赛/题单ID" class="search-item">
          <n-input
            v-model:value="search.related_contest__id"
            type="number"
            placeholder="请输入"
            @keydown.enter="writeSearchToQuery"
          />
        </n-form-item>
        <n-form-item label="作者用户名称" class="search-item">
          <n-input
            v-model:value="search.author__username"
            placeholder="请输入"
            @keydown.enter="writeSearchToQuery"
          />
        </n-form-item>
        <n-form-item class="search-action">
          <n-button type="primary" @click="writeSearchToQuery">搜索</n-button>
        </n-form-item>
      </n-form>

      <n-button
        v-if="canPublishDiscussion"
        class="create-btn"
        type="primary"
        @click="createDiscussion"
      >
        <template #icon>
          <n-icon :component="AddOutline" />
        </template>
        创建讨论
      </n-button>
    </n-layout-content>

    <n-layout-content class="table-wrap">
      <DiscussionTable :data="data" :loading="loading" />
    </n-layout-content>

    <n-layout-content class="pagination-shell">
      <div class="pagination-wrap">
        <n-pagination
          v-model:page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :item-count="pagination.count"
          show-size-picker
          show-quick-jumper
          :page-sizes="[10, 20, 50]"
          @update:page="writeSearchToQuery"
          @update:page-size="
            pageSize => {
              pagination.pageSize = pageSize;
              pagination.page = 1;
              writeSearchToQuery();
            }
          "
        />
      </div>
    </n-layout-content>
  </n-layout>
</template>

<style scoped>
.discussion-list-page {
  width: 100%;
  padding: 6px 2px 18px;
}

.title-wrap {
  margin-bottom: 14px;
}

.page-title {
  margin: 0;
  font-size: 36px;
  font-weight: 800;
  letter-spacing: 0.5px;
  color: #1f2d3d;
}

.page-subtitle {
  margin: 8px 0 0;
  color: #60748a;
  font-size: 14px;
}

.toolbar-wrap {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 14px;
  padding: 16px;
  border-radius: 16px;
  border: 1px solid #e4ecf7;
  background: linear-gradient(180deg, #f7fbff 0%, #ffffff 100%);
  box-shadow: 0 10px 24px rgba(32, 80, 160, 0.07);
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 12px;
  flex: 1;
}

.search-form :deep(.n-form-item-label) {
  color: #3b4d66;
  font-weight: 600;
}

.search-item {
  min-width: 180px;
}

.search-item :deep(.n-input-wrapper) {
  border-radius: 10px;
}

.search-action {
  margin-left: 0;
}

.search-action :deep(.n-button),
.create-btn {
  height: 40px;
  border-radius: 10px;
  font-weight: 600;
}

.create-btn {
  flex: 0 0 auto;
}

.table-wrap {
  background: #fff;
  border: 1px solid #e4ecf7;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 24px rgba(32, 80, 160, 0.07);
}

.pagination-shell {
  margin-top: 12px;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  padding: 12px 8px;
  background: #fff;
  border: 1px solid #e4ecf7;
  border-radius: 14px;
}

@media (max-width: 900px) {
  .discussion-list-page {
    padding: 0 0 14px;
  }

  .page-title {
    font-size: 30px;
  }

  .page-subtitle {
    font-size: 13px;
    line-height: 1.6;
  }

  .toolbar-wrap {
    flex-direction: column;
    align-items: stretch;
    padding: 12px;
    border-radius: 14px;
  }

  .search-form {
    width: 100%;
  }

  .search-item {
    width: 100%;
    min-width: 0;
  }

  .search-item :deep(.n-input),
  .search-item :deep(.n-input-number),
  .search-item :deep(.n-select) {
    width: 100%;
  }

  .search-action :deep(.n-button),
  .create-btn {
    width: 100%;
  }

  .pagination-wrap {
    justify-content: flex-start;
    overflow-x: auto;
    padding-bottom: 6px;
  }
}
</style>
