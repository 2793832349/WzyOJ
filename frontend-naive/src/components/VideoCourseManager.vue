<template>
  <div class="video-course-manager">
    <div class="container">
      <h1>视频课程管理</h1>

      <!-- 上传视频部分 -->
      <div class="upload-section" v-if="isTeacher">
        <h2>上传视频课程</h2>
        <div class="upload-form">
          <div class="form-group">
            <label>选择视频文件 (MP4, AVI, MOV 等)</label>
            <div class="file-input-wrapper">
              <input
                type="file"
                ref="fileInput"
                @change="handleFileSelect"
                accept="video/*"
                class="file-input"
              />
              <span class="file-name">
                {{ selectedFile ? selectedFile.name : '点击选择文件或拖拽上传' }}
              </span>
            </div>
            <p class="help-text">最大文件大小: 5GB</p>
          </div>

          <div class="form-group" v-if="selectedFile">
            <label>文件大小: {{ formatFileSize(selectedFile.size) }}</label>
            <div class="progress-bar" v-if="uploadProgress > 0">
              <div class="progress-fill" :style="{ width: uploadProgress + '%' }">
                {{ uploadProgress }}%
              </div>
            </div>
          </div>

          <button
            @click="uploadVideo"
            :disabled="!selectedFile || uploading"
            class="upload-btn"
          >
            {{ uploading ? '上传中...' : '上传视频' }}
          </button>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="error-message">
        {{ error }}
        <button @click="error = null" class="close-btn">×</button>
      </div>

      <!-- 课程章节列表 -->
      <div class="chapters-section">
        <h2>课程章节</h2>
        <div class="chapters-list">
          <div v-if="chapters.length === 0" class="empty-state">
            <p>暂无章节</p>
          </div>

          <div v-for="chapter in chapters" :key="chapter.id" class="chapter-card">
            <div class="chapter-header">
              <h3>{{ chapter.title }}</h3>
              <span class="chapter-order">第 {{ chapter.order }} 章</span>
            </div>

            <p class="chapter-description">{{ chapter.description }}</p>

            <!-- 视频状态 -->
            <div class="video-status">
              <span class="status-label">视频状态:</span>
              <span :class="['status-badge', `status-${chapter.video_status}`]">
                {{ getStatusLabel(chapter.video_status) }}
              </span>
              <span v-if="chapter.error_message" class="error-text">
                {{ chapter.error_message }}
              </span>
            </div>

            <!-- 视频信息 -->
            <div v-if="chapter.video_status === 'completed'" class="video-info">
              <div class="info-item">
                <span class="info-label">时长:</span>
                <span class="info-value">{{ formatTime(chapter.duration) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">分辨率:</span>
                <span class="info-value">{{ chapter.resolution || '未知' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">码率:</span>
                <span class="info-value">{{ chapter.bitrate || '自适应' }}</span>
              </div>
            </div>

            <!-- 视频播放器 -->
            <div v-if="chapter.video_status === 'completed'" class="video-player-wrapper">
              <VideoPlayer :chapterId="chapter.id" :apiBaseUrl="apiBaseUrl" />
            </div>

            <!-- 操作按钮 -->
            <div class="chapter-actions">
              <button
                v-if="isTeacher && chapter.video"
                @click="reprocessVideo(chapter.id)"
                class="action-btn secondary"
                :disabled="chapter.video_status === 'processing'"
              >
                重新处理
              </button>
              <button
                v-if="isTeacher"
                @click="editChapter(chapter.id)"
                class="action-btn secondary"
              >
                编辑
              </button>
              <button
                v-if="isTeacher"
                @click="deleteChapter(chapter.id)"
                class="action-btn danger"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import VideoPlayer from './VideoPlayer.vue'

export default {
  name: 'VideoCourseManager',
  components: {
    VideoPlayer
  },
  props: {
    courseId: {
      type: Number,
      required: true
    },
    apiBaseUrl: {
      type: String,
      default: '/api/course-chapters'
    },
    uploadUrl: {
      type: String,
      default: '/api/course-chapters'
    }
  },
  data() {
    return {
      chapters: [],
      selectedFile: null,
      uploading: false,
      uploadProgress: 0,
      error: null,
      isTeacher: false,
      currentChapterId: null
    }
  },
  mounted() {
    this.loadChapters()
    this.checkTeacherStatus()
  },
  methods: {
    async loadChapters() {
      try {
        const response = await axios.get(this.apiBaseUrl, {
          params: { course_id: this.courseId }
        })
        this.chapters = response.data.results || response.data
      } catch (err) {
        this.error = '加载章节失败: ' + err.message
      }
    },

    checkTeacherStatus() {
      // 这里应该根据实际用户权限检查
      // 简化示例：检查 localStorage 中的用户信息
      try {
        const user = JSON.parse(localStorage.getItem('user') || '{}')
        this.isTeacher = user.is_staff || user.id === this.currentChapterId
      } catch (e) {
        this.isTeacher = false
      }
    },

    handleFileSelect(event) {
      const file = event.target.files[0]
      if (file) {
        // 检查文件大小
        const maxSize = 5 * 1024 * 1024 * 1024 // 5GB
        if (file.size > maxSize) {
          this.error = '文件过大，最大允许 5GB'
          return
        }

        // 检查文件类型
        const allowedTypes = ['video/mp4', 'video/mpeg', 'video/quicktime', 'video/x-matroska']
        if (!allowedTypes.some(type => file.type.includes('video'))) {
          this.error = '不支持的文件格式，请上传视频文件'
          return
        }

        this.selectedFile = file
        this.error = null
      }
    },

    async uploadVideo() {
      if (!this.selectedFile) {
        this.error = '请先选择视频文件'
        return
      }

      if (!this.currentChapterId) {
        this.error = '请先选择课程章节'
        return
      }

      try {
        this.uploading = true
        this.uploadProgress = 0

        const formData = new FormData()
        formData.append('file', this.selectedFile)

        const config = {
          onUploadProgress: (progressEvent) => {
            this.uploadProgress = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            )
          }
        }

        await axios.post(
          `${this.uploadUrl}/${this.currentChapterId}/upload-video/`,
          formData,
          config
        )

        this.error = null
        this.selectedFile = null
        this.uploadProgress = 0
        this.$refs.fileInput.value = ''

        // 重新加载章节列表
        await this.loadChapters()
      } catch (err) {
        this.error = '上传失败: ' + (err.response?.data?.error || err.message)
      } finally {
        this.uploading = false
      }
    },

    async reprocessVideo(chapterId) {
      try {
        await axios.post(`${this.apiBaseUrl}/${chapterId}/reprocess_video/`)
        this.error = null
        await this.loadChapters()
      } catch (err) {
        this.error = '重新处理失败: ' + (err.response?.data?.error || err.message)
      }
    },

    editChapter(chapterId) {
      this.$emit('edit-chapter', chapterId)
    },

    deleteChapter(chapterId) {
      if (confirm('确定删除此章节?')) {
        axios
          .delete(`${this.apiBaseUrl}/${chapterId}/`)
          .then(() => {
            this.loadChapters()
          })
          .catch((err) => {
            this.error = '删除失败: ' + err.message
          })
      }
    },

    getStatusLabel(status) {
      const labels = {
        pending: '待处理',
        processing: '处理中',
        completed: '已完成',
        failed: '处理失败'
      }
      return labels[status] || status
    },

    formatTime(seconds) {
      if (!seconds) return '00:00'
      const hrs = Math.floor(seconds / 3600)
      const mins = Math.floor((seconds % 3600) / 60)
      const secs = Math.floor(seconds % 60)

      if (hrs > 0) {
        return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
      }
      return `${mins}:${secs.toString().padStart(2, '0')}`
    },

    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    }
  }
}
</script>

<style scoped>
.video-course-manager {
  padding: 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  color: #333;
  margin-bottom: 30px;
  font-size: 28px;
}

h2 {
  color: #555;
  margin-top: 30px;
  margin-bottom: 20px;
  font-size: 20px;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
}

/* 上传部分 */
.upload-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
}

.upload-form {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 10px;
  font-weight: 600;
  color: #333;
}

.file-input-wrapper {
  position: relative;
  display: block;
  cursor: pointer;
  padding: 30px;
  border: 2px dashed #3498db;
  border-radius: 8px;
  text-align: center;
  background: #f0f7ff;
  transition: all 0.3s;
}

.file-input-wrapper:hover {
  border-color: #2980b9;
  background: #e8f5ff;
}

.file-input {
  display: none;
}

.file-name {
  color: #666;
  font-size: 14px;
}

.help-text {
  margin-top: 10px;
  color: #999;
  font-size: 12px;
}

.progress-bar {
  height: 10px;
  background: #e0e0e0;
  border-radius: 5px;
  overflow: hidden;
  margin-top: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2980b9);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 10px;
  font-weight: bold;
  transition: width 0.3s;
}

