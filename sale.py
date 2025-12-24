import streamlit as st
import requests
import datetime

# ページ設定
st.set_page_config(page_title="営業進捗入力", layout="centered")

st.title("営業進捗入力")

# --- 設定（GASのURL） ---
# Streamlit Cloudの「Secrets」に保存したURLを読み込みます
GOOGLE_SCRIPT_URL = st.secrets["GOOGLE_SCRIPT_URL"]

# --- 入力フォーム ---
with st.container():
    # A: 登録日（一番上）
    date = st.date_input("登録日", datetime.date.today())
    
    # B: 担当者名
    staff_name = st.text_input("担当者名", placeholder="氏名を入力")
    
    # C: 物件名
    col1, col2 = st.columns([3, 1])
    with col1:
        name = st.text_input("物件名", placeholder="物件名を入力")
    with col2:
        if st.button("読込"):
            res = requests.get(f"{GOOGLE_SCRIPT_URL}?name={name}")
            if res.status_code == 200 and "error" not in res.json():
                st.session_state.data = res.json()
                st.success("読み込み完了")
            else:
                st.warning("新規物件")

    # D, E, G: 数字入力
    c1, c2, c3 = st.columns(3)
    pre_period = c1.number_input("空室期間(日)", min_value=0, step=1)
    views = c2.number_input("閲覧数", min_value=0, step=1)
    days_to_close = c3.number_input("成約日数", min_value=0, step=1)

    # F: 案内数（カウンター風）
    st.write("---")
    if "showings" not in st.session_state:
        st.session_state.showings = 0
    
    col_s1, col_s2 = st.columns([1, 2])
    with col_s1:
        st.metric("現地案内回数", st.session_state.showings)
    with col_s2:
        if st.button("➕ 案内を1件追加", use_container_width=True):
            st.session_state.showings += 1

    # H: 記録メモ
    feedback = st.text_area("記録メモ / 大家さんの声", placeholder="内容を入力してください")

# --- 保存ボタン ---
if st.button("スプレッドシートへ保存", type="primary", use_container_width=True):
    payload = {
        "date": str(date),
        "staffName": staff_name,
        "name": name,
        "prePeriod": pre_period,
        "views": views,
        "showings": st.session_state.showings,
        "daysToClose": days_to_close,
        "feedback": feedback
    }
    
    with st.spinner("保存中..."):
        res = requests.post(GOOGLE_SCRIPT_URL, json=payload)
        if res.status_code == 200:
            st.success("Excelに保存しました！")
        else:
            st.error("保存に失敗しました")