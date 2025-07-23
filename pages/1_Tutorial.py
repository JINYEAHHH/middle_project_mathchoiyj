# pages/1_Tutorial.py

import streamlit as st
import os
import sys

# 상위 디렉토리 경로 추가 (utils.py를 불러오기 위해)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import CARD_DIR

# 예시 카드 세트
set1 = ["0000.png", "0010.png", "0020.png"]
set2 = ["0120.png", "1201.png", "2012.png"]
not_set = ["0000.png", "0001.png", "1002.png"]

# 정답 데이터
answers = {
    "set1": ["전부 다름", "전부 같음", "전부 같음", "전부 같음"],
    "set2": ["전부 다름", "전부 다름", "전부 다름", "전부 다름"],
    "notset": ["전부 같음", "전부 같음", "2개만 같음", "전부 다름"]
}
set_type = {
    "set1": True,
    "set2": True,
    "notset": False
}

# 속성 이름
attribute_labels = ["색깔", "모양", "명암", "개수"]

# 선택 박스 UI 함수
def show_select_table(key_prefix):
    options = ["전부 같음", "2개만 같음", "전부 다름"]
    cols = st.columns(4)
    selections = []
    for i, col in enumerate(cols):
        sel = col.selectbox(
            attribute_labels[i],
            [""] + options,
            key=f"{key_prefix}_attr{i}"
        )
        if sel == "":
            selections.append(None)
        else:
            selections.append(sel)
    return selections

# 정답 비교 및 결과 출력 함수
def check_answer_and_display(selection, correct, is_set, example_num):
    if any(sel is None for sel in selection):
        return  # 아직 모든 속성이 선택되지 않음

    if selection == correct:
        st.success(f"맞았어요! 예제 {example_num}은 SET{'입니다' if is_set else '이 아닙니다'}.")
    else:
        st.warning("다시 한 번 확인해보세요!")

# ------------------------
# 페이지 내용 구성 시작
# ------------------------

st.title("📘 SET 보드게임이란?")

st.markdown("**SET**은 81장의 카드로 이루어진 보드게임입니다.")
st.markdown("각 카드는 다음과 같은 4가지 속성을 가지고 있습니다:")

st.markdown("##### 1. 색깔: 빨강, 보라, 초록")
st.image(["set_cards/0100.png", "set_cards/0110.png", "set_cards/0120.png"], width=130)

st.markdown("##### 2. 모양: 타원, 마름모, 물결")
st.image(["set_cards/2222.png", "set_cards/2122.png", "set_cards/2022.png"], width=130)

st.markdown("##### 3. 명암: 색칠된 것, 줄무늬, 빈 것")
st.image(["set_cards/0211.png", "set_cards/1211.png", "set_cards/2211.png"], width=130)

st.markdown("##### 4. 개수: 1개, 2개, 3개")
st.image(["set_cards/1000.png", "set_cards/1001.png", "set_cards/1002.png"], width=130)

st.markdown("---")
st.markdown("### 🎯 게임 목표")
st.markdown("3장의 카드를 선택하여 **SET**을 찾는 것이 목표입니다.")

st.markdown("---")
st.markdown("### ✅ SET의 조건")
st.markdown("선택한 3장의 카드에 대해, **각 속성마다 다음 중 하나**를 만족해야 합니다:")
st.markdown("- 전부 같거나")
st.markdown("- 전부 다르거나")
st.markdown("이 조건을 4가지 속성 모든 것에 대해 만족하면 **SET**입니다.")

st.markdown("---")
st.markdown("### 🧪 SET 판단 연습")
st.markdown("아래의 예제에 나온 세 장의 카드 속성을 각각 확인하여, **SET인지 아닌지** 판단해보세요.")

# 예제 1
st.markdown("### 🎲 예제 1")
st.image([os.path.join(CARD_DIR, f) for f in set1], width=130)
sel1 = show_select_table("set1")
check_answer_and_display(sel1, answers["set1"], set_type["set1"], 1)

# 예제 2
st.markdown("---")
st.markdown("### 🎲 예제 2")
st.image([os.path.join(CARD_DIR, f) for f in set2], width=130)
sel2 = show_select_table("set2")
check_answer_and_display(sel2, answers["set2"], set_type["set2"], 2)

# 예제 3
st.markdown("---")
st.markdown("### 🎲 예제 3")
st.image([os.path.join(CARD_DIR, f) for f in not_set], width=130)
sel3 = show_select_table("notset")
check_answer_and_display(sel3, answers["notset"], set_type["notset"], 3)
