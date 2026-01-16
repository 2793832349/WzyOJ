<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue';
import * as Blockly from 'blockly';
import 'blockly/blocks';
import * as ZhHans from 'blockly/msg/zh-hans';

Blockly.setLocale(ZhHans);

Blockly.Msg['RENAME_VARIABLE'] = '重命名变量...';
Blockly.Msg['DELETE_VARIABLE'] = '删除变量 %1';
Blockly.Msg['DELETE_VARIABLE_CONFIRMATION'] = '删除变量“%1”将会删除所有使用它的地方。确定删除吗？';

const emit = defineEmits(['update:workspaceXml', 'update:code']);
const props = defineProps({
  workspaceXml: {
    type: String,
    default: '',
  },
});

const containerRef = ref(null);
let workspace = null;

const arrayTypeOptions = [
  ['整型', 'int'],
  ['长整型', 'longlong'],
  ['小数', 'double'],
  ['字符串', 'string'],
  ['布尔', 'bool'],
];

const getArrayNameOptions = () => {
  const opts = [['- 选择 -', '']];
  if (!workspace) return opts;
  const set = new Set();
  const blocks = workspace.getAllBlocks(false) || [];
  for (const b of blocks) {
    if (!b || !b.type) continue;
    if (b.type !== 'array_define_1d' && b.type !== 'array_define_2d') continue;
    const raw = (b.getFieldValue('NAME') || '').trim();
    if (!raw) continue;
    if (set.has(raw)) continue;
    set.add(raw);
    opts.push([raw, raw]);
  }
  return opts;
};

const sanitizeWorkspaceDom = (dom) => {
  try {
    const varsNodes = Array.from(dom.getElementsByTagName('variables') || []);
    for (const n of varsNodes) {
      n.parentNode && n.parentNode.removeChild(n);
    }

    const fields = Array.from(dom.getElementsByTagName('field') || []);
    for (const f of fields) {
      const name = f.getAttribute('name');
      if (name === 'VAR') {
        f.removeAttribute('id');
        f.removeAttribute('variabletype');
      }
    }
  } catch (_) {}
  return dom;
};

Blockly.Blocks['array_define_1d'] = {
  init: function () {
    this.appendDummyInput()
      .appendField('定义一维数组：类型为')
      .appendField(new Blockly.FieldDropdown(arrayTypeOptions), 'TYPE')
      .appendField('名为')
      .appendField(new Blockly.FieldInput('YouNamed'), 'NAME')
      .appendField('长度为');
    this.appendValueInput('LEN1').setCheck('Number');
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setColour(285);
  },
};

Blockly.Blocks['array_define_2d'] = {
  init: function () {
    this.appendDummyInput()
      .appendField('定义二维数组：类型为')
      .appendField(new Blockly.FieldDropdown(arrayTypeOptions), 'TYPE')
      .appendField('名为')
      .appendField(new Blockly.FieldInput('YouNamed'), 'NAME')
      .appendField('长度为');
    this.appendValueInput('LEN1').setCheck('Number');
    this.appendValueInput('LEN2').setCheck('Number');
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setColour(285);
  },
};

Blockly.Blocks['array_set'] = {
  init: function () {
    this.appendDummyInput()
      .appendField('赋值(如果是一维数组，第二个下标不要设值)')
      .appendField(new Blockly.FieldDropdown(getArrayNameOptions), 'ARR');
    this.appendValueInput('I1').setCheck('Number');
    this.appendValueInput('I2').setCheck('Number');
    this.appendDummyInput().appendField('为');
    this.appendValueInput('VALUE');
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setColour(285);
  },
};

Blockly.Blocks['array_get'] = {
  init: function () {
    this.appendDummyInput()
      .appendField('(如果是一维数组，第二个下标不要设值)')
      .appendField(new Blockly.FieldDropdown(getArrayNameOptions), 'ARR');
    this.appendValueInput('I1').setCheck('Number');
    this.appendValueInput('I2').setCheck('Number');
    this.setOutput(true);
    this.setColour(285);
  },
};

