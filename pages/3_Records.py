import streamlit as st
from utils import plot_game_stats

st.set_page_config(page_title="SET 게임 기록", layout="wide")
st.title("📊 SET 게임 누적 기록 분석")

plot_game_stats()

st.markdown("---")
st.info("※ 이 기록은 각 판 종료 시 자동 저장된 통계입니다.\n\nCSV 파일로 저장되며, 새 게임이 끝날 때마다 누적됩니다.")
