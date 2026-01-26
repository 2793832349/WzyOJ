<template>
  <div class="videocourse-container">
    <!-- 页面标题和操作栏 -->
    <div class="header-section">
      <h1>📹 录播课程</h1>
      <button
        v-if="isTeacher"
        class="create-btn"
        @click="$router.push({ name: 'videocourse_create' })"
      >
        <i class="icon">+</i> 新建录播课
      </button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-section">
      <input
        v-model="search"
        type="text"
        placeholder="搜索课程名称..."
        @keyup.enter="handleSearch"
        class="search-input"
      />
      <button @click="handleSearch" class="search-btn">搜索</button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 课程列表 -->
    <div v-else class="courses-grid">
      <div v-if="data.length === 0" class="empty-state">
        <p>暂无录播课程</p>
      </div>

      <div
        v-for="course in data"
        :key="course.id"
        class="course-card"
        @click="goToCourseDetail(course.id)"
      >
        <div class="course-cover">
          <div class="cover-placeholder">📺</div>
        </div>

        <div class="course-info">
          <h3>{{ course.title }}</h3>
          <p class="description">{{ course.description }}</p>

          <div class="course-meta">
            <div class="meta-item">
              <span class="label">讲师:</span>
              <span class="value">{{ course.teacher.real_name || course.teacher.username }}</span>
            </div>
            <div class="meta-item">
              <span class="label">学生:</span>
              <span class="value">{{ course.member_count }} 人</span>
            </div>
            <div class="meta-item">
              <span class="label">章节:</span>
              <span class="value">{{ course.chapter_count || 0 }} 个</span>
            </div>
          </div>

          <div class="course-actions">
            <button
              v-if="!course.joined"
              class="action-btn join-btn"
              @click.stop="joinCourse(course.id)"
            >
              加入课程
            </button>
            <button
              v-else
              class="action-btn joined-btn"
              @click.stop="leaveCourse(course.id)"
            >
              已加入
            </button>

            <button
              v-if="isTeacher && course.teacher.id === currentUserId"
              class="action-btn edit-btn"
              @click.stop="goToEdit(course.id)"
            >
              编辑
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="pagination.count > 0" class="pagination">
      <button
        :disabled="pagination.page === 1"
        @click="pagination.page--"
        class="page-btn"
      >
        上一页
      </button>
      <span class="page-info">
        第 {{ pagination.page }} / {{ Math.ceil(pagination.count / pagination.pageSize) }} 页
      </span>
      <button
        :disabled="pagination.page * pagination.pageSize >= pagination.count"
        @click="pagination.page++"
        class="page-btn"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Axios from '@/plugins/axios'
import store from '@/store'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const pagination = ref({ pageSize: 12, page: 1, count: 0 })
const search = ref('')
const data = ref([])
const loading = ref(false)

const currentUserId = computed(() => store.state.user?.id)
const isTeacher = computed(() => store.state.user?.is_staff || false)

const handleSearch = () => {
  pagination.value.page = 1
  loadCourses()
}

const loadCourses = () => {
  loading.value = true
  Axios.get('/course/course/', {
    params: {
      limit: pagination.value.pageSize,
      offset: (pagination.value.page - 1) * pagination.value.pageSize,
      search: search.value,
    },
  })
    .then((res) => {
      pagination.value.count = res.count
      data.value = res.results.map(course => ({
        ...course,
        chapter_count: course.chapters?.length || 0
      }))
    })
    .catch(() => {
      message.error('加载课程失败')
    })
    .finally(() => {
      loading.value = false
    })
}

const goToCourseDetail = (courseId) => {
  router.push({ name: 'videocourse_detail', params: { id: courseId } })
}

const goToEdit = (courseId) => {
  router.push({ name: 'videocourse_edit', params: { id: courseId } })
}

const joinCourse = (courseId) => {
  Axios.post(`/course/course/${courseId}/join/`)
    .then(() => {
      message.success('加入课程成功')
      loadCourses()
    })
    .catch(() => {
      message.error('加入课程失败')
    })
}

const leaveCourse = (courseId) => {
  if (confirm('确定要退出此课程吗?')) {
    Axios.post(`/course/course/${courseId}/leave/`)
      .then(() => {
        message.success('已退出课程')
        loadCourses()
      })
      .catch(() => {
        message.error('退出课程失败')
      })
  }
}

watch(
  () => pagination.value.page,
  () => loadCourses()
)

loadCourses()
</script>

<style scoped>
.videocourse-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header-section h1 {
  margin: 0;
  font-size: 28px;
  color: #333;
}

.create-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: background 0.3s;
}

.create-btn:hover {
  background: #2980b9;
}

.create-btn i {
  margin-right: 5px;
}

.search-section {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
}

.search-input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.search-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.search-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.search-btn:hover {
  background: #2980b9;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
  font-size: 16px;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.course-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.course-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.course-cover {
  width: 100%;
  height: 160px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.cover-placeholder {
  font-size: 48px;
}

.course-info {
  padding: 15px;
}

.course-info h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

.description {
  color: #666;
  font-size: 12px;
  margin: 0 0 12px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.course-meta {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.meta-item {
  text-align: center;
}

.meta-item .label {
  display: block;
  color: #999;
  font-size: 11px;
}

.meta-item .value {
  display: block;
  color: #333;
  font-size: 13px;
  font-weight: 600;
}

.course-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  flex: 1;
  padding: 8px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.3s;
}

.join-btn {
  background: #f0f0f0;
  color: #333;
}

.join-btn:hover {
  background: #3498db;
  color: white;
}

.joined-btn {
  background: #d4edda;
  color: #155724;
  cursor: default;
}

.joined-btn:hover {
  background: #d4edda;
  color: #155724;
}

.edit-btn {
  background: #f39c12;
  color: white;
  flex: 0.5;
}

.edit-btn:hover {
  background: #d68910;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 30px;
}

.page-btn {
  padding: 8px 16px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.page-btn:hover:not(:disabled) {
  background: #2980b9;
}

.page-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.page-info {
  color: #666;
  font-size: 14px;
}

@media (max-width: 768px) {
  .header-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .courses-grid {
    grid-template-columns: 1fr;
  }

  .course-meta {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
