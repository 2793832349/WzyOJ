<script setup>
import { computed, ref } from 'vue';
import { useRoute } from 'vue-router';
import Axios from '@/plugins/axios';
import router from '@/router';
import store from '@/store';
import MdEditor from '@/components/MdEditor.vue';

const route = useRoute();
const message = useMessage();

const id = route.params.id;
const course = ref({ chapters: [] });
const loading = ref(false);

const liveSession = ref(null);
const loadingLive = ref(false);

const canManage = computed(() => {
  return store.state.user?.permissions?.includes('class') && (store.state.user?.is_staff || store.state.user?.id === course.value.teacher?.id);
});

const loadData = () => {
  loading.value = true;
  Axios.get(`/course/course/${id}/`)
    .then((res) => {
      course.value = res;
    })
    .finally(() => {
      loading.value = false;
    });
};

const loadLiveSession = () => {
  loadingLive.value = true;
  Axios.get('/live/session/active/', { params: { course_id: Number(id) } })
    .then((res) => {
      liveSession.value = res.session;
    })
    .finally(() => {
      loadingLive.value = false;
    });
};

loadData();
loadLiveSession();

const join = async () => {
  await Axios.post(`/course/course/${id}/join/`);
  message.success('加入成功');
  loadData();
  loadLiveSession();
};

const leave = async () => {
  await Axios.post(`/course/course/${id}/leave/`);
  message.success('退出成功');
  loadData();
  loadLiveSession();
};

const enterLive = async () => {
  if (!course.value.joined && !canManage.value) {
    message.error('请先加入课程');
    return;
  }

  if (liveSession.value) {
    router.push({ name: 'course_live', params: { id }, query: { session_id: liveSession.value.id } });
    return;
  }

  if (!canManage.value) {
    message.error('当前暂无直播');
    return;
  }

  const s = await Axios.post('/live/session/start/', { course_id: Number(id) });
  liveSession.value = s;
  router.push({ name: 'course_live', params: { id }, query: { session_id: s.id } });
};

const showCreateChapter = ref(false);
const creatingChapter = ref(false);
const newChapter = ref({ title: '', description: '', order: 0, problem_ids: [] });
const newChapterSelectingProblemId = ref(null);

const showEditChapter = ref(false);
const editingChapter = ref({ id: null, title: '', description: '', order: 0, problem_ids: [] });
const updatingChapter = ref(false);
const editingChapterSelectingProblemId = ref(null);

const showDeleteChapter = ref(false);
const deletingChapter = ref(null);
const deleting = ref(false);

const problemOptions = ref([]);
const loadingProblem = ref(false);
const searchProblem = (search) => {
  if (!search) {
    problemOptions.value = [];
    return;
  }
  loadingProblem.value = true;
  Axios.get('/problem/', { params: { search } })
    .then((res) => {
      res = res.results;
      problemOptions.value = res.map((item) => ({
        label: `#${item.id} | ${item.title}`,
        value: item.id,
      }));
    })
    .finally(() => {
      loadingProblem.value = false;
    });
};

const draggingProblemId = ref(null);

const moveArrayItem = (arr, from, to) => {
  if (!Array.isArray(arr)) return;
  if (from === to) return;
  if (from < 0 || from >= arr.length) return;
  if (to < 0 || to >= arr.length) return;

  const [item] = arr.splice(from, 1);
  const insertIndex = to > from ? to - 1 : to;
  arr.splice(insertIndex, 0, item);
};

const onProblemTagDragStart = (problemId, e) => {
  const normalized = typeof problemId === 'string' ? Number(problemId) : problemId;
  draggingProblemId.value = Number.isNaN(normalized) ? problemId : normalized;
  if (e?.dataTransfer) {
    e.dataTransfer.effectAllowed = 'move';
    try {
      e.dataTransfer.setData('text/plain', String(problemId));
    } catch {
      // ignore
    }
  }
};

