import streamlit as st
import pandas as pd
import time

# הגדרת דף רחב אבל נשלוט ברוחב התוכן בתוך הדף
st.set_page_config(page_title="מבצע אליענה 50", layout="wide")

# עיצוב מותאם אישית למרכוז וכותרות
st.markdown("""
    <style>
    .stVideo { margin: auto; border-radius: 15px; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); }
    h1, h2, h3 { text-align: center; }
    </style>
    """, unsafe_allow_html=True)

SHEET_ID = "1TXdTlGeOrthRKf5Ax6YNk6xLaiwnflDVqpMv89ksnP8"

def fix_google_drive_link(url):
    if pd.isna(url) or not isinstance(url, str) or len(url) < 10:
        return None
    if "drive.google.com" in url:
        try:
            if "/d/" in url:
                file_id = url.split('/d/')[1].split('/')[0]
            elif "id=" in url:
                file_id = url.split('id=')[1].split('&')[0]
            else: return url
            return f"https://drive.google.com/uc?export=download&id={file_id}"
        except: return url
    return url

def get_sheet_data(worksheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={worksheet_name}"
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except: return None

# --- מסך כניסה ---
if 'user_name' not in st.session_state:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🎂 חוגגים 50 לאליענה!")
        name = st.text_input("הכניסו שם כדי להצטרף:")
        if st.button("אני מוכן/ה!", use_container_width=True):
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
    
    q_row = df_questions[df_questions['id'] == curr_q_id]
    
    if not q_row.empty:
        q_data = q_row.iloc[0]
        
        # מרכוז התוכן באמצעות עמודות - זה הפתרון לגודל!
        # יחס של [1, 2, 1] אומר שהווידאו יתפוס 50% מהמרכז
        side_space, center_content, side_space2 = st.columns([1, 2, 1])
        
        with center_content:
            if state == "welcome" or state == "intro":
                st.header("הנה זה מתחיל..." if state == "welcome" else f"שאלה {curr_q_id}")
                v_url = fix_google_drive_link(q_data.get('host_intro_video'))
                if v_url: 
                    st.video(v_url)
                else: 
                    st.info("🎥 ממתינים לסרטון... (וודאו שיש לינק תקין בגליון בשורה המתאימה)")

            elif state == "question":
                st.header("זמן להצביע!")
                img = fix_google_drive_link(q_data.get('options_image'))
                if img: st.image(img, use_container_width=True)
                
                st.subheader(q_data.get('question_text', ''))
                
                # כפתורי הצבעה גדולים
                vote_cols = st.columns(4)
                for i, char in enumerate(["A", "B", "C", "D"]):
                    if vote_cols[i].button(char, use_container_width=True, key=f"v_{char}"):
                        st.balloons()
                        st.success(f"הצבעת {char}!")

            elif state == "reveal":
                st.header("והתשובה היא...")
                v_url = fix_google_drive_link(q_data.get('reveal_video'))
                if v_url: st.video(v_url)
                st.success(f"התשובה הנכונה: {q_data.get('correct_answer')}")

    else:
        st.warning(f"ממתין לנתונים עבור שאלה {curr_q_id}...")

# ריענון אוטומטי כל 3 שניות
time.sleep(3)
st.rerun()
