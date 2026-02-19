<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useMessage } from 'naive-ui';
import Axios from '@/plugins/axios';
import MdEditor from '@/components/MdEditor.vue';

const route = useRoute();
const router = useRouter();
const message = useMessage();
const bookId = route.params.id;
const isEdit = computed(() => !!bookId);

const loading = ref(false);
const saving = ref(false);

const form = ref({
  title: '',
  description: '',
  difficulty: 'beginner',
  tags: [],
  is_published: false,
  is_free: true,
  order: 0,
});

const chapters = ref([]);
const loadingChapters = ref(false);

const difficultyOptions = [
  { label: '入门', value: 'beginner' },
  { label: '简单', value: 'easy' },
  { label: '中等', value: 'medium' },
  { label: '困难', value: 'hard' },
];

const PAYMENT_NOTE_PREFIX = 'PAYREQ:';
const paymentRequests = ref([]);
const loadingPaymentRequests = ref(false);
const processingPaymentRequestId = ref(null);
const paymentStatusMap = {
  pending: { label: '待确认', type: 'warning' },
  activated: { label: '已开通', type: 'success' },
  rejected: { label: '已驳回', type: 'error' },
};

const loadBook = async () => {
  if (!bookId) return;
  loading.value = true;
  try {
    const res = await Axios.get(`/book/books/${bookId}/`);
    form.value = {
      title: res.title,
      description: res.description,
      difficulty: res.difficulty,
      tags: res.tags || [],
      is_published: res.is_published,
      is_free: res.is_free,
      order: res.order || 0,
    };
    // 加载章节
    loadChapters();
  } catch (err) {
    message.error('加载书籍失败');
  } finally {
    loading.value = false;
  }
};

const loadChapters = async () => {
  if (!bookId) return;
  loadingChapters.value = true;
  try {
    const res = await Axios.get('/book/chapters/', { params: { book_id: bookId } });
    chapters.value = res.results || res;
  } catch (err) {
    console.error('Load chapters error:', err);
  } finally {
    loadingChapters.value = false;
  }
};

const save = async () => {
  if (!form.value.title) {
    message.warning('请输入书籍标题');
    return;
  }
  saving.value = true;
  try {
    if (isEdit.value) {
      await Axios.put(`/book/books/${bookId}/`, form.value);
      message.success('保存成功');
    } else {
      const res = await Axios.post('/book/books/', form.value);
      message.success('创建成功');
      router.push({ name: 'book_edit', params: { id: res.id } });
    }
  } catch (err) {
    message.error(err.response?.data?.detail || '保存失败');
  } finally {
    saving.value = false;
  }
};

const deleteBook = async () => {
  if (!confirm('确定要删除这本书吗？所有章节和小节都会被删除！')) return;
  try {
    await Axios.delete(`/book/books/${bookId}/`);
    message.success('删除成功');
    router.push({ name: 'book_list' });
  } catch (err) {
    message.error('删除失败');
  }
};

// 章节管理
const showChapterModal = ref(false);
const editingChapter = ref(null);
const chapterForm = ref({ title: '', description: '', order: 0 });

const openAddChapter = () => {
  editingChapter.value = null;
  chapterForm.value = { title: '', description: '', order: chapters.value.length + 1 };
  showChapterModal.value = true;
};

const openEditChapter = (chapter) => {
  editingChapter.value = chapter;
  chapterForm.value = { 
    title: chapter.title, 
    description: chapter.description, 
    order: chapter.order 
  };
  showChapterModal.value = true;
};

const saveChapter = async () => {
  if (!chapterForm.value.title) {
    message.warning('请输入章节标题');
    return;
  }
  try {
    if (editingChapter.value) {
      await Axios.put(`/book/chapters/${editingChapter.value.id}/`, {
        ...chapterForm.value,
        book: bookId,
      });
      message.success('章节已更新');
    } else {
      await Axios.post('/book/chapters/', {
        ...chapterForm.value,
        book: bookId,
      });
      message.success('章节已添加');
    }
    showChapterModal.value = false;
    loadChapters();
  } catch (err) {
    message.error('保存章节失败');
  }
};

const deleteChapter = async (chapter) => {
  if (!confirm(`确定要删除章节"${chapter.title}"吗？所有小节都会被删除！`)) return;
  try {
    await Axios.delete(`/book/chapters/${chapter.id}/`);
    message.success('章节已删除');
    loadChapters();
  } catch (err) {
    message.error('删除失败');
  }
};

const goToEditSection = (chapterId) => {
  router.push({ name: 'book_chapter_edit', params: { id: bookId, chapterId } });
};

