import os
import random
import streamlit as st

# 카드 이미지 경로
CARD_DIR = "set_cards"

# 속성 정의
shading_map = {"0": "색칠", "1": "줄무늬", "2": "빈 것"}
shape_map = {"0": "물결", "1": "마름모", "2": "타원"}
color_map = {"0": "빨강", "1": "보라", "2": "초록"}
number_map = {"0": "1개", "1": "2개", "2": "3개"}

columns = ["색깔", "모양", "명암", "개수"]
choices = ["전부 같음", "2개만 같음", "전부 다름"]

def decode(cardname):
    return {
        "명암": shading_map[cardname[0]],
        "모양": shape_map[cardname[1]],
        "색깔": color_map[cardname[2]],
        "개수": number_map[cardname[3]],
    }

def load_random_cards(n=12):
    files = [f for f in os.listdir(CARD_DIR) if f.endswith(".png")]
    return random.sample(files, n)

def display_card(filename):
    st.image(os.path.join(CARD_DIR, filename), width=120)
    meta = decode(filename)
    st.markdown(f"**{meta['개수']} {meta['색깔']} {meta['명암']} {meta['모양']}**")

def show_select_table(key_prefix):
    st.markdown('<style>div[data-testid="column"] { padding: 0.5rem; }</style>', unsafe_allow_html=True)
    cols = st.columns(len(columns))
    selections = []
    for i, col in enumerate(cols):
        with col:
            val = st.selectbox(columns[i], [""] + choices, key=f"{key_prefix}_{i}")
            selections.append(val)
    return selections

def check_answer(user_selections, correct, is_set, idx):
    if all(user_selections[i] == correct[i] for i in range(4)):
        msg = f"✅ 맞았어요! 예제 {idx}은 SET{'입니다' if is_set else '이 아닙니다'}."
        st.success(msg)


# utils.py

def parse_card_name(filename):
    return [int(c) for c in filename[:4]]

def is_set(card1, card2, card3):
    attrs = zip(parse_card_name(card1), parse_card_name(card2), parse_card_name(card3))
    return all((a + b + c) % 3 == 0 for a, b, c in attrs)




import streamlit as st
import os
import random
import time
import csv
from datetime import timedelta, datetime
from itertools import combinations
import pandas as pd
import matplotlib.pyplot as plt

# 카드 이미지 폴더 경로
CARD_DIR = "set_cards"
ALL_CARDS = sorted([f for f in os.listdir(CARD_DIR) if f.endswith(".png")])
RECORDS_CSV = "game_records.csv"

# SET 판별 함수
def get_card_attributes(filename):
    return [int(ch) for ch in filename[:4]]

def is_set(cards):
    attrs = [get_card_attributes(c) for c in cards]
    for i in range(4):
        values = {attr[i] for attr in attrs}
        if len(values) == 2:
            return False
    return True

def any_set_exists(card_list):
    for a, b, c in combinations(card_list, 3):
        if is_set([a, b, c]):
            return True
    return False

def time_str_to_seconds(tstr):
    h, m, s = map(int, tstr.split(":"))
    return h * 3600 + m * 60 + s

def seconds_to_time_str(seconds):
    return str(timedelta(seconds=int(seconds)))

