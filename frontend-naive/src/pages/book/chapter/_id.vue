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

const selectingProblemId = ref(null);
const problemOptions = ref([]);
const loadingProblem = ref(false);
const problemLabelMap = ref({});

const searchProblem = (search) => {
  if (!search) {
    problemOptions.value = [];
    return;
  }
  loadingProblem.value = true;
  Axios.get('/problem/', { params: { search } })
    .then((res) => {
      const results = res?.results ?? res;
      problemOptions.value = (results || []).map((item) => {
        const label = `#${item.id} | ${item.title}`;
        problemLabelMap.value[item.id] = label;
        return {
          label,
          value: item.id,
        };
      });
    })
    .finally(() => {
      loadingProblem.value = false;
    });
};

const normalizeProblemId = (problemId) => {
  if (problemId === null || problemId === undefined || problemId === '') return null;
  const normalized = typeof problemId === 'string' ? Number(problemId) : problemId;
  return Number.isNaN(normalized) ? problemId : normalized;
};

const addProblemIdToSection = (problemId) => {
  const pid = normalizeProblemId(problemId);
  if (pid === null) return;
  if (!Array.isArray(sectionForm.value.problem_ids)) sectionForm.value.problem_ids = [];
  if (sectionForm.value.problem_ids.includes(pid)) return;
  sectionForm.value.problem_ids.push(pid);
};

const onSelectProblemForSection = (problemId) => {
  addProblemIdToSection(problemId);
  selectingProblemId.value = null;
};

const removeProblemIdFromSection = (problemId) => {
  if (!Array.isArray(sectionForm.value.problem_ids)) return;
  const pid = normalizeProblemId(problemId);
  if (pid === null) return;
  const idx = sectionForm.value.problem_ids.indexOf(pid);
  if (idx === -1) return;
  sectionForm.value.problem_ids.splice(idx, 1);
};

const placeholderProblemId = ref(null);
const placeholderVideoUrl = ref('');

const placeholderProblemOptions = computed(() => {
  const ids = Array.isArray(sectionForm.value.problem_ids) ? sectionForm.value.problem_ids : [];
  return ids.map((pid) => ({
    label: getProblemLabel(pid),
    value: pid,
  }));
});

const getProblemPlaceholder = (problemId) => {
  const pid = normalizeProblemId(problemId);
  if (pid === null) return '';
  return `[[problem:${pid}]]`;
};

const getVideoPlaceholder = (url) => {
  const raw = (url ?? '').toString().trim();
  if (!raw) return '';
  return `[[video:${raw}]]`;
};

const copyText = (text, event = undefined) => {
  if (event) event.stopPropagation();
  const input = document.createElement('textarea');
  input.value = text;
  document.body.appendChild(input);
  input.select();
  document.execCommand('copy');
  document.body.removeChild(input);
  message.success('复制成功');
};

const copyProblemPlaceholder = (problemId, event = undefined) => {
  const placeholder = getProblemPlaceholder(problemId);
  if (!placeholder) {
    message.warning('请选择题目');
    return;
  }
  copyText(placeholder, event);
};

const insertProblemPlaceholder = (problemId) => {
  const placeholder = getProblemPlaceholder(problemId);
  if (!placeholder) {
    message.warning('请选择题目');
    return;
  }
  const rawContent = (sectionForm.value.content ?? '').toString();
  if (!rawContent.trim()) {
    sectionForm.value.content = `${placeholder}\n\n`;
    message.success('已插入占位符');
    return;
  }

  let content = rawContent;
  if (!content.endsWith('\n')) content += '\n';
  if (!content.endsWith('\n\n')) content += '\n';
  sectionForm.value.content = `${content}${placeholder}\n\n`;
  message.success('已插入占位符');
};

const copyVideoPlaceholder = (url, event = undefined) => {
  const placeholder = getVideoPlaceholder(url);
  if (!placeholder) {
    message.warning('请输入视频链接');
    return;
  }
  copyText(placeholder, event);
};

