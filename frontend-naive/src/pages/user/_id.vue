<script setup>
import { computed, ref, watch } from 'vue';
import Axios from '@/plugins/axios';
import { difficultyColor } from '@/plugins/consts';
import SubmissionTable from '@/components/SubmissionTable.vue';
import { useRoute } from 'vue-router';
import store from '@/store';

const route = useRoute();

const id = ref(route.params.id),
  data = ref({});

const activityLoading = ref(false);
const activity = ref(null);
const activityType = ref('solved');
const activityYear = ref(new Date().getFullYear());

const yearOptions = computed(() => {
  const now = new Date().getFullYear();
  const opts = [];
  for (let y = now; y >= now - 5; y -= 1) {
    opts.push({ label: String(y), value: y });
  }
  return opts;
});

const typeOptions = [
  { label: 'Solved（去重题目数）', value: 'solved' },
  { label: 'Accepted（AC 提交次数）', value: 'accepted' },
];

const fetchActivity = () => {
  activityLoading.value = true;
  Axios.get(`/user/${id.value}/activity/`, {
    params: {
      year: activityYear.value,
      type: activityType.value,
      tz: 'Asia/Shanghai',
    },
  })
    .then(res => {
      activity.value = res;
    })
    .finally(() => {
      activityLoading.value = false;
    });
};

const _pad2 = n => String(n).padStart(2, '0');
const _dateKey = d => `${d.getFullYear()}-${_pad2(d.getMonth() + 1)}-${_pad2(d.getDate())}`;
const _weekdayIndex = d => (d.getDay() + 6) % 7; // Monday=0

const calendarWeeks = computed(() => {
  const year = activityYear.value;
  const start = new Date(year, 0, 1);
  const end = new Date(year, 11, 31);
  const startOffset = _weekdayIndex(start);
  const totalDays = Math.floor((end - start) / 86400000) + 1;
  const weeksCount = Math.ceil((startOffset + totalDays) / 7);

  const max = Object.values(activity.value?.days || {}).reduce((a, b) => Math.max(a, b), 0);
  const levels = count => {
    if (!count) return 0;
    if (!max) return 0;
    const r = count / max;
    if (r <= 0.25) return 1;
    if (r <= 0.5) return 2;
    if (r <= 0.75) return 3;
    return 4;
  };

  const weeks = Array.from({ length: weeksCount }, () => Array.from({ length: 7 }, () => null));
  for (let i = 0; i < totalDays; i += 1) {
    const d = new Date(year, 0, 1 + i);
    const index = startOffset + i;
    const w = Math.floor(index / 7);
    const wd = index % 7;
    const key = _dateKey(d);
    const count = Number(activity.value?.days?.[key] || 0);
    weeks[w][wd] = {
      key,
      date: d,
      count,
      level: levels(count),
    };
  }
  return weeks;
});

const monthLabels = computed(() => {
  const labels = [];
  let lastMonth = null;
  const weeks = calendarWeeks.value;
  for (let w = 0; w < weeks.length; w += 1) {
    const first = weeks[w].find(c => c && c.date);
    if (!first) continue;
    const m = first.date.getMonth();
    if (m !== lastMonth) {
      labels.push({ weekIndex: w, month: m });
      lastMonth = m;
    }
  }
  return labels;
});

const monthName = m => ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'][m];

const refresh = () => {
  Axios.get(`/user/${id.value}/`).then(res => {
    data.value = res;
  });
  fetchActivity();
};

refresh();

watch(
  () => route.params.id,
  newId => {
    id.value = newId;
    refresh();
  }
);

watch([activityYear, activityType], fetchActivity);
</script>

