import streamlit as st
import os
import random
import time
from datetime import timedelta

# 카드 폴더 경로
CARD_DIR = "set_cards"
ALL_CARDS = sorted([f for f in os.listdir(CARD_DIR) if f.endswith(".png")])

# 페이지 설정
st.set_page_config(page_title="SET 보드게임", layout="wide")

# 타이틀 & 타이머
col1, col2 = st.columns([8, 2])
with col1:
    st.markdown("## 🎮 SET 보드게임")
with col2:
    if "start_time" in st.session_state:
        elapsed = int(time.time() - st.session_state.start_time)
        st.markdown(f"**🕒 경과 시간:** {str(timedelta(seconds=elapsed))}")
    else:
        st.markdown("**🕒 경과 시간:** 00:00:00")

st.markdown("---")

# 상태 초기화
if "game_started" not in st.session_state:
    st.session_state.game_started = False
    st.session_state.cards = []
    st.session_state.used_cards = set()
    st.session_state.selected = []
    st.session_state.set_successes = []
    st.session_state.set_failures = []

# SET 판별 함수
def is_set(cards):
    features = list(zip(*[list(card[:4]) for card in cards]))
    return all(len(set(f)) in [1, 3] for f in features)

# 카드 클릭 핸들러
def toggle_card(idx):
    if idx in st.session_state.selected:
        st.session_state.selected.remove(idx)
    elif len(st.session_state.selected) < 3:
        st.session_state.selected.append(idx)

# 카드 3장 SET인지 판별
def process_selection():
    selected = st.session_state.selected
    cards = [st.session_state.cards[i] for i in selected]
    now = int(time.time() - st.session_state.start_time)

    if is_set(cards):
        st.session_state.set_successes.append((len(st.session_state.set_successes)+1, str(timedelta(seconds=now))))
        st.success("🎉 SET 성공!")
        # 성공한 카드 제거
        for i in sorted(selected, reverse=True):
            del st.session_state.cards[i]
        # 새 카드 추가
        remaining_cards = list(set(ALL_CARDS) - set(st.session_state.cards) - st.session_state.used_cards)
        new_cards = random.sample(remaining_cards, min(3, len(remaining_cards)))
        st.session_state.cards.extend(new_cards)
        st.session_state.used_cards.update(new_cards)
    else:
        st.session_state.set_failures.append((len(st.session_state.set_failures)+1, str(timedelta(seconds=now))))
        st.error("❌ SET 실패!")

    st.session_state.selected = []

# 게임 시작 버튼
if not st.session_state.game_started:
    if st.button("🎲 게임 시작하기", key="start_btn"):
        st.session_state.game_started = True
        st.session_state.start_time = time.time()
        st.session_state.cards = random.sample(ALL_CARDS, 12)
        st.session_state.used_cards = set(st.session_state.cards)
        st.session_state.selected = []
        st.rerun()
    else:
        st.stop()

# 카드 선택 처리
if len(st.session_state.selected) == 3:
    process_selection()

# 카드 출력
cols = st.columns(4)
for idx, card_file in enumerate(st.session_state.cards):
    col = cols[idx % 4]
    with col:
        st.image(os.path.join(CARD_DIR, card_file), width=160)
        is_selected = idx in st.session_state.selected
        btn_label = "✅ 선택됨" if is_selected else "⚪"
        st.button(
            btn_label,
            key=f"btn_{idx}",
            on_click=toggle_card,
            args=(idx,),
            help=card_file
        )

st.markdown("---")

# SET 성공 / 실패 기록 테이블
left, right = st.columns(2)
with left:
    st.markdown("### ✅ SET 성공 기록")
    if st.session_state.set_successes:
        st.table({"번호": [s[0] for s in st.session_state.set_successes],
                  "소요 시간": [s[1] for s in st.session_state.set_successes]})
    else:
        st.write("아직 성공한 SET이 없습니다.")

with right:
    st.markdown("### ❌ SET 실패 기록")
    if st.session_state.set_failures:
        st.table({"번호": [f[0] for f in st.session_state.set_failures],
                  "소요 시간": [f[1] for f in st.session_state.set_failures]})
    else:
        st.write("아직 실패한 SET이 없습니다.")

# 게임 종료
if len(st.session_state.cards) == 0:
    st.markdown("### 🎉 모든 카드를 사용했습니다! 게임 종료!")
