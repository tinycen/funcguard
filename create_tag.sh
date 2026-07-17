#!/bin/bash
# bash create_tag.sh

PROJECT_DIR="funcguard"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VERSION="$(cat "$SCRIPT_DIR/$PROJECT_DIR/.version")"
TAG_NAME="v${VERSION}"

echo "Version from $PROJECT_DIR/.version: $VERSION"
echo "Tag to create: $TAG_NAME"

# 显示 创建前 3个本地标签
echo "Before create tag , Latest 3 local tags:"
git tag -l | sort -V | tail -n 3

# 显示 创建前 3个远程标签
echo "Before create tag , Latest 3 remote tags:"
git ls-remote --tags origin | awk '{print $2}' | sed 's/refs\/tags\///' | sort -V | tail -n 3

# 创建本地标签
git tag $TAG_NAME
# 推送标签到远程仓库
git push origin $TAG_NAME

# 显示 创建后 3个本地标签
echo "After create tag , Latest 3 local tags:"
git tag -l | sort -V | tail -n 3

# 显示 创建后 3个远程标签
echo "After create tag , Latest 3 remote tags:"
git ls-remote --tags origin | awk '{print $2}' | sed 's/refs\/tags\///' | sort -V | tail -n 3