from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
WAR_ROOM = ROOT / "services" / "control-plane-web" / "war-room"


def test_war_room_surface_contains_required_track_d_controls() -> None:
    html = (WAR_ROOM / "index.html").read_text(encoding="utf-8")
    script = (WAR_ROOM / "war-room.js").read_text(encoding="utf-8")

    for label in (
        "ผู้เข้าร่วม",
        "ห้องสนทนาสด",
        "วาระ",
        "ข้อค้นพบ",
        "คำตัดสิน",
        "การใช้งาน",
    ):
        assert label in html

    for command in (
        "START",
        "PAUSE",
        "RESUME",
        "STOP",
        "ASK_ROLE",
        "ASK_ALL",
        "SUBMIT_OWNER_DECISION",
        "BEGIN_SUMMARY",
    ):
        assert f'data-command="{command}"' in html

    assert "/snapshot" in script
    assert "/events" in script
    assert "/commands" in script
    assert "new EventSource" in script
    assert "after_sequence" in script


def test_war_room_browser_does_not_own_runtime_authority() -> None:
    script = (WAR_ROOM / "war-room.js").read_text(encoding="utf-8")
    readme = (WAR_ROOM / "README.md").read_text(encoding="utf-8")

    forbidden_runtime_terms = (
        "run_next_turn",
        "OpenRouter",
        "model_policy_ref",
        "authorize_turn",
        "record_usage",
        "pg_advisory",
    )
    for term in forbidden_runtime_terms:
        assert term not in script

    assert "same-origin" in script
    assert "server-established" in readme
    assert "does **not** schedule agents" in readme


def test_war_room_surface_has_no_package_dependency_manifest() -> None:
    assert not (WAR_ROOM / "package.json").exists()
