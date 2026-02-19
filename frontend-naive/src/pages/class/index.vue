<template>
  <div class="class-list-page">
    <section class="class-hero">
      <div class="hero-text">
        <p class="hero-kicker">教学中心</p>
        <h1>我的班级</h1>
        <p class="hero-subtitle">管理你创建的班级，或查看你加入的班级</p>
      </div>
      <div class="hero-metrics">
        <div class="metric-card">
          <n-icon :component="SchoolOutline" />
          <span>{{ classes.length }}</span>
          <small>班级总数</small>
        </div>
        <div class="metric-card">
          <n-icon :component="BookOutline" />
          <span>{{ teachingClasses.length }}</span>
          <small>我创建的</small>
        </div>
        <div class="metric-card">
          <n-icon :component="PeopleOutline" />
          <span>{{ joinedClasses.length }}</span>
          <small>我加入的</small>
        </div>
      </div>
    </section>

    <section class="toolbar-card" v-if="canCreateClass">
      <n-button type="primary" @click="showCreateModal = true" class="create-btn">
        创建班级
      </n-button>
    </section>

    <n-tabs type="line" animated v-model:value="activeTab" class="class-tabs">
      <n-tab-pane name="teaching" tab="我创建的班级">
        <div class="class-grid" v-if="teachingClasses.length > 0">
          <n-card
            v-for="cls in teachingClasses"
            :key="cls.id"
            hoverable
            class="class-card"
            @click="router.push({ name: 'class_detail', params: { id: cls.id } })"
          >
            <template #header>
              <div class="card-header">
                <div class="title-wrap">
                  <n-text strong class="class-title">{{ cls.title }}</n-text>
                  <n-tag v-if="cls.is_hidden" type="warning" size="small">隐藏</n-tag>
                </div>
                <n-space>
                  <n-button size="small" @click.stop="openEditModal(cls)">编辑</n-button>
                  <n-button type="error" size="small" @click.stop="handleDisband(cls)">解散班级</n-button>
                </n-space>
              </div>
            </template>

            <div class="meta-row">
              <span class="meta-pill">教师：{{ cls.teacher.username }}</span>
              <span class="meta-pill">学生数：{{ cls.student_count }}</span>
              <span class="meta-pill">题目数：{{ cls.problem_count }}</span>
              <span class="meta-pill">作业数：{{ cls.assignment_count }}</span>
            </div>

            <n-text v-if="cls.description" depth="3" class="class-desc">{{ cls.description }}</n-text>
            <n-text v-else depth="3" class="class-desc empty-desc">暂无班级描述</n-text>
          </n-card>
        </div>
        <n-empty v-else description="暂无班级" class="empty-wrap" />
      </n-tab-pane>

      <n-tab-pane name="joined" tab="我加入的班级">
        <div class="class-grid" v-if="joinedClasses.length > 0">
          <n-card
            v-for="cls in joinedClasses"
            :key="cls.id"
            hoverable
            class="class-card"
            @click="router.push({ name: 'class_detail', params: { id: cls.id } })"
          >
            <template #header>
              <div class="card-header">
                <div class="title-wrap">
                  <n-text strong class="class-title">{{ cls.title }}</n-text>
                </div>
              </div>
            </template>

            <div class="meta-row">
              <span class="meta-pill">教师：{{ cls.teacher.username }}</span>
              <span class="meta-pill">学生数：{{ cls.student_count }}</span>
              <span class="meta-pill">题目数：{{ cls.problem_count }}</span>
              <span class="meta-pill">作业数：{{ cls.assignment_count }}</span>
            </div>

            <n-text v-if="cls.description" depth="3" class="class-desc">{{ cls.description }}</n-text>
            <n-text v-else depth="3" class="class-desc empty-desc">暂无班级描述</n-text>
          </n-card>
        </div>
        <n-empty v-else description="暂未加入任何班级" class="empty-wrap" />
      </n-tab-pane>
    </n-tabs>

    <n-modal v-model:show="showCreateModal" preset="dialog" title="创建班级">
      <n-form :model="newClass" label-placement="left" label-width="80">
        <n-form-item label="班级名称" required>
          <n-input v-model:value="newClass.title" placeholder="请输入班级名称" />
        </n-form-item>
        <n-form-item label="班级描述">
          <n-input
            v-model:value="newClass.description"
            type="textarea"
            placeholder="请输入班级描述"
            :rows="3"
          />
        </n-form-item>
        <n-form-item label="是否隐藏">
          <n-switch v-model:value="newClass.is_hidden" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" @click="createClass" :loading="creating">创建</n-button>
        </n-space>
      </template>
    </n-modal>

    <n-modal v-model:show="showEditModal" preset="dialog" title="编辑班级">
      <n-form :model="editClass" label-placement="left" label-width="80">
        <n-form-item label="班级名称" required>
          <n-input v-model:value="editClass.title" placeholder="请输入班级名称" />
        </n-form-item>
        <n-form-item label="班级描述">
          <n-input
            v-model:value="editClass.description"
            type="textarea"
            placeholder="请输入班级描述"
            :rows="3"
          />
        </n-form-item>
        <n-form-item label="是否隐藏">
          <n-switch v-model:value="editClass.is_hidden" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="showEditModal = false">取消</n-button>
          <n-button type="primary" @click="updateClass" :loading="updating">保存</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useMessage, useDialog } from 'naive-ui';
import { SchoolOutline, BookOutline, PeopleOutline } from '@vicons/ionicons5';
import Axios from '@/plugins/axios';
import store from '@/store';
import router from '@/router';

