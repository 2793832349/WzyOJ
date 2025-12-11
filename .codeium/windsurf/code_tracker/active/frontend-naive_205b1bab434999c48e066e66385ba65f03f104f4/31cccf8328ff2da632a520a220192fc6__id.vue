ÿË<template>
  <div v-if="classInfo">
    <h1>{{ classInfo.title }}</h1>
    <p>{{ classInfo.description }}</p>

    <n-tabs type="line" animated>
      <!-- ä½œä¸šåˆ—è¡¨ -->
      <n-tab-pane name="assignments" tab="ä½œä¸š">
        <n-space vertical>
          <n-button
            v-if="isTeacher"
            type="primary"
            @click="showCreateAssignmentModal = true"
          >
            åˆ›å»ºä½œä¸š
          </n-button>
          
          <n-list>
            <n-list-item v-for="assignment in assignments" :key="assignment.id">
              <n-thing>
                <template #header>
                  <n-space align="center">
                    {{ assignment.title }}
                    <n-tag v-if="assignment.is_expired" type="error">å·²æˆªæ­¢</n-tag>
                    <n-tag v-if="assignment.is_hidden" type="warning">éšè—</n-tag>
                  </n-space>
                </template>
                <template #description>
                  <span v-if="assignment.deadline">
                    æˆªæ­¢æ—¶é—´ï¼š{{ formatDate(assignment.deadline) }}
                  </span>
                </template>
                {{ assignment.description || 'æš‚æ— æè¿°' }}
                <template #action>
                  <n-space>
                    <n-button size="small" type="primary" @click="viewAssignmentDetail(assignment)">
                      æŸ¥çœ‹ä½œä¸š
                    </n-button>
                    <n-button v-if="isTeacher" size="small" @click="viewAssignmentGrades(assignment)">
                      æˆç»©è¡¨
                    </n-button>
                    <n-button v-if="isTeacher" size="small" @click="openEditAssignmentModal(assignment)">
                      ç¼–è¾‘
                    </n-button>
                    <n-button v-if="isTeacher" size="small" type="error" @click="deleteAssignment(assignment.id)">
                      åˆ é™¤
                    </n-button>
                  </n-space>
                </template>
              </n-thing>
            </n-list-item>
            <n-empty v-if="assignments.length === 0" description="æš‚æ— ä½œä¸š" />
          </n-list>
        </n-space>
      </n-tab-pane>

      <!-- é¢˜ç›®åˆ—è¡¨ -->
      <n-tab-pane name="problems" tab="é¢˜ç›®åº“">
        <n-space vertical>
          <n-space v-if="isTeacher">
            <n-button type="primary" @click="openReferenceProblemModal">
              å¼•ç”¨ä¸»é¢˜åº“é¢˜ç›®
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

      <!-- æˆå‘˜ç®¡ç† -->
      <n-tab-pane name="students" tab="ç®¡ç†" v-if="isTeacher">
        <n-space vertical>
          <n-button type="primary" @click="showAddStudentModal = true">
            æ·»åŠ æˆå‘˜
          </n-button>

          <n-list>
            <n-list-item v-for="student in students" :key="student.id">
              <n-thing>
                <template #header>
                  <n-space align="center">
                    <span>{{ student.user.username }}</span>
                    <span v-if="student.user.real_name">({{ student.user.real_name }})</span>
                    <n-tag :type="student.role === 'teacher' ? 'success' : 'info'" size="small">
                      {{ student.role === 'teacher' ? 'æ•™å¸ˆ' : 'å­¦ç”Ÿ' }}
                    </n-tag>
                  </n-space>
                </template>
                <template #description>
                  å­¦å·ï¼š{{ student.user.student_id || 'æ— ' }}
                </template>
                <template #action>
                  <n-space>
                    <n-button 
                      size="small" 
                      @click="toggleMemberRole(student)"
                    >
                      åˆ‡æ¢ä¸º{{ student.role === 'teacher' ? 'å­¦ç”Ÿ' : 'æ•™å¸ˆ' }}
                    </n-button>
                    <n-button size="small" type="error" @click="removeStudent(student.user.id)">
                      ç§»é™¤
                    </n-button>
                  </n-space>
                </template>
              </n-thing>
            </n-list-item>
            <n-empty v-if="students.length === 0" description="æš‚æ— æˆå‘˜" />
          </n-list>
        </n-space>
      </n-tab-pane>
    </n-tabs>

    <!-- åˆ›å»º/ç¼–è¾‘ä½œä¸šå¯¹è¯æ¡† -->
    <n-modal 
      v-model:show="showCreateAssignmentModal" 
      style="width: 900px" 
      :title="editingAssignment ? 'ç¼–è¾‘ä½œä¸š' : 'åˆ›å»ºä½œä¸š'"
      preset="dialog"
    >
      <n-card>
        <n-scrollbar style="max-height: 65vh">
          <n-form :model="newAssignment" label-placement="top">
          <n-form-item label="ä½œä¸šæ ‡é¢˜" required>
            <n-input v-model:value="newAssignment.title" placeholder="è¯·è¾“å…¥ä½œä¸šæ ‡é¢˜" />
          </n-form-item>
          <n-form-item label="ä½œä¸šæè¿°">
            <n-input 
              v-model:value="newAssignment.description" 
              type="textarea" 
              :rows="3" 
              placeholder="è¯·è¾“å…¥ä½œä¸šæè¿°"
            />
          </n-form-item>
          <n-form-item label="æˆªæ­¢æ—¶é—´">
            <n-date-picker
              v-model:value="newAssignment.deadline"
              type="datetime"
              clearable
              style="width: 100%"
            />
          </n-form-item>
          
          <n-divider />
          
          <n-form-item label="é€‰æ‹©é¢˜ç›®">
            <n-space vertical style="width: 100%">
              <n-button @click="openSelectProblemForAssignment">
                + æ·»åŠ é¢˜ç›®
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
                        ç§»é™¤
                      </n-button>
                    </template>
                  </n-thing>
                </n-list-item>
              </n-list>
              
              <n-alert v-else type="info">
                è¯·æ·»åŠ ä½œä¸šé¢˜ç›®
              </n-alert>
            </n-space>
          </n-form-item>
        </n-form>
        </n-scrollbar>
      </n-card>
      <template #action>
        <n-space>
          <n-button @click="closeAssignmentModal">å–æ¶ˆ</n-button>
          <n-button type="primary" @click="saveAssignment" :loading="savingAssignment">
            {{ editingAssignment ? 'ä¿å­˜' : 'åˆ›å»º' }}
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- ä¸ºä½œä¸šé€‰æ‹©é¢˜ç›®å¯¹è¯æ¡† -->
    <n-modal v-model:show="showSelectProblemForAssignment" style="width: 800px" title="é€‰æ‹©é¢˜ç›®">
      <n-card>
        <n-space vertical>
          <n-input
            v-model:value="assignmentProblemSearchKeyword"
            placeholder="æœç´¢é¢˜ç›®æ ‡é¢˜..."
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
        <n-button @click="showSelectProblemForAssignment = false">å…³é—­</n-button>
      </template>
    </n-modal>

    <!-- ä½œä¸šè¯¦æƒ…å¯¹è¯æ¡† -->
    <n-modal v-model:show="showAssignmentDetailModal" style="width: 900px" title="ä½œä¸šè¯¦æƒ…">
      <n-card v-if="viewingAssignment">
        <n-descriptions bordered :column="2">
          <n-descriptions-item label="ä½œä¸šæ ‡é¢˜" :span="2">
            {{ viewingAssignment.title }}
          </n-descriptions-item>
          <n-descriptions-item label="æˆªæ­¢æ—¶é—´">
            {{ viewingAssignment.deadline ? formatDate(viewingAssignment.deadline) : 'æ— é™åˆ¶' }}
          </n-descriptions-item>
          <n-descriptions-item label="çŠ¶æ€">
            <n-tag v-if="viewingAssignment.is_expired" type="error">å·²æˆªæ­¢</n-tag>
            <n-tag v-else type="success">è¿›è¡Œä¸­</n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="ä½œä¸šæè¿°" :span="2">
            {{ viewingAssignment.description || 'æš‚æ— æè¿°' }}
          </n-descriptions-item>
        </n-descriptions>
        
        <n-divider />
        
        <h3>é¢˜ç›®åˆ—è¡¨</h3>
        <n-list bordered v-if="assignmentProblems.length > 0">
          <n-list-item v-for="(item, index) in assignmentProblems" :key="item.id">
            <n-thing>
              <template #header>
                <n-space align="center">
                  {{ index + 1 }}. {{ item.problem.display_title }}
                  <n-tag v-if="item.problem.is_reference" type="info" size="small">å¼•ç”¨</n-tag>
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
                  åšé¢˜
                </n-button>
              </template>
            </n-thing>
          </n-list-item>
        </n-list>
        <n-empty v-else description="æš‚æ— é¢˜ç›®" />
      </n-card>
      <template #action>
        <n-button @click="showAssignmentDetailModal = false">å…³é—­</n-button>
      </template>
    </n-modal>

    <!-- ä½œä¸šæˆç»©è¡¨å¯¹è¯æ¡† -->
    <n-modal v-model:show="showAssignmentGradesModal" style="width: 95%; max-width: 1400px" title="ä½œä¸šæˆç»©è¡¨">
      <n-card v-if="viewingAssignmentGrades">
        <n-space vertical>
          <n-descriptions bordered :column="2">
            <n-descriptions-item label="ä½œä¸šæ ‡é¢˜">
              {{ viewingAssignmentGrades.title }}
            </n-descriptions-item>
            <n-descriptions-item label="æˆªæ­¢æ—¶é—´">
              {{ viewingAssignmentGrades.deadline ? formatDate(viewingAssignmentGrades.deadline) : 'æ— é™åˆ¶' }}
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
        <n-button @click="showAssignmentGradesModal = false">å…³é—­</n-button>
      </template>
    </n-modal>

    <!-- å¼•ç”¨ä¸»é¢˜åº“é¢˜ç›®å¯¹è¯æ¡† -->
    <n-modal v-model:show="showReferenceProblemModal" style="width: 800px" title="å¼•ç”¨ä¸»é¢˜åº“é¢˜ç›®">
      <n-card>
        <n-space vertical>
          <n-input
            v-model:value="problemSearchKeyword"
            placeholder="æœç´¢é¢˜ç›®æ ‡é¢˜..."
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
        <n-button @click="showReferenceProblemModal = false">å…³é—­</n-button>
      </template>
    </n-modal>

    <!-- åˆ›å»º/ç¼–è¾‘ç­çº§ä¸“å±é¢˜ç›®å¯¹è¯æ¡† - å·²éšè—ï¼Œåªä½¿ç”¨ä¸»é¢˜åº“å¼•ç”¨ -->
    <n-modal 
      v-if="false"
      v-model:show="showProblemFormModal" 
      style="width: 95%; max-width: 1200px" 
      :title="editingProblem ? 'ç¼–è¾‘é¢˜ç›®' : 'åˆ›å»ºç­çº§ä¸“å±é¢˜ç›®'"
      :closable="false"
    >
      <n-card>
        <n-scrollbar style="max-height: 70vh">
          <n-form :model="problemForm" label-placement="top">
            <n-form-item label="é¢˜ç›®æ ‡é¢˜" required>
              <n-input v-model:value="problemForm.title" placeholder="è¯·è¾“å…¥é¢˜ç›®æ ‡é¢˜" />
            </n-form-item>
            
            <n-form-item label="é¢˜ç›®æè¿°" required>
              <n-input
                v-model:value="problemForm.description"
                type="textarea"
                placeholder="è¯·è¾“å…¥é¢˜ç›®æè¿°"
                :rows="8"
              />
            </n-form-item>

            <n-form-item label="è¾“å…¥æ ¼å¼">
              <n-input
                v-model:value="problemForm.input_format"
                type="textarea"
                placeholder="è¯·è¾“å…¥è¾“å…¥æ ¼å¼è¯´æ˜"
                :rows="4"
              />
            </n-form-item>

            <n-form-item label="è¾“å‡ºæ ¼å¼">
              <n-input
                v-model:value="problemForm.output_format"
                type="textarea"
                placeholder="è¯·è¾“å…¥è¾“å‡ºæ ¼å¼è¯´æ˜"
                :rows="4"
              />
            </n-form-item>

            <n-form-item label="æ ·ä¾‹æ•°æ®">
              <n-space vertical style="width: 100%">
                <n-tabs type="line" animated>
                  <n-tab-pane
                    v-for="(sample, index) in problemForm.samples"
                    :key="index"
                    :name="'sample_' + index"
                    :tab="'æ ·ä¾‹ #' + (index + 1)"
                  >
                    <n-grid :cols="2" :x-gap="12">
                      <n-gi>
                        <h4>æ ·ä¾‹è¾“å…¥ #{{ index + 1 }}</h4>
                        <n-input
                          v-model:value="sample.input"
                          type="textarea"
                          placeholder="è¯·è¾“å…¥æ ·ä¾‹è¾“å…¥"
                          :rows="8"
                        />
                      </n-gi>
                      <n-gi>
                        <h4>æ ·ä¾‹è¾“å‡º #{{ index + 1 }}</h4>
                        <n-input
                          v-model:value="sample.output"
                          type="textarea"
                          placeholder="è¯·è¾“å…¥æ ·ä¾‹è¾“å‡º"
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
                        åˆ é™¤æ­¤æ ·ä¾‹
                      </n-button>
                    </n-space>
                  </n-tab-pane>
                </n-tabs>
                <n-button @click="addSample" size="small">
                  + æ·»åŠ æ ·ä¾‹
                </n-button>
              </n-space>
            </n-form-item>

            <n-form-item label="æ•°æ®èŒƒå›´">
              <n-input
                v-model:value="problemForm.hint"
                type="textarea"
                placeholder="è¯·è¾“å…¥æ•°æ®èŒƒå›´"
                :rows="4"
              />
            </n-form-item>

            <n-grid :cols="3" :x-gap="12">
              <n-gi>
                <n-form-item label="æ—¶é—´é™åˆ¶ (ms)">
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
                <n-form-item label="å†…å­˜é™åˆ¶ (MB)">
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
                <n-form-item label="éš¾åº¦">
                  <n-select
                    v-model:value="problemForm.difficulty"
                    :options="difficultyOptions"
                    placeholder="è¯·é€‰æ‹©éš¾åº¦"
                  />
                </n-form-item>
              </n-gi>
            </n-grid>

            <n-divider />
            
            <n-form-item label="æµ‹è¯•æ•°æ®ä¸Šä¼ ">
              <n-space vertical style="width: 100%">
                <n-alert type="info">
                  ä¸Šä¼ åŒ…å«æµ‹è¯•æ•°æ®çš„ .zip æ–‡ä»¶ã€‚æ–‡ä»¶å‘½åè§„åˆ™ï¼š<br>
                  â€¢ è¾“å…¥æ–‡ä»¶ï¼š1.in, 2.in, 3.in, ...<br>
                  â€¢ è¾“å‡ºæ–‡ä»¶ï¼š1.ans (æˆ– 1.out), 2.ans, 3.ans, ...<br>
                  ä¸Šä¼ åä¼šè‡ªåŠ¨ç”Ÿæˆæµ‹è¯•ç”¨ä¾‹é…ç½®
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
                  <n-button>é€‰æ‹© .zip æ–‡ä»¶ä¸Šä¼ </n-button>
                </n-upload>
                <n-text depth="3" v-else>
                  è¯·å…ˆåˆ›å»ºé¢˜ç›®ï¼Œç„¶ååœ¨ç¼–è¾‘æ—¶ä¸Šä¼ æµ‹è¯•æ•°æ®
                </n-text>
              </n-space>
            </n-form-item>

            <n-form-item label="æµ‹è¯•æ•°æ®é…ç½®ï¼ˆé«˜çº§ï¼‰">
              <n-alert type="warning" style="margin-bottom: 12px">
                å¦‚æœä¸Šä¼ äº†æµ‹è¯•æ•°æ® .zip æ–‡ä»¶ï¼Œç³»ç»Ÿä¼šè‡ªåŠ¨ç”Ÿæˆé…ç½®ã€‚<br>
                åªæœ‰åœ¨éœ€è¦è‡ªå®šä¹‰é…ç½®æ—¶æ‰æ‰‹åŠ¨ä¿®æ”¹æ­¤é¡¹ã€‚
              </n-alert>
              <n-input
                v-model:value="problemForm.test_case_config"
                type="textarea"
                placeholder='ç¤ºä¾‹ï¼š{"test_cases": [{"input": "1.in", "output": "1.out", "score": 10}]}'
                :rows="4"
              />
            </n-form-item>
          </n-form>
        </n-scrollbar>
      </n-card>
      <template #action>
        <n-space>
          <n-button @click="closeProblemFormModal">å–æ¶ˆ</n-button>
          <n-button type="primary" @click="saveProblem" :loading="savingProblem">
            {{ editingProblem ? 'ä¿å­˜' : 'åˆ›å»º' }}
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- é¢˜ç›®è¯¦æƒ…å¯¹è¯æ¡† - å·²éšè—ï¼Œå¼•ç”¨çš„é¢˜ç›®ç›´æ¥è·³è½¬ä¸»é¢˜åº“æŸ¥çœ‹ -->
    <n-modal v-if="false" v-model:show="showProblemDetailModal" style="width: 800px" title="é¢˜ç›®è¯¦æƒ…">
      <n-card v-if="viewingProblem">
        <n-descriptions bordered :column="2">
          <n-descriptions-item label="é¢˜ç›®æ ‡é¢˜">
            {{ viewingProblem.display_title }}
          </n-descriptions-item>
          <n-descriptions-item label="ç±»å‹">
            <n-tag v-if="viewingProblem.is_reference" type="info">å¼•ç”¨ä¸»é¢˜åº“</n-tag>
            <n-tag v-else type="success">ç­çº§ä¸“å±</n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="æ—¶é—´é™åˆ¶">
            {{ viewingProblem.time_limit }} ms
          </n-descriptions-item>
          <n-descriptions-item label="å†…å­˜é™åˆ¶">
            {{ viewingProblem.memory_limit }} MB
          </n-descriptions-item>
          <n-descriptions-item label="éš¾åº¦" v-if="viewingProblem.difficulty">
            {{ viewingProblem.difficulty }}
          </n-descriptions-item>
          <n-descriptions-item label="é¢˜ç›®æè¿°" :span="2">
            <div style="white-space: pre-wrap">{{ viewingProblem.description }}</div>
          </n-descriptions-item>
        </n-descriptions>
      </n-card>
      <template #action>
        <n-space>
          <n-button @click="showProblemDetailModal = false">å…³é—­</n-button>
          <n-button v-if="isTeacher && viewingProblem && !viewingProblem.is_reference" type="primary" @click="editProblem(viewingProblem)">
            ç¼–è¾‘
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- æ·»åŠ æˆå‘˜å¯¹è¯æ¡† -->
    <n-modal v-model:show="showAddStudentModal" preset="dialog" title="æ·»åŠ æˆå‘˜">
      <n-form :model="addStudentForm" label-placement="left" label-width="80">
        <n-form-item label="ç”¨æˆ·ID" required>
          <n-input-number v-model:value="addStudentForm.user_id" style="width: 100%" />
        </n-form-item>
        <n-form-item label="è§’è‰²" required>
          <n-radio-group v-model:value="addStudentForm.role">
            <n-radio value="student">å­¦ç”Ÿ</n-radio>
            <n-radio value="teacher">æ•™å¸ˆ</n-radio>
          </n-radio-group>
        </n-form-item>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="showAddStudentModal = false">å–æ¶ˆ</n-button>
          <n-button type="primary" @click="addStudent">æ·»åŠ </n-button>
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

