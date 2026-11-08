"""Jev(TypeSafe)로 PR이 머지해도 안전한지 판정하고 jev:pass / jev:needs-review 라벨을 붙인다."""
import os

from common import add_labels, comment, gh, gh_text, http_json, remove_label, require_secret, truncate

key = require_secret("TYPESAFE_API_KEY")
number = os.environ["PR_NUMBER"]
threshold = float(os.environ.get("JEV_MIN_CONFIDENCE") or 0.6)

pr = gh(f"/pulls/{number}")
diff = gh_text(f"/pulls/{number}", "application/vnd.github.diff")

result = http_json(
    "https://api.typesafe.ai/v1/systemone",
    {
        "model": "jev-latest",
        "state": {
            "title": pr["title"],
            "description": pr.get("body") or "",
            "diff": truncate(diff, 200_000),
        },
        "questions": {
            "safe": {
                "type": "noul",
                "instructions": "`diff`를 머지해도 안전한가?",
                "criteria": {
                    "true": "변경이 설명과 일치하고, 비밀키 노출·대량 삭제·배포 설정 파손이 없다",
                    "false": "비밀키 노출, 의도치 않은 대량 삭제, 배포 파손, 설명과 무관한 변경 중 하나라도 있다",
                },
            },
            "in_scope": {
                "type": "noul",
                "instructions": "`diff`가 `title`과 `description`에 적힌 작업 범위 안에만 머무는가?",
            },
        },
    },
    {"Authorization": f"Bearer {key}"},
)

safe = result["answers"]["safe"]["noul"]
in_scope = result["answers"]["in_scope"]["noul"]
passed = safe >= threshold and in_scope >= threshold

remove_label(number, "jev:needs-review" if passed else "jev:pass")
add_labels(number, ["jev:pass" if passed else "jev:needs-review"])
comment(
    number,
    f"🛡️ **Jev 검문: {'통과' if passed else '사람 검토 필요'}**\n\n"
    f"- 머지 안전 확률: {safe:.2f}\n- 작업 범위 준수 확률: {in_scope:.2f}\n- 기준: {threshold}",
)
