import streamlit as st
import pandas as pd
import time

# הגדרות דף בסיסיות
st.set_page_config(page_title="מבצע אליענה 50", layout="centered")

# ה-ID של הגליון שלך
SHEET_ID = "1TXdTlGeOrthRKf5Ax6YNk6xLaiwnflDVqpMv89ksnP8"

# פונקציה לתיקון לינקים של גוגל דרייב
def fix_google_drive_link(url):
    if pd.isna(url) or not isinstance(url, str) or "http" not in url:
        return None
    if "drive.google.com" in url and "view" in url:
        try:
            file_id = url.split('/')[-2]
            return f"https://drive.google.com/uc?id={file_id}"
        except:
            return url
    return url

# פונקציה למשיכת נתונים מהגליון
def get_sheet_data(worksheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={worksheet_name}"
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except:
        return None

# --- מסך כניסה ---
if 'user_name' not in st.session_state:
    st.title("🎂 חוגגים 50 לאליענה!")
    st.subheader("ברוכים הבאים לאפליקציית החידון")
    name = st.text_input("הכניסו שם כדי להצטרף למשחק:")
    if st.button("אני מוכן/ה!"):
        if name:
            st.session_state.user_name = name
            st.rerun()
    st.stop()

# קריאת נתוני שליטה ושאלות
df_control = get_sheet_data("Control")
df_questions = get_sheet_data("Questions")

if df_control is not None and df_questions is not None:
    try:
        # שליפת מצב נוכחי
        curr_q_id = int(df_control.iloc[0]['current_q'])
        state = df_control.iloc[0]['state']
        
        # חיפוש נתוני השאלה הספציפית
        q_row = df_questions[df_questions['id'] == curr_q_id]
        
        # תפריט במאי סודי בצידי המסך
        with st.sidebar:
            if st.checkbox("מצב במאי"):
                pwd = st.text_input("סיסמה:", type="password")
                if pwd == "eliana50":
                    st.success("שלום ירון הבמאי!")
                    st.write(f"שאלה נוכחית: {curr_q_id}")
                    st.write(f"מצב שידור: {state}")
                else:
                    st.error("סיסמה שגויה")

        if not q_row.empty:
            q_data = q_row.iloc[0]
            
            # פונקציה להצגת וידאו במידות נכונות וממורכזות
            def display_centered_video(url_key):
                video_url = fix_google_drive_link(q_data.get(url_key))
                if video_url:
                    # יצירת עמודות כדי שהווידאו לא יהיה ענק מדי
                    col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
                    with col2:
                        st.video(video_url)
                else:
                    st.info("📺 כאן יופיע הווידאו ברגע שתדביקו לינק בגליון")

            # --- לוגיקת התצוגה לפי ה-State ---
            if state == "welcome":
                st.header("מיד מתחילים...")
                display_centered_video('host_intro_video')
                
            elif state == "intro":
                st.header(f"שאלה {curr_q_id}")
                display_centered_video('host_intro_video')

            elif state == "question":
                st.header("הצביעו עכשיו!")
                img_link = fix_google_drive_link(q_data.get('options_image'))
                if img_link:
                    st.image(img_link, use_container_width=True)
                
                st.write(f"### {q_data.get('question_text', '')}")
                
                # כפתורי הצבעה
                cols = st.columns(4)
                for i, char in enumerate(["A", "B", "C", "D"]):
                    if cols[i].button(char, use_container_width=True, key=f"btn_{char}"):
                        st.balloons()
                        st.success(f"הצבעת ל-{char}! מחכים לתוצאות...")
        
            elif state == "reveal":
                st.header("והתשובה הנכונה היא...")
                display_centered_video('reveal_video')
                st.success(f"התשובה היא: {q_data.get('correct_answer')}")

        else:
            st.warning(f"ממתין לנתונים עבור שאלה {curr_q_id}...")

    except Exception as e:
        st.error(f"יש תקלה קטנה בנתונים: {e}")

# ריענון אוטומטי כל 3 שניות כדי לסנכרן בין כל האורחים
time.sleep(3)
st.rerun()
