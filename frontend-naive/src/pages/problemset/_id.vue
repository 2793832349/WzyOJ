<script setup>
import { computed, ref } from 'vue';
import Axios from '@/plugins/axios';

import router from '@/router';
import store from '@/store';
import { useRoute } from 'vue-router';
import MdEditor from '@/components/MdEditor.vue';
import ProblemTable from '@/components/ProblemTable.vue';
import RankingTable from '@/components/RankingTable.vue';

const route = useRoute(),
  message = useMessage();
const id = route.params.id,
  contestData = ref({ problems: [] }),
  mode = ref('题单');

const rankingData = ref({}),
  loadingRanking = ref(false);
const getRankingData = (force_update = false) => {
  loadingRanking.value = true;
  Axios.get(`/contest/${id}/ranking/`, {
    params: { force_update },
  })
    .then(res => {
      rankingData.value = res;
    })
    .finally(() => {
      loadingRanking.value = false;
    });
};

const challengeLevels = computed(() => {
  const problems = Array.isArray(contestData.value?.problems) ? contestData.value.problems : [];
  let lockFollowing = false;

  return problems.map((problem, index) => {
    const solved = Boolean(problem?.solved);
    const unlocked = index === 0 || !lockFollowing;

    if (!solved) {
      lockFollowing = true;
    }

    return {
      ...problem,
      level: index + 1,
      solved,
      unlocked,
      state: solved ? 'passed' : (unlocked ? 'current' : 'locked'),
    };
  });
});

const challengeSolvedCount = computed(() => challengeLevels.value.filter(item => item.solved).length);

const challengeTotalCount = computed(() => challengeLevels.value.length);

const challengeProgress = computed(() => {
  const total = challengeTotalCount.value;
  if (!total) return 0;
  return Number(((challengeSolvedCount.value * 100) / total).toFixed(1));
});

const nextChallengeProblem = computed(() => {
  return challengeLevels.value.find(item => item.unlocked && !item.solved) || null;
});

const challengeActionLabel = computed(() => {
  if (!challengeTotalCount.value) return '暂无关卡';
  if (!nextChallengeProblem.value) return '已全部通关';
  return `继续第 ${nextChallengeProblem.value.level} 关`;
});

const openProblem = (problem) => {
  if (!problem || !problem.id) return;
  router.push({
    name: 'problem_detail',
    params: { id: problem.id },
  });
};

const loadData = () => {
  Axios.get(`/contest/${id}/`).then(res => {
    res.start_time = res.start_time ? Number(new Date(res.start_time)) : null;
    res.end_time = res.end_time ? Number(new Date(res.end_time)) : null;
    contestData.value = res;

    // 题单模式：直接加载排行榜
    if (res.problem_list_mode) {
      if (res.joined || store.state.user.permissions.includes('contest')) {
        getRankingData();
      }
    }
    // 比赛模式：按时间加载排行榜
    else if (res.start_time <= Date.now()) {
      getRankingData();
    } else {
      setTimeout(getRankingData, res.start_time - Date.now());
    }

    mode.value = res.problem_list_mode ? '题单' : '比赛';
  });
};

loadData();

const beforeLeave = tabName => {
  if (tabName === 'discussion') {
    router.push({
      name: 'discussion_list',
      query: { related_contest__id: id },
    });
    return false;
  } else if (tabName === 'edit') {
    router.push({
      name: 'problemset_edit',
      params: { id },
    });
    return false;
  }
  return true;
};

const signUp = () => {
  Axios.post(`/contest/${id}/sign_up/`).then(() => {
    message.success('报名成功');
    loadData();
  });
};
</script>

