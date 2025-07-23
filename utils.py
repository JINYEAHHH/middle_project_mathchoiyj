import time
import os
import random
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import csv
from datetime import datetime

# 📁 카드 이미지 경로
CARD_DIR = "set_cards"

# ✅ 한글 폰트 설정 (NanumGothic)
font_path = os.path.join("fonts", "NanumGothic-Regular.ttf")
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False

# ✅ 속성 매핑
shading_map = {"0": "색칠", "1": "줄무늬", "2": "빈 것"}
shape_map = {"0": "물결", "1": "마름모", "2": "타원"}
color_map = {"0": "빨강", "1": "보라", "2": "초록"}
number_map = {"0": "1개", "1": "2개", "2": "3개"}
columns = ["색깔", "모양", "명암", "개수"]
choices = ["전부 같음", "2개만 같음", "전부 다름"]

# ✅ 카드 정보 해독
def decode(cardname):
    return {
        "명암": shading_map[cardname[0]],
        "모양": shape_map[cardname[1]],
        "색깔": color_map[cardname[2]],
        "개수": number_map[cardname[3]],
    }

# ✅ 카드 로딩
def load_random_cards(n=12):
    files = [f for f in os.listdir(CARD_DIR) if f.endswith(".png")]
    return random.sample(files, n)

# ✅ 카드 출력
def display_card(filename):
    st.image(os.path.join(CARD_DIR, filename), width=120)
    meta = decode(filename)
    st.markdown(f"**{meta['개수']} {meta['색깔']} {meta['명암']} {meta['모양']}**")

# ✅ 선택지 테이블
def show_select_table(key_prefix):
    st.markdown('<style>div[data-testid="column"] { padding: 0.5rem; }</style>', unsafe_allow_html=True)
    cols = st.columns(len(columns))
    selections = []
    for i, col in enumerate(cols):
        with col:
            val = st.selectbox(columns[i], [""] + choices, key=f"{key_prefix}_{i}")
            selections.append(val)
    return selections

# ✅ 예제 정답 확인
def check_answer(user_selections, correct, is_set, idx):
    if all(user_selections[i] == correct[i] for i in range(4)):
        msg = f"✅ 맞았어요! 예제 {idx}은 SET{'입니다' if is_set else '이 아닙니다'}."
        st.success(msg)

# ✅ 카드 이름 → 속성값 리스트로 변환
def parse_card_name(filename):
    return [int(c) for c in filename[:4]]

# ✅ 세 카드가 SET인지 판별
def is_set(card1, card2, card3):
    attrs = zip(parse_card_name(card1), parse_card_name(card2), parse_card_name(card3))
    return all((a + b + c) % 3 == 0 for a, b, c in attrs)

# ✅ 게임 기록 저장 함수 (점수 = 힌트 없이 SET 맞춘 수 − 실패 수)
def save_stats_summary(success_records, fail_records, duration_sec, file_path="game_records.csv"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 힌트 여부 분리
    no_hint_times = [record[1] for record in success_records if record[2] == ""]
    hint_times = [record[1] for record in success_records if record[2] == "힌트 사용"]

    def avg_seconds(times):
        if not times:
            return 0
        return round(sum([_str_to_seconds(t) for t in times]) / len(times), 2)

    def _str_to_seconds(time_str):
        h, m, s = map(int, time_str.split(":"))
        return h * 3600 + m * 60 + s

    no_hint_success = len(no_hint_times)
    hint_success = len(hint_times)
    total_success = no_hint_success + hint_success
    total_fail = len(fail_records)

    avg_no_hint_time = avg_seconds(no_hint_times)
    avg_fail_time = avg_seconds([f[1] for f in fail_records])

    # ✅ 점수 계산 변경: 힌트 없이 맞춘 SET - 실패 수
    score = no_hint_success - total_fail

    # 저장
    with open(file_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            now,
            no_hint_success,
            avg_no_hint_time,
            hint_success,
            total_success,
            total_fail,
            avg_fail_time,
            score,
            duration_sec
        ])
