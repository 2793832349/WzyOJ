<script setup>
import { ref, watch } from 'vue';
import { Codemirror } from 'vue-codemirror';
import { cpp } from '@codemirror/lang-cpp';
import { python } from '@codemirror/lang-python';
import { oneDark } from '@codemirror/theme-one-dark';
import { indentUnit as cmIndentUnit } from '@codemirror/language';
import store from '@/store';
const extensions = { python3: [python()], cpp: [cpp()], c: [cpp()] };

const emit = defineEmits(['update:code']);
const props = defineProps({
  language: {
    type: String,
    default: 'cpp',
  },
  code: {
    type: String,
    default: '',
  },
  tabSize: {
    type: Number,
    default: 4,
  },
  indentUnit: {
    type: Number,
    default: 4,
  },
  indentWithTab: {
    type: Boolean,
    default: true,
  },
  autofocus: {
    type: Boolean,
    default: true,
  },
});

const _code = ref(props.code);
watch(_code, val => emit('update:code', val));
</script>

<template>
  <codemirror
    v-model="_code"
    placeholder="请输入你的代码..."
    :style="{ height: '600px', fontSize: '16px' }"
    :autofocus="autofocus"
    :indent-with-tab="indentWithTab"
    :tab-size="tabSize"
    :extensions="
      [cmIndentUnit.of(' '.repeat(Math.max(1, props.indentUnit)))].concat(
        extensions[language] ?? [],
        store.getters.theme === 'dark' ? [oneDark] : []
      )
    "
  />
</template>

<style lang="scss" scoped>
:deep(.ͼ1.cm-editor.cm-focused) {
  outline: none;
}

:deep(.ͼ1.cm-editor div),
:deep(.ͼ1.cm-editor span) {
  font-family: 'SourceCodePro';
}
</style>
