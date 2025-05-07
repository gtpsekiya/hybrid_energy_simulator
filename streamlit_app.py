

# streamlit_app.py (V4)
import streamlit as st
import pandas as pd

st.set_page_config(page_title="ハイブリッドマイクロインバーター節電V4", layout="wide")
st.title("🔋 ハイブリッドマイクロインバーター節電シミュレーター V4")

# --- 設定入力 ---
st.sidebar.header("🔧 システム設定")
scenario = st.sidebar.selectbox("使用シナリオ", ["自宅", "オフィス", "手動入力"])
battery_capacity = st.sidebar.selectbox("蓄電池容量 (kWh)", [2, 4, 6, 8])
solar_power = st.sidebar.slider("ソーラー出力上限 (W)", 0, 4000, 1000, step=100)
electricity_cost = st.sidebar.number_input("電気代 (円/kWh)", min_value=1, max_value=100, value=35)
st.sidebar.markdown("---")

st.sidebar.header("⚙️ エコモード設定")
eco_start = st.sidebar.slider("エコモード開始 (時)", 0, 23, 23)
eco_end = st.sidebar.slider("エコモード終了 (時)", 1, 24, 6)
st.sidebar.markdown("※この時間帯だけ電力会社から充電を許可")

# --- データ準備 ---
time_slots = [f"{h}:00-{h+1}:00" for h in range(24)]
default_profile = {
    "自宅":  [0.3]*6 + [0.6]*2 + [0.4]*4 + [0.8]*5 + [1.0]*4 + [0.6]*3,
    "オフィス": [0.2]*8 + [1.2]*8 + [0.2]*8
}

data = pd.DataFrame({"時間帯": time_slots})

if scenario != "手動入力":
    data["使用電力 (kWh)"] = default_profile[scenario]
else:
    uploaded_file = st.file_uploader("またはCSVファイルをアップロード (時間帯,使用電力)", type="csv")
    if uploaded_file:
        user_data = pd.read_csv(uploaded_file)
        data = user_data.copy()
    else:
        data["使用電力 (kWh)"] = [0.0]*24
        data["使用電力 (kWh)"] = st.data_editor(data)["使用電力 (kWh)"]

# --- シミュレーション処理 ---
def simulate(df):
    result = []
    battery = battery_capacity
    for i, row in df.iterrows():
        usage = row["使用電力 (kWh)"]
        hour = i
        solar = min(solar_power * 1 / 1000, usage)  # 仮に1時間定格発電
        usage -= solar
        from_battery = 0
        from_grid = 0

        # バッテリーから供給
        if battery >= usage:
            from_battery = usage
            battery -= usage
            usage = 0
        else:
            from_battery = battery
            usage -= battery
            battery = 0

        # 電力会社（エコモード充電考慮）
        from_grid = usage
        if eco_start <= hour or hour < eco_end:
            charge = min(battery_capacity - battery, 1.0)
            battery += charge
            from_grid += charge

        result.append([solar, from_battery, from_grid])

    result_df = pd.DataFrame(result, columns=["ソーラー", "蓄電池", "電力会社"])
    return result_df

# --- 計算＆表示 ---
if st.button("🚀 シミュレーション開始"):
    result_df = simulate(data)
    merged = pd.concat([data, result_df], axis=1)
    merged["節電額 (円)"] = merged["電力会社"] * electricity_cost

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Before（電力会社のみ）")
        before_total = data["使用電力 (kWh)"].sum()
        before_cost = before_total * electricity_cost
        st.metric("合計電力", f"{before_total:.2f} kWh")
        st.metric("電気料金 (推定)", f"{before_cost:.0f} 円")

    with col2:
        st.subheader("✅ After（ハイブリッド）")
        after_cost = merged["節電額 (円)"].sum()
        saved = before_cost - after_cost
        st.metric("節電後電気料金", f"{after_cost:.0f} 円")
        st.metric("節約額", f"{saved:.0f} 円")

    st.markdown("---")
    st.subheader("⏱ 時間別使用電力と節電額")
    st.dataframe(merged[["時間帯", "使用電力 (kWh)", "ソーラー", "蓄電池", "電力会社", "節電額 (円)"]], use_container_width=True)

    st.bar_chart(merged[["ソーラー", "蓄電池", "電力会社"]])
