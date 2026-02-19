<script setup>
import Axios from '@/plugins/axios';
import { computed, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import store from '@/store';
import {
  RefreshOutline,
  MegaphoneOutline,
  SettingsOutline,
  TrophyOutline,
  PeopleOutline,
} from '@vicons/ionicons5';

const router = useRouter();

const yiyan = ref({ content: '', from_show: '' });
const loadingYiyan = ref(false);
const announcements = ref([]);
const loadingAnnouncement = ref(false);

const rankingLoading = ref(false);
const rankingMode = ref('global');
const rankingRows = ref([]);
const classOptions = ref([]);
const classLoading = ref(false);
const selectedClassId = ref(null);

const canManageAnnouncement = computed(() => {
  const perms = store.state.user?.permissions || [];
  return perms.includes('site_setting');
});

const canUseClassRanking = computed(() => {
  return Boolean(store.state.user?.token) && classOptions.value.length > 0;
});

const normalizeYiyan = raw => {
  const res = raw || {};
  if (res.provenance && res.author) {
    res.from_show = `${res.provenance} · ${res.author}`;
  } else {
    res.from_show = `${res.provenance || res.author || ''}`;
  }
  return {
    content: res.content || '点击刷新一言',
    from_show: res.from_show || '',
  };
};

const parseMaybeJson = input => {
  if (typeof input === 'string') {
    try {
      return JSON.parse(input);
    } catch (e) {
      return {};
    }
  }
  return input || {};
};

const normalizeRankingRows = rows => {
  if (!Array.isArray(rows)) return [];
  return rows.map((item, index) => {
    const user = item?.user || {};
    return {
      rank: Number(item?.rank || index + 1),
      solved_count: Number(item?.solved_count || 0),
      accepted_count: Number(item?.accepted_count || 0),
      user: {
        id: user?.id,
        username: user?.username || 'unknown',
        real_name: user?.real_name || '',
        avatar: user?.avatar || null,
      },
    };
  });
};

const rankBadge = rank => {
  if (rank === 1) return '🥇';
  if (rank === 2) return '🥈';
  if (rank === 3) return '🥉';
  return `#${rank}`;
};

const getYiyan = async () => {
  loadingYiyan.value = true;
  const start = Date.now();

  try {
    let res;
    if (store.state.displaySettings.sentenceApi === 'hitokoto') {
      res = await Axios.get('https://v1.hitokoto.cn/?encode=json').then(resp => {
        const item = parseMaybeJson(resp);
        item.provenance = item.from;
        item.author = item.from_who;
        item.content = item.hitokoto;
        return item;
      });
    } else {
      res = await Axios.get('https://api.yixiangzhilv.com/yiyan/sentence/get/');
    }

    setTimeout(() => {
      yiyan.value = normalizeYiyan(res);
      loadingYiyan.value = false;
    }, Math.max(0, 300 - (Date.now() - start)));
  } catch (e) {
    yiyan.value = normalizeYiyan({ content: '一言加载失败，点击重试' });
    loadingYiyan.value = false;
  }
};

const parseAnnouncementResponse = res => {
  const data = parseMaybeJson(res);
  const rows = Array.isArray(data) ? data : data?.results;
  if (!Array.isArray(rows)) return [];
  return rows.map(item => ({
    id: item?.id,
    title: item?.title || '未命名公告',
    content: item?.content || '',
    is_pinned: !!item?.is_pinned,
    updated_at: item?.updated_at || null,
  }));
};

const getAnnouncements = () => {
  loadingAnnouncement.value = true;
  Axios.get('/announcement/', {
    params: {
      limit: 5,
    },
  })
    .then(res => {
      announcements.value = parseAnnouncementResponse(res);
    })
    .catch(() => {
      announcements.value = [];
    })
    .finally(() => {
      loadingAnnouncement.value = false;
    });
};

const fetchClassOptions = async () => {
  if (!store.state.user?.token) {
    classOptions.value = [];
    selectedClassId.value = null;
    return;
  }

  classLoading.value = true;
  try {
    const res = await Axios.get('class/class/');
    const rows = Array.isArray(res) ? res : [];
    classOptions.value = rows.map(item => ({
      label: item?.title || `班级 #${item?.id}`,
      value: item?.id,
    }));

    if (!classOptions.value.length) {
      selectedClassId.value = null;
      rankingMode.value = 'global';
    } else if (!selectedClassId.value) {
      selectedClassId.value = classOptions.value[0].value;
    }
  } catch (e) {
    classOptions.value = [];
    selectedClassId.value = null;
    rankingMode.value = 'global';
  } finally {
    classLoading.value = false;
  }
};

const fetchRanking = () => {
  rankingLoading.value = true;
  const params = { limit: 10 };
  if (rankingMode.value === 'class' && selectedClassId.value) {
    params.class_id = selectedClassId.value;
  }

  Axios.get('user/ranking/', { params })
    .then(res => {
      const list = Array.isArray(res?.ranking) ? res.ranking : (Array.isArray(res) ? res : []);
      rankingRows.value = normalizeRankingRows(list);
    })
    .catch(() => {
      rankingRows.value = [];
    })
    .finally(() => {
      rankingLoading.value = false;
    });
};

const refreshRanking = async () => {
  if (rankingMode.value === 'class' && !canUseClassRanking.value) {
    rankingMode.value = 'global';
  }
  if (rankingMode.value === 'class' && !selectedClassId.value && classOptions.value.length) {
    selectedClassId.value = classOptions.value[0].value;
  }
  fetchRanking();
};

const toLocalTime = value => {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  return date.toLocaleString('zh-CN', { hour12: false });
};

watch(rankingMode, value => {
  if (value === 'class' && !canUseClassRanking.value) {
    rankingMode.value = 'global';
    return;
  }
  refreshRanking();
});

watch(selectedClassId, () => {
  if (rankingMode.value === 'class') {
    refreshRanking();
  }
});

onMounted(async () => {
  getYiyan();
  getAnnouncements();
  await fetchClassOptions();
  fetchRanking();
});
</script>

<template>
  <n-layout-content class="home-page">
    <section class="announcement-panel">
      <div class="panel-head">
        <div class="head-left">
          <div class="title-row">
            <n-icon :component="MegaphoneOutline" />
            <h2>公告中心</h2>
            <span class="hot-badge">HOT</span>
          </div>
          <p class="panel-desc">重要通知会优先显示在这里，建议每天查看。</p>
        </div>
        <div class="head-actions">
          <n-button quaternary @click="getAnnouncements">
            <template #icon>
              <n-icon :component="RefreshOutline" />
            </template>
            刷新
          </n-button>
          <n-button
            v-if="canManageAnnouncement"
            type="primary"
            @click="router.push({ name: 'announcement_manage' })"
          >
            <template #icon>
              <n-icon :component="SettingsOutline" />
            </template>
            管理公告
          </n-button>
        </div>
      </div>

      <n-spin :show="loadingAnnouncement">
        <n-empty v-if="!announcements.length" description="暂无公告" />
        <div v-else class="announcement-list">
          <article
            v-for="(item, index) in announcements"
            :key="item.id"
            class="announcement-item"
            :class="{ pinned: item.is_pinned, featured: index === 0 }"
          >
            <div class="accent"></div>
            <div class="main">
              <div class="item-head">
                <h3>{{ item.title }}</h3>
                <div class="item-tags">
                  <n-tag v-if="item.is_pinned" type="warning" size="small" :bordered="false">
                    置顶
                  </n-tag>
                  <n-tag v-if="index === 0" type="success" size="small" :bordered="false">最新</n-tag>
                </div>
              </div>
              <p class="content">{{ item.content }}</p>
              <p class="time" v-if="toLocalTime(item.updated_at)">更新时间：{{ toLocalTime(item.updated_at) }}</p>
            </div>
          </article>
        </div>
      </n-spin>
    </section>

    <section class="ranking-panel">
      <div class="panel-head ranking-head">
        <div class="head-left">
          <div class="title-row">
            <n-icon :component="TrophyOutline" />
            <h2>做题排行榜</h2>
            <span class="rank-badge">TOP 10</span>
          </div>
          <p class="panel-desc">按通过题目数量（去重）排序，鼓励持续刷题。</p>
        </div>

        <div class="head-actions ranking-actions">
          <n-radio-group v-model:value="rankingMode" size="small">
            <n-radio-button value="global">全站榜</n-radio-button>
            <n-radio-button value="class" :disabled="!canUseClassRanking">班级榜</n-radio-button>
          </n-radio-group>

          <n-select
            v-if="rankingMode === 'class'"
            v-model:value="selectedClassId"
            :options="classOptions"
            :loading="classLoading"
            placeholder="选择班级"
            style="width: 220px"
          />

          <n-button quaternary @click="refreshRanking">
            <template #icon>
              <n-icon :component="RefreshOutline" />
            </template>
            刷新榜单
          </n-button>
        </div>
      </div>

      <n-spin :show="rankingLoading">
        <n-empty v-if="!rankingRows.length" description="暂无排行数据" />
        <div v-else class="ranking-list">
          <article v-for="item in rankingRows" :key="`${item.user.id}-${item.rank}`" class="ranking-item">
            <div class="rank-tag" :class="`r${item.rank}`">{{ rankBadge(item.rank) }}</div>
            <div class="ranking-main">
              <n-button text @click="router.push(`/user/${item.user.id}`)" class="ranking-name-btn">
                <n-space align="center" size="small">
                  <n-avatar v-if="item.user.avatar" round :src="item.user.avatar" size="small" />
                  <n-icon v-else :component="PeopleOutline" />
                  <span class="ranking-name">{{ item.user.real_name || item.user.username }}</span>
                </n-space>
              </n-button>
              <div class="ranking-sub">@{{ item.user.username }}</div>
            </div>
            <div class="solved-count">
              <strong>{{ item.solved_count }}</strong>
              <span>题</span>
            </div>
          </article>
        </div>
      </n-spin>
    </section>

    <section
      class="quote-panel"
      :class="{ loading: loadingYiyan }"
      @click="getYiyan"
      title="点击刷新一言"
    >
      <h1>
        <div class="quote-content">{{ yiyan.content }}</div>
        <div v-show="yiyan.from_show" class="quote-from">- 「 {{ yiyan.from_show }} 」</div>
      </h1>
    </section>
  </n-layout-content>
</template>

<style lang="scss" scoped>
.home-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.announcement-panel {
  border: 1px solid #cedef2;
  border-radius: 18px;
  background: linear-gradient(180deg, #f2f8ff 0%, #ffffff 40%);
  padding: 18px;
  box-shadow: 0 14px 28px rgba(33, 89, 145, 0.08);
}

.ranking-panel {
  border: 1px solid #dce8db;
  border-radius: 18px;
  background: linear-gradient(180deg, #f4fbf4 0%, #ffffff 38%);
  padding: 18px;
  box-shadow: 0 14px 28px rgba(37, 116, 66, 0.08);
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 14px;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.head-left h2 {
  margin: 0;
  font-size: 28px;
  color: #0f497a;
  letter-spacing: 1px;
}

.ranking-panel .head-left h2 {
  color: #1c4d31;
}

.head-left :deep(.n-icon) {
  font-size: 28px;
  color: #0f71b0;
}

.ranking-panel .head-left :deep(.n-icon) {
  color: #2d9758;
}

.hot-badge,
.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 20px;
  padding: 0 8px;
  border-radius: 999px;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
}

.hot-badge {
  background: linear-gradient(90deg, #f97316 0%, #ef4444 100%);
}

.rank-badge {
  background: linear-gradient(90deg, #16a34a 0%, #15803d 100%);
}

.panel-desc {
  margin: 8px 0 0;
  color: #436484;
  font-size: 14px;
}

.ranking-panel .panel-desc {
  color: #4d6f58;
}

.head-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ranking-actions {
  flex-wrap: wrap;
  justify-content: flex-end;
}

.announcement-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.announcement-item {
  position: relative;
  display: flex;
  border: 1px solid #dce9f9;
  border-radius: 14px;
  background: #ffffff;
  overflow: hidden;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid #d8e8dd;
  border-radius: 14px;
  background: #ffffff;
  padding: 10px 12px;
}

.rank-tag {
  min-width: 56px;
  height: 36px;
  border-radius: 12px;
  background: #edf4ee;
  color: #2a5f39;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.rank-tag.r1 {
  background: #fff4d4;
}

.rank-tag.r2 {
  background: #ecf1f7;
}

.rank-tag.r3 {
  background: #f9ede5;
}

.ranking-main {
  flex: 1;
  min-width: 0;
}

.ranking-name-btn {
  padding: 0;
}

.ranking-name {
  font-size: 16px;
  font-weight: 700;
  color: #194b2d;
}

.ranking-sub {
  margin-top: 2px;
  font-size: 12px;
  color: #6b7e74;
}

.solved-count {
  display: inline-flex;
  align-items: baseline;
  gap: 2px;
  color: #166534;
}

.solved-count strong {
  font-size: 24px;
  line-height: 1;
}

.solved-count span {
  font-size: 13px;
}

.announcement-item .accent {
  width: 6px;
  background: linear-gradient(180deg, #2b8ed8 0%, #5aa7e8 100%);
}

.announcement-item .main {
  flex: 1;
  padding: 14px 16px;
}

.announcement-item.featured {
  border-color: #8ec3ef;
  box-shadow: 0 10px 20px rgba(37, 115, 186, 0.1);
}

.announcement-item.featured .accent {
  background: linear-gradient(180deg, #0ea5e9 0%, #0284c7 100%);
}

.announcement-item.pinned {
  border-color: #f2d39f;
  background: linear-gradient(180deg, #fff9ee 0%, #fffefb 100%);
}

.announcement-item.pinned .accent {
  background: linear-gradient(180deg, #f59e0b 0%, #f97316 100%);
}

.item-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.item-head h3 {
  margin: 0;
  font-size: 19px;
  color: #173b63;
}

.item-tags {
  display: flex;
  align-items: center;
  gap: 6px;
}

.content {
  margin: 10px 0 0;
  white-space: pre-wrap;
  line-height: 1.75;
  color: #2f4965;
  font-size: 16px;
}

.time {
  margin: 10px 0 0;
  font-size: 13px;
  color: #64748b;
}

.quote-panel {
  height: calc(100vh - 590px);
  min-height: 240px;
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
  transition: all 0.4s;
  opacity: 1;
  cursor: pointer;
}

.quote-panel.loading {
  opacity: 0.35;
}

.quote-panel h1 {
  text-align: center;
}

.quote-content {
  letter-spacing: 2px;
  font-weight: 700;
  font-size: 42px;
  line-height: 1.3;
  background: linear-gradient(90deg, #1d4f7f 0%, #2a699b 35%, #ec6c2f 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.quote-from {
  margin-top: 40px;
  letter-spacing: 2px;
  color: #7a3450;
  font-size: 28px;
  font-weight: 600;
}

@media (max-width: 900px) {
  .panel-head {
    flex-direction: column;
    align-items: stretch;
  }

  .head-actions,
  .ranking-actions {
    justify-content: flex-end;
  }

  .head-left h2 {
    font-size: 24px;
  }

  .announcement-item .main {
    padding: 12px;
  }

  .item-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .content {
    font-size: 15px;
  }

  .quote-panel {
    min-height: 220px;
    height: auto;
    padding: 20px 0;
  }

  .quote-content {
    font-size: 30px;
  }

  .quote-from {
    font-size: 20px;
  }
}
</style>
