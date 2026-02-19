<script setup>
import { ref, onMounted, computed, reactive, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useMessage } from 'naive-ui';
import Axios from '@/plugins/axios';
import MdEditor from '@/components/MdEditor.vue';
import CodeWithCard from '@/components/CodeWithCard.vue';
import Captcha from '@/components/captcha.vue';
import store from '@/store';
import { languageOptions } from '@/plugins/consts';

const route = useRoute();
const router = useRouter();
const message = useMessage();
const sectionId = computed(() => route.params.id);

const section = ref(null);
const loading = ref(false);
const isCompleted = ref(false);
const completing = ref(false);

const submitStateMap = reactive({});
const captchaRefs = {};

const getSubmitState = (problemId) => {
  const key = String(problemId);
  if (!submitStateMap[key]) {
    submitStateMap[key] = {
      source: '',
      language: store.getters.defaultSubmitLanguage,
      _is_hidden: false,
      captcha: '',
      submiting: false,
    };
  }
  return submitStateMap[key];
};

const setCaptchaRef = (problemId, el) => {
  if (!problemId && problemId !== 0) return;
  if (!el) return;
  captchaRefs[String(problemId)] = el;
};

const problemDetailMap = reactive({});

const getProblemDetailState = (problemId) => {
  const key = String(problemId);
  if (!problemDetailMap[key]) {
    problemDetailMap[key] = {
      loading: false,
      error: false,
      data: null,
    };
  }
  return problemDetailMap[key];
};

const loadProblemDetail = async (problemId) => {
  if (!problemId && problemId !== 0) return;
  const state = getProblemDetailState(problemId);
  if (state.loading || state.data) return;

  state.loading = true;
  state.error = false;
  try {
    state.data = await Axios.get(`/problem/${problemId}/`);
  } catch (err) {
    console.error('Failed to load problem detail:', err);
    state.error = true;
  } finally {
    state.loading = false;
  }
};

const parseProblemIdFromPanelName = (name, prefix = '') => {
  if (typeof name === 'number') return name;
  if (typeof name !== 'string') return null;

  const raw = prefix && name.startsWith(prefix)
    ? name.slice(prefix.length)
    : name;
  const pid = Number(raw);
  return Number.isFinite(pid) ? pid : null;
};

const onProblemPanelHeaderClick = ({ name }) => {
  const pid = parseProblemIdFromPanelName(name);
  if (!pid && pid !== 0) return;
  loadProblemDetail(pid);
};

const onProblemEditorialPanelHeaderClick = (payload = {}) => {
  const pid = parseProblemIdFromPanelName(payload?.name, 'editorial-');
  if (!pid && pid !== 0) return;
  loadProblemDetail(pid);
  onProblemEditorialHeaderClick(pid, payload);
};

const getProblemBrief = (problemId) => {
  const ps = section.value?.problems;
  if (!Array.isArray(ps)) return null;
  return ps.find((p) => p && p.id === problemId) ?? null;
};

const getProblemTitle = (problemId) => {
  const brief = getProblemBrief(problemId);
  if (brief?.title) return brief.title;
  const detail = getProblemDetailState(problemId).data;
  if (detail?.title) return detail.title;
  return '';
};

const normalizeCodeText = (val) => {
  if (val === null || val === undefined) return '';
  return val.toString().replace(/\r\n/g, '\n').trimEnd();
};

const copyText = (text) => {
  const input = document.createElement('textarea');
  input.value = (text ?? '').toString();
  document.body.appendChild(input);
  input.select();
  document.execCommand('copy');
  document.body.removeChild(input);
  message.success('复制成功');
};

const getValidSamples = (pd) => {
  if (!pd || typeof pd !== 'object') return [];
  const samples = Array.isArray(pd.samples) ? pd.samples : [];
  return samples
    .filter((item) => item && (item.input || item.output))
    .map((item, i) => ({
      index: item.index || i + 1,
      input: normalizeCodeText(item.input),
      output: normalizeCodeText(item.output),
      explanation: normalizeCodeText(
        item.explain ?? item.explanation ?? item.analysis ?? ''
      ).trim(),
    }))
    .filter((item) => item.input.trim() || item.output.trim() || item.explanation);
};

