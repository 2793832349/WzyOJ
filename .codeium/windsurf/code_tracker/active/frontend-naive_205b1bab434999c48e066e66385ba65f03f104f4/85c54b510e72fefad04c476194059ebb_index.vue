Ö/<template>
  <div>
    <h1>
      <n-space align="center" size="large">
        <span>æˆ‘çš„ç­çº§</span>
        <n-button type="primary" @click="showCreateModal = true" v-if="canCreateClass">
          åˆ›å»ºç­çº§
        </n-button>
      </n-space>
    </h1>

    <n-tabs type="line" animated v-model:value="activeTab">
      <n-tab-pane v-if="teachingClasses.length > 0" name="teaching" tab="æˆ‘åˆ›å»ºçš„ç­çº§">
        <n-space vertical>
          <n-card
            v-for="cls in teachingClasses"
            :key="cls.id"
            hoverable
            @click="$router.push({ name: 'class_detail', params: { id: cls.id } })"
            style="cursor: pointer"
          >
            <template #header>
              <n-space align="center">
                <n-text strong style="font-size: 18px">{{ cls.title }}</n-text>
                <n-tag v-if="cls.is_hidden" type="warning" size="small">éšè—</n-tag>
              </n-space>
            </template>
            <n-space>
              <n-text depth="3">æ•™å¸ˆï¼š</n-text>
              <n-text>{{ cls.teacher.username }}</n-text>
              <n-divider vertical />
              <n-text depth="3">å­¦ç”Ÿæ•°ï¼š</n-text>
              <n-text>{{ cls.student_count }}</n-text>
              <n-divider vertical />
              <n-text depth="3">é¢˜ç›®æ•°ï¼š</n-text>
              <n-text>{{ cls.problem_count }}</n-text>
              <n-divider vertical />
              <n-text depth="3">ä½œä¸šæ•°ï¼š</n-text>
              <n-text>{{ cls.assignment_count }}</n-text>
            </n-space>
            <n-text v-if="cls.description" depth="3" style="margin-top: 12px; display: block">
              {{ cls.description }}
            </n-text>
          </n-card>
          <n-empty v-if="teachingClasses.length === 0" description="æš‚æ— ç­çº§" />
        </n-space>
      </n-tab-pane>

      <n-tab-pane name="joined" tab="æˆ‘åŠ å…¥çš„ç­çº§">
        <n-space vertical>
          <n-card
            v-for="cls in joinedClasses"
            :key="cls.id"
            hoverable
            @click="$router.push({ name: 'class_detail', params: { id: cls.id } })"
            style="cursor: pointer"
          >
            <template #header>
              <n-text strong style="font-size: 18px">{{ cls.title }}</n-text>
            </template>
            <n-space>
              <n-text depth="3">æ•™å¸ˆï¼š</n-text>
              <n-text>{{ cls.teacher.username }}</n-text>
              <n-divider vertical />
              <n-text depth="3">å­¦ç”Ÿæ•°ï¼š</n-text>
              <n-text>{{ cls.student_count }}</n-text>
              <n-divider vertical />
              <n-text depth="3">é¢˜ç›®æ•°ï¼š</n-text>
              <n-text>{{ cls.problem_count }}</n-text>
              <n-divider vertical />
              <n-text depth="3">ä½œä¸šæ•°ï¼š</n-text>
              <n-text>{{ cls.assignment_count }}</n-text>
            </n-space>
            <n-text v-if="cls.description" depth="3" style="margin-top: 12px; display: block">
              {{ cls.description }}
            </n-text>
          </n-card>
          <n-empty v-if="joinedClasses.length === 0" description="æš‚æœªåŠ å…¥ä»»ä½•ç­çº§" />
        </n-space>
      </n-tab-pane>
    </n-tabs>

    <!-- åˆ›å»ºç­çº§å¯¹è¯æ¡† -->
    <n-modal v-model:show="showCreateModal" preset="dialog" title="åˆ›å»ºç­çº§">
      <n-form :model="newClass" label-placement="left" label-width="80">
        <n-form-item label="ç­çº§åç§°" required>
          <n-input v-model:value="newClass.title" placeholder="è¯·è¾“å…¥ç­çº§åç§°" />
        </n-form-item>
        <n-form-item label="ç­çº§æè¿°">
          <n-input
            v-model:value="newClass.description"
            type="textarea"
            placeholder="è¯·è¾“å…¥ç­çº§æè¿°"
            :rows="3"
          />
        </n-form-item>
        <n-form-item label="æ˜¯å¦éšè—">
          <n-switch v-model:value="newClass.is_hidden" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="showCreateModal = false">å–æ¶ˆ</n-button>
          <n-button type="primary" @click="createClass" :loading="creating">
            åˆ›å»º
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useMessage } from 'naive-ui';
import Axios from '@/plugins/axios';

