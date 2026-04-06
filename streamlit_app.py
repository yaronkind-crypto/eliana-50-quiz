import streamlit as st
import pandas as pd
import time
import requests

st.set_page_config(page_title="מבצע אליענה 50", layout="centered")

SHEET_ID = "1TXdTlGeOrthRKf5Ax6YNk6xLaiwnflDVqpMv89ksnP8"

def fix_google_drive_link(url):
    if pd.isna(url) or not isinstance(url, str) or "http" not in url:
        return None
    if "drive.google.com" in url and "view" in url:
        try:
            file_id = url.split('/')[-2]
            return f"https://drive.google.com/uc?id={file_id}"
        except: return url
    return url

def get_sheet_data(worksheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={worksheet_name}"
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except: return None

# פונקציית כתיבה (לצורך עדכון ה-Control מהאפליקציה)
def update_sheet_control(q_id, state):
    # הערה: כתיבה דורשת Service Account. כרגע נשתמש בעדכון ידני בגליון
    # או שנבנה לינק "חכם" לעדכון אם תרצה בהמשך.
    st.info(f"הבמאי ביקש לעבור ל: {state} בשאלה {q_id}. שנה זאת בטאב Control בגליון.")

# --- כניסה ---
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
    curr_q_id = int(df_control.iloc[0]['current_q'])
    state = df_control.iloc[0]['state']
    
    # --- ממשק במאי סודי ---
    with st.sidebar:
        is_admin = st.checkbox("מצב במאי (ירון)")
        if is_admin:
            pwd = st.text_input("סיסמה:", type="password")
            if pwd == "eliana50":
                st.write("### 🎬 לוח בקרה")
                st.write(f"מצב נוכחי: **{state}**")
                st.caption("שנה את הערכים בגליון הגוגל והאפליקציה תתעדכן:")
                st.code(f"ID: {curr_q_id} | State: {state}")
            else: is_admin = False

    # שליפת השאלה
    q_row = df_questions[df_questions['id'] == curr_q_id]
    if not q_row.empty:
        q_data = q_row.iloc[0]
        
        if state == "welcome":
            st.header("ברוכים הבאים!")
            video = fix_google_drive_link(q_data.get('host_intro_video'))
            if video: st.video(video)
            else: st.warning("ממתינים לסרטון הפתיחה...")

        elif state == "intro":
            st.header(f"שאלה {curr_q_id}")
            video = fix_google_drive_link(q_data.get('host_intro_video'))
            if video: st.video(video)
            else: st.warning(f"חסר סרטון מנחה לשאלה {curr_q_id}")

        elif state == "question":
            st.header(q_data.get('question_text', 'שאלה'))
            img = fix_google_drive_link(q_data.get('options_image'))
            if img: st.image(img, use_container_width=True)
            else: st.error("חסר גריד תמונות לשאלה זו!")
            
            # כפתורי הצבעה
            st.write("### מה התשובה הנכונה?")
            cols = st.columns(4)
            for i, char in enumerate(["A", "B", "C", "D"]):
                if cols[i].button(char, use_container_width=True):
                    st.success(f"תודה {st.session_state.user_name}, הצבעתך ל-{char} נקלטה!")

        elif state == "reveal":
            st.header("והתשובה היא...")
            video = fix_google_drive_link(q_data.get('reveal_video'))
            if video: st.video(video)
            st.success(f"התשובה הנכונה: {q_data.get('correct_answer')}")
            st.balloons()
    else:
        st.warning(f"לא נמצאה שאלה עם ID {curr_q_id}")

# ריענון אוטומטי
time.sleep(3)
st.rerun()