const generateProblemMarkdown = (pd) => {
  if (!pd || typeof pd !== 'object') return '';

  const rawBackground = (pd.background ?? '').toString().trim();
  const rawDescription = (pd.description ?? '').toString().trim();
  const rawInputFormat = (pd.input_format ?? '').toString().trim();
  const rawOutputFormat = (pd.output_format ?? '').toString().trim();
  const rawHint = (pd.hint ?? '').toString().trim();

  let md = '';

  if (rawBackground) md += `## 题目背景\n\n${rawBackground}\n\n`;
  if (rawDescription) md += `## 题目描述\n\n${rawDescription}\n\n`;
  if (rawInputFormat) md += `## 输入格式\n\n${rawInputFormat}\n\n`;
  if (rawOutputFormat) md += `## 输出格式\n\n${rawOutputFormat}\n\n`;
  if (rawHint) md += `## 数据范围\n\n${rawHint}\n`;

  return md.trimEnd() + '\n';
};

const getProblemEditorialMarkdown = (pd) => {
  if (!pd || typeof pd !== 'object') return '';
  return (pd.editorial?.content ?? '').toString().trim();
};

const problemEditorialExpandedMap = reactive({});

const isProblemEditorialExpanded = (problemId) => {
  return !!problemEditorialExpandedMap[String(problemId)];
};

const onProblemEditorialHeaderClick = (problemId, payload = {}) => {
  const key = String(problemId);
  if (typeof payload?.expanded === 'boolean') {
    problemEditorialExpandedMap[key] = payload.expanded;
    return;
  }
  problemEditorialExpandedMap[key] = !problemEditorialExpandedMap[key];
};

const parseContentToBlocks = (rawContent) => {
  const content = (rawContent ?? '').toString();
  const regex = /\[\[\s*(problem|video)\s*:\s*([^\]]+?)\s*\]\]/gi;
  const blocks = [];
  const embeddedProblemIds = [];

  let lastIndex = 0;
  let match;
  while ((match = regex.exec(content)) !== null) {
    const before = content.slice(lastIndex, match.index);
    if (before.trim()) blocks.push({ type: 'md', content: before });

    const kind = (match[1] ?? '').toString().toLowerCase();
    const rawVal = (match[2] ?? '').toString().trim();
    if (kind === 'problem') {
      const pid = Number(rawVal);
      if (!Number.isNaN(pid)) {
        embeddedProblemIds.push(pid);
        blocks.push({ type: 'problem', id: pid });
      }
    } else if (kind === 'video') {
      if (rawVal) blocks.push({ type: 'video', url: rawVal });
    }

    lastIndex = match.index + match[0].length;
  }

  const after = content.slice(lastIndex);
  if (after.trim()) blocks.push({ type: 'md', content: after });

  return { blocks, embeddedProblemIds };
};

const contentBlocks = computed(() => {
  const sec = section.value;
  if (!sec) return [];

  const content = (sec.content ?? '').toString();
  const assocIds = Array.isArray(sec.problems)
    ? sec.problems
        .map((p) => p?.id)
        .filter((id) => id || id === 0)
    : [];

  const { blocks, embeddedProblemIds } = parseContentToBlocks(content);
  const hasPlaceholder = blocks.some((b) => b.type !== 'md');

  const embeddedSet = new Set(embeddedProblemIds.map((id) => String(id)));
  const extraIds = assocIds.filter((id) => !embeddedSet.has(String(id)));

  let result = [];
  if (!hasPlaceholder) {
    if (content.trim()) result.push({ type: 'md', content });
    assocIds.forEach((id) => result.push({ type: 'problem', id }));
  } else {
    result = blocks.slice();
    extraIds.forEach((id) => result.push({ type: 'problem', id }));
  }

  return result.map((b, idx) => ({
    ...b,
    _key: `${b.type}-${b.type === 'problem' ? b.id : b.type === 'video' ? b.url : 'md'}-${idx}`,
  }));
});