<template>
  <div>
    <h1>#{{ contestData.id }}&ensp;{{ contestData.title }}</h1>
  </div>
  <n-layout has-sider>
    <n-layout-content>
      <n-tabs
        type="line"
        size="large"
        :tabs-padding="20"
        @before-leave="beforeLeave"
      >
        <template #suffix>
          <div style="font-size: medium" v-if="!contestData.problem_list_mode">
            <span
              v-if="
                contestData.start_time && contestData.start_time > Date.now()
              "
            >
              距离比赛开始还有：<n-countdown
                :duration="contestData.start_time - Date.now()"
              />
            </span>
            <span
              v-else-if="
                contestData.end_time && contestData.end_time > Date.now()
              "
            >
              距离比赛结束还有：<n-countdown
                :duration="contestData.end_time - Date.now()"
              />
            </span>
          </div>
        </template>
        <n-tab-pane name="description" :tab="mode + '信息'">
          <n-space vertical size="large">
            <div></div>

            <div v-if="contestData.joined || contestData.allow_sign_up">
              <h2>操作</h2>
              <n-button
                type="primary"
                @click="signUp"
                :disabled="
                  contestData.joined ||
                  (!contestData.problem_list_mode &&
                    contestData.end_time &&
                    Date.now() > contestData.end_time)
                "
              >
                {{ contestData.joined ? '已加入' : '报名' }}
              </n-button>
            </div>

            <div v-if="!contestData.problem_list_mode">
              <h2>比赛时间</h2>
              <span
                style="font-size: medium"
                v-if="contestData.start_time || contestData.end_time"
              >
                <n-time
                  :time="contestData.start_time"
                  format="yyyy-MM-dd HH:mm:ss"
                  style="margin-right: 5px"
                />
                ~
                <n-time
                  :time="contestData.end_time"
                  format="yyyy-MM-dd HH:mm:ss"
                  style="margin-left: 5px"
                />
              </span>
            </div>

            <div v-if="contestData.description">
              <h2>{{ mode }}描述</h2>
              <n-card class="description">
                <MdEditor
                  :content="contestData.description"
                  :previewOnly="true"
                />
              </n-card>
            </div>
          </n-space>
        </n-tab-pane>
        <n-tab-pane
          name="problem"
          tab="题目列表"
          :disabled="!contestData.problems.length"
        >
          <ProblemTable :data="contestData.problems" />
        </n-tab-pane>

        <n-tab-pane
          name="challenge"
          tab="闯关模式"
          :disabled="!contestData.problem_list_mode || !contestData.problems.length"
        >
          <n-space vertical size="large" class="challenge-mode">
            <n-card class="challenge-summary" :bordered="false">
              <div class="challenge-summary__head">
                <div>
                  <h2>题单闯关进度</h2>
                  <p>按顺序解锁：上一关通过（AC）后自动解锁下一关。</p>
                </div>
                <n-button
                  type="primary"
                  :disabled="!nextChallengeProblem"
                  @click="openProblem(nextChallengeProblem)"
                >
                  {{ challengeActionLabel }}
                </n-button>
              </div>

              <div class="challenge-summary__meta">
                <span>已通关 {{ challengeSolvedCount }}/{{ challengeTotalCount }}</span>
                <span>进度 {{ challengeProgress }}%</span>
              </div>
              <n-progress
                type="line"
                :show-indicator="false"
                :percentage="challengeProgress"
              />
            </n-card>

            <div class="challenge-grid">
              <n-card
                v-for="item in challengeLevels"
                :key="item.id"
                size="small"
                class="challenge-level"
                :class="[`state-${item.state}`]"
                :bordered="false"
              >
                <div class="challenge-level__head">
                  <span class="level-index">第 {{ item.level }} 关</span>
                  <n-tag v-if="item.state === 'passed'" type="success" size="small" :bordered="false">已通关</n-tag>
                  <n-tag v-else-if="item.state === 'current'" type="info" size="small" :bordered="false">进行中</n-tag>
                  <n-tag v-else type="default" size="small" :bordered="false">未解锁</n-tag>
                </div>

                <div class="challenge-level__title">{{ item.title }}</div>
                <div class="challenge-level__id">题目 #{{ item.id }}</div>

                <n-button
                  block
                  :type="item.state === 'passed' ? 'success' : 'primary'"
                  :secondary="item.state !== 'passed'"
                  :disabled="item.state === 'locked'"
                  @click="openProblem(item)"
                >
                  {{ item.state === 'passed' ? '再次挑战' : (item.state === 'current' ? '开始闯关' : '等待解锁') }}
                </n-button>
              </n-card>
            </div>
          </n-space>
        </n-tab-pane>

        <n-tab-pane
          name="ranking"
          tab="排行榜"
        >
          <p style="font-size: medium">
            <span v-if="contestData.problem_list_mode">
              说明：题单排行榜统计所有用户通过（AC）的题目数量。上次更新时间：<n-time
                :time="Number(new Date(rankingData.time))"
              />。
            </span>
            <span v-else-if="
              contestData.start_time <= Date.now() &&
              Date.now() <= contestData.end_time
            ">
              说明：比赛排行榜仅统计比赛持续时间中的提交，每分钟更新一次。上次更新时间：<n-time
                :time="Number(new Date(rankingData.time))"
              />。
            </span>
            <n-alert
              v-if="rankingData.is_frozen && !store.state.user.permissions.includes('contest')"
              type="warning"
              style="margin: 10px 0"
            >
              ⏸️ 排行榜已封榜，当前显示的是封榜时刻的排名，实际排名可能已发生变化
            </n-alert>
            <n-popover v-if="store.state.user.permissions.includes('contest')">
              <template #trigger>
                <n-button
                  @click="getRankingData(true)"
                  :disabled="loadingRanking"
                >
                  强制更新
                </n-button>
              </template>
              仅管理员可用，将会立即刷新排行榜缓存，该缓存对所有用户生效。
            </n-popover>
          </p>
          <RankingTable
            :data="rankingData"
            :loading="loadingRanking"
            :isProblemSet="contestData.problem_list_mode"
            style="margin-top: 15px"
          />
        </n-tab-pane>
        <n-tab-pane
          name="discussion"
          tab="讨论"
          :disabled="
            contestData.start_time <= Date.now() &&
            Date.now() <= contestData.end_time
          "
        />
        <n-tab-pane
          name="edit"
          :tab="'修改' + mode"
          v-if="store.state.user.permissions.includes('contest')"
        />
      </n-tabs>
    </n-layout-content>
  </n-layout>
