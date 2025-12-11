�6<script setup>
import { ref } from 'vue';
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
  mode = ref('比赛');

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

const loadData = () => {
  Axios.get(`/contest/${id}/`).then(res => {
    res.start_time = (res.start_time && Number(new Date(res.start_time))) || 0;
    res.end_time = (res.end_time && Number(new Date(res.end_time))) || 0;
    contestData.value = res;
    if (!res.problem_list_mode && res.start_time <= Date.now())
      getRankingData();
    else setTimeout(getRankingData, res.start_time - Date.now());
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
      name: 'contest_edit',
      params: { id },
    });
    return false;
  }
  return true;
};

const signUp = () => {
  Axios.post(`/contest/${id}/sign_up/`).then(res => {
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
            <!-- <span v-else>比赛已结束</span> -->
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
                  contestData.joined || Date.now() > contestData.end_time
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
          name="ranking"
          tab="排行榜"
          v-if="!contestData.problem_list_mode"
        >
          <p
            style="font-size: medium"
            v-if="
              contestData.start_time <= Date.now() &&
              Date.now() <= contestData.end_time
            "
          >
            说明：比赛排行榜仅统计比赛持续时间中的提交，每分钟更新一次。上次更新时间：<n-time
              :time="Number(new Date(rankingData.time))"
            />。
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
          <n-popover
            v-else-if="store.state.user.permissions.includes('contest')"
          >
            <template #trigger>
              <n-button
                @click="getRankingData(true)"
                :disabled="loadingRanking"
                style="margin-left: 1px"
              >
                强制更新
              </n-button>
            </template>
            仅管理员可用，将会立即刷新排行榜缓存，该缓存对所有用户生效。
          </n-popover>
          <RankingTable
            :data="rankingData"
            :loading="loadingRanking"
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
</style>
�6"(205b1bab434999c48e066e66385ba65f03f104f425file:///root/frontend-naive/src/pages/contest/_id.vue:file:///root/frontend-naive