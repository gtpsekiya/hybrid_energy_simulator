import zipfile
import os

# Create the new V5 Streamlit app code (as a simple example)
streamlit_code = """
import streamlit as st
import pandas as pd

st.set_page_config(page_title="ハイブリッドマイクロインバーター節電シミュレーター V5", layout="wide")

st.title("🔋 ハイブリッドマイクロインバーター節電シミュレーター V5")
st.markdown("マイクロインバーター＋蓄電池＋ソーラーの運用による節電効果を時間別に計算し、Before/Afterで比較します。")

battery_capacity = st.selectbox("蓄電池容量（kWh）", [2, 4, 6, 8])
solar_power = st.slider("ソーラー出力（W）", 0, 4000, 1000, step=100)
electricity_cost = st.number_input("電力会社の電気代（円/kWh）", min_value=5.0, max_value=60.0, value=35.0, step=0.1)

time_slots = [f"{i}:00-{i+1}:00" for i in range(24)]
default_usage = [0]*24

st.subheader("📥 時間別使用電力（W）を入力")
electricity_input = st.data_editor(pd.DataFrame({
    "時間帯": time_slots,
    "使用電力 (W)": default_usage,
}), use_container_width=True)

if st.button("⚡ シミュレーション開始"):
    df = electricity_input
    df["使用電力 (kWh)"] = df["使用電力 (W)"] / 1000

    df["蓄電池からの供給 (kWh)"] = 0.0
    df["ソーラーからの供給 (kWh)"] = 0.0
    df["電力会社から購入 (kWh)"] = 0.0

    remaining_battery = battery_capacity
    for i in range(24):
        use = df.loc[i, "使用電力 (kWh)"]
        solar = solar_power / 1000 if 7 <= i <= 16 else 0  # 7時〜16時発電
        from_solar = min(solar, use)
        remaining = use - from_solar

        from_battery = min(remaining_battery, remaining)
        remaining -= from_battery
        from_grid = remaining

        df.loc[i, "ソーラーからの供給 (kWh)"] = from_solar
        df.loc[i, "蓄電池からの供給 (kWh)"] = from_battery
        df.loc[i, "電力会社から購入 (kWh)"] = from_grid
        remaining_battery -= from_battery

    df["Before料金 (円)"] = df["使用電力 (kWh)"] * electricity_cost
    df["After料金 (円)"] = df["電力会社から購入 (kWh)"] * electricity_cost
    df["節電額 (円)"] = df["Before料金 (円)"] - df["After料金 (円)"]

    st.success("✅ 結果表示")
    st.dataframe(df[["時間帯", "使用電力 (kWh)", "ソーラーからの供給 (kWh)", "蓄電池からの供給 (kWh)", "電力会社から購入 (kWh)", "節電額 (円)"]])

    st.subheader("💰 節電効果グラフ")
    st.bar_chart(df.set_index("時間帯")[["節電額 (円)"]])
"""

# Save to Python file
file_path = "/mnt/data/streamlit_app.py"
with open(file_path, "w", encoding="utf-8") as f:
    f.write(streamlit_code)

file_path
