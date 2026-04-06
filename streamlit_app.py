import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="מבצע אליענה 50", layout="centered")

SHEET_ID = "1TXdTlGeOrthRKf5Ax6YNk6xLaiwnflDVqpMv89ksnP8"

def fix_google_drive_link(url):
    # בודק אם הקישור תקין ולא ריק (float/NaN)
    if pd.isna(url) or not isinstance(url, str):
        return None
    if "drive.google.com" in url and "view" in url:
        try:
            file_id = url.split('/')[-2]
            return f"https://drive.google.com/uc?id={file_id}"
        except:
            return url
    return url

def get_sheet_data(worksheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={worksheet_name}"
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except:
        return None

# --- כניסה ---
if 'user_name' not in st.session_state:
    st.title("🎂 חוגגים 50 לאליענה!")
    name = st.text_input("הכניסו שם כדי להצטרף:")
    if st.button("אני מוכן/ה!"):
        if name:
            st.session_state.user_name = name
            st.rerun()
    st.stop()

df_control = get_sheet_data("Control")
df_questions = get_sheet_data("Questions")

if df_control is not None and df_questions is not None:
    try:
        curr_q_id = int(df_control.iloc[0]['current_q'])
        state = df_control.iloc[0]['state']
        q_row = df_questions[df_questions['id'] == curr_q_id]
        
        if not q_row.empty:
            q_data = q_row.iloc[0]
            
            # פונקציית עזר להצגת וידאו בטוחה
            def safe_video(url_key):
                link = fix_google_drive_link(q_data.get(url_key))
                if link:
                    st.video(link)
                else:
                    st.warning(f"חסר קישור לווידאו בעמודה {url_key} עבור שאלה {curr_q_id}")

            if state == "welcome":
                st.header("ברוכים הבאים!")
                safe_video('host_intro_video')
                
            elif state == "intro":
                st.header(f"שאלה {curr_q_id}")
                safe_video('host_intro_video')

            elif state == "question":
                st.header("זמן להצביע!")
                img_link = fix_google_drive_link(q_data.get('options_image'))
                if img_link:
                    st.image(img_link, use_container_width=True)
                else:
                    st.error("חסרה תמונת האפשרויות (Grid Image)!")
                
                # כפתורים
                st.columns(4)[0].button("A")
                
            elif state == "reveal":
                st.header("והתשובה היא...")
                safe_video('reveal_video')
                st.success(f"התשובה הנכונה: {q_data['correct_answer']}")

        else:
            st.warning(f"לא מצאתי את שאלה {curr_q_id} בטאב Questions")

    except Exception as e:
        st.error(f"שגיאה בעיבוד הנתונים: {e}")

time.sleep(3)
st.rerun()
