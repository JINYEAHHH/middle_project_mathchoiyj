import streamlit as st
import sys
import os
import random
import time
from datetime import timedelta
from itertools import combinations

# ✅ utils.py에서 기록 저장 함수 불러오기
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import save_stats_summary

# 카드 이미지 폴더 경로
CARD_DIR = "set_cards"
ALL_CARDS = sorted([f for f in os.listdir(CARD_DIR) if f.endswith(".png")])

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
    st.session_state.set_success = []
    st.session_state.set_fail = []
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

# 카드 선택
def toggle_card(idx):
    if idx in st.session_state.selected:
        st.session_state.selected.remove(idx)
    elif len(st.session_state.selected) < 3:
        st.session_state.selected.append(idx)

# 힌트 보기
if st.button("💡 힌트 보기"):
    for combo in combinations(st.session_state.cards, 3):
        if is_set(combo):
            hint_cards = random.sample(combo, 2)
            st.session_state.selected = [st.session_state.cards.index(c) for c in hint_cards]
            st.session_state.hint_mode = True
            st.rerun()
    st.warning("현재 보드에는 SET이 없습니다.")

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

# SET 판별 로직
if len(st.session_state.selected) == 3:
    selected_cards = [st.session_state.cards[i] for i in st.session_state.selected]
    elapsed = int(time.time() - st.session_state.start_time)
    if is_set(selected_cards):
        st.success("🎉 SET 성공!")
        note = "힌트 사용" if st.session_state.hint_mode else ""
        st.session_state.set_success.append(
            (len(st.session_state.set_success)+1, str(timedelta(seconds=elapsed)), note)
        )

        selected_indices = sorted(st.session_state.selected)
        card_count_before = len(st.session_state.cards)

        if card_count_before == 12 and len(st.session_state.remaining) >= 3:
            # 12장 → SET 성공 → 3장 제거 + 새 3장 추가 → 12장 유지
            new_cards = random.sample(st.session_state.remaining, 3)
            for i, card_idx in enumerate(selected_indices):
                st.session_state.cards[card_idx] = new_cards[i]
                st.session_state.remaining.remove(new_cards[i])
        else:
            # 15장 → SET 성공 → 3장 제거만 → 12장 유지
            for card_idx in reversed(selected_indices):
                st.session_state.cards.pop(card_idx)

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

# SET이 없으면 3장 추가 (단, 12장일 때만)
if not any_set_exists(st.session_state.cards):
    if len(st.session_state.cards) == 12 and len(st.session_state.remaining) >= 3:
        st.warning("⚠️ SET이 없어 3장을 추가합니다!")
        new_cards = random.sample(st.session_state.remaining, 3)
        st.session_state.cards.extend(new_cards)
        for c in new_cards:
            st.session_state.remaining.remove(c)
        st.rerun()

# 게임 종료
if st.button("🛑 게임 종료"):
    duration = int(time.time() - st.session_state.start_time)
    save_stats_summary(
        st.session_state.set_success,
        st.session_state.set_fail,
        duration
    )
    st.success("✅ 게임이 종료되었고 결과가 game_records.csv에 저장되었습니다.")
    st.session_state.game_started = False
    st.session_state.cards = []
    st.session_state.remaining = ALL_CARDS.copy()
    st.session_state.selected = []
    st.session_state.set_success = []
    st.session_state.set_fail = []
    st.session_state.start_time = 0
    st.session_state.hint_mode = False
    st.stop()

# 기록 테이블
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