<template>
  <n-layout has-sider>
    <n-layout-sider content-style="padding: 24px; text-align: center">
      <n-space vertical>
        <img
          style="width: 70%; margin: auto; display: block; border-radius: 50%"
          :src="
            data.avatar ||
            'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
          "
        />
        <div style="margin-bottom: 18px">
          <h1 style="margin-bottom: 0">{{ data.username }}</h1>
          <p v-if="data.real_name">{{ data.real_name }}</p>
        </div>
        <n-statistic label="通过题目数">
          {{ data.solved_problems && data.solved_problems.length }}
        </n-statistic>
        <n-statistic label="通过 / 提交次数">
          <template #prefix>
            {{ data.accepted_count }}
          </template>
          /
          <template #suffix>
            {{ data.submission_count }}
          </template>
        </n-statistic>
        <router-link
          :to="{ name: 'user_edit', params: { id } }"
          v-if="store.state.user.permissions.includes('user')"
        >
          <n-button type="primary" style="margin-top: 10px">管理</n-button>
        </router-link>
      </n-space>
    </n-layout-sider>
    <n-layout-content content-style="padding: 24px 35px;">
      <div style="margin-bottom: 30px">
        <n-space justify="space-between" align="center" style="margin-bottom: 10px" wrap>
          <h2 style="margin: 0">刷题记录</h2>
          <n-space align="center" wrap>
            <n-select
              v-model:value="activityType"
              :options="typeOptions"
              style="width: min(92vw, 220px)"
            />
            <n-select
              v-model:value="activityYear"
              :options="yearOptions"
              style="width: 140px"
            />
          </n-space>
        </n-space>

        <n-card :bordered="false" embedded>
          <div v-if="activityLoading" style="padding: 18px 8px">
            <n-skeleton text :repeat="3" />
          </div>
          <div v-else class="heatmap">
            <div class="heatmap-months">
              <div
                v-for="m in monthLabels"
                :key="m.weekIndex"
                class="heatmap-month"
                :style="{ left: `calc(${m.weekIndex} * (var(--cell) + var(--gap)))` }"
              >
                {{ monthName(m.month) }}
              </div>
            </div>
            <div class="heatmap-grid">
              <div v-for="(week, w) in calendarWeeks" :key="w" class="heatmap-week">
                <div v-for="(cell, d) in week" :key="`${w}-${d}`" class="heatmap-day-wrap">
                  <div v-if="!cell" class="heatmap-day empty"></div>
                  <n-popover v-else trigger="hover">
                    <template #trigger>
                      <div :class="['heatmap-day', `lv-${cell.level}`]"></div>
                    </template>
                    <div>{{ cell.key }}</div>
                    <div>
                      {{ cell.count }}
                      {{ activityType === 'accepted' ? '次 AC' : '题' }}
                    </div>
                  </n-popover>
                </div>
              </div>
            </div>

            <div class="heatmap-stats">
              <div class="stat">
                <div class="stat-num">{{ activity?.stats?.all_time ?? 0 }}</div>
                <div class="stat-sub">{{ activityType === 'accepted' ? '次' : '题' }}</div>
                <div class="stat-tip">{{ activityType === 'accepted' ? '累计 AC' : '累计通过' }}</div>
              </div>
              <div class="stat">
                <div class="stat-num">{{ activity?.stats?.last_year ?? 0 }}</div>
                <div class="stat-sub">{{ activityType === 'accepted' ? '次' : '题' }}</div>
                <div class="stat-tip">{{ activityType === 'accepted' ? '近一年 AC' : '近一年通过' }}</div>
              </div>
              <div class="stat">
                <div class="stat-num">{{ activity?.stats?.last_month ?? 0 }}</div>
                <div class="stat-sub">{{ activityType === 'accepted' ? '次' : '题' }}</div>
                <div class="stat-tip">{{ activityType === 'accepted' ? '近一月 AC' : '近一月通过' }}</div>
              </div>
              <div class="stat">
                <div class="stat-num">{{ activity?.stats?.streak_max ?? 0 }}</div>
                <div class="stat-sub">天</div>
                <div class="stat-tip">最长连续天数</div>
              </div>
              <div class="stat">
                <div class="stat-num">{{ activity?.stats?.streak_last_year_max ?? 0 }}</div>
                <div class="stat-sub">天</div>
                <div class="stat-tip">近一年最长连续</div>
              </div>
              <div class="stat">
                <div class="stat-num">{{ activity?.stats?.streak_last_month_max ?? 0 }}</div>
                <div class="stat-sub">天</div>
                <div class="stat-tip">近一月最长连续</div>
              </div>
            </div>
          </div>
        </n-card>
      </div>

      <div style="margin-bottom: 30px">
        <h2>通过的题目</h2>
        <n-space size="small">
          <n-popover
            trigger="hover"
            v-for="item in data.solved_problems"
            :key="item.problem.id"
          >
            <template #trigger>
              <router-link
                :to="{
                  name: 'problem_detail',
                  params: { id: item.problem.id },
                }"
              >
                <n-button :color="difficultyColor[item.problem.difficulty]">
                  #{{ item.problem.id }} | {{ item.problem.title }}
                </n-button>
              </router-link>
            </template>
            通过时间：<n-time :time="Number(new Date(item.create_time))" />
          </n-popover>
        </n-space>
      </div>
      <div>
        <h2>最近的提交</h2>
        <SubmissionTable :data="data.submissions" @refresh="refresh" />
      </div>
    </n-layout-content>
  </n-layout>
</template>

<style lang="scss" scoped>
a {
  text-decoration: none;
}

.heatmap {
  --cell: 11px;
  --gap: 3px;
}

.heatmap-grid {
  display: flex;
  gap: var(--gap);
  padding-top: 18px;
  overflow-x: auto;
  padding-bottom: 6px;
}

.heatmap-week {
  display: flex;
  flex-direction: column;
  gap: var(--gap);
}

.heatmap-day {
  width: var(--cell);
  height: var(--cell);
  border-radius: 2px;
  background: #ebedf0;
}

.heatmap-day.empty {
  background: transparent;
}

.heatmap-day.lv-0 {
  background: #ebedf0;
}

.heatmap-day.lv-1 {
  background: #9be9a8;
}

.heatmap-day.lv-2 {
  background: #40c463;
}

.heatmap-day.lv-3 {
  background: #30a14e;
}

.heatmap-day.lv-4 {
  background: #216e39;
}

.heatmap-months {
  position: relative;
  height: 16px;
}

.heatmap-month {
  position: absolute;
  font-size: 12px;
  color: #666;
}

.heatmap-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(120px, 1fr));
  gap: 18px;
  margin-top: 18px;
}

.stat-num {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.1;
}

.stat-sub {
  font-size: 12px;
  color: #666;
  margin-top: 2px;
}

.stat-tip {
  font-size: 12px;
  color: #999;
}

@media (max-width: 900px) {
  .heatmap-stats {
    grid-template-columns: repeat(2, minmax(120px, 1fr));
  }
}
</style>