const loadSection = async () => {
  loading.value = true;
  try {
    section.value = await Axios.get(`/book/sections/${sectionId.value}/`);
    if (Array.isArray(section.value?.problems)) {
      section.value.problems.forEach((p) => {
        if (!p?.id && p?.id !== 0) return;
        getSubmitState(p.id);
      });
    }
    // 记录阅读
    await Axios.post(`/book/sections/${sectionId.value}/record_read/`);
  } catch (err) {
    console.error('Failed to load section:', err);
    if (route.name !== 'book_section') return;
    message.error('加载内容失败');
  } finally {
    loading.value = false;
  }
};

const submitProblem = async (problemId) => {
  const state = getSubmitState(problemId);
  const code = (state.source ?? '').toString();
  if (!code.trim()) {
    message.warning('代码不能为空');
    return;
  }
  const captchaRef = captchaRefs[String(problemId)];
  if (captchaRef?.checkCaptcha) {
    const ok = await captchaRef.checkCaptcha();
    if (!ok) return;
  }

  state.submiting = true;
  Axios.post('/submission/', {
    problem_id: problemId,
    source: code,
    language: state.language,
    _is_hidden: state._is_hidden,
    captcha: state.captcha,
  })
    .then((res) => {
      if (!res?.id) {
        message.error('提交返回异常，请稍后重试');
        return;
      }
      store.commit('setSubmitLanguage', state.language);
      router.push(`/submission/${res.id}/`);
    })
    .finally(() => {
      state.submiting = false;
    });
};

