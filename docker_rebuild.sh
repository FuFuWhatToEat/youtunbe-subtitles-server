#!/bin/bash
set -e

IMAGE_NAME="youtube_subtitles"
CONTAINER_NAME="youtube_subtitles_container"
API_URL=${1:-"http://localhost:9870"} # 默认API地址

# 强制停止并删除所有同名容器
echo "清理现有容器..."
docker ps -a --filter "name=${CONTAINER_NAME}" --format "{{.ID}}" | xargs -r docker rm -f

# 清理可能残留的网络
echo "清理残留网络..."
docker network ls --filter "name=${CONTAINER_NAME}" --format "{{.ID}}" | xargs -r docker network rm

# 删除旧镜像
if docker images --format '{{.Repository}}' | grep -q "^${IMAGE_NAME}\$"; then
  echo "删除旧镜像..."
  docker rmi ${IMAGE_NAME} || true
fi

# 构建新镜像
echo "构建新镜像..."
docker build -t ${IMAGE_NAME} .

# 运行新容器
echo "启动新容器..."
docker run -d \
  --name ${CONTAINER_NAME} \
  -p 9870:9870 \
  -e API_BASE_URL=${API_URL} \
  ${IMAGE_NAME}

# 检查容器状态
echo "检查容器状态..."
docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo "容器已启动，API基础URL设置为: ${API_URL}"
