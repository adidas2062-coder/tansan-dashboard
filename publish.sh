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

# 크론 환경에는 TTY·키체인이 없으므로 SSH 키로 인증한다.
# 푸시가 실패해도 커밋은 남으므로 다음 실행에서 함께 올라간다.
if git push -q origin main 2>&1; then
    echo "[$(date '+%Y-%m-%d %H:%M')] 배포 완료: https://adidas2062-coder.github.io/tansan-dashboard/"
else
    echo "[$(date '+%Y-%m-%d %H:%M')] 푸시 실패 — 커밋은 로컬에 보관됨. SSH 키 등록 상태를 확인하세요."
    exit 1
fi
