<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useMessage } from 'naive-ui';
import Axios from '@/plugins/axios';
import store from '@/store';

const route = useRoute();
const router = useRouter();
const message = useMessage();
const bookId = route.params.id;

const book = ref(null);
const loading = ref(false);
const activeTab = ref('overview');

const hasAccess = ref(true);
const checkingAccess = ref(false);

const showRedeemModal = ref(false);
const redeemCode = ref('');
const redeeming = ref(false);

const showPaymentModal = ref(false);
const paymentRequesting = ref(false);
const paymentForm = ref({
  amount_cents: 9900,
  payment_reference: '',
  remark: '',
});
const loadingPaymentRequests = ref(false);
const paymentRequests = ref([]);

const canManage = computed(() => {
  const permissions = store.state.user?.permissions || [];
  return store.state.user?.is_staff || permissions.includes('class') || permissions.includes('problem');
});

const difficultyMap = {
  beginner: { label: '入门', type: 'success' },
  easy: { label: '简单', type: 'info' },
  medium: { label: '中等', type: 'warning' },
  hard: { label: '困难', type: 'error' },
};

const paymentStatusMap = {
  pending: { label: '待确认', type: 'warning' },
  activated: { label: '已开通', type: 'success' },
  rejected: { label: '已驳回', type: 'error' },
};

const paymentStatusMeta = (status) => {
  return paymentStatusMap[status] || { label: status || '未知', type: 'default' };
};

const formatYuan = (amountCents) => {
  const cents = Number(amountCents || 0);
  return (cents / 100).toFixed(2);
};

const formatTime = (value) => {
  if (!value) return '-';
  const time = new Date(value);
  if (Number.isNaN(time.getTime())) return '-';
  return time.toLocaleString();
};

const loadBook = async () => {
  loading.value = true;
  try {
    book.value = await Axios.get(`/book/books/${bookId}/`);
    if (!book.value.is_free) {
      await checkAccess();
      await loadPaymentRequests();
    } else {
      hasAccess.value = true;
      paymentRequests.value = [];
    }
  } catch (err) {
    console.error('Failed to load book:', err);
    message.error('加载书籍失败');
  } finally {
    loading.value = false;
  }
};

const checkAccess = async () => {
  checkingAccess.value = true;
  try {
    const res = await Axios.get(`/book/books/${bookId}/check_access/`);
    hasAccess.value = !!res.has_access;
  } catch (err) {
    hasAccess.value = false;
  } finally {
    checkingAccess.value = false;
  }
};

const loadPaymentRequests = async () => {
  if (!book.value || book.value.is_free) {
    paymentRequests.value = [];
    return;
  }
  loadingPaymentRequests.value = true;
  try {
    const res = await Axios.get(`/book/books/${bookId}/payment_requests/`);
    paymentRequests.value = res.results || [];
  } catch (err) {
    paymentRequests.value = [];
  } finally {
    loadingPaymentRequests.value = false;
  }
};


const openRedeemModal = () => {
  redeemCode.value = '';
  showRedeemModal.value = true;
};

const submitRedeem = async () => {
  const code = String(redeemCode.value || '').trim();
  if (!code) {
    message.warning('请输入兑换码');
    return;
  }

  redeeming.value = true;
  try {
    await Axios.post(`/book/books/${bookId}/redeem/`, { code });
    message.success('兑换成功，已自动开通电子书');
    showRedeemModal.value = false;
    hasAccess.value = true;
    await loadBook();
  } catch (err) {
    message.error(err?.response?.data?.detail || err?.detail || '兑换失败');
  } finally {
    redeeming.value = false;
  }
};


const openPaymentModal = () => {
  paymentForm.value = {
    amount_cents: paymentForm.value.amount_cents || 9900,
    payment_reference: '',
    remark: '',
  };
  showPaymentModal.value = true;
};

const submitPaymentRequest = async () => {
  if (!paymentForm.value.amount_cents || Number(paymentForm.value.amount_cents) <= 0) {
    message.warning('请输入正确的支付金额（分）');
    return;
  }

  paymentRequesting.value = true;
  try {
    const res = await Axios.post(`/book/books/${bookId}/payment_request/`, {
      amount_cents: Number(paymentForm.value.amount_cents),
      payment_reference: paymentForm.value.payment_reference,
      remark: paymentForm.value.remark,
    });
    message.success(res.detail || '支付申请已提交');
    showPaymentModal.value = false;
    await loadPaymentRequests();
    await checkAccess();
  } catch (err) {
    message.error(err?.response?.data?.detail || err?.detail || '提交支付申请失败');
  } finally {
    paymentRequesting.value = false;
  }
};

