<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useMessage, NIcon } from 'naive-ui';
import { HelpCircleOutline } from '@vicons/ionicons5';
import Axios from '@/plugins/axios';
import { difficultyOptions as allDifficultyOptions } from '@/plugins/consts';

const router = useRouter();
const message = useMessage();

const creating = ref(false);
const joining = ref(false);
const roomId = ref('');
const myRating = ref(null);
const loading = ref(false);

const difficultyMin = ref(null);
const difficultyMax = ref(null);

const difficultyOptions = [{ label: '不限', value: null }, ...allDifficultyOptions];

const createRoom = async () => {
  creating.value = true;
  try {
    let dmin = difficultyMin.value;
    let dmax = difficultyMax.value;
    if (dmin === null && dmax !== null) dmin = 0;
    if (dmin !== null && dmax === null) dmax = dmin;

    const res = await Axios.post('/battle/rooms/', {
      room_type: 'friend',
      duration_seconds: 1800,
      difficulty_min: dmin,
      difficulty_max: dmax,
    });
    await router.push({ name: 'battle_room', params: { id: res.id } });
  } finally {
    creating.value = false;
  }
};

const joinRoom = async () => {
  const id = (roomId.value || '').trim();
  if (!id) {
    message.warning('请输入房间 ID');
    return;
  }
  joining.value = true;
  try {
    await Axios.post(`/battle/rooms/${id}/join/`);
    await router.push({ name: 'battle_room', params: { id } });
  } finally {
    joining.value = false;
  }
};

const loadMyRating = async () => {
  loading.value = true;
  try {
    const res = await Axios.get('/battle/my-rating/');
    myRating.value = res.rating;
  } catch (err) {
    console.error('Load rating error:', err);
  } finally {
    loading.value = false;
  }
};

const getRatingColor = (rating) => {
  if (!rating) return '#708090';
  if (rating >= 2000) return '#e74c3c';
  if (rating >= 1800) return '#f39c12';
  if (rating >= 1500) return '#27ae60';
  if (rating >= 1200) return '#2d78d4';
  if (rating >= 900) return '#9a7b18';
  if (rating >= 600) return '#607d8b';
  return '#7f8c8d';
};

const getRatingTier = (rating) => {
  if (!rating) return '青铜';
  if (rating >= 2000) return '荣耀';
  if (rating >= 1800) return '大师';
  if (rating >= 1500) return '钻石';
  if (rating >= 1200) return '铂金';
  if (rating >= 900) return '黄金';
  if (rating >= 600) return '白银';
  return '青铜';
};

const expProgress = computed(() => {
  if (!myRating.value) return 0;
  const currentLevelExp = myRating.value.experience % 100;
  return currentLevelExp;
});

const expForNextLevel = computed(() => 100);

const currentLevelExp = computed(() => {
  if (!myRating.value) return 0;
  return myRating.value.experience % 100;
});

const winRateLabel = computed(() => {
  if (!myRating.value || myRating.value.win_rate === null || myRating.value.win_rate === undefined) {
    return '-';
  }
  return `${myRating.value.win_rate}%`;
});

onMounted(() => {
  loadMyRating();
});
</script>

<template>
  <div class="battle-lobby-page">
    <n-card class="battle-hero" :bordered="false">
      <div class="battle-hero__main">
        <div>
          <div class="battle-hero__badge">实时匹配 · 1v1 对战</div>
          <h1 class="battle-hero__title">⚔️ 对战大厅</h1>
          <p class="battle-hero__desc">创建房间邀请同学切磋，按段位难度选题，实时比拼解题速度与稳定性。</p>
        </div>
        <n-space class="battle-hero__actions" wrap>
          <n-button type="primary" class="hero-create-btn" :loading="creating" @click="createRoom">
            快速创建房间
          </n-button>
          <n-button type="primary" ghost @click="router.push('/battle/leaderboard')">🏆 对战排行榜</n-button>
          <n-button ghost @click="router.push('/battle/leaderboard?tab=history')">📜 对战历史</n-button>
          <n-button ghost @click="router.push('/battle/leaderboard?tab=rules')">📖 规则说明</n-button>
        </n-space>
      </div>
    </n-card>

    <n-grid :cols="24" :x-gap="16" :y-gap="16" responsive="screen" class="battle-grid">
      <n-gi :span="24" :l="14">
        <n-card class="panel-card" :bordered="false" :loading="loading">
          <div class="rating-panel">
            <div class="rating-panel__left">
              <div class="rating-panel__tier">{{ getRatingTier(myRating?.rating || 500) }}</div>
              <div class="rating-panel__score" :style="{ color: getRatingColor(myRating?.rating || 500) }">
                {{ myRating?.rating || 500 }}
              </div>
              <div class="rating-panel__label">当前等级分</div>
            </div>

            <div class="rating-panel__right">
              <div class="level-panel">
                <div class="level-panel__header">
                  <span class="level-panel__title">⭐ 对战等级</span>
                  <n-button circle size="tiny" quaternary>
                    <template #icon>
                      <n-icon><HelpCircleOutline /></n-icon>
                    </template>
                  </n-button>
                </div>
                <div class="level-panel__value">Lv.{{ myRating?.battle_level || 1 }}</div>
                <div class="level-panel__meta">
                  <span>经验 {{ currentLevelExp }} / {{ expForNextLevel }}</span>
                  <span>还需 {{ expForNextLevel - currentLevelExp }}</span>
                </div>
                <n-progress
                  type="line"
                  :percentage="expProgress"
                  :show-indicator="false"
                  :height="10"
                  :border-radius="6"
                  rail-color="#dceaf9"
                  fill-color="#2d78d4"
                />
              </div>
            </div>
          </div>

          <n-grid :cols="3" :x-gap="12" class="stats-grid">
            <n-gi>
              <div class="stat-box">
                <div class="stat-box__label">胜场</div>
                <div class="stat-box__value">{{ myRating?.wins || 0 }}</div>
              </div>
            </n-gi>
            <n-gi>
              <div class="stat-box">
                <div class="stat-box__label">总场次</div>
                <div class="stat-box__value">{{ myRating?.total_battles || 0 }}</div>
              </div>
            </n-gi>
            <n-gi>
              <div class="stat-box">
                <div class="stat-box__label">胜率</div>
                <div class="stat-box__value">{{ winRateLabel }}</div>
              </div>
            </n-gi>
          </n-grid>
        </n-card>
      </n-gi>

      <n-gi :span="24" :l="10">
        <n-space vertical size="16">
          <n-card title="🎮 创建好友房" class="panel-card" :bordered="false">
            <div class="room-hint">可按难度范围创建房间，系统在范围内随机出题。</div>
            <n-grid :cols="2" :x-gap="12" :y-gap="12" class="room-form-grid">
              <n-gi>
                <n-select
                  v-model:value="difficultyMin"
                  placeholder="最低难度"
                  :options="difficultyOptions"
                />
              </n-gi>
              <n-gi>
                <n-select
                  v-model:value="difficultyMax"
                  placeholder="最高难度"
                  :options="difficultyOptions"
                />
              </n-gi>
            </n-grid>
            <n-button type="primary" block class="room-action-btn" :loading="creating" @click="createRoom">
              创建房间并进入
            </n-button>
          </n-card>

          <n-card title="🚪 加入房间" class="panel-card" :bordered="false">
            <div class="room-hint">输入好友分享的房间 ID（UUID）。</div>
            <n-input v-model:value="roomId" placeholder="例如：54b2f7c8-xxxx-xxxx-xxxx-xxxxxxxxxxxx" />
            <n-button type="success" block class="room-action-btn" :loading="joining" @click="joinRoom">
              加入并开始对战
            </n-button>
          </n-card>
        </n-space>
      </n-gi>
    </n-grid>
  </div>
