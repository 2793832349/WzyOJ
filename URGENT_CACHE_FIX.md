# 紧急：浏览器缓存问题

## 问题确认

您的错误日志显示：
```
DELETE http://156.239.242.97/problem/1/file/44%20A+B%E9%97%AE%E9%A2%98%20testdata.zip/
```

这个 URL 有两个旧代码的特征：
1. ❌ 缺少 `/api` 前缀
2. ❌ 有尾部斜杠 `/`

**服务器上部署的新代码是正确的**，已经修复了这两个问题。问题是**您的浏览器缓存了旧的 JavaScript 文件**。

## 验证方法

### 检查加载的 JS 文件

1. 打开浏览器开发者工具（F12）
2. 切换到 "Network" (网络) 标签
3. 刷新页面
4. 查找 `edit.40930e7d.js` 文件
5. 检查它的 "Size" 列：
   - 如果显示 "(disk cache)" 或 "(memory cache)" - **这就是问题所在**
   - 如果显示实际大小（如 "134 KB"） - 说明是从服务器加载的

### 检查请求 URL

1. 在开发者工具的 "Network" 标签中
2. 尝试删除一个文件
3. 查看 DELETE 请求的 URL：
   - ❌ 错误：`http://156.239.242.97/problem/1/file/...` (缺少 /api)
   - ✅ 正确：`http://156.239.242.97/api/problem/1/file/...` (有 /api)

## 解决方案（按优先级）

### 方案 1：硬性重新加载（强烈推荐）

**Chrome/Edge/Firefox (Windows/Linux):**
1. 打开开发者工具（F12）
2. **右键点击**浏览器地址栏旁边的刷新按钮
3. 选择 "清空缓存并硬性重新加载" (Empty Cache and Hard Reload)

**或者使用快捷键：**
- Windows/Linux: `Ctrl + Shift + Delete` 打开清除缓存对话框
- Mac: `Cmd + Shift + Delete`

### 方案 2：禁用缓存（用于测试）

1. 打开开发者工具（F12）
2. 切换到 "Network" 标签
3. 勾选 "Disable cache" (禁用缓存)
4. **保持开发者工具打开**
5. 刷新页面并测试

### 方案 3：无痕模式

1. 打开无痕/隐私浏览窗口：
   - Chrome/Edge: `Ctrl + Shift + N`
   - Firefox: `Ctrl + Shift + P`
   - Safari: `Cmd + Shift + N`
2. 访问网站并测试

### 方案 4：手动清除特定域名的缓存

**Chrome/Edge:**
1. 打开开发者工具（F12）
2. 右键点击刷新按钮
3. 选择 "清空缓存并硬性重新加载"

**Firefox:**
1. 按 `Ctrl + Shift + Delete`
2. 时间范围选择 "全部"
3. 只勾选 "缓存"
4. 点击 "立即清除"

### 方案 5：清除所有浏览器数据（最彻底）

**警告：这会清除所有网站的缓存和 Cookie**

1. Chrome: `chrome://settings/clearBrowserData`
2. Firefox: `about:preferences#privacy`
3. 选择 "缓存的图片和文件"
4. 点击清除

## 成功标志

清除缓存后，您应该看到：

1. ✅ DELETE 请求 URL 包含 `/api` 前缀：
   ```
   DELETE http://156.239.242.97/api/problem/1/file/44%20A%2BB%E9%97%AE%E9%A2%98%20testdata.zip
   ```

2. ✅ 文件名被正确编码（`%20` 代表空格，`%2B` 代表 `+`）

3. ✅ URL 末尾没有斜杠

4. ✅ 返回 204 状态码（成功删除）或 404（文件不存在）

5. ✅ 不再出现 405 错误

## 为什么会发生这个问题？

1. 浏览器默认会缓存 JavaScript 文件以提高性能
2. 虽然 JS 文件名包含哈希值（`edit.40930e7d.js`），但如果浏览器已经缓存了，它可能不会检查新版本
3. 我已经更新了 nginx 配置，添加了缓存控制头，但这只对**新的请求**有效
4. 已经缓存的文件需要手动清除

## 技术细节

当前部署的代码（正确）：
```javascript
Ae.delete(`/problem/${B}/file/${encodeURIComponent(m.name)}`)
```

- ✅ 使用 `encodeURIComponent` 编码文件名
- ✅ 没有尾部斜杠
- ✅ `Ae` 是配置了 `baseURL: "/api"` 的 Axios 实例

旧代码（错误）：
```javascript
Axios.delete(`/problem/${id}/file/${file.name}/`)
```

- ❌ 没有编码文件名
- ❌ 有尾部斜杠

## 如果问题仍然存在

如果清除缓存后问题仍然存在，请提供：

1. 浏览器开发者工具中 Network 标签的截图
2. DELETE 请求的完整 URL
3. DELETE 请求的 Headers（请求头）
4. 浏览器名称和版本

## 联系信息

如果需要进一步帮助，请提供上述调试信息。
