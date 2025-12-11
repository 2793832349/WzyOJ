»!<template>
  <div v-if="problem">
    <h1>#{{ problem.id }} {{ problem.display_title }}</h1>
    
    <n-space style="margin-bottom: 20px">
      <n-button
        size="small"
        :color="difficultyColor[problem.difficulty || 0]"
        style="cursor: default"
      >
        {{ difficultyMap[problem.difficulty || 0] }}
      </n-button>
      <n-tag type="info">æ—¶é—´é™åˆ¶: {{ problem.time_limit }}ms</n-tag>
      <n-tag type="info">å†…å­˜é™åˆ¶: {{ problem.memory_limit }}MB</n-tag>
      <n-tag type="success">ç­çº§ä¸“å±é¢˜ç›®</n-tag>
    </n-space>

    <n-card title="é¢˜ç›®æè¿°" v-if="problem.description">
      <div style="white-space: pre-wrap">{{ problem.description }}</div>
    </n-card>

    <n-card title="è¾“å…¥æ ¼å¼" v-if="problem.input_format" style="margin-top: 16px">
      <div style="white-space: pre-wrap">{{ problem.input_format }}</div>
    </n-card>

    <n-card title="è¾“å‡ºæ ¼å¼" v-if="problem.output_format" style="margin-top: 16px">
      <div style="white-space: pre-wrap">{{ problem.output_format }}</div>
    </n-card>

    <n-card title="æ ·ä¾‹" v-if="problem.samples && problem.samples.length > 0" style="margin-top: 16px">
      <n-tabs type="line" animated>
        <n-tab-pane
          v-for="(sample, index) in problem.samples"
          :key="index"
          :name="'sample_' + index"
          :tab="'æ ·ä¾‹ #' + (index + 1)"
        >
          <n-grid :cols="2" :x-gap="12">
            <n-gi>
              <h4>è¾“å…¥</h4>
              <n-input
                :value="sample.input"
                type="textarea"
                :rows="10"
                readonly
                style="font-family: monospace"
              />
            </n-gi>
            <n-gi>
              <h4>è¾“å‡º</h4>
              <n-input
                :value="sample.output"
                type="textarea"
                :rows="10"
                readonly
                style="font-family: monospace"
              />
            </n-gi>
          </n-grid>
        </n-tab-pane>
      </n-tabs>
    </n-card>

    <n-card title="æ•°æ®èŒƒå›´" v-if="problem.hint" style="margin-top: 16px">
      <div style="white-space: pre-wrap">{{ problem.hint }}</div>
    </n-card>

    <n-card title="æäº¤ä»£ç " style="margin-top: 16px">
      <n-alert type="info" style="margin-bottom: 16px">
        æç¤ºï¼šç­çº§ä¸“å±é¢˜ç›®çš„æäº¤åŠŸèƒ½æ­£åœ¨å¼€å‘ä¸­ï¼Œè¯·ç¨åå†è¯•ã€‚
      </n-alert>
      
      <n-form label-placement="top">
        <n-form-item label="é€‰æ‹©è¯­è¨€">
          <n-select
            v-model:value="submission.language"
            :options="languageOptions"
            placeholder="è¯·é€‰æ‹©ç¼–ç¨‹è¯­è¨€"
          />
        </n-form-item>
        <n-form-item label="ä»£ç ">
          <n-input
            v-model:value="submission.code"
            type="textarea"
            placeholder="è¯·è¾“å…¥ä»£ç ..."
            :rows="15"
            :disabled="true"
          />
        </n-form-item>
      </n-form>
      
      <n-space>
        <n-button type="primary" disabled>
          æäº¤ï¼ˆå¼€å‘ä¸­ï¼‰
        </n-button>
        <n-button @click="$router.push({ name: 'class_detail', params: { id: classId } })">
          è¿”å›ç­çº§
        </n-button>
      </n-space>
    </n-card>
  </div>
  <div v-else>
    <n-spin size="large" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useMessage } from 'naive-ui';
import Axios from '@/plugins/axios';
import { difficulty as difficultyMap, difficultyColor } from '@/plugins/consts';

const route = useRoute();
const message = useMessage();

const classId = route.params.id;
const problemId = route.params.problemId;
const problem = ref(null);

const submission = ref({
  language: 'cpp',
  code: '',
});

const languageOptions = [
  { label: 'C++', value: 'cpp' },
  { label: 'C', value: 'c' },
  { label: 'Python', value: 'python' },
  { label: 'Java', value: 'java' },
];

// è·å–é¢˜ç›®è¯¦æƒ…
const fetchProblem = () => {
  Axios.get(`class/class-problem/${problemId}/`)
    .then(res => {
      problem.value = res;
    })
    .catch(() => {
      message.error('è·å–é¢˜ç›®è¯¦æƒ…å¤±è´¥');
    });
};

onMounted(() => {
  fetchProblem();
});
</script>
Ÿ	 *cascade08Ÿ	¹	*cascade08¹	º	 *cascade08º	Ù	*cascade08Ù	„
 *cascade08„

*cascade08
›
 *cascade08›
¤
*cascade08¤
¥
 *cascade08¥
ª
*cascade08ª
­
 *cascade08­
°
*cascade08°
±
 *cascade08±
¹
*cascade08¹
»
 *cascade08»
½
*cascade08½
À
 *cascade08À
Á
*cascade08Á
É
 *cascade08É
Ñ
*cascade08Ñ
Ø
 *cascade08Ø
Ü
*cascade08Ü
İ
 *cascade08İ
Ş
*cascade08Ş
ç
 *cascade08ç
ê
*cascade08ê
ë
 *cascade08ë
ò
*cascade08ò
ô
 *cascade08ô
ö
*cascade08ö
 *cascade08*cascade08¨ *cascade08¨©*cascade08©½ *cascade08½¿*cascade08¿À *cascade08ÀÁ*cascade08ÁÊ *cascade08ÊÌ*cascade08ÌÎ *cascade08ÎĞ*cascade08Ğß *cascade08ßô*cascade08ôö *cascade08öú*cascade08úŠ *cascade08Š‘*cascade08‘’ *cascade08’*cascade08¥ *cascade08¥©*cascade08©ª *cascade08ª«*cascade08«¬ *cascade08¬±*cascade08±» *cascade08»Å*cascade08ÅĞ *cascade08ĞÛ*cascade08ÛÜ *cascade08ÜŞ*cascade08Şß *cascade08ßà*cascade08àì *cascade08ìî*cascade08îû *cascade08ûş*cascade08şÿ *cascade08ÿ*cascade08ƒ *cascade08ƒ„*cascade08„… *cascade08…Œ*cascade08Œ *cascade08×*cascade08×à *cascade08àâ*cascade08âä *cascade08äå*cascade08åñ *cascade08ñò*cascade08òõ *cascade08õŠ*cascade08ŠŒ *cascade08Œ*cascade08¡ *cascade08¡¦*cascade08¦§ *cascade08§¼*cascade08¼½ *cascade08½¿*cascade08¿À *cascade08À××Ù *cascade08Ù‡*cascade08‡ˆ *cascade08ˆŠ*cascade08Š‹ *cascade08‹*cascade08‘ *cascade08‘£*cascade08£¤ *cascade08¤²*cascade08²¶ *cascade08¶¸*cascade08¸Ò *cascade08ÒÔ*cascade08Ôä *cascade08äæ*cascade08æè *cascade08è‚*cascade08‚»! *cascade08"(205b1bab434999c48e066e66385ba65f03f104f42;file:///root/frontend-naive/src/pages/class/problem/_id.vue:file:///root/frontend-naive