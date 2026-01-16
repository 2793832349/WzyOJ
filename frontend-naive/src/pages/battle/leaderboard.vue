<template>
  <div class="leaderboard-container">
    <n-space vertical size="large">
      <n-card>
        <n-space justify="space-between" align="center">
          <h1 style="margin: 0">🏆 对战排行榜</h1>
          <n-space>
            <n-button type="primary" @click="showTab = '1v1'">1v1对战</n-button>
            <n-button @click="showTab = 'history'">对战历史</n-button>
            <n-button @click="showTab = 'rules'">说明</n-button>
          </n-space>
        </n-space>
      </n-card>

      <n-card v-if="showTab === '1v1'">
        <n-tabs type="line" animated>
          <n-tab-pane name="leaderboard" tab="对战排行榜">
            <n-space vertical>
              <n-space justify="space-between" align="center">
                <n-select
                  v-model:value="selectedSeason"
                  :options="seasonOptions"
                  placeholder="选择赛季"
                  style="width: 200px"
                  @update:value="loadLeaderboard"
                />
                <n-button @click="loadLeaderboard" :loading="loading">
                  <template #icon>
                    <n-icon><RefreshOutline /></n-icon>
                  </template>
                  刷新
                </n-button>
              </n-space>

              <n-card v-if="myRating" size="small" title="我的等级分">
                <n-space vertical>
                  <n-space align="center">
                    <n-tag :type="getRatingColor(myRating.rating)" size="large">
                      {{ getRatingTier(myRating.rating) }}
                    </n-tag>
                    <span style="font-size: 24px; font-weight: bold">{{ myRating.rating }}</span>
                    <span style="color: #666">等级分</span>
                  </n-space>
                  <n-space>
                    <n-statistic label="对战等级" :value="myRating.battle_level" />
                    <n-statistic label="经验值" :value="myRating.experience" />
                    <n-statistic label="胜场" :value="myRating.wins" />
                    <n-statistic label="总场次" :value="myRating.total_battles" />
                    <n-statistic label="胜率" :value="myRating.win_rate + '%'" />
                    <n-statistic label="最高分" :value="myRating.peak_rating" />
                  </n-space>
                </n-space>
              </n-card>

              <n-data-table
                :columns="columns"
                :data="leaderboardData"
                :loading="loading"
                :pagination="false"
                :bordered="false"
              />
            </n-space>
          </n-tab-pane>
        </n-tabs>
      </n-card>

      <n-card v-if="showTab === 'history'" title="对战历史">
        <n-space vertical>
          <n-data-table
            :columns="historyColumns"
            :data="historyData"
            :loading="loadingHistory"
            :pagination="pagination"
            @update:page="handlePageChange"
          />
        </n-space>
      </n-card>

      <n-card v-if="showTab === 'rules'" title="规则说明">
        <n-space vertical size="large">
          <div>
            <h3>📊 等级分系统</h3>
            <ul>
              <li>如果没有进行过对战，等级分将初始化为 <strong>500 分</strong></li>
              <li>每个赛季开始时，所有玩家的等级分将重置，但可以继承部分上赛季分数</li>
              <li>对战等级不会重置，每 100 经验升 1 级</li>
            </ul>
          </div>

          <div>
            <h3>⚖️ 分数结算规则</h3>
            <p>当两个玩家均完成（AC）或放弃后，系统会根据以下规则结算分数：</p>
            
            <h4>⚠️ 特判规则（惩罚消极比赛）</h4>
            <n-alert type="warning" style="margin-bottom: 12px">
              双方都超时且均未AC/放弃 → 双方各扣 <strong>20 分</strong>，<strong>0 经验</strong>
            </n-alert>
            <p style="color: #666; margin-bottom: 20px">此规则是为了惩罚消极比赛，避免双方都不认真做题，等待对方放弃的情况</p>

            <h4>常规规则</h4>
            <n-table :bordered="true" :single-line="false">
              <thead>
                <tr>
                  <th>规则</th>
                  <th>你的状态</th>
                  <th>对方状态</th>
                  <th>分数变动</th>
                  <th>经验变化</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>规则1</td>
                  <td>首先 AC</td>
                  <td>后 AC 或放弃（包括对方放弃后你AC）</td>
                  <td><n-tag type="success">+15 分</n-tag><br/>如果在奖励时间内AC，额外<n-tag type="success">+5分</n-tag></td>
                  <td><n-tag type="info">+10 经验</n-tag></td>
                </tr>
                <tr>
                  <td>规则2</td>
                  <td>对方先 AC 后，你放弃</td>
                  <td>先 AC</td>
                  <td><n-tag type="error">-12 分</n-tag></td>
                  <td>0 经验</td>
                </tr>
                <tr>
                  <td>规则3</td>
                  <td>对方先 AC 后，你后 AC</td>
                  <td>先 AC</td>
                  <td><n-tag type="warning">-2 分</n-tag><br/>如果在奖励时间内AC，额外<n-tag type="success">+5分</n-tag></td>
                  <td><n-tag type="info">+5 经验</n-tag></td>
                </tr>
                <tr>
                  <td>规则4</td>
                  <td>对方 AC/放弃之前，你先放弃</td>
                  <td>未 AC 且未放弃，或后完成</td>
                  <td><n-tag type="error">-15 分</n-tag></td>
                  <td>0 经验</td>
                </tr>
                <tr>
                  <td>规则5</td>
                  <td>对方放弃后，你放弃</td>
                  <td>先放弃（未 AC）</td>
                  <td><n-tag type="success">+2 分</n-tag></td>
                  <td>0 经验</td>
                </tr>
              </tbody>
            </n-table>
          </div>

          <div>
            <h3>🎖️ 等级分段位</h3>
            <n-space>
              <n-tag type="error" size="large">荣耀 (2000+)</n-tag>
              <n-tag type="warning" size="large">大师 (1800-1999)</n-tag>
              <n-tag type="success" size="large">钻石 (1500-1799)</n-tag>
              <n-tag type="info" size="large">铂金 (1200-1499)</n-tag>
              <n-tag type="default" size="large">黄金 (900-1199)</n-tag>
              <n-tag size="large">白银 (600-899)</n-tag>
              <n-tag size="large">青铜 (0-599)</n-tag>
            </n-space>
          </div>
        </n-space>
      </n-card>
    </n-space>
  </div>
