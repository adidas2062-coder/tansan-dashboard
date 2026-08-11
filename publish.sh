#!/bin/bash
# 대시보드를 GitHub Pages로 배포한다.
# tansan-monitor가 생성한 docs/dashboard.html을 index.html로 복사 후 커밋·푸시.
# 내용이 바뀌지 않았으면 아무것도 하지 않는다.
set -e

SRC="/Users/jeonjuwon/tansan-monitor/docs/dashboard.html"
REPO="/Users/jeonjuwon/tansan-dashboard"

[ -f "$SRC" ] || { echo "대시보드 파일 없음: $SRC"; exit 1; }

cd "$REPO"
cp "$SRC" index.html

if git diff --quiet index.html; then
    echo "변경 없음 — 배포 생략"
    exit 0
fi

git add index.html
git -c user.name="jeonjuwon" -c user.email="adidas2062@gmail.com" \
    commit -q -m "대시보드 갱신 $(date '+%Y-%m-%d %H:%M')"
git push -q origin main

echo "배포 완료: https://adidas2062-coder.github.io/tansan-dashboard/"
