# YouTube 字幕提取服务 API 文档

## 基础信息

- **API 根路径**: `/subtitles`
- **Swagger 文档**: `/docs` (访问此路径查看交互式 API 文档)
- **CORS 配置**: 允许所有来源访问，支持 GET/POST/OPTIONS 方法
- **请求日志**: 所有请求和响应都会记录到日志中

## 接口列表

### 1. 创建字幕提取任务

**请求方法**: POST  
**路径**: /subtitles  
**Content-Type**: application/json

**请求参数**:

```json
{
  "url": "YouTube视频URL"
}
```

**成功响应** (200 OK):

```json
{
  "task_id": "唯一任务ID(也是字幕文件名)",
  "message": "Subtitle extraction started",
  "url": "解码后的视频URL"
}
```

**错误响应**:

- 400 Bad Request (缺少 URL 参数):

```json
{
  "error": "URL is required in JSON payload"
}
```

**示例请求**:

```http
POST /subtitles HTTP/1.1
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=example"
}
```

### 2. 获取字幕提取结果

**请求方法**: GET  
**路径**: /subtitles/{task_id}

**路径参数**:

- task_id: 任务 ID(也是字幕文件名，不带扩展名)

**成功响应** (200 OK):

```json
{
  "status": "completed",
  "content": "字幕文本内容",
  "path": "字幕文件存储路径(格式为/subtitles/{task_id}.vtt)"
}
```

**处理中响应** (200 OK):

```json
{
  "status": "processing",
  "message": "任务正在处理中"
}
```

**错误响应**:

- 400 Bad Request (缺少 task_id):

```json
{
  "error": "Task ID is required"
}
```

- 404 Not Found (任务不存在):

```json
{
  "status": "not_found"
}
```

### 3. CORS 预检请求

**请求方法**: OPTIONS  
**路径**: /subtitles

**响应** (200 OK):

```json
{
  "status": "ok",
  "message": "CORS preflight request allowed"
}
```

## 文件命名规则

- 所有生成的字幕文件都使用 task_id 作为文件名
- 文件格式为 WebVTT(.vtt)
- 存储路径为: /subtitles/{task_id}.vtt