const toggleComplete = async () => {
  completing.value = true;
  try {
    if (isCompleted.value) {
      await Axios.post(`/book/sections/${sectionId.value}/uncomplete/`);
      isCompleted.value = false;
      message.success('已取消完成标记');
    } else {
      await Axios.post(`/book/sections/${sectionId.value}/complete/`);
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

watch(sectionId, (newId) => {
  if (route.name !== 'book_section') return;
  if (!newId) return;
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
            <div class="section-content" v-if="contentBlocks.length">
              <div v-for="block in contentBlocks" :key="block._key" class="section-block">
                <MdEditor v-if="block.type === 'md'" :content="block.content" previewOnly />

                <div v-else-if="block.type === 'video'" class="video-inline">
                  <n-card size="small" title="🎬 视频">
                    <video
                      :src="block.url"
                      controls
                      playsinline
                      style="width: 100%; max-height: 70vh"
                    ></video>
                  </n-card>
                </div>

                <div v-else-if="block.type === 'problem'" class="problem-inline">
                  <div class="problem-card">
                    <n-collapse
                      display-directive="show"
                      @item-header-click="onProblemPanelHeaderClick"
                    >
                      <n-collapse-item :name="block.id">
                        <template #header>
                          <div class="problem-header">
                            <div class="problem-header-left">
                              <span class="problem-header-icon">
                                <svg
                                  xmlns="http://www.w3.org/2000/svg"
                                  viewBox="0 0 24 24"
                                  fill="currentColor"
                                >
                                  <path
                                    d="M6 4.5C6 3.67157 6.67157 3 7.5 3H20V19H7.5C6.67157 19 6 19.6716 6 20.5V4.5Z"
                                  />
                                  <path
                                    d="M4 20.5C4 18.567 5.567 17 7.5 17H20V21H7.5C6.67157 21 6 20.3284 6 19.5V18.5C6 19.3284 5.32843 20 4.5 20H4V20.5Z"
                                  />
                                </svg>
                              </span>
                              <span class="problem-header-badge">题目</span>
                              <span class="problem-header-title">
                                #{{ block.id }} {{ getProblemTitle(block.id) }}
                              </span>
                            </div>
                            <div class="problem-header-right">
                              <span class="problem-header-tip">点击展开</span>
                              <n-button
                                size="tiny"
                                text
                                @click.stop="goToProblem(block.id)"
                              >
                                打开题目
                              </n-button>
                            </div>
                          </div>
                        </template>

                        <n-space vertical size="large">
                          <n-spin :show="getProblemDetailState(block.id).loading">
                            <div v-if="getProblemDetailState(block.id).data">
                              <MdEditor
                                :content="generateProblemMarkdown(getProblemDetailState(block.id).data)"
                                previewOnly
                              />

                              <div
                                v-if="getValidSamples(getProblemDetailState(block.id).data).length"
                                class="problem-samples"
                              >
                                <div class="problem-samples-title">样例</div>
                                <div
                                  v-for="sample in getValidSamples(getProblemDetailState(block.id).data)"
                                  :key="sample.index"
                                  class="problem-sample"
                                >
                                  <n-row :gutter="12">
                                    <n-col :span="11">
                                      <div class="sample-title">
                                        <span>样例输入 #{{ sample.index }}</span>
                                        <n-button
                                          size="tiny"
                                          text
                                          @click="() => copyText(sample.input)"
                                        >
                                          复制
                                        </n-button>
                                      </div>
                                      <CodeWithCard :code="sample.input" />
                                    </n-col>
                                    <n-col :span="2"></n-col>
                                    <n-col :span="11">
                                      <div class="sample-title">
                                        <span>样例输出 #{{ sample.index }}</span>
                                        <n-button
                                          size="tiny"
                                          text
                                          @click="() => copyText(sample.output)"
                                        >
                                          复制
                                        </n-button>
                                      </div>
                                      <CodeWithCard :code="sample.output" />
                                    </n-col>
                                  </n-row>

                                  <div
                                    v-if="sample.explanation"
                                    class="sample-explanation"
                                  >
                                    <div class="sample-explanation-title">
                                      解释#{{ sample.index }}
                                    </div>
                                    <MdEditor :content="sample.explanation" previewOnly />
                                  </div>
                                </div>
                              </div>
                            </div>
                            <n-empty
                              v-else-if="getProblemDetailState(block.id).error"
                              description="题目加载失败"
                            />
                            <n-empty v-else description="点击展开加载题目内容" />
                          </n-spin>

                          <n-input
                            v-model:value="getSubmitState(block.id).source"
                            type="textarea"
                            placeholder="在此粘贴代码后提交"
                            :autosize="{ minRows: 6, maxRows: 18 }"
                          />

                          <n-space justify="space-between" align="center">
                            <n-space align="center">
                              <n-select
                                v-model:value="getSubmitState(block.id).language"
                                :options="languageOptions"
                                style="width: 180px"
                              />
                              <n-switch v-model:value="getSubmitState(block.id)._is_hidden" />
                              <span style="color: #666">隐藏</span>
                            </n-space>
                            <n-button
                              type="primary"
                              :loading="getSubmitState(block.id).submiting"
                              :disabled="getSubmitState(block.id).submiting"
                              @click="submitProblem(block.id)"
                            >
                              提交
                            </n-button>
                          </n-space>

                          <Captcha
                            scene="submission"
                            v-model:captcha="getSubmitState(block.id).captcha"
                            :ref="(el) => setCaptchaRef(block.id, el)"
                          />
                        </n-space>
                      </n-collapse-item>
                    </n-collapse>
                  </div>

                  <div class="problem-editorial-inline">
                    <div class="problem-editorial">
                      <n-collapse
                        display-directive="show"
                        @item-header-click="onProblemEditorialPanelHeaderClick"
                      >
                        <n-collapse-item :name="`editorial-${block.id}`">
                          <template #header>
                            <div class="editorial-header">
                              <div class="editorial-header-left">
                                <span class="editorial-header-icon">✏️</span>
                                <span class="editorial-header-title">题解</span>
                              </div>
                              <div class="editorial-header-right">
                                <span class="editorial-header-tip">
                                  {{ isProblemEditorialExpanded(block.id) ? '点击收起' : '点击展开' }}
                                </span>
                              </div>
                            </div>
                          </template>

                          <n-spin :show="getProblemDetailState(block.id).loading">
                            <div
                              class="editorial-content"
                              v-if="getProblemEditorialMarkdown(getProblemDetailState(block.id).data)"
                            >
                              <MdEditor
                                :content="getProblemEditorialMarkdown(getProblemDetailState(block.id).data)"
                                previewOnly
                              />
                            </div>
                            <n-empty
                              v-else-if="getProblemDetailState(block.id).error"
                              description="题解加载失败"
                            />
                            <n-empty v-else description="暂无题解" />
                          </n-spin>
                        </n-collapse-item>
                      </n-collapse>
                    </div>
                  </div>
                </div>
              </div>
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

.video-inline {
  margin: 16px 0;
}

.video-inline video {
  background: #000;
  border-radius: 8px;
  display: block;
}

.section-content {
  line-height: 1.8;
  font-size: 16px;
}

.section-block {
  margin-bottom: 20px;
}

.section-block:last-child {
  margin-bottom: 0;
}

.problem-inline {
  margin: 16px 0;
}

.problem-card {
  border: 1px solid #dbeafe;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
  box-shadow: 0 6px 18px rgba(59, 130, 246, 0.08);
}

.problem-card :deep(.n-collapse) {
  border: none;
}

.problem-card :deep(.n-collapse-item) {
  border-top: none;
}

.problem-card :deep(.n-collapse-item__header) {
  padding: 0;
  background: linear-gradient(
    90deg,
    rgba(219, 234, 254, 0.9) 0%,
    rgba(224, 242, 254, 0.9) 45%,
    rgba(239, 246, 255, 0.9) 100%
  );
}

.problem-card :deep(.n-collapse-item__header-main) {
  width: 100%;
}

.problem-card :deep(.n-collapse-item__content-inner) {
  padding: 16px 18px 18px;
}

.problem-header {
  width: 100%;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  background: transparent;
}

.problem-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.problem-header-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.75);
  color: #2563eb;
  box-shadow: 0 4px 10px rgba(37, 99, 235, 0.12);
}

.problem-header-icon svg {
  width: 18px;
  height: 18px;
}

.problem-header-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.12);
  color: #1d4ed8;
  font-weight: 600;
  flex-shrink: 0;
}

.problem-header-title {
  font-weight: 700;
  color: #1f2937;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.problem-header-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.problem-header-tip {
  font-size: 12px;
  color: #64748b;
  display: inline-flex;
  align-items: center;
}

.problem-header-tip::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #3b82f6;
  display: inline-block;
  margin-right: 6px;
}

