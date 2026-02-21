<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import Axios from '@/plugins/axios';
import store from '@/store';
import {
  BookOutline,
  PeopleOutline,
  LibraryOutline,
  AddOutline,
  CreateOutline,
  SparklesOutline,
  DocumentTextOutline,
} from '@vicons/ionicons5';

const router = useRouter();
const books = ref([]);
const loading = ref(false);

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

const freeCount = computed(() => books.value.filter(b => b.is_free).length);
const paidCount = computed(() => books.value.filter(b => !b.is_free).length);
const totalReaders = computed(() => books.value.reduce((sum, b) => sum + Number(b.reader_count || 0), 0));

const loadBooks = async () => {
  loading.value = true;
  try {
    const res = await Axios.get('/book/books/');
    books.value = res.results || res;
  } catch (err) {
    console.error('Failed to load books:', err);
  } finally {
    loading.value = false;
  }
};

const goToBook = book => {
  router.push({ name: 'book_detail', params: { id: book.id } });
};

const goToEdit = (book, event) => {
  event.stopPropagation();
  router.push({ name: 'book_edit', params: { id: book.id } });
};

onMounted(() => {
  loadBooks();
});
</script>

<template>
  <div class="book-list-page">
    <section class="book-hero">
      <div class="hero-main">
        <n-space align="center" class="hero-kicker" size="small">
          <n-icon :component="SparklesOutline" />
          学习资源中心
        </n-space>
        <h1 class="hero-title">电子书</h1>
        <p class="hero-subtitle">按章节组织知识点，支持免费/付费开通与进度追踪，便于系统化学习。</p>
      </div>

      <div class="hero-metrics">
        <div class="metric-item">
          <span class="metric-label">总书籍</span>
          <span class="metric-value">{{ books.length }}</span>
        </div>
        <div class="metric-item">
          <span class="metric-label">免费 / 付费</span>
          <span class="metric-value">{{ freeCount }} / {{ paidCount }}</span>
        </div>
        <div class="metric-item">
          <span class="metric-label">累计在读</span>
          <span class="metric-value">{{ totalReaders }}</span>
        </div>
      </div>

      <n-space class="hero-actions" v-if="canManage">
        <n-button type="primary" size="large" @click="router.push({ name: 'book_create' })">
          <template #icon><n-icon :component="AddOutline" /></template>
          创建电子书
        </n-button>
      </n-space>
    </section>

    <n-spin :show="loading">
      <n-grid :cols="1" :x-gap="16" :y-gap="16" responsive="screen" s="1" m="1" l="2" xl="2" v-if="books.length > 0">
        <n-gi v-for="book in books" :key="book.id">
          <n-card hoverable class="book-card" @click="goToBook(book)" :bordered="false">
            <div class="book-card-layout">
              <div class="book-visual">
                <img v-if="book.cover" :src="book.cover" :alt="book.title" class="book-cover-img" />
                <div v-else class="book-cover-fallback">
                  <n-icon size="36" color="rgba(255,255,255,0.95)">
                    <LibraryOutline />
                  </n-icon>
                  <span>{{ (book.title || '书').substring(0, 2) }}</span>
                </div>
                <div class="visual-glow" />
              </div>

              <div class="book-main">
                <div class="book-main-head">
                  <n-space size="small" class="book-badges" wrap>
                    <n-tag size="small" :type="book.is_free ? 'success' : 'warning'" :bordered="false" round>
                      {{ book.is_free ? '免费' : '付费' }}
                    </n-tag>
                    <n-tag
                      v-if="book.difficulty"
                      size="small"
                      :type="difficultyMap[book.difficulty]?.type || 'default'"
                      :bordered="false"
                      round
                    >
                      {{ difficultyMap[book.difficulty]?.label || book.difficulty }}
                    </n-tag>
                    <n-tag v-if="!book.is_published" size="small" type="error" :bordered="false" round>未发布</n-tag>
                  </n-space>
                  <span class="book-id">#{{ book.id }}</span>
                </div>

                <h3 class="book-title" :title="book.title">{{ book.title }}</h3>

                <n-ellipsis :line-clamp="2" class="book-desc">
                  {{ book.description || '暂无描述' }}
                </n-ellipsis>

                <div class="book-meta-grid">
                  <div class="meta-chip">
                    <n-icon :component="DocumentTextOutline" />
                    <span>{{ book.chapter_count }} 章 · {{ book.section_count }} 节</span>
                  </div>
                  <div class="meta-chip">
                    <n-icon :component="PeopleOutline" />
                    <span>{{ book.reader_count }} 人已读</span>
                  </div>
                </div>

                <div v-if="book.user_progress" class="progress-wrap">
                  <div class="progress-meta">
                    <span>学习进度</span>
                    <span class="progress-value">{{ book.user_progress.progress_percent || 0 }}%</span>
                  </div>
                  <n-progress
                    type="line"
                    :percentage="book.user_progress.progress_percent"
                    :height="8"
                    :show-indicator="false"
                    status="success"
                  />
                </div>

                <div class="book-card-actions">
                  <n-button tertiary type="primary" @click.stop="goToBook(book)">
                    查看详情
                  </n-button>
                  <n-button v-if="canManage" tertiary @click="goToEdit(book, $event)">
                    <template #icon><n-icon :component="CreateOutline" /></template>
                    编辑
                  </n-button>
                </div>
              </div>
            </div>
          </n-card>
        </n-gi>
      </n-grid>

      <n-empty v-else-if="!loading" description="暂无电子书" style="margin-top: 40px" />
    </n-spin>
  </div>