const message = useMessage();

const classes = ref([]);
const showCreateModal = ref(false);
const creating = ref(false);
const activeTab = ref('joined'); // é»˜è®¤é€‰ä¸­"æˆ‘åŠ å…¥çš„ç­çº§"
const newClass = ref({
  title: '',
  description: '',
  is_hidden: false,
});

// æˆ‘æ•™çš„ç­çº§
const teachingClasses = computed(() => {
  return classes.value.filter(cls => cls.user_role === 'teacher');
});

// æˆ‘åŠ å…¥çš„ç­çº§
const joinedClasses = computed(() => {
  return classes.value.filter(cls => cls.user_role === 'student');
});

// æ˜¯å¦å¯ä»¥åˆ›å»ºç­çº§ï¼ˆä»»ä½•ç™»å½•ç”¨æˆ·éƒ½å¯ä»¥ï¼‰
const canCreateClass = ref(true);

// è·å–ç­çº§åˆ—è¡¨
const fetchClasses = () => {
  Axios.get('class/class/')
    .then(res => {
      classes.value = res;
      // å¦‚æœæœ‰æ•™å¸ˆç­çº§ï¼Œé»˜è®¤é€‰ä¸­"æˆ‘åˆ›å»ºçš„ç­çº§"
      const hasTeachingClasses = res.some(cls => cls.user_role === 'teacher');
      if (hasTeachingClasses) {
        activeTab.value = 'teaching';
      }
    })
    .catch(() => {
      message.error('è·å–ç­çº§åˆ—è¡¨å¤±è´¥');
    });
};

// åˆ›å»ºç­çº§
const createClass = () => {
  if (!newClass.value.title) {
    message.warning('è¯·è¾“å…¥ç­çº§åç§°');
    return;
  }

  creating.value = true;
  Axios.post('class/class/', newClass.value)
    .then(() => {
      message.success('åˆ›å»ºæˆåŠŸ');
      showCreateModal.value = false;
      newClass.value = {
        title: '',
        description: '',
        is_hidden: false,
      };
      fetchClasses();
    })
    .catch(() => {
      message.error('åˆ›å»ºå¤±è´¥');
    })
    .finally(() => {
      creating.value = false;
    });
};

onMounted(() => {
  fetchClasses();
});
</script>
© *cascade08©Ã*cascade08Ã× *cascade08×ù*cascade08ù‘ *cascade08‘—*cascade08—¯ *cascade08¯·*cascade08·¸ *cascade08¸¼*cascade08¼Ë *cascade08ËÛ*cascade08Ûú *cascade08ú†*cascade08†¢ *cascade08¢¤*cascade08¤¥ *cascade08¥¦*cascade08¦§ *cascade08§©*cascade08©· *cascade08·¸*cascade08¸» *cascade08»½*cascade08½¿ *cascade08¿À*cascade08ÀÆ *cascade08ÆÌ*cascade08Ìü *cascade08üı*cascade08ı‹ *cascade08‹™*cascade08™š *cascade08š£*cascade08£ª *cascade08ª³*cascade08³´ *cascade08´¼*cascade08¼½ *cascade08½À*cascade08ÀÁ *cascade08ÁÃ*cascade08ÃÅ *cascade08ÅÍ*cascade08ÍÜ *cascade08Ü*cascade08† *cascade08†*cascade08‘ *cascade08‘•*cascade08•– *cascade08–˜*cascade08˜™ *cascade08™Ÿ*cascade08Ÿ  *cascade08 °*cascade08°± *cascade08±´*cascade08´µ *cascade08µ½*cascade08½¾ *cascade08¾Ã*cascade08Ãÿ *cascade08ÿŒ*cascade08ŒÙ *cascade08Ùï*cascade08ïò *cascade08òô*cascade08ôö *cascade08ö÷*cascade08÷ı *cascade08ı*cascade08 *cascade08”*cascade08”¦ *cascade08¦«*cascade08«É *cascade08ÉÎ*cascade08Î…	 *cascade08…	”	*cascade08”	¡	 *cascade08¡	Á	*cascade08Á	Û	 *cascade08Û	à	*cascade08à	•
 *cascade08•
