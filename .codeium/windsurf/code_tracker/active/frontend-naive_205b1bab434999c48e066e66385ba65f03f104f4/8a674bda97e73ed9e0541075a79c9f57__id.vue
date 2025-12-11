­6<script setup>
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
  mode = ref('é¢˜å•');

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
    
    // é¢˜å•æ¨¡å¼ï¼šç›´æ¥åŠ è½½æ’è¡Œæ¦œ
    if (res.problem_list_mode) {
      getRankingData();
    }
    // æ¯”èµ›æ¨¡å¼ï¼šæŒ‰æ—¶é—´åŠ è½½æ’è¡Œæ¦œ
    else if (res.start_time <= Date.now()) {
      getRankingData();
    } else {
      setTimeout(getRankingData, res.start_time - Date.now());
    }
    
    mode.value = res.problem_list_mode ? 'é¢˜å•' : 'æ¯”èµ›';
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
  Axios.post(`/contest/${id}/sign_up/`).then(res => {
    message.success('æŠ¥åæˆåŠŸ');
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
              è·ç¦»æ¯”èµ›å¼€å§‹è¿˜æœ‰ï¼š<n-countdown
                :duration="contestData.start_time - Date.now()"
              />
            </span>
            <span
              v-else-if="
                contestData.end_time && contestData.end_time > Date.now()
              "
            >
              è·ç¦»æ¯”èµ›ç»“æŸè¿˜æœ‰ï¼š<n-countdown
                :duration="contestData.end_time - Date.now()"
              />
            </span>
            <!-- <span v-else>æ¯”èµ›å·²ç»“æŸ</span> -->
          </div>
        </template>
        <n-tab-pane name="description" :tab="mode + 'ä¿¡æ¯'">
          <n-space vertical size="large">
            <div></div>

            <div v-if="contestData.joined || contestData.allow_sign_up">
              <h2>æ“ä½œ</h2>
              <n-button
                type="primary"
                @click="signUp"
                :disabled="
                  contestData.joined || Date.now() > contestData.end_time
                "
              >
                {{ contestData.joined ? 'å·²åŠ å…¥' : 'æŠ¥å' }}
              </n-button>
            </div>

            <div v-if="!contestData.problem_list_mode">
              <h2>æ¯”èµ›æ—¶é—´</h2>
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
              <h2>{{ mode }}æè¿°</h2>
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
          tab="é¢˜ç›®åˆ—è¡¨"
          :disabled="!contestData.problems.length"
        >
          <ProblemTable :data="contestData.problems" />
        </n-tab-pane>
        <n-tab-pane
          name="ranking"
          tab="æ’è¡Œæ¦œ"
        >
          <p style="font-size: medium">
            <span v-if="contestData.problem_list_mode">
              è¯´æ˜ï¼šé¢˜å•æ’è¡Œæ¦œç»Ÿè®¡æ‰€æœ‰ç”¨æˆ·é€šè¿‡ï¼ˆACï¼‰çš„é¢˜ç›®æ•°é‡ã€‚ä¸Šæ¬¡æ›´æ–°æ—¶é—´ï¼š<n-time
                :time="Number(new Date(rankingData.time))"
              />ã€‚
            </span>
            <span v-else-if="
              contestData.start_time <= Date.now() &&
              Date.now() <= contestData.end_time
            ">
              è¯´æ˜ï¼šæ¯”èµ›æ’è¡Œæ¦œä»…ç»Ÿè®¡æ¯”èµ›æŒç»­æ—¶é—´ä¸­çš„æäº¤ï¼Œæ¯åˆ†é’Ÿæ›´æ–°ä¸€æ¬¡ã€‚ä¸Šæ¬¡æ›´æ–°æ—¶é—´ï¼š<n-time
                :time="Number(new Date(rankingData.time))"
              />ã€‚
            </span>
            <n-popover v-if="store.state.user.permissions.includes('contest')">
              <template #trigger>
                <n-button
                  @click="getRankingData(true)"
                  :disabled="loadingRanking"
                >
                  å¼ºåˆ¶æ›´æ–°
                </n-button>
              </template>
              ä»…ç®¡ç†å‘˜å¯ç”¨ï¼Œå°†ä¼šç«‹å³åˆ·æ–°æ’è¡Œæ¦œç¼“å­˜ï¼Œè¯¥ç¼“å­˜å¯¹æ‰€æœ‰ç”¨æˆ·ç”Ÿæ•ˆã€‚
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
          tab="è®¨è®º"
          :disabled="
            contestData.start_time <= Date.now() &&
            Date.now() <= contestData.end_time
          "
        />
        <n-tab-pane
          name="edit"
          :tab="'ä¿®æ”¹' + mode"
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
Ã *cascade08Ãô*cascade08ô	 *cascade08	‘	*cascade08‘	’	 *cascade08’	Ş	*cascade08Ş	ß	 *cascade08ß	ë	*cascade08ë	ˆ
 *cascade08ˆ
Š
*cascade08Š
§
 *cascade08§
©
*cascade08©
®
 *cascade08®
¶
*cascade08¶
î
 *cascade08î
ù
*cascade08ù
É *cascade08ÉË*cascade08ËÌ *cascade08ÌÎ*cascade08ÎÏ *cascade08ÏĞ*cascade08ĞÑ *cascade08ÑÒ*cascade08Òá& *cascade08á&â&*cascade08â&ï& *cascade08ï&õ&*cascade08õ&‡' *cascade08‡'ˆ'*cascade08ˆ'Š' *cascade08Š'Œ'*cascade08Œ'' *cascade08'‘'*cascade08‘'•' *cascade08•'—'*cascade08—'™' *cascade08™'š'*cascade08š'²' *cascade08²'¸'*cascade08¸'Ç' *cascade08Ç'á'*cascade08á'ä' *cascade08ä'ğ'*cascade08ğ'( *cascade08(’(*cascade08’(×( *cascade08×(Ù(*cascade08Ù(ì( *cascade08ì(í(*cascade08í(ï( *cascade08ï(ğ(*cascade08ğ(ÿ( *cascade08ÿ(„)*cascade08„)…) *cascade08…)‡)*cascade08‡)‰) *cascade08‰)Š)*cascade08Š)‹) *cascade08‹)Œ)*cascade08Œ)) *cascade08))*cascade08)Ÿ) *cascade08Ÿ) )*cascade08 )¢) *cascade08¢)£)*cascade08£)¤) *cascade08¤)¥)*cascade08¥)ª) *cascade08ª)¬)¬)­) *cascade08­)®)*cascade08®)¯) *cascade08¯)´)´)¶) *cascade08¶)¸)¸)¹) *cascade08¹)Ç)Ç)Õ) *cascade08Õ)Ö)*cascade08Ö)×) *cascade08×)Ø)*cascade08Ø)Ù) *cascade08Ù)á)á)â) *cascade08â)ä)*cascade08ä)æ) *cascade08æ)í)*cascade08í)î) *cascade08î)ğ)ğ)ñ) *cascade08ñ)ô)ô)õ) *cascade08õ)÷)*cascade08÷)„* *cascade08„*…**cascade08…*•* *cascade08•*õ**cascade08õ*û* *cascade08û*‹+*cascade08‹+œ+ *cascade08œ++*cascade08++ *cascade08+ª+*cascade08ª+«+ *cascade08«+­+*cascade08­+®+ *cascade08®+°+*cascade08°+²+ *cascade08²+»+*cascade08»+½+ *cascade08½+Â+*cascade08Â+Ã+ *cascade08Ã+Æ+*cascade08Æ+Õ+ *cascade08Õ+×+*cascade08×+é+ *cascade08é+ì+*cascade08ì+½, *cascade08½,¾,*cascade08¾,ï, *cascade08ï,ñ,*cascade08ñ,û, *cascade08û,ü,*cascade08ü,Œ- *cascade08Œ--*cascade08-«- *cascade08«-­-*cascade08­-è- *cascade08è-é-*cascade08é-—. *cascade08—.™.*cascade08™.¥. *cascade08¥.¦.*cascade08¦.². *cascade08².³.*cascade08³.¿. *cascade08¿.Á.*cascade08Á.²/ *cascade08²/´/*cascade08´/¿/ *cascade08¿/Î/*cascade08Î/º0 *cascade08º0ô0*cascade08ô0­6 *cascade08"(205b1bab434999c48e066e66385ba65f03f104f428file:///root/frontend-naive/src/pages/problemset/_id.vue:file:///root/frontend-naive