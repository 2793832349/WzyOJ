<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useMessage, NIcon } from 'naive-ui';
import { HelpCircleOutline } from '@vicons/ionicons5';
import Axios from '@/plugins/axios';

const router = useRouter();
const message = useMessage();

const creating = ref(false);
const joining = ref(false);
const roomId = ref('');
const myRating = ref(null);
const loading = ref(false);

const difficultyMin = ref(null);
const difficultyMax = ref(null);

const difficultyOptions = [
  { label: '不限', value: null },
  { label: '入门', value: 0 },
  { label: '普及-', value: 1 },
  { label: '普及/提高-', value: 2 },
  { label: '普及+/提高', value: 3 },
  { label: '提高+/省选-', value: 4 },
  { label: '省选/NOI-', value: 5 },
  { label: 'NOI/NOI+/CTSC', value: 6 },
];

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
  if (!id) return;
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
  if (!rating) return '#999';
  if (rating >= 2000) return '#e74c3c';
  if (rating >= 1800) return '#f39c12';
  if (rating >= 1500) return '#27ae60';
  if (rating >= 1200) return '#3498db';
  if (rating >= 900) return '#f1c40f';
  if (rating >= 600) return '#95a5a6';
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
  const exp = myRating.value.experience;
  const level = myRating.value.battle_level;
  const expForNextLevel = level * 100;
  const currentLevelExp = exp % 100;
  return (currentLevelExp / 100) * 100;
});

const expForNextLevel = computed(() => {
  if (!myRating.value) return 100;
  return 100;
});

const currentLevelExp = computed(() => {
  if (!myRating.value) return 0;
  return myRating.value.experience % 100;
});

onMounted(() => {
  loadMyRating();
});
</script>

<template>
  <n-layout>
    <n-space justify="space-between" align="center" style="margin-bottom: 20px">
      <h1 style="margin: 0">⚔️ 开始对战</h1>
      <n-space>
        <n-button type="primary" @click="router.push('/battle/leaderboard')">
          🏆 对战排行榜
        </n-button>
        <n-button @click="router.push('/battle/leaderboard?tab=history')">
          📜 对战历史
        </n-button>
        <n-button @click="router.push('/battle/leaderboard?tab=rules')">
          📖 说明
        </n-button>
      </n-space>
    </n-space>
    <n-layout-content>
      <n-space vertical size="large">
        <!-- 等级和段位显示卡片 -->
        <n-card>
          <div style="background: linear-gradient(135deg, #27ae60 0%, #229954 100%); padding: 20px; border-radius: 8px; color: white;">
            <n-space justify="space-between" align="center">
              <n-space align="center">
                <span style="font-size: 18px">⭐ 对战等级</span>
                <n-button circle size="small" quaternary style="color: white;">
                  <template #icon>
                    <n-icon><HelpCircleOutline /></n-icon>
                  </template>
                </n-button>
              </n-space>
              <span style="font-size: 32px; font-weight: bold;">Lv.{{ myRating?.battle_level || 1 }}</span>
            </n-space>
            
            <n-space vertical size="small" style="margin-top: 16px;">
              <n-space justify="space-between">
                <span>当前经验</span>
                <span>{{ currentLevelExp }} / {{ expForNextLevel }}</span>
              </n-space>
              <n-progress
                type="line"
                :percentage="expProgress"
                :show-indicator="false"
                :height="12"
                :border-radius="6"
                rail-color="rgba(255,255,255,0.3)"
                fill-color="rgba(255,255,255,0.9)"
              />
              <n-space justify="space-between">
                <span>已完成 {{ expProgress.toFixed(0) }}%</span>
                <span>还需 {{ expForNextLevel - currentLevelExp }} 经验升级</span>
              </n-space>
            </n-space>
          </div>
        </n-card>

        <n-card style="max-width: 500px;">
          <div style="text-align: center;">
            <div style="font-size: 14px; color: #666; margin-bottom: 8px;">{{ getRatingTier(myRating?.rating || 500) }}</div>
            <div style="font-size: 18px; margin-bottom: 8px;">⚔️ 1v1对战</div>
            <div 
              style="font-size: 48px; font-weight: bold; margin-bottom: 16px;"
              :style="{ color: getRatingColor(myRating?.rating || 500) }"
            >
              {{ myRating?.rating || 500 }}
            </div>
            <n-space justify="space-around" style="margin-top: 16px;">
              <div style="text-align: center;">
                <div style="color: #666; font-size: 12px;">胜场</div>
                <div style="font-size: 20px; font-weight: bold;">{{ myRating?.wins || 0 }}</div>
              </div>
              <div style="text-align: center;">
                <div style="color: #666; font-size: 12px;">总场次</div>
                <div style="font-size: 20px; font-weight: bold;">{{ myRating?.total_battles || 0 }}</div>
              </div>
              <div style="text-align: center;">
                <div style="color: #666; font-size: 12px;">胜率</div>
                <div style="font-size: 20px; font-weight: bold;">{{ myRating?.win_rate || '-' }}{{ myRating?.win_rate ? '%' : '' }}</div>
              </div>
            </n-space>
          </div>
        </n-card>
        <n-card title="🎮 好友房" size="small">
          <n-space>
            <n-select
              v-model:value="difficultyMin"
              placeholder="难度最小"
              :options="difficultyOptions"
              style="width: 180px"
            />
            <n-select
              v-model:value="difficultyMax"
              placeholder="难度最大"
              :options="difficultyOptions"
              style="width: 180px"
            />
            <n-button type="primary" :loading="creating" @click="createRoom">
              创建房间
            </n-button>
          </n-space>
        </n-card>

        <n-card title="加入房间" size="small">
          <n-space>
            <n-input v-model:value="roomId" placeholder="输入房间ID (UUID)" style="max-width: 360px" />
            <n-button type="primary" :loading="joining" @click="joinRoom">
              加入
            </n-button>
          </n-space>
        </n-card>
      </n-space>
    </n-layout-content>
  </n-layout>
</template>