const cppGenerator = new Blockly.Generator('CPP');
cppGenerator.RESERVED_WORDS_ =
  'auto,break,case,catch,char,class,const,continue,default,delete,do,double,else,enum,explicit,export,extern,false,float,for,friend,goto,if,inline,int,long,mutable,namespace,new,operator,private,protected,public,register,return,short,signed,sizeof,static,struct,switch,template,this,throw,true,try,typedef,typeid,typename,union,unsigned,using,virtual,void,volatile,wchar_t,while';

cppGenerator.ORDER_ATOMIC = 0;
cppGenerator.ORDER_NONE = 99;

cppGenerator.init = function (ws) {
  cppGenerator.nameDB_ = new Blockly.Names(cppGenerator.RESERVED_WORDS_);
  cppGenerator.nameDB_.setVariableMap(ws.getVariableMap());

  const declared = new Set();
  const allBlocks = ws?.getAllBlocks?.(false) ?? [];
  for (const b of allBlocks) {
    if (!b || !b.type) continue;
    if (b.type === 'var_define') {
      declared.add(toVarName(b));
    }
  }
  cppGenerator._declaredVarNames = declared;
};

cppGenerator.finish = function (code) {
  const varDefs = new Map();
  const arrayDefs = [];

  const allBlocks = workspace?.getAllBlocks?.(false) ?? [];
  for (const b of allBlocks) {
    if (!b || !b.type) continue;
    if (b.type === 'var_define') {
      const varName = toVarName(b);
      const typeKey = b.getFieldValue('TYPE') || 'int';
      varDefs.set(varName, { typeKey, block: b });
    }
    if (b.type === 'array_define_1d') {
      const raw = (b.getFieldValue('NAME') || '').trim();
      if (!raw) continue;
      const name = cppGenerator.nameDB_.getName(raw, Blockly.VARIABLE_CATEGORY_NAME);
      const typeKey = b.getFieldValue('TYPE') || 'int';
      const len1 = cppGenerator.valueToCode(b, 'LEN1', cppGenerator.ORDER_NONE) || '1';
      arrayDefs.push({ dim: 1, name, typeKey, len1 });
    }
    if (b.type === 'array_define_2d') {
      const raw = (b.getFieldValue('NAME') || '').trim();
      if (!raw) continue;
      const name = cppGenerator.nameDB_.getName(raw, Blockly.VARIABLE_CATEGORY_NAME);
      const typeKey = b.getFieldValue('TYPE') || 'int';
      const len1 = cppGenerator.valueToCode(b, 'LEN1', cppGenerator.ORDER_NONE) || '1';
      const len2 = cppGenerator.valueToCode(b, 'LEN2', cppGenerator.ORDER_NONE) || '1';
      arrayDefs.push({ dim: 2, name, typeKey, len1, len2 });
    }
  }

  const typeMap = {
    int: 'int',
    longlong: 'long long',
    double: 'double',
    string: 'string',
    bool: 'bool',
  };

  const defaultInit = {
    int: '0',
    longlong: '0',
    double: '0',
    string: '""',
    bool: 'false',
  };

  const declaredLines = [];
  for (const [name, info] of varDefs.entries()) {
    const typeKey = info.typeKey in typeMap ? info.typeKey : 'int';
    const cppType = typeMap[typeKey];
    const initExpr =
      cppGenerator.valueToCode(info.block, 'INIT', cppGenerator.ORDER_NONE) ||
      defaultInit[typeKey] ||
      '0';
    declaredLines.push(`  ${cppType} ${name} = ${initExpr};`);
  }

  const usedVars = new Set();
  for (const b of allBlocks) {
    if (!b || !b.type) continue;
    if (
      b.type === 'var_define' ||
      b.type === 'var_assign' ||
      b.type === 'var_get' ||
      b.type === 'io_read' ||
      b.type === 'variables_get' ||
      b.type === 'variables_set' ||
      b.type === 'controls_for' ||
      b.type === 'controls_for_custom'
    ) {
      const n = toVarName(b);
      if (n) usedVars.add(n);
    }
  }
  for (const name of usedVars) {
    if (varDefs.has(name)) continue;
    declaredLines.push(`  long long ${name} = 0;`);
  }

  for (const a of arrayDefs) {
    const typeKey = a.typeKey in typeMap ? a.typeKey : 'int';
    const cppType = typeMap[typeKey];
    if (a.dim === 1) {
      declaredLines.push(`  vector<${cppType}> ${a.name}(${a.len1});`);
    } else {
      declaredLines.push(
        `  vector<vector<${cppType}>> ${a.name}(${a.len1}, vector<${cppType}>(${a.len2}));`
      );
    }
  }

  const declared = declaredLines.join('\n');

  const body = (code || '').trimEnd();
  const indentedBody = body
    ? body
        .split('\n')
        .map(line => (line ? `  ${line}` : line))
        .join('\n')
    : '';
  const header = `#include <bits/stdc++.h>\nusing namespace std;\n\n`;
  const mainStart = `int main(){\n  ios::sync_with_stdio(false);\n  cin.tie(nullptr);\n`;
  const mainEnd = `\n  return 0;\n}`;

  const combined = [
    header,
    mainStart,
    declared ? declared + '\n' : '',
    indentedBody ? indentedBody + '\n' : '',
    mainEnd,
  ].join('');

  return combined;
};

