import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# ✅ 한글 폰트 설정
font_path = os.path.join("fonts", "NanumGothic-Regular.ttf")
font_prop = fm.FontProperties(fname=font_path)

# ✅ 페이지 설정
st.set_page_config(page_title="SET 기록 보기", layout="wide")
st.markdown("## 📊 게임 기록 시각화")

file_path = "game_records.csv"

# ✅ 기록 삭제 버튼
with st.expander("⚙️ 기록 관리"):
    if st.button("🗑 기록 전체 삭제하기"):
        if os.path.exists(file_path):
            os.remove(file_path)
            st.success("✅ 모든 기록이 삭제되었습니다.")
            st.stop()
        else:
            st.warning("삭제할 기록 파일이 없습니다.")
            st.stop()

# ✅ 기록 시각화
if os.path.exists(file_path):
    df = pd.read_csv(
        file_path,
        names=[
            "날짜", 
            "힌트 없이 SET 맞춘 횟수", 
            "힌트 없이 평균 시간(초)", 
            "힌트 써서 맞춘 SET", 
            "총 맞춘 SET 개수", 
            "SET 틀린 횟수", 
            "SET 틀린 평균 시간(초)", 
            "총점", 
            "총 플레이 시간(초)"
        ]
    )

    df["날짜"] = pd.to_datetime(df["날짜"])
    df = df.sort_values("날짜")

    st.markdown("### 📋 전체 게임 기록")
    st.dataframe(df, use_container_width=True)

    # 🎯 총점 추이
    st.markdown("### 🎯 총점 변화 추이")
    fig1, ax1 = plt.subplots()
    ax1.plot(df["날짜"], df["총점"], marker="o", linestyle="-", color="blue")
    ax1.set_title("총점 변화 추이", fontproperties=font_prop)
    ax1.set_xlabel("날짜", fontproperties=font_prop)
    ax1.set_ylabel("총점", fontproperties=font_prop)
    ax1.tick_params(axis='x', rotation=45)
    for label in ax1.get_xticklabels() + ax1.get_yticklabels():
        label.set_fontproperties(font_prop)
    st.pyplot(fig1)


    # ⏱ 플레이 시간 vs 총점
    st.markdown("### ⏱ 플레이 시간과 총점의 관계")
    fig3, ax3 = plt.subplots()
    ax3.scatter(df["총 플레이 시간(초)"], df["총점"], color="purple", alpha=0.7)
    ax3.set_title("플레이 시간 vs 총점", fontproperties=font_prop)
    ax3.set_xlabel("총 플레이 시간 (초)", fontproperties=font_prop)
    ax3.set_ylabel("총점", fontproperties=font_prop)
    for label in ax3.get_xticklabels() + ax3.get_yticklabels():
        label.set_fontproperties(font_prop)
    st.pyplot(fig3)

    # 📅 날짜별 힌트 없이 맞춘 횟수
    st.markdown("### 📅 날짜별 힌트 없이 맞춘 횟수")
    fig5, ax5 = plt.subplots()
    ax5.plot(df["날짜"], df["힌트 없이 SET 맞춘 횟수"], marker="o", linestyle="-", color="green")
    ax5.set_title("날짜별 힌트 없이 SET 성공 횟수", fontproperties=font_prop)
    ax5.set_xlabel("날짜", fontproperties=font_prop)
    ax5.set_ylabel("힌트 없이 SET 성공", fontproperties=font_prop)
    ax5.tick_params(axis='x', rotation=45)
    for label in ax5.get_xticklabels() + ax5.get_yticklabels():
        label.set_fontproperties(font_prop)
    st.pyplot(fig5)

    # 🔁 힌트 없이 성공 vs 실패 관계 (산점도)
    st.markdown("### 🔁 힌트 없이 성공 vs 실패 횟수")
    fig6, ax6 = plt.subplots()
    ax6.scatter(df["힌트 없이 SET 맞춘 횟수"], df["SET 틀린 횟수"], color="red", alpha=0.6)
    ax6.set_title("힌트 없이 성공과 실패의 관계", fontproperties=font_prop)
    ax6.set_xlabel("힌트 없이 SET 성공", fontproperties=font_prop)
    ax6.set_ylabel("실패 횟수", fontproperties=font_prop)
    for label in ax6.get_xticklabels() + ax6.get_yticklabels():
        label.set_fontproperties(font_prop)
    st.pyplot(fig6)



    # 🏅 최고 점수 TOP 5
    st.markdown("### 🏅 최고 점수 TOP 5")
    st.table(df.sort_values("총점", ascending=False).head(5).reset_index(drop=True))

else:
    st.warning("아직 저장된 게임 기록이 없습니다. 먼저 게임을 플레이하세요!")