</template>

<script setup>
import { ref, h, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useMessage, NTag, NButton, NSpace } from 'naive-ui';
import { RefreshOutline } from '@vicons/ionicons5';
import Axios from '@/plugins/axios';

const router = useRouter();
const message = useMessage();

const showTab = ref('1v1');
const loading = ref(false);
const loadingHistory = ref(false);
const leaderboardData = ref([]);
const historyData = ref([]);
const myRating = ref(null);
const currentSeason = ref(null);
const selectedSeason = ref(null);
const seasons = ref([]);

const pagination = ref({
  page: 1,
  pageSize: 20,
  itemCount: 0,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
});

const seasonOptions = computed(() => {
  const options = seasons.value.map(s => ({
    label: s.name,
    value: s.id,
  }));
  options.unshift({ label: '当前赛季', value: null });
  return options;
});

const getRatingColor = (rating) => {
  if (rating >= 2000) return 'error';
  if (rating >= 1800) return 'warning';
  if (rating >= 1500) return 'success';
  if (rating >= 1200) return 'info';
  return 'default';
};

const getRatingTier = (rating) => {
  if (rating >= 2000) return '荣耀';
  if (rating >= 1800) return '大师';
  if (rating >= 1500) return '钻石';
  if (rating >= 1200) return '铂金';
  if (rating >= 900) return '黄金';
  if (rating >= 600) return '白银';
  return '青铜';
};

const columns = [
  {
    title: '排名',
    key: 'rank',
    width: 80,
    render: (row, index) => {
      if (index === 0) return h('span', { style: 'font-size: 24px' }, '🥇');
      if (index === 1) return h('span', { style: 'font-size: 24px' }, '🥈');
      if (index === 2) return h('span', { style: 'font-size: 24px' }, '🥉');
      return index + 1;
    },
  },
  {
    title: '用户',
    key: 'user',
    render: (row) => {
      return h(
        NButton,
        {
          text: true,
          onClick: () => router.push(`/user/${row.user.id}`),
        },
        { default: () => row.user.real_name || row.user.username }
      );
    },
  },
  {
    title: '等级分',
    key: 'rating',
    sorter: 'default',
    render: (row) => {
      return h(
        NSpace,
        { align: 'center' },
        {
          default: () => [
            h(NTag, { type: getRatingColor(row.rating) }, { default: () => getRatingTier(row.rating) }),
            h('span', { style: 'font-weight: bold; font-size: 16px' }, row.rating),
          ],
        }
      );
    },
  },
  {
    title: '胜场',
    key: 'wins',
    width: 80,
  },
  {
    title: '总场次',
    key: 'total_battles',
    width: 100,
  },
  {
    title: '胜率',
    key: 'win_rate',
    width: 100,
    render: (row) => `${row.win_rate}%`,
  },
];

