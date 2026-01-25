<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useMessage } from 'naive-ui';
import Axios from '@/plugins/axios';
import MdEditor from '@/components/MdEditor.vue';

const route = useRoute();
const router = useRouter();
const message = useMessage();
const bookId = route.params.id;
const isEdit = computed(() => !!bookId);

const loading = ref(false);
const saving = ref(false);

const form = ref({
  title: '',
  description: '',
  difficulty: 'beginner',
  tags: [],
  is_published: false,
  is_free: true,
  order: 0,
});

const chapters = ref([]);
const loadingChapters = ref(false);

const difficultyOptions = [
  { label: '入门', value: 'beginner' },
  { label: '简单', value: 'easy' },
  { label: '中等', value: 'medium' },
  { label: '困难', value: 'hard' },
];

const loadBook = async () => {
  if (!bookId) return;
  loading.value = true;
  try {
    const res = await Axios.get(`/book/books/${bookId}/`);
    form.value = {
      title: res.title,
      description: res.description,
      difficulty: res.difficulty,
      tags: res.tags || [],
      is_published: res.is_published,
      is_free: res.is_free,
      order: res.order || 0,
    };
    // 加载章节
    loadChapters();
  } catch (err) {
    message.error('加载书籍失败');
  } finally {
    loading.value = false;
  }
};

const loadChapters = async () => {
  if (!bookId) return;
  loadingChapters.value = true;
  try {
    const res = await Axios.get('/book/chapters/', { params: { book_id: bookId } });
    chapters.value = res.results || res;
  } catch (err) {
    console.error('Load chapters error:', err);
  } finally {
    loadingChapters.value = false;
  }
};

const save = async () => {
  if (!form.value.title) {
    message.warning('请输入书籍标题');
    return;
  }
  saving.value = true;
  try {
    if (isEdit.value) {
      await Axios.put(`/book/books/${bookId}/`, form.value);
      message.success('保存成功');
    } else {
      const res = await Axios.post('/book/books/', form.value);
      message.success('创建成功');
      router.push({ name: 'book_edit', params: { id: res.id } });
    }
  } catch (err) {
    message.error(err.response?.data?.detail || '保存失败');
  } finally {
    saving.value = false;
  }
};

const deleteBook = async () => {
  if (!confirm('确定要删除这本书吗？所有章节和小节都会被删除！')) return;
  try {
    await Axios.delete(`/book/books/${bookId}/`);
    message.success('删除成功');
    router.push({ name: 'book_list' });
  } catch (err) {
    message.error('删除失败');
  }
};

// 章节管理
const showChapterModal = ref(false);
const editingChapter = ref(null);
const chapterForm = ref({ title: '', description: '', order: 0 });

const openAddChapter = () => {
  editingChapter.value = null;
  chapterForm.value = { title: '', description: '', order: chapters.value.length + 1 };
  showChapterModal.value = true;
};

const openEditChapter = (chapter) => {
  editingChapter.value = chapter;
  chapterForm.value = { 
    title: chapter.title, 
    description: chapter.description, 
    order: chapter.order 
  };
  showChapterModal.value = true;
};

const saveChapter = async () => {
  if (!chapterForm.value.title) {
    message.warning('请输入章节标题');
    return;
  }
  try {
    if (editingChapter.value) {
      await Axios.put(`/book/chapters/${editingChapter.value.id}/`, {
        ...chapterForm.value,
        book: bookId,
      });
      message.success('章节已更新');
    } else {
      await Axios.post('/book/chapters/', {
        ...chapterForm.value,
        book: bookId,
      });
      message.success('章节已添加');
    }
    showChapterModal.value = false;
    loadChapters();
  } catch (err) {
    message.error('保存章节失败');
  }
};

const deleteChapter = async (chapter) => {
  if (!confirm(`确定要删除章节"${chapter.title}"吗？所有小节都会被删除！`)) return;
  try {
    await Axios.delete(`/book/chapters/${chapter.id}/`);
    message.success('章节已删除');
    loadChapters();
  } catch (err) {
    message.error('删除失败');
  }
};

const goToEditSection = (chapterId) => {
  router.push({ name: 'book_chapter_edit', params: { id: bookId, chapterId } });
};