def save_stats_summary():
    hint_used = [s for s in st.session_state.set_success if s[2] == "힌트 사용"]
    no_hint = [s for s in st.session_state.set_success if s[2] != "힌트 사용"]
    no_hint_times = [time_str_to_seconds(s[1]) for s in no_hint]
    fail_times = [time_str_to_seconds(f[1]) for f in st.session_state.set_fail]
    play_time = int(time.time() - st.session_state.start_time)

    stats = {
        "날짜": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "힌트 없이 SET 맞춘 횟수": len(no_hint),
        "힌트 없이 SET 맞춘 시간 평균": seconds_to_time_str(sum(no_hint_times) / len(no_hint_times)) if no_hint_times else "00:00:00",
        "힌트 써서 맞춘 SET 개수": len(hint_used),
        "총 맞춘 SET 개수": len(st.session_state.set_success),
        "SET 틀린 횟수": len(st.session_state.set_fail),
        "SET 틀린 시간 평균": seconds_to_time_str(sum(fail_times) / len(fail_times)) if fail_times else "00:00:00",
        "총점": len(no_hint) - len(st.session_state.set_fail),
        "총 플레이 시간": seconds_to_time_str(play_time)
    }

    # 현재 세션 저장
    st.session_state.stats_summary = stats

    # CSV 저장
    file_exists = os.path.isfile(RECORDS_CSV)
    with open(RECORDS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=stats.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(stats)

# 결과 시각화 함수 (3_Records.py 용)
def plot_game_stats():
    if not os.path.exists(RECORDS_CSV):
        st.warning("저장된 게임 기록이 없습니다.")
        return

    df = pd.read_csv(RECORDS_CSV)

    # 시간 문자열을 초 단위로 변환
    df["총 플레이 시간(초)"] = df["총 플레이 시간"].apply(time_str_to_seconds)
    df["힌트 없이 SET 맞춘 시간 평균(초)"] = df["힌트 없이 SET 맞춘 시간 평균"].apply(time_str_to_seconds)
    df["SET 틀린 시간 평균(초)"] = df["SET 틀린 시간 평균"].apply(time_str_to_seconds)

    st.subheader("📈 누적 통계 시각화")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**SET 성공/실패 횟수**")
        plt.figure(figsize=(4,2))
        plt.plot(df["날짜"], df["총 맞춘 SET 개수"], label="성공")
        plt.plot(df["날짜"], df["SET 틀린 횟수"], label="실패")
        plt.xticks(rotation=45)
        plt.legend()
        st.pyplot(plt.gcf())

    with col2:
        st.markdown("**플레이 시간 및 점수 변화**")
        plt.figure(figsize=(4,2))
        plt.plot(df["날짜"], df["총점"], label="총점")
        plt.plot(df["날짜"], df["총 플레이 시간(초)"], label="플레이 시간")
        plt.xticks(rotation=45)
        plt.legend()
        st.pyplot(plt.gcf())

    # 평균 통계
    st.subheader("📊 평균 통계 요약")
    avg_score = df["총점"].mean()
    avg_success_rate = (df["힌트 없이 SET 맞춘 횟수"].sum() / df["총 맞춘 SET 개수"].sum()) * 100 if df["총 맞춘 SET 개수"].sum() else 0
    avg_hint_rate = (df["힌트 써서 맞춘 SET 개수"].sum() / df["총 맞춘 SET 개수"].sum()) * 100 if df["총 맞춘 SET 개수"].sum() else 0

    st.markdown(f"**총 평균 점수:** {avg_score:.2f}")
    st.markdown(f"**힌트 없이 성공률:** {avg_success_rate:.2f}%")
    st.markdown(f"**힌트 사용률:** {avg_hint_rate:.2f}%")




import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import timedelta

def time_str_to_seconds(tstr):
    h, m, s = map(int, tstr.split(":"))
    return h * 3600 + m * 60 + s

def plot_game_stats():
    if not os.path.exists("game_records.csv"):
        st.warning("저장된 게임 기록이 없습니다.")
        return

    df = pd.read_csv("game_records.csv")

    df["총 플레이 시간(초)"] = df["총 플레이 시간"].apply(time_str_to_seconds)
    df["힌트 없이 SET 맞춘 시간 평균(초)"] = df["힌트 없이 SET 맞춘 시간 평균"].apply(time_str_to_seconds)
    df["SET 틀린 시간 평균(초)"] = df["SET 틀린 시간 평균"].apply(time_str_to_seconds)

    st.subheader("📈 누적 통계 시각화")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**SET 성공/실패 횟수**")
        plt.figure(figsize=(4, 2))
        plt.plot(df["날짜"], df["총 맞춘 SET 개수"], label="성공")
        plt.plot(df["날짜"], df["SET 틀린 횟수"], label="실패")
        plt.xticks(rotation=45)
        plt.legend()
        st.pyplot(plt.gcf())

    with col2:
        st.markdown("**플레이 시간 및 점수 변화**")
        plt.figure(figsize=(4, 2))
        plt.plot(df["날짜"], df["총점"], label="총점")
        plt.plot(df["날짜"], df["총 플레이 시간(초)"], label="플레이 시간")
        plt.xticks(rotation=45)
        plt.legend()
        st.pyplot(plt.gcf())

    st.subheader("📊 평균 통계 요약")
    avg_score = df["총점"].mean()
    avg_success_rate = (df["힌트 없이 SET 맞춘 횟수"].sum() / df["총 맞춘 SET 개수"].sum()) * 100 if df["총 맞춘 SET 개수"].sum() else 0
    avg_hint_rate = (df["힌트 써서 맞춘 SET 개수"].sum() / df["총 맞춘 SET 개수"].sum()) * 100 if df["총 맞춘 SET 개수"].sum() else 0

    st.markdown(f"**총 평균 점수:** {avg_score:.2f}")
    st.markdown(f"**힌트 없이 성공률:** {avg_success_rate:.2f}%")
    st.markdown(f"**힌트 사용률:** {avg_hint_rate:.2f}%")
