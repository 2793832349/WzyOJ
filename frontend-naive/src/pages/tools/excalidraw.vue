<script setup>
import { computed, markRaw, nextTick, ref, shallowRef } from 'vue';
import { GlobalWorkerOptions, getDocument } from 'pdfjs-dist/legacy/build/pdf';
import pdfWorkerUrl from 'pdfjs-dist/legacy/build/pdf.worker.min.js?url';

GlobalWorkerOptions.workerSrc = pdfWorkerUrl;

const message = useMessage();

const pdfFile = ref(null);
const pdfDoc = shallowRef(null);
const pageCount = ref(0);
const page = ref(1);
const scale = ref(1.25);
const rendering = ref(false);

const canvasRef = ref(null);

const canPrev = computed(() => page.value > 1);
const canNext = computed(() => page.value < pageCount.value);

const loadPdfFromFile = async (file) => {
  const buf = await file.arrayBuffer();
  const task = getDocument({ data: buf, disableWorker: true });
  const doc = await task.promise;
  // pdf.js 对象包含 JS 私有字段，不能被 Vue 包装成 Proxy
  pdfDoc.value = markRaw(doc);
  pageCount.value = doc.numPages;
  page.value = 1;
  await nextTick();
  await renderPage();
};

const onPdfChange = async ({ file }) => {
  const raw = file?.file;
  if (!raw) return;
  if (!raw.name?.toLowerCase().endsWith('.pdf')) {
    message.error('请上传 PDF 文件');
    return;
  }
  pdfFile.value = raw;
  try {
    await loadPdfFromFile(raw);
    message.success('PDF 加载成功');
  } catch (e) {
    message.error('PDF 加载失败');
  }
};

const renderPage = async () => {
  if (!pdfDoc.value) return;
  const canvas = canvasRef.value;
  if (!canvas) return;
  rendering.value = true;
  try {
    const pdfPage = await pdfDoc.value.getPage(page.value);
    const viewport = pdfPage.getViewport({ scale: scale.value });
    const ctx = canvas.getContext('2d');
    canvas.width = Math.floor(viewport.width);
    canvas.height = Math.floor(viewport.height);
    await pdfPage.render({ canvasContext: ctx, viewport }).promise;
  } catch (e) {
    // eslint-disable-next-line no-console
    console.error('pdf render failed', e);
    message.error('渲染失败');
  } finally {
    rendering.value = false;
  }
};

const prevPage = async () => {
  if (!canPrev.value) return;
  page.value -= 1;
  await nextTick();
  await renderPage();
};

const nextPage = async () => {
  if (!canNext.value) return;
  page.value += 1;
  await nextTick();
  await renderPage();
};

const onScaleChange = async () => {
  await nextTick();
  await renderPage();
};

const canvasToBlob = () => {
  const canvas = canvasRef.value;
  if (!canvas) return Promise.resolve(null);
  return new Promise((resolve) => {
    canvas.toBlob((blob) => resolve(blob), 'image/png');
  });
};

const downloadCurrentPage = async () => {
  const blob = await canvasToBlob();
  if (!blob) {
    message.error('没有可下载的内容');
    return;
  }
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  const baseName = (pdfFile.value?.name || 'pdf').replace(/\.pdf$/i, '');
  a.download = `${baseName}-p${page.value}.png`;
  a.click();
  URL.revokeObjectURL(url);
};

const copyCurrentPageToClipboard = async () => {
  const blob = await canvasToBlob();
  if (!blob) {
    message.error('没有可复制的内容');
    return;
  }
  try {
    if (!window.isSecureContext) {
      message.error('当前环境不支持剪贴板写入：需要 HTTPS 或 localhost，请使用下载 PNG 方案');
      await downloadCurrentPage();
      return;
    }
    if (typeof ClipboardItem === 'undefined' || !navigator.clipboard?.write) {
      message.error('当前浏览器不支持剪贴板写入，请使用下载 PNG 方案');
      await downloadCurrentPage();
      return;
    }
    const item = new ClipboardItem({ 'image/png': blob });
    await navigator.clipboard.write([item]);
    message.success('已复制为图片：切到右侧画板 Ctrl+V 粘贴');
  } catch (e) {
    message.error('复制失败（可能需要 HTTPS/localhost 权限），已为你准备下载 PNG');
    await downloadCurrentPage();
  }
};
</script>

<template>
  <n-card>
    <n-space justify="space-between" align="center">
      <div style="font-size: 18px; font-weight: 600">画板（Excalidraw）</div>
      <n-button tag="a" href="https://excalidraw.com" target="_blank" tertiary>
        新窗口打开
      </n-button>
    </n-space>

    <n-space vertical style="margin-top: 12px">
      <n-card size="small" title="PDF -> 图片（复制到画板）">
        <n-space vertical>
          <n-upload
            :max="1"
            accept="application/pdf"
            :default-upload="false"
            @change="onPdfChange"
          >
            <n-button>选择 PDF</n-button>
          </n-upload>

          <n-space align="center" justify="space-between">
            <n-space align="center">
              <n-button size="small" :disabled="!pdfDoc || rendering || !canPrev" @click="prevPage">
                上一页
              </n-button>
              <n-button size="small" :disabled="!pdfDoc || rendering || !canNext" @click="nextPage">
                下一页
              </n-button>
              <n-text depth="3" v-if="pdfDoc">{{ page }} / {{ pageCount }}</n-text>
            </n-space>
            <n-space align="center">
              <n-text depth="3">缩放</n-text>
              <n-slider
                style="width: 140px"
                v-model:value="scale"
                :min="0.5"
                :max="2.5"
                :step="0.05"
                :disabled="!pdfDoc || rendering"
                @update:value="onScaleChange"
              />
            </n-space>
          </n-space>

          <n-space>
            <n-button size="small" type="primary" :disabled="!pdfDoc || rendering" @click="copyCurrentPageToClipboard">
              复制当前页到剪贴板
            </n-button>
            <n-button size="small" :disabled="!pdfDoc || rendering" @click="downloadCurrentPage">
              下载 PNG
            </n-button>
          </n-space>

          <n-alert type="info" :bordered="false">
            说明：Excalidraw 不支持直接导入 PDF。
            你可以在此处上传 PDF，把某一页复制为图片，然后在下方画板里 Ctrl+V 粘贴进行标注。
          </n-alert>

          <n-spin :show="rendering">
            <div style="max-height: 40vh; overflow: auto; border: 1px solid rgba(0,0,0,0.08); border-radius: 8px; padding: 8px">
              <canvas ref="canvasRef" style="max-width: 100%; display: block; margin: 0 auto" />
            </div>
          </n-spin>
        </n-space>
      </n-card>

      <div style="height: 75vh">
        <iframe
          src="https://excalidraw.com"
          style="width: 100%; height: 100%; border: 0; border-radius: 8px"
          allow="clipboard-read; clipboard-write"
        />
      </div>
    </n-space>
  </n-card>
</template>
