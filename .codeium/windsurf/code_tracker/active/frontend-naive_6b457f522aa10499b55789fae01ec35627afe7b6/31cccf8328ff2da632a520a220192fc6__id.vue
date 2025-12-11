��<template>
  <div v-if="classInfo">
    <h1>{{ classInfo.title }}</h1>
    <p>{{ classInfo.description }}</p>

    <n-tabs type="line" animated>
      <!-- 作业列表 -->
      <n-tab-pane name="assignments" tab="作业">
        <n-space vertical>
          <n-button
            v-if="isTeacher"
            type="primary"
            @click="showCreateAssignmentModal = true"
          >
            创建作业
          </n-button>
          
          <n-list>
            <n-list-item v-for="assignment in assignments" :key="assignment.id">
              <n-thing>
                <template #header>
                  <n-space align="center">
                    {{ assignment.title }}
                    <n-tag v-if="assignment.is_expired" type="error">已截止</n-tag>
                    <n-tag v-if="assignment.is_hidden" type="warning">隐藏</n-tag>
                  </n-space>
                </template>
                <template #description>
                  <span v-if="assignment.deadline">
                    截止时间：{{ formatDate(assignment.deadline) }}
                  </span>
                </template>
                {{ assignment.description || '暂无描述' }}
                <template #action>
                  <n-space>
                    <n-button size="small" type="primary" @click="viewAssignmentDetail(assignment)">
                      查看作业
                    </n-button>
                    <n-button v-if="isTeacher" size="small" @click="viewAssignmentGrades(assignment)">
                      成绩表
                    </n-button>
                    <n-button v-if="isTeacher" size="small" @click="openEditAssignmentModal(assignment)">
                      编辑
                    </n-button>
                    <n-button v-if="isTeacher" size="small" type="error" @click="deleteAssignment(assignment.id)">
                      删除
                    </n-button>
                  </n-space>
                </template>
              </n-thing>
            </n-list-item>
            <n-empty v-if="assignments.length === 0" description="暂无作业" />
          </n-list>
        </n-space>
      </n-tab-pane>

      <!-- 题目列表 -->
      <n-tab-pane name="problems" tab="题目库">
        <n-space vertical>
          <n-space v-if="isTeacher">
            <n-button type="primary" @click="openReferenceProblemModal">
              引用主题库题目
            </n-button>
          </n-space>

          <n-data-table
            :columns="problemColumns"
            :data="problems"
            :pagination="{ pageSize: 20 }"
            :bordered="false"
          />
        </n-space>
      </n-tab-pane>

      <!-- 成员管理 -->
      <n-tab-pane name="students" tab="管理" v-if="isTeacher">
        <n-space vertical>
          <n-button type="primary" @click="showAddStudentModal = true">
            添加成员
          </n-button>

          <n-list>
            <n-list-item v-for="student in students" :key="student.id">
              <n-thing>
                <template #header>
                  <n-space align="center">
                    <span>{{ student.user.username }}</span>
                    <span v-if="student.user.real_name">({{ student.user.real_name }})</span>
                    <n-tag :type="student.role === 'teacher' ? 'success' : 'info'" size="small">
                      {{ student.role === 'teacher' ? '教师' : '学生' }}
                    </n-tag>
                  </n-space>
                </template>
                <template #description>
                  学号：{{ student.user.student_id || '无' }}
                </template>
                <template #action>
                  <n-space>
                    <n-button 
                      size="small" 
                      @click="toggleMemberRole(student)"
                    >
                      切换为{{ student.role === 'teacher' ? '学生' : '教师' }}
                    </n-button>
                    <n-button size="small" type="error" @click="removeStudent(student.user.id)">
                      移除
                    </n-button>
                  </n-space>
                </template>
              </n-thing>
            </n-list-item>
            <n-empty v-if="students.length === 0" description="暂无成员" />
          </n-list>
        </n-space>
      </n-tab-pane>
    </n-tabs>

    <!-- 创建/编辑作业对话框 -->
    <n-modal 
      v-model:show="showCreateAssignmentModal" 
      style="width: 900px" 
      :title="editingAssignment ? '编辑作业' : '创建作业'"
      preset="dialog"
    >
      <n-card>
        <n-scrollbar style="max-height: 65vh">
          <n-form :model="newAssignment" label-placement="top">
          <n-form-item label="作业标题" required>
            <n-input v-model:value="newAssignment.title" placeholder="请输入作业标题" />
          </n-form-item>
          <n-form-item label="作业描述">
            <n-input 
              v-model:value="newAssignment.description" 
              type="textarea" 
              :rows="3" 
              placeholder="请输入作业描述"
            />
          </n-form-item>
          <n-form-item label="截止时间">
            <n-date-picker
              v-model:value="newAssignment.deadline"
              type="datetime"
              clearable
              style="width: 100%"
            />
          </n-form-item>
          
          <n-divider />
          
          <n-form-item label="选择题目">
            <n-space vertical style="width: 100%">
              <n-button @click="openSelectProblemForAssignment">
                + 添加题目
              </n-button>
              
              <n-list v-if="selectedProblemsForAssignment.length > 0" bordered>
                <n-list-item v-for="(problem, index) in selectedProblemsForAssignment" :key="problem.id">
                  <n-thing>
                    <template #header>
                      {{ index + 1 }}. {{ problem.title }}
                    </template>
                    <template #header-extra>
                      <n-button 
                        size="small" 
                        type="error" 
                        @click="removeSelectedProblemForAssignment(index)"
                      >
                        移除
                      </n-button>
                    </template>
                  </n-thing>
                </n-list-item>
              </n-list>
              
              <n-alert v-else type="info">
                请添加作业题目
              </n-alert>
            </n-space>
          </n-form-item>
        </n-form>
        </n-scrollbar>
      </n-card>
      <template #action>
        <n-space>
          <n-button @click="closeAssignmentModal">取消</n-button>
          <n-button type="primary" @click="saveAssignment" :loading="savingAssignment">
            {{ editingAssignment ? '保存' : '创建' }}
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 为作业选择题目对话框 -->
    <n-modal v-model:show="showSelectProblemForAssignment" style="width: 800px" title="选择题目">
      <n-card>
        <n-space vertical>
          <n-input
            v-model:value="assignmentProblemSearchKeyword"
            placeholder="搜索题目标题..."
            clearable
            @update:value="searchProblemsForAssignment"
          >
            <template #prefix>
              <n-icon :component="SearchIcon" />
            </template>
          </n-input>

          <n-data-table
            :columns="selectProblemColumns"
            :data="availableProblemsForAssignment"
            :pagination="{ pageSize: 10 }"
            :loading="loadingProblemsForAssignment"
            max-height="400"
          />
        </n-space>
      </n-card>
      <template #action>
        <n-button @click="showSelectProblemForAssignment = false">关闭</n-button>
      </template>
    </n-modal>

    <!-- 作业详情对话框 -->
    <n-modal v-model:show="showAssignmentDetailModal" style="width: 900px" title="作业详情">
      <n-card v-if="viewingAssignment">
        <n-descriptions bordered :column="2">
          <n-descriptions-item label="作业标题" :span="2">
            {{ viewingAssignment.title }}
          </n-descriptions-item>
          <n-descriptions-item label="截止时间">
            {{ viewingAssignment.deadline ? formatDate(viewingAssignment.deadline) : '无限制' }}
          </n-descriptions-item>
          <n-descriptions-item label="状态">
            <n-tag v-if="viewingAssignment.is_expired" type="error">已截止</n-tag>
            <n-tag v-else type="success">进行中</n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="作业描述" :span="2">
            {{ viewingAssignment.description || '暂无描述' }}
          </n-descriptions-item>
        </n-descriptions>
        
        <n-divider />
        
        <h3>题目列表</h3>
        <n-list bordered v-if="assignmentProblems.length > 0">
          <n-list-item v-for="(item, index) in assignmentProblems" :key="item.id">
            <n-thing>
              <template #header>
                <n-space align="center">
                  {{ index + 1 }}. {{ item.problem.display_title }}
                  <n-tag v-if="item.problem.is_reference" type="info" size="small">引用</n-tag>
                </n-space>
              </template>
              <template #header-extra>
                <n-button 
                  size="small" 
                  type="primary"
                  tag="a"
                  :href="`/problem/${item.problem.reference_problem}/`"
                  target="_blank"
                >
                  做题
                </n-button>
              </template>
            </n-thing>
          </n-list-item>
        </n-list>
        <n-empty v-else description="暂无题目" />
      </n-card>
      <template #action>
        <n-button @click="showAssignmentDetailModal = false">关闭</n-button>
      </template>
    </n-modal>

    <!-- 作业成绩表对话框 -->
    <n-modal v-model:show="showAssignmentGradesModal" style="width: 95%; max-width: 1400px" title="作业成绩表">
      <n-card v-if="viewingAssignmentGrades">
        <n-space vertical>
          <n-descriptions bordered :column="2">
            <n-descriptions-item label="作业标题">
              {{ viewingAssignmentGrades.title }}
            </n-descriptions-item>
            <n-descriptions-item label="截止时间">
              {{ viewingAssignmentGrades.deadline ? formatDate(viewingAssignmentGrades.deadline) : '无限制' }}
            </n-descriptions-item>
          </n-descriptions>
          
          <n-divider />
          
          <n-data-table
            :columns="gradesColumns"
            :data="gradesData"
            :loading="loadingGrades"
            :pagination="{ pageSize: 50 }"
            :scroll-x="800"
            striped
          />
        </n-space>
      </n-card>
      <template #action>
        <n-button @click="showAssignmentGradesModal = false">关闭</n-button>
      </template>
    </n-modal>

    <!-- 引用主题库题目对话框 -->
    <n-modal v-model:show="showReferenceProblemModal" style="width: 800px" title="引用主题库题目">
      <n-card>
        <n-space vertical>
          <n-input
            v-model:value="problemSearchKeyword"
            placeholder="搜索题目标题..."
            clearable
            @update:value="searchMainProblems"
          >
            <template #prefix>
              <n-icon :component="SearchIcon" />
            </template>
          </n-input>

          <n-data-table
            :columns="mainProblemColumns"
            :data="mainProblems"
            :pagination="{ pageSize: 10 }"
            :loading="loadingMainProblems"
            max-height="400"
          />
        </n-space>
      </n-card>
      <template #action>
        <n-button @click="showReferenceProblemModal = false">关闭</n-button>
      </template>
    </n-modal>

    <!-- 创建/编辑班级专属题目对话框 - 已隐藏，只使用主题库引用 -->
    <n-modal 
      v-if="false"
      v-model:show="showProblemFormModal" 
      style="width: 95%; max-width: 1200px" 
      :title="editingProblem ? '编辑题目' : '创建班级专属题目'"
      :closable="false"
    >
      <n-card>
        <n-scrollbar style="max-height: 70vh">
          <n-form :model="problemForm" label-placement="top">
            <n-form-item label="题目标题" required>
              <n-input v-model:value="problemForm.title" placeholder="请输入题目标题" />
            </n-form-item>
            
            <n-form-item label="题目描述" required>
              <n-input
                v-model:value="problemForm.description"
                type="textarea"
                placeholder="请输入题目描述"
                :rows="8"
              />
            </n-form-item>

            <n-form-item label="输入格式">
              <n-input
                v-model:value="problemForm.input_format"
                type="textarea"
                placeholder="请输入输入格式说明"
                :rows="4"
              />
            </n-form-item>

            <n-form-item label="输出格式">
              <n-input
                v-model:value="problemForm.output_format"
                type="textarea"
                placeholder="请输入输出格式说明"
                :rows="4"
              />
            </n-form-item>

            <n-form-item label="样例数据">
              <n-space vertical style="width: 100%">
                <n-tabs type="line" animated>
                  <n-tab-pane
                    v-for="(sample, index) in problemForm.samples"
                    :key="index"
                    :name="'sample_' + index"
                    :tab="'样例 #' + (index + 1)"
                  >
                    <n-grid :cols="2" :x-gap="12">
                      <n-gi>
                        <h4>样例输入 #{{ index + 1 }}</h4>
                        <n-input
                          v-model:value="sample.input"
                          type="textarea"
                          placeholder="请输入样例输入"
                          :rows="8"
                        />
                      </n-gi>
                      <n-gi>
                        <h4>样例输出 #{{ index + 1 }}</h4>
                        <n-input
                          v-model:value="sample.output"
                          type="textarea"
                          placeholder="请输入样例输出"
                          :rows="8"
                        />
                      </n-gi>
                    </n-grid>
                    <n-space style="margin-top: 12px">
                      <n-button 
                        size="small" 
                        type="error" 
                        @click="removeSample(index)"
                        v-if="problemForm.samples.length > 1"
                      >
                        删除此样例
                      </n-button>
                    </n-space>
                  </n-tab-pane>
                </n-tabs>
                <n-button @click="addSample" size="small">
                  + 添加样例
                </n-button>
              </n-space>
            </n-form-item>

            <n-form-item label="数据范围">
              <n-input
                v-model:value="problemForm.hint"
                type="textarea"
                placeholder="请输入数据范围"
                :rows="4"
              />
            </n-form-item>

            <n-grid :cols="3" :x-gap="12">
              <n-gi>
                <n-form-item label="时间限制 (ms)">
                  <n-input-number
                    v-model:value="problemForm.time_limit"
                    :min="100"
                    :max="10000"
                    :step="100"
                    style="width: 100%"
                  >
                    <template #suffix>ms</template>
                  </n-input-number>
                </n-form-item>
              </n-gi>
              <n-gi>
                <n-form-item label="内存限制 (MB)">
                  <n-input-number
                    v-model:value="problemForm.memory_limit"
                    :min="16"
                    :max="2048"
                    :step="16"
                    style="width: 100%"
                  >
                    <template #suffix>MB</template>
                  </n-input-number>
                </n-form-item>
              </n-gi>
              <n-gi>
                <n-form-item label="难度">
                  <n-select
                    v-model:value="problemForm.difficulty"
                    :options="difficultyOptions"
                    placeholder="请选择难度"
                  />
                </n-form-item>
              </n-gi>
            </n-grid>

            <n-divider />
            
            <n-form-item label="测试数据上传">
              <n-space vertical style="width: 100%">
                <n-alert type="info">
                  上传包含测试数据的 .zip 文件。文件命名规则：<br>
                  • 输入文件：1.in, 2.in, 3.in, ...<br>
                  • 输出文件：1.ans (或 1.out), 2.ans, 3.ans, ...<br>
                  上传后会自动生成测试用例配置
                </n-alert>
                <n-upload
                  v-if="editingProblem"
                  :action="`/api/class/class-problem/${editingProblem.id}/upload-test-data/`"
                  :headers="{ Authorization: `Bearer ${getToken()}` }"
                  accept=".zip"
                  :max="1"
                  @finish="handleTestDataUploadFinish"
                  @error="handleTestDataUploadError"
                >
                  <n-button>选择 .zip 文件上传</n-button>
                </n-upload>
                <n-text depth="3" v-else>
                  请先创建题目，然后在编辑时上传测试数据
                </n-text>
              </n-space>
            </n-form-item>

            <n-form-item label="测试数据配置（高级）">
              <n-alert type="warning" style="margin-bottom: 12px">
                如果上传了测试数据 .zip 文件，系统会自动生成配置。<br>
                只有在需要自定义配置时才手动修改此项。
              </n-alert>
              <n-input
                v-model:value="problemForm.test_case_config"
                type="textarea"
                placeholder='示例：{"test_cases": [{"input": "1.in", "output": "1.out", "score": 10}]}'
                :rows="4"
              />
            </n-form-item>
          </n-form>
        </n-scrollbar>
      </n-card>
      <template #action>
        <n-space>
          <n-button @click="closeProblemFormModal">取消</n-button>
          <n-button type="primary" @click="saveProblem" :loading="savingProblem">
            {{ editingProblem ? '保存' : '创建' }}
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 题目详情对话框 - 已隐藏，引用的题目直接跳转主题库查看 -->
    <n-modal v-if="false" v-model:show="showProblemDetailModal" style="width: 800px" title="题目详情">
      <n-card v-if="viewingProblem">
        <n-descriptions bordered :column="2">
          <n-descriptions-item label="题目标题">
            {{ viewingProblem.display_title }}
          </n-descriptions-item>
          <n-descriptions-item label="类型">
            <n-tag v-if="viewingProblem.is_reference" type="info">引用主题库</n-tag>
            <n-tag v-else type="success">班级专属</n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="时间限制">
            {{ viewingProblem.time_limit }} ms
          </n-descriptions-item>
          <n-descriptions-item label="内存限制">
            {{ viewingProblem.memory_limit }} MB
          </n-descriptions-item>
          <n-descriptions-item label="难度" v-if="viewingProblem.difficulty">
            {{ viewingProblem.difficulty }}
          </n-descriptions-item>
          <n-descriptions-item label="题目描述" :span="2">
            <div style="white-space: pre-wrap">{{ viewingProblem.description }}</div>
          </n-descriptions-item>
        </n-descriptions>
      </n-card>
      <template #action>
        <n-space>
          <n-button @click="showProblemDetailModal = false">关闭</n-button>
          <n-button v-if="isTeacher && viewingProblem && !viewingProblem.is_reference" type="primary" @click="editProblem(viewingProblem)">
            编辑
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 添加成员对话框 -->
    <n-modal v-model:show="showAddStudentModal" preset="dialog" title="添加成员">
      <n-form :model="addStudentForm" label-placement="left" label-width="80">
        <n-form-item label="用户ID" required>
          <n-input-number v-model:value="addStudentForm.user_id" style="width: 100%" />
        </n-form-item>
        <n-form-item label="角色" required>
          <n-radio-group v-model:value="addStudentForm.role">
            <n-radio value="student">学生</n-radio>
            <n-radio value="teacher">教师</n-radio>
          </n-radio-group>
        </n-form-item>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="showAddStudentModal = false">取消</n-button>
          <n-button type="primary" @click="addStudent">添加</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue';