// 兑换码管理
const redeemCodes = ref([]);
const loadingCodes = ref(false);
const showCodeModal = ref(false);
const codeForm = ref({ count: 1, max_uses: 1, note: '' });
const generatingCodes = ref(false);
const generatedCodes = ref([]);

const loadRedeemCodes = async () => {
  if (!bookId) return;
  loadingCodes.value = true;
  try {
    const res = await Axios.get('/book/redeem-codes/', { params: { book_id: bookId } });
    const allCodes = res.results || res;
    redeemCodes.value = allCodes.filter(item => !String(item.note || '').startsWith(PAYMENT_NOTE_PREFIX));
  } catch (err) {
    console.error('Load redeem codes error:', err);
  } finally {
    loadingCodes.value = false;
  }
};

const openGenerateCodeModal = () => {
  codeForm.value = { count: 1, max_uses: 1, note: '' };
  generatedCodes.value = [];
  showCodeModal.value = true;
};

const generateCodes = async () => {
  generatingCodes.value = true;
  try {
    const res = await Axios.post('/book/redeem-codes/generate/', {
      book_id: bookId,
      count: codeForm.value.count,
      max_uses: codeForm.value.max_uses,
      note: codeForm.value.note,
    });
    generatedCodes.value = res.codes;
    message.success(`成功生成 ${res.count} 个兑换码`);
    loadRedeemCodes();
  } catch (err) {
    message.error('生成兑换码失败');
  } finally {
    generatingCodes.value = false;
  }
};

const deleteRedeemCode = async (code) => {
  if (!confirm(`确定要删除兑换码 ${code.code} 吗？`)) return;
  try {
    await Axios.delete(`/book/redeem-codes/${code.id}/`);
    message.success('兑换码已删除');
    loadRedeemCodes();
  } catch (err) {
    message.error('删除失败');
  }
};

const copyCode = (code) => {
  navigator.clipboard.writeText(code);
  message.success('已复制到剪贴板');
};


const parsePaymentPayload = (note) => {
  const text = String(note || '');
  if (!text.startsWith(PAYMENT_NOTE_PREFIX)) {
    return null;
  }
  try {
    const payload = JSON.parse(text.slice(PAYMENT_NOTE_PREFIX.length));
    return payload && typeof payload === 'object' ? payload : null;
  } catch (e) {
    return null;
  }
};

const getPaymentRequestStatus = (request) => {
  const payload = parsePaymentPayload(request.note) || {};
  let status = String(payload.status || '').trim();

  if (!status) {
    status = request.used_count > 0 ? 'activated' : 'pending';
  }

  if (status === 'paid' || status === 'redeemed' || status === 'code_issued') {
    return 'activated';
  }

  if (!paymentStatusMap[status]) {
    return 'pending';
  }

  return status;
};

const paymentRequestRows = computed(() => {
  return paymentRequests.value.map((item) => {
    const payload = parsePaymentPayload(item.note) || {};
    return {
      ...item,
      status: getPaymentRequestStatus(item),
      amount_cents: Number(payload.amount_cents || 0),
      payment_reference: payload.payment_reference || '',
      remark: payload.remark || '',
      rejected_reason: payload.rejected_reason || '',
      paid_at: payload.paid_at || null,
      activated_at: payload.activated_at || null,
    };
  });
});

const formatYuan = (amountCents) => {
  const cents = Number(amountCents || 0);
  return (cents / 100).toFixed(2);
};

const loadPaymentRequests = async () => {
  if (!bookId || form.value.is_free) {
    paymentRequests.value = [];
    return;
  }

  loadingPaymentRequests.value = true;
  try {
    const res = await Axios.get('/book/redeem-codes/', {
      params: {
        book_id: bookId,
        payment_request: 1,
      },
    });
    paymentRequests.value = res.results || res;
  } catch (err) {
    console.error('Load payment requests error:', err);
    paymentRequests.value = [];
  } finally {
    loadingPaymentRequests.value = false;
  }
};

const confirmPaymentRequest = async (row) => {
  processingPaymentRequestId.value = row.id;
  try {
    const res = await Axios.post(`/book/redeem-codes/${row.id}/confirm-payment/`);
    message.success(res.detail || '已确认支付并开通');
    await loadPaymentRequests();
  } catch (err) {
    message.error(err.response?.data?.detail || '确认失败');
  } finally {
    processingPaymentRequestId.value = null;
  }
};

const rejectPaymentRequest = async (row) => {
  const reason = window.prompt('请输入驳回原因（可选）', '') || '';
  processingPaymentRequestId.value = row.id;
  try {
    const res = await Axios.post(`/book/redeem-codes/${row.id}/reject-payment/`, { reason });
    message.success(res.detail || '已驳回');
    await loadPaymentRequests();
  } catch (err) {
    message.error(err.response?.data?.detail || '驳回失败');
  } finally {
    processingPaymentRequestId.value = null;
  }
};