const startReading = async () => {
  if (!hasAccess.value && !book.value?.is_free) {
    openRedeemModal();
    return;
  }
  try {
    const res = await Axios.post(`/book/books/${bookId}/start_reading/`);
    if (res.first_section_id) {
      router.push({ name: 'book_section', params: { id: res.first_section_id } });
    } else {
      message.warning('该书籍暂无内容');
    }
  } catch (err) {
    message.error('开始阅读失败');
  }
};

const continueReading = () => {
  if (!hasAccess.value && !book.value?.is_free) {
    openRedeemModal();
    return;
  }
  if (book.value?.user_progress?.last_section_id) {
    router.push({ name: 'book_section', params: { id: book.value.user_progress.last_section_id } });
  } else {
    startReading();
  }
};

const goToSection = (sectionId) => {
  if (!hasAccess.value && !book.value?.is_free) {
    openRedeemModal();
    return;
  }
  router.push({ name: 'book_section', params: { id: sectionId } });
};

const totalEstimatedTime = computed(() => {
  if (!book.value?.chapters) return 0;
  let total = 0;
  book.value.chapters.forEach(chapter => {
    chapter.sections?.forEach(section => {
      total += section.estimated_time || 0;
    });
  });
  return total;
});

onMounted(() => {
  loadBook();
});
</script>

