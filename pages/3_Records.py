import sys
import os
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ✅ 상위 폴더의 utils.py import 가능하도록 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import plot_game_stats

# ✅ 한글 폰트 설정 (NanumGothic)
font_path = os.path.join("fonts", "NanumGothic-Regular.ttf")
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False

# ✅ Streamlit 페이지 설정
st.set_page_config(page_title="SET 게임 기록", layout="wide")
st.title("📊 SET 게임 누적 기록 분석")

# ✅ 누적 통계 시각화 함수 호출
plot_game_stats()

# ✅ 안내 메시지
st.markdown("---")
st.info("※ 이 기록은 각 판 종료 시 자동 저장된 통계입니다.\n\n게임을 다시 시작하면 통계가 누적됩니다.")