const onProblemTagDrop = (problemIds, targetProblemId) => {
  const fromProblemId = draggingProblemId.value;
  if (fromProblemId === null || fromProblemId === undefined) return;
  if (!Array.isArray(problemIds)) return;

  const fromIndex = problemIds.indexOf(fromProblemId);
  const toIndex = problemIds.indexOf(targetProblemId);
  if (fromIndex === -1 || toIndex === -1) return;

  moveArrayItem(problemIds, fromIndex, toIndex);
};

const onProblemTagDragEnd = () => {
  draggingProblemId.value = null;
};

const getProblemLabel = (problemId) => {
  const opt = problemOptions.value.find((o) => o.value === problemId);
  return opt?.label ?? `#${problemId}`;
};

const addProblemIdToChapter = (chapterRefOrObj, problemId) => {
  if (!problemId && problemId !== 0) return;
  const normalized = typeof problemId === 'string' ? Number(problemId) : problemId;
  const pid = Number.isNaN(normalized) ? problemId : normalized;
  const chapter = chapterRefOrObj?.value ?? chapterRefOrObj;
  if (!chapter) return;
  if (!Array.isArray(chapter.problem_ids)) chapter.problem_ids = [];
  if (chapter.problem_ids.includes(pid)) return;
  chapter.problem_ids.push(pid);
};

const removeProblemIdFromChapter = (chapterRefOrObj, problemId) => {
  const chapter = chapterRefOrObj?.value ?? chapterRefOrObj;
  if (!chapter) return;
  if (!Array.isArray(chapter.problem_ids)) return;
  const idx = chapter.problem_ids.indexOf(problemId);
  if (idx === -1) return;
  chapter.problem_ids.splice(idx, 1);
};

const onSelectProblemForNewChapter = (v) => {
  addProblemIdToChapter(newChapter, v);
  newChapterSelectingProblemId.value = null;
};

const onSelectProblemForEditingChapter = (v) => {
  addProblemIdToChapter(editingChapter, v);
  editingChapterSelectingProblemId.value = null;
};

const createChapter = () => {
  if (!newChapter.value.title) {
    message.error('章节标题不能为空');
    return;
  }
  creatingChapter.value = true;
  Axios.post('/course/chapter/', {
    course: Number(id),
    title: newChapter.value.title,
    description: newChapter.value.description,
    order: newChapter.value.order,
    problem_ids: newChapter.value.problem_ids,
  })
    .then(() => {
      message.success('创建成功');
      showCreateChapter.value = false;
      newChapter.value = { title: '', description: '', order: 0, problem_ids: [] };
      loadData();
    })
    .finally(() => {
      creatingChapter.value = false;
    });
};

const openEditChapter = (ch) => {
  editingChapter.value = {
    id: ch.id,
    course: Number(id),
    title: ch.title,
    description: ch.description,
    order: ch.order,
    problem_ids: ch.problems?.map((p) => p.problem.id) || [],
  };
  showEditChapter.value = true;
};

const updateChapter = () => {
  if (!editingChapter.value.title) {
    message.error('章节标题不能为空');
    return;
  }
  updatingChapter.value = true;
  Axios.put(`/course/chapter/${editingChapter.value.id}/`, {
    course: Number(id),
    title: editingChapter.value.title,
    description: editingChapter.value.description,
    order: editingChapter.value.order,
    problem_ids: editingChapter.value.problem_ids,
  })
    .then(() => {
      message.success('修改成功');
      showEditChapter.value = false;
      loadData();
    })
    .finally(() => {
      updatingChapter.value = false;
    });
};

const deleteChapter = (ch) => {
  deletingChapter.value = ch;
  showDeleteChapter.value = true;
};

const confirmDeleteChapter = () => {
  if (!deletingChapter.value) return;
  deleting.value = true;
  Axios.delete(`/course/chapter/${deletingChapter.value.id}/`)
    .then(() => {
      message.success('删除成功');
      showDeleteChapter.value = false;
      deletingChapter.value = null;
      loadData();
    })
    .finally(() => {
      deleting.value = false;
    });
};