<template>
  <div class="book-detail-page">
    <n-spin :show="loading">
      <template v-if="book">
        <div class="book-header">
          <div class="book-cover-large">
            <img v-if="book.cover" :src="book.cover" :alt="book.title" />
            <div v-else class="book-cover-placeholder">
              <span>{{ book.title.substring(0, 2) }}</span>
            </div>
          </div>

          <div class="book-info">
            <h1 class="book-title">{{ book.title }}</h1>

            <n-space class="book-tag-space" align="center">
              <n-tag v-if="book.difficulty" :type="difficultyMap[book.difficulty]?.type" size="small">
                {{ difficultyMap[book.difficulty]?.label }}
              </n-tag>
              <n-tag v-for="tag in book.tags" :key="tag" size="small" :bordered="false">
                {{ tag }}
              </n-tag>
              <n-tag v-if="!book.is_free" type="warning" size="small">付费书籍</n-tag>
              <n-tag v-if="!book.is_free && hasAccess" type="success" size="small">已开通</n-tag>
              <n-tag v-if="!book.is_free" type="info" size="small">支付成功自动开通</n-tag>
            </n-space>

            <p class="book-desc">{{ book.description }}</p>

            <n-space class="book-meta-space" align="center">
              <span>{{ book.chapter_count }} 章 / {{ book.section_count }} 节</span>
              <n-divider vertical />
              <span>预计 {{ totalEstimatedTime }} 分钟</span>
              <n-divider vertical />
              <span>{{ book.reader_count }} 人已读</span>
            </n-space>

            <div v-if="book.user_progress" class="progress-section">
              <n-space justify="space-between" style="margin-bottom: 8px">
                <span>学习进度</span>
                <span>{{ book.user_progress.completed_count }} / {{ book.user_progress.total_count }}</span>
              </n-space>
              <n-progress
                type="line"
                :percentage="book.user_progress.progress_percent"
                :height="8"
                status="success"
              />
            </div>

            <n-space class="book-action-space">
              <n-button v-if="book.user_progress" type="primary" size="large" @click="continueReading">
                继续阅读
              </n-button>
              <n-button v-else type="primary" size="large" @click="startReading">
                开始阅读
              </n-button>
              <n-button size="large" @click="router.push({ name: 'book_list' })">
                返回列表
              </n-button>
              <n-button
                v-if="!book.is_free && !hasAccess"
                type="success"
                size="large"
                @click="openRedeemModal"
              >
                输入兑换码
              </n-button>
              <n-button
                v-if="!book.is_free && !hasAccess"
                type="warning"
                size="large"
                @click="openPaymentModal"
              >
                提交支付申请
              </n-button>
            </n-space>
          </div>
        </div>

        <n-tabs v-model:value="activeTab" type="line" class="book-tabs">
          <n-tab-pane name="overview" tab="概览">
            <div class="overview-content">
              <h3>📖 书籍简介</h3>
              <p>{{ book.description || '暂无简介' }}</p>

              <h3 style="margin-top: 24px">📚 章节概览</h3>
              <n-list>
                <n-list-item v-for="chapter in book.chapters" :key="chapter.id">
                  <n-thing>
                    <template #header>
                      <n-space align="center">
                        <span style="font-weight: 600">{{ chapter.title }}</span>
                        <n-tag size="small" :bordered="false">
                          {{ chapter.completed_count || 0 }} / {{ chapter.section_count }} 已完成
                        </n-tag>
                      </n-space>
                    </template>
                    <template #description>
                      {{ chapter.description || '暂无描述' }}
                    </template>
                  </n-thing>
                </n-list-item>
              </n-list>
            </div>
          </n-tab-pane>

          <n-tab-pane name="catalog" tab="目录">
            <div class="catalog-content">
              <n-collapse>
                <n-collapse-item v-for="chapter in book.chapters" :key="chapter.id" :title="chapter.title" :name="chapter.id">
                  <template #header-extra>
                    <n-tag size="small" :type="chapter.completed_count === chapter.section_count ? 'success' : 'default'">
                      {{ chapter.completed_count || 0 }} / {{ chapter.section_count }}
                    </n-tag>
                  </template>

                  <n-list>
                    <n-list-item
                      v-for="section in chapter.sections"
                      :key="section.id"
                      class="section-item"
                      @click="goToSection(section.id)"
                    >
                      <n-space align="center" justify="space-between" style="width: 100%">
                        <n-space align="center">
                          <n-icon v-if="section.is_completed" color="#18a058">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                            </svg>
                          </n-icon>
                          <n-icon v-else-if="section.content_type === 'video'" color="#2080f0">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                              <path d="M8 5v14l11-7z"/>
                            </svg>
                          </n-icon>
                          <n-icon v-else-if="section.content_type === 'problem'" color="#f0a020">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
                            </svg>
                          </n-icon>
                          <n-icon v-else color="#666">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                              <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11z"/>
                            </svg>
                          </n-icon>
                          <span>{{ section.title }}</span>
                        </n-space>
                        <span style="color: #999; font-size: 12px">{{ section.estimated_time }} 分钟</span>
                      </n-space>
                    </n-list-item>
                  </n-list>
                </n-collapse-item>
              </n-collapse>
            </div>
          </n-tab-pane>
        </n-tabs>

        <n-alert v-if="!book.is_free && !hasAccess" type="warning" class="access-alert">
          <template #header>此书籍需要开通</template>
          支持两种方式：输入兑换码直接兑换，或提交支付申请并在确认后自动开通。
          <n-button size="small" type="success" style="margin-left: 12px" @click="openRedeemModal">
            输入兑换码
          </n-button>
          <n-button size="small" type="primary" style="margin-left: 8px" @click="openPaymentModal">
            提交支付申请
          </n-button>
        </n-alert>

        <n-card v-if="!book.is_free && canManage" title="支付记录（自动开通）" class="payment-record-card">
          <template #header-extra>
            <n-button size="small" @click="loadPaymentRequests" :loading="loadingPaymentRequests">刷新</n-button>
          </template>
          <n-spin :show="loadingPaymentRequests || checkingAccess">
            <div class="payment-table-wrap" v-if="paymentRequests.length > 0">
              <n-table :bordered="false" :single-line="false">
                <thead>
                  <tr>
                    <th>申请时间</th>
                    <th>金额</th>
                    <th>支付备注</th>
                    <th>状态</th>
                    <th>处理结果</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="req in paymentRequests" :key="req.request_id">
                    <td>{{ formatTime(req.created_at) }}</td>
                    <td>¥ {{ formatYuan(req.amount_cents) }}</td>
                    <td>{{ req.payment_reference || req.remark || '-' }}</td>
                    <td>
                      <n-tag size="small" :type="paymentStatusMeta(req.status).type">
                        {{ paymentStatusMeta(req.status).label }}
                      </n-tag>
                    </td>
                    <td>
                      <template v-if="req.status === 'activated'">
                        {{ formatTime(req.activated_at || req.paid_at) }} 开通
                      </template>
                      <template v-else-if="req.status === 'rejected'">
                        驳回：{{ req.rejected_reason || '无' }}
                      </template>
                      <span style="color: #999">等待教师确认</span>
                    </td>
                  </tr>
                </tbody>
              </n-table>
            </div>
            <n-empty v-else description="暂无支付记录" />
          </n-spin>
        </n-card>
      </template>
    </n-spin>


    <n-modal v-model:show="showRedeemModal" preset="dialog" title="输入兑换码兑换">
      <n-input
        v-model:value="redeemCode"
        placeholder="请输入兑换码"
        @keyup.enter="submitRedeem"
      />
      <template #action>
        <n-button @click="showRedeemModal = false">取消</n-button>
        <n-button type="primary" :loading="redeeming" @click="submitRedeem">兑换</n-button>
      </template>
    </n-modal>

    <n-modal v-model:show="showPaymentModal" preset="dialog" title="提交支付申请（支付成功后自动开通）">
      <n-form :model="paymentForm" label-placement="left" label-width="110px">
        <n-form-item label="支付金额（分）" required>
          <n-input-number v-model:value="paymentForm.amount_cents" :min="1" :step="100" style="width: 220px" />
          <span style="margin-left: 8px; color: #999">当前：¥ {{ formatYuan(paymentForm.amount_cents) }}</span>
        </n-form-item>
        <n-form-item label="支付流水号">
          <n-input v-model:value="paymentForm.payment_reference" placeholder="可选，填写转账单号" />
        </n-form-item>
        <n-form-item label="备注">
          <n-input
            v-model:value="paymentForm.remark"
            type="textarea"
            :rows="3"
            placeholder="可选，例如：微信已支付，请尽快确认"
          />
        </n-form-item>
      </n-form>
      <template #action>
        <n-button @click="showPaymentModal = false">取消</n-button>
        <n-button type="primary" :loading="paymentRequesting" @click="submitPaymentRequest">提交申请</n-button>
      </template>
    </n-modal>
  </div>
