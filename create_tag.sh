#!/bin/bash
# bash create_tag.sh

# 定义要创建的标签
TAG_NAME="v0.2.4"
# 请注意，需要同步修改 setup.py 中的 version，否则无法同步到Pypi

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