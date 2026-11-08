# AI 팀 설정 가이드

Slack에서 Dots에게 한 번 지시하면 Codex·Claude·Gemini·Muse가 나눠서 일하고, Jev가 배정과 검문을 맡는 구조.

```
[Slack] 사용자 ─▶ Codex Dots (지휘자, 상시 실행)
                    │ 작업을 쪼개 GitHub 이슈 생성
                    ├─ `task` 라벨 ─▶ Jev가 담당 선택 (agent-router.yml)
                    └─ `agent:<이름>` 라벨 ─▶ 바로 실행
                                │
   ┌───────────────┬────────────┼──────────────┬──────────────┐
 agent:codex     agent:claude   agent:gemini    agent:muse
 Dots가 Codex    PR 생성        댓글로 결과     댓글로 분석
 클라우드 작업
                                │
                    모든 PR ─▶ Muse 리뷰 + Jev 검문 (agent-pr-review.yml)
                                │
                    Dots가 Slack에 보고, 사람이 머지
```

## 1. 시크릿 등록

저장소 **Settings → Secrets and variables → Actions → Secrets**:

| 이름 | 용도 | 발급 |
|---|---|---|
| `CLAUDE_CODE_OAUTH_TOKEN` | Claude (Pro/Max 구독 사용) | 터미널에서 `claude setup-token` |
| `GEMINI_API_KEY` | Gemini | Google AI Studio |
| `META_API_KEY` | Muse (Meta Model API) | dev.meta.ai |
| `TYPESAFE_API_KEY` | Jev | typesafe.ai |

키가 없는 작업자는 실패하지 않고 건너뛴다. 하나씩 등록해도 된다.

선택 **Variables**: `JEV_MIN_CONFIDENCE`(기본 0.6), `GEMINI_MODEL`(기본 `gemini-pro-latest`), `MUSE_MODEL`(기본 `muse-spark-1.3`).

## 2. Claude GitHub 앱 설치

https://github.com/apps/claude 에서 이 저장소에 설치한다 (`claude-code-action`이 사용).

## 3. Dots 설정

1. ChatGPT에서 Dots를 만들고 Slack과 GitHub(`tansan-dashboard`)를 연결한다.
2. Codex 환경에 이 저장소를 등록한다.
3. 아래 지시문을 Dots에 넣는다.

```text
너는 tansan-dashboard 저장소 AI 팀의 지휘자다. 저장소의 AGENTS.md 규칙을 따른다.

Slack에서 작업 지시를 받으면:
1. 작업을 서로 겹치지 않는 단위로 쪼갠다. 같은 파일을 두 담당이 동시에 고치지 않게 한다.
2. 단위마다 GitHub 이슈를 만든다. 본문에 목표, 범위(건드릴 파일), 완료 조건을 적는다.
3. 담당이 명확하면 `agent:claude` / `agent:gemini` / `agent:muse` 라벨을, 애매하면 `task` 라벨을 붙여 Jev에게 맡긴다.
4. `agent:codex` 작업은 직접 Codex 클라우드 작업으로 만들고, 브랜치 `agent/codex-issue-<번호>`로 PR을 열게 한다.
5. 이슈 댓글, PR, `jev:pass`/`jev:needs-review`/`needs-human` 라벨을 지켜보고 Slack 스레드에 진행 상황을 보고한다.
6. `needs-human`이나 `jev:needs-review`가 붙으면 Slack에서 사람에게 결정을 요청한다.
7. 머지는 하지 않는다. 사람이 한다.
8. 어떤 작업자가 사용량 한도로 실패하면 다른 담당에게 다시 배정한다.
```

## 4. 확인

이슈를 하나 만들고 `task` 라벨을 붙인다 → Actions 탭에서 `agent-router` 실행과 Jev 배정 댓글을 확인한다.

## 알려진 제약

- Claude가 만든 PR은 `GITHUB_TOKEN`으로 생성돼 `pull_request` 이벤트가 안 생긴다. 그래서 `agent-claude.yml`이 리뷰 워크플로를 직접 호출한다.
- Muse는 PR에 커밋이 올라올 때마다 리뷰 댓글을 단다. 시끄러우면 `agent-pr-review.yml`의 `synchronize`를 빼면 된다.
- Muse·Jev API 주소와 모델명은 2026-10 기준 공식 문서에서 확인했다. 바뀌면 Variables로 모델명을 바꾼다.
