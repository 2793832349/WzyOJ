<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useMessage } from 'naive-ui';
import Axios from '@/plugins/axios';
import MdEditor from '@/components/MdEditor.vue';

const route = useRoute();
const router = useRouter();
const message = useMessage();
const sectionId = route.params.id;

const section = ref(null);
const loading = ref(false);
const isCompleted = ref(false);
const completing = ref(false);

const loadSection = async () => {
  loading.value = true;
  try {
    section.value = await Axios.get(`/book/sections/${sectionId}/`);
    // 记录阅读
    await Axios.post(`/book/sections/${sectionId}/record_read/`);
  } catch (err) {
    console.error('Failed to load section:', err);
    message.error('加载内容失败');
  } finally {
    loading.value = false;
  }
};

const toggleComplete = async () => {
  completing.value = true;
  try {
    if (isCompleted.value) {
      await Axios.post(`/book/sections/${sectionId}/uncomplete/`);
      isCompleted.value = false;
      message.success('已取消完成标记');
    } else {
      await Axios.post(`/book/sections/${sectionId}/complete/`);
      isCompleted.value = true;
      message.success('已标记为完成');
    }
  } catch (err) {
    message.error('操作失败');
  } finally {
    completing.value = false;
  }
};

const goToPrev = () => {
  if (section.value?.prev_section) {
    router.push({ name: 'book_section', params: { id: section.value.prev_section.id } });
  }
};

const goToNext = () => {
  if (section.value?.next_section) {
    router.push({ name: 'book_section', params: { id: section.value.next_section.id } });
  }
};

const goToBook = () => {
  if (section.value?.book_id) {
    router.push({ name: 'book_detail', params: { id: section.value.book_id } });
  }
};

const goToProblem = (problemId) => {
  router.push({ name: 'problem_detail', params: { id: problemId } });
};

onMounted(() => {
  loadSection();
});
</script>

<template>
  <div class="section-page">
    <n-spin :show="loading">
      <template v-if="section">
        <!-- 左侧目录 -->
        <div class="section-layout">
          <div class="section-sidebar">
            <div class="sidebar-header">
              <div class="book-cover-mini" @click="goToBook">
                <span>{{ section.book_title?.substring(0, 2) }}</span>
              </div>
              <div class="book-info-mini">
                <div class="book-title-mini" @click="goToBook">{{ section.book_title }}</div>
              </div>
            </div>
            
            <n-divider style="margin: 12px 0" />
            
            <div class="chapter-title">{{ section.chapter_title }}</div>
          </div>
          
          <!-- 主内容区 -->
          <div class="section-main">
            <!-- 面包屑导航 -->
            <n-breadcrumb style="margin-bottom: 16px">
              <n-breadcrumb-item @click="router.push({ name: 'book_list' })">电子书</n-breadcrumb-item>
              <n-breadcrumb-item @click="goToBook">{{ section.book_title }}</n-breadcrumb-item>
              <n-breadcrumb-item>{{ section.chapter_title }}</n-breadcrumb-item>
              <n-breadcrumb-item>{{ section.title }}</n-breadcrumb-item>
            </n-breadcrumb>
            
            <!-- 标题 -->
            <h1 class="section-title">
              <n-icon v-if="section.content_type === 'video'" color="#2080f0" style="margin-right: 8px">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M8 5v14l11-7z"/>
                </svg>
              </n-icon>
              {{ section.title }}
            </h1>
            
            <!-- 视频内容 -->
            <div v-if="section.content_type === 'video' && section.video_url" class="video-container">
              <n-card title="🎬 视频讲解">
                <video :src="section.video_url" controls style="width: 100%; max-height: 500px"></video>
              </n-card>
            </div>
            
            <!-- Markdown 内容 -->
            <div class="section-content" v-if="section.content">
              <MdEditor :content="section.content" previewOnly />
            </div>
            
            <!-- 关联题目 -->
            <div v-if="section.problems && section.problems.length > 0" class="problems-section">
              <h3>📝 练习题目</h3>
              <n-list>
                <n-list-item v-for="problem in section.problems" :key="problem.id" class="problem-item" @click="goToProblem(problem.id)">
                  <n-space align="center">
                    <n-tag :type="problem.difficulty === 1 ? 'success' : problem.difficulty === 2 ? 'warning' : 'error'" size="small">
                      {{ problem.difficulty === 1 ? '简单' : problem.difficulty === 2 ? '中等' : '困难' }}
                    </n-tag>
                    <span>{{ problem.title }}</span>
                  </n-space>
                </n-list-item>
              </n-list>
            </div>
            
            <!-- 底部导航 -->
            <div class="section-footer">
              <n-space justify="space-between" align="center">
                <n-button 
                  :disabled="!section.prev_section" 
                  @click="goToPrev"
                >
                  ← {{ section.prev_section?.title || '没有上一节' }}
                </n-button>
                
                <n-button 
                  :type="isCompleted ? 'default' : 'success'"
                  :loading="completing"
                  @click="toggleComplete"
                >
                  {{ isCompleted ? '✓ 已完成' : '标记完成' }}
                </n-button>
                
                <n-button 
                  :disabled="!section.next_section" 
                  type="primary"
                  @click="goToNext"
                >
                  {{ section.next_section?.title || '没有下一节' }} →
                </n-button>
              </n-space>
            </div>
          </div>
          
          <!-- 右侧目录 -->
          <div class="section-toc">
            <div class="toc-title">此页内容</div>
            <div class="toc-content">
              <!-- 可以根据 Markdown 内容生成目录 -->
              <div class="toc-item">📖 本节导学</div>
            </div>
          </div>
        </div>
      </template>
    </n-spin>
  </div>
