# 使用官方Python镜像作为基础
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY requirements.txt .
COPY app ./app
COPY run.py ./

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 9877

# 启动命令
CMD ["python", "run.py"]