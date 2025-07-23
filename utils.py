import os
import random
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
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

# ✅ SET 판단

def parse_card_name(filename):
    return [int(c) for c in filename[:4]]

def is_set(card1, card2, card3):
    attrs = zip(parse_card_name(card1), parse_card_name(card2), parse_card_name(card3))
    return all((a + b + c) % 3 == 0 for a, b, c in attrs)

# ✅ 누적 기록 테이블 시각화

def plot_game_stats():
    if not os.path.exists("records.py"):
        st.warning("기록 파일이 아직 없습니다.")
        return

    import importlib.util
    spec = importlib.util.spec_from_file_location("records", "records.py")
    records = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(records)

    success_data = records.set_success_records
    fail_data = records.set_fail_records

    game_records = []
    current_game = []
    current_hint_used = 0

    for record in success_data:
        if record[0] == 1 and current_game:
            game_records.append(current_game)
            current_game = []
            current_hint_used = 0
        current_game.append(record)
    if current_game:
        game_records.append(current_game)

    df_list = []
    for idx, game in enumerate(game_records):
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 예시로 현재 시간
        total = len(game)
        hint_used = sum(1 for r in game if r[2] == "힌트 사용")
        no_hint = total - hint_used
        total_time = sum(pd.to_timedelta(r[1]).total_seconds() for r in game)
        avg_time = total_time / total if total else 0

        fail_this_game = [f for f in fail_data if f[0] <= total]  # fail 번호 기준 추정
        fail_time = sum(pd.to_timedelta(f[1]).total_seconds() for f in fail_this_game)
        avg_fail_time = fail_time / len(fail_this_game) if fail_this_game else 0

        df_list.append({
            "날짜": date_str,
            "힌트 없이 SET 맞춘 횟수": no_hint,
            "힌트 없이 평균 시간(초)": round(avg_time, 1),
            "힌트 써서 맞춘 SET": hint_used,
            "총 맞춘 SET 개수": total,
            "SET 틀린 횟수": len(fail_this_game),
            "SET 틀린 평균 시간(초)": round(avg_fail_time, 1),
            "총점": no_hint - len(fail_this_game),
            "총 플레이 시간(초)": round(total_time, 1)
        })

    if not df_list:
        st.warning("누적된 게임 기록이 없습니다.")
        return

    df = pd.DataFrame(df_list)
    st.dataframe(df, use_container_width=True)

    # 📈 성공/실패 횟수
    plt.figure(figsize=(5, 3))
    plt.plot(df["날짜"], df["총 맞춘 SET 개수"], label="성공", marker="o")
    plt.plot(df["날짜"], df["SET 틀린 횟수"], label="실패", marker="x")
    plt.title("SET 성공/실패 횟수", fontproperties=font_prop)
    plt.xticks(rotation=45, fontproperties=font_prop)
    plt.yticks(fontproperties=font_prop)
    plt.legend(prop=font_prop)
    st.pyplot(plt.gcf())

    # 📈 총점과 플레이 시간
    plt.figure(figsize=(5, 3))
    plt.plot(df["날짜"], df["총점"], label="총점", marker="s")
    plt.plot(df["날짜"], df["총 플레이 시간(초)"], label="플레이 시간(초)", marker="d")
    plt.title("플레이 시간 및 점수 변화", fontproperties=font_prop)
    plt.xticks(rotation=45, fontproperties=font_prop)
    plt.yticks(fontproperties=font_prop)
    plt.legend(prop=font_prop)
    st.pyplot(plt.gcf())


    import time
from datetime import timedelta

# SET 통계 저장 함수
def save_stats_summary():
    if "set_success" not in st.session_state or "set_fail" not in st.session_state:
        return

    # 총 플레이 시간 계산
    end_time = time.time()
    total_time = int(end_time - st.session_state.start_time)
    formatted_time = str(timedelta(seconds=total_time))

    # 통계 계산
    total_set = len(st.session_state.set_success)
    total_fail = len(st.session_state.set_fail)
    hint_success = sum(1 for s in st.session_state.set_success if s[2] == "힌트 사용")
    no_hint_success = total_set - hint_success
    score = no_hint_success - total_fail

    # 평균 시간 계산
    def to_seconds(tstr):
        try:
            t = list(map(int, tstr.split(":")))
            return t[0]*3600 + t[1]*60 + t[2]
        except:
            return 0

    hint_times = [to_seconds(s[1]) for s in st.session_state.set_success if s[2] == "힌트 사용"]
    no_hint_times = [to_seconds(s[1]) for s in st.session_state.set_success if s[2] == ""]
    fail_times = [to_seconds(f[1]) for f in st.session_state.set_fail]

    avg_hint = str(timedelta(seconds=int(sum(hint_times)/len(hint_times)))) if hint_times else "-"
    avg_no_hint = str(timedelta(seconds=int(sum(no_hint_times)/len(no_hint_times)))) if no_hint_times else "-"
    avg_fail = str(timedelta(seconds=int(sum(fail_times)/len(fail_times)))) if fail_times else "-"

    # 저장할 누적 리스트 초기화
    if "game_history" not in st.session_state:
        st.session_state.game_history = []

    st.session_state.game_history.append({
        "일자": time.strftime("%Y-%m-%d %H:%M:%S"),
        "힌트 없이 성공": no_hint_success,
        "힌트 없이 평균시간(초)": avg_no_hint,
        "힌트 성공": hint_success,
        "총 성공": total_set,
        "실패": total_fail,
        "실패 평균시간(초)": avg_fail,
        "총점": score,
        "플레이 시간": formatted_time,
    })
