Ä<script setup>
import { h, computed } from 'vue';
import router from '@/router';
import store from '@/store';
import { NButton, NTime, NPopover, NSpace } from 'naive-ui';
import { CheckCircleTwotone } from '@vicons/antd';
import { judgeStatus } from '@/plugins/consts';
import { RouterLink } from 'vue-router';

const props = defineProps({
  data: {
    type: Object,
    default: {},
  },
  loading: {
    type: Boolean,
    default: false,
  },
  isProblemSet: {
    type: Boolean,
    default: false,
  },
});

// è·å–èµ›åˆ¶ç±»å‹
const getRuleType = () => {
  return props.data.rule_type || 'IOI';
};

// åŠ¨æ€ç”Ÿæˆåˆ—é…ç½®
const getColumns = () => {
  const baseColumns = [
    {
      title: 'åæ¬¡',
      render(row, index) {
        return `# ${index + 1}`;
      },
      width: 100,
    },
    {
      title: 'ç”¨æˆ·',
      render(row) {
        return h(
          RouterLink,
          { to: { name: 'user_detail', params: { id: row.id } } },
          {
            default: () =>
              h(
                NButton,
                {
                  text: true,
                  size: 'small',
                },
                { default: () => row.username }
              ),
          }
        );
      },
    },
    {
      title() {
        const ruleType = getRuleType();
        if (props.isProblemSet) return 'ACæ•°é‡';
        if (ruleType === 'ACM') return 'ACæ•°';
        return 'æ€»åˆ†';
      },
      render(row) {
        const ruleType = getRuleType();
        if (props.isProblemSet && row.ac_count !== undefined) {
          return `${row.ac_count} é¢˜`;
        }
        if (ruleType === 'ACM') {
          return `${row.ac_count || 0} é¢˜`;
        }
        return row.score;
      },
    },
  ];

  // åªåœ¨ ACM æ¯”èµ›æ¨¡å¼ï¼ˆéé¢˜å•ï¼‰æ˜¾ç¤ºç½šæ—¶åˆ—
  const ruleType = getRuleType();
  if (ruleType === 'ACM' && !props.isProblemSet) {
    baseColumns.push({
      title: 'ç½šæ—¶',
      render(row) {
        return `${row.penalty || 0} åˆ†é’Ÿ`;
      },
    });
  }

  // æ·»åŠ "æäº¤è¿‡çš„é¢˜ç›®"åˆ—
  baseColumns.push({
    title: 'æäº¤è¿‡çš„é¢˜ç›®',
    render(row) {
      return h(
        'div',
        { style: 'display: flex; flex-wrap: wrap; gap: 8px; max-width: 600px;' },
        row.problems.map(item => 
          h(
            NPopover,
            {
              trigger: 'hover',
            },
            {
              trigger: () =>
                h(
                  RouterLink,
                  {
                    to: {
                      name: 'submission_detail',
                      params: { id: item.submission_id },
                    },
                  },
                  h(
                    NButton,
                    {
                      size: 'small',
                      color: judgeStatus.getColorClass(item.status),
                    },
                    { default: () => item.title }
                  )
                ),
              default: () => [
                `åˆ†æ•°ï¼š${item.score}`,
                h('br'),
                `çŠ¶æ€ï¼š${judgeStatus.getDisplay(item.status)}`,
                h('br'),
                'æ—¶é—´ï¼š',
                h(NTime, {
                  time: Number(new Date(item.time)),
                }),
              ],
            }
          )
        )
      );
    },
  });

  return baseColumns;
};

const columns = computed(() => getColumns());
</script>

<template>
  <n-spin :show="loading">
    <n-data-table :columns="columns" :data="data.users" :bordered="false" />
  </n-spin>
</template>

<style lang="scss" scoped>
:deep(a) {
  text-decoration: none;
}
</style>
 #*cascade08	#‚ ‚à*cascade08àù*cascade08