.upload-btn {
  padding: 12px 30px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: background 0.3s;
}

.upload-btn:hover:not(:disabled) {
  background: #2980b9;
}

.upload-btn:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

/* 错误消息 */
.error-message {
  background: #fdeaea;
  color: #c0392b;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #c0392b;
}

/* 章节列表 */
.chapters-list {
  display: grid;
  gap: 20px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  font-size: 16px;
}

.chapter-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chapter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.chapter-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.chapter-order {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.chapter-description {
  color: #666;
  margin: 10px 0;
  font-size: 14px;
}

.video-status {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 15px 0;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
}

.status-label {
  font-weight: 600;
  color: #333;
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

.error-text {
  color: #c0392b;
  font-size: 12px;
  font-weight: 600;
}

.video-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin: 15px 0;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 4px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-label {
  font-weight: 600;
  color: #666;
  font-size: 12px;
}

.info-value {
  color: #333;
  font-size: 14px;
  margin-top: 4px;
}

.video-player-wrapper {
  margin: 20px 0;
}

.chapter-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.3s;
}

.action-btn.secondary {
  background: #e9ecef;
  color: #495057;
}

.action-btn.secondary:hover:not(:disabled) {
  background: #dee2e6;
}

.action-btn.danger {
  background: #f8d7da;
  color: #721c24;
}

.action-btn.danger:hover {
  background: #f5c6cb;
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .chapter-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .chapter-actions {
    flex-wrap: wrap;
  }

  .video-info {
    grid-template-columns: 1fr;
  }
}
</style>
