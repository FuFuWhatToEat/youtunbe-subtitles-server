# YouTube 字幕提取 API 文档

## 概述

该 API 提供 YouTube 视频字幕提取功能，支持异步任务提交和结果查询。

## 端点

### 1. 创建字幕提取任务

**URL**: `POST /subtitles`

**请求参数**:

```json
{
  "url": "YouTube视频URL"
}
```

**成功响应** (200 OK):

```json
{
  "task_id": "唯一任务ID",
  "message": "Subtitle extraction started",
  "url": "原始视频URL"
}
```

**错误响应**:

- 400 Bad Request (缺少 URL 参数):

```json
{
  "error": "URL is required in JSON payload"
}
```

### 2. 查询字幕提取结果

**URL**: `GET /subtitles/{task_id}`

**路径参数**:

- `task_id`: 任务 ID

**成功响应** (200 OK):

- 任务完成:

```json
{
  "status": "completed",
  "content": "字幕文本内容",
  "path": "字幕文件存储路径"
}
```

- 任务处理中:

```json
{
  "status": "processing",
  "message": "任务处理中"
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
  "status": "error",
  "message": "Task not found"
}
```

## 使用示例

1. 提交任务:

```bash
curl -X POST http://localhost:5000/subtitles \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

2. 查询结果:

```bash
curl http://localhost:5000/subtitles/12345
```

## 错误代码

| 状态码 | 描述               |
| ------ | ------------------ |
| 400    | 请求参数缺失或无效 |
| 404    | 请求的资源不存在   |
| 500    | 服务器内部错误     |
