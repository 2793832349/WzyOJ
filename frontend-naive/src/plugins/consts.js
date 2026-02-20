import config from '../config';

const judgeStatus = {
  PENDING: -4,
  JUDGING: -3,
  COMPILE_ERROR: -2,
  WRONG_ANSWER: -1,
  ACCEPTED: 0,
  TIME_LIMIT_EXCEEDED: 1,
  MEMORY_LIMIT_EXCEEDED: 2,
  RUNTIME_ERROR: 3,
  SYSTEM_ERROR: 4,
};

const judgeStatusDisplay = {
  PENDING: 'Pending',
  JUDGING: 'Judging',
  COMPILE_ERROR: 'CE',
  WRONG_ANSWER: 'WA',
  ACCEPTED: 'AC',
  TIME_LIMIT_EXCEEDED: 'TLE',
  MEMORY_LIMIT_EXCEEDED: 'MLE',
  RUNTIME_ERROR: 'RE',
  SYSTEM_ERROR: 'SE',
};

const judgeStatusColor = {
  PENDING: '#49C4C0',
  JUDGING: '#5252C4',
  COMPILE_ERROR: '#9231D9',
  WRONG_ANSWER: '#FF0000',
  ACCEPTED: '#27AE60',
  TIME_LIMIT_EXCEEDED: '#DBB131',
  MEMORY_LIMIT_EXCEEDED: '#DBB131',
  RUNTIME_ERROR: '#AE27AE',
  SYSTEM_ERROR: '#808080',
};

const noTime = [
  judgeStatus.PENDING,
  judgeStatus.JUDGING,
  judgeStatus.COMPILE_ERROR,
  judgeStatus.TIME_LIMIT_EXCEEDED,
  judgeStatus.SYSTEM_ERROR,
];

const noMemory = [
  judgeStatus.PENDING,
  judgeStatus.JUDGING,
  judgeStatus.COMPILE_ERROR,
  judgeStatus.MEMORY_LIMIT_EXCEEDED,
  judgeStatus.SYSTEM_ERROR,
];

const initDisplay = (obj, objDisplay) => {
  const displays = {};
  for (const key in obj) {
    displays[obj[key]] = objDisplay[key];
  }
  obj.getDisplay = value => displays[value];
};

const initColor = (obj, objColor) => {
  const color = {};
  for (const key in obj) {
    color[obj[key]] = objColor[key];
  }
  obj.getColorClass = value => color[value];
};

initDisplay(judgeStatus, judgeStatusDisplay);
// initDisplay(languages, languagesDisplay);

initColor(judgeStatus, judgeStatusColor);

const languageOptions = [];
for (const key in config.languages) {
  languageOptions.push({
    label: config.languages[key],
    value: key,
  });
}

const statusOptions = [];
for (const key in judgeStatus) {
  if (typeof judgeStatus[key] === 'number') {
    statusOptions.push({
      label: judgeStatus.getDisplay(judgeStatus[key]),
      value: judgeStatus[key],
    });
  }
}

const difficulty = {
  0: '未设定',
  1: '黑铁',
  2: '青铜',
  3: '白银',
  4: '黄金',
  5: '翡翠',
  6: '铂金',
  7: '钻石',
  8: '大师',
  9: '宗师',
  10: '王者',
};

const difficultyColor = {
  0: '#9CA3AF',
  1: '#4B5563',
  2: '#CD7F32',
  3: '#C0C0C0',
  4: '#FACC15',
  5: '#10B981',
  6: '#14B8A6',
  7: '#3B82F6',
  8: '#8B5CF6',
  9: '#EF4444',
  10: '#F59E0B',
};