cppGenerator.scrub_ = function (block, code, opt_thisOnly) {
  const nextBlock = block.nextConnection && block.nextConnection.targetBlock();
  if (nextBlock && !opt_thisOnly) {
    const next = cppGenerator.blockToCode(nextBlock);
    if (!code) return next;
    if (!next) return code;
    return code + '\n' + next;
  }
  return code;
};

const toVarName = block => {
  const varField = block.getField('VAR');
  const variable = varField?.getVariable?.();
  const raw =
    variable?.name ??
    varField?.getText?.() ??
    block.getFieldValue('NAME') ??
    '';
  return cppGenerator.nameDB_.getName(raw, Blockly.VARIABLE_CATEGORY_NAME);
};

cppGenerator.forBlock['program_main'] = function (block) {
  return cppGenerator.statementToCode(block, 'DO').trimEnd();
};

cppGenerator.forBlock['program_end'] = function (_block) {
  return '';
};

cppGenerator.forBlock['variables_get'] = function (block) {
  return [toVarName(block), cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['variables_set'] = function (block) {
  const varName = toVarName(block);
  const value = cppGenerator.valueToCode(block, 'VALUE', cppGenerator.ORDER_NONE) || '0';
  return `${varName} = ${value};`;
};

cppGenerator.forBlock['var_define'] = function (_block) {
  return '';
};

cppGenerator.forBlock['var_assign'] = function (block) {
  const varName = toVarName(block);
  const value = cppGenerator.valueToCode(block, 'VALUE', cppGenerator.ORDER_NONE) || '0';
  return `${varName} = ${value};`;
};

cppGenerator.forBlock['var_get'] = function (block) {
  return [toVarName(block), cppGenerator.ORDER_ATOMIC];
};

const getArrayCppName = (block) => {
  const field = block.getField('ARR');
  const raw = (field?.getValue?.() ?? block.getFieldValue('NAME') ?? '').toString().trim();
  if (!raw) return '';
  return cppGenerator.nameDB_.getName(raw, Blockly.VARIABLE_CATEGORY_NAME);
};

cppGenerator.forBlock['array_define_1d'] = function (_block) {
  return '';
};

cppGenerator.forBlock['array_define_2d'] = function (_block) {
  return '';
};

cppGenerator.forBlock['array_set'] = function (block) {
  const arr = getArrayCppName(block);
  if (!arr) return '';
  const i1 = cppGenerator.valueToCode(block, 'I1', cppGenerator.ORDER_NONE) || '0';
  const i2 = cppGenerator.valueToCode(block, 'I2', cppGenerator.ORDER_NONE);
  const val = cppGenerator.valueToCode(block, 'VALUE', cppGenerator.ORDER_NONE) || '0';
  if (i2) {
    return `${arr}[${i1}][${i2}] = ${val};`;
  }
  return `${arr}[${i1}] = ${val};`;
};

cppGenerator.forBlock['array_get'] = function (block) {
  const arr = getArrayCppName(block);
  if (!arr) return ['0', cppGenerator.ORDER_ATOMIC];
  const i1 = cppGenerator.valueToCode(block, 'I1', cppGenerator.ORDER_NONE) || '0';
  const i2 = cppGenerator.valueToCode(block, 'I2', cppGenerator.ORDER_NONE);
  if (i2) {
    return [`${arr}[${i1}][${i2}]`, cppGenerator.ORDER_ATOMIC];
  }
  return [`${arr}[${i1}]`, cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['math_number'] = function (block) {
  const num = block.getFieldValue('NUM');
  const text = (num ?? '0').toString();
  return [text, cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['math_arithmetic'] = function (block) {
  const op = block.getFieldValue('OP');
  const A = cppGenerator.valueToCode(block, 'A', cppGenerator.ORDER_NONE) || '0';
  const B = cppGenerator.valueToCode(block, 'B', cppGenerator.ORDER_NONE) || '0';
  const map = {
    ADD: '+',
    MINUS: '-',
    MULTIPLY: '*',
    DIVIDE: '/',
    POWER: 'pow',
  };
  const sym = map[op] || '+';
  if (sym === 'pow') {
    return [`(pow(${A}, ${B}))`, cppGenerator.ORDER_ATOMIC];
  }
  return [`(${A} ${sym} ${B})`, cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['logic_compare'] = function (block) {
  const op = block.getFieldValue('OP');
  const A = cppGenerator.valueToCode(block, 'A', cppGenerator.ORDER_NONE) || '0';
  const B = cppGenerator.valueToCode(block, 'B', cppGenerator.ORDER_NONE) || '0';
  const map = {
    EQ: '==',
    NEQ: '!=',
    LT: '<',
    LTE: '<=',
    GT: '>',
    GTE: '>=',
  };
  const sym = map[op] || '==';
  return [`(${A} ${sym} ${B})`, cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['logic_operation'] = function (block) {
  const op = block.getFieldValue('OP');
  const A = cppGenerator.valueToCode(block, 'A', cppGenerator.ORDER_NONE) || 'false';
  const B = cppGenerator.valueToCode(block, 'B', cppGenerator.ORDER_NONE) || 'false';
  const sym = op === 'AND' ? '&&' : '||';
  return [`(${A} ${sym} ${B})`, cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['logic_negate'] = function (block) {
  const val = cppGenerator.valueToCode(block, 'BOOL', cppGenerator.ORDER_NONE) || 'false';
  return [`(!${val})`, cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['controls_if'] = function (block) {
  let n = 0;
  let code = '';
  while (block.getInput('IF' + n)) {
    const condition = cppGenerator.valueToCode(block, 'IF' + n, cppGenerator.ORDER_NONE) || 'false';
    const branch = cppGenerator.statementToCode(block, 'DO' + n);
    code += `${n === 0 ? 'if' : 'else if'} (${condition}) {\n${branch}}\n`;
    n++;
  }
  if (block.getInput('ELSE')) {
    const branch = cppGenerator.statementToCode(block, 'ELSE');
    code += `else {\n${branch}}\n`;
  }
  return code.trimEnd();
};

cppGenerator.forBlock['controls_for'] = function (block) {
  const varName = toVarName(block);
  const from = cppGenerator.valueToCode(block, 'FROM', cppGenerator.ORDER_NONE) || '0';
  const to = cppGenerator.valueToCode(block, 'TO', cppGenerator.ORDER_NONE) || '0';
  const by = cppGenerator.valueToCode(block, 'BY', cppGenerator.ORDER_NONE) || '1';
  const branch = cppGenerator.statementToCode(block, 'DO');
  const declared = cppGenerator._declaredVarNames && cppGenerator._declaredVarNames.has(varName);
  const init = declared ? `${varName} = ${from}` : `long long ${varName} = ${from}`;
  return `for (${init}; ${varName} <= ${to}; ${varName} += ${by}) {\n${branch}}`;
};

cppGenerator.forBlock['controls_for_custom'] = function (block) {
  const varName = toVarName(block);
  const from = cppGenerator.valueToCode(block, 'FROM', cppGenerator.ORDER_NONE) || '0';
  const to = cppGenerator.valueToCode(block, 'TO', cppGenerator.ORDER_NONE) || '0';
  const by = cppGenerator.valueToCode(block, 'BY', cppGenerator.ORDER_NONE) || '1';
  const branch = cppGenerator.statementToCode(block, 'DO');
  const declared = cppGenerator._declaredVarNames && cppGenerator._declaredVarNames.has(varName);
  const init = declared ? `${varName} = ${from}` : `long long ${varName} = ${from}`;
  return `for (${init}; ${varName} <= ${to}; ${varName} += ${by}) {\n${branch}}`;
};

cppGenerator.forBlock['controls_whileUntil'] = function (block) {
  const mode = block.getFieldValue('MODE');
  const condition = cppGenerator.valueToCode(block, 'BOOL', cppGenerator.ORDER_NONE) || 'false';
  const expr = mode === 'UNTIL' ? `(!${condition})` : condition;
  const branch = cppGenerator.statementToCode(block, 'DO');
  return `while (${expr}) {\n${branch}}`;
};

Blockly.common.defineBlocksWithJsonArray([
  {
    type: 'program_main',
    message0: '主程序',
    message1: '%1',
    args1: [
      {
        type: 'input_statement',
        name: 'DO',
      },
    ],
    colour: 290,
  },
  {
    type: 'program_end',
    message0: '程序结束',
    previousStatement: null,
    colour: 290,
  },
  {
    type: 'controls_for_custom',
    message0: '循环：变量 %1 从 %2 到 %3 步长 %4',
    args0: [
      {
        type: 'field_input',
        name: 'NAME',
        text: 'i',
      },
      {
        type: 'input_value',
        name: 'FROM',
      },
      {
        type: 'input_value',
        name: 'TO',
      },
      {
        type: 'input_value',
        name: 'BY',
      },
    ],
    message1: '%1',
    args1: [
      {
        type: 'input_statement',
        name: 'DO',
      },
    ],
    previousStatement: null,
    nextStatement: null,
    colour: 120,
  },
  {
    type: 'var_define',
    message0: '定义变量：类型为 %1 名为 %2 初始值 %3',
    args0: [
      {
        type: 'field_dropdown',
        name: 'TYPE',
        options: [
          ['整型', 'int'],
          ['长整型', 'longlong'],
          ['小数', 'double'],
          ['字符串', 'string'],
          ['布尔', 'bool'],
        ],
      },
      {
        type: 'field_input',
        name: 'NAME',
        text: 'YouNamed',
      },
      {
        type: 'input_value',
        name: 'INIT',
      },
    ],
    previousStatement: null,
    nextStatement: null,
    colour: 330,
  },
  {
    type: 'var_assign',
    message0: '赋值 %1 为 %2',
    args0: [
      {
        type: 'field_input',
        name: 'NAME',
        text: 'x',
      },
      {
        type: 'input_value',
        name: 'VALUE',
      },
    ],
    previousStatement: null,
    nextStatement: null,
    colour: 330,
  },
  {
    type: 'var_get',
    message0: '%1',
    args0: [
      {
        type: 'field_input',
        name: 'NAME',
        text: 'x',
      },
    ],
    output: null,
    colour: 330,
  },
  {
    type: 'io_read',
    message0: '输入 %1',
    args0: [
      {
        type: 'field_input',
        name: 'NAME',
        text: 'x',
      },
    ],
    previousStatement: null,
    nextStatement: null,
    colour: 210,
  },
  {
    type: 'io_println',
    message0: '输出 %1',
    args0: [
      {
        type: 'input_value',
        name: 'VALUE',
      },
    ],
    previousStatement: null,
    nextStatement: null,
    colour: 210,
  },
]);

cppGenerator.forBlock['io_read'] = function (block) {
  const varName = toVarName(block);
  return `cin >> ${varName};`;
};

cppGenerator.forBlock['io_println'] = function (block) {
  const val = cppGenerator.valueToCode(block, 'VALUE', cppGenerator.ORDER_NONE) || '0';
  return `cout << ${val} << '\\n';`;
};

const toolbox = {
  kind: 'categoryToolbox',
  contents: [
    {
      kind: 'category',
      name: '常用',
      colour: 290,
      contents: [{ kind: 'block', type: 'program_main' }, { kind: 'block', type: 'program_end' }],
    },
    {
      kind: 'category',
      name: '变量集',
      colour: 60,
      contents: [
        {
          kind: 'category',
          name: '变量',
          colour: 330,
          contents: [
            { kind: 'block', type: 'var_define' },
            { kind: 'block', type: 'var_assign' },
            { kind: 'block', type: 'var_get' },
          ],
        },
        {
          kind: 'category',
          name: '数组',
          colour: 285,
          contents: [
            {
              kind: 'block',
              type: 'array_define_1d',
              inputs: {
                LEN1: {
                  shadow: {
                    type: 'math_number',
                    fields: { NUM: 1 },
                  },
                },
              },
            },
            {
              kind: 'block',
              type: 'array_define_2d',
              inputs: {
                LEN1: {
                  shadow: {
                    type: 'math_number',
                    fields: { NUM: 1 },
                  },
                },
                LEN2: {
                  shadow: {
                    type: 'math_number',
                    fields: { NUM: 1 },
                  },
                },
              },
            },
            {
              kind: 'block',
              type: 'array_set',
              inputs: {
                I1: {
                  shadow: {
                    type: 'math_number',
                    fields: { NUM: 0 },
                  },
                },
              },
            },
            {
              kind: 'block',
              type: 'array_get',
              inputs: {
                I1: {
                  shadow: {
                    type: 'math_number',
                    fields: { NUM: 0 },
                  },
                },
              },
            },
          ],
        },
      ],
    },
    {
      kind: 'category',
      name: '逻辑',
      categorystyle: 'logic_category',
      contents: [
        { kind: 'block', type: 'controls_if' },
        { kind: 'block', type: 'logic_compare' },
        { kind: 'block', type: 'logic_operation' },
        { kind: 'block', type: 'logic_negate' },
      ],
    },
    {
      kind: 'category',
      name: '循环',
      categorystyle: 'loop_category',
      contents: [
        {
          kind: 'block',
          type: 'controls_for_custom',
          inputs: {
            FROM: {
              shadow: {
                type: 'math_number',
                fields: { NUM: 1 },
              },
            },
            TO: {
              shadow: {
                type: 'math_number',
                fields: { NUM: 1 },
              },
            },
            BY: {
              shadow: {
                type: 'math_number',
                fields: { NUM: 1 },
              },
            },
          },
        },
        { kind: 'block', type: 'controls_whileUntil' },
      ],
    },
    {
      kind: 'category',
      name: '算术',
      categorystyle: 'math_category',
      contents: [
        { kind: 'block', type: 'math_number' },
        { kind: 'block', type: 'math_arithmetic' },
      ],
    },
    {
      kind: 'category',
      name: '文本',
      categorystyle: 'text_category',
      contents: [{ kind: 'block', type: 'text' }],
    },
    {
      kind: 'category',
      name: '输入/输出',
      colour: 210,
      contents: [
        { kind: 'block', type: 'io_read' },
        { kind: 'block', type: 'io_println' },
      ],
    },
  ],
};

const generate = () => {
  if (!workspace) return;
  cppGenerator.init(workspace);
  const code = cppGenerator.workspaceToCode(workspace);
  emit('update:code', code);
  const xml = Blockly.Xml.domToText(Blockly.Xml.workspaceToDom(workspace));
  emit('update:workspaceXml', xml);
  lastEmittedWorkspaceXml = xml;
};

let ignorePropUpdate = false;
let lastEmittedWorkspaceXml = '';

let restoreBlocklyDialogs = null;

const ensureDialogDom = () => {
  let root = document.getElementById('blockly-custom-dialog');
  if (root) return root;
  root = document.createElement('div');
  root.id = 'blockly-custom-dialog';
  root.style.display = 'none';
  root.innerHTML = `
    <div class="blockly-custom-dialog__mask"></div>
    <div class="blockly-custom-dialog__panel" role="dialog" aria-modal="true">
      <div class="blockly-custom-dialog__title">提示</div>
      <div class="blockly-custom-dialog__content"></div>
      <input class="blockly-custom-dialog__input" />
      <div class="blockly-custom-dialog__actions">
        <button class="blockly-custom-dialog__btn blockly-custom-dialog__btn--cancel" type="button">取消</button>
        <button class="blockly-custom-dialog__btn blockly-custom-dialog__btn--ok" type="button">确定</button>
      </div>
    </div>
  `;
  document.body.appendChild(root);
  return root;
};

const showBlocklyDialog = (type, message, defaultValue) => {
  const root = ensureDialogDom();
  const content = root.querySelector('.blockly-custom-dialog__content');
  const input = root.querySelector('.blockly-custom-dialog__input');
  const btnCancel = root.querySelector('.blockly-custom-dialog__btn--cancel');
  const btnOk = root.querySelector('.blockly-custom-dialog__btn--ok');
  const mask = root.querySelector('.blockly-custom-dialog__mask');

  content.textContent = (message ?? '').toString();
  input.value = (defaultValue ?? '').toString();
  input.style.display = type === 'prompt' ? 'block' : 'none';
  btnCancel.style.display = type === 'alert' ? 'none' : 'inline-flex';
  root.style.display = 'block';

  const cleanup = () => {
    root.style.display = 'none';
    btnCancel.onclick = null;
    btnOk.onclick = null;
    mask.onclick = null;
    input.onkeydown = null;
  };

  return new Promise((resolve) => {
    const ok = () => {
      const val = type === 'prompt' ? input.value : true;
      cleanup();
      resolve(val);
    };
    const cancel = () => {
      cleanup();
      resolve(type === 'confirm' ? false : null);
    };

    btnOk.onclick = ok;
    btnCancel.onclick = cancel;
    mask.onclick = cancel;
    input.onkeydown = (e) => {
      if (e.key === 'Enter') ok();
      if (e.key === 'Escape') cancel();
    };

    if (type === 'prompt') {
      setTimeout(() => {
        input.focus();
        input.select();
      }, 0);
    } else {
      setTimeout(() => btnOk.focus(), 0);
    }
  });
};

const setupBlocklyDialogs = () => {
  const oldAlert = Blockly.alert;
  const oldConfirm = Blockly.confirm;
  const oldPrompt = Blockly.prompt;
  const oldDialog = Blockly.dialog
    ? {
        alert: Blockly.dialog.alert,
        confirm: Blockly.dialog.confirm,
        prompt: Blockly.dialog.prompt,
      }
    : null;

  const oldUtilsDialog = Blockly.utils?.dialog
    ? {
        alert: Blockly.utils.dialog.alert,
        confirm: Blockly.utils.dialog.confirm,
        prompt: Blockly.utils.dialog.prompt,
      }
    : null;

  Blockly.alert = (message, callback) => {
    showBlocklyDialog('alert', message).then(() => callback && callback());
  };
  Blockly.confirm = (message, callback) => {
    showBlocklyDialog('confirm', message).then((ok) => callback && callback(!!ok));
  };
  Blockly.prompt = (message, defaultValue, callback) => {
    showBlocklyDialog('prompt', message, defaultValue).then((val) => callback && callback(val));
  };

  if (Blockly.dialog) {
    Blockly.dialog.alert = (message, callback) => {
      showBlocklyDialog('alert', message).then(() => callback && callback());
    };
    Blockly.dialog.confirm = (message, callback) => {
      showBlocklyDialog('confirm', message).then((ok) => callback && callback(!!ok));
    };
    Blockly.dialog.prompt = (message, defaultValue, callback) => {
      showBlocklyDialog('prompt', message, defaultValue).then((val) => callback && callback(val));
    };
  }

  restoreBlocklyDialogs = () => {
    Blockly.alert = oldAlert;
    Blockly.confirm = oldConfirm;
    Blockly.prompt = oldPrompt;
    if (Blockly.dialog && oldDialog) {
      Blockly.dialog.alert = oldDialog.alert;
      Blockly.dialog.confirm = oldDialog.confirm;
      Blockly.dialog.prompt = oldDialog.prompt;
    }
    if (Blockly.utils?.dialog && oldUtilsDialog) {
      Blockly.utils.dialog.alert = oldUtilsDialog.alert;
      Blockly.utils.dialog.confirm = oldUtilsDialog.confirm;
      Blockly.utils.dialog.prompt = oldUtilsDialog.prompt;
    }
    restoreBlocklyDialogs = null;
  };
};

const ensureMainBlock = () => {
  if (!workspace) return;
  const blocks = workspace.getAllBlocks(false) || [];
  if (blocks.length > 0) return;

  const main = workspace.newBlock('program_main');
  main.initSvg();
  main.render();
  main.moveBy(380, 80);

  const end = workspace.newBlock('program_end');
  end.initSvg();
  end.render();

  const bodyConn = main.getInput('DO')?.connection;
  if (bodyConn && end.previousConnection) {
    bodyConn.connect(end.previousConnection);
  }
};

onMounted(() => {
  setupBlocklyDialogs();
  workspace = Blockly.inject(containerRef.value, {
    toolbox,
    scrollbars: true,
    trashcan: true,
    renderer: 'zelos',
  });

  if (props.workspaceXml) {
    try {
      const dom = sanitizeWorkspaceDom(Blockly.Xml.textToDom(props.workspaceXml));
      Blockly.Xml.domToWorkspace(dom, workspace);
    } catch (_) {}
  }

  ensureMainBlock();

  workspace.addChangeListener(() => {
    if (ignorePropUpdate) return;
    generate();
  });

  generate();
});

watch(
  () => props.workspaceXml,
  val => {
    if (!workspace) return;
    if (!val) return;
    if (val === lastEmittedWorkspaceXml) return;
    try {
      const dom = sanitizeWorkspaceDom(Blockly.Xml.textToDom(val));
      ignorePropUpdate = true;
      workspace.clear();
      Blockly.Xml.domToWorkspace(dom, workspace);
      lastEmittedWorkspaceXml = val;
    } catch (_) {
    } finally {
      ignorePropUpdate = false;
      ensureMainBlock();
      generate();
    }
  }
);

onBeforeUnmount(() => {
  if (restoreBlocklyDialogs) restoreBlocklyDialogs();
  if (workspace) {
    workspace.dispose();
    workspace = null;
  }
});
</script>

<template>
  <div ref="containerRef" style="width: 100%; height: 600px"></div>
</template>

<style>
:global(.blocklyWidgetDiv),
:global(.blocklyDropDownDiv),
:global(.blocklyTooltipDiv) {
  z-index: 99999;
}

:global(#blockly-custom-dialog) {
  position: fixed;
  inset: 0;
  z-index: 100000;
}

:global(#blockly-custom-dialog .blockly-custom-dialog__mask) {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
}

:global(#blockly-custom-dialog .blockly-custom-dialog__panel) {
  position: absolute;
  left: 50%;
  top: 20%;
  transform: translateX(-50%);
  width: 520px;
  max-width: calc(100vw - 32px);
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  padding: 16px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

:global(#blockly-custom-dialog .blockly-custom-dialog__title) {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #111;
}

:global(#blockly-custom-dialog .blockly-custom-dialog__content) {
  font-size: 14px;
  color: #333;
  line-height: 1.4;
  white-space: pre-wrap;
}

:global(#blockly-custom-dialog .blockly-custom-dialog__input) {
  margin-top: 12px;
  width: 100%;
  box-sizing: border-box;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid #d9d9d9;
  outline: none;
}

:global(#blockly-custom-dialog .blockly-custom-dialog__input:focus) {
  border-color: #18a058;
  box-shadow: 0 0 0 3px rgba(24, 160, 88, 0.18);
}

:global(#blockly-custom-dialog .blockly-custom-dialog__actions) {
  margin-top: 14px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:global(#blockly-custom-dialog .blockly-custom-dialog__btn) {
  appearance: none;
  border: 0;
  border-radius: 10px;
  padding: 8px 14px;
  font-size: 14px;
  cursor: pointer;
}

:global(#blockly-custom-dialog .blockly-custom-dialog__btn--cancel) {
  background: #f2f2f2;
  color: #222;
}

:global(#blockly-custom-dialog .blockly-custom-dialog__btn--ok) {
  background: #18a058;
  color: #fff;
}
</style>
