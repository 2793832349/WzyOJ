<template>
  <div class="videocourse-detail-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 课程详情 -->
    <div v-else class="detail-wrapper">
      <!-- 课程头部 -->
      <div class="course-header">
        <div class="header-left">
          <h1>{{ course.title }}</h1>
          <p class="meta">
            <span>讲师: {{ course.teacher?.real_name || course.teacher?.username }}</span>
            <span>学生: {{ course.member_count }} 人</span>
            <span v-if="course.chapters">章节: {{ course.chapters.length }} 个</span>
          </p>
          <p class="description">{{ course.description }}</p>
        </div>
        <div class="header-actions">
          <button
            v-if="!course.joined && !isTeacher"
            class="btn btn-primary"
            @click="joinCourse"
          >
            加入课程
          </button>
          <button
            v-if="course.joined && !isTeacher"
            class="btn btn-secondary"
            @click="leaveCourse"
          >
            退出课程
          </button>
          <button
            v-if="isTeacher && isTeacherOfCourse"
            class="btn btn-warning"
            @click="goToEdit"
          >
            编辑课程
          </button>
        </div>
      </div>

      <!-- 课程章节 -->
      <div class="chapters-section">
        <h2>课程内容</h2>

        <div v-if="!course.chapters || course.chapters.length === 0" class="empty-chapters">
          <p>暂无章节内容</p>
        </div>

        <div v-else class="chapters-list">
          <div
            v-for="chapter in course.chapters"
            :key="chapter.id"
            class="chapter-item"
          >
            <!-- 章节标题和操作 -->
            <div class="chapter-header" @click="toggleChapter(chapter.id)">
              <div class="chapter-left">
                <span class="expand-icon" :class="{ expanded: expandedChapter === chapter.id }">
                  ▶
                </span>
                <span class="chapter-number">第 {{ chapter.order }} 章</span>
                <span class="chapter-title">{{ chapter.title }}</span>
              </div>
              <div class="chapter-status">
                <span
                  v-if="chapter.video_status"
                  class="status-badge"
                  :class="`status-${chapter.video_status}`"
                >
                  {{ getStatusLabel(chapter.video_status) }}
                </span>
                <span v-if="chapter.duration" class="duration">
                  {{ formatTime(chapter.duration) }}
                </span>
              </div>
            </div>

            <!-- 章节详细内容 -->
            <div v-show="expandedChapter === chapter.id" class="chapter-content">
              <p v-if="chapter.description" class="chapter-description">
                {{ chapter.description }}
              </p>

              <!-- 视频播放器 -->
              <div v-if="chapter.video_status === 'completed'" class="video-player-section">
                <h4>视频讲义</h4>
                <VideoPlayer :chapterId="chapter.id" :apiBaseUrl="apiBaseUrl" />
              </div>

              <!-- 视频处理状态 -->
              <div v-else-if="chapter.video" class="video-status-section">
                <h4>视频状态</h4>
                <div class="status-info">
                  <span class="status-label">处理状态:</span>
                  <span class="status-value" :class="`status-${chapter.video_status}`">
                    {{ getStatusLabel(chapter.video_status) }}
                  </span>
                  <p v-if="chapter.error_message" class="error-message">
                    {{ chapter.error_message }}
                  </p>
                </div>
              </div>

              <div v-else class="no-video">
                <p>该章节暂无视频</p>
              </div>

              <!-- 章节练习题 -->
              <div v-if="chapter.problems && chapter.problems.length > 0" class="problems-section">
                <h4>章节练习 ({{ chapter.solved_count }}/{{ chapter.total_count }})</h4>
                <div class="problems-list">
                  <div
                    v-for="problem in chapter.problems"
                    :key="problem.id"
                    class="problem-item"
                  >
                    <a :href="`/problem/${problem.problem.id}/`" class="problem-link">
                      <span class="problem-id">#{{ problem.problem.id }}</span>
                      <span class="problem-title">{{ problem.problem.title }}</span>
                      <span v-if="isSolved(problem.problem.id)" class="solved-badge">✓</span>
                    </a>
                  </div>
                </div>
              </div>

              <!-- 编辑按钮 -->
              <div v-if="isTeacher && isTeacherOfCourse" class="chapter-actions">
                <button class="btn btn-sm btn-warning" @click="editChapter(chapter.id)">
                  编辑章节
                </button>
                <button class="btn btn-sm btn-danger" @click="deleteChapter(chapter.id)">
                  删除章节
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Axios from '@/plugins/axios'
import store from '@/store'
import VideoPlayer from '@/components/VideoPlayer.vue'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const course = ref({
  chapters: []
})
const loading = ref(false)
const expandedChapter = ref(null)

const courseId = computed(() => route.params.id)
const currentUserId = computed(() => store.state.user?.id)
const isTeacher = computed(() => store.state.user?.is_staff || false)
const isTeacherOfCourse = computed(() => course.value.teacher?.id === currentUserId.value)
const apiBaseUrl = '/api/course-chapters'

const getStatusLabel = (status) => {
  const labels = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '处理失败'
  }
  return labels[status] || status
}

