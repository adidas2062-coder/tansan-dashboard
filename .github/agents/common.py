"""에이전트 워크플로 공용 헬퍼. 표준 라이브러리만 쓴다(설치 단계 없음)."""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

REPO = os.environ.get("GITHUB_REPOSITORY", "")
GH_TOKEN = os.environ.get("GITHUB_TOKEN", "")


def http_json(url, payload=None, headers=None, method=None, timeout=300):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} {url}\n{e.read().decode(errors='replace')[:2000]}")


def gh(path, payload=None, method=None, accept="application/vnd.github+json"):
    return http_json(
        f"https://api.github.com/repos/{REPO}{path}",
        payload,
        {"Authorization": f"Bearer {GH_TOKEN}", "Accept": accept},
        method,
    )


def gh_text(path, accept):
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}{path}")
    req.add_header("Authorization", f"Bearer {GH_TOKEN}")
    req.add_header("Accept", accept)
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read().decode(errors="replace")


def comment(number, body):
    gh(f"/issues/{number}/comments", {"body": body})


def add_labels(number, labels):
    gh(f"/issues/{number}/labels", {"labels": labels})


def remove_label(number, label):
    """라벨이 없어서 나는 404는 무시한다."""
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/issues/{number}/labels/{urllib.parse.quote(label)}",
        method="DELETE",
    )
    req.add_header("Authorization", f"Bearer {GH_TOKEN}")
    try:
        urllib.request.urlopen(req, timeout=60)
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise


def require_secret(name):
    """키가 없으면 실패 대신 건너뛴다. 키 등록 전에도 CI가 빨간불이 되지 않게."""
    value = os.environ.get(name, "")
    if not value:
        print(f"::notice::{name} 미등록 — 이 단계를 건너뜁니다.")
        sys.exit(0)
    return value


def set_output(name, value):
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a") as f:
            f.write(f"{name}={value}\n")


def truncate(text, limit):
    return text if len(text) <= limit else text[:limit] + f"\n...(이하 {len(text) - limit}자 생략)"