onMounted(() => {
  loadBook();
  if (bookId) {
    loadRedeemCodes();
    loadPaymentRequests();
  }
});
</script>

<template>
  <div class="book-edit-page">
    <n-spin :show="loading">
      <n-space justify="space-between" align="center" style="margin-bottom: 24px">
        <h1 style="margin: 0">{{ isEdit ? '编辑电子书' : '创建电子书' }}</h1>
        <n-space>
          <n-button @click="router.push({ name: 'book_list' })">返回列表</n-button>
          <n-button v-if="isEdit" type="error" @click="deleteBook">删除书籍</n-button>
        </n-space>
      </n-space>

      <n-card title="基本信息">
        <n-form :model="form" label-placement="left" label-width="100px">
          <n-form-item label="书籍标题" required>
            <n-input v-model:value="form.title" placeholder="请输入书籍标题" />
          </n-form-item>
          
          <n-form-item label="书籍描述">
            <n-input 
              v-model:value="form.description" 
              type="textarea" 
              placeholder="请输入书籍描述"
              :rows="4"
            />
          </n-form-item>
          
          <n-form-item label="难度">
            <n-select v-model:value="form.difficulty" :options="difficultyOptions" style="width: 200px" />
          </n-form-item>
          
          <n-form-item label="标签">
            <n-dynamic-tags v-model:value="form.tags" />
          </n-form-item>
          
          <n-form-item label="排序">
            <n-input-number v-model:value="form.order" :min="0" />
          </n-form-item>
          
          <n-form-item label="状态">
            <n-space>
              <n-switch v-model:value="form.is_published">
                <template #checked>已发布</template>
                <template #unchecked>未发布</template>
              </n-switch>
              <n-switch v-model:value="form.is_free">
                <template #checked>免费</template>
                <template #unchecked>付费</template>
              </n-switch>
            </n-space>
          </n-form-item>
          
          <n-form-item>
            <n-button type="primary" :loading="saving" @click="save">
              {{ isEdit ? '保存修改' : '创建书籍' }}
            </n-button>
          </n-form-item>
        </n-form>
      </n-card>

      <!-- 章节管理（仅编辑模式） -->
      <n-card v-if="isEdit" title="章节管理" style="margin-top: 16px">
        <template #header-extra>
          <n-button type="primary" size="small" @click="openAddChapter">添加章节</n-button>
        </template>
        
        <n-spin :show="loadingChapters">
          <n-list v-if="chapters.length > 0">
            <n-list-item v-for="chapter in chapters" :key="chapter.id">
              <n-space justify="space-between" align="center" style="width: 100%">
                <n-space align="center">
                  <n-tag size="small">{{ chapter.order }}</n-tag>
                  <span style="font-weight: 600">{{ chapter.title }}</span>
                  <n-tag size="small" :bordered="false">{{ chapter.sections?.length || 0 }} 小节</n-tag>
                </n-space>
                <n-space>
                  <n-button size="small" @click="goToEditSection(chapter.id)">编辑小节</n-button>
                  <n-button size="small" @click="openEditChapter(chapter)">编辑</n-button>
                  <n-button size="small" type="error" @click="deleteChapter(chapter)">删除</n-button>
                </n-space>
              </n-space>
            </n-list-item>
          </n-list>
          <n-empty v-else description="暂无章节，点击上方按钮添加" />
        </n-spin>
      </n-card>
      
      <!-- 兑换码管理（仅编辑模式且为付费书籍） -->
      <n-card v-if="isEdit && !form.is_free" title="兑换码管理" style="margin-top: 16px">
        <template #header-extra>
          <n-button type="primary" size="small" @click="openGenerateCodeModal">生成兑换码</n-button>
        </template>
        
        <n-spin :show="loadingCodes">
          <n-table v-if="redeemCodes.length > 0" :bordered="false" :single-line="false">
            <thead>
              <tr>
                <th>兑换码</th>
                <th>使用次数</th>
                <th>状态</th>
                <th>备注</th>
                <th>创建时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="code in redeemCodes" :key="code.id">
                <td>
                  <n-space align="center">
                    <code>{{ code.code }}</code>
                    <n-button size="tiny" @click="copyCode(code.code)">复制</n-button>
                  </n-space>
                </td>
                <td>{{ code.used_count }} / {{ code.max_uses }}</td>
                <td>
                  <n-tag :type="code.is_valid ? 'success' : 'error'" size="small">
                    {{ code.is_valid ? '有效' : '已失效' }}
                  </n-tag>
                </td>
                <td>{{ code.note || '-' }}</td>
                <td>{{ new Date(code.created_at).toLocaleString() }}</td>
                <td>
                  <n-button size="tiny" type="error" @click="deleteRedeemCode(code)">删除</n-button>
                </td>
              </tr>
            </tbody>
          </n-table>
          <n-empty v-else description="暂无兑换码，点击上方按钮生成" />
        </n-spin>
      </n-card>


      <n-card v-if="isEdit && !form.is_free" title="支付申请（自动开通）" style="margin-top: 16px">
        <template #header-extra>
          <n-button size="small" @click="loadPaymentRequests" :loading="loadingPaymentRequests">刷新</n-button>
        </template>

        <n-spin :show="loadingPaymentRequests">
          <n-table v-if="paymentRequestRows.length > 0" :bordered="false" :single-line="false">
            <thead>
              <tr>
                <th>ID</th>
                <th>申请用户</th>
                <th>金额</th>
                <th>支付备注</th>
                <th>状态</th>
                <th>申请时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in paymentRequestRows" :key="row.id">
                <td>{{ row.id }}</td>
                <td>{{ row.created_by_name || '-' }}</td>
                <td>¥ {{ formatYuan(row.amount_cents) }}</td>
                <td>{{ row.payment_reference || row.remark || '-' }}</td>
                <td>
                  <n-tag size="small" :type="paymentStatusMap[row.status]?.type || 'default'">
                    {{ paymentStatusMap[row.status]?.label || row.status }}
                  </n-tag>
                </td>
                <td>{{ new Date(row.created_at).toLocaleString() }}</td>
                <td>
                  <n-space v-if="row.status === 'pending'" size="small">
                    <n-button
                      size="tiny"
                      type="primary"
                      :loading="processingPaymentRequestId === row.id"
                      @click="confirmPaymentRequest(row)"
                    >
                      确认并开通
                    </n-button>
                    <n-button
                      size="tiny"
                      type="error"
                      :loading="processingPaymentRequestId === row.id"
                      @click="rejectPaymentRequest(row)"
                    >
                      驳回
                    </n-button>
                  </n-space>
                  <span v-else-if="row.status === 'activated'" style="color: #18a058">已开通</span>
                  <span v-else style="color: #d03050">已驳回</span>
                </td>
              </tr>
            </tbody>
          </n-table>
          <n-empty v-else description="暂无支付申请" />
        </n-spin>
      </n-card>
    </n-spin>

    <!-- 章节编辑弹窗 -->
    <n-modal v-model:show="showChapterModal" preset="dialog" :title="editingChapter ? '编辑章节' : '添加章节'">
      <n-form :model="chapterForm" label-placement="left" label-width="80px">
        <n-form-item label="章节标题" required>
          <n-input v-model:value="chapterForm.title" placeholder="请输入章节标题" />
        </n-form-item>
        <n-form-item label="章节描述">
          <n-input v-model:value="chapterForm.description" type="textarea" placeholder="请输入章节描述" />
        </n-form-item>
        <n-form-item label="排序">
          <n-input-number v-model:value="chapterForm.order" :min="0" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-button @click="showChapterModal = false">取消</n-button>
        <n-button type="primary" @click="saveChapter">保存</n-button>
      </template>
    </n-modal>
    
    <!-- 生成兑换码弹窗 -->
    <n-modal v-model:show="showCodeModal" preset="dialog" title="生成兑换码">
      <n-form :model="codeForm" label-placement="left" label-width="100px">
        <n-form-item label="生成数量">
          <n-input-number v-model:value="codeForm.count" :min="1" :max="100" />
        </n-form-item>
        <n-form-item label="每码使用次数">
          <n-input-number v-model:value="codeForm.max_uses" :min="1" disabled />
          <span style="margin-left: 8px; color: #999">每个兑换码只能使用一次</span>
        </n-form-item>
        <n-form-item label="备注">
          <n-input v-model:value="codeForm.note" placeholder="可选，如：某某班级" />
        </n-form-item>
      </n-form>
      
      <!-- 生成结果 -->
      <div v-if="generatedCodes.length > 0" style="margin-top: 16px">
        <n-divider>生成的兑换码</n-divider>
        <n-space vertical>
          <n-space v-for="code in generatedCodes" :key="code.id" align="center">
            <code>{{ code.code }}</code>
            <n-button size="tiny" @click="copyCode(code.code)">复制</n-button>
          </n-space>
        </n-space>
      </div>
      
      <template #action>
        <n-button @click="showCodeModal = false">关闭</n-button>
        <n-button type="primary" :loading="generatingCodes" @click="generateCodes">生成</n-button>
      </template>
    </n-modal>
  </div>
</template>

<style scoped>
.book-edit-page {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}
</style>
