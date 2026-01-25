<template>
  <div>
    <h3>课程录播管理</h3>

    <div>
      <input type="file" @change="onFileChange" accept="video/*" />
      <button @click="upload" :disabled="!file">上传并转码</button>
    </div>

    <div v-if="uploading">上传中...</div>
    <div v-if="job">
      <p>视频 ID: {{ job.id }} 状态: {{ job.status }}</p>
      <p v-if="job.status === 'failed'">错误: {{ job.error }}</p>
    </div>

    <div v-if="m3u8Url" style="margin-top:16px;">
      <video ref="video" controls style="width:100%;max-width:900px;"></video>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import Hls from 'hls.js'

export default {
  name: 'CourseRecorded',
  data() {
    return {
      file: null,
      uploading: false,
      job: null,
      pollTimer: null,
      m3u8Url: '',
    }
  },
  beforeUnmount() {
    if (this.pollTimer) clearInterval(this.pollTimer)
  },
  methods: {
    onFileChange(e) {
      this.file = e.target.files[0] || null
    },
    async upload() {
      if (!this.file) return
      this.uploading = true
      const fd = new FormData()
      fd.append('file', this.file)
      const courseId = this.$route.params.id
      try {
        const res = await axios.post(`/api/course/${courseId}/videos/`, fd, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        this.job = res.data
        this.uploading = false
        this.startPoll()
      } catch (err) {
        this.uploading = false
        console.error(err)
        window.$message.error('上传失败')
      }
    },
    startPoll() {
      if (!this.job) return
      const courseId = this.$route.params.id
      const id = this.job.id
      const poll = async () => {
        try {
          const res = await axios.get(`/api/course/${courseId}/videos/${id}/`)
          this.job = res.data
          if (this.job.status === 'ready') {
            this.m3u8Url = this.job.m3u8_url
            this.initPlayer()
            clearInterval(this.pollTimer)
            this.pollTimer = null
          } else if (this.job.status === 'failed') {
            clearInterval(this.pollTimer)
            this.pollTimer = null
          }
        } catch (e) {
          console.error(e)
        }
      }
      this.pollTimer = setInterval(poll, 4000)
      poll()
    },
    initPlayer() {
      if (!this.m3u8Url) return
      const video = this.$refs.video
      if (Hls.isSupported()) {
        const hls = new Hls()
        hls.loadSource(this.m3u8Url)
        hls.attachMedia(video)
      } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        video.src = this.m3u8Url
      } else {
        window.$message.error('当前浏览器不支持播放 m3u8')
      }
    }
  }
}
</script>