onMounted(() => {
  loadBook();
});
</script>

<template>
  <div class="book-edit-page">
    <n-spin :show="loading">
      <n-space justify="space-between" align="center" style="margin-bottom: 24px">
        <h1 style="margin: 0">{{ isEdit ? '编辑电子书' : '创建电子书' }}</h1>
        <n-space>
          <n-button @click="router.push({ name: 'book_list' })">返回列表</n-button>
          <n-button v-if="isEdit" type="error" @click="deleteBook">删除书籍</n-button>
        </n-space>
      </n-space>

      <n-card title="基本信息">
        <n-form :model="form" label-placement="left" label-width="100px">
          <n-form-item label="书籍标题" required>
            <n-input v-model:value="form.title" placeholder="请输入书籍标题" />
          </n-form-item>
          
          <n-form-item label="书籍描述">
            <n-input 
              v-model:value="form.description" 
              type="textarea" 
              placeholder="请输入书籍描述"
              :rows="4"
            />
          </n-form-item>
          
          <n-form-item label="难度">
            <n-select v-model:value="form.difficulty" :options="difficultyOptions" style="width: 200px" />
          </n-form-item>
          
          <n-form-item label="标签">
            <n-dynamic-tags v-model:value="form.tags" />
          </n-form-item>
          
          <n-form-item label="排序">
            <n-input-number v-model:value="form.order" :min="0" />
          </n-form-item>
          
          <n-form-item label="状态">
            <n-space>
              <n-switch v-model:value="form.is_published">
                <template #checked>已发布</template>
                <template #unchecked>未发布</template>
              </n-switch>
              <n-switch v-model:value="form.is_free">
                <template #checked>免费</template>
                <template #unchecked>付费</template>
              </n-switch>
            </n-space>
          </n-form-item>
          
          <n-form-item>
            <n-button type="primary" :loading="saving" @click="save">
              {{ isEdit ? '保存修改' : '创建书籍' }}
            </n-button>
          </n-form-item>
        </n-form>
      </n-card>

      <!-- 章节管理（仅编辑模式） -->
      <n-card v-if="isEdit" title="章节管理" style="margin-top: 16px">
        <template #header-extra>
          <n-button type="primary" size="small" @click="openAddChapter">添加章节</n-button>
        </template>
        
        <n-spin :show="loadingChapters">
          <n-list v-if="chapters.length > 0">
            <n-list-item v-for="chapter in chapters" :key="chapter.id">
              <n-space justify="space-between" align="center" style="width: 100%">
                <n-space align="center">
                  <n-tag size="small">{{ chapter.order }}</n-tag>
                  <span style="font-weight: 600">{{ chapter.title }}</span>
                  <n-tag size="small" :bordered="false">{{ chapter.sections?.length || 0 }} 小节</n-tag>
                </n-space>
                <n-space>
                  <n-button size="small" @click="goToEditSection(chapter.id)">编辑小节</n-button>
                  <n-button size="small" @click="openEditChapter(chapter)">编辑</n-button>
                  <n-button size="small" type="error" @click="deleteChapter(chapter)">删除</n-button>
                </n-space>
              </n-space>
            </n-list-item>
          </n-list>
          <n-empty v-else description="暂无章节，点击上方按钮添加" />
        </n-spin>
      </n-card>
    </n-spin>

    <!-- 章节编辑弹窗 -->
    <n-modal v-model:show="showChapterModal" preset="dialog" :title="editingChapter ? '编辑章节' : '添加章节'">
      <n-form :model="chapterForm" label-placement="left" label-width="80px">
        <n-form-item label="章节标题" required>
          <n-input v-model:value="chapterForm.title" placeholder="请输入章节标题" />
        </n-form-item>
        <n-form-item label="章节描述">
          <n-input v-model:value="chapterForm.description" type="textarea" placeholder="请输入章节描述" />
        </n-form-item>
        <n-form-item label="排序">
          <n-input-number v-model:value="chapterForm.order" :min="0" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-button @click="showChapterModal = false">取消</n-button>
        <n-button type="primary" @click="saveChapter">保存</n-button>
      </template>
    </n-modal>
  </div>
</template>

<style scoped>
.book-edit-page {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}
</style>
