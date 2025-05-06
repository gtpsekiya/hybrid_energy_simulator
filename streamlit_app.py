import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="節電シミュレーターV2", layout="wide")
st.title("🔋 ハイブリッドマイクロインバーター節電シミュレーター V2")

st.markdown("""
家庭の電力使用に応じて、ハイブリッドマイクロインバーターがどのように節電に貢献するかを可視化します。
使用前／使用後の比較ができ、より効果的な節電戦略を確認できます。
""")

# --- 入力エリア ---
col1, col2, col3 = st.columns(3)
with col1:
    battery_capacity = st.selectbox("蓄電池容量 (kWh)", [2, 4, 6, 8])
with col2:
    solar_power = st.slider("ソーラー出力 (W)", 0, 4000, 1000, step=100)
with col3:
    electricity_cost = st.number_input("電気代 (円/kWh)", min_value=10, max_value=100, value=35)

# --- 時間帯別の使用電力入力 ---
time_slots = [f"{i}:00 - {i+1}:00" for i in range(24)]
default_values = [0]*24

st.subheader("⏱ 時間帯別 電気使用量 (W)")
electricity_input = st.data_editor(pd.DataFrame({"時間帯": time_slots, "使用電力 (W)": default_values}), use_container_width=True)

# --- 処理 ---
if st.button("🔍 シミュレーション実行"):
    df = electricity_input
    df["使用電力量 (kWh)"] = df["使用電力 (W)"].astype(float) / 1000

    total_usage = df["使用電力量 (kWh)"].sum()
    battery_used = min(total_usage, battery_capacity)
    solar_used = min(battery_used, solar_power / 1000 * 5)  # 仮に日中5時間発電として試算
    grid_used = total_usage - battery_used

    saved_cost = grid_used * electricity_cost

    st.success("✅ 結果表示")
    st.metric("一日の総消費電力量 (kWh)", f"{total_usage:.2f}")
    st.metric("ソーラー＋蓄電池からの供給 (kWh)", f"{battery_used:.2f}")
    st.metric("電力会社からの購入 (kWh)", f"{grid_used:.2f}")
    st.metric("想定電気代 (円)", f"{saved_cost:.0f}")

    # グラフ
    chart_df = pd.DataFrame({
        "使用前 (全て電力会社)": df["使用電力量 (kWh)"],
        "使用後 (節電後)": [g if g > 0 else 0 for g in df["使用電力量 (kWh)"].values - battery_used / 24]
    }, index=time_slots)

    st.bar_chart(chart_df, use_container_width=True)