const message = useMessage();
const dialog = useDialog();

const classes = ref([]);
const showCreateModal = ref(false);
const showEditModal = ref(false);
const creating = ref(false);
const updating = ref(false);
const activeTab = ref('joined');
const newClass = ref({
  title: '',
  description: '',
  is_hidden: false,
});

const editingClassId = ref(null);
const editClass = ref({
  title: '',
  description: '',
  is_hidden: false,
});

const teachingClasses = computed(() => classes.value.filter(cls => cls.user_role === 'teacher'));
const joinedClasses = computed(() => classes.value.filter(cls => cls.user_role === 'student'));
const canCreateClass = computed(() => store.state.user?.permissions?.includes('class'));

const fetchClasses = () => {
  Axios.get('class/class/')
    .then(res => {
      classes.value = res;
      const hasTeachingClasses = res.some(cls => cls.user_role === 'teacher');
      activeTab.value = hasTeachingClasses ? 'teaching' : 'joined';
    })
    .catch(() => {
      message.error('获取班级列表失败');
    });
};

const openEditModal = (cls) => {
  editingClassId.value = cls.id;
  editClass.value = {
    title: cls.title || '',
    description: cls.description || '',
    is_hidden: !!cls.is_hidden,
  };
  showEditModal.value = true;
};

const updateClass = () => {
  if (!editingClassId.value) {
    message.error('班级信息异常');
    return;
  }
  if (!editClass.value.title) {
    message.warning('请输入班级名称');
    return;
  }

  updating.value = true;
  Axios.patch(`class/class/${editingClassId.value}/`, editClass.value)
    .then(() => {
      message.success('保存成功');
      showEditModal.value = false;
      fetchClasses();
    })
    .catch(() => {
      message.error('保存失败');
    })
    .finally(() => {
      updating.value = false;
    });
};

const createClass = () => {
  if (!newClass.value.title) {
    message.warning('请输入班级名称');
    return;
  }

  creating.value = true;
  Axios.post('class/class/', newClass.value)
    .then(() => {
      message.success('创建成功');
      showCreateModal.value = false;
      newClass.value = {
        title: '',
        description: '',
        is_hidden: false,
      };
      fetchClasses();
    })
    .catch(() => {
      message.error('创建失败');
    })
    .finally(() => {
      creating.value = false;
    });
};

const handleDisband = (cls) => {
  dialog.error({
    title: '解散班级',
    content: `确定要解散班级 "${cls.title}" 吗？解散后所有成员将被移除，且班级不可恢复！`,
    positiveText: '确定解散',
    negativeText: '取消',
    onPositiveClick: () => {
      return new Promise((resolve, reject) => {
        Axios.post(`class/class/${cls.id}/disband/`)
          .then(() => {
            message.success('班级已解散');
            fetchClasses();
            resolve();
          })
          .catch((err) => {
            message.error(err.response?.data?.error || '解散失败');
            reject();
          });
      });
    },
  });
};

onMounted(() => {
  fetchClasses();
});
</script>

<style lang="scss" scoped>
.class-list-page {
  padding: 8px 6px 16px;
  --primary-ink: #173a63;
  --soft-ink: #66758a;
  --line-color: #d9e5f2;
}

.class-hero {
  display: flex;
  justify-content: space-between;
  align-items: stretch;
  gap: 14px;
  padding: 22px 24px;
  border-radius: 18px;
  background: linear-gradient(135deg, #1f4f86 0%, #356fa8 52%, #6ba4d7 100%);
  color: #fff;
  margin-bottom: 14px;
}

.hero-kicker {
  margin: 0;
  font-size: 13px;
  letter-spacing: 0.08em;
  opacity: 0.88;
}

.hero-text h1 {
  margin: 4px 0;
  font-size: 34px;
  line-height: 1.1;
}

.hero-subtitle {
  margin: 0;
  font-size: 14px;
  opacity: 0.92;
}

.hero-metrics {
  display: flex;
  gap: 10px;
}

.metric-card {
  min-width: 120px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.16);
  border: 1px solid rgba(255, 255, 255, 0.28);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 10px 8px;
}

.metric-card :deep(.n-icon) {
  font-size: 18px;
}

.metric-card span {
  font-size: 24px;
  font-weight: 700;
  line-height: 1.2;
}

.metric-card small {
  font-size: 12px;
  opacity: 0.9;
}

.toolbar-card {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 10px;
}

.create-btn {
  box-shadow: 0 8px 20px rgba(29, 151, 84, 0.24);
}

.class-tabs {
  border-radius: 12px;
  background: #fff;
  padding: 8px 10px 14px;
  border: 1px solid var(--line-color);
}

.class-grid {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 12px;
}

.class-card {
  cursor: pointer;
  border-radius: 14px;
  border: 1px solid #dce8f8;
  border-left: 4px solid #2f76b9;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.class-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 22px rgba(30, 66, 109, 0.12);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.title-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}

.class-title {
  color: var(--primary-ink);
  font-size: 21px;
}

.meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.meta-pill {
  font-size: 13px;
  color: #35587f;
  background: #edf5ff;
  border: 1px solid #d2e4fb;
  border-radius: 999px;
  padding: 4px 10px;
}

.class-desc {
  display: block;
  color: var(--soft-ink);
}

.empty-desc {
  font-style: italic;
  opacity: 0.72;
}

.empty-wrap {
  margin-top: 12px;
}

@media (max-width: 900px) {
  .class-hero {
    flex-direction: column;
    padding: 18px;
  }

  .hero-metrics {
    width: 100%;
  }

  .metric-card {
    flex: 1;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
