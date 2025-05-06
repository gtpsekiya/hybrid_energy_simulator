import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="ハイブリッド節電シミュレーターV2", layout="wide")
st.title("🔋 ハイブリッドマイクロインバーター節電シミュレーター V2")

st.markdown("""
このアプリは、時間帯別の使用電力量から、節電モード別（売電優先／蓄電優先／エコ）に基づいて節電効果（kWh・金額）を計算・比較します。
""")

# 入力欄
unit_price = st.sidebar.number_input("電気料金（円/kWh）", min_value=1, max_value=100, value=35)
usage_kwh = []
st.sidebar.markdown("### 時間帯別使用量（kWh）")
for h in range(24):
    usage_kwh.append(st.sidebar.slider(f"{h}:00-{h+1}:00", 0.0, 3.0, 1.0, 0.1))

# モード別節電率
modes = {
    "売電優先": 0.10,
    "蓄電優先": 0.20,
    "エコモード": 0.30
}

# 使用前の合計
total_before = sum(usage_kwh)

# 結果計算
results = []
mode_lines = {}
for mode, reduction in modes.items():
    usage_after = [round(v * (1 - reduction), 2) for v in usage_kwh]
    total_after = sum(usage_after)
    saved_kwh = total_before - total_after
    saved_yen = round(saved_kwh * unit_price)
    results.append({
        "モード": mode,
        "節電量（kWh）": round(saved_kwh, 2),
        "節電金額（円）": saved_yen,
        "節約率": f"{int(reduction * 100)}%"
    })
    mode_lines[mode] = usage_after

# 表表示
df_results = pd.DataFrame(results)
st.subheader("📊 節電モード別 比較表")
st.dataframe(df_results, use_container_width=True)

# グラフ
st.subheader("📈 使用前 vs モード別 使用電力の比較")
time_slots = [f"{h}:00-{h+1}:00" for h in range(24)]
plt.figure(figsize=(12, 6))
plt.plot(time_slots, usage_kwh, label="使用前", linestyle="--", color="black")
for mode, line in mode_lines.items():
    plt.plot(time_slots, line, label=f"{mode}（使用後）")
plt.xticks(rotation=45)
plt.ylabel("使用電力（kWh）")
plt.title("時間帯別 使用前 vs 節電モード別 使用後の比較")
plt.legend()
plt.grid(True)
st.pyplot(plt)

# 合計
st.subheader("🔎 合計使用量と節電効果")
st.markdown(f"**使用前合計**：{round(total_before, 2)} kWh")