œ
*cascade08œ

 *cascade08
Ÿ
*cascade08Ÿ
 
 *cascade08 
¦
*cascade08¦
³
 *cascade08³
Ó
*cascade08Ó
í
 *cascade08í
ò
*cascade08ò
§ *cascade08§®*cascade08®¯ *cascade08¯±*cascade08±² *cascade08²¸*cascade08¸Å *cascade08Åå*cascade08å *cascade08™*cascade08™œ *cascade08œ*cascade08¬ *cascade08¬³*cascade08³´ *cascade08´Ê*cascade08ÊË *cascade08ËÖ*cascade08Ö× *cascade08×Ù*cascade08ÙÚ *cascade08ÚÜ*cascade08Üİ *cascade08İñ*cascade08ñô *cascade08ôı*cascade08ı´ *cascade08´·*cascade08·Ç *cascade08ÇË*cascade08Ë¯ *cascade08¯³*cascade08³ *cascade08˜*cascade08˜™ *cascade08™*cascade08¬ *cascade08¬¼*cascade08¼Ù *cascade08Ùå*cascade08å *cascade08ƒ*cascade08ƒ„ *cascade08„…*cascade08…† *cascade08†ˆ*cascade08ˆ– *cascade08–Ÿ*cascade08Ÿ¥ *cascade08¥«*cascade08«Û *cascade08ÛÜ*cascade08Üê *cascade08êø*cascade08øù *cascade08ù‚*cascade08‚ˆ *cascade08ˆ›*cascade08›œ *cascade08œŸ*cascade08Ÿ  *cascade08 ¢*cascade08¢¤ *cascade08¤¬*cascade08¬¼ *cascade08¼Å*cascade08ÅÇ *cascade08ÇË*cascade08ËÌ *cascade08ÌÎ*cascade08ÎÏ *cascade08ÏÕ*cascade08ÕÖ *cascade08Öæ*cascade08æç *cascade08çê*cascade08êë *cascade08ëó*cascade08óô *cascade08ôù*cascade08ùŸ *cascade08Ÿµ*cascade08µ¸ *cascade08¸º*cascade08º¼ *cascade08¼½*cascade08½Ã *cascade08ÃÔ*cascade08ÔÕ *cascade08ÕÚ*cascade08Úì *cascade08ìñ*cascade08ñ *cascade08”*cascade08”É *cascade08ÉĞ*cascade08ĞÑ *cascade08ÑÓ*cascade08ÓÔ *cascade08ÔÚ*cascade08Úç *cascade08ç‡*cascade08‡¡ *cascade08¡¦*cascade08¦İ *cascade08İì*cascade08ìù *cascade08ù™*cascade08™³ *cascade08³¸*cascade08¸ï *cascade08ïş*cascade08ş‹ *cascade08‹«*cascade08«Ç *cascade08Çß*cascade08ßâ *cascade08âä*cascade08äò *cascade08òù*cascade08ùú *cascade08ú*cascade08‘ *cascade08‘”*cascade08”• *cascade08•Ÿ*cascade08Ÿ  *cascade08 ¢*cascade08¢£ *cascade08£·*cascade08·º *cascade08ºÃ*cascade08Ãú *cascade08úı*cascade08ı *cascade08‘*cascade08‘ÿ *cascade08ÿƒ*cascade08ƒÈ# *cascade08È#$$Á( *cascade08Á( **cascade08 *Ö/ *cascade08"(205b1bab434999c48e066e66385ba65f03f104f425file:///root/frontend-naive/src/pages/class/index.vue:file:///root/frontend-naive