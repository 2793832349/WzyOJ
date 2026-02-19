<script setup>
import { ref, watch, computed } from 'vue';
import Axios from '@/plugins/axios';
import store from '@/store';
import { useRoute } from 'vue-router';
import router from '@/router';
import { AddOutline, SearchOutline, PeopleOutline, SchoolOutline } from '@vicons/ionicons5';
import { _writeSearchToQuery } from '@/plugins/utils';

const route = useRoute();
const message = useMessage();

const pagination = ref({ pageSize: 20, page: 1, count: 0 });
const search = ref('');
const data = ref([]);
const loading = ref(false);

const totalCourses = computed(() => pagination.value.count || 0);

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
  <n-layout class="course-list-page">
    <section class="course-hero">
      <div class="hero-text">
        <p class="hero-kicker">学习中心</p>
        <h1>课程</h1>
        <p class="hero-subtitle">查找、加入并管理你的课程</p>
      </div>
      <div class="hero-metrics">
        <div class="metric-card">
          <n-icon :component="SchoolOutline" />
          <span>{{ totalCourses }}</span>
          <small>课程总数</small>
        </div>
        <div class="metric-card">
          <n-icon :component="PeopleOutline" />
          <span>{{ data.length }}</span>
          <small>当前页课程</small>
        </div>
      </div>
    </section>

    <section class="toolbar-card">
      <div class="toolbar-left">
        <n-form inline>
          <n-form-item label="课程 ID/名称">
            <n-input v-model:value="search" placeholder="输入课程 ID 或名称" @keydown.enter="handleQueryChange" />
          </n-form-item>
          <n-form-item>
            <n-button type="primary" @click="handleQueryChange">
              <template #icon>
                <n-icon :component="SearchOutline" />
              </template>
              搜索
            </n-button>
          </n-form-item>
        </n-form>
      </div>
      <router-link :to="{ name: 'course_create' }" v-if="canManageCourse()">
        <n-button type="primary" class="create-btn">
          <template #icon>
            <n-icon :component="AddOutline" />
          </template>
          创建课程
        </n-button>
      </router-link>
    </section>

    <n-layout-content>
      <n-spin :show="loading">
        <div class="course-grid" v-if="data.length">
          <n-card
            v-for="course in data"
            :key="course.id"
            class="course-card"
            hoverable
            @click="router.push({ name: 'course_detail', params: { id: course.id } })"
          >
            <template #header>
              <div class="course-card-header">
                <div class="course-card-title-wrap">
                  <n-text strong class="course-card-title">{{ course.title }}</n-text>
                  <n-tag v-if="course.is_hidden" type="warning" size="small">隐藏</n-tag>
                </div>
                <n-tag type="info" size="small" :bordered="false">参与人数：{{ course.member_count }}</n-tag>
              </div>
            </template>

            <n-text depth="3" v-if="course.description" class="course-desc">
              {{ course.description }}
            </n-text>
            <n-text depth="3" v-else class="course-desc empty-desc">
              暂无课程描述
            </n-text>

            <div class="course-footer">
              <n-text depth="3">教师：{{ course.teacher?.username }}</n-text>
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
            </div>
          </n-card>
        </div>

        <n-empty v-else description="暂无课程" style="margin-top: 30px" />
      </n-spin>
    </n-layout-content>

    <n-layout-content>
      <div class="pagination-wrap">
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

<style lang="scss" scoped>
.course-list-page {
  padding: 8px 6px 16px;
  --primary-ink: #14345c;
  --soft-ink: #647084;
  --line-color: #dbe5f3;
}

.course-hero {
  display: flex;
  justify-content: space-between;
  align-items: stretch;
  gap: 18px;
  padding: 22px 24px;
  border-radius: 18px;
  background: linear-gradient(135deg, #1f4f86 0%, #356fa8 48%, #5f95ca 100%);
  color: #fff;
  margin-bottom: 16px;
}

.hero-kicker {
  margin: 0;
  font-size: 13px;
  letter-spacing: 0.08em;
  opacity: 0.85;
}

.hero-text h1 {
  margin: 6px 0 2px;
  font-size: 34px;
  line-height: 1.1;
}

.hero-subtitle {
  margin: 0;
  opacity: 0.92;
  font-size: 14px;
}

.hero-metrics {
  display: flex;
  gap: 10px;
}

.metric-card {
  min-width: 132px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.28);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px 10px;
}

.metric-card :deep(.n-icon) {
  font-size: 18px;
  margin-bottom: 2px;
}

.metric-card span {
  font-size: 24px;
  font-weight: 700;
  line-height: 1.2;
}

.metric-card small {
  font-size: 12px;
  opacity: 0.92;
}

.toolbar-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 18px 8px;
  border: 1px solid var(--line-color);
  border-radius: 14px;
  background: #fff;
  margin-bottom: 14px;
}

.create-btn {
  box-shadow: 0 8px 20px rgba(29, 151, 84, 0.24);
}

.course-grid {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 14px;
}

.course-card {
  cursor: pointer;
  border: 1px solid #dce8f8;
  border-left: 4px solid #2f76b9;
  border-radius: 14px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.course-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 22px rgba(30, 66, 109, 0.12);
}

.course-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.course-card-title-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}

.course-card-title {
  color: var(--primary-ink);
  font-size: 20px;
}

.course-desc {
  display: block;
  color: var(--soft-ink);
  margin-bottom: 12px;
}

.empty-desc {
  font-style: italic;
  opacity: 0.7;
}

.course-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.pagination-wrap {
  margin-top: 22px;
  display: flex;
  justify-content: center;
}

@media (max-width: 900px) {
  .course-hero {
    flex-direction: column;
    padding: 18px;
  }

  .hero-metrics {
    width: 100%;
  }

  .metric-card {
    flex: 1;
  }

  .toolbar-card {
    flex-direction: column;
    align-items: stretch;
  }

  .course-card-header,
  .course-footer {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