</template>

<style scoped>
.book-list-page {
  width: 100%;
  max-width: 1240px;
  margin: 0 auto;
  padding: 14px 10px 28px;
}

.book-hero {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: 1.5fr 1fr auto;
  gap: 16px;
  padding: 18px 20px;
  border-radius: 18px;
  border: 1px solid #dce8f8;
  background:
    radial-gradient(95% 120% at 100% 0%, rgba(56, 189, 248, 0.16) 0%, rgba(255, 255, 255, 0) 55%),
    radial-gradient(95% 120% at 0% 100%, rgba(59, 130, 246, 0.14) 0%, rgba(255, 255, 255, 0) 52%),
    linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
}

.hero-kicker {
  margin-bottom: 6px;
  color: #2563eb;
  font-weight: 700;
  font-size: 13px;
}

.hero-title {
  margin: 0;
  font-size: 40px;
  line-height: 1.06;
  color: #1f2f43;
}

.hero-subtitle {
  margin: 8px 0 0;
  color: #5b708a;
  line-height: 1.65;
}

.hero-metrics {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.metric-item {
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(155, 188, 225, 0.46);
  background: rgba(255, 255, 255, 0.78);
}

.metric-label {
  display: block;
  color: #637991;
  font-size: 12px;
}

.metric-value {
  display: block;
  margin-top: 3px;
  color: #223752;
  font-weight: 800;
  font-size: 19px;
}

.hero-actions {
  align-items: flex-start;
}

.hero-actions :deep(.n-button) {
  border-radius: 12px;
  font-weight: 700;
}

.book-card {
  cursor: pointer;
  border: 1px solid #e4ecf8;
  border-radius: 18px;
  overflow: hidden;
  background: #fff;
  box-shadow: 0 8px 20px rgba(23, 52, 93, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.book-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 14px 30px rgba(23, 52, 93, 0.14);
}

.book-card-layout {
  display: grid;
  grid-template-columns: 148px minmax(0, 1fr);
  min-height: 212px;
}

.book-visual {
  position: relative;
  overflow: hidden;
  background: linear-gradient(145deg, #2563eb, #0ea5e9 55%, #14b8a6);
}

.book-cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-cover-fallback {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #fff;
  font-size: 28px;
  font-weight: 800;
}

.visual-glow {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.05), rgba(15, 23, 42, 0.35));
}

.book-main {
  padding: 14px 16px 12px;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.book-main-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.book-id {
  font-size: 12px;
  color: #7488a7;
  font-weight: 700;
  white-space: nowrap;
}

.book-title {
  margin: 8px 0 0;
  font-size: 30px;
  line-height: 1.12;
  color: #1f314d;
  font-weight: 800;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.book-desc {
  margin-top: 8px;
  font-size: 13px;
  color: #607489;
  line-height: 1.65;
  min-height: 40px;
}

.book-meta-grid {
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 8px;
  border-radius: 9px;
  background: #f5f9ff;
  color: #4c6583;
  font-size: 12px;
  border: 1px solid #e3ecf8;
}

.progress-wrap {
  margin-top: 10px;
  padding: 8px;
  border-radius: 10px;
  background: #f8fbff;
  border: 1px solid #e5edf8;
}

.progress-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 12px;
  color: #4b6280;
}

.progress-value {
  font-weight: 700;
  color: #166534;
}

.book-card-actions {
  margin-top: 10px;
  display: flex;
  gap: 8px;
}

.book-card-actions :deep(.n-button) {
  border-radius: 10px;
  font-weight: 700;
}

@media (max-width: 1100px) {
  .book-hero {
    grid-template-columns: 1fr;
  }

  .hero-metrics {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 860px) {
  .book-list-page {
    padding: 8px 4px 18px;
  }

  .book-hero {
    padding: 14px;
    border-radius: 14px;
  }

  .hero-title {
    font-size: 32px;
  }

  .hero-subtitle {
    font-size: 13px;
  }

  .hero-metrics {
    grid-template-columns: 1fr;
  }

  .hero-actions :deep(.n-button) {
    width: 100%;
  }

  .book-card-layout {
    grid-template-columns: 1fr;
  }

  .book-visual {
    height: 140px;
  }

  .book-title {
    font-size: 24px;
  }

  .book-meta-grid {
    grid-template-columns: 1fr;
  }

  .book-card-actions {
    flex-wrap: wrap;
  }

  .book-card-actions :deep(.n-button) {
    width: 100%;
  }
}
</style>