import { useRoute } from 'vue-router';
import { useMessage, NButton, NSpace, NTag, NTooltip, NRadioGroup, NRadio } from 'naive-ui';
import { Search as SearchIcon } from '@vicons/ionicons5';
import Axios from '@/plugins/axios';
import { difficultyOptions, difficulty as difficultyMap, difficultyColor } from '@/plugins/consts';
import store from '@/store';

const route = useRoute();
const message = useMessage();

const classId = route.params.id;
const classInfo = ref(null);
const assignments = ref([]);
const problems = ref([]);
const students = ref([]);
const mainProblems = ref([]);

// 模态框控制
const showCreateAssignmentModal = ref(false);
const showReferenceProblemModal = ref(false);
const showProblemFormModal = ref(false);
const showProblemDetailModal = ref(false);
const showAddStudentModal = ref(false);
const showSelectProblemForAssignment = ref(false);
const showAssignmentDetailModal = ref(false);
const showAssignmentGradesModal = ref(false);

// 加载状态
const loadingMainProblems = ref(false);
const savingProblem = ref(false);
const savingAssignment = ref(false);
const loadingProblemsForAssignment = ref(false);
const loadingGrades = ref(false);

// 搜索关键词
const problemSearchKeyword = ref('');
const assignmentProblemSearchKeyword = ref('');

