<template>
  <n-card :bordered="false" class="md-editor-card">
    <MdEditor
      :editorId="`md-editor-${id}`"
      class="md-editor-v3"
      v-model="_content"
      katexJs="https://cdn.staticfile.org/KaTeX/0.15.1/katex.min.js"
      katexCss="https://cdn.staticfile.org/KaTeX/0.15.1/katex.min.css"
      noMermaid
      prettierCDN="https://cdn.staticfile.org/prettier/2.0.3/standalone.min.js"
      prettierMDCDN="https://cdn.staticfile.org/prettier/2.0.3/parser-markdown.min.js"
      noCropper
      :toolbars="[
        'revoke',
        'next',
        '-',
        'bold',
        'underline',
        'strikeThrough',
        'quote',
        '-',
        'link',
        'image',
        'katex',
        'codeRow',
        'code',
        '-',
        'preview',
      ]"
      :preview="true"
      :previewOnly="previewOnly"
      :historyLength="20"
      showCodeRowNumber
      :previewTheme="store.state.displaySettings.markdownTheme"
      :theme="store.getters.theme"
      @onUploadImg="handleUploadImg"
    />

    <div v-if="!previewOnly" class="image-host-panel">
      <div class="image-host-tip">支持 Ctrl+V 粘贴、拖拽上传。上传后可复制链接手动粘贴。</div>
      <n-space v-if="uploadedImages.length" vertical size="small" class="image-link-list">
        <div class="image-link-header">
          <span>最近上传</span>
          <n-button size="tiny" tertiary @click="clearUploadedImages">清空</n-button>
        </div>
        <div v-for="item in uploadedImages" :key="item.id" class="image-link-item">
          <div class="image-link-main">
            <div class="image-link-name">{{ item.name }}</div>
            <a :href="item.url" target="_blank" rel="noopener noreferrer">{{ item.url }}</a>
            <div class="image-link-size">{{ item.sizeText }}</div>
          </div>
          <n-space size="small">
            <n-button size="tiny" @click="copyText(item.url)">复制链接</n-button>
            <n-button size="tiny" secondary @click="copyText(`![](${item.url})`)">复制Markdown</n-button>
          </n-space>
        </div>
      </n-space>
    </div>
  </n-card>
</template>

<script setup>
import MdEditor from 'md-editor-v3';
import 'md-editor-v3/lib/style.css';
import { ref, toRef, watch } from 'vue';
import { useMessage } from 'naive-ui';
import store from '@/store';
import Axios from '@/plugins/axios';
import hljs from 'highlight.js/lib/core';
import c from 'highlight.js/lib/languages/c';
import cpp from 'highlight.js/lib/languages/cpp';
import python from 'highlight.js/lib/languages/python';