// æ¨¡æ€æ¡†æ§åˆ¶
const showCreateAssignmentModal = ref(false);
const showReferenceProblemModal = ref(false);
const showProblemFormModal = ref(false);
const showProblemDetailModal = ref(false);
const showAddStudentModal = ref(false);
const showSelectProblemForAssignment = ref(false);
const showAssignmentDetailModal = ref(false);
const showAssignmentGradesModal = ref(false);

// åŠ è½½çŠ¶æ€
const loadingMainProblems = ref(false);
const savingProblem = ref(false);
const savingAssignment = ref(false);
const loadingProblemsForAssignment = ref(false);
const loadingGrades = ref(false);

// æœç´¢å…³é”®è¯
const problemSearchKeyword = ref('');
const assignmentProblemSearchKeyword = ref('');

// è¡¨å•æ•°æ®
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

// æ˜¯å¦æ˜¯æ•™å¸ˆ
const isTeacher = computed(() => {
  return classInfo.value && classInfo.value.user_role === 'teacher';
});

// æ ¼å¼åŒ–æ—¥æœŸ
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN');
};

// é¢˜ç›®è¡¨æ ¼åˆ—å®šä¹‰
const problemColumns = [
  {
    title: 'åºå·',
    key: 'order',
    width: 80,
    render: (row, index) => index + 1,
  },
  {
    title: 'é¢˜ç›®æ ‡é¢˜',
    key: 'display_title',
    render: (row) => {
      // å¦‚æœæ˜¯å¼•ç”¨é¢˜ç›®ï¼Œå¯ä»¥ç‚¹å‡»è·³è½¬åˆ°ä¸»é¢˜åº“
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
      // ç­çº§ä¸“å±é¢˜ç›®æ˜¾ç¤ºè¯¦æƒ…
      return h('span', { style: 'cursor: pointer; color: #18a058', onClick: () => viewProblemDetail(row) }, row.display_title);
    },
  },
  {
    title: 'éš¾åº¦',
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
    title: 'ç±»å‹',
    key: 'is_reference',
    width: 100,
    render: (row) => {
      return row.is_reference
        ? h(NTag, { type: 'info', size: 'small' }, { default: () => 'å¼•ç”¨' })
        : h(NTag, { type: 'success', size: 'small' }, { default: () => 'ä¸“å±' });
    },
  },
  {
    title: 'æ—¶é—´/å†…å­˜',
    key: 'limits',
    width: 140,
    render: (row) => `${row.time_limit}ms / ${row.memory_limit}MB`,
  },
  {
    title: 'æ“ä½œ',
    key: 'actions',
    width: 250,
    render: (row) => {
      const buttons = [];
      
      // åšé¢˜æŒ‰é’®
      if (row.is_reference && row.reference_problem) {
        // å¼•ç”¨é¢˜ç›®ï¼šè·³è½¬åˆ°ä¸»é¢˜åº“
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
            { default: () => 'åšé¢˜' }
          )
        );
      } else {
        // ç­çº§ä¸“å±é¢˜ç›®ï¼šè·³è½¬åˆ°ç­çº§é¢˜ç›®é¡µ
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
            { default: () => 'åšé¢˜' }
          )
        );
      }
      
      // ç¼–è¾‘æŒ‰é’®ï¼ˆä»…æ•™å¸ˆä¸”ç­çº§ä¸“å±é¢˜ç›®ï¼‰
      if (isTeacher.value && !row.is_reference) {
        buttons.push(
          h(NButton, { size: 'small', onClick: () => editProblem(row) }, { default: () => 'ç¼–è¾‘' })
        );
      }
      
      // åˆ é™¤æŒ‰é’®ï¼ˆä»…æ•™å¸ˆï¼‰
      if (isTeacher.value) {
        buttons.push(
          h(NButton, { size: 'small', type: 'error', onClick: () => deleteProblem(row.id) }, { default: () => 'åˆ é™¤' })
        );
      }
      
      return h(NSpace, null, { default: () => buttons });
    },
  },
];

