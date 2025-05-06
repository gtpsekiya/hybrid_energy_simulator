import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ページ設定
st.set_page_config(page_title="ハイブリッドマイクロインバーター節電シミュレーターV2", layout="wide")
st.title("🔋 ハイブリッドマイクロインバーター節電シミュレーターV2")
st.caption("時間帯別の電力使用に応じて最適モードを提案します（売電優先／蓄電優先／エコ）")

# ユーザー設定
col1, col2, col3 = st.columns(3)
with col1:
    battery_kwh = st.selectbox("🔋蓄電池容量 (kWh)", [2, 4, 6, 8])
with col2:
    solar_output = st.slider("☀️ソーラー出力 (W)", 0, 4000, 1000)
with col3:
    price = st.number_input("💰電気代 (円/kWh)", 10, 100, 35)

# 時間帯入力（24時間）
st.markdown("### ⏱️時間別電力入力（W）")
time_slots = [f"{i}:00–{i+1}:00" for i in range(24)]
usage = {}
for t in time_slots:
    usage[t] = st.number_input(f"{t}", 0, 3000, 0, key=t)

# モード別変換効率
eff = {
    "売電優先": 0.10,
    "蓄電優先": 0.20,
    "エコ": 0.30
}

# 結果の保存
results = []

for mode, eff_rate in eff.items():
    total_kwh = sum(usage.values()) / 1000
    saved = total_kwh * eff_rate
    saved_yen = saved * price
    results.append({
        "モード": mode,
        "総使用量 (kWh)": total_kwh,
        "節電量 (kWh)": round(saved, 2),
        "節電金額 (円)": round(saved_yen)
    })

# 表示
st.markdown("### 📊 節電結果（モード別）")
df = pd.DataFrame(results)
st.dataframe(df, use_container_width=True)

# グラフ
st.markdown("### 📈 モード別節電金額グラフ")
fig, ax = plt.subplots()
ax.bar(df["モード"], df["節電金額 (円)"], color=["skyblue", "orange", "green"])
ax.set_ylabel("節電金額 (円)")
ax.set_title("モード別 節電効果比較")
st.pyplot(fig)

# 使用前 vs 使用後
st.markdown("### 🔍 使用前 vs 使用後（エコモード基準）")
before = sum(usage.values()) / 1000 * price
after = before - df[df["モード"] == "エコ"]["節電金額 (円)"].values[0]
st.metric("使用前電気代 (円)", round(before))
st.metric("使用後電気代 (円)", round(after))
