<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useMessage } from 'naive-ui';
import Axios from '@/plugins/axios';
import store from '@/store';

const route = useRoute();
const router = useRouter();
const message = useMessage();
const bookId = route.params.id;

const book = ref(null);
const loading = ref(false);
const activeTab = ref('overview');

const canManage = computed(() => {
  const permissions = store.state.user?.permissions || [];
  return store.state.user?.is_staff || permissions.includes('class') || permissions.includes('problem');
});

const difficultyMap = {
  beginner: { label: '入门', type: 'success' },
  easy: { label: '简单', type: 'info' },
  medium: { label: '中等', type: 'warning' },
  hard: { label: '困难', type: 'error' },
};

const loadBook = async () => {
  loading.value = true;
  try {
    book.value = await Axios.get(`/book/books/${bookId}/`);
  } catch (err) {
    console.error('Failed to load book:', err);
    message.error('加载书籍失败');
  } finally {
    loading.value = false;
  }
};

const startReading = async () => {
  try {
    const res = await Axios.post(`/book/books/${bookId}/start_reading/`);
    if (res.first_section_id) {
      router.push({ name: 'book_section', params: { id: res.first_section_id } });
    } else {
      message.warning('该书籍暂无内容');
    }
  } catch (err) {
    message.error('开始阅读失败');
  }
};

const continueReading = () => {
  if (book.value?.user_progress?.last_section_id) {
    router.push({ name: 'book_section', params: { id: book.value.user_progress.last_section_id } });
  } else {
    startReading();
  }
};

const goToSection = (sectionId) => {
  router.push({ name: 'book_section', params: { id: sectionId } });
};

const totalEstimatedTime = computed(() => {
  if (!book.value?.chapters) return 0;
  let total = 0;
  book.value.chapters.forEach(chapter => {
    chapter.sections?.forEach(section => {
      total += section.estimated_time || 0;
    });
  });
  return total;
});

onMounted(() => {
  loadBook();
});
</script>