ùÿ ÿ–*cascade08
–˜ ˜¢*cascade08
¢¬ ¬®*cascade08
®¶ ¶¸*cascade08
¸É ÉË*cascade08
Ëä äæ*cascade08
æ‰ ‰‹*cascade08
‹ *cascade08
   ¢*cascade08
¢© ©«*cascade08
«­ ­¯*cascade08
¯Ä ÄÆ*cascade08
ÆŞ Şà*cascade08
àê êì*cascade08
ì€ €*cascade08
‰ ‰Š*cascade08
ŠË ËÍ*cascade08
ÍÏ ÏÑ*cascade08
Ñê êë*cascade08
ë÷ ÷ø*cascade08
øû ûı*cascade08
ı” ”–*cascade08
–¶ ¶¸*cascade08
¸Ä ÄÆ*cascade08
Æå åç*cascade08
ç†	 †	ˆ	*cascade08
ˆ	´	 ´	¶	*cascade08
¶	¹	 ¹	º	*cascade08
º	Â	 Â	Ã	*cascade08
Ã	Å	 Å	Ç	*cascade08
Ç	Ô	 Ô	Ö	*cascade08
Ö	Ù	 Ù	Ú	*cascade08
Ú	Ü	 Ü	İ	*cascade08
İ	à	 à	â	*cascade08
â	æ	 æ	è	*cascade08
è	ñ	 ñ	ö	 *cascade08ö	÷	*cascade08÷	ú	 *cascade08
ú	û	 û	ı	 *cascade08ı	ş	*cascade08ş	
 *cascade08
 
*cascade08 
ª
 *cascade08
ª
¼
 ¼
½
*cascade08
½
¾
 ¾
Ä
*cascade08
Ä
Ï
 Ï
Ñ
*cascade08
Ñ
Ò
 Ò
×
 *cascade08×
Ù
*cascade08Ù
 *cascade08‚*cascade08‚ˆ *cascade08ˆ‰*cascade08‰ *cascade08
˜ ˜ *cascade08 *cascade08 ¡ *cascade08
¡£ £¥*cascade08
¥½ ½¿*cascade08¿ß *cascade08ßá*cascade08áç *cascade08
çŸ Ÿ¡*cascade08
¡Í ÍÏ*cascade08
ÏÑ ÑÓ*cascade08
ÓÙ Ùó *cascade08óõ*cascade08õ¦ *cascade08¦¨*cascade08¨ª *cascade08ª¬*cascade08¬² *cascade08
²Â ÂÈ *cascade08ÈÊ*cascade08ÊÍ *cascade08ÍÏ*cascade08ÏÖ *cascade08ÖÙ*cascade08ÙÜ *cascade08ÜŞ*cascade08Şß *cascade08ßå*cascade08åæ *cascade08æé*cascade08éê *cascade08ê‹*cascade08‹‘ *cascade08‘”*cascade08”î *cascade08î°*cascade08°à *cascade08àá*cascade08áæ *cascade08æè*cascade08èñ *cascade08ñ“*cascade08“” *cascade08”—*cascade08—› *cascade08›œ*cascade08œ *cascade08Ÿ*cascade08Ÿ¥*cascade08
¥ò ò÷*cascade08
÷ƒ ƒ‰*cascade08
‰Š Š‹*cascade08
‹Œ Œ*cascade08
‘ ‘’*cascade08
’” ”™*cascade08
™š š¤*cascade08
¤¥ ¥ª*cascade08
ª« «¯*cascade08
¯° °´*cascade08
´µ µ¼*cascade08
¼½ ½¿*cascade08
¿À ÀÇ*cascade08
ÇÈ ÈÊ*cascade08
Êà àâ*cascade08
âä äè*cascade08
èé éë*cascade08
ëì ìí*cascade08
í— —´*cascade08
´µ µÅ *cascade08ÅÔ*cascade08Ôß *cascade08ßà*cascade08àá *cascade08
áÄ "(6b457f522aa10499b55789fae01ec35627afe7b62;file:///root/frontend-naive/src/components/RankingTable.vue:file:///root/frontend-naive