// ä¸»é¢˜åº“é¢˜ç›®è¡¨æ ¼åˆ—å®šä¹‰
const mainProblemColumns = [
  {
    title: 'ID',
    key: 'id',
    width: 80,
  },
  {
    title: 'é¢˜ç›®æ ‡é¢˜',
    key: 'title',
  },
  {
    title: 'éš¾åº¦',
    key: 'difficulty',
    width: 100,
  },
  {
    title: 'æ“ä½œ',
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
        { default: () => (isReferenced ? 'å·²å¼•ç”¨' : 'å¼•ç”¨') }
      );
    },
  },
];

// ä¸ºä½œä¸šé€‰æ‹©é¢˜ç›®çš„è¡¨æ ¼åˆ—å®šä¹‰
const selectProblemColumns = [
  {
    title: 'ID',
    key: 'id',
    width: 80,
  },
  {
    title: 'é¢˜ç›®æ ‡é¢˜',
    key: 'title',
  },
  {
    title: 'éš¾åº¦',
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
    title: 'æ“ä½œ',
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
        { default: () => (isSelected ? 'å·²æ·»åŠ ' : 'æ·»åŠ ') }
      );
    },
  },
];

// æˆç»©è¡¨åˆ—å®šä¹‰
const gradesColumns = computed(() => {
  if (!viewingAssignmentGrades.value || gradesData.value.length === 0) {
    return [];
  }
  
  const columns = [
    {
      title: 'åºå·',
      key: 'rank',
      width: 80,
      fixed: 'left',
    },
    {
      title: 'å§“å',
      key: 'real_name',
      width: 100,
      fixed: 'left',
    },
  ];
  
  // åŠ¨æ€æ·»åŠ é¢˜ç›®åˆ—
  if (gradesData.value[0] && gradesData.value[0].problems) {
    gradesData.value[0].problems.forEach((problem, index) => {
      columns.push({
        title: `é¢˜${index + 1}`,
        key: `problem_${problem.problem_id}`,
        width: 80,
        render: (row) => {
          const problemStatus = row.problems.find(p => p.problem_id === problem.problem_id);
          if (!problemStatus || !problemStatus.problem_id) {
            return h('span', { style: 'color: #999' }, '-');
          }
          
          // åˆ›å»ºå¯ç‚¹å‡»çš„æ ‡ç­¾
          const tagProps = {
            type: problemStatus.status === 'AC' ? 'success' : (problemStatus.status ? 'error' : 'default'),
            size: 'small',
            style: 'cursor: pointer;',
            onClick: () => {
              // è·³è½¬åˆ°åšé¢˜é¡µé¢
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
          
          // ä½¿ç”¨ Tooltip åŒ…è£¹æ ‡ç­¾ï¼Œæ˜¾ç¤ºé¢˜ç›®åç§°
          return h(
            NTooltip,
            { trigger: 'hover' },
            {
              trigger: () => tagContent,
              default: () => problem.problem_title || `é¢˜ç›® ${problemStatus.problem_id}`
            }
          );
        },
      });
    });
  }
  
  // æ·»åŠ æ€»å®Œæˆæ•°åˆ—
  columns.push({
    title: 'å®Œæˆæ•°',
    key: 'completed_count',
    width: 100,
    render: (row) => {
      const total = row.problems.length;
      return `${row.completed_count || 0}/${total}`;
    },
  });
  
  return columns;
});

// API è°ƒç”¨
const fetchClassInfo = () => {
  Axios.get(`class/class/${classId}/`)
    .then(res => {
      classInfo.value = res;
    })
    .catch(() => {
      message.error('è·å–ç­çº§ä¿¡æ¯å¤±è´¥');
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
      message.error('æœç´¢é¢˜ç›®å¤±è´¥');
    })
    .finally(() => {
      loadingMainProblems.value = false;
    });
};

// é¢˜ç›®æ“ä½œ
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

// æ·»åŠ æ ·ä¾‹
const addSample = () => {
  problemForm.value.samples.push({ input: '', output: '' });
};

// åˆ é™¤æ ·ä¾‹
const removeSample = (index) => {
  if (problemForm.value.samples.length > 1) {
    problemForm.value.samples.splice(index, 1);
  }
};

// å…³é—­é¢˜ç›®è¡¨å•
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
      message.success('å¼•ç”¨æˆåŠŸ');
      fetchProblems();
    })
    .catch((err) => {
      message.error(err.response?.data?.error || 'å¼•ç”¨å¤±è´¥');
    });
};

const saveProblem = () => {
  if (!problemForm.value.title) {
    message.warning('è¯·è¾“å…¥é¢˜ç›®æ ‡é¢˜');
    return;
  }

  savingProblem.value = true;
  const request = editingProblem.value
    ? Axios.put(`class/class-problem/${editingProblem.value.id}/`, problemForm.value)
    : Axios.post('class/class-problem/', problemForm.value);

  request
    .then(() => {
      message.success(editingProblem.value ? 'ä¿å­˜æˆåŠŸ' : 'åˆ›å»ºæˆåŠŸ');
      showProblemFormModal.value = false;
      fetchProblems();
    })
    .catch(() => {
      message.error(editingProblem.value ? 'ä¿å­˜å¤±è´¥' : 'åˆ›å»ºå¤±è´¥');
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
      message.success('åˆ é™¤æˆåŠŸ');
      fetchProblems();
    })
    .catch(() => {
      message.error('åˆ é™¤å¤±è´¥');
    });
};

// ä½œä¸šæ“ä½œ
const saveAssignment = () => {
  if (!newAssignment.value.title) {
    message.warning('è¯·è¾“å…¥ä½œä¸šæ ‡é¢˜');
    return;
  }
  
  if (selectedProblemsForAssignment.value.length === 0) {
    message.warning('è¯·è‡³å°‘é€‰æ‹©ä¸€é“é¢˜ç›®');
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
      message.success(editingAssignment.value ? 'ä¿å­˜æˆåŠŸ' : 'åˆ›å»ºæˆåŠŸ');
      closeAssignmentModal();
      fetchAssignments();
    })
    .catch(() => {
      message.error(editingAssignment.value ? 'ä¿å­˜å¤±è´¥' : 'åˆ›å»ºå¤±è´¥');
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
  
  // åŠ è½½ä½œä¸šçš„é¢˜ç›®
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
      message.success('åˆ é™¤æˆåŠŸ');
      fetchAssignments();
    })
    .catch(() => {
      message.error('åˆ é™¤å¤±è´¥');
    });
};

const viewAssignmentDetail = (assignment) => {
  viewingAssignment.value = assignment;
  
  // è·å–ä½œä¸šé¢˜ç›®
  Axios.get(`class/assignment/${assignment.id}/problems/`)
    .then((res) => {
      assignmentProblems.value = res;
    });
  
  showAssignmentDetailModal.value = true;
};

const viewAssignmentGrades = (assignment) => {
  viewingAssignmentGrades.value = assignment;
  loadingGrades.value = true;
  
  // è·å–æˆç»©è¡¨æ•°æ®
  Axios.get(`class/assignment/${assignment.id}/grades/`)
    .then((res) => {
      gradesData.value = res;
    })
    .catch(() => {
      message.error('åŠ è½½æˆç»©è¡¨å¤±è´¥');
    })
    .finally(() => {
      loadingGrades.value = false;
    });
  
  showAssignmentGradesModal.value = true;
};

// ä¸ºä½œä¸šé€‰æ‹©é¢˜ç›®
const openSelectProblemForAssignment = () => {
  showSelectProblemForAssignment.value = true;
  assignmentProblemSearchKeyword.value = '';
  // ç«‹å³åŠ è½½é¢˜ç›®åˆ—è¡¨
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
  // æ£€æŸ¥æ˜¯å¦å·²æ·»åŠ 
  if (selectedProblemsForAssignment.value.find(p => p.id === problem.id)) {
    message.warning('è¯¥é¢˜ç›®å·²æ·»åŠ ');
    return;
  }
  
  selectedProblemsForAssignment.value.push({
    id: problem.id,
    title: problem.title,
  });
  message.success('æ·»åŠ æˆåŠŸ');
};

const removeSelectedProblemForAssignment = (index) => {
  selectedProblemsForAssignment.value.splice(index, 1);
};

// å­¦ç”Ÿæ“ä½œ
const addStudent = () => {
  if (!addStudentForm.value.user_id) {
    message.warning('è¯·è¾“å…¥ç”¨æˆ·ID');
    return;
  }

  Axios.post(`class/class/${classId}/add_student/`, addStudentForm.value)
    .then(() => {
      message.success('æ·»åŠ æˆåŠŸ');
      showAddStudentModal.value = false;
      addStudentForm.value = { user_id: null, role: 'student' };
      fetchStudents();
    })
    .catch(err => {
      message.error(err.response?.data?.error || 'æ·»åŠ å¤±è´¥');
    });
};