// 表单数据
const newAssignment = ref({
  title: '',
  description: '',
  deadline: null,
  class_obj: classId,
});

const editingAssignment = ref(null);
const selectedProblemsForAssignment = ref([]);
const availableProblemsForAssignment = ref([]);
const viewingAssignment = ref(null);
const assignmentProblems = ref([]);
const viewingAssignmentGrades = ref(null);
const gradesData = ref([]);

const problemForm = ref({
  title: '',
  description: '',
  input_format: '',
  output_format: '',
  hint: '',
  time_limit: 1000,
  memory_limit: 128,
  difficulty: 0,
  samples: [
    { input: '', output: '' },
    { input: '', output: '' },
    { input: '', output: '' },
  ],
  test_case_config: '',
  class_obj: classId,
  is_reference: false,
});

const addStudentForm = ref({
  user_id: null,
  role: 'student',
});

const editingProblem = ref(null);
const viewingProblem = ref(null);

// 是否是教师
const isTeacher = computed(() => {
  return classInfo.value && classInfo.value.user_role === 'teacher';
});

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN');
};

// 题目表格列定义
const problemColumns = [
  {
    title: '序号',
    key: 'order',
    width: 80,
    render: (row, index) => index + 1,
  },
  {
    title: '题目标题',
    key: 'display_title',
    render: (row) => {
      // 如果是引用题目，可以点击跳转到主题库
      if (row.is_reference && row.reference_problem) {
        return h(
          'a',
          {
            href: `/problem/${row.reference_problem}/`,
            target: '_blank',
            style: 'color: #18a058; cursor: pointer; text-decoration: none',
            onMouseenter: (e) => { e.target.style.textDecoration = 'underline'; },
            onMouseleave: (e) => { e.target.style.textDecoration = 'none'; },
          },
          row.display_title
        );
      }
      // 班级专属题目显示详情
      return h('span', { style: 'cursor: pointer; color: #18a058', onClick: () => viewProblemDetail(row) }, row.display_title);
    },
  },
  {
    title: '难度',
    key: 'difficulty',
    width: 140,
    render: (row) => {
      const diffValue = row.difficulty || 0;
      return h(
        NButton,
        {
          size: 'small',
          color: difficultyColor[diffValue],
          style: 'cursor: default',
        },
        { default: () => difficultyMap[diffValue] }
      );
    },
  },
  {
    title: '类型',
    key: 'is_reference',
    width: 100,
    render: (row) => {
      return row.is_reference
        ? h(NTag, { type: 'info', size: 'small' }, { default: () => '引用' })
        : h(NTag, { type: 'success', size: 'small' }, { default: () => '专属' });
    },
  },
  {
    title: '时间/内存',
    key: 'limits',
    width: 140,
    render: (row) => `${row.time_limit}ms / ${row.memory_limit}MB`,
  },
  {
    title: '操作',
    key: 'actions',
    width: 250,
    render: (row) => {
      const buttons = [];
      
      // 做题按钮
      if (row.is_reference && row.reference_problem) {
        // 引用题目：跳转到主题库
        buttons.push(
          h(
            NButton,
            {
              size: 'small',
              type: 'primary',
              tag: 'a',
              href: `/problem/${row.reference_problem}/`,
              target: '_blank',
            },
            { default: () => '做题' }
          )
        );
      } else {
        // 班级专属题目：跳转到班级题目页
        buttons.push(
          h(
            NButton,
            {
              size: 'small',
              type: 'primary',
              tag: 'a',
              href: `/class/${classId}/problem/${row.id}/`,
              target: '_blank',
            },
            { default: () => '做题' }
          )
        );
      }
      
      // 编辑按钮（仅教师且班级专属题目）
      if (isTeacher.value && !row.is_reference) {
        buttons.push(
          h(NButton, { size: 'small', onClick: () => editProblem(row) }, { default: () => '编辑' })
        );
      }
      
      // 删除按钮（仅教师）
      if (isTeacher.value) {
        buttons.push(
          h(NButton, { size: 'small', type: 'error', onClick: () => deleteProblem(row.id) }, { default: () => '删除' })
        );
      }
      
      return h(NSpace, null, { default: () => buttons });
    },
  },
];

