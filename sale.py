import streamlit as st
import requests
import datetime

# 1. ページ設定
st.set_page_config(page_title="営業進捗入力", layout="centered")

# 2. 上部・全体の余白を極限まで削るCSS
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* メインコンテンツエリアの余白をゼロに */
            .block-container {
                padding-top: 0rem;
                padding-bottom: 0rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }
            
            /* タイトル（h1）の上の余白を消す */
            h1 {
                margin-top: -30px;
                padding-top: 0px;
            }
            
            /* 画面最上部のデッドスペースを消す */
            .stAppHeader {
                height: 0px;
                display: none;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# 3. タイトル表示
st.title("営業進捗入力")

# --- 設定（GASのURL） ---
GOOGLE_SCRIPT_URL = st.secrets["GOOGLE_SCRIPT_URL"]

# --- データの初期化 (読み込み値を保持する場所) ---
if "data" not in st.session_state:
    st.session_state.data = {}
if "showings" not in st.session_state:
    st.session_state.showings = 0

# --- 入力フォーム ---
with st.container():
    # A: 登録日
    # 読み込みデータがあればそれを使い、なければ今日の日付
    default_date = datetime.date.today()
    if "date" in st.session_state.data and st.session_state.data["date"]:
        default_date = datetime.datetime.strptime(st.session_state.data["date"], "%Y-%m-%d").date()
    
    date = st.date_input("登録日", default_date)
    
    # B: 担当者名
    staff_name = st.text_input("担当者名", value=st.session_state.data.get("staffName", ""), placeholder="氏名を入力")
    
    # C: 物件名
    col1, col2 = st.columns([3, 1])
    with col1:
        name = st.text_input("物件名", value=st.session_state.data.get("name", ""), placeholder="物件名を入力")
    with col2:
        st.write(" ") # 余白調整
        if st.button("読込"):
            if not name:
                st.error("物件名を入力してください")
            else:
                with st.spinner("読込中..."):
                    res = requests.get(f"{GOOGLE_SCRIPT_URL}?name={name}")
                    if res.status_code == 200:
                        result = res.json()
                        if "error" not in result:
                            st.session_state.data = result
                            st.session_state.showings = result.get("showings", 0)
                            st.rerun() # 画面を再描画して値を反映
                        else:
                            st.warning("新規物件です")
                    else:
                        st.error("通信エラー")

    # D, E, G: 数字入力 (valueに読み込んだ値を指定)
    c1, c2, c3 = st.columns(3)
    pre_period = c1.number_input("空室期間(日)", min_value=0, step=1, value=int(st.session_state.data.get("prePeriod", 0)))
    views = c2.number_input("閲覧数", min_value=0, step=1, value=int(st.session_state.data.get("views", 0)))
    days_to_close = c3.number_input("成約日数", min_value=0, step=1, value=int(st.session_state.data.get("daysToClose", 0)))

    # F: 案内数
    st.write("---")
    col_s1, col_s2 = st.columns([1, 2])
    with col_s1:
        st.metric("現地案内回数", st.session_state.showings)
    with col_s2:
        if st.button("➕ 案内を1件追加", use_container_width=True):
            st.session_state.showings += 1

    # H: 記録メモ
    feedback = st.text_area("記録メモ / 大家さんの声", value=st.session_state.data.get("feedback", ""), placeholder="内容を入力してください")

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
            st.success("スプレッドシートに保存しました！")
            # 保存後はデータをリセット
            st.session_state.data = {}
            st.session_state.showings = 0
        else:
            st.error("保存に失敗しました")