const formatTime = (seconds) => {
  if (!seconds) return '00:00'
  const hrs = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)

  if (hrs > 0) {
    return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const toggleChapter = (chapterId) => {
  expandedChapter.value = expandedChapter.value === chapterId ? null : chapterId
}

const isSolved = (problemId) => {
  return course.value.solved_problem_ids?.includes(problemId) || false
}

const loadCourse = () => {
  loading.value = true
  Axios.get(`/course/course/${courseId.value}/`)
    .then((res) => {
      course.value = res
      if (res.chapters && res.chapters.length > 0) {
        expandedChapter.value = res.chapters[0].id
      }
    })
    .catch(() => {
      message.error('加载课程失败')
    })
    .finally(() => {
      loading.value = false
    })
}

const joinCourse = () => {
  Axios.post(`/course/course/${courseId.value}/join/`)
    .then(() => {
      message.success('加入课程成功')
      loadCourse()
    })
    .catch(() => {
      message.error('加入课程失败')
    })
}

const leaveCourse = () => {
  if (confirm('确定要退出此课程吗?')) {
    Axios.post(`/course/course/${courseId.value}/leave/`)
      .then(() => {
        message.success('已退出课程')
        loadCourse()
      })
      .catch(() => {
        message.error('退出课程失败')
      })
  }
}

const goToEdit = () => {
  router.push({ name: 'videocourse_edit', params: { id: courseId.value } })
}

const editChapter = (chapterId) => {
  // 这里可以实现编辑章节的逻辑
  message.info('编辑章节功能开发中')
}

const deleteChapter = (chapterId) => {
  if (confirm('确定要删除此章节吗?')) {
    Axios.delete(`/course-chapters/${chapterId}/`)
      .then(() => {
        message.success('章节已删除')
        loadCourse()
      })
      .catch(() => {
        message.error('删除失败')
      })
  }
}

onMounted(() => {
  loadCourse()
})
</script>

<style scoped>
.videocourse-detail-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
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

.detail-wrapper {
  background: white;
  border-radius: 8px;
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 30px;
  padding: 30px;
  border-bottom: 1px solid #e0e0e0;
}

.header-left {
  flex: 1;
}

.course-header h1 {
  margin: 0 0 10px 0;
  font-size: 28px;
  color: #333;
}

.meta {
  margin: 10px 0;
  color: #666;
  font-size: 14px;
}

.meta span {
  margin-right: 20px;
}

.description {
  margin: 15px 0 0 0;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

.header-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 120px;
}

.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background: #7f8c8d;
}

.btn-warning {
  background: #f39c12;
  color: white;
}

.btn-warning:hover {
  background: #d68910;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background: #c0392b;
}

.chapters-section {
  padding: 30px;
}

.chapters-section h2 {
  margin: 0 0 20px 0;
  font-size: 20px;
  color: #333;
}

.empty-chapters {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.chapters-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.chapter-item {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.chapter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  cursor: pointer;
  user-select: none;
  transition: background 0.3s;
}

.chapter-header:hover {
  background: #e9ecef;
}

.chapter-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.expand-icon {
  display: inline-block;
  font-size: 12px;
  transition: transform 0.3s;
  color: #666;
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.chapter-number {
  color: #999;
  font-size: 12px;
  font-weight: 600;
}

.chapter-title {
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.chapter-status {
  display: flex;
  align-items: center;
  gap: 15px;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-pending {
  background: #fff3cd;
  color: #856404;
}

.status-processing {
  background: #cce5ff;
  color: #004085;
}

.status-completed {
  background: #d4edda;
  color: #155724;
}

.status-failed {
  background: #f8d7da;
  color: #721c24;
}

.duration {
  color: #666;
  font-size: 12px;
}

.chapter-content {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
}

.chapter-description {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
  margin: 0 0 20px 0;
}

.video-player-section,
.video-status-section,
.problems-section {
  margin-bottom: 20px;
}

.video-player-section h4,
.video-status-section h4,
.problems-section h4 {
  margin: 0 0 15px 0;
  font-size: 14px;
  color: #333;
  font-weight: 600;
}

.video-player-section {
  background: #000;
  border-radius: 4px;
  padding: 15px;
}

.status-info {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-label {
  color: #666;
  font-weight: 600;
}

.status-value {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.error-message {
  color: #c0392b;
  margin: 10px 0 0 0;
  font-size: 12px;
}

.no-video {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 4px;
  text-align: center;
  color: #999;
}

.problems-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.problem-item {
  background: #f8f9fa;
  border-radius: 4px;
  padding: 0;
}

.problem-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 15px;
  text-decoration: none;
  color: #333;
  transition: background 0.3s;
}

.problem-link:hover {
  background: #e9ecef;
}

.problem-id {
  color: #999;
  font-size: 12px;
  font-weight: 600;
  min-width: 40px;
}

.problem-title {
  flex: 1;
  color: #333;
  font-size: 14px;
}

.solved-badge {
  color: #27ae60;
  font-weight: bold;
  font-size: 16px;
}

.chapter-actions {
  display: flex;
  gap: 10px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .course-header {
    flex-direction: column;
  }

  .header-actions {
    flex-direction: row;
    width: 100%;
  }

  .header-actions .btn {
    flex: 1;
  }

  .chapter-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .chapter-status {
    width: 100%;
  }
}
</style>