<template>
  <div class="book-detail-page">
    <n-spin :show="loading">
      <template v-if="book">
        <!-- 书籍头部 -->
        <div class="book-header">
          <div class="book-cover-large">
            <img v-if="book.cover" :src="book.cover" :alt="book.title" />
            <div v-else class="book-cover-placeholder">
              <span>{{ book.title.substring(0, 2) }}</span>
            </div>
          </div>
          
          <div class="book-info">
            <h1 class="book-title">{{ book.title }}</h1>
            
            <n-space align="center" style="margin-bottom: 12px">
              <n-tag v-if="book.difficulty" :type="difficultyMap[book.difficulty]?.type" size="small">
                {{ difficultyMap[book.difficulty]?.label }}
              </n-tag>
              <n-tag v-for="tag in book.tags" :key="tag" size="small" :bordered="false">
                {{ tag }}
              </n-tag>
            </n-space>
            
            <p class="book-desc">{{ book.description }}</p>
            
            <n-space align="center" style="margin-bottom: 16px; color: #666; font-size: 14px">
              <span>{{ book.chapter_count }} 章 / {{ book.section_count }} 节</span>
              <n-divider vertical />
              <span>预计 {{ totalEstimatedTime }} 分钟</span>
              <n-divider vertical />
              <span>{{ book.reader_count }} 人已读</span>
            </n-space>
            
            <!-- 进度条 -->
            <div v-if="book.user_progress" class="progress-section">
              <n-space justify="space-between" style="margin-bottom: 8px">
                <span>学习进度</span>
                <span>{{ book.user_progress.completed_count }} / {{ book.user_progress.total_count }}</span>
              </n-space>
              <n-progress
                type="line"
                :percentage="book.user_progress.progress_percent"
                :height="8"
                status="success"
              />
            </div>
            
            <n-space style="margin-top: 16px">
              <n-button v-if="book.user_progress" type="primary" size="large" @click="continueReading">
                继续阅读
              </n-button>
              <n-button v-else type="primary" size="large" @click="startReading">
                开始阅读
              </n-button>
              <n-button size="large" @click="router.push({ name: 'book_list' })">
                返回列表
              </n-button>
            </n-space>
          </div>
        </div>
        
        <!-- 标签页 -->
        <n-tabs v-model:value="activeTab" type="line" style="margin-top: 24px">
          <n-tab-pane name="overview" tab="概览">
            <div class="overview-content">
              <h3>📖 书籍简介</h3>
              <p>{{ book.description || '暂无简介' }}</p>
              
              <h3 style="margin-top: 24px">📚 章节概览</h3>
              <n-list>
                <n-list-item v-for="chapter in book.chapters" :key="chapter.id">
                  <n-thing>
                    <template #header>
                      <n-space align="center">
                        <span style="font-weight: 600">{{ chapter.title }}</span>
                        <n-tag size="small" :bordered="false">
                          {{ chapter.completed_count || 0 }} / {{ chapter.section_count }} 已完成
                        </n-tag>
                      </n-space>
                    </template>
                    <template #description>
                      {{ chapter.description || '暂无描述' }}
                    </template>
                  </n-thing>
                </n-list-item>
              </n-list>
            </div>
          </n-tab-pane>
          
          <n-tab-pane name="catalog" tab="目录">
            <div class="catalog-content">
              <n-collapse>
                <n-collapse-item v-for="chapter in book.chapters" :key="chapter.id" :title="chapter.title" :name="chapter.id">
                  <template #header-extra>
                    <n-tag size="small" :type="chapter.completed_count === chapter.section_count ? 'success' : 'default'">
                      {{ chapter.completed_count || 0 }} / {{ chapter.section_count }}
                    </n-tag>
                  </template>
                  
                  <n-list>
                    <n-list-item 
                      v-for="section in chapter.sections" 
                      :key="section.id"
                      class="section-item"
                      @click="goToSection(section.id)"
                    >
                      <n-space align="center" justify="space-between" style="width: 100%">
                        <n-space align="center">
                          <n-icon v-if="section.is_completed" color="#18a058">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                            </svg>
                          </n-icon>
                          <n-icon v-else-if="section.content_type === 'video'" color="#2080f0">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                              <path d="M8 5v14l11-7z"/>
                            </svg>
                          </n-icon>
                          <n-icon v-else-if="section.content_type === 'problem'" color="#f0a020">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
                            </svg>
                          </n-icon>
                          <n-icon v-else color="#666">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                              <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11z"/>
                            </svg>
                          </n-icon>
                          <span>{{ section.title }}</span>
                        </n-space>
                        <span style="color: #999; font-size: 12px">{{ section.estimated_time }} 分钟</span>
                      </n-space>
                    </n-list-item>
                  </n-list>
                </n-collapse-item>
              </n-collapse>
            </div>
          </n-tab-pane>
        </n-tabs>
      </template>
    </n-spin>
  </div>
</template>

<style scoped>
.book-detail-page {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.book-header {
  display: flex;
  gap: 32px;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.book-cover-large {
  width: 200px;
  height: 260px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.book-cover-large img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-cover-placeholder {
  color: white;
  font-size: 48px;
  font-weight: bold;
}

.book-info {
  flex: 1;
}

.book-title {
  margin: 0 0 12px 0;
  font-size: 28px;
  font-weight: 600;
}

.book-desc {
  color: #666;
  line-height: 1.6;
  margin-bottom: 16px;
}

.progress-section {
  background: #f5f5f5;
  padding: 12px 16px;
  border-radius: 8px;
}

.overview-content h3 {
  margin: 0 0 12px 0;
  font-size: 18px;
  color: #333;
}

.overview-content p {
  color: #666;
  line-height: 1.8;
}

.catalog-content {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
}

.section-item {
  cursor: pointer;
  padding: 12px 16px;
  border-radius: 4px;
  transition: background 0.2s;
}

.section-item:hover {
  background: #f5f5f5;
}
</style>