</template>

<style scoped>
.battle-lobby-page {
  padding: 8px 0 20px;
}

.battle-hero {
  margin-bottom: 16px;
  background: linear-gradient(120deg, #113b62 0%, #1b5b8f 56%, #1f7f86 100%);
  border-radius: 16px;
  color: #f2f8ff;
  box-shadow: 0 12px 28px rgba(17, 59, 98, 0.18);
}

.battle-hero__main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.battle-hero__badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  color: #c4e8ff;
  background: rgba(255, 255, 255, 0.1);
  margin-bottom: 12px;
}

.battle-hero__title {
  margin: 0;
  font-size: 32px;
  font-weight: 800;
  letter-spacing: 0.4px;
}

.battle-hero__desc {
  margin: 10px 0 0;
  line-height: 1.7;
  color: #d8ebfb;
  max-width: 680px;
}

.battle-hero__actions :deep(.n-button) {
  border-color: rgba(255, 255, 255, 0.38);
  color: #f5fbff;
  background: rgba(255, 255, 255, 0.06);
}

.battle-hero__actions :deep(.hero-create-btn) {
  border-color: transparent;
  background: #20a65a;
  color: #fff;
  font-weight: 700;
  box-shadow: 0 8px 18px rgba(32, 166, 90, 0.36);
}

.battle-hero__actions :deep(.hero-create-btn):hover {
  background: #1b9651;
}

.battle-grid {
  width: 100%;
}

.panel-card {
  border-radius: 14px;
  box-shadow: 0 8px 24px rgba(16, 39, 68, 0.08);
}

.rating-panel {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 16px;
  align-items: stretch;
}

.rating-panel__left {
  border-radius: 12px;
  background: linear-gradient(180deg, #f4f8fc 0%, #ebf2f8 100%);
  padding: 16px;
  text-align: center;
}

.rating-panel__tier {
  font-size: 13px;
  color: #4d6073;
}

.rating-panel__score {
  margin-top: 4px;
  font-size: 48px;
  font-weight: 800;
  line-height: 1.1;
}

.rating-panel__label {
  margin-top: 6px;
  color: #6e8195;
  font-size: 13px;
}

.rating-panel__right {
  min-width: 0;
}

.level-panel {
  border: 1px solid #dceaf9;
  background: #f8fbff;
  border-radius: 12px;
  padding: 14px;
}

.level-panel__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.level-panel__title {
  font-size: 14px;
  font-weight: 600;
  color: #1f3550;
}

.level-panel__value {
  margin-top: 8px;
  font-size: 28px;
  font-weight: 800;
  color: #144977;
}

.level-panel__meta {
  margin: 8px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  color: #566c83;
  font-size: 12px;
}

.stats-grid {
  margin-top: 14px;
}

.stat-box {
  border-radius: 10px;
  border: 1px solid #e7edf4;
  background: #fbfdff;
  padding: 10px 12px;
}

.stat-box__label {
  font-size: 12px;
  color: #6f8092;
}

.stat-box__value {
  margin-top: 4px;
  font-size: 22px;
  font-weight: 700;
  color: #1f3550;
}

.room-hint {
  margin-bottom: 10px;
  color: #5c7085;
  font-size: 13px;
}

.room-form-grid {
  margin-bottom: 12px;
}

.room-action-btn {
  margin-top: 10px;
}

@media (max-width: 1200px) {
  .battle-hero__main {
    flex-direction: column;
  }
}

@media (max-width: 900px) {
  .rating-panel {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .battle-hero__title {
    font-size: 26px;
  }

  .battle-hero__desc {
    font-size: 13px;
  }
}
</style>
