import streamlit as st
import pandas as pd

st.set_page_config(page_title="ハイブリッドマイクロインバーター節電シミュレーター", layout="wide")

st.title("🔋 ハイブリッドマイクロインバーター節電シミュレーター")
st.caption("関谷株式会社 - 家庭の電力使用に最適なモードと節電方法を提案します")

# ユーザー設定入力
col1, col2, col3 = st.columns(3)
with col1:
    battery_capacity = st.selectbox("蓄電池容量（kWh）", [2, 4, 6, 8])
with col2:
    solar_output = st.slider("ソーラー出力（W）", 0, 4000, 1000, step=100)
with col3:
    electricity_cost = st.number_input("電気代（円/kWh）", value=35)

st.markdown("### ⏱️ 時間別使用電力入力")
time_slots = [f"{i}:00–{i+1}:00" for i in range(24)]
default_values = [0] * 24
usage = st.data_editor(
    pd.DataFrame({"時間帯": time_slots, "使用電力（W）": default_values}),
    num_rows="fixed"
)

# 節電計算ロジック（例）
if st.button("🔍 シミュレーション開始"):
    df = usage
    df["kWh"] = df["使用電力（W）"] / 1000
    total_kWh = df["kWh"].sum()
    battery_use = min(total_kWh, battery_capacity)
    grid_use = total_kWh - battery_use
    cost = grid_use * electricity_cost

    st.success("✅ 結果表示")
    st.metric("一日の消費電力量（kWh）", f"{total_kWh:.2f}")
    st.metric("蓄電池からの使用量（kWh）", f"{battery_use:.2f}")
    st.metric("電力会社からの使用量（kWh）", f"{grid_use:.2f}")
    st.metric("推定電気代（円）", f"{cost:.0f}")

    st.bar_chart(
        pd.DataFrame({
            "ソーラー＋蓄電池": [battery_use],
            "電力会社": [grid_use]
        })
    )
