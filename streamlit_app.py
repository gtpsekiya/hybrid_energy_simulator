import streamlit as st
import pandas as pd

st.set_page_config(page_title="節電シミュレーター V2", layout="wide")
st.title("🔋 ハイブリッドマイクロインバーター節電シミュレーター")
st.caption("時間別の使用電力を入力すると、最も経済的な動作モード（蓄電優先 / 売電優先 / エコ）と節電額が自動表示されます。")

# -------------------------
# 入力パネル
# -------------------------
with st.sidebar:
    st.header("⚙️ システム設定")
    battery_capacity = st.selectbox("蓄電池容量 (kWh)", [2, 4, 6, 8], index=0)
    solar_power = st.slider("ソーラー出力 (W)", 0, 4000, 1000, step=100)
    electricity_cost = st.number_input("電気代 (円/kWh)", value=35, min_value=0, max_value=100)

# -------------------------
# 時間別使用電力 入力
# -------------------------
st.subheader("🕒 時間別使用電力を入力")
time_slots = [f"{i}:00–{i+1}:00" for i in range(24)]
default_values = [0] * 24

electricity_input = st.data_editor(
    pd.DataFrame({"時間帯": time_slots, "使用電力 (W)": default_values}),
    use_container_width=True
)
df = electricity_input["使用電力 (W)"].astype(float) / 1000

# -------------------------
# 処理・ロジック
# -------------------------
if st.button("🔍 シミュレーションする"):
    total_usage = df.sum()
    battery_used = min(total_usage, battery_capacity)
    solar_energy = solar_power * 5 / 1000  # 仮に5時間発電
    solar_used = min(total_usage, solar_energy)
    grid_used = total_usage - battery_used - solar_used
    saved_cost = grid_used * electricity_cost

    # 結果表示
    st.success("✅ 結果表示")
    st.metric("一日の消費電力量 (kWh)", f"{total_usage:.2f}")
    st.metric("蓄電池からの使用量 (kWh)", f"{battery_used:.2f}")
    st.metric("電力会社からの使用量 (kWh)", f"{grid_used:.2f}")
    st.metric("推定電気代 (円)", f"{saved_cost:.0f}")

    # 棒グラフ
    chart_df = pd.DataFrame({
        "使用電力 (合計)": df,
        "電力会社": df - battery_used / 24
    })
    st.bar_chart(chart_df)

