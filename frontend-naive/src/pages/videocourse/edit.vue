<template>
  <div class="videocourse-edit-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 编辑表单 -->
    <div v-else class="edit-wrapper">
      <h1>{{ isCreate ? '新建录播课' : '编辑录播课' }}</h1>

      <form @submit.prevent="saveCourse" class="edit-form">
        <!-- 基本信息 -->
        <section class="form-section">
          <h2>基本信息</h2>

          <div class="form-group">
            <label for="title">课程名称 *</label>
            <input
              id="title"
              v-model="form.title"
              type="text"
              placeholder="输入课程名称"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="description">课程简介</label>
            <textarea
              id="description"
              v-model="form.description"
              placeholder="输入课程简介"
              rows="4"
              class="form-textarea"
            ></textarea>
          </div>

          <div class="form-group">
            <label>
              <input v-model="form.is_hidden" type="checkbox" />
              隐藏课程（仅教师和已加入的学生可见）
            </label>
          </div>
        </section>

        <!-- 章节管理 -->
        <section v-if="!isCreate" class="form-section">
          <h2>课程章节</h2>

          <button
            type="button"
            class="btn btn-primary"
            @click="openAddChapterModal"
          >
            + 添加章节
          </button>

          <div v-if="form.chapters.length === 0" class="empty-chapters">
            <p>暂无章节，点击上方按钮添加</p>
          </div>

          <div v-else class="chapters-management">
            <div
              v-for="(chapter, idx) in form.chapters"
              :key="chapter.id || idx"
              class="chapter-edit-item"
            >
              <div class="chapter-drag-handle">⋮</div>
              <div class="chapter-edit-content">
                <div class="chapter-edit-row">
                  <input
                    v-model="chapter.order"
                    type="number"
                    placeholder="顺序"
                    class="form-input sm"
                  />
                  <input
                    v-model="chapter.title"
                    type="text"
                    placeholder="章节标题"
                    class="form-input"
                  />
                </div>
                <textarea
                  v-model="chapter.description"
                  placeholder="章节描述"
                  rows="2"
                  class="form-textarea sm"
                ></textarea>

                <!-- 视频上传区域 -->
                <div class="video-upload-area">
                  <h4>章节视频</h4>
                  <div
                    v-if="chapter.video_status === 'completed'"
                    class="video-info-box"
                  >
                    <p>✓ 视频已上传并处理完成</p>
                    <p v-if="chapter.duration" class="video-meta">
                      时长: {{ formatTime(chapter.duration) }} | 分辨率: {{ chapter.resolution }}
                    </p>
                    <button
                      type="button"
                      class="btn btn-sm btn-secondary"
                      @click="openVideoUpload(idx)"
                    >
                      重新上传
                    </button>
                  </div>
                  <div v-else-if="chapter.video" class="video-processing-box">
                    <p>视频处理中: {{ chapter.video_status }}</p>
                    <button
                      type="button"
                      class="btn btn-sm btn-secondary"
                      @click="openVideoUpload(idx)"
                    >
                      更换视频
                    </button>
                  </div>
                  <div v-else class="video-upload-box">
                    <input
                      type="file"
                      accept="video/*"
                      @change="(e) => handleVideoSelect(e, idx)"
                      class="file-input hidden"
                    />
                    <button
                      type="button"
                      class="btn btn-secondary"
                      @click="() => $refs[`videoInput${idx}`]?.click()"
                    >
                      选择视频文件
                    </button>
                    <p class="help-text">最大 5GB，支持 MP4、AVI、MOV 等格式</p>
                  </div>
                </div>
              </div>

              <div class="chapter-actions-mini">
                <button
                  type="button"
                  class="btn btn-sm btn-danger"
                  @click="removeChapter(idx)"
                >
                  删除
                </button>
              </div>
            </div>
          </div>
        </section>

        <!-- 提交按钮 -->
        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="submitting">
            {{ submitting ? '保存中...' : '保存课程' }}
          </button>
          <button
            type="button"
            class="btn btn-secondary"
            @click="$router.back()"
          >
            取消
          </button>
        </div>
      </form>

      <!-- 添加章节模态框 -->
      <div v-if="showAddChapterModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-content">
          <h3>添加章节</h3>

          <div class="form-group">
            <label for="newChapterTitle">章节标题 *</label>
            <input
              id="newChapterTitle"
              v-model="newChapter.title"
              type="text"
              placeholder="输入章节标题"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="newChapterDesc">章节描述</label>
            <textarea
              id="newChapterDesc"
              v-model="newChapter.description"
              placeholder="输入章节描述"
              rows="3"
              class="form-textarea"
            ></textarea>
          </div>

          <div class="modal-actions">
            <button
              type="button"
              class="btn btn-primary"
              @click="addChapter"
              :disabled="!newChapter.title"
            >
              添加
            </button>
            <button
              type="button"
              class="btn btn-secondary"
              @click="closeModal"
            >
              取消
            </button>
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

const route = useRoute()
const router = useRouter()
const message = useMessage()

const loading = ref(false)
const submitting = ref(false)
const showAddChapterModal = ref(false)

const form = ref({
  title: '',
  description: '',
  is_hidden: false,
  chapters: []
})

const newChapter = ref({
  title: '',
  description: ''
})

