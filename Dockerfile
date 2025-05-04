# 使用官方Python镜像作为基础
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 安装poetry
RUN pip install poetry

# 复制项目文件
COPY pyproject.toml poetry.lock ./
COPY app ./app
COPY run.py ./

# 安装项目依赖
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# 暴露端口
EXPOSE 9870

# 启动命令
CMD ["poetry", "run", "python", "run.py"]