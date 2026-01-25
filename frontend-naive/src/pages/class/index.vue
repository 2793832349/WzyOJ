<template>
  <div>
    <h1>
      <n-space align="center" size="large">
        <span>我的班级</span>
        <n-button type="primary" @click="showCreateModal = true" v-if="canCreateClass">
          创建班级
        </n-button>
      </n-space>
    </h1>

    <n-tabs type="line" animated v-model:value="activeTab">
      <n-tab-pane v-if="teachingClasses.length > 0" name="teaching" tab="我创建的班级">
        <n-space vertical>
          <n-card
            v-for="cls in teachingClasses"
            :key="cls.id"
            hoverable
            style="cursor: pointer"
          >
            <template #header>
              <n-space align="center" justify="space-between">
                <n-space align="center">
                  <n-text strong style="font-size: 18px">{{ cls.title }}</n-text>
                  <n-tag v-if="cls.is_hidden" type="warning" size="small">隐藏</n-tag>
                </n-space>
                <n-space>
                  <n-button size="small" @click.stop="openEditModal(cls)">
                    编辑
                  </n-button>
                  <n-button
                    type="error"
                    size="small"
                    @click.stop="handleDisband(cls)"
                  >
                    解散班级
                  </n-button>
                </n-space>
              </n-space>
            </template>
            <div @click="$router.push({ name: 'class_detail', params: { id: cls.id } })">
              <n-space>
                <n-text depth="3">教师：</n-text>
                <n-text>{{ cls.teacher.username }}</n-text>
                <n-divider vertical />
                <n-text depth="3">学生数：</n-text>
                <n-text>{{ cls.student_count }}</n-text>
                <n-divider vertical />
                <n-text depth="3">题目数：</n-text>
                <n-text>{{ cls.problem_count }}</n-text>
                <n-divider vertical />
                <n-text depth="3">作业数：</n-text>
                <n-text>{{ cls.assignment_count }}</n-text>
              </n-space>
              <n-text v-if="cls.description" depth="3" style="margin-top: 12px; display: block">
                {{ cls.description }}
              </n-text>
            </div>
          </n-card>
          <n-empty v-if="teachingClasses.length === 0" description="暂无班级" />
        </n-space>
      </n-tab-pane>

      <n-tab-pane name="joined" tab="我加入的班级">
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
              <n-text depth="3">教师：</n-text>
              <n-text>{{ cls.teacher.username }}</n-text>
              <n-divider vertical />
              <n-text depth="3">学生数：</n-text>
              <n-text>{{ cls.student_count }}</n-text>
              <n-divider vertical />
              <n-text depth="3">题目数：</n-text>
              <n-text>{{ cls.problem_count }}</n-text>
              <n-divider vertical />
              <n-text depth="3">作业数：</n-text>
              <n-text>{{ cls.assignment_count }}</n-text>
            </n-space>
            <n-text v-if="cls.description" depth="3" style="margin-top: 12px; display: block">
              {{ cls.description }}
            </n-text>
          </n-card>
          <n-empty v-if="joinedClasses.length === 0" description="暂未加入任何班级" />
        </n-space>
      </n-tab-pane>
    </n-tabs>

    <!-- 创建班级对话框 -->
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
          <n-button type="primary" @click="createClass" :loading="creating">
            创建
          </n-button>
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
          <n-button type="primary" @click="updateClass" :loading="updating">
            保存
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useMessage, useDialog } from 'naive-ui';
import Axios from '@/plugins/axios';
import store from '@/store';

const message = useMessage();
const dialog = useDialog();

const classes = ref([]);
const showCreateModal = ref(false);
const showEditModal = ref(false);
const creating = ref(false);
const updating = ref(false);
const activeTab = ref('joined'); // 默认选中"我加入的班级"
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

// 我教的班级
const teachingClasses = computed(() => {
  return classes.value.filter(cls => cls.user_role === 'teacher');
});

// 我加入的班级
const joinedClasses = computed(() => {
  return classes.value.filter(cls => cls.user_role === 'student');
});

// 是否可以创建班级
const canCreateClass = computed(() => {
  return store.state.user?.permissions?.includes('class');
});

// 获取班级列表
const fetchClasses = () => {
  Axios.get('class/class/')
    .then(res => {
      classes.value = res;
      // 如果有教师班级，默认选中"我创建的班级"
      const hasTeachingClasses = res.some(cls => cls.user_role === 'teacher');
      if (hasTeachingClasses) {
        activeTab.value = 'teaching';
      }
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

// 创建班级
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

// 解散班级
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
    }
  });
};

onMounted(() => {
  fetchClasses();
});
</script>