</template>

<style scoped>
.section-page {
  min-height: calc(100vh - 64px);
  background: #f5f5f5;
}

.section-layout {
  display: flex;
  max-width: 1400px;
  margin: 0 auto;
  gap: 0;
}

.section-sidebar {
  width: 260px;
  background: #fff;
  padding: 20px;
  border-right: 1px solid #e8e8e8;
  position: sticky;
  top: 64px;
  height: calc(100vh - 64px);
  overflow-y: auto;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.book-cover-mini {
  width: 60px;
  height: 80px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  cursor: pointer;
}

.book-title-mini {
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
}

.book-title-mini:hover {
  color: #18a058;
}

.chapter-title {
  font-weight: 600;
  color: #333;
  padding: 8px 0;
}

.section-main {
  flex: 1;
  background: #fff;
  padding: 24px 40px;
  min-height: calc(100vh - 64px);
}

.section-title {
  margin: 0 0 24px 0;
  font-size: 28px;
  font-weight: 600;
  display: flex;
  align-items: center;
}

.video-container {
  margin-bottom: 24px;
}

.section-content {
  line-height: 1.8;
  font-size: 16px;
}

.section-content :deep(h1),
.section-content :deep(h2),
.section-content :deep(h3) {
  margin-top: 24px;
  margin-bottom: 12px;
}

.section-content :deep(pre) {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
}

.section-content :deep(code) {
  font-family: 'Consolas', 'Monaco', monospace;
}

.problems-section {
  margin-top: 32px;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}

.problems-section h3 {
  margin: 0 0 16px 0;
}

.problem-item {
  cursor: pointer;
  padding: 12px;
  border-radius: 4px;
  transition: background 0.2s;
}

.problem-item:hover {
  background: #e8e8e8;
}

.section-footer {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #e8e8e8;
}

.section-toc {
  width: 200px;
  padding: 20px;
  position: sticky;
  top: 64px;
  height: calc(100vh - 64px);
  overflow-y: auto;
}

.toc-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
  font-size: 14px;
}

.toc-item {
  padding: 6px 0;
  font-size: 13px;
  color: #666;
  cursor: pointer;
}

.toc-item:hover {
  color: #18a058;
}

@media (max-width: 1200px) {
  .section-toc {
    display: none;
  }
}

@media (max-width: 900px) {
  .section-sidebar {
    display: none;
  }
  
  .section-main {
    padding: 16px;
  }
}
</style>