// 主题库题目表格列定义
const mainProblemColumns = [
  {
    title: 'ID',
    key: 'id',
    width: 80,
  },
  {
    title: '题目标题',
    key: 'title',
  },
  {
    title: '难度',
    key: 'difficulty',
    width: 100,
  },
  {
    title: '操作',
    key: 'actions',
    width: 120,
    render: (row) => {
      const isReferenced = problems.value.some(p => p.reference_problem === row.id);
      return h(
        NButton,
        {
          size: 'small',
          type: 'primary',
          disabled: isReferenced,
          onClick: () => referenceProblem(row.id),
        },
        { default: () => (isReferenced ? '已引用' : '引用') }
      );
    },
  },
];

// 为作业选择题目的表格列定义
const selectProblemColumns = [
  {
    title: 'ID',
    key: 'id',
    width: 80,
  },
  {
    title: '题目标题',
    key: 'title',
  },
  {
    title: '难度',
    key: 'difficulty',
    width: 120,
    render: (row) => {
      const diffValue = row.difficulty || 0;
      return h(
        NButton,
        {
          size: 'small',
          color: difficultyColor[diffValue],
          style: 'cursor: default',
        },
        { default: () => difficultyMap[diffValue] }
      );
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 120,
    render: (row) => {
      const isSelected = selectedProblemsForAssignment.value.some(p => p.id === row.id);
      return h(
        NButton,
        {
          size: 'small',
          type: 'primary',
          disabled: isSelected,
          onClick: () => addProblemToAssignment(row),
        },
        { default: () => (isSelected ? '已添加' : '添加') }
      );
    },
  },
];

// 成绩表列定义
const gradesColumns = computed(() => {
  if (!viewingAssignmentGrades.value || gradesData.value.length === 0) {
    return [];
  }
  
  const columns = [
    {
      title: '序号',
      key: 'rank',
      width: 80,
      fixed: 'left',
    },
    {
      title: '姓名',
      key: 'real_name',
      width: 100,
      fixed: 'left',
    },
  ];
  
  // 动态添加题目列
  if (gradesData.value[0] && gradesData.value[0].problems) {
    gradesData.value[0].problems.forEach((problem, index) => {
      columns.push({
        title: `题${index + 1}`,
        key: `problem_${problem.problem_id}`,
        width: 80,
        render: (row) => {
          const problemStatus = row.problems.find(p => p.problem_id === problem.problem_id);
          if (!problemStatus || !problemStatus.problem_id) {
            return h('span', { style: 'color: #999' }, '-');
          }
          
          // 创建可点击的标签
          const tagProps = {
            type: problemStatus.status === 'AC' ? 'success' : (problemStatus.status ? 'error' : 'default'),
            size: 'small',
            style: 'cursor: pointer;',
            onClick: () => {
              // 跳转到做题页面
              window.open(`/problem/${problemStatus.problem_id}`, '_blank');
            },
          };
          
          let tagContent;
          if (problemStatus.status === 'AC') {
            tagContent = h(NTag, tagProps, { default: () => 'AC' });
          } else if (problemStatus.status) {
            tagContent = h(NTag, tagProps, { default: () => problemStatus.status });
          } else {
            tagContent = h(NTag, { ...tagProps, type: 'default' }, { default: () => '-' });
          }
          
          // 使用 Tooltip 包裹标签，显示题目名称
          return h(
            NTooltip,
            { trigger: 'hover' },
            {
              trigger: () => tagContent,
              default: () => problem.problem_title || `题目 ${problemStatus.problem_id}`
            }
          );
        },
      });
    });
  }
  
  // 添加总完成数列
  columns.push({
    title: '完成数',
    key: 'completed_count',
    width: 100,
    render: (row) => {
      const total = row.problems.length;
      return `${row.completed_count || 0}/${total}`;
    },
  });
  
  return columns;
});

// API 调用
const fetchClassInfo = () => {
  Axios.get(`class/class/${classId}/`)
    .then(res => {
      classInfo.value = res;
    })
    .catch(() => {
      message.error('获取班级信息失败');
    });
};

const fetchAssignments = () => {
  Axios.get('class/assignment/', { params: { class_id: classId } })
    .then(res => {
      assignments.value = res;
    });
};

const fetchProblems = () => {
  Axios.get('class/class-problem/', { params: { class_id: classId } })
    .then(res => {
      problems.value = res;
    });
};

const fetchStudents = () => {
  if (isTeacher.value) {
    Axios.get(`class/class/${classId}/students/`)
      .then(res => {
        students.value = res;
      });
  }
};

const searchMainProblems = () => {
  loadingMainProblems.value = true;
  const params = {};
  if (problemSearchKeyword.value) {
    params.search = problemSearchKeyword.value;
  }
  
  Axios.get('problem/', { params })
    .then(res => {
      mainProblems.value = res.results || res;
    })
    .catch(() => {
      message.error('搜索题目失败');
    })
    .finally(() => {
      loadingMainProblems.value = false;
    });
};

// 题目操作
const openReferenceProblemModal = () => {
  showReferenceProblemModal.value = true;
  searchMainProblems();
};

const openCreateProblemModal = () => {
  editingProblem.value = null;
  problemForm.value = {
    title: '',
    description: '',
    input_format: '',
    output_format: '',
    hint: '',
    time_limit: 1000,
    memory_limit: 128,
    difficulty: 0,
    samples: [
      { input: '', output: '' },
      { input: '', output: '' },
      { input: '', output: '' },
    ],
    test_case_config: '',
    class_obj: classId,
    is_reference: false,
  };
  showProblemFormModal.value = true;
};

// 添加样例
const addSample = () => {
  problemForm.value.samples.push({ input: '', output: '' });
};

// 删除样例
const removeSample = (index) => {
  if (problemForm.value.samples.length > 1) {
    problemForm.value.samples.splice(index, 1);
  }
};

// 关闭题目表单
const closeProblemFormModal = () => {
  showProblemFormModal.value = false;
  editingProblem.value = null;
};

const referenceProblem = (problemId) => {
  Axios.post('class/class-problem/reference/', {
    class_id: classId,
    problem_id: problemId,
  })
    .then(() => {
      message.success('引用成功');
      fetchProblems();
    })
    .catch((err) => {
      message.error(err.response?.data?.error || '引用失败');
    });
};

const saveProblem = () => {
  if (!problemForm.value.title) {
    message.warning('请输入题目标题');
    return;
  }

  savingProblem.value = true;
  const request = editingProblem.value
    ? Axios.put(`class/class-problem/${editingProblem.value.id}/`, problemForm.value)
    : Axios.post('class/class-problem/', problemForm.value);

  request
    .then(() => {
      message.success(editingProblem.value ? '保存成功' : '创建成功');
      showProblemFormModal.value = false;
      fetchProblems();
    })
    .catch(() => {
      message.error(editingProblem.value ? '保存失败' : '创建失败');
    })
    .finally(() => {
      savingProblem.value = false;
    });
};

const viewProblemDetail = (problem) => {
  viewingProblem.value = problem;
  showProblemDetailModal.value = true;
};

const editProblem = (problem) => {
  editingProblem.value = problem;
  problemForm.value = {
    title: problem.title,
    description: problem.description,
    input_format: problem.input_format,
    output_format: problem.output_format,
    hint: problem.hint,
    time_limit: problem.time_limit,
    memory_limit: problem.memory_limit,
    difficulty: problem.difficulty,
    samples: problem.samples && problem.samples.length > 0 
      ? JSON.parse(JSON.stringify(problem.samples))
      : [{ input: '', output: '' }, { input: '', output: '' }, { input: '', output: '' }],
    test_case_config: problem.test_case_config || '',
    class_obj: classId,
    is_reference: false,
  };
  showProblemDetailModal.value = false;
  showProblemFormModal.value = true;
};

const deleteProblem = (id) => {
  Axios.delete(`class/class-problem/${id}/`)
    .then(() => {
      message.success('删除成功');
      fetchProblems();
    })
    .catch(() => {
      message.error('删除失败');
    });
};

// 作业操作
const saveAssignment = () => {
  if (!newAssignment.value.title) {
    message.warning('请输入作业标题');
    return;
  }
  
  if (selectedProblemsForAssignment.value.length === 0) {
    message.warning('请至少选择一道题目');
    return;
  }

  savingAssignment.value = true;
  const data = {
    ...newAssignment.value,
    deadline: newAssignment.value.deadline 
      ? new Date(newAssignment.value.deadline).toISOString() 
      : null,
    problem_ids: selectedProblemsForAssignment.value.map(p => p.id),
  };

  const request = editingAssignment.value
    ? Axios.put(`class/assignment/${editingAssignment.value.id}/`, data)
    : Axios.post('class/assignment/', data);

  request
    .then(() => {
      message.success(editingAssignment.value ? '保存成功' : '创建成功');
      closeAssignmentModal();
      fetchAssignments();
    })
    .catch(() => {
      message.error(editingAssignment.value ? '保存失败' : '创建失败');
    })
    .finally(() => {
      savingAssignment.value = false;
    });
};

const closeAssignmentModal = () => {
  showCreateAssignmentModal.value = false;
  editingAssignment.value = null;
  selectedProblemsForAssignment.value = [];
  newAssignment.value = {
    title: '',
    description: '',
    deadline: null,
    class_obj: classId,
  };
};

const openEditAssignmentModal = (assignment) => {
  editingAssignment.value = assignment;
  newAssignment.value = {
    title: assignment.title,
    description: assignment.description,
    deadline: assignment.deadline ? new Date(assignment.deadline).getTime() : null,
    class_obj: classId,
  };
  
  // 加载作业的题目
  Axios.get(`class/assignment/${assignment.id}/problems/`)
    .then((res) => {
      selectedProblemsForAssignment.value = res.map(item => ({
        id: item.problem.reference_problem,
        title: item.problem.display_title,
      }));
    });
  
  showCreateAssignmentModal.value = true;
};

const deleteAssignment = (id) => {
  Axios.delete(`class/assignment/${id}/`)
    .then(() => {
      message.success('删除成功');
      fetchAssignments();
    })
    .catch(() => {
      message.error('删除失败');
    });
};

const viewAssignmentDetail = (assignment) => {
  viewingAssignment.value = assignment;
  
  // 获取作业题目
  Axios.get(`class/assignment/${assignment.id}/problems/`)
    .then((res) => {
      assignmentProblems.value = res;
    });
  
  showAssignmentDetailModal.value = true;
};

const viewAssignmentGrades = (assignment) => {
  viewingAssignmentGrades.value = assignment;
  loadingGrades.value = true;
  
  // 获取成绩表数据
  Axios.get(`class/assignment/${assignment.id}/grades/`)
    .then((res) => {
      gradesData.value = res;
    })
    .catch(() => {
      message.error('加载成绩表失败');
    })
    .finally(() => {
      loadingGrades.value = false;
    });
  
  showAssignmentGradesModal.value = true;
};

// 为作业选择题目
const openSelectProblemForAssignment = () => {
  showSelectProblemForAssignment.value = true;
  assignmentProblemSearchKeyword.value = '';
  // 立即加载题目列表
  searchProblemsForAssignment();
};

const searchProblemsForAssignment = () => {
  loadingProblemsForAssignment.value = true;
  
  const params = {};
  if (assignmentProblemSearchKeyword.value) {
    params.search = assignmentProblemSearchKeyword.value;
  }
  
  Axios.get('problem/', { params })
    .then((res) => {
      availableProblemsForAssignment.value = res.results || res;
    })
    .finally(() => {
      loadingProblemsForAssignment.value = false;
    });
};

const addProblemToAssignment = (problem) => {
  // 检查是否已添加
  if (selectedProblemsForAssignment.value.find(p => p.id === problem.id)) {
    message.warning('该题目已添加');
    return;
  }
  
  selectedProblemsForAssignment.value.push({
    id: problem.id,
    title: problem.title,
  });
  message.success('添加成功');
};

const removeSelectedProblemForAssignment = (index) => {
  selectedProblemsForAssignment.value.splice(index, 1);
};

// 学生操作
const addStudent = () => {
  if (!addStudentForm.value.user_id) {
    message.warning('请输入用户ID');
    return;
  }

  Axios.post(`class/class/${classId}/add_student/`, addStudentForm.value)
    .then(() => {
      message.success('添加成功');
      showAddStudentModal.value = false;
      addStudentForm.value = { user_id: null, role: 'student' };
      fetchStudents();
    })
    .catch(err => {
      message.error(err.response?.data?.error || '添加失败');
    });
};

const removeStudent = (userId) => {
  Axios.post(`class/class/${classId}/remove_student/`, { user_id: userId })
    .then(() => {
      message.success('移除成功');
      fetchStudents();
    })
    .catch(() => {
      message.error('移除失败');
    });
};

const toggleMemberRole = (member) => {
  const newRole = member.role === 'teacher' ? 'student' : 'teacher';
  const roleText = newRole === 'teacher' ? '教师' : '学生';
  
  Axios.post(`class/class/${classId}/update_member_role/`, { 
    user_id: member.user.id,
    role: newRole
  })
    .then(() => {
      message.success(`已切换为${roleText}`);
      fetchStudents();
    })
    .catch(err => {
      message.error(err.response?.data?.error || '切换失败');
    });
};

// 获取认证令牌
const getToken = () => {
  return store.state.user.token || '';
};

// 处理测试数据上传完成
const handleTestDataUploadFinish = ({ file, event }) => {
  try {
    const response = JSON.parse(event.target.response);
    if (response.message) {
      message.success(response.message);
      // 刷新题目列表
      fetchProblems();
      // 如果有返回的文件列表，可以显示
      if (response.files) {
        message.info(`上传了 ${response.files.length} 个文件`);
      }
    }
  } catch (e) {
    message.error('上传成功但解析响应失败');
  }
};

// 处理测试数据上传错误
const handleTestDataUploadError = ({ file, event }) => {
  try {
    const response = JSON.parse(event.target.response);
    message.error(response.error || '上传失败');
  } catch (e) {
    message.error('上传失败');
  }
};

onMounted(() => {
  fetchClassInfo();
  fetchAssignments();
  fetchProblems();
  setTimeout(() => {
    if (isTeacher.value) {
      fetchStudents();
    }
  }, 500);
});
</script>
��"(6b457f522aa10499b55789fae01ec35627afe7b623file:///root/frontend-naive/src/pages/class/_id.vue:file:///root/frontend-naive