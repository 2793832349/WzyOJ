<script setup>
import { ref, onBeforeUnmount, h, watch, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { NButton, useMessage } from 'naive-ui';
import Axios from '@/plugins/axios';
import MdEditor from '@/components/MdEditor.vue';
import CodeMirrorBattle from '@/components/CodeMirrorBattle.vue';
import { languageOptions } from '@/plugins/consts';

const message = useMessage();

const route = useRoute();
const router = useRouter();
const roomId = String(route.params.id || '');

const loading = ref(false);
const starting = ref(false);
const joining = ref(false);
const room = ref(null);
const events = ref([]);
const currentUserId = ref(null);
const firstAcUserId = ref(null);

const language = ref('cpp');
const source = ref('');
const submitting = ref(false);

const ws = ref(null);

const problemDetail = ref(null);
const loadingProblem = ref(false);
const editorRef = ref(null);

// 自测功能
const testInput = ref('');
const testOutput = ref('');
const testRunning = ref(false);
const showTestPanel = ref(false);


// 自测运行
const runTest = async () => {
  if (!source.value) {
    message.warning('请先输入代码');
    return;
  }
  testRunning.value = true;
  testOutput.value = '运行中...';
  try {
    const res = await Axios.post('/submission/debug/', {
      language: language.value,
      source: source.value,
      input: testInput.value,
    });
    testOutput.value = res.output || res.error || '无输出';
  } catch (err) {
    testOutput.value = err.response?.data?.error || '运行失败';
  } finally {
    testRunning.value = false;
  }
};

const loadProblemDetail = async (problemId) => {
  if (!problemId) return;
  loadingProblem.value = true;
  try {
    problemDetail.value = await Axios.get(`/problem/${problemId}/`);
  } catch (err) {
    console.error('Failed to load problem:', err);
  } finally {
    loadingProblem.value = false;
  }
};

watch(() => room.value?.problem?.id, (newProblemId) => {
  if (newProblemId && !problemDetail.value) {
    loadProblemDetail(newProblemId);
  }
});


const loadRoom = async () => {
  loading.value = true;
  try {
    room.value = await Axios.get(`/battle/rooms/${roomId}/`);
    if (!currentUserId.value) {
      const user = await Axios.get('/user/info/');
      currentUserId.value = user.id;
    }
  } finally {
    loading.value = false;
  }
};

const startRoom = async () => {
  starting.value = true;
  try {
    room.value = await Axios.post(`/battle/rooms/${roomId}/start/`);
  } finally {
    starting.value = false;
  }
};

const submit = async () => {
  if (!source.value) return;
  submitting.value = true;
  try {
    const res = await Axios.post(`/battle/rooms/${roomId}/submit/`, {
      language: language.value,
      source: source.value,
    });
    events.value.unshift({ type: 'submission_created', ...res, ts: Date.now() });
  } finally {
    submitting.value = false;
  }
};

const connectWs = () => {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const url = `${protocol}://${window.location.host}/ws/battle/${roomId}/`;
  const socket = new WebSocket(url);
  ws.value = socket;

  socket.onmessage = e => {
    try {
      const data = JSON.parse(e.data);
      events.value.unshift({ ...data, ts: Date.now() });
      if (data.type === 'room_started' && data.room) room.value = data.room;
      if (data.type === 'participant_joined' && data.room) room.value = data.room;
      if (data.type === 'first_ac') {
        firstAcUserId.value = data.user_id;
        loadRoom();
        showFirstAcModal(data);
      }
      if (data.type === 'room_finished') {
        loadRoom();
        showResultModal(data);
      }
    } catch (_) {}
  };

  socket.onclose = () => {
    ws.value = null;
  };
};

const joinRoom = async () => {
  joining.value = true;
  try {
    room.value = await Axios.post(`/battle/rooms/${roomId}/join/`);
  } finally {
    joining.value = false;
  }
};

const leave = async () => {
  await router.push({ name: 'battle_lobby' });
};

const isParticipant = () => {
  if (!room.value || !currentUserId.value) return false;
  return room.value.participants?.some(p => p.user.id === currentUserId.value);
};

const showFirstAcModal = (data) => {
  const acUserId = data.user_id;
  const isMe = acUserId === currentUserId.value;
  
  if (isMe) {
    window.$dialog.success({
      title: '🎉 你首先通过了！',
      content: '恭喜你率先通过题目！等待对方提交或超时后对战结束。',
      positiveText: '继续',
    });
  } else {
    window.$dialog.warning({
      title: '⚠️ 对方首先通过了',
      content: '对方已率先通过题目。你仍可继续提交以获得经验和分数！',
      positiveText: '继续挑战',
    });
  }
};

const showResultModal = (data) => {
  const winnerId = data.winner_id;
  const finishReason = data.finish_reason;
  
  let title = '';
  let content = '';
  let type = 'info';
  
  if (winnerId === currentUserId.value) {
    title = '🎉 胜利！';
    type = 'success';
    if (finishReason === 'first_ac') {
      content = '恭喜你率先通过题目，赢得了本场对战！';
    } else if (finishReason === 'timeout') {
      content = '对战超时，你获得了胜利！';
    } else if (finishReason === 'opponent_give_up') {
      content = '对手放弃了对战，你获得了胜利！';
    }
  } else if (winnerId === null) {
    title = '⚖️ 平局';
    type = 'warning';
    content = '对战超时，双方平局。';
  } else {
    title = '😢 失败';
    type = 'error';
    if (finishReason === 'first_ac') {
      content = '对手率先通过题目，你输掉了本场对战。';
    } else if (finishReason === 'timeout') {
      content = '对战超时，你输掉了本场对战。';
    } else if (finishReason === 'opponent_give_up') {
      content = '你放弃了对战。';
    }
  }
  
  window.$dialog[type]({
    title,
    content,
    positiveText: '确定',
    onPositiveClick: () => {
      // Optional: redirect to lobby
    }
  });
};

const formatEventMessage = (event) => {
  const type = event.type;
  
  if (type === 'submission_created') {
    return `提交 #${event.submission_id} 已创建`;
  } else if (type === 'submission_update') {
    const statusMap = {
      'judging': '判题中',
      'accepted': '通过',
      'wrong_answer': '答案错误',
      'time_limit_exceeded': '超时',
      'memory_limit_exceeded': '内存超限',
      'runtime_error': '运行错误',
      'compile_error': '编译错误',
      'system_error': '系统错误'
    };
    const status = statusMap[event.status] || `状态 ${event.status}`;
    const score = event.score !== undefined && event.score !== 100 ? ` (${event.score}分)` : '';
    return `提交 #${event.submission_id}: ${status}${score}`;
  } else if (type === 'first_ac') {
    const isMe = event.user_id === currentUserId.value;
    return isMe ? '🎉 你首先通过了！对方仍可继续提交' : '⚠️ 对方首先通过了！你仍可继续提交获得经验';
  } else if (type === 'room_finished') {
    const reasonMap = {
      'first_ac': '首次通过',
      'timeout': '超时'
    };
    const reason = reasonMap[event.finish_reason] || event.finish_reason;
    const winner = event.winner_id ? `胜者: ${room.value?.winner?.username || 'Unknown'}` : '平局';
    return `对战结束 - ${reason} - ${winner}`;
  }
  
  return type || '未知事件';
};

const formatEventTime = (ts) => {
  if (!ts) return '';
  const date = new Date(ts);
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
};

loadRoom();
connectWs();

onBeforeUnmount(() => {
  try {
    ws.value?.close();
  } catch (_) {}
});
</script>

<template>
  <n-layout class="battle-room">
    <!-- 顶部信息栏 -->
    <n-card size="small" style="margin-bottom: 12px">
      <n-space align="center" justify="space-between">
        <n-space align="center">
          <h2 style="margin: 0">⚔️ 对战房间</h2>
          <n-tag v-if="room" :type="room.status === 'running' ? 'success' : room.status === 'finished' ? 'default' : 'warning'">
            {{ room.status === 'waiting' ? '等待中' : room.status === 'running' ? '进行中' : '已结束' }}
          </n-tag>
          <n-tag v-if="room && room.problem" type="info">
            {{ room.problem.title }}
          </n-tag>
        </n-space>
        <n-space>
          <n-space v-if="room && room.status === 'waiting'">
            <n-button v-if="!isParticipant()" type="primary" @click="joinRoom" :loading="joining">加入房间</n-button>
            <n-button v-else type="success" @click="startRoom" :loading="starting">开始对战</n-button>
          </n-space>
          <n-button @click="loadRoom" :loading="loading" size="small">刷新</n-button>
          <n-button @click="leave" size="small">返回</n-button>
        </n-space>
      </n-space>
    </n-card>

    <!-- 主要内容区：左边题目，右边编辑器 -->
    <div class="battle-main" v-if="room && room.status !== 'waiting'">
      <!-- 左侧：题目区域（禁止复制） -->
      <div class="battle-left">
        <n-card size="small" title="📝 题目" class="problem-card">
          <div v-if="problemDetail" class="problem-content">
            <h3>{{ problemDetail.title }}</h3>
            <n-space style="margin-bottom: 12px; color: #666; font-size: 12px;">
              <span>时间限制: {{ problemDetail.time_limit }}ms</span>
              <span>内存限制: {{ problemDetail.memory_limit }}MB</span>
            </n-space>
            <n-divider />
            
            <!-- 题目描述部分：禁止复制 -->
            <div 
              class="problem-section no-select"
              @copy.prevent
              @cut.prevent
              @contextmenu.prevent
            >
              <div v-if="problemDetail.description">
                <strong>题目描述</strong>
                <MdEditor :content="problemDetail.description" previewOnly />
              </div>
              <div v-if="problemDetail.input_description">
                <strong>输入格式</strong>
                <MdEditor :content="problemDetail.input_description" previewOnly />
              </div>
              <div v-if="problemDetail.output_description">
                <strong>输出格式</strong>
                <MdEditor :content="problemDetail.output_description" previewOnly />
              </div>
            </div>
            
            <!-- 样例部分：允许复制 -->
            <div class="problem-section" v-if="problemDetail.samples && problemDetail.samples.length > 0">
              <strong>样例</strong>
              <div v-for="(sample, idx) in problemDetail.samples" :key="idx" class="sample-box">
                <n-grid :cols="2" :x-gap="12">
                  <n-gi>
                    <div class="sample-label">输入 #{{ idx + 1 }}</div>
                    <pre class="sample-content">{{ sample.input }}</pre>
                  </n-gi>
                  <n-gi>
                    <div class="sample-label">输出 #{{ idx + 1 }}</div>
                    <pre class="sample-content">{{ sample.output }}</pre>
                  </n-gi>
                </n-grid>
              </div>
            </div>
            
            <!-- 提示部分：禁止复制 -->
            <div 
              v-if="problemDetail.hint"
              class="problem-section no-select"
              @copy.prevent
              @cut.prevent
              @contextmenu.prevent
            >
              <strong>提示</strong>
              <MdEditor :content="problemDetail.hint" previewOnly />
            </div>
          </div>
          <div v-else style="text-align: center; padding: 40px; color: #999;">
            <n-spin v-if="loadingProblem" />
            <span v-else>题目加载中...</span>
          </div>
        </n-card>
      </div>

      <!-- 右侧：代码编辑器和事件流 -->
      <div class="battle-right">
        <!-- 代码提交区 -->
        <n-card size="small" title="💻 代码编辑器" style="margin-bottom: 12px;">
          <template #header-extra>
            <n-select 
              v-model:value="language" 
              :options="languageOptions"
              style="width: 120px"
              size="small"
              :disabled="room && room.status !== 'running'"
            />
          </template>
          <n-alert v-if="firstAcUserId && room && room.status === 'running'" type="info" style="margin-bottom: 12px">
            {{ firstAcUserId === currentUserId ? '🎉 你已首先AC！等待对方提交或超时' : '⚠️ 对方已首先AC！你仍可提交获得经验和分数' }}
          </n-alert>
          <div class="battle-editor" style="height: 350px; border: 1px solid #e0e0e0; border-radius: 4px; overflow: hidden;">
            <CodeMirrorBattle
              ref="editorRef"
              v-model:code="source"
              :language="language"
              :block-paste="room && room.status === 'running'"
              @paste-blocked="message.warning('对战模式禁止粘贴代码')"
            />
          </div>
          
          <!-- 自测面板 -->
          <n-collapse style="margin-top: 12px;">
            <n-collapse-item title="自测运行" name="test">
              <n-grid :cols="2" :x-gap="12">
                <n-gi>
                  <div style="font-size: 12px; color: #666; margin-bottom: 4px;">自测输入</div>
                  <n-input
                    v-model:value="testInput"
                    type="textarea"
                    placeholder="输入测试数据..."
                    :autosize="{ minRows: 3, maxRows: 5 }"
                    style="font-family: 'Consolas', monospace; font-size: 13px;"
                  />
                </n-gi>
                <n-gi>
                  <div style="font-size: 12px; color: #666; margin-bottom: 4px;">运行结果</div>
                  <n-input
                    v-model:value="testOutput"
                    type="textarea"
                    placeholder="运行结果将显示在这里..."
                    :autosize="{ minRows: 3, maxRows: 5 }"
                    readonly
                    style="font-family: 'Consolas', monospace; font-size: 13px;"
                  />
                </n-gi>
              </n-grid>
              <n-space style="margin-top: 8px;">
                <n-button @click="runTest" :loading="testRunning" type="info" size="small">
                  ▶ 自测运行
                </n-button>
              </n-space>
            </n-collapse-item>
          </n-collapse>
          
          <n-space style="margin-top: 12px" justify="end">
            <n-button 
              type="primary" 
              :loading="submitting" 
              @click="submit"
              :disabled="room && room.status !== 'running'"
            >
              {{ room && room.status !== 'running' ? '本局对战已结束' : '提交代码' }}
            </n-button>
          </n-space>
        </n-card>

        <!-- 事件流 -->
        <n-card size="small" title="📋 事件流">
          <n-scrollbar style="max-height: 200px">
            <n-timeline>
              <n-timeline-item
                v-for="(event, idx) in events"
                :key="idx"
                :type="event.type === 'room_finished' ? 'success' : event.type === 'submission_update' && event.score === 100 ? 'success' : 'info'"
                :title="formatEventMessage(event)"
                :time="formatEventTime(event.ts)"
              />
            </n-timeline>
            <div v-if="events.length === 0" style="color: #999; text-align: center; padding: 20px;">
              暂无事件
            </div>
          </n-scrollbar>
        </n-card>
      </div>
    </div>

    <!-- 等待状态时显示的内容 -->
    <n-card v-else-if="room && room.status === 'waiting'" size="small" style="margin-top: 12px">
      <n-space vertical align="center" style="padding: 40px;">
        <n-spin size="large" />
        <h3>等待对手加入...</h3>
        <p style="color: #666;">房间 ID: {{ roomId }}</p>
        <n-space>
          <n-tag v-for="p in room.participants" :key="p.user.id" type="success">
            {{ p.user.username }}
          </n-tag>
        </n-space>
      </n-space>
    </n-card>
  </n-layout>
</template>

<style scoped>
.battle-room {
  padding: 12px;
  height: calc(100vh - 64px);
  overflow: hidden;
}

.battle-main {
  display: flex;
  gap: 12px;
  height: calc(100% - 80px);
}

.battle-left {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.battle-right {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.problem-card {
  height: 100%;
  overflow: hidden;
}

.problem-card :deep(.n-card__content) {
  height: calc(100% - 50px);
  overflow-y: auto;
}

.problem-content {
  line-height: 1.8;
}

.problem-section {
  margin-bottom: 20px;
}

.problem-section strong {
  display: block;
  margin-bottom: 8px;
  color: #18a058;
  font-size: 15px;
}

.sample-box {
  margin-top: 12px;
  margin-bottom: 12px;
}

.sample-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.sample-content {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  margin: 0;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  white-space: pre-wrap;
  word-break: break-all;
  /* 样例允许复制 */
  -webkit-user-select: text;
  -moz-user-select: text;
  -ms-user-select: text;
  user-select: text;
  cursor: text;
}

.problem-text {
  background: transparent;
  padding: 0;
  margin: 0;
  font-family: inherit;
  font-size: 14px;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.8;
}

/* 禁止复制的样式 */
.no-select {
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

.markdown-body {
  font-size: 14px;
}

.markdown-body :deep(pre) {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
}

.markdown-body :deep(code) {
  font-family: 'Consolas', 'Monaco', monospace;
}
</style>