const removeStudent = (userId) => {
  Axios.post(`class/class/${classId}/remove_student/`, { user_id: userId })
    .then(() => {
      message.success('ç§»é™¤æˆåŠŸ');
      fetchStudents();
    })
    .catch(() => {
      message.error('ç§»é™¤å¤±è´¥');
    });
};

const toggleMemberRole = (member) => {
  const newRole = member.role === 'teacher' ? 'student' : 'teacher';
  const roleText = newRole === 'teacher' ? 'æ•™å¸ˆ' : 'å­¦ç”Ÿ';
  
  Axios.post(`class/class/${classId}/update_member_role/`, { 
    user_id: member.user.id,
    role: newRole
  })
    .then(() => {
      message.success(`å·²åˆ‡æ¢ä¸º${roleText}`);
      fetchStudents();
    })
    .catch(err => {
      message.error(err.response?.data?.error || 'åˆ‡æ¢å¤±è´¥');
    });
};

// è·å–è®¤è¯ä»¤ç‰Œ
const getToken = () => {
  return store.state.user.token || '';
};

// å¤„ç†æµ‹è¯•æ•°æ®ä¸Šä¼ å®Œæˆ
const handleTestDataUploadFinish = ({ file, event }) => {
  try {
    const response = JSON.parse(event.target.response);
    if (response.message) {
      message.success(response.message);
      // åˆ·æ–°é¢˜ç›®åˆ—è¡¨
      fetchProblems();
      // å¦‚æœæœ‰è¿”å›çš„æ–‡ä»¶åˆ—è¡¨ï¼Œå¯ä»¥æ˜¾ç¤º
      if (response.files) {
        message.info(`ä¸Šä¼ äº† ${response.files.length} ä¸ªæ–‡ä»¶`);
      }
    }
  } catch (e) {
    message.error('ä¸Šä¼ æˆåŠŸä½†è§£æå“åº”å¤±è´¥');
  }
};

