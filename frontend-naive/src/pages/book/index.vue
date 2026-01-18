<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import Axios from '@/plugins/axios';
import store from '@/store';

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

const goToBook = (book) => {
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
    <n-space justify="space-between" align="center" style="margin-bottom: 24px">
      <h1 style="margin: 0">📚 电子书</h1>
      <n-button v-if="canManage" type="primary" @click="router.push({ name: 'book_create' })">
        创建电子书
      </n-button>
    </n-space>

    <n-spin :show="loading">
      <n-grid :cols="3" :x-gap="20" :y-gap="20" v-if="books.length > 0">
        <n-gi v-for="book in books" :key="book.id">
          <n-card hoverable class="book-card" @click="goToBook(book)">
            <template #cover>
              <div class="book-cover">
                <img v-if="book.cover" :src="book.cover" :alt="book.title" />
                <div v-else class="book-cover-placeholder">
                  <n-icon size="48" color="#999">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M21 4H3a1 1 0 0 0-1 1v14a1 1 0 0 0 1 1h18a1 1 0 0 0 1-1V5a1 1 0 0 0-1-1zM4 18V6h16v12H4z"/>
                      <path d="M6.5 8a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zM8 15l3-4 2.5 3 3.5-4.5 4 6H5l3-4.5z"/>
                    </svg>
                  </n-icon>
                  <span>{{ book.title.substring(0, 2) }}</span>
                </div>
              </div>
            </template>
            
            <n-space vertical size="small">
              <n-space align="center" justify="space-between">
                <n-space align="center">
                  <span class="book-title">{{ book.title }}</span>
                  <n-tag v-if="book.difficulty" :type="difficultyMap[book.difficulty]?.type || 'default'" size="small">
                    {{ difficultyMap[book.difficulty]?.label || book.difficulty }}
                  </n-tag>
                  <n-tag v-if="!book.is_published" type="warning" size="small">未发布</n-tag>
                </n-space>
                <n-button v-if="canManage" size="tiny" @click="goToEdit(book, $event)">编辑</n-button>
              </n-space>
              
              <n-ellipsis :line-clamp="2" class="book-desc">
                {{ book.description || '暂无描述' }}
              </n-ellipsis>
              
              <n-space align="center" justify="space-between" style="margin-top: 8px">
                <n-space size="small">
                  <n-tag size="small" :bordered="false">{{ book.chapter_count }} 章</n-tag>
                  <n-tag size="small" :bordered="false">{{ book.section_count }} 节</n-tag>
                </n-space>
                <span class="reader-count">{{ book.reader_count }} 人已读</span>
              </n-space>
              
              <n-progress
                v-if="book.user_progress"
                type="line"
                :percentage="book.user_progress.progress_percent"
                :height="6"
                :show-indicator="false"
                status="success"
              />
            </n-space>
          </n-card>
        </n-gi>
      </n-grid>
      
      <n-empty v-else-if="!loading" description="暂无电子书" />
    </n-spin>
  </div>
</template>

<style scoped>
.book-list-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.book-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.book-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.book-cover {
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-cover-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  font-weight: bold;
}

.book-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.book-desc {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
}

.reader-count {
  font-size: 12px;
  color: #999;
}
</style>