const mergeCaretRowspanInTables = (html) => {
  if (typeof document === 'undefined') return html;
  if (!html || typeof html !== 'string') return html;

  const container = document.createElement('div');
  container.innerHTML = html;

  let mergedCells = 0;

  const startRowMap = new WeakMap();

  const getColCount = (table) => {
    let max = 0;
    const rows = table.querySelectorAll('tr');
    rows.forEach((tr) => {
      let count = 0;
      tr.querySelectorAll('th,td').forEach((cell) => {
        const colspan = parseInt(cell.getAttribute('colspan') || '1', 10) || 1;
        count += colspan;
      });
      if (count > max) max = count;
    });
    return max;
  };

  const processOneTable = (table) => {
    const colCount = getColCount(table);
    if (!colCount) return;

    const carry = new Array(colCount).fill(null);
    let prevRowCellByCol = new Array(colCount).fill(null);

    const rows = Array.from(table.querySelectorAll('tr'));
    rows.forEach((tr, rowIndex) => {
      const cells = Array.from(tr.querySelectorAll('th,td'));
      const rowCellsByCol = new Array(colCount).fill(null);

      let colPointer = 0;

      const isColOccupiedByCarry = (col) => {
        const entry = carry[col];
        return !!(entry && rowIndex < entry.endRow);
      };

      const setCarryForCell = (cell, startRow, colspan, rowspan) => {
        const endRow = startRow + rowspan;
        for (let k = 0; k < colspan; k++) {
          const col = colPointer + k;
          if (col >= colCount) break;
          carry[col] = { cell, endRow };
        }
      };

      cells.forEach((cell) => {
        while (colPointer < colCount && isColOccupiedByCarry(colPointer)) {
          rowCellsByCol[colPointer] = carry[colPointer].cell;
          colPointer++;
        }
        if (colPointer >= colCount) return;

        const rawText = cell.textContent || '';
        const text = rawText.trim();
        const colspan = parseInt(cell.getAttribute('colspan') || '1', 10) || 1;

        if (text === '^') {
          for (let k = 0; k < colspan; k++) {
            const col = colPointer + k;
            if (col >= colCount) break;
            const above = (carry[col] && rowIndex < carry[col].endRow) ? carry[col].cell : prevRowCellByCol[col];
            if (!above) continue;

            const current = parseInt(above.getAttribute('rowspan') || '1', 10) || 1;
            const next = current + 1;
            above.setAttribute('rowspan', String(next));
            mergedCells += 1;

            if (!startRowMap.has(above)) {
              startRowMap.set(above, Math.max(0, rowIndex - 1));
            }
            const startRow = startRowMap.get(above);
            carry[col] = { cell: above, endRow: startRow + next };
            rowCellsByCol[col] = above;
          }

          cell.remove();
          colPointer += colspan;
          return;
        }

        if (!startRowMap.has(cell)) startRowMap.set(cell, rowIndex);
        for (let k = 0; k < colspan; k++) {
          const col = colPointer + k;
          if (col >= colCount) break;
          rowCellsByCol[col] = cell;
        }

        const rowspan = parseInt(cell.getAttribute('rowspan') || '1', 10) || 1;
        if (rowspan > 1) {
          setCarryForCell(cell, startRowMap.get(cell), colspan, rowspan);
        }

        colPointer += colspan;
      });

      while (colPointer < colCount && isColOccupiedByCarry(colPointer)) {
        rowCellsByCol[colPointer] = carry[colPointer].cell;
        colPointer++;
      }

      prevRowCellByCol = rowCellsByCol;
    });
  };

  container.querySelectorAll('table').forEach(processOneTable);
  return container.innerHTML;
};

hljs.registerLanguage('c', c);
hljs.registerLanguage('cpp', cpp);
hljs.registerLanguage('python', python);
hljs.registerLanguage('python3', python);

const preserveLeadingWhitespaceOnFirstLine = (html) => {
  // md-editor-v3 会对高亮结果做 trim()，先把首行缩进转成 &nbsp;
  return String(html ?? '').replace(/^[ \t]+/, (indent) => (
    indent
      .replace(/ /g, '&nbsp;')
      .replace(/\t/g, '&nbsp;&nbsp;&nbsp;&nbsp;')
  ));
};

if (!hljs.__mdEditorPatched) {
  const rawHighlight = hljs.highlight.bind(hljs);
  const rawHighlightAuto = hljs.highlightAuto.bind(hljs);

  hljs.highlight = (code, options = {}) => {
    const res = rawHighlight(code, options);
    return { ...res, value: preserveLeadingWhitespaceOnFirstLine(res.value) };
  };
  hljs.highlightAuto = (code, languageSubset) => {
    const res = rawHighlightAuto(code, languageSubset);
    return { ...res, value: preserveLeadingWhitespaceOnFirstLine(res.value) };
  };
  hljs.__mdEditorPatched = true;
}

MdEditor.config({
  editorExtensions: {
    highlight: {
      instance: hljs,
    },
  },
  markedRenderer(renderer) {
    const rawTable = renderer.table;
    renderer.table = function (...args) {
      const html = rawTable ? rawTable.apply(this, args) : '';
      return mergeCaretRowspanInTables(html);
    };
    return renderer;
  },
});

const id = parseInt(Math.random() * 100000).toString();