const difficultyBadgeStyle = {
  0: { background: 'linear-gradient(135deg, #6B7280 0%, #9CA3AF 100%)', color: '#F9FAFB', boxShadow: '0 6px 16px rgba(107, 114, 128, 0.25)' },
  1: { background: 'linear-gradient(135deg, #111827 0%, #4B5563 100%)', color: '#F9FAFB', boxShadow: '0 6px 16px rgba(17, 24, 39, 0.28)' },
  2: { background: 'linear-gradient(135deg, #7C2D12 0%, #CD7F32 100%)', color: '#FFF7ED', boxShadow: '0 6px 16px rgba(124, 45, 18, 0.3)' },
  3: { background: 'linear-gradient(135deg, #64748B 0%, #D1D5DB 100%)', color: '#0F172A', boxShadow: '0 6px 16px rgba(100, 116, 139, 0.28)' },
  4: { background: 'linear-gradient(135deg, #B45309 0%, #FACC15 100%)', color: '#1F2937', boxShadow: '0 8px 18px rgba(250, 204, 21, 0.35)' },
  5: { background: 'linear-gradient(135deg, #065F46 0%, #34D399 100%)', color: '#ECFDF5', boxShadow: '0 8px 18px rgba(16, 185, 129, 0.35)' },
  6: { background: 'linear-gradient(135deg, #0F766E 0%, #67E8F9 100%)', color: '#ECFEFF', boxShadow: '0 8px 18px rgba(15, 118, 110, 0.35)' },
  7: { background: 'linear-gradient(135deg, #1E3A8A 0%, #60A5FA 100%)', color: '#EFF6FF', boxShadow: '0 8px 18px rgba(30, 58, 138, 0.35)' },
  8: { background: 'linear-gradient(135deg, #4C1D95 0%, #A78BFA 100%)', color: '#F5F3FF', boxShadow: '0 8px 18px rgba(76, 29, 149, 0.35)' },
  9: { background: 'linear-gradient(135deg, #7F1D1D 0%, #F87171 100%)', color: '#FEF2F2', boxShadow: '0 8px 18px rgba(127, 29, 29, 0.36)' },
  10: { background: 'linear-gradient(135deg, #78350F 0%, #FDE047 45%, #F59E0B 100%)', color: '#1C1917', boxShadow: '0 10px 22px rgba(245, 158, 11, 0.42)' },
};

const difficultyOptions = [];
for (const key in difficulty) {
  if (typeof difficulty[key] === 'string') {
    difficultyOptions.push({
      label: difficulty[key],
      value: Number(key),
    });
  }
}

const themeOptions = [
  { label: '跟随系统', value: 'system' },
  { label: '浅色', value: 'light' },
  { label: '深色', value: 'dark' },
];
const markdownThemeOptions = [
  { label: 'default', value: 'default' },
  { label: 'github', value: 'github' },
  { label: 'vuepress', value: 'vuepress' },
  { label: 'mk-cute', value: 'mk-cute' },
  { label: 'smart-blue', value: 'smart-blue' },
  { label: 'cyanosis', value: 'cyanosis' },
  { label: 'arknights', value: 'arknights' },
];
const sentenceApiOptions = [
  { label: '异想之旅亿言', value: 'yxzl' },
  { label: 'Hitokoto - 一言', value: 'hitokoto' },
];
const captchaTypeOptions = [
  { label: 'reCAPTCHA V3', value: 'recaptcha-v3' },
  { label: 'HCCAPTCHA', value: 'hccaptcha' },
];
const captchaSceneOptions = [
  { label: '注册', value: 'register' },
  { label: '登录', value: 'login' },
  { label: '评测', value: 'submission' },
  { label: '讨论', value: 'discussion' },
];
const permissionOptions = [
  { label: '站点设置', value: 'site_setting' },
  { label: '用户管理', value: 'user' },
  { label: '题目管理', value: 'problem' },
  { label: '评测管理', value: 'submission' },
  { label: '讨论管理', value: 'discussion' },
  { label: '比赛管理', value: 'contest' },
  { label: '班级管理', value: 'class' },
];
export {
  judgeStatus,
  languageOptions,
  statusOptions,
  noTime,
  noMemory,
  difficulty,
  difficultyColor,
  difficultyBadgeStyle,
  difficultyOptions,
  themeOptions,
  markdownThemeOptions,
  sentenceApiOptions,
  captchaTypeOptions,
  captchaSceneOptions,
  permissionOptions,
};
