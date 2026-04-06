import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="מבצע אליענה 50", layout="centered")

SHEET_ID = "1TXdTlGeOrthRKf5Ax6YNk6xLaiwnflDVqpMv89ksnP8"

# פונקציה לתיקון לינקים של גוגל דרייב כדי שיעבדו ב-Streamlit
def fix_google_drive_link(url):
    if "drive.google.com" in str(url) and "view" in str(url):
        file_id = url.split('/')[-2]
        return f"https://drive.google.com/uc?id={file_id}"
    return url

def get_sheet_data(worksheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={worksheet_name}"
    try:
        df = pd.read_csv(url)
        # ניקוי כותרות - הופך הכל לאותיות קטנות ומוחק רווחים
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        return None

# --- מסך כניסה ---
if 'user_name' not in st.session_state:
    st.title("🎂 חוגגים 50 לאליענה!")
    name = st.text_input("הכניסו שם כדי להצטרף:")
    if st.button("אני מוכן/ה!"):
        if name:
            st.session_state.user_name = name
            st.rerun()
    st.stop()

# קריאת נתונים (Control ו-Questions)
df_control = get_sheet_data("Control")
df_questions = get_sheet_data("Questions")

if df_control is not None and df_questions is not None:
    try:
        curr_q_id = int(df_control.iloc[0]['current_q'])
        state = df_control.iloc[0]['state']
        
        # חיפוש נתוני השאלה
        q_row = df_questions[df_questions['id'] == curr_q_id]
        
        if not q_row.empty:
            q_data = q_row.iloc[0]
            
            # --- תצוגה לפי המצב ב-Control ---
            if state == "welcome":
                st.header("ברוכים הבאים!")
                st.video(fix_google_drive_link(q_data['host_intro_video']))
                
            elif state == "intro":
                st.header(f"שאלה {curr_q_id}")
                st.video(fix_google_drive_link(q_data['host_intro_video']))

            elif state == "question":
                st.header("זמן להצביע!")
                st.image(fix_google_drive_link(q_data['options_image']), use_container_width=True)
                
                # כפתורי הצבעה (כרגע רק ליופי, בהמשך נחבר לשמירת תוצאות)
                col1, col2, col3, col4 = st.columns(4)
                if col1.button("A"): st.balloons()
                if col2.button("B"): st.balloons()
                if col3.button("C"): st.balloons()
                if col4.button("D"): st.balloons()
                
            elif state == "reveal":
                st.header("והתשובה היא...")
                st.video(fix_google_drive_link(q_data['reveal_video']))
                st.success(f"התשובה הנכונה: {q_data['correct_answer']}")

        else:
            st.warning(f"לא מצאתי את שאלה {curr_q_id} בטאב Questions")

    except Exception as e:
        st.error(f"שגיאה בעיבוד הנתונים: {e}")

# ריענון אוטומטי (כל 3 שניות)
time.sleep(3)
st.rerun()
