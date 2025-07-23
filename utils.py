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