const uploadVideo = async (chapterId, file) => {
  const form = new FormData();
  form.append('file', file);
  await Axios.post(`/course/chapter/${chapterId}/upload-video/`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  message.success('上传成功');
  loadData();
};
</script>

<template>
  <n-spin :show="loading">
    <div>
      <h1>#{{ course.id }}&ensp;{{ course.title }}</h1>
      <n-space align="center" style="margin-top: 10px">
        <n-text depth="3">教师：{{ course.teacher?.username }}</n-text>
        <n-text depth="3">参与人数：{{ course.member_count }}</n-text>
        <n-button
          :loading="loadingLive"
          type="warning"
          secondary
          :disabled="!liveSession && !canManage"
          @click="enterLive"
        >
          {{ liveSession ? '进入直播课堂' : (canManage ? '开启直播课堂' : '直播未开启') }}
        </n-button>
        <n-button v-if="canManage" @click="router.push({ name: 'course_edit', params: { id } })">
          编辑课程
        </n-button>
        <n-button v-if="!course.joined" type="primary" @click="join">加入课程</n-button>
        <n-button v-else @click="leave">退出课程</n-button>
      </n-space>

      <div v-if="course.description" style="margin-top: 15px">
        <n-card>
          <MdEditor :content="course.description" :previewOnly="true" />
        </n-card>
      </div>

      <n-divider />

      <n-space justify="space-between" align="center">
        <h2 style="margin: 0">章节</h2>
        <n-button v-if="canManage" type="primary" @click="showCreateChapter = true">新增章节</n-button>
      </n-space>

      <n-collapse accordion style="margin-top: 10px">
        <n-collapse-item
          v-for="ch in course.chapters"
          :key="ch.id"
          :title="`${ch.title}（完成情况：${ch.solved_count}/${ch.total_count}）`"
        >
          <n-space vertical>
            <n-card v-if="ch.description" size="small">
              <MdEditor :content="ch.description" :previewOnly="true" />
            </n-card>

            <n-space v-if="canManage" justify="end">
              <n-button size="small" secondary @click="openEditChapter(ch)">编辑章节</n-button>
              <n-button size="small" type="error" secondary @click="deleteChapter(ch)">删除章节</n-button>
            </n-space>

            <n-card size="small" title="视频" v-if="ch.video_url || canManage">
              <n-space vertical>
                <video v-if="ch.video_url" :src="ch.video_url" controls style="width: 100%" />
                <n-upload
                  v-if="canManage"
                  :max="1"
                  :default-upload="false"
                  accept="video/*"
                  @change="({ file }) => uploadVideo(ch.id, file.file)"
                >
                  <n-button>上传/替换视频</n-button>
                </n-upload>
              </n-space>
            </n-card>

            <n-card size="small" title="题目列表" v-if="ch.problems?.length">
              <n-space vertical>
                <n-button
                  v-for="p in ch.problems"
                  :key="p.problem.id"
                  text
                  @click="router.push({ name: 'problem_detail', params: { id: p.problem.id } })"
                >
                  <n-space align="center" :wrap-item="false" style="gap: 8px">
                    <span>#{{ p.problem.id }} {{ p.problem.title }}</span>
                    <n-tag v-if="p.problem.solved" size="small" type="success" :bordered="false">已完成</n-tag>
                  </n-space>
                </n-button>
              </n-space>
            </n-card>
          </n-space>
        </n-collapse-item>
      </n-collapse>

      <n-modal v-model:show="showCreateChapter" preset="dialog" title="新增章节">
        <n-form :model="newChapter" label-placement="left" label-width="80">
          <n-form-item label="标题" required>
            <n-input v-model:value="newChapter.title" placeholder="请输入章节标题" />
          </n-form-item>
          <n-form-item label="描述">
            <n-input v-model:value="newChapter.description" type="textarea" :rows="3" placeholder="请输入章节描述" />
          </n-form-item>
          <n-form-item label="顺序">
            <n-input-number v-model:value="newChapter.order" />
          </n-form-item>
          <n-form-item label="题目">
            <n-space vertical style="width: 100%">
              <n-select
                v-model:value="newChapterSelectingProblemId"
                filterable
                placeholder="搜索题目并添加"
                :options="problemOptions"
                :loading="loadingProblem"
                clearable
                remote
                @search="searchProblem"
                @update:value="onSelectProblemForNewChapter"
              />
              <n-space v-if="newChapter.problem_ids?.length" wrap>
                <span
                  v-for="pid in newChapter.problem_ids"
                  :key="pid"
                  style="display: inline-flex; cursor: move; user-select: none"
                  draggable="true"
                  @dragstart="(e) => onProblemTagDragStart(pid, e)"
                  @dragover.prevent
                  @drop.prevent="() => onProblemTagDrop(newChapter.problem_ids, pid)"
                  @dragend="onProblemTagDragEnd"
                >
                  <n-tag closable @close="() => removeProblemIdFromChapter(newChapter, pid)">
                    {{ getProblemLabel(pid) }}
                  </n-tag>
                </span>
              </n-space>
            </n-space>
          </n-form-item>
        </n-form>
        <template #action>
          <n-space>
            <n-button @click="showCreateChapter = false">取消</n-button>
            <n-button type="primary" :loading="creatingChapter" @click="createChapter">创建</n-button>
          </n-space>
        </template>
      </n-modal>

      <n-modal v-model:show="showEditChapter" preset="dialog" title="编辑章节">
        <n-form :model="editingChapter" label-placement="left" label-width="80">
          <n-form-item label="标题" required>
            <n-input v-model:value="editingChapter.title" placeholder="请输入章节标题" />
          </n-form-item>
          <n-form-item label="描述">
            <n-input v-model:value="editingChapter.description" type="textarea" :rows="3" placeholder="请输入章节描述" />
          </n-form-item>
          <n-form-item label="顺序">
            <n-input-number v-model:value="editingChapter.order" />
          </n-form-item>
          <n-form-item label="题目">
            <n-space vertical style="width: 100%">
              <n-select
                v-model:value="editingChapterSelectingProblemId"
                filterable
                placeholder="搜索题目并添加"
                :options="problemOptions"
                :loading="loadingProblem"
                clearable
                remote
                @search="searchProblem"
                @update:value="onSelectProblemForEditingChapter"
              />
              <n-space v-if="editingChapter.problem_ids?.length" wrap>
                <span
                  v-for="pid in editingChapter.problem_ids"
                  :key="pid"
                  style="display: inline-flex; cursor: move; user-select: none"
                  draggable="true"
                  @dragstart="(e) => onProblemTagDragStart(pid, e)"
                  @dragover.prevent
                  @drop.prevent="() => onProblemTagDrop(editingChapter.problem_ids, pid)"
                  @dragend="onProblemTagDragEnd"
                >
                  <n-tag closable @close="() => removeProblemIdFromChapter(editingChapter, pid)">
                    {{ getProblemLabel(pid) }}
                  </n-tag>
                </span>
              </n-space>
            </n-space>
          </n-form-item>
        </n-form>
        <template #action>
          <n-space>
            <n-button @click="showEditChapter = false">取消</n-button>
            <n-button type="primary" :loading="updatingChapter" @click="updateChapter">保存</n-button>
          </n-space>
        </template>
      </n-modal>

      <n-modal
        v-model:show="showDeleteChapter"
        preset="dialog"
        title="删除章节"
        type="error"
        :show-icon="true"
      >
        <template #default>
          <n-text>确认删除章节「{{ deletingChapter?.title }}」吗？该操作不可恢复。</n-text>
        </template>
        <template #action>
          <n-space>
            <n-button @click="showDeleteChapter = false" :disabled="deleting">取消</n-button>
            <n-button type="error" :loading="deleting" @click="confirmDeleteChapter">删除</n-button>
          </n-space>
        </template>
      </n-modal>
    </div>
  </n-spin>
</template>