// å¤„ç†æµ‹è¯•æ•°æ®ä¸Šä¼ é”™è¯¯
const handleTestDataUploadError = ({ file, event }) => {
  try {
    const response = JSON.parse(event.target.response);
    message.error(response.error || 'ä¸Šä¼ å¤±è´¥');
  } catch (e) {
    message.error('ä¸Šä¼ å¤±è´¥');
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
 
 *cascade08 
Ù
*cascade08Ù
Ú
 *cascade08Ú
ñ
*cascade08ñ
÷
 *cascade08÷
à*cascade08àÕ *cascade08ÕááÏ *cascade08Ï×*cascade08×Ø *cascade08ØÙ*cascade08Ùæ *cascade08æè*cascade08èê *cascade08êë*cascade08ë÷ *cascade08÷ù*cascade08ùú *cascade08úü*cascade08üŒ *cascade08Œ*cascade08© *cascade08©ª*cascade08ª¬ *cascade08¬­*cascade08­± *cascade08±²*cascade08²¶ *cascade08¶¹*cascade08¹º *cascade08º¿¿À *cascade08ÀÆ*cascade08ÆÔ *cascade08ÔÕ*cascade08Õİ *cascade08İŞ*cascade08Şß *cascade08ßà*cascade08àâ *cascade08âã*cascade08ãä *cascade08äå*cascade08å¦ *cascade08¦¬*cascade08¬í *cascade08íó*cascade08ó³ *cascade08³æ*cascade08æ *cascade08ˆ*cascade08ˆ‰ *cascade08‰‹*cascade08‹÷ *cascade08÷ß*cascade08ß© *cascade08©Ï*cascade08Ï­  *cascade08­ ¯ *cascade08¯ ¶  *cascade08¶ ¸ *cascade08¸ Ô  *cascade08Ô ñ *cascade08ñ ˆ" *cascade08ˆ""*cascade08"ì" *cascade08ì"ó"*cascade08ó"“# *cascade08“#š#*cascade08š#Ä# *cascade08Ä#Ë#*cascade08Ë#Í# *cascade08Í#Ğ#*cascade08Ğ#Ò# *cascade08Ò#Ô#*cascade08Ô#Õ# *cascade08Õ#Ş#*cascade08Ş#à# *cascade08à#è#*cascade08è#ï# *cascade08ï#•$*cascade08•$¡$ *cascade08¡$¢$*cascade08¢$£$ *cascade08£$¨$*cascade08¨$¾$*cascade08¾$É$ *cascade08É$Ï$ *cascade08Ï$€%*cascade08€%‹% *cascade08‹%¹% *cascade08¹%»%*cascade08»%¾% *cascade08¾%À%*cascade08À%ô% *cascade08ô%õ%*cascade08õ%ÿ% *cascade08ÿ%€&*cascade08€&­& *cascade08­&Ñ&*cascade08Ñ&Ô& *cascade08Ô&Ö&*cascade08Ö&í& *cascade08í&ï&*cascade08ï&¤' *cascade08¤'¦'*cascade08¦'®' *cascade08®'½'*cascade08½'è' *cascade08è'÷'*cascade08÷'‡( *cascade08‡(–(*cascade08–( ( *cascade08 (ß(*cascade08ß(â( *cascade08â(ä(*cascade08ä(ƒ) *cascade08ƒ)…)*cascade08…)²) *cascade08²)´)*cascade08´)Ã) *cascade08Ã)Ä)*cascade08Ä)Ğ) *cascade08Ğ)Ñ)*cascade08Ñ)„* *cascade08„*†**cascade08†*–* *cascade08–*˜**cascade08˜*º* *cascade08º*¼**cascade08¼*Ú* *cascade08Ú*Ü**cascade08Ü*ß* *cascade08ß*á**cascade08á*ş* *cascade08ş*+*cascade08++ *cascade08+˜+*cascade08˜+™+ *cascade08™+±+*cascade08±+·+ *cascade08·+§, *cascade08§,ª,*cascade08ª,Ú4 *cascade08Ú4ñ4ñ4ù4 *cascade08ù4Â5 *cascade08Â5ˆ8*cascade08ˆ8Œ8 *cascade08Œ8”<*cascade08”<•< *cascade08•<º<*cascade08º<»< *cascade08»<¾<*cascade08¾<¿< *cascade08¿<â<*cascade08â<ä< *cascade08ä<î<*cascade08î<ï< *cascade08ï<£=*cascade08£=­= *cascade08­=İ?*cascade08İ?â? *cascade08â?ã?*cascade08ã?ä? *cascade08ä?é?*cascade08é?ê? *cascade08ê?ñ?*cascade08ñ?ò? *cascade08ò? @*cascade08 @¡@ *cascade08¡@…A*cascade08…A†A *cascade08†AˆA*cascade08ˆA‰A *cascade08‰AšA*cascade08šA›A *cascade08›AµA*cascade08µA¶A *cascade08¶A¡B*cascade08¡B£B *cascade08£B’C*cascade08’C–C *cascade08–CÊC*cascade08ÊCËC *cascade08ËCÏD*cascade08ÏDĞD *cascade08ĞDäD*cascade08äDåD *cascade08åDşD*cascade08şDÿD *cascade08ÿD€E*cascade08€E‚E *cascade08‚EˆE*cascade08ˆE—E *cascade08—E“K*cascade08“KšK *cascade08šKÍK*cascade08ÍKÛK *cascade08ÛKóN*cascade08óNüN *cascade08üN÷P*cascade08÷PøP *cascade08øPùP*cascade08ùPúP *cascade08úP„Q*cascade08„Q…Q *cascade08…Q•Q*cascade08•Q–Q *cascade08–Q°Q*cascade08°Q±Q *cascade08±QÅQ*cascade08ÅQÆQ *cascade08ÆQ¶R*cascade08¶RÀR *cascade08ÀR§S*cascade08§S©S *cascade08©SÉT*cascade08ÉTÍT *cascade08ÍTU*cascade08UU *cascade08U±U*cascade08±U²U *cascade08²UÕU*cascade08ÕUÖU *cascade08ÖUáU*cascade08áUâU *cascade08âUóU*cascade08óUôU *cascade08ôU÷U*cascade08÷UøU *cascade08øUğV*cascade08ğVƒW *cascade08ƒWûW*cascade08ûWŸX *cascade08ŸXå_ *cascade08å_Œ`*cascade08Œ`œ` *cascade08œ`¯`*cascade08¯`¶`*cascade08¶`Ú` *cascade08Ú`á`*cascade08á`ğ` *cascade08ğ`a*cascade08a†a *cascade08†aa*cascade08aÓa *cascade08Óağa*cascade08ğaŒb *cascade08Œb½b*cascade08½bøb *cascade08øbúb*cascade08úb¦c *cascade08¦c¨c*cascade08¨c†d *cascade08†dˆd*cascade08ˆd«d *cascade08«d­d*cascade08­d®d *cascade08®d°d*cascade08°dÛd *cascade08Ûdäd*cascade08ädæd *cascade08ædèd*cascade08èdıd *cascade08ıdÿd*cascade08ÿdÃe *cascade08ÃeÅe*cascade08ÅeÕe *cascade08Õe×e*cascade08×e‰f *cascade08‰f‹f*cascade08‹f f *cascade08 f¡f*cascade08¡f£f *cascade08£f¥f*cascade08¥f´f *cascade08´f¶f*cascade08¶fÚf *cascade08ÚfÜf*cascade08Üf‹g *cascade08‹gg*cascade08g–g *cascade08–g˜g*cascade08˜gİg *cascade08İgßg*cascade08ßgïg *cascade08ïgñg*cascade08ñg©h *cascade08©hªh*cascade08ªh¸h *cascade08¸h¹h*cascade08¹hÀh *cascade08ÀhÁh*cascade08ÁhÃh *cascade08ÃhÅh*cascade08ÅhÔh *cascade08ÔhÕh*cascade08Õhßh *cascade08ßhàh*cascade08àhğh *cascade08ğhòh*cascade08òh«i *cascade08«i­i*cascade08­i¶i *cascade08¶i·i*cascade08·iÅi *cascade08ÅiÆi*cascade08Æiği *cascade08ğiòi*cascade08òij *cascade08j j*cascade08 jÊj *cascade08ÊjËj*cascade08ËjÙj *cascade08ÙjÚj*cascade08Újáj *cascade08ájâj*cascade08âjäj *cascade08äjæj*cascade08æjÿj *cascade08ÿjk*cascade08k‘k *cascade08‘kày*cascade08àyz *cascade08zz*cascade08z¤z *cascade08¤z¦z*cascade08¦zãz *cascade08ãzåz*cascade08åzõz *cascade08õz÷z*cascade08÷z·{ *cascade08·{¹{*cascade08¹{À{ *cascade08À{Á{*cascade08Á{Ã{ *cascade08Ã{Å{*cascade08Å{Ş{ *cascade08Ş{à{*cascade08à{ú{ *cascade08ú{ü{*cascade08ü{‹| *cascade08‹|Œ|*cascade08Œ|§| *cascade08§|©|*cascade08©|°| *cascade08°|²|*cascade08²|è| *cascade08è|é|*cascade08é|ù| *cascade08ù|ú|*cascade08ú|Š} *cascade08Š}Œ}*cascade08Œ}×} *cascade08×}Ù}*cascade08Ù}ä} *cascade08ä}å}*cascade08å}÷} *cascade08÷}ø}*cascade08ø}—~ *cascade08—~¹~*cascade08¹~İ~ *cascade08İ~Š*cascade08Š‹ *cascade08‹“*cascade08“• *cascade08•»*cascade08»ä *cascade08äæ*cascade08æú *cascade08úü*cascade08üƒ€ *cascade08ƒ€…€*cascade08…€Ë€ *cascade08Ë€Í€*cascade08Í€İ€ *cascade08İ€ß€*cascade08ß€š *cascade08šœ*cascade08œÊ *cascade08ÊÌ*cascade08Ìê *cascade08ê‹‚*cascade08‹‚¯‚ *cascade08¯‚Ü‚*cascade08Ü‚İ‚ *cascade08İ‚å‚*cascade08å‚ç‚ *cascade08ç‚ƒ*cascade08ƒ¶ƒ *cascade08¶ƒ¸ƒ*cascade08¸ƒÊƒ *cascade08ÊƒÎƒ*cascade08ÎƒÕƒ *cascade08ÕƒÛƒ*cascade08Ûƒ„ *cascade08„”„*cascade08”„„ *cascade08„Ÿ„*cascade08Ÿ„­„ *cascade08­„²„*cascade08²„ç„ *cascade08ç„í„*cascade08í„Š… *cascade08Š…‹…*cascade08‹…™… *cascade08™……*cascade08…¼… *cascade08¼…Â…*cascade08Â…Û… *cascade08Û…á…*cascade08á…ğ… *cascade08ğ…ö…*cascade08ö…‚† *cascade08‚†Ó†*cascade08Ó†×† *cascade08×†ğ† *cascade08ğ†«‡*cascade08«‡®‡ *cascade08®‡°‡*cascade08°‡Ò‡ *cascade08Ò‡Ø‡*cascade08Ø‡Ù‡ *cascade08Ù‡§ˆ*cascade08§ˆ¨ˆ *cascade08¨ˆÑˆ*cascade08ÑˆÓˆ *cascade08Óˆåˆ*cascade08åˆæˆ *cascade08æˆ›‰*cascade08›‰œ‰ *cascade08œ‰‰*cascade08‰‰ *cascade08‰ ‰*cascade08 ‰¢‰ *cascade08¢‰µ‰*cascade08µ‰Ç‰ *cascade08Ç‰á‰*cascade08á‰ç‰ *cascade08ç‰í‰*cascade08í‰ó‰ *cascade08ó‰„Š*cascade08„Š…Š *cascade08…Š‹Š*cascade08‹ŠŒŠ *cascade08ŒŠŠ*cascade08Š Š *cascade08 Š¥Š*cascade08¥Š¦Š *cascade08¦Š§Š*cascade08§Š¨Š *cascade08¨ŠÁŠ*cascade08ÁŠÂŠ *cascade08ÂŠÏŠ*cascade08ÏŠĞŠ *cascade08ĞŠæŠ*cascade08æŠçŠ *cascade08çŠöŠ*cascade08öŠ÷Š *cascade08÷ŠøŠ*cascade08øŠùŠ *cascade08ùŠúŠ*cascade08úŠüŠ *cascade08üŠ£‹*cascade08£‹¥‹ *cascade08¥‹­‹*cascade08­‹®‹ *cascade08®‹Á‹*cascade08Á‹Â‹ *cascade08Â‹Ì‹*cascade08Ì‹Í‹ *cascade08Í‹å‹*cascade08å‹æ‹ *cascade08æ‹ô‹*cascade08ô‹õ‹ *cascade08õ‹ŒŒ*cascade08ŒŒŒ *cascade08ŒŒ*cascade08ŒŒ *cascade08Œ¨Œ*cascade08¨Œ©Œ *cascade08©Œ¶Œ*cascade08¶Œ·Œ *cascade08·ŒËŒ*cascade08ËŒÌŒ *cascade08ÌŒáŒ*cascade08áŒãŒ *cascade08ãŒæŒ*cascade08æŒçŒ *cascade08çŒìŒ*cascade08ìŒíŒ *cascade08íŒ*cascade08‚ *cascade08‚*cascade08 *cascade08‘*cascade08‘’ *cascade08’Å*cascade08ÅÇ *cascade08ÇÑ*cascade08ÑÓ *cascade08Óë*cascade08ëì *cascade08ìƒ*cascade08ƒ„ *cascade08„*cascade08Ÿ *cascade08Ÿ©*cascade08©ª *cascade08ª¨*cascade08¨© *cascade08©­*cascade08­® *cascade08®°*cascade08°± *cascade08±Å*cascade08ÅÇ *cascade08Çì*cascade08ìí *cascade08íï*cascade08ïğ *cascade08ğË*cascade08ËÎ *cascade08Î¬‘*cascade08¬‘­‘ *cascade08­‘¯‘*cascade08¯‘±‘ *cascade08±‘û‘*cascade08û‘¥“ *cascade08¥“¨“*cascade08¨“«“ *cascade08«“ñ“*cascade08ñ“â” *cascade08â”»• *cascade08»•¾•*cascade08¾•¿• *cascade08¿•À•*cascade08À•Ø— *cascade08Ø—‘˜*cascade08‘˜ ˜ *cascade08 ˜­˜*cascade08­˜«¤ *cascade08«¤º¤ *cascade08º¤À¤*cascade08À¤›¥ *cascade08›¥¡¥*cascade08¡¥’§ *cascade08’§œ©*cascade08œ©å« *cascade08
å«è«è«±¬ *cascade08
±¬È¬È¬Ò¬*cascade08Ò¬ç¬*cascade08ç¬ø¬ *cascade08ø¬²­*cascade08²­Ú­ *cascade08Ú­¾®*cascade08¾®Û®*cascade08Û®¤° *cascade08¤°Õ°*cascade08Õ°± *cascade08
±—±—±¼± *cascade08¼±½±*cascade08½±¾± *cascade08¾±Á±*cascade08Á±Â± *cascade08
Â±Ê±Ê±Ë± *cascade08
Ë±Ğ±Ğ±Ñ± *cascade08Ñ±å±*cascade08å±ì± *cascade08ì±ò±*cascade08ò±®² *cascade08®²½³*cascade08½³¾³ *cascade08¾³˜´ *cascade08˜´µ*cascade08µÊµ *cascade08Êµúµ*cascade08úµ‹¶ *cascade08‹¶ğ¶ *cascade08ğ¶…¹*cascade08…¹¹ *cascade08¹¯º *cascade08¯º°º*cascade08°º´º *cascade08´º»»*cascade08»»ñ» *cascade08ñ»™¼ *cascade08™¼¬¼*cascade08¬¼±¼ *cascade08±¼ù¼ *cascade08ù¼¿ *cascade08¿“Å*cascade08“Å™Å *cascade08™ÅÎÆ *cascade08ÎÆ»É*cascade08»ÉéÉ *cascade08éÉêÉ*cascade08êÉèË *cascade08èËïË*cascade08ïËÌ *cascade08Ì‚Ì*cascade08‚Ì‘Ì *cascade08‘Ì’Ì*cascade08’Ì¿Ì *cascade08¿ÌÀÌ*cascade08ÀÌ—Í *cascade08—Í˜Í*cascade08˜Í¸Í *cascade08¸ÍèÍ *cascade08èÍèÍ*cascade08èÍúÍ *cascade08úÍüÍ *cascade08üÍ Î *cascade08 ÎÍÎ*cascade08ÍÎ×Î *cascade08×ÎØÎ *cascade08ØÎŞÎ*cascade08ŞÎßÎ *cascade08ßÎìÎ*cascade08ìÎïÎ *cascade08ïÎüÎ*cascade08üÎıÎ *cascade08ıÎÀÏ*cascade08ÀÏÁÏ *cascade08ÁÏÉÏ*cascade08ÉÏÊÏ *cascade08ÊÏ’Ğ*cascade08’Ğ”Ğ *cascade08”ĞŸĞ*cascade08ŸĞ Ğ *cascade08 Ğ¦Ğ*cascade08¦Ğ§Ğ *cascade08§Ğ¼Ğ*cascade08¼Ğ½Ğ *cascade08½Ğ¿Ğ*cascade08¿ĞÀĞ *cascade08ÀĞÄĞ*cascade08ÄĞÅĞ *cascade08ÅĞÏĞ*cascade08ÏĞĞĞ *cascade08ĞĞÓĞ*cascade08ÓĞÛĞ *cascade08ÛĞŞĞ*cascade08ŞĞíĞ *cascade08íĞ÷Ğ*cascade08÷Ğ‚Ñ *cascade08‚Ñ—Ñ *cascade08—Ñ›Ñ*cascade08›ÑœÑ *cascade08œÑÑ*cascade08Ñ©Ñ *cascade08©ÑÖÑ*cascade08ÖÑ×Ñ *cascade08×ÑÙÑ*cascade08ÙÑõÑ *cascade08õÑ÷Ñ*cascade08÷ÑùÑ *cascade08ùÑ†Ò*cascade08†ÒÒ *cascade08ÒšÒ*cascade08šÒœÒ *cascade08œÒªÒ*cascade08ªÒ¹Ò *cascade08¹ÒÀÒ*cascade08ÀÒÁÒ *cascade08ÁÒÑÒ*cascade08ÑÒÒÒ *cascade08ÒÒêÒ*cascade08êÒìÒ *cascade08ìÒıÒ*cascade08ıÒÿÒ *cascade08ÿÒÓ*cascade08Ó‚Ó *cascade08‚Ó™Ó*cascade08™ÓŸÓ *cascade08ŸÓ¿Ó*cascade08¿ÓÁÓ *cascade08ÁÓÇÓ*cascade08ÇÓÈÓ *cascade08ÈÓØÓ*cascade08ØÓÛÓ *cascade08ÛÓçÓ*cascade08çÓúÓ *cascade08úÓ€Ô*cascade08€ÔƒÔ *cascade08ƒÔÔ*cascade08ÔÔ *cascade08ÔÔ *cascade08Ô‘Ô*cascade08‘Ô—Ô *cascade08—Ô˜Ô*cascade08˜ÔšÔ *cascade08šÔŸÔ *cascade08ŸÔ¡Ô *cascade08¡Ô©Ô*cascade08©ÔªÔ *cascade08ªÔ°Ô *cascade08°ÔÅÔ *cascade08ÅÔÎÔ*cascade08ÎÔîÔ *cascade08îÔ’Õ *cascade08’Õ•Õ*cascade08•ÕÕ *cascade08Õ­Õ*cascade08­Õ±Õ *cascade08±ÕµÕ*cascade08µÕ™Ö *cascade08™ÖÖ*cascade08Ö£Ö *cascade08£Ö¤Ö*cascade08¤Ö©Ö *cascade08©Ö¬Ö*cascade08¬Ö²Ö *cascade08²ÖÛÖ*cascade08ÛÖêÖ *cascade08êÖíÖ*cascade08íÖöÖ *cascade08öÖ†×*cascade08†×Š× *cascade08Š××*cascade08×†Ø *cascade08†Ø‰Ø*cascade08‰ØØ *cascade08ØØ*cascade08Ø”Ø *cascade08”Ø˜Ø*cascade08˜ØØ *cascade08Ø­Ø*cascade08­Ø¯Ø *cascade08¯Ø´Ø*cascade08´ØµØ *cascade08µØ¶Ø*cascade08¶Ø·Ø *cascade08·Ø¿Ø*cascade08¿ØÀØ *cascade08ÀØÅØ*cascade08ÅØÆØ *cascade08ÆØÍØ*cascade08ÍØ›Ş *cascade08›ŞÈç *cascade08ÈçËç*cascade08Ëçİç *cascade08İçßç*cascade08ßçàç *cascade08àçáç*cascade08áçñç *cascade08ñçòç*cascade08òçŸì *cascade08Ÿì¼ì*cascade08¼ì“í *cascade08“íèí*cascade08èí†î *cascade08†îªî*cascade08ªî«î *cascade08«îÂî*cascade08ÂîÏî *cascade08ÏîÒî*cascade08ÒîÓî *cascade08ÓîÔî*cascade08ÔîÕî *cascade08ÕîØî*cascade08ØîÙî *cascade08ÙîÜî*cascade08Üîİî *cascade08İîŞî*cascade08Şîßî *cascade08ßîèî*cascade08èîéî *cascade08éîëî*cascade08ëîíî *cascade08íîîî*cascade08îîòî *cascade08òîõî*cascade08õîöî *cascade08öîÿî*cascade08ÿî€ï *cascade08€ï‚ï*cascade08‚ï„ï *cascade08„ïï*cascade08ïï *cascade08ï•ï*cascade08•ï–ï *cascade08–ï˜ï*cascade08˜ïšï *cascade08šï¼ï *cascade08¼ï¿ï*cascade08¿ïÅï *cascade08ÅïÈï*cascade08Èïëï *cascade08ëïìï *cascade08ìïøï*cascade08øïùï *cascade08ùïğ*cascade08ğ‚ğ *cascade08‚ğğ*cascade08ğğ *cascade08ğ’ğ*cascade08’ğ“ğ *cascade08“ğ¡ğ*cascade08¡ğ¤ğ *cascade08¤ğ½ğ *cascade08½ğ×ğ*cascade08×ğ“ñ *cascade08“ñ—ñ*cascade08—ñ˜ñ *cascade08˜ññ*cascade08ñ°ñ *cascade08°ñ…ò *cascade08…ò‰ò*cascade08‰òŠò *cascade08Šòò*cascade08òšò *cascade08šòò*cascade08òŸò *cascade08Ÿò ò*cascade08 òØò *cascade08Øòßò*cascade08ßòêò *cascade08êòóò*cascade08óòôò *cascade08ôòõò*cascade08õòöò *cascade08öòøò*cascade08øòûò *cascade08ûòıò*cascade08ıòşò *cascade08şòÿò*cascade08ÿòƒó *cascade08ƒóó*cascade08óó *cascade08óó*cascade08ó’ó *cascade08’ó“ó*cascade08“ó—ó *cascade08—óœó*cascade08œóó *cascade08óó*cascade08ó£ó *cascade08£ó´ó*cascade08´ó·ó *cascade08·ó¹ó*cascade08¹ó¹õ *cascade08¹õÁõ*cascade08Áõ‡ö *cascade08‡ö…÷ *cascade08…÷‹÷*cascade08‹÷î÷ *cascade08î÷ò÷*cascade08ò÷û÷ *cascade08û÷†ø*cascade08†ø½ø *cascade08½øÇø *cascade08Çø†ş *cascade08†ş¹*cascade08¹¼ *cascade08¼³„ *cascade08³„´„*cascade08´„º„ *cascade08º„Í…*cascade08Í…¢† *cascade08¢†ª‰*cascade08ª‰® *cascade08®´ *cascade08´¢• *cascade08¢•£—*cascade08£—‘š *cascade08‘š—š *cascade08
—ššš¤š *cascade08¤š¥š*cascade08¥š¦š *cascade08¦š§š*cascade08§šŸ› *cascade08Ÿ›Áœ*cascade08Áœé *cascade08é®*cascade08®´ *cascade08´«Ÿ*cascade08«ŸĞŸ *cascade08ĞŸÜŸ*cascade08ÜŸ…  *cascade08… ° *cascade08° Ç  *cascade08Ç Ø¢*cascade08Ø¢ƒ£ *cascade08ƒ£š£*cascade08š£›£ *cascade08›£œ£*cascade08œ££ *cascade08£££*cascade08££¥£ *cascade08¥£¨£*cascade08¨£©£ *cascade08©£¸£*cascade08¸£Ë£ *cascade08Ë£Î£*cascade08Î£Ñ£ *cascade08Ñ£ä£*cascade08ä£å£ *cascade08å£æ£*cascade08æ£ç£ *cascade08ç£é£*cascade08é£‘¤ *cascade08‘¤š¤*cascade08š¤›¤ *cascade08›¤¡¤*cascade08¡¤¤¤ *cascade08¤¤¶¤*cascade08¶¤·¤ *cascade08·¤Ê¤*cascade08Ê¤Ë¤ *cascade08Ë¤İ¤*cascade08İ¤Ş¤ *cascade08Ş¤÷¤*cascade08÷¤ø¤ *cascade08ø¤Š¥*cascade08Š¥‹¥ *cascade08‹¥“¥*cascade08“¥”¥ *cascade08”¥•¥*cascade08•¥–¥ *cascade08–¥—¥*cascade08—¥˜¥ *cascade08˜¥¥*cascade08¥Ÿ¥ *cascade08Ÿ¥¯¥*cascade08¯¥°¥ *cascade08°¥½¥*cascade08½¥¾¥ *cascade08¾¥Ï¥*cascade08Ï¥Ğ¥ *cascade08Ğ¥Ñ¥*cascade08Ñ¥×¥ *cascade08×¥Ğ¦*cascade08Ğ¦ê¦ *cascade08ê¦í¦*cascade08í¦ï¦ *cascade08ï¦‹§*cascade08‹§§ *cascade08§¸§*cascade08¸§¹§ *cascade08¹§¹ª*cascade08¹ª„« *cascade08„«Š«*cascade08Š«¦« *cascade08¦«µ«*cascade08µ«¶« *cascade08¶«¹«*cascade08¹«º« *cascade08º«Å«*cascade08Å«Æ« *cascade08Æ«Ç«*cascade08Ç«È« *cascade08È«Ó«*cascade08Ó«Ô« *cascade08Ô«Ø«*cascade08Ø«â« *cascade08â«è«*cascade08è«ë« *cascade08ë«¬*cascade08¬¬ *cascade08¬½¬*cascade08½¬¿¬ *cascade08¿¬Û¬*cascade08Û¬ä¬ *cascade08ä¬™­*cascade08™­š­ *cascade08š­œ­*cascade08œ­­ *cascade08­ª­*cascade08ª­«­ *cascade08«­ˆ®*cascade08ˆ®Š® *cascade08Š®ª®*cascade08ª®¬® *cascade08¬®°®*cascade08°®±® *cascade08±®²®*cascade08²®³® *cascade08³®¶®*cascade08¶®·® *cascade08·®¹®*cascade08¹®º® *cascade08º®å®*cascade08å®ú® *cascade08ú®…¯*cascade08…¯ˆ¯ *cascade08ˆ¯¯*cascade08¯¯ *cascade08¯¡¯*cascade08¡¯®¯ *cascade08®¯²¯*cascade08²¯´¯ *cascade08´¯º¯*cascade08º¯»¯ *cascade08»¯Â¯*cascade08Â¯Ã¯ *cascade08Ã¯Ñ¯*cascade08Ñ¯Ó¯ *cascade08Ó¯Õ¯*cascade08Õ¯Ö¯ *cascade08Ö¯ç¯*cascade08ç¯ê¯ *cascade08ê¯ó¯*cascade08ó¯õ¯ *cascade08õ¯û¯*cascade08û¯ş¯ *cascade08ş¯Š°*cascade08Š°’° *cascade08’°•°*cascade08•°—° *cascade08—°š°*cascade08š°›° *cascade08›°»°*cascade08»°¼° *cascade08¼°ç°*cascade08ç°è° *cascade08è°¥± *cascade08¥±ó²*cascade08ó²÷² *cascade08÷²ù² *cascade08ù²„³*cascade08„³³ *cascade08³‘³*cascade08‘³“³ *cascade08“³Ä³*cascade08Ä³È³ *cascade08È³É³*cascade08É³Ë³ *cascade08Ë³Û³*cascade08Û³Ü³ *cascade08Ü³ˆ´*cascade08ˆ´‰´ *cascade08‰´‹´*cascade08‹´´ *cascade08´–´*cascade08–´—´ *cascade08—´›´*cascade08›´œ´ *cascade08œ´ ´*cascade08 ´¡´ *cascade08¡´©´*cascade08©´ª´ *cascade08ª´µ´*cascade08µ´·´ *cascade08·´Ø´*cascade08Ø´Ù´ *cascade08Ù´ú´*cascade08ú´û´ *cascade08û´ÿ´*cascade08ÿ´Œµ *cascade08Œµ›µ*cascade08›µœµ *cascade08œµ´µ*cascade08´µ¶µ *cascade08¶µ½µ*cascade08½µ¾µ *cascade08¾µÖµ*cascade08Öµ×µ *cascade08×µïµ*cascade08ïµğµ *cascade08ğµõµ*cascade08õµöµ *cascade08öµ…¶*cascade08…¶†¶ *cascade08†¶Š¶*cascade08Š¶‹¶ *cascade08‹¶«¶*cascade08«¶¬¶ *cascade08¬¶Â¶*cascade08Â¶Ä¶ *cascade08Ä¶ù¶*cascade08ù¶ú¶ *cascade08ú¶É·*cascade08É·Ë· *cascade08Ë·İ·*cascade08İ·ã· *cascade08ã·í·*cascade08í·ğ· *cascade08ğ·é¹*cascade08é¹ù¹ *cascade08
ù¹ÿ¹ÿ¹Õ¼ *cascade08Õ¼æ¼*cascade08æ¼õ¿ *cascade08õ¿ÚÃ*cascade08ÚÃÊÊ*cascade08ÊÊÿË *cascade08"(205b1bab434999c48e066e66385ba65f03f104f423file:///root/frontend-naive/src/pages/class/_id.vue:file:///root/frontend-naive