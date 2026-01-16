<script setup>
import { ref, watch } from 'vue';
import Axios from '@/plugins/axios';
import store from '@/store';
import { useRoute } from 'vue-router';
import router from '@/router';
import { AddOutline } from '@vicons/ionicons5';
import { _writeSearchToQuery } from '@/plugins/utils';

const route = useRoute();
const message = useMessage();

const pagination = ref({ pageSize: 20, page: 1, count: 0 });
const search = ref('');
const data = ref([]);
const loading = ref(false);

const writeSearchToQuery = () => {
  const _search = { search: search.value };
  _writeSearchToQuery(_search, pagination.value, route)();
};

const handleQueryChange = () => {
  if (route.name !== 'course_list') return;

  if (route.query.search) search.value = route.query.search;
  for (const key in pagination.value) {
    if (route.query[key]) pagination.value[key] = parseInt(route.query[key]);
  }

  loading.value = true;
  Axios.get('/course/course/', {
    params: {
      limit: pagination.value.pageSize,
      offset: (pagination.value.page - 1) * pagination.value.pageSize,
      search: search.value,
    },
  })
    .then((res) => {
      pagination.value.count = res.count;
      data.value = res.results;
    })
    .finally(() => {
      loading.value = false;
    });
};

watch(() => route.query, handleQueryChange);
handleQueryChange();

const join = async (course) => {
  await Axios.post(`/course/course/${course.id}/join/`);
  message.success('加入成功');
  handleQueryChange();
};

const leave = async (course) => {
  await Axios.post(`/course/course/${course.id}/leave/`);
  message.success('退出成功');
  handleQueryChange();
};

const canManageCourse = () => {
  return store.state.user?.permissions?.includes('class');
};
</script>

<template>
  <n-layout>
    <h1>课程</h1>

    <n-layout-content>
      <div style="display: inline-block">
        <n-form inline>
          <n-form-item label="课程 ID/名称">
            <n-input v-model:value="search" @keydown.enter="handleQueryChange" />
          </n-form-item>
          <n-form-item>
            <n-button type="primary" @click="handleQueryChange">搜索</n-button>
          </n-form-item>
        </n-form>
      </div>

      <router-link :to="{ name: 'course_create' }" v-if="canManageCourse()">
        <n-button style="float: right; margin-top: 25px" type="primary">
          <template #icon>
            <n-icon :component="AddOutline" />
          </template>
          创建课程
        </n-button>
      </router-link>
    </n-layout-content>

    <n-layout-content>
      <n-spin :show="loading">
        <n-space vertical>
          <n-card
            v-for="course in data"
            :key="course.id"
            hoverable
            style="cursor: pointer"
            @click="router.push({ name: 'course_detail', params: { id: course.id } })"
          >
            <template #header>
              <n-space align="center" justify="space-between">
                <n-space align="center">
                  <n-text strong style="font-size: 18px">{{ course.title }}</n-text>
                  <n-tag v-if="course.is_hidden" type="warning" size="small">隐藏</n-tag>
                </n-space>
                <n-space align="center">
                  <n-text depth="3">参与人数：{{ course.member_count }}</n-text>
                  <n-button
                    size="small"
                    type="primary"
                    v-if="!course.joined"
                    @click.stop="join(course)"
                  >
                    加入
                  </n-button>
                  <n-button
                    size="small"
                    v-else
                    @click.stop="leave(course)"
                  >
                    退出
                  </n-button>
                </n-space>
              </n-space>
            </template>
            <n-text depth="3" v-if="course.description" style="display: block">
              {{ course.description }}
            </n-text>
            <n-text depth="3" style="margin-top: 10px; display: block">
              教师：{{ course.teacher?.username }}
            </n-text>
          </n-card>
        </n-space>
      </n-spin>
    </n-layout-content>

    <n-layout-content>
      <div style="margin-top: 30px; text-align: center">
        <n-pagination
          v-model:page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :item-count="pagination.count"
          show-size-picker
          show-quick-jumper
          :page-sizes="[10, 20, 50]"
          @update:page="writeSearchToQuery"
          @update:page-size="(pageSize) => {
            pagination.pageSize = pageSize;
            pagination.page = 1;
            writeSearchToQuery();
          }"
        />
      </div>
    </n-layout-content>
  </n-layout>
</template>
