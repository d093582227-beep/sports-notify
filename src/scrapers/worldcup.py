import datetime
from ._common import fetch_matches

URL = "https://liquipedia.net/lab/Football/FIFA/World_Cup/2026"

# ISO 3166-1 alpha-3 → 中文隊名（2026 世界盃 48 隊）
_COUNTRY_ZH = {
    # 北中美洲 CONCACAF
    "USA": "美國", "MEX": "墨西哥", "CAN": "加拿大",
    "PAN": "巴拿馬", "HON": "洪都拉斯", "JAM": "牙買加",
    "CRC": "哥斯大黎加", "TRI": "千里達及托巴哥",
    # 南美洲 CONMEBOL
    "BRA": "巴西", "ARG": "阿根廷", "COL": "哥倫比亞",
    "URU": "烏拉圭", "ECU": "厄瓜多", "VEN": "委內瑞拉",
    "CHI": "智利", "PAR": "巴拉圭", "PER": "秘魯",
    "BOL": "玻利維亞",
    # 歐洲 UEFA
    "FRA": "法國", "ENG": "英格蘭", "ESP": "西班牙",
    "GER": "德國", "PRT": "葡萄牙", "NED": "荷蘭",
    "BEL": "比利時", "ITA": "義大利", "HRV": "克羅埃西亞",
    "DEN": "丹麥", "AUT": "奧地利", "SUI": "瑞士",
    "POL": "波蘭", "SRB": "塞爾維亞", "SCO": "蘇格蘭",
    "TUR": "土耳其", "HUN": "匈牙利", "ROU": "羅馬尼亞",
    "CZE": "捷克", "NOR": "挪威", "SVK": "斯洛伐克",
    "GRE": "希臘", "UKR": "烏克蘭", "SWE": "瑞典",
    # 非洲 CAF
    "MAR": "摩洛哥", "NGA": "奈及利亞", "SEN": "塞內加爾",
    "CMR": "喀麥隆", "EGY": "埃及", "CIV": "象牙海岸",
    "GHA": "迦納", "MLI": "馬利", "TUN": "突尼西亞",
    "DZA": "阿爾及利亞",
    # 亞洲 AFC
    "JPN": "日本", "KOR": "韓國", "AUS": "澳洲",
    "IRN": "伊朗", "SAU": "沙烏地阿拉伯", "QAT": "卡達",
    "IRQ": "伊拉克", "JOR": "約旦", "UZB": "烏茲別克",
    "CHN": "中國",
    # 大洋洲 OFC
    "NZL": "紐西蘭",
}


def get_matches(target_date: datetime.date) -> list[dict]:
    matches = fetch_matches(URL, target_date)
    for m in matches:
        m["team1"] = _COUNTRY_ZH.get(m["team1"], m["team1"])
        m["team2"] = _COUNTRY_ZH.get(m["team2"], m["team2"])
    return matches
