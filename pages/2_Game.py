import streamlit as st
import os
import random
import time
from datetime import timedelta
from itertools import combinations

# 카드 이미지 폴더 경로
CARD_DIR = "set_cards"
ALL_CARDS = sorted([f for f in os.listdir(CARD_DIR) if f.endswith(".png")])

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

# 페이지 설정
st.set_page_config(page_title="SET 게임", layout="wide")
col1, col2 = st.columns([8, 2])
with col1:
    st.markdown("## 🎮 SET 보드게임")
with col2:
    if st.session_state.get("game_started", False):
        elapsed = int(time.time() - st.session_state.start_time)
        st.markdown(f"**🕒 경과 시간:** {str(timedelta(seconds=elapsed))}")
    else:
        st.markdown("**🕒 경과 시간:** 00:00:00")

st.markdown("---")

# 세션 상태 초기화
if "game_started" not in st.session_state:
    st.session_state.game_started = False
    st.session_state.cards = []
    st.session_state.remaining = ALL_CARDS.copy()
    st.session_state.selected = []
    st.session_state.set_success = []  # (번호, 시간, 특이사항)
    st.session_state.set_fail = []     # (번호, 시간)
    st.session_state.start_time = 0
    st.session_state.hint_mode = False

# 게임 시작
if not st.session_state.game_started:
    if st.button("🎲 게임 시작하기"):
        st.session_state.game_started = True
        st.session_state.start_time = time.time()
        st.session_state.remaining = ALL_CARDS.copy()
        st.session_state.cards = random.sample(st.session_state.remaining, 12)
        for c in st.session_state.cards:
            st.session_state.remaining.remove(c)
        st.rerun()
    else:
        st.stop()

# 선택 핸들러
def toggle_card(idx):
    if idx in st.session_state.selected:
        st.session_state.selected.remove(idx)
    elif len(st.session_state.selected) < 3:
        st.session_state.selected.append(idx)

# 힌트 보기 버튼
if st.button("💡 힌트 보기"):
    for combo in combinations(st.session_state.cards, 3):
        if is_set(combo):
            hint_cards = random.sample(combo, 2)
            st.session_state.selected = [st.session_state.cards.index(c) for c in hint_cards]
            st.session_state.hint_mode = True
            st.rerun()

# 카드 표시
cols = st.columns(4)
for idx, card_file in enumerate(st.session_state.cards):
    col = cols[idx % 4]
    card_path = os.path.join(CARD_DIR, card_file)
    with col:
        st.image(card_path, width=160)
        ui_cols = st.columns([1, 5])
        if ui_cols[0].button("●", key=f"btn_{idx}"):
            toggle_card(idx)
            st.rerun()
        if idx in st.session_state.selected:
            ui_cols[1].markdown("선택됨")

# SET 판별
if len(st.session_state.selected) == 3:
    selected_cards = [st.session_state.cards[i] for i in st.session_state.selected]
    elapsed = int(time.time() - st.session_state.start_time)
    if is_set(selected_cards):
        st.success("🎉 SET 성공!")
        note = "힌트 사용" if st.session_state.hint_mode else ""
        st.session_state.set_success.append(
            (len(st.session_state.set_success)+1, str(timedelta(seconds=elapsed)), note)
        )
        for i in sorted(st.session_state.selected, reverse=True):
            st.session_state.cards.pop(i)
        if len(st.session_state.cards) <= 12 and len(st.session_state.remaining) >= 3:
            new_cards = random.sample(st.session_state.remaining, 3)
            st.session_state.cards.extend(new_cards)
            for c in new_cards:
                st.session_state.remaining.remove(c)
        st.session_state.selected.clear()
        st.session_state.hint_mode = False
        st.rerun()
    else:
        st.error("❌ SET 실패!")
        st.session_state.set_fail.append(
            (len(st.session_state.set_fail)+1, str(timedelta(seconds=elapsed)))
        )
        st.session_state.selected.clear()
        st.session_state.hint_mode = False
        st.rerun()

# SET 없음 → 카드 추가
if not any_set_exists(st.session_state.cards):
    if len(st.session_state.cards) == 12 and len(st.session_state.remaining) >= 3:
        st.warning("⚠️ SET이 만들어지지 않으니 3장을 추가하겠습니다!")
        new_cards = random.sample(st.session_state.remaining, 3)
        st.session_state.cards.extend(new_cards)
        for c in new_cards:
            st.session_state.remaining.remove(c)
        st.rerun()

# 종료 조건 검사
if not st.session_state.remaining:
    board = st.session_state.cards.copy()
    while len(board) >= 3:
        if any_set_exists(board):
            break
        board = board[:-3]
    else:
        st.markdown("## 🏁 게임 종료!")
        st.stop()

# 게임 종료 버튼
if st.button("🛑 게임 종료"):
    st.session_state.game_started = False

    # 결과 저장
    with open("records.py", "w", encoding="utf-8") as f:
        f.write("set_success_records = [\n")
        for s in st.session_state.set_success:
            f.write(f"    {s},\n")
        f.write("]\n\n")
        f.write("set_fail_records = [\n")
        for f_ in st.session_state.set_fail:
            f.write(f"    {f_},\n")
        f.write("]\n")

    st.success("✅ 게임이 종료되었고 결과가 Records에 저장되었습니다.")
    st.stop()

# 결과 테이블
col1, col2 = st.columns(2)
with col1:
    st.markdown("### ✅ SET 성공 기록")
    if st.session_state.set_success:
        st.table(
            {
                "번호": [s[0] for s in st.session_state.set_success],
                "시간": [s[1] for s in st.session_state.set_success],
                "특이사항": [s[2] for s in st.session_state.set_success],
            }
        )
with col2:
    st.markdown("### ❌ SET 실패 기록")
    if st.session_state.set_fail:
        st.table(
            {
                "번호": [f[0] for f in st.session_state.set_fail],
                "시간": [f[1] for f in st.session_state.set_fail],
            }
        )