.problem-samples-title {
  font-weight: 600;
  font-size: 18px;
  margin: 8px 0 12px 0;
}

.problem-sample {
  margin-bottom: 18px;
}

.problem-sample:last-child {
  margin-bottom: 0;
}

.sample-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
  margin-bottom: 8px;
}

.sample-explanation {
  margin-top: 12px;
}

.sample-explanation-title {
  font-weight: 600;
  margin: 0 0 8px 0;
}


.problem-editorial-inline {
  margin-top: 14px;
}

.problem-editorial {
  border: 1px solid #cfe8cf;
  border-radius: 12px;
  overflow: hidden;
  background: #f7fbf7;
}

.problem-editorial :deep(.n-collapse) {
  border: none;
}

.problem-editorial :deep(.n-collapse-item) {
  border-top: none;
}

.problem-editorial :deep(.n-collapse-item__header) {
  padding: 0;
  background: linear-gradient(90deg, #ecf8ec 0%, #e5f4e5 100%);
}

.problem-editorial :deep(.n-collapse-item__header-main) {
  width: 100%;
}

.problem-editorial :deep(.n-collapse-item__content-inner) {
  padding: 14px;
  border-top: 1px solid #d8ecd8;
}

.editorial-header {
  width: 100%;
  padding: 12px 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  background: transparent;
}

.editorial-header-left {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.editorial-header-icon {
  font-size: 18px;
  line-height: 1;
}

.editorial-header-title {
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
}

.editorial-header-right {
  display: inline-flex;
  align-items: center;
}

.editorial-header-tip {
  color: #2f855a;
  font-size: 14px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
}

.editorial-header-tip::before {
  content: '';
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #48bb78;
  box-shadow: 0 0 0 6px rgba(72, 187, 120, 0.2);
  margin-right: 10px;
}

.editorial-content {
  background: #f6fbf6;
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
