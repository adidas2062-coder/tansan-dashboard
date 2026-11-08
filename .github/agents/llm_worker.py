"""Gemini·Muse 작업자. 코드는 바꾸지 않고 결과를 댓글로 남긴다.

PROVIDER=gemini|muse, MODE=issue(이슈 처리)|review(PR 리뷰)
"""
import os
import subprocess

from common import comment, gh, gh_text, http_json, require_secret, truncate

PROVIDER = os.environ["PROVIDER"]
MODE = os.environ["MODE"]
NUMBER = os.environ["NUMBER"]

ROLE = {
    "gemini": "너는 문서 작성과 리서치 담당이다. 근거를 밝히고, 확인이 안 된 내용은 그렇다고 적어라.",
    "muse": "너는 저장소 전체 분석과 코드 리뷰 담당이다. 문제는 파일:줄 단위로 구체적으로 지적하라.",
}[PROVIDER]


def ask_gemini(prompt):
    key = require_secret("GEMINI_API_KEY")
    model = os.environ.get("GEMINI_MODEL") or "gemini-pro-latest"
    res = http_json(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        {"contents": [{"parts": [{"text": prompt}]}]},
        {"x-goog-api-key": key},
    )
    return "".join(p.get("text", "") for p in res["candidates"][0]["content"]["parts"])


def ask_muse(prompt):
    # Meta Model API는 OpenAI 호환 — https://dev.meta.ai/ai/resources/blog/build-with-muse-spark/
    key = require_secret("META_API_KEY")
    model = os.environ.get("MUSE_MODEL") or "muse-spark-1.3"
    res = http_json(
        "https://api.meta.ai/v1/responses",
        {"model": model, "input": prompt},
        {"Authorization": f"Bearer {key}"},
    )
    if res.get("output_text"):
        return res["output_text"]
    return "".join(
        c.get("text", "")
        for item in res.get("output", [])
        if item.get("type") == "message"
        for c in item.get("content", [])
    )


def repo_context():
    files = subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout
    rules = open("AGENTS.md").read() if os.path.exists("AGENTS.md") else ""
    return f"## 팀 규칙 (AGENTS.md)\n{rules}\n\n## 저장소 파일 목록\n{files}"


if MODE == "issue":
    issue = gh(f"/issues/{NUMBER}")
    task = f"## 작업 (이슈 #{NUMBER})\n제목: {issue['title']}\n\n{issue.get('body') or ''}"
    instruction = "위 작업을 수행하고 결과를 한국어 마크다운으로 작성하라."
else:
    pr = gh(f"/pulls/{NUMBER}")
    diff = gh_text(f"/pulls/{NUMBER}", "application/vnd.github.diff")
    task = f"## 리뷰할 PR #{NUMBER}\n제목: {pr['title']}\n\n{pr.get('body') or ''}\n\n```diff\n{truncate(diff, 400_000)}\n```"
    instruction = "이 PR을 리뷰하라. 머지 전에 꼭 고쳐야 할 것과 선택 사항을 나눠 한국어로 적어라. 문제가 없으면 없다고 짧게 적어라."

prompt = f"{ROLE}\n\n{repo_context()}\n\n{task}\n\n{instruction}"
answer = (ask_gemini if PROVIDER == "gemini" else ask_muse)(prompt).strip()
icon = {"gemini": "✨ Gemini", "muse": "🎨 Muse"}[PROVIDER]
comment(NUMBER, f"### {icon} {'결과' if MODE == 'issue' else '리뷰'}\n\n{truncate(answer, 60_000)}")