const emit = defineEmits(['update:content']);
const props = defineProps({
  content: {
    type: String,
    default: '',
  },
  previewOnly: {
    type: Boolean,
    default: false,
  },
});

const _content = ref(props.content);
watch(_content, val => emit('update:content', val));
watch(toRef(props, 'content'), val => (_content.value = val));

const message = useMessage();
const uploadedImages = ref([]);

const toAbsoluteUrl = (url) => {
  if (!url || typeof url !== 'string') return '';
  if (/^https?:\/\//i.test(url)) return url;
  if (typeof window === 'undefined') return url;
  return new URL(url, window.location.origin).toString();
};

const formatSize = (size) => {
  const bytes = Number(size || 0);
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
};

const uploadOneImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await Axios.post('/user/upload-image/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return {
    name: res?.name || file.name || 'image',
    url: toAbsoluteUrl(res?.url || ''),
    size: Number(res?.size || file.size || 0),
  };
};

const handleUploadImg = async (files, callback) => {
  const list = Array.isArray(files) ? files : [];
  if (!list.length) {
    if (typeof callback === 'function') callback([]);
    return;
  }

  const uploaded = [];
  for (const file of list) {
    try {
      const item = await uploadOneImage(file);
      if (item.url) {
        uploaded.push({
          id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
          ...item,
          sizeText: formatSize(item.size),
        });
      }
    } catch (e) {
      // axios interceptor handles API error message
    }
  }

  if (uploaded.length) {
    uploadedImages.value = [...uploaded, ...uploadedImages.value].slice(0, 20);
    message.success('图片上传成功，可在下方复制链接');
  }

  if (typeof callback === 'function') callback([]);
};

const copyText = async (text) => {
  if (!text) return;
  try {
    await navigator.clipboard.writeText(text);
    message.success('已复制');
  } catch (e) {
    const input = document.createElement('input');
    input.value = text;
    document.body.appendChild(input);
    input.select();
    document.execCommand('copy');
    document.body.removeChild(input);
    message.success('已复制');
  }
};

const clearUploadedImages = () => {
  uploadedImages.value = [];
};
</script>

<style lang="scss" scoped>
.md-editor-v3 {
  background-color: var(--n-color);
  color: var(--n-text-color);
  border-radius: var(--n-border-radius);
  transition: color 0.3s var(--n-bezier), background-color 0.3s var(--n-bezier),
    box-shadow 0.3s var(--n-bezier), border-color 0.3s var(--n-bezier);
}

:deep(.md-editor-v3 .md-preview) {
  div,
  h1,
  h2,
  h3,
  h4,
  h5,
  h6,
  p,
  a,
  strong {
    color: var(--n-text-color) !important;
  }
}

.md-editor-v3 :deep(img) {
  max-width: 70% !important;
  margin: 0 auto !important;
}

.md-editor-v3 :deep(pre code),
.md-editor-v3 :deep(.md-editor-scrn pre code),
.md-editor-v3 :deep(pre code span),
.md-editor-v3 :deep(pre code span[rn-wrapper]) {
  white-space: pre !important;
}

@media (max-width: 768px) {
  .md-editor-v3 :deep(img) {
    max-width: 100% !important;
  }
}

.n-card.md-editor-card :deep(.n-card__content) {
  margin: 0 !important;
  padding: 0 !important;
}

:deep(.github-theme) {
  margin-top: 10px !important;
}

.image-host-panel {
  border-top: 1px dashed var(--n-border-color);
  padding: 12px 14px 14px;
}

.image-host-tip {
  font-size: 12px;
  color: var(--n-text-color-3);
}

.image-link-list {
  margin-top: 10px;
}

.image-link-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
  font-weight: 600;
}

.image-link-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border: 1px solid var(--n-border-color);
  border-radius: 8px;
  padding: 8px 10px;
}

.image-link-main {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.image-link-name {
  font-size: 12px;
  color: var(--n-text-color-3);
}

.image-link-main a {
  color: var(--n-primary-color);
  text-decoration: none;
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 620px;
}

.image-link-size {
  font-size: 12px;
  color: var(--n-text-color-3);
}
</style>
