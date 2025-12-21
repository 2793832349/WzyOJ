# 浏览器缓存清除说明

## 问题说明

您遇到的 405 错误和缺少 `/api` 前缀的问题是由于浏览器缓存了旧版本的 JavaScript 文件导致的。

错误日志显示：
```
DELETE http://156.239.242.97/problem/1/file/44%20A+B%E9%97%AE%E9%A2%98%20testdata.zip/ 405 (Not Allowed)
```

这个 URL 有两个问题：
1. 缺少 `/api` 前缀
2. 有尾部斜杠 `/`

这些都是旧代码的特征。新代码已经修复了这些问题。

## 解决方案

### 方法 1：强制刷新（推荐）

在浏览器中按以下快捷键强制刷新页面：

- **Windows/Linux**: `Ctrl + Shift + R` 或 `Ctrl + F5`
- **Mac**: `Cmd + Shift + R`

### 方法 2：清除浏览器缓存

#### Chrome/Edge
1. 按 `F12` 打开开发者工具
2. 右键点击刷新按钮
3. 选择"清空缓存并硬性重新加载"

#### Firefox
1. 按 `Ctrl + Shift + Delete`
2. 选择"缓存"
3. 点击"立即清除"

#### Safari
1. 按 `Cmd + Option + E` 清空缓存
2. 刷新页面

### 方法 3：无痕/隐私模式

在无痕模式下打开网站，这样不会使用缓存的文件。

## 已完成的修复

1. ✅ 修复了前端代码中的文件删除 bug
   - 使用 `encodeURIComponent()` 对文件名进行 URL 编码
   - 移除了 URL 末尾的斜杠

2. ✅ 重新构建并部署了前端

3. ✅ 添加了 nginx 缓存控制头
   - HTML 文件不会被缓存
   - JS/CSS 等静态资源可以长期缓存（因为文件名包含哈希值）

## 验证修复

清除缓存后，删除附件时应该：
1. 请求 URL 应该是：`DELETE http://156.239.242.97/api/problem/1/file/44%20A%2BB%E9%97%AE%E9%A2%98%20testdata.zip`
2. 不应该有 405 错误
3. 文件应该成功删除

## 技术细节

修改的文件：
- `/root/frontend-naive/src/pages/problem/edit/detail.vue` (第 76 行)
- `/root/deploy/config/nginx-templates/default.conf.template` (添加缓存控制)

构建脚本：
- `/root/deploy/build-local-frontend.sh`
