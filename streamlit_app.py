import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="מבצע אליענה 50", layout="centered")

# ה-ID של הגליון שלך (מתוך הלינק ששלחת)
SHEET_ID = "1TXdTlGeOrthRKf5Ax6YNk6xLaiwnflDVqpMv89ksnP8"

def get_sheet_data(worksheet_name):
    # שיטה ישירה לקריאת CSV מגוגל שיטס
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={worksheet_name}"
    try:
        return pd.read_csv(url)
    except Exception as e:
        st.error(f"שגיאה בקריאת הטאב {worksheet_name}")
        st.write(e)
        return None

# --- כניסה ראשונית ---
if 'user_name' not in st.session_state:
    st.title("🎂 חוגגים 50 לאליענה!")
    name = st.text_input("הכניסו שם כדי להצטרף:")
    if st.button("אני מוכן/ה!"):
        if name:
            st.session_state.user_name = name
            st.rerun()
    st.stop()

# קריאת נתונים
df_control = get_sheet_data("Control")
df_questions = get_sheet_data("Questions")

if df_control is not None and df_questions is not None:
    # שליפת המצב הנוכחי
    curr_q_id = int(df_control.iloc[0]['current_q'])
    state = df_control.iloc[0]['state']
    
    # שליפת נתוני השאלה
    q_data = df_questions[df_questions['id'] == curr_q_id].iloc[0]

    # --- תצוגה לפי מצב (State) ---
    if state == "welcome":
        st.header("ברוכים הבאים!")
        st.video(q_data['host_intro_video'])
        
    elif state == "intro":
        st.header(f"שאלה {curr_q_id}")
        st.video(q_data['host_intro_video'])

    elif state == "question":
        st.header("זמן להצביע!")
        st.image(q_data['options_image'], use_container_width=True)
        # כאן יבואו כפתורי ההצבעה
        st.columns(4)[0].button("A") # דוגמה לכפתור
        
    elif state == "reveal":
        st.header("והתשובה היא...")
        st.video(q_data['reveal_video'])
        st.balloons()

    # ריענון אוטומטי כל 3 שניות
    time.sleep(3)
    st.rerun()
