<script setup>
import { ref, watch, computed } from 'vue';
import { Codemirror } from 'vue-codemirror';
import { cpp } from '@codemirror/lang-cpp';
import { python } from '@codemirror/lang-python';
import { oneDark } from '@codemirror/theme-one-dark';
import { EditorView } from '@codemirror/view';
import store from '@/store';

const extensions = { python3: [python()], cpp: [cpp()], c: [cpp()] };

const emit = defineEmits(['update:code', 'paste-blocked']);
const props = defineProps({
  language: {
    type: String,
    default: 'cpp',
  },
  code: {
    type: String,
    default: '',
  },
  blockPaste: {
    type: Boolean,
    default: false,
  },
});

const _code = ref(props.code);
watch(_code, val => emit('update:code', val));

// 监听外部 code 变化
watch(() => props.code, val => {
  if (val !== _code.value) {
    _code.value = val;
  }
});

// 创建禁止粘贴的扩展
const pasteBlockExtension = EditorView.domEventHandlers({
  paste(event) {
    if (props.blockPaste) {
      event.preventDefault();
      emit('paste-blocked');
      return true;
    }
    return false;
  },
});

const allExtensions = computed(() => {
  const exts = [...(extensions[props.language] ?? [])];
  if (store.getters.theme === 'dark') {
    exts.push(oneDark);
  }
  if (props.blockPaste) {
    exts.push(pasteBlockExtension);
  }
  return exts;
});
</script>

<template>
  <codemirror
    v-model="_code"
    placeholder="请输入你的代码..."
    :style="{ height: '100%', fontSize: '14px' }"
    :autofocus="true"
    :indent-with-tab="true"
    :tab-size="4"
    :extensions="allExtensions"
  />
</template>

<style lang="scss" scoped>
:deep(.ͼ1.cm-editor.cm-focused) {
  outline: none;
}

:deep(.ͼ1.cm-editor div),
:deep(.ͼ1.cm-editor span) {
  font-family: 'SourceCodePro', 'Consolas', 'Monaco', monospace;
}

:deep(.cm-editor) {
  height: 100%;
}

:deep(.cm-scroller) {
  overflow: auto;
}
</style>
