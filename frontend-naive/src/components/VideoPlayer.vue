<template>
  <div class="video-player-container">
    <!-- 视频加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ loadingMessage }}</p>
    </div>

    <!-- 处理失败状态 -->
    <div v-else-if="error" class="error-state">
      <p class="error-message">{{ error }}</p>
      <button @click="retryLoad" class="retry-btn">重新加载</button>
    </div>

    <!-- HLS 视频播放器 -->
    <div v-else class="video-wrapper">
      <video
        ref="videoPlayer"
        class="video-js vjs-default-skin"
        controls
        preload="auto"
        width="100%"
        height="auto"
        @play="onPlay"
        @pause="onPause"
        @timeupdate="onTimeUpdate"
      >
        <source :src="m3u8Url" type="application/x-mpegURL" />
        <p class="vjs-no-js">
          要查看此视频，请启用 JavaScript，并考虑升级到支持 HTML5 视频的网络浏览器
        </p>
      </video>
    </div>

    <!-- 视频信息 -->
    <div v-if="!loading && !error" class="video-info">
      <div class="info-row">
        <span class="label">时长:</span>
        <span class="value">{{ formatTime(duration) }}</span>
      </div>
      <div class="info-row">
        <span class="label">分辨率:</span>
        <span class="value">{{ resolution || '未知' }}</span>
      </div>
      <div class="info-row">
        <span class="label">码率:</span>
        <span class="value">{{ bitrate || '自适应' }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'VideoPlayer',
  props: {
    chapterId: {
      type: Number,
      required: true
    },
    apiBaseUrl: {
      type: String,
      default: '/api/course-chapters'
    }
  },
  data() {
    return {
      m3u8Url: '',
      duration: 0,
      resolution: '',
      bitrate: '',
      loading: true,
      error: null,
      loadingMessage: '加载中...',
      player: null,
      polling: null
    }
  },
  mounted() {
    this.loadVideoPlaylist()
  },
  beforeUnmount() {
    this.stopPolling()
    if (this.player) {
      this.player.dispose()
    }
  },
  methods: {
    async loadVideoPlaylist() {
      try {
        this.loading = true
        this.error = null
        this.loadingMessage = '加载视频...'

        // 首先检查视频处理状态
        const statusResponse = await axios.get(
          `${this.apiBaseUrl}/${this.chapterId}/video_status/`
        )

        const { video_status, duration, resolution, bitrate, error_message } = statusResponse.data

        // 如果视频处理完成，获取播放列表
        if (video_status === 'completed') {
          const playlistResponse = await axios.get(
            `${this.apiBaseUrl}/${this.chapterId}/video_playlist/`
          )

          this.m3u8Url = playlistResponse.data.m3u8_url
          this.duration = playlistResponse.data.duration
          this.resolution = playlistResponse.data.resolution
          this.bitrate = playlistResponse.data.bitrate

          this.loading = false
          this.$nextTick(() => {
            this.initializePlayer()
          })
        } else if (video_status === 'failed') {
          this.error = `视频处理失败: ${error_message || '未知错误'}`
          this.loading = false
        } else if (video_status === 'processing') {
          this.loadingMessage = '正在处理视频...'
          this.startPolling()
        } else if (video_status === 'pending') {
          this.loadingMessage = '等待处理...'
          this.startPolling()
        }
      } catch (err) {
        console.error('加载视频失败:', err)
        if (err.response?.status === 404) {
          this.error = '视频不存在或未找到'
        } else {
          this.error = `加载失败: ${err.message}`
        }
        this.loading = false
      }
    },

    startPolling() {
      // 每 5 秒检查一次视频处理状态
      this.polling = setInterval(() => {
        this.checkVideoStatus()
      }, 5000)
    },

    stopPolling() {
      if (this.polling) {
        clearInterval(this.polling)
        this.polling = null
      }
    },

    async checkVideoStatus() {
      try {
        const response = await axios.get(
          `${this.apiBaseUrl}/${this.chapterId}/video_status/`
        )

        const { video_status, duration, resolution, bitrate, error_message } = response.data

        if (video_status === 'completed') {
          this.stopPolling()
          this.loadVideoPlaylist()
        } else if (video_status === 'failed') {
          this.stopPolling()
          this.error = `视频处理失败: ${error_message || '未知错误'}`
          this.loading = false
        }
      } catch (err) {
        console.error('检查状态失败:', err)
      }
    },

    initializePlayer() {
      // 使用 HTML5 video 标签的原生播放功能
      // 如果需要高级功能，可以集成 Video.js 或 hls.js

      // 这里显示基础的 HTML5 video 播放
      // 如果需要更多功能，可以安装并使用:
      // npm install hls.js
      // 然后在这里初始化 HLS 播放器
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

    onPlay() {
      this.$emit('play')
    },

    onPause() {
      this.$emit('pause')
    },

    onTimeUpdate(event) {
      this.$emit('timeupdate', event.target.currentTime)
    },

    retryLoad() {
      this.error = null
      this.loadVideoPlaylist()
    }
  }
}
</script>

<style scoped>
.video-player-container {
  width: 100%;
  max-width: 100%;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  background: #1a1a1a;
  color: #fff;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.loading-state p,
.error-state p {
  font-size: 16px;
  margin: 10px 0;
}

.error-message {
  color: #e74c3c;
  margin-bottom: 20px;
  text-align: center;
  max-width: 80%;
}

.retry-btn {
  padding: 10px 20px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.retry-btn:hover {
  background: #2980b9;
}

.video-wrapper {
  position: relative;
  width: 100%;
  background: #000;
}

video {
  width: 100%;
  height: auto;
  display: block;
}

.video-info {
  padding: 15px;
  background: #f8f9fa;
  border-top: 1px solid #e0e0e0;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #e0e0e0;
}

.info-row:last-child {
  border-bottom: none;
}

.label {
  font-weight: 600;
  color: #333;
}

.value {
  color: #666;
}

/* HLS 相关样式 */
.video-js {
  width: 100%;
  height: auto;
}

.vjs-no-js {
  padding: 20px;
  background: #f8d7da;
  color: #721c24;
  text-align: center;
}
</style>