</template>

<style scoped>
.book-detail-page {
  padding: 18px 20px 24px;
  max-width: 1080px;
  margin: 0 auto;
}

.book-header {
  display: flex;
  gap: 32px;
  padding: 26px;
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
  border: 1px solid #e4ecf7;
  border-radius: 20px;
  box-shadow: 0 12px 28px rgba(32, 80, 160, 0.08);
}

.book-cover-large {
  width: 220px;
  height: 288px;
  flex-shrink: 0;
  border-radius: 14px;
  overflow: hidden;
  background: linear-gradient(135deg, #5b8df4 0%, #4f46c8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.book-cover-large img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-cover-placeholder {
  color: white;
  font-size: 48px;
  font-weight: bold;
}

.book-info {
  flex: 1;
}

.book-title {
  margin: 0 0 14px 0;
  font-size: 44px;
  line-height: 1.15;
  font-weight: 800;
  letter-spacing: 0.4px;
  color: #1f2d3d;
}

.book-tag-space {
  margin-bottom: 14px;
}

.book-tag-space :deep(.n-tag) {
  border-radius: 999px;
}

.book-desc {
  color: #5f7388;
  line-height: 1.75;
  margin-bottom: 14px;
}

.book-meta-space {
  margin-bottom: 16px;
  color: #61768e;
  font-size: 14px;
}

.progress-section {
  margin-top: 14px;
  background: #f5faff;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid #deebfa;
}

.book-action-space {
  margin-top: 16px;
  flex-wrap: wrap;
}

.book-action-space :deep(.n-button) {
  border-radius: 10px;
  font-weight: 600;
}

.book-tabs {
  margin-top: 22px;
}

.book-tabs :deep(.n-tabs-nav) {
  padding: 0 4px 6px;
  border-bottom: 1px solid #e8eef8;
}

.book-tabs :deep(.n-tabs-tab) {
  font-weight: 600;
}

.overview-content,
.catalog-content {
  background: #fff;
  border-radius: 14px;
  border: 1px solid #e6edf8;
  box-shadow: 0 10px 24px rgba(32, 80, 160, 0.05);
  padding: 18px;
}

.overview-content h3 {
  margin: 0 0 12px 0;
  font-size: 19px;
  color: #2b3f56;
}

.overview-content p {
  color: #61758b;
  line-height: 1.9;
}

.section-item {
  cursor: pointer;
  padding: 12px 14px;
  border-radius: 10px;
  transition: background 0.2s, transform 0.2s;
}

.section-item:hover {
  background: #f4f8ff;
  transform: translateX(2px);
}

.payment-table-wrap {
  width: 100%;
  overflow-x: auto;
}

.access-alert {
  margin-top: 16px;
  border-radius: 12px;
}

.payment-record-card {
  margin-top: 16px;
  border: 1px solid #e4ecf7;
  border-radius: 14px;
  box-shadow: 0 10px 24px rgba(32, 80, 160, 0.05);
}

@media (max-width: 900px) {
  .book-detail-page {
    padding: 10px 12px 16px;
  }

  .book-header {
    flex-direction: column;
    gap: 16px;
    padding: 16px;
    border-radius: 16px;
  }

  .book-cover-large {
    width: 100%;
    height: auto;
    max-width: 260px;
    aspect-ratio: 3 / 4;
    margin: 0 auto;
  }

  .book-title {
    font-size: 30px;
  }

  .book-meta-space {
    gap: 8px 12px;
  }

  .book-meta-space :deep(.n-divider.n-divider--vertical) {
    display: none;
  }

  .book-action-space {
    width: 100%;
    margin-top: 12px;
  }

  .book-action-space :deep(.n-button) {
    width: 100%;
  }

  .overview-content,
  .catalog-content {
    padding: 12px;
    border-radius: 12px;
  }

  .section-item {
    padding: 10px;
  }
}
</style>
