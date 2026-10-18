"""Jev(TypeSafe)로 이슈를 담당 AI에게 배정한다.

확신도가 JEV_MIN_CONFIDENCE 미만이면 사람에게 넘긴다(needs-human).
API: https://docs.typesafe.ai/api.md
"""
import os

from common import add_labels, comment, gh, http_json, require_secret, set_output

AGENTS = {
    "claude": "핵심 기능 구현, 여러 파일에 걸친 코드 변경, 리팩터링",
    "codex": "테스트 작성, 버그 수정, 작고 명확한 코드 변경",
    "gemini": "문서 작성·정리, 리서치, 조사 결과 요약 (코드 변경 없음)",
    "muse": "저장소 전체 분석, 구조 리뷰, 대량의 코드를 읽어야 하는 검토 (코드 변경 없음)",
}

key = require_secret("TYPESAFE_API_KEY")
number = os.environ["ISSUE_NUMBER"]
threshold = float(os.environ.get("JEV_MIN_CONFIDENCE") or 0.6)

issue = gh(f"/issues/{number}")
result = http_json(
    "https://api.typesafe.ai/v1/systemone",
    {
        "model": "jev-latest",
        "state": {"title": issue["title"], "body": issue.get("body") or ""},
        "questions": {
            "agent": {
                "type": "choice",
                "instructions": "이 작업을 가장 잘 처리할 담당자는 누구인가?",
                "criteria": AGENTS,
            },
            "risky": {
                "type": "noul",
                "instructions": "이 작업이 배포, 비밀키, 데이터 삭제, 권한 변경처럼 되돌리기 어려운 일을 포함하는가?",
            },
        },
    },
    {"Authorization": f"Bearer {key}"},
)

answer = result["answers"]["agent"]
risky = result["answers"]["risky"]["noul"]
agent, confidence = answer["choice"], answer["confidence"]
probs = " / ".join(f"{k} {v:.2f}" for k, v in sorted(answer["probabilities"].items(), key=lambda kv: -kv[1]))

if confidence < threshold or risky >= 0.5:
    reason = f"확신도 {confidence:.2f} < {threshold}" if confidence < threshold else f"위험 작업 확률 {risky:.2f}"
    add_labels(number, ["needs-human"])
    comment(number, f"🧭 **Jev 배정 보류** — {reason}\n\n후보: {probs}\n\n사람이 `agent:<이름>` 라벨을 직접 붙여주세요.")
    set_output("agent", "human")
else:
    add_labels(number, [f"agent:{agent}"])
    comment(number, f"🧭 **Jev 배정 → `{agent}`** (확신도 {confidence:.2f})\n\n후보: {probs}")
    set_output("agent", agent)
