# AI 팀 규칙

이 저장소에서 일하는 모든 AI(Dots, Codex, Claude, Gemini, Muse, Jev)가 따르는 규칙.

## 역할

| 담당 | 역할 | 결과물 |
|---|---|---|
| Codex Dots | 지휘자. Slack에서 지시를 받아 작업을 쪼개고 GitHub 이슈로 배정, 진행 상황 보고 | 이슈, Slack 보고 |
| Jev | 배정 판단(`task` 라벨 이슈), PR 머지 안전 판정 | 라벨, 댓글 |
| Claude | 핵심 기능 구현, 여러 파일에 걸친 변경 | PR |
| Codex | 테스트, 버그 수정, 작고 명확한 변경 | PR |
| Gemini | 문서, 리서치 | 이슈 댓글 |
| Muse | 저장소 전체 분석, 모든 PR 리뷰 | 댓글 |

## 작업 규칙

- 이슈 하나 = 작업 하나 = 담당 하나. 브랜치는 `agent/<담당>-issue-<번호>`.
- `main`에 직접 푸시하지 않는다. 항상 draft PR로 올리고 본문에 `Closes #<번호>`를 적는다.
- 이슈에 적힌 범위 밖의 파일은 건드리지 않는다.
- `index.html`은 `tansan-monitor`가 매일 생성해 덮어쓴다. 여기서 직접 고치면 다음 배포 때 사라지므로 수정 금지.
- 비밀키·토큰을 코드, 커밋, 댓글에 쓰지 않는다.

## 라벨

- `task` — Jev가 담당을 골라 자동 실행
- `agent:claude` / `agent:codex` / `agent:gemini` / `agent:muse` — 담당 직접 지정
- `needs-human` — Jev 확신도 부족 또는 위험 작업. 사람이 결정
- `jev:pass` / `jev:needs-review` — PR 머지 판정 결과