const courseId = computed(() => route.params.id)
const isCreate = computed(() => !courseId.value || courseId.value === 'create')

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

const loadCourse = () => {
  if (isCreate.value) return

  loading.value = true
  Axios.get(`/course/course/${courseId.value}/`)
    .then((res) => {
      form.value = {
        title: res.title,
        description: res.description,
        is_hidden: res.is_hidden,
        chapters: res.chapters || []
      }
    })
    .catch(() => {
      message.error('加载课程失败')
    })
    .finally(() => {
      loading.value = false
    })
}

const openAddChapterModal = () => {
  newChapter.value = { title: '', description: '' }
  showAddChapterModal.value = true
}

const closeModal = () => {
  showAddChapterModal.value = false
}

const addChapter = () => {
  if (!newChapter.value.title) {
    message.error('请输入章节标题')
    return
  }

  const chapter = {
    title: newChapter.value.title,
    description: newChapter.value.description,
    order: form.value.chapters.length + 1,
    video: null,
    video_status: 'pending'
  }

  form.value.chapters.push(chapter)
  closeModal()
  message.success('章节已添加')
}

const removeChapter = (idx) => {
  if (confirm('确定要删除此章节吗?')) {
    form.value.chapters.splice(idx, 1)
    message.success('章节已删除')
  }
}

const handleVideoSelect = (event, idx) => {
  const file = event.target.files[0]
  if (!file) return

  // 验证文件大小（5GB）
  const maxSize = 5 * 1024 * 1024 * 1024
  if (file.size > maxSize) {
    message.error('文件过大，最大允许 5GB')
    return
  }

  // 这里可以实现视频上传逻辑
  message.info('视频将在保存课程时上传')
  form.value.chapters[idx].video = file
}

const openVideoUpload = (idx) => {
  message.info('选择视频文件重新上传')
}

const saveCourse = () => {
  if (!form.value.title) {
    message.error('请输入课程名称')
    return
  }

  submitting.value = true

  const data = {
    title: form.value.title,
    description: form.value.description,
    is_hidden: form.value.is_hidden
  }

  const url = isCreate.value ? '/course/course/' : `/course/course/${courseId.value}/`
  const method = isCreate.value ? 'post' : 'put'

  Axios[method](url, data)
    .then((res) => {
      message.success(isCreate.value ? '课程创建成功' : '课程保存成功')

      // 如果有章节需要上传视频，继续处理
      if (form.value.chapters.length > 0) {
        // 这里可以实现章节和视频的保存逻辑
        message.info('章节内容将在下一步保存')
      }

      router.push({
        name: 'videocourse_detail',
        params: { id: res.id }
      })
    })
    .catch(() => {
      message.error('保存失败，请重试')
    })
    .finally(() => {
      submitting.value = false
    })
}

onMounted(() => {
  if (!isCreate.value) {
    loadCourse()
  }
})
</script>

<style scoped>
.videocourse-edit-container {
  max-width: 900px;
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

.edit-wrapper h1 {
  margin: 0 0 30px 0;
  font-size: 28px;
  color: #333;
}

.edit-form {
  background: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 30px;
}

.form-section h2 {
  margin: 0 0 20px 0;
  font-size: 18px;
  color: #333;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 10px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 600;
  font-size: 14px;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.form-input.sm {
  padding: 8px 10px;
  font-size: 13px;
}

.form-textarea.sm {
  font-size: 13px;
}

.chapters-management {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 20px;
}

.chapter-edit-item {
  display: flex;
  gap: 12px;
  padding: 15px;
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.chapter-drag-handle {
  padding: 10px;
  color: #999;
  cursor: grab;
}

.chapter-edit-content {
  flex: 1;
}

.chapter-edit-row {
  display: flex;
  gap: 12px;
  margin-bottom: 10px;
}

.chapter-edit-row input:first-child {
  width: 80px;
}

.chapter-edit-row input:last-child {
  flex: 1;
}

.video-upload-area {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ddd;
}

.video-upload-area h4 {
  margin: 0 0 10px 0;
  font-size: 13px;
  color: #666;
  font-weight: 600;
}

.video-info-box,
.video-processing-box,
.video-upload-box {
  background: white;
  padding: 12px;
  border-radius: 4px;
  border: 1px dashed #3498db;
}

.video-info-box p,
.video-processing-box p {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #666;
}

.video-meta {
  color: #999;
  font-size: 11px;
}

.video-upload-box {
  text-align: center;
}

.video-upload-box button {
  margin: 0 auto 8px;
}

.help-text {
  margin: 0;
  color: #999;
  font-size: 11px;
}

.chapter-actions-mini {
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.btn {
  padding: 10px 20px;
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

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-primary:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background: #7f8c8d;
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

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 30px;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.modal-content h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  color: #333;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  justify-content: flex-end;
}

.empty-chapters {
  text-align: center;
  padding: 30px;
  color: #999;
  background: #f8f9fa;
  border-radius: 4px;
  margin-top: 15px;
}

.file-input.hidden {
  display: none;
}

@media (max-width: 768px) {
  .edit-form {
    padding: 20px;
  }

  .chapter-edit-item {
    flex-direction: column;
  }

  .form-actions {
    flex-direction: column;
  }

  .form-actions .btn {
    width: 100%;
  }
}
</style>
