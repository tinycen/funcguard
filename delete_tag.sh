#!/bin/bash

# bash delete_tag.sh

# 定义要删除的标签
TAG_NAME="v0.1.0"

# 删除本地标签
git tag -d $TAG_NAME
# 删除远程标签
git push origin :refs/tags/$TAG_NAME

# 显示最新的3个本地标签
echo "Latest 3 local tags:"
git tag -l | sort -V | tail -n 3

# 显示最新的3个远程标签
echo "Latest 3 remote tags:"
git ls-remote --tags origin | awk '{print $2}' | sed 's/refs\/tags\///' | sort -V | tail -n 3
