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
  cppGenerator._procedureDefs = new Map();
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
  const procedureDefs = cppGenerator._procedureDefs && cppGenerator._procedureDefs.size
    ? Array.from(cppGenerator._procedureDefs.values()).join('\n\n') + '\n\n'
    : '';
  const mainStart = `int main(){\n  ios::sync_with_stdio(false);\n  cin.tie(nullptr);\n`;
  const mainEnd = `\n  return 0;\n}`;

  const combined = [
    header,
    procedureDefs,
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
    colour: 25,
  },
  {
    type: 'io_read_int',
    message0: '读入一个整数',
    output: 'Number',
    colour: 25,
  },
  {
    type: 'io_read_float',
    message0: '读入一个浮点数',
    output: 'Number',
    colour: 25,
  },
  {
    type: 'io_read_string',
    message0: '读入一个字符串',
    output: 'String',
    colour: 25,
  },
  {
    type: 'io_read_line',
    message0: '读入一行',
    output: 'String',
    colour: 25,
  },
  {
    type: 'io_print',
    message0: '输出 %1',
    args0: [
      {
        type: 'input_value',
        name: 'VALUE',
      },
    ],
    previousStatement: null,
    nextStatement: null,
    colour: 25,
  },
  {
    type: 'io_println',
    message0: '输出 %1 并换行',
    args0: [
      {
        type: 'input_value',
        name: 'VALUE',
      },
    ],
    previousStatement: null,
    nextStatement: null,
    colour: 25,
  },
]);

cppGenerator.forBlock['io_read'] = function (block) {
  const varName = toVarName(block);
  return `cin >> ${varName};`;
};

cppGenerator.forBlock['io_read_int'] = function (_block) {
  return [`([&](){ long long __x; cin >> __x; return __x; })()`, cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['io_read_float'] = function (_block) {
  return [`([&](){ double __x; cin >> __x; return __x; })()`, cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['io_read_string'] = function (_block) {
  return [`([&](){ string __s; cin >> __s; return __s; })()`, cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['io_read_line'] = function (_block) {
  return [`([&](){ string __s; getline(cin >> ws, __s); return __s; })()`, cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['io_print'] = function (block) {
  const val = cppGenerator.valueToCode(block, 'VALUE', cppGenerator.ORDER_NONE) || '0';
  return `cout << ${val};`;
};

cppGenerator.forBlock['io_println'] = function (block) {
  const val = cppGenerator.valueToCode(block, 'VALUE', cppGenerator.ORDER_NONE) || '0';
  return `cout << ${val} << '\\n';`;
};

const toCppStringLiteral = (val) => JSON.stringify((val ?? '').toString());

const asStringExpr = (expr) => `([&](){ std::ostringstream __oss; __oss << (${expr}); return __oss.str(); })()`;

const asSimpleIdentifier = (expr) => {
  const m = (expr || '').trim().match(/^[A-Za-z_]\w*$/);
  return m ? m[0] : null;
};

const listIndexExpr = (where, listExpr, atExpr) => {
  switch (where) {
    case 'FIRST':
      return '0';
    case 'LAST':
      return `(long long)(${listExpr}.size()) - 1`;
    case 'FROM_END':
      return `(long long)(${listExpr}.size()) - (${atExpr})`;
    case 'RANDOM':
      return `(long long)(rand() % ${listExpr}.size())`;
    case 'FROM_START':
    default:
      return `(${atExpr}) - 1`;
  }
};

cppGenerator.forBlock['logic_boolean'] = function (block) {
  return [block.getFieldValue('BOOL') === 'TRUE' ? 'true' : 'false', cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['logic_null'] = function (_block) {
  return ['nullptr', cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['logic_ternary'] = function (block) {
  const condition = cppGenerator.valueToCode(block, 'IF', cppGenerator.ORDER_NONE) || 'false';
  const thenExpr = cppGenerator.valueToCode(block, 'THEN', cppGenerator.ORDER_NONE) || '0';
  const elseExpr = cppGenerator.valueToCode(block, 'ELSE', cppGenerator.ORDER_NONE) || '0';
  return [`((${condition}) ? (${thenExpr}) : (${elseExpr}))`, cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['controls_repeat_ext'] = function (block) {
  const repeats = block.getInput('TIMES')
    ? cppGenerator.valueToCode(block, 'TIMES', cppGenerator.ORDER_NONE) || '0'
    : Number(block.getFieldValue('TIMES')) || '0';
  const branch = cppGenerator.statementToCode(block, 'DO');
  const loopVar = cppGenerator.nameDB_.getDistinctName('count', Blockly.VARIABLE_CATEGORY_NAME);
  return `for (long long ${loopVar} = 0; ${loopVar} < (${repeats}); ++${loopVar}) {\n${branch}}`;
};

cppGenerator.forBlock['controls_forEach'] = function (block) {
  const itemName = toVarName(block);
  const listExpr = cppGenerator.valueToCode(block, 'LIST', cppGenerator.ORDER_NONE) || 'vector<long long>{}';
  const branch = cppGenerator.statementToCode(block, 'DO');
  return `for (auto ${itemName} : ${listExpr}) {\n${branch}}`;
};

cppGenerator.forBlock['controls_flow_statements'] = function (block) {
  return block.getFieldValue('FLOW') === 'BREAK' ? 'break;' : 'continue;';
};

cppGenerator.forBlock['math_random_float'] = function (_block) {
  return ['((double)rand() / (double)RAND_MAX)', cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['math_atan2'] = function (block) {
  const x = cppGenerator.valueToCode(block, 'X', cppGenerator.ORDER_NONE) || '0';
  const y = cppGenerator.valueToCode(block, 'Y', cppGenerator.ORDER_NONE) || '0';
  return [`(atan2(${y}, ${x}) * 180.0 / M_PI)`, cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['text'] = function (block) {
  return [toCppStringLiteral(block.getFieldValue('TEXT')), cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['text_join'] = function (block) {
  const itemCount = block.itemCount_ || 0;
  if (itemCount === 0) return ['""', cppGenerator.ORDER_ATOMIC];
  const parts = [];
  for (let i = 0; i < itemCount; i++) {
    const part = cppGenerator.valueToCode(block, `ADD${i}`, cppGenerator.ORDER_NONE) || '""';
    parts.push(asStringExpr(part));
  }
  return [parts.join(' + '), cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['text_length'] = function (block) {
  const textExpr = cppGenerator.valueToCode(block, 'VALUE', cppGenerator.ORDER_NONE) || '""';
  return [`((long long)${asStringExpr(textExpr)}.size())`, cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['text_isEmpty'] = function (block) {
  const textExpr = cppGenerator.valueToCode(block, 'VALUE', cppGenerator.ORDER_NONE) || '""';
  return [`(${asStringExpr(textExpr)}.empty())`, cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['text_indexOf'] = function (block) {
  const textExpr = cppGenerator.valueToCode(block, 'VALUE', cppGenerator.ORDER_NONE) || '""';
  const findExpr = cppGenerator.valueToCode(block, 'FIND', cppGenerator.ORDER_NONE) || '""';
  const end = block.getFieldValue('END') || 'FIRST';
  const finder = end === 'LAST' ? 'rfind' : 'find';
  return [
    `([&](){ string __t = ${asStringExpr(textExpr)}; string __f = ${asStringExpr(findExpr)}; auto __p = __t.${finder}(__f); return __p == string::npos ? 0LL : (long long)__p + 1; })()`,
    cppGenerator.ORDER_ATOMIC,
  ];
};

cppGenerator.forBlock['text_charAt'] = function (block) {
  const textExpr = cppGenerator.valueToCode(block, 'VALUE', cppGenerator.ORDER_NONE) || '""';
  const where = block.getFieldValue('WHERE') || 'FROM_START';
  const at = cppGenerator.valueToCode(block, 'AT', cppGenerator.ORDER_NONE) || '1';
  const idx = where === 'FIRST'
    ? '0'
    : where === 'LAST'
      ? '(long long)__t.size() - 1'
      : where === 'FROM_END'
        ? `(long long)__t.size() - (${at})`
        : where === 'RANDOM'
          ? '(long long)(rand() % __t.size())'
          : `(${at}) - 1`;
  return [
    `([&](){ string __t = ${asStringExpr(textExpr)}; if (__t.empty()) return string(""); long long __idx = ${idx}; if (__idx < 0 || __idx >= (long long)__t.size()) return string(""); return string(1, __t[(size_t)__idx]); })()`,
    cppGenerator.ORDER_ATOMIC,
  ];
};

cppGenerator.forBlock['text_getSubstring'] = function (block) {
  const textExpr = cppGenerator.valueToCode(block, 'STRING', cppGenerator.ORDER_NONE) || '""';
  const where1 = block.getFieldValue('WHERE1') || 'FROM_START';
  const where2 = block.getFieldValue('WHERE2') || 'FROM_START';
  const at1 = cppGenerator.valueToCode(block, 'AT1', cppGenerator.ORDER_NONE) || '1';
  const at2 = cppGenerator.valueToCode(block, 'AT2', cppGenerator.ORDER_NONE) || '1';
  const start = where1 === 'FIRST' ? '0' : where1 === 'FROM_END' ? `(long long)__t.size() - (${at1})` : `(${at1}) - 1`;
  const end = where2 === 'LAST' ? '(long long)__t.size() - 1' : where2 === 'FROM_END' ? `(long long)__t.size() - (${at2})` : `(${at2}) - 1`;
  return [
    `([&](){ string __t = ${asStringExpr(textExpr)}; if (__t.empty()) return string(""); long long __s = ${start}; long long __e = ${end}; if (__s < 0) __s = 0; if (__e >= (long long)__t.size()) __e = (long long)__t.size() - 1; if (__s > __e) return string(""); return __t.substr((size_t)__s, (size_t)(__e - __s + 1)); })()`,
    cppGenerator.ORDER_ATOMIC,
  ];
};

cppGenerator.forBlock['text_changeCase'] = function (block) {
  const textExpr = cppGenerator.valueToCode(block, 'TEXT', cppGenerator.ORDER_NONE) || '""';
  const mode = block.getFieldValue('CASE') || 'UPPERCASE';
  if (mode === 'LOWERCASE') {
    return [
      `([&](){ string __s = ${asStringExpr(textExpr)}; for (char &c : __s) c = (char)tolower((unsigned char)c); return __s; })()`,
      cppGenerator.ORDER_ATOMIC,
    ];
  }
  if (mode === 'TITLECASE') {
    return [
      `([&](){ string __s = ${asStringExpr(textExpr)}; bool __nw = true; for (char &c : __s) { if (isspace((unsigned char)c)) { __nw = true; } else { c = (char)(__nw ? toupper((unsigned char)c) : tolower((unsigned char)c)); __nw = false; } } return __s; })()`,
      cppGenerator.ORDER_ATOMIC,
    ];
  }
  return [
    `([&](){ string __s = ${asStringExpr(textExpr)}; for (char &c : __s) c = (char)toupper((unsigned char)c); return __s; })()`,
    cppGenerator.ORDER_ATOMIC,
  ];
};

cppGenerator.forBlock['text_trim'] = function (block) {
  const textExpr = cppGenerator.valueToCode(block, 'TEXT', cppGenerator.ORDER_NONE) || '""';
  const mode = block.getFieldValue('MODE') || 'BOTH';
  return [
    `([&](){ string __s = ${asStringExpr(textExpr)}; size_t __l = 0, __r = __s.size(); if ('${mode}' != 'RIGHT') while (__l < __r && isspace((unsigned char)__s[__l])) ++__l; if ('${mode}' != 'LEFT') while (__r > __l && isspace((unsigned char)__s[__r - 1])) --__r; return __s.substr(__l, __r - __l); })()`,
    cppGenerator.ORDER_ATOMIC,
  ];
};

cppGenerator.forBlock['lists_create_empty'] = function (_block) {
  return ['vector<long long>{}', cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['lists_create_with'] = function (block) {
  const itemCount = block.itemCount_ || 0;
  const items = [];
  for (let i = 0; i < itemCount; i++) {
    items.push(cppGenerator.valueToCode(block, `ADD${i}`, cppGenerator.ORDER_NONE) || '0');
  }
  return [`vector<long long>{${items.join(', ')}}`, cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['lists_repeat'] = function (block) {
  const item = cppGenerator.valueToCode(block, 'ITEM', cppGenerator.ORDER_NONE) || '0';
  const num = cppGenerator.valueToCode(block, 'NUM', cppGenerator.ORDER_NONE) || '0';
  return [`vector<long long>((long long)(${num}), ${item})`, cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['lists_length'] = function (block) {
  const listExpr = cppGenerator.valueToCode(block, 'VALUE', cppGenerator.ORDER_NONE) || 'vector<long long>{}';
  return [`((long long)(${listExpr}).size())`, cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['lists_isEmpty'] = function (block) {
  const listExpr = cppGenerator.valueToCode(block, 'VALUE', cppGenerator.ORDER_NONE) || 'vector<long long>{}';
  return [`(${listExpr}).empty()`, cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['lists_indexOf'] = function (block) {
  const listExpr = cppGenerator.valueToCode(block, 'VALUE', cppGenerator.ORDER_NONE) || 'vector<long long>{}';
  const findExpr = cppGenerator.valueToCode(block, 'FIND', cppGenerator.ORDER_NONE) || '0';
  const end = block.getFieldValue('END') || 'FIRST';
  if (end === 'LAST') {
    return [
      `([&](){ auto __l = ${listExpr}; for (long long __i = (long long)__l.size() - 1; __i >= 0; --__i) { if (__l[(size_t)__i] == (${findExpr})) return __i + 1; } return 0LL; })()`,
      cppGenerator.ORDER_ATOMIC,
    ];
  }
  return [
    `([&](){ auto __l = ${listExpr}; for (size_t __i = 0; __i < __l.size(); ++__i) { if (__l[__i] == (${findExpr})) return (long long)__i + 1; } return 0LL; })()`,
    cppGenerator.ORDER_ATOMIC,
  ];
};

cppGenerator.forBlock['lists_getIndex'] = function (block) {
  const mode = block.getFieldValue('MODE') || 'GET';
  const where = block.getFieldValue('WHERE') || 'FROM_START';
  const listExpr = cppGenerator.valueToCode(block, 'VALUE', cppGenerator.ORDER_NONE) || '';
  const listName = asSimpleIdentifier(listExpr);
  const at = cppGenerator.valueToCode(block, 'AT', cppGenerator.ORDER_NONE) || '1';
  if (!listName) {
    return mode === 'REMOVE' ? '' : ['0', cppGenerator.ORDER_ATOMIC];
  }
  const idxExpr = listIndexExpr(where, listName, at);
  if (mode === 'REMOVE') {
    return `if (!${listName}.empty()) { long long __idx = ${idxExpr}; if (__idx >= 0 && __idx < (long long)${listName}.size()) ${listName}.erase(${listName}.begin() + __idx); }`;
  }
  if (mode === 'GET_REMOVE') {
    return [
      `([&](){ if (${listName}.empty()) return 0LL; long long __idx = ${idxExpr}; if (__idx < 0 || __idx >= (long long)${listName}.size()) return 0LL; long long __v = ${listName}[(size_t)__idx]; ${listName}.erase(${listName}.begin() + __idx); return __v; })()`,
      cppGenerator.ORDER_ATOMIC,
    ];
  }
  return [
    `([&](){ if (${listName}.empty()) return 0LL; long long __idx = ${idxExpr}; if (__idx < 0 || __idx >= (long long)${listName}.size()) return 0LL; return ${listName}[(size_t)__idx]; })()`,
    cppGenerator.ORDER_ATOMIC,
  ];
};

cppGenerator.forBlock['lists_setIndex'] = function (block) {
  const mode = block.getFieldValue('MODE') || 'SET';
  const where = block.getFieldValue('WHERE') || 'FROM_START';
  const listExpr = cppGenerator.valueToCode(block, 'LIST', cppGenerator.ORDER_NONE) || '';
  const listName = asSimpleIdentifier(listExpr);
  const at = cppGenerator.valueToCode(block, 'AT', cppGenerator.ORDER_NONE) || '1';
  const toExpr = cppGenerator.valueToCode(block, 'TO', cppGenerator.ORDER_NONE) || '0';
  if (!listName) return '';
  const idxExpr = listIndexExpr(where, listName, at);
  if (mode === 'INSERT') {
    return `if (${listName}.empty()) { ${listName}.push_back(${toExpr}); } else { long long __idx = ${idxExpr}; if (__idx < 0) __idx = 0; if (__idx > (long long)${listName}.size()) __idx = (long long)${listName}.size(); ${listName}.insert(${listName}.begin() + __idx, ${toExpr}); }`;
  }
  return `if (!${listName}.empty()) { long long __idx = ${idxExpr}; if (__idx >= 0 && __idx < (long long)${listName}.size()) ${listName}[(size_t)__idx] = ${toExpr}; }`;
};

cppGenerator.forBlock['lists_getSublist'] = function (block) {
  const listExpr = cppGenerator.valueToCode(block, 'LIST', cppGenerator.ORDER_NONE) || 'vector<long long>{}';
  const where1 = block.getFieldValue('WHERE1') || 'FROM_START';
  const where2 = block.getFieldValue('WHERE2') || 'FROM_START';
  const at1 = cppGenerator.valueToCode(block, 'AT1', cppGenerator.ORDER_NONE) || '1';
  const at2 = cppGenerator.valueToCode(block, 'AT2', cppGenerator.ORDER_NONE) || '1';
  const start = where1 === 'FIRST' ? '0' : where1 === 'FROM_END' ? `(long long)__src.size() - (${at1})` : `(${at1}) - 1`;
  const end = where2 === 'LAST' ? '(long long)__src.size() - 1' : where2 === 'FROM_END' ? `(long long)__src.size() - (${at2})` : `(${at2}) - 1`;
  return [
    `([&](){ auto __src = ${listExpr}; vector<long long> __out; if (__src.empty()) return __out; long long __s = ${start}; long long __e = ${end}; if (__s < 0) __s = 0; if (__e >= (long long)__src.size()) __e = (long long)__src.size() - 1; if (__s > __e) return __out; __out.insert(__out.end(), __src.begin() + __s, __src.begin() + __e + 1); return __out; })()`,
    cppGenerator.ORDER_ATOMIC,
  ];
};

cppGenerator.forBlock['lists_split'] = function (block) {
  const mode = block.getFieldValue('MODE') || 'SPLIT';
  const input = cppGenerator.valueToCode(block, 'INPUT', cppGenerator.ORDER_NONE) || '""';
  const delim = cppGenerator.valueToCode(block, 'DELIM', cppGenerator.ORDER_NONE) || '","';
  if (mode === 'JOIN') {
    return [
      `([&](){ auto __v = ${input}; string __d = ${asStringExpr(delim)}; std::ostringstream __oss; for (size_t __i = 0; __i < __v.size(); ++__i) { if (__i) __oss << __d; __oss << __v[__i]; } return __oss.str(); })()`,
      cppGenerator.ORDER_ATOMIC,
    ];
  }
  return [
    `([&](){ string __s = ${asStringExpr(input)}; string __d = ${asStringExpr(delim)}; vector<long long> __out; if (__d.empty()) { for (char __c : __s) __out.push_back((long long)__c); return __out; } size_t __pos = 0; while (true) { size_t __p = __s.find(__d, __pos); string __tok = (__p == string::npos) ? __s.substr(__pos) : __s.substr(__pos, __p - __pos); try { __out.push_back(stoll(__tok)); } catch (...) { __out.push_back(0); } if (__p == string::npos) break; __pos = __p + __d.size(); } return __out; })()`,
    cppGenerator.ORDER_ATOMIC,
  ];
};

cppGenerator.forBlock['lists_sort'] = function (block) {
  const dir = block.getFieldValue('DIRECTION') || '1';
  const listExpr = cppGenerator.valueToCode(block, 'LIST', cppGenerator.ORDER_NONE) || 'vector<long long>{}';
  const reverseCode = dir === '-1' ? 'reverse(__v.begin(), __v.end()); ' : '';
  return [
    `([&](){ auto __v = ${listExpr}; sort(__v.begin(), __v.end()); ${reverseCode}return __v; })()`,
    cppGenerator.ORDER_ATOMIC,
  ];
};

cppGenerator.forBlock['procedures_defnoreturn'] = function (block) {
  const def = block.getProcedureDef ? block.getProcedureDef() : null;
  const rawName = def?.[0] || block.getFieldValue('NAME') || 'doSomething';
  const args = def?.[1] || [];
  const funcName = cppGenerator.nameDB_.getName(rawName, Blockly.PROCEDURE_CATEGORY_NAME);
  const argDecl = args
    .map((arg) => `long long ${cppGenerator.nameDB_.getName(arg, Blockly.VARIABLE_CATEGORY_NAME)}`)
    .join(', ');
  const body = cppGenerator.statementToCode(block, 'STACK');
  cppGenerator._procedureDefs.set(funcName, `void ${funcName}(${argDecl}) {\n${body}}`);
  return '';
};

cppGenerator.forBlock['procedures_defreturn'] = function (block) {
  const def = block.getProcedureDef ? block.getProcedureDef() : null;
  const rawName = def?.[0] || block.getFieldValue('NAME') || 'doSomething';
  const args = def?.[1] || [];
  const funcName = cppGenerator.nameDB_.getName(rawName, Blockly.PROCEDURE_CATEGORY_NAME);
  const argDecl = args
    .map((arg) => `long long ${cppGenerator.nameDB_.getName(arg, Blockly.VARIABLE_CATEGORY_NAME)}`)
    .join(', ');
  const body = cppGenerator.statementToCode(block, 'STACK');
  const ret = cppGenerator.valueToCode(block, 'RETURN', cppGenerator.ORDER_NONE) || '0';
  cppGenerator._procedureDefs.set(funcName, `long long ${funcName}(${argDecl}) {\n${body}  return ${ret};\n}`);
  return '';
};

cppGenerator.forBlock['procedures_callnoreturn'] = function (block) {
  const rawName = block.getProcedureCall ? block.getProcedureCall() : block.getFieldValue('NAME');
  const funcName = cppGenerator.nameDB_.getName(rawName || 'doSomething', Blockly.PROCEDURE_CATEGORY_NAME);
  const args = (block.arguments_ || []).map((_, i) =>
    cppGenerator.valueToCode(block, `ARG${i}`, cppGenerator.ORDER_NONE) || '0'
  );
  return `${funcName}(${args.join(', ')});`;
};

cppGenerator.forBlock['procedures_callreturn'] = function (block) {
  const rawName = block.getProcedureCall ? block.getProcedureCall() : block.getFieldValue('NAME');
  const funcName = cppGenerator.nameDB_.getName(rawName || 'doSomething', Blockly.PROCEDURE_CATEGORY_NAME);
  const args = (block.arguments_ || []).map((_, i) =>
    cppGenerator.valueToCode(block, `ARG${i}`, cppGenerator.ORDER_NONE) || '0'
  );
  return [`${funcName}(${args.join(', ')})`, cppGenerator.ORDER_ATOMIC];
};

cppGenerator.forBlock['procedures_ifreturn'] = function (block) {
  const condition = cppGenerator.valueToCode(block, 'CONDITION', cppGenerator.ORDER_NONE) || 'false';
  if (block.hasReturnValue_) {
    const value = cppGenerator.valueToCode(block, 'VALUE', cppGenerator.ORDER_NONE) || '0';
    return `if (${condition}) {\n  return ${value};\n}`;
  }
  return `if (${condition}) {\n  return;\n}`;
};

const rawBlockToCode = cppGenerator.blockToCode.bind(cppGenerator);
cppGenerator.blockToCode = function (block, opt_thisOnly) {
  if (!block) return '';
  const generator = cppGenerator.forBlock[block.type];
  if (!generator) {
    if (block.outputConnection) return ['0', cppGenerator.ORDER_ATOMIC];
    const next = block.nextConnection && block.nextConnection.targetBlock();
    return next ? cppGenerator.blockToCode(next, opt_thisOnly) : '';
  }
  return rawBlockToCode(block, opt_thisOnly);
};


const toolbox = {
  kind: 'categoryToolbox',
  contents: [
    {
      kind: 'category',
      name: '逻辑',
      categorystyle: 'logic_category',
      contents: [
        { kind: 'block', type: 'controls_if' },
        { kind: 'block', type: 'logic_compare' },
        { kind: 'block', type: 'logic_operation' },
        { kind: 'block', type: 'logic_negate' },
        { kind: 'block', type: 'logic_boolean' },
        { kind: 'block', type: 'logic_null' },
        { kind: 'block', type: 'logic_ternary' },
      ],
    },
    {
      kind: 'category',
      name: '循环',
      categorystyle: 'loop_category',
      contents: [
        {
          kind: 'block',
          type: 'controls_repeat_ext',
          inputs: {
            TIMES: {
              shadow: {
                type: 'math_number',
                fields: { NUM: 10 },
              },
            },
          },
        },
        { kind: 'block', type: 'controls_whileUntil' },
        {
          kind: 'block',
          type: 'controls_for',
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
                fields: { NUM: 10 },
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
        { kind: 'block', type: 'controls_forEach' },
        { kind: 'block', type: 'controls_flow_statements' },
      ],
    },
    {
      kind: 'category',
      name: '数学',
      categorystyle: 'math_category',
      contents: [
        { kind: 'block', type: 'math_number' },
        { kind: 'block', type: 'math_arithmetic' },
        { kind: 'block', type: 'math_single' },
        { kind: 'block', type: 'math_round' },
        { kind: 'block', type: 'math_modulo' },
        {
          kind: 'block',
          type: 'math_random_int',
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
                fields: { NUM: 100 },
              },
            },
          },
        },
        { kind: 'block', type: 'math_random_float' },
        {
          kind: 'block',
          type: 'math_atan2',
          inputs: {
            X: {
              shadow: {
                type: 'math_number',
                fields: { NUM: 1 },
              },
            },
            Y: {
              shadow: {
                type: 'math_number',
                fields: { NUM: 1 },
              },
            },
          },
        },
      ],
    },
    {
      kind: 'category',
      name: '文本',
      categorystyle: 'text_category',
      contents: [
        { kind: 'block', type: 'text' },
        { kind: 'block', type: 'text_join' },
        { kind: 'block', type: 'text_length' },
        { kind: 'block', type: 'text_isEmpty' },
        { kind: 'block', type: 'text_indexOf' },
        { kind: 'block', type: 'text_charAt' },
        { kind: 'block', type: 'text_getSubstring' },
        { kind: 'block', type: 'text_changeCase' },
        { kind: 'block', type: 'text_trim' },
      ],
    },
    {
      kind: 'category',
      name: '列表',
      categorystyle: 'list_category',
      contents: [
        { kind: 'block', type: 'lists_create_empty' },
        { kind: 'block', type: 'lists_create_with' },
        {
          kind: 'block',
          type: 'lists_repeat',
          inputs: {
            ITEM: {
              shadow: {
                type: 'math_number',
                fields: { NUM: 0 },
              },
            },
            NUM: {
              shadow: {
                type: 'math_number',
                fields: { NUM: 5 },
              },
            },
          },
        },
        { kind: 'block', type: 'lists_length' },
        { kind: 'block', type: 'lists_isEmpty' },
        { kind: 'block', type: 'lists_indexOf' },
        {
          kind: 'block',
          type: 'lists_getIndex',
          inputs: {
            AT: {
              shadow: {
                type: 'math_number',
                fields: { NUM: 1 },
              },
            },
          },
        },
        {
          kind: 'block',
          type: 'lists_setIndex',
          inputs: {
            AT: {
              shadow: {
                type: 'math_number',
                fields: { NUM: 1 },
              },
            },
            TO: {
              shadow: {
                type: 'math_number',
                fields: { NUM: 0 },
              },
            },
          },
        },
        {
          kind: 'block',
          type: 'lists_getSublist',
          inputs: {
            AT1: {
              shadow: {
                type: 'math_number',
                fields: { NUM: 1 },
              },
            },
            AT2: {
              shadow: {
                type: 'math_number',
                fields: { NUM: 1 },
              },
            },
          },
        },
        {
          kind: 'block',
          type: 'lists_split',
          inputs: {
            DELIM: {
              shadow: {
                type: 'text',
                fields: { TEXT: ',' },
              },
            },
          },
        },
        { kind: 'block', type: 'lists_sort' },
      ],
    },
    {
      kind: 'category',
      name: '输入输出',
      colour: 25,
      contents: [
        { kind: 'block', type: 'io_read_int' },
        { kind: 'block', type: 'io_read_float' },
        { kind: 'block', type: 'io_read_string' },
        { kind: 'block', type: 'io_read_line' },
        {
          kind: 'block',
          type: 'io_print',
          inputs: {
            VALUE: {
              shadow: {
                type: 'text',
                fields: { TEXT: 'abc' },
              },
            },
          },
        },
        {
          kind: 'block',
          type: 'io_println',
          inputs: {
            VALUE: {
              shadow: {
                type: 'text',
                fields: { TEXT: '' },
              },
            },
          },
        },
      ],
    },
    { kind: 'sep' },
    {
      kind: 'category',
      name: '变量',
      colour: 330,
      custom: 'VARIABLE',
    },
    {
      kind: 'category',
      name: '函数',
      colour: 290,
      custom: 'PROCEDURE',
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

  let main = workspace.getBlocksByType('program_main', false)?.[0] || null;
  if (!main) {
    main = workspace.newBlock('program_main');
    main.initSvg();
    main.render();
    main.moveBy(80, 80);

    const doConn = main.getInput('DO')?.connection;
    if (doConn) {
      const tops = workspace
        .getTopBlocks(true)
        .filter((b) => b.id !== main.id && b.previousConnection && !b.outputConnection && !b.isShadow());
      const first = tops[0];
      if (first?.previousConnection) {
        try {
          doConn.connect(first.previousConnection);
        } catch (_) {}
      }
    }
  }

  main.setDeletable(false);
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
