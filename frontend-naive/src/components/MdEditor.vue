<template>
  <n-card :bordered="false" class="md-editor-card">
    <MdEditor
      :editorId="`md-editor-${id}`"
      class="md-editor-v3"
      v-model="_content"
      katexJs="https://cdn.staticfile.org/KaTeX/0.15.1/katex.min.js"
      katexCss="https://cdn.staticfile.org/KaTeX/0.15.1/katex.min.css"
      highlightJs="https://cdn.staticfile.org/highlight.js/11.2.0/highlight.min.js"
      highlightCss="https://cdn.staticfile.org/highlight.js/10.0.0/styles/atom-one-dark.min.css"
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
    />
  </n-card>
</template>

<script setup>
import MdEditor from 'md-editor-v3';
import 'md-editor-v3/lib/style.css';
import { ref, toRef, watch } from 'vue';
import store from '@/store';

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

MdEditor.config({
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
</style>