const insertVideoPlaceholder = (url) => {
  const placeholder = getVideoPlaceholder(url);
  if (!placeholder) {
    message.warning('请输入视频链接');
    return;
  }
  const rawContent = (sectionForm.value.content ?? '').toString();
  if (!rawContent.trim()) {
    sectionForm.value.content = `${placeholder}\n\n`;
    message.success('已插入占位符');
    return;
  }

  let content = rawContent;
  if (!content.endsWith('\n')) content += '\n';
  if (!content.endsWith('\n\n')) content += '\n';
  sectionForm.value.content = `${content}${placeholder}\n\n`;
  message.success('已插入占位符');
};

const getProblemLabel = (problemId) => {
  const pid = normalizeProblemId(problemId);
  if (pid === null) return '';
  return problemLabelMap.value?.[pid] ?? `#${pid}`;
};

// 小节管理
const showSectionModal = ref(false);
const editingSection = ref(null);
const sectionForm = ref({
  title: '',
  content_type: 'article',
  content: '',
  video_url: '',
  problem_ids: [],
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
    problem_ids: [],
    estimated_time: 5,
    order: sections.value.length + 1,
  };
  placeholderProblemId.value = null;
  placeholderVideoUrl.value = '';
  showSectionModal.value = true;
};

const openEditSection = (section) => {
  editingSection.value = section;
  const ps = Array.isArray(section?.problems) ? section.problems : [];
  ps.forEach((p) => {
    if (!p?.id && p?.id !== 0) return;
    problemLabelMap.value[p.id] = `#${p.id} | ${p.title}`;
  });
  sectionForm.value = {
    title: section.title,
    content_type: section.content_type,
    content: section.content || '',
    video_url: section.video_url || '',
    problem_ids: ps.map((p) => p.id),
    estimated_time: section.estimated_time,
    order: section.order,
  };
  placeholderProblemId.value = ps.length ? ps[0].id : null;
  placeholderVideoUrl.value = section.video_url || '';
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

        <n-form-item label="视频占位符">
          <n-space align="center" :wrap-item="false" style="width: 100%">
            <n-input
              v-model:value="placeholderVideoUrl"
              clearable
              placeholder="请输入视频链接"
              style="width: 260px"
            />
            <n-input
              :value="getVideoPlaceholder(placeholderVideoUrl)"
              placeholder="[[video:URL]]"
              readonly
            />
            <n-button size="small" @click="(e) => copyVideoPlaceholder(placeholderVideoUrl, e)">
              复制
            </n-button>
            <n-button size="small" @click="() => insertVideoPlaceholder(placeholderVideoUrl)">
              插入到末尾
            </n-button>
          </n-space>
        </n-form-item>

        <n-form-item label="关联题目">
          <n-space vertical style="width: 100%">
            <n-select
              v-model:value="selectingProblemId"
              filterable
              remote
              clearable
              placeholder="搜索题目（标题或 ID）"
              :options="problemOptions"
              :loading="loadingProblem"
              @search="searchProblem"
              @update:value="onSelectProblemForSection"
            />
            <n-space wrap>
              <n-tag
                v-for="pid in (sectionForm.problem_ids || [])"
                :key="pid"
                closable
                @close="removeProblemIdFromSection(pid)"
              >
                {{ getProblemLabel(pid) }}
              </n-tag>
            </n-space>
          </n-space>
        </n-form-item>

        <n-form-item
          label="题目占位符"
          v-if="(sectionForm.problem_ids || []).length"
        >
          <n-space align="center" :wrap-item="false" style="width: 100%">
            <n-select
              v-model:value="placeholderProblemId"
              clearable
              placeholder="选择题目"
              :options="placeholderProblemOptions"
              style="width: 260px"
            />
            <n-input
              :value="getProblemPlaceholder(placeholderProblemId)"
              placeholder="[[problem:ID]]"
              readonly
            />
            <n-button
              size="small"
              @click="(e) => copyProblemPlaceholder(placeholderProblemId, e)"
            >
              复制
            </n-button>
            <n-button
              size="small"
              @click="() => insertProblemPlaceholder(placeholderProblemId)"
            >
              插入到末尾
            </n-button>
          </n-space>
        </n-form-item>

        <n-form-item label="内容">
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