</template>

<style lang="scss" scoped>
.n-layout-content,
.n-layout-sider {
  margin: 20px !important;
}

.description :deep(.n-card__content) {
  padding: 0 20px !important;
  margin: 0 10px !important;
}

.challenge-mode {
  margin-top: 12px;
}

.challenge-summary {
  border: 1px solid #d6e5ff;
  background: linear-gradient(135deg, #f5f9ff 0%, #eef6ff 100%);
}

.challenge-summary__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.challenge-summary__head h2 {
  margin: 0;
  font-size: 20px;
  color: #1f3f72;
}

.challenge-summary__head p {
  margin: 8px 0 0;
  color: #60708a;
  font-size: 14px;
}

.challenge-summary__meta {
  margin: 14px 0 10px;
  display: flex;
  justify-content: space-between;
  color: #2b4d80;
  font-weight: 600;
}

.challenge-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
}

.challenge-level {
  border: 1px solid #e2e8f5;
  transition: all 0.2s ease;
}

.challenge-level:hover {
  transform: translateY(-2px);
}

.challenge-level.state-passed {
  border-color: #bde8cc;
  background: linear-gradient(180deg, #f3fcf6 0%, #ffffff 100%);
}

.challenge-level.state-current {
  border-color: #b8d6ff;
  background: linear-gradient(180deg, #f4f9ff 0%, #ffffff 100%);
}

.challenge-level.state-locked {
  border-color: #e9edf5;
  background: #f8fafc;
}

.challenge-level__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.level-index {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  background: #e8eef9;
  color: #3c4f70;
  font-size: 12px;
  font-weight: 700;
}

.challenge-level__title {
  min-height: 44px;
  font-size: 15px;
  color: #1d2f48;
  font-weight: 700;
  line-height: 1.45;
  margin-bottom: 8px;
}

.challenge-level__id {
  color: #6d7f98;
  font-size: 13px;
  margin-bottom: 12px;
}

@media (max-width: 768px) {
  .challenge-summary__head {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
