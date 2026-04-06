import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
from datetime import datetime

# הגדרות עמוד בסיסיות
st.set_page_config(page_title="מבצע אליענה 50", layout="centered")

# חיבור לגליון (חיבור חי ללא Cache כדי שיהיה סנכרון מהיר)
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    # משיכת נתונים מהגליון
    control = conn.read(worksheet="Control", ttl=0).iloc[0]
    questions = conn.read(worksheet="Questions", ttl=0)
    return control, questions

def update_control(q_id, state):
    # עדכון מצב המשחק (עבור הבמאי)
    df = pd.DataFrame([{"current_q": q_id, "state": state}])
    conn.update(worksheet="Control", data=df)

def save_vote(user_name, q_id, answer, correct_ans):
    # שמירת הצבעה של אורח
    is_correct = (answer == correct_ans)
    new_data = pd.DataFrame([{
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_name": user_name,
        "q_id": q_id,
        "answer": answer,
        "is_correct": is_correct
    }])
    # כאן הקוד יוסיף שורה לטאב Responses
    # הערה: יש לוודא הגדרות כתיבה ב-Streamlit Secrets
    st.toast(f"התשובה {answer} נשלחה!")

# --- לוגיקת זיהוי משתמש ---
if 'user_name' not in st.session_state:
    st.title("🎂 חוגגים 50 לאליענה!")
    name = st.text_input("הכניסו את שמכם כדי להצטרף לחידון:")
    if st.button("אני מוכן/ה!"):
        if name:
            st.session_state.user_name = name
            st.rerun()
    st.stop()

# שליפת המצב הנוכחי מהגליון
control, questions = get_data()
curr_q_id = int(control['current_q'])
state = control['state']
q_data = questions[questions['id'] == curr_q_id].iloc[0]

# --- תפריט צד סודי לבמאי (ירון) ---
with st.sidebar:
    st.write(f"שלום, {st.session_state.user_name}")
    is_admin = st.checkbox("מצב במאי (סיסמה נדרשת)")
    if is_admin:
        pwd = st.text_input("סיסמה:", type="password")
        if pwd != "eliana50": # שנה את הסיסמה כאן
            is_admin = False
            st.error("סיסמה שגויה")

# --- הצגת התוכן לפי ה-State ---
if is_admin:
    st.title("🎬 לוח בקרה - במאי")
    st.info(f"מצב נוכחי: {state} | שאלה: {curr_q_id}")
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("🎥 פתיחה (Welcome)"): update_control(curr_q_id, "welcome")
    if c2.button("🎙️ מנחה (Intro)"): update_control(curr_q_id, "intro")
    if c3.button("❓ שאלה (Vote)"): update_control(curr_q_id, "question")
    if c4.button("✅ חשיפה (Reveal)"): update_control(curr_q_id, "reveal")
    
    if st.button("➡️ עבור לשאלה הבאה"):
        update_control(curr_q_id + 1, "intro")
    st.divider()

# --- מה שהאורחים רואים ---
if state == "welcome":
    st.header("ברוכים הבאים!")
    st.video(q_data['host_intro_video'])
    st.write("הישארו מחוברים, מיד מתחילים...")

elif state == "intro":
    st.header(f"שאלה {curr_q_id}")
    st.video(q_data['host_intro_video'])
    st.write("הקשיבו לשאלה...")

elif state == "question":
    st.header("זמן להצביע!")
    st.image(q_data['options_image'], use_container_width=True)
    
    # כפתורי הצבעה
    cols = st.columns(4)
    for i, char in enumerate(["A", "B", "C", "D"]):
        if cols[i].button(char, use_container_width=True):
            save_vote(st.session_state.user_name, curr_q_id, char, q_data['correct_answer'])

elif state == "reveal":
    st.header("והתשובה היא...")
    st.video(q_data['reveal_video'])
    st.success(f"התשובה הנכונה: {q_data['correct_answer']}")
    st.balloons()

# ריענון אוטומטי לאורחים כדי להסתנכרן עם הבמאי
if not is_admin:
    time.sleep(2)
    st.rerun()