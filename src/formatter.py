import datetime


def format_message(
    target_date: datetime.date,
    worldcup: list[dict],
    lck: list[dict],
    lol_intl: list[dict],
    is_preview: bool = False,
) -> str | None:
    """
    組合三個賽事的場次成 Discord 訊息。
    若三個賽事當天均無場次，回傳 None（不推送）。
    """
    if not worldcup and not lck and not lol_intl:
        return None

    label = "明日賽程預告" if is_preview else "今日賽程"
    date_str = target_date.strftime("%Y-%m-%d")
    lines = [f"📅 【{label}】{date_str}", ""]

    def render_section(emoji: str, title: str, matches: list[dict]) -> list[str]:
        out = [f"{emoji} {title}"]
        if not matches:
            out.append("  （今日無場次）")
        else:
            for m in matches:
                note = f"（{m['note']}）" if m.get("note") else ""
                out.append(f"  🕐 {m['time']}  {m['team1']} vs {m['team2']} {note}".rstrip())
        return out

    lines += render_section("⚽", "世界盃", worldcup)
    lines.append("")
    lines += render_section("🎮", "LCK", lck)
    lines.append("")
    lines += render_section("🌍", "LOL 國際賽", lol_intl)

    return "\n".join(lines)