const historyColumns = [
  {
    title: '时间',
    key: 'created_at',
    render: (row) => new Date(row.created_at).toLocaleString('zh-CN'),
  },
  {
    title: '对手',
    key: 'opponent',
    render: (row) => {
      const isUserA = row.user_a.id === myRating.value?.user?.id;
      const opponent = isUserA ? row.user_b : row.user_a;
      return opponent.real_name || opponent.username;
    },
  },
  {
    title: '结果',
    key: 'result',
    render: (row) => {
      const isUserA = row.user_a.id === myRating.value?.user?.id;
      const isWin = row.winner?.id === myRating.value?.user?.id;
      return h(
        NTag,
        { type: isWin ? 'success' : 'error' },
        { default: () => (isWin ? '胜利' : '失败') }
      );
    },
  },
  {
    title: '分数变化',
    key: 'rating_change',
    render: (row) => {
      const isUserA = row.user_a.id === myRating.value?.user?.id;
      const change = isUserA ? row.user_a_rating_change : row.user_b_rating_change;
      return h(
        'span',
        { style: `color: ${change > 0 ? 'green' : 'red'}; font-weight: bold` },
        change > 0 ? `+${change}` : change
      );
    },
  },
  {
    title: '经验变化',
    key: 'exp_change',
    render: (row) => {
      const isUserA = row.user_a.id === myRating.value?.user?.id;
      const change = isUserA ? row.user_a_exp_change : row.user_b_exp_change;
      return `+${change}`;
    },
  },
];

const loadLeaderboard = async () => {
  loading.value = true;
  try {
    const params = {};
    if (selectedSeason.value) {
      params.season_id = selectedSeason.value;
    }
    
    const res = await Axios.get('/battle/leaderboard/', { params });
    leaderboardData.value = res.leaderboard || [];
    currentSeason.value = res.current_season;
  } catch (err) {
    console.error('Load leaderboard error:', err);
    message.error('加载排行榜失败');
  } finally {
    loading.value = false;
  }
};

const loadMyRating = async () => {
  try {
    const params = {};
    if (selectedSeason.value) {
      params.season_id = selectedSeason.value;
    }
    
    const res = await Axios.get('/battle/my-rating/', { params });
    myRating.value = res.rating;
  } catch (err) {
    console.error('Load my rating error:', err);
  }
};

const loadHistory = async (page = 1) => {
  loadingHistory.value = true;
  try {
    const res = await Axios.get('/battle/history/', {
      params: {
        page,
        page_size: pagination.value.pageSize,
      },
    });
    historyData.value = res.results || [];
    pagination.value.itemCount = res.total;
    pagination.value.page = page;
  } catch (err) {
    console.error('Load history error:', err);
    message.error('加载对战历史失败');
  } finally {
    loadingHistory.value = false;
  }
};

const loadSeasons = async () => {
  try {
    const res = await Axios.get('/battle/seasons/');
    seasons.value = res.seasons || [];
  } catch (err) {
    console.error('Load seasons error:', err);
  }
};

const handlePageChange = (page) => {
  loadHistory(page);
};

// 监听 tab 切换，加载对应数据
watch(showTab, async (newTab) => {
  if (newTab === 'history' && historyData.value.length === 0) {
    await loadHistory();
  }
});

onMounted(async () => {
  await loadSeasons();
  await loadLeaderboard();
  await loadMyRating();
});
</script>

<style scoped>
.leaderboard-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h3 {
  margin-top: 0;
  margin-bottom: 12px;
}

h4 {
  margin-top: 16px;
  margin-bottom: 8px;
}

ul {
  margin: 8px 0;
  padding-left: 24px;
}

li {
  margin: 8px 0;
}
</style>
