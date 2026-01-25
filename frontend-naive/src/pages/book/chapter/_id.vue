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
const chapterId = route.params.chapterId;

const loading = ref(false);
const chapter = ref(null);
const sections = ref([]);

const contentTypeOptions = [
  { label: '文章', value: 'article' },
  { label: '视频', value: 'video' },
  { label: '题目', value: 'problem' },
];

const loadChapter = async () => {
  loading.value = true;
  try {
    chapter.value = await Axios.get(`/book/chapters/${chapterId}/`);
    loadSections();
  } catch (err) {
    message.error('加载章节失败');
  } finally {
    loading.value = false;
  }
};

const loadSections = async () => {
  try {
    const res = await Axios.get('/book/sections/', { params: { chapter_id: chapterId } });
    sections.value = res.results || res;
  } catch (err) {
    console.error('Load sections error:', err);
  }
};

// 小节管理
const showSectionModal = ref(false);
const editingSection = ref(null);
const sectionForm = ref({
  title: '',
  content_type: 'article',
  content: '',
  video_url: '',
  estimated_time: 5,
  order: 0,
});

const openAddSection = () => {
  editingSection.value = null;
  sectionForm.value = {
    title: '',
    content_type: 'article',
    content: '',
    video_url: '',
    estimated_time: 5,
    order: sections.value.length + 1,
  };
  showSectionModal.value = true;
};

const openEditSection = (section) => {
  editingSection.value = section;
  sectionForm.value = {
    title: section.title,
    content_type: section.content_type,
    content: section.content || '',
    video_url: section.video_url || '',
    estimated_time: section.estimated_time,
    order: section.order,
  };
  showSectionModal.value = true;
};

const saveSection = async () => {
  if (!sectionForm.value.title) {
    message.warning('请输入小节标题');
    return;
  }
  try {
    if (editingSection.value) {
      await Axios.put(`/book/sections/${editingSection.value.id}/`, {
        ...sectionForm.value,
        chapter: chapterId,
      });
      message.success('小节已更新');
    } else {
      await Axios.post('/book/sections/', {
        ...sectionForm.value,
        chapter: chapterId,
      });
      message.success('小节已添加');
    }
    showSectionModal.value = false;
    loadSections();
  } catch (err) {
    message.error('保存小节失败');
  }
};

const deleteSection = async (section) => {
  if (!confirm(`确定要删除小节"${section.title}"吗？`)) return;
  try {
    await Axios.delete(`/book/sections/${section.id}/`);
    message.success('小节已删除');
    loadSections();
  } catch (err) {
    message.error('删除失败');
  }
};

const goBack = () => {
  router.push({ name: 'book_edit', params: { id: bookId } });
};

onMounted(() => {
  loadChapter();
});
</script>

<template>
  <div class="chapter-edit-page">
    <n-spin :show="loading">
      <n-space justify="space-between" align="center" style="margin-bottom: 24px">
        <n-space align="center">
          <n-button @click="goBack">← 返回</n-button>
          <h1 style="margin: 0">编辑章节：{{ chapter?.title }}</h1>
        </n-space>
        <n-button type="primary" @click="openAddSection">添加小节</n-button>
      </n-space>

      <n-card title="小节列表">
        <n-list v-if="sections.length > 0">
          <n-list-item v-for="section in sections" :key="section.id">
            <n-space justify="space-between" align="center" style="width: 100%">
              <n-space align="center">
                <n-tag size="small">{{ section.order }}</n-tag>
                <n-tag size="small" :type="section.content_type === 'video' ? 'info' : section.content_type === 'problem' ? 'warning' : 'default'">
                  {{ section.content_type === 'article' ? '文章' : section.content_type === 'video' ? '视频' : '题目' }}
                </n-tag>
                <span style="font-weight: 600">{{ section.title }}</span>
                <span style="color: #999; font-size: 12px">{{ section.estimated_time }} 分钟</span>
              </n-space>
              <n-space>
                <n-button size="small" @click="openEditSection(section)">编辑</n-button>
                <n-button size="small" type="error" @click="deleteSection(section)">删除</n-button>
              </n-space>
            </n-space>
          </n-list-item>
        </n-list>
        <n-empty v-else description="暂无小节，点击上方按钮添加" />
      </n-card>
    </n-spin>

    <!-- 小节编辑弹窗 -->
    <n-modal 
      v-model:show="showSectionModal" 
      preset="card" 
      :title="editingSection ? '编辑小节' : '添加小节'"
      style="width: 800px; max-width: 90vw"
    >
      <n-form :model="sectionForm" label-placement="left" label-width="100px">
        <n-form-item label="小节标题" required>
          <n-input v-model:value="sectionForm.title" placeholder="请输入小节标题" />
        </n-form-item>
        
        <n-form-item label="内容类型">
          <n-select v-model:value="sectionForm.content_type" :options="contentTypeOptions" style="width: 200px" />
        </n-form-item>
        
        <n-form-item label="预计时间">
          <n-input-number v-model:value="sectionForm.estimated_time" :min="1" />
          <span style="margin-left: 8px">分钟</span>
        </n-form-item>
        
        <n-form-item label="排序">
          <n-input-number v-model:value="sectionForm.order" :min="0" />
        </n-form-item>
        
        <n-form-item v-if="sectionForm.content_type === 'video'" label="视频链接">
          <n-input v-model:value="sectionForm.video_url" placeholder="请输入视频链接" />
        </n-form-item>
        
        <n-form-item label="内容" v-if="sectionForm.content_type !== 'problem'">
          <div style="width: 100%">
            <MdEditor v-model:content="sectionForm.content" />
          </div>
        </n-form-item>
      </n-form>
      
      <template #footer>
        <n-space justify="end">
          <n-button @click="showSectionModal = false">取消</n-button>
          <n-button type="primary" @click="saveSection">保存</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<style scoped>
.chapter-edit-page {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}
</style>
