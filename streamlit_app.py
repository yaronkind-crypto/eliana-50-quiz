import streamlit as st
import pandas as pd
import time
from pathlib import Path

# --- הגדרות עמוד ---
st.set_page_config(page_title="מבצע אליענה 50", layout="centered")

# --- עיצוב ---
st.markdown("""
<style>
.block-container { padding-top: 2rem; max-width: 800px !important; }
iframe { border-radius: 15px; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); transition: all 0.5s ease; }
.flash { animation: flash 0.5s linear 3; }
.fade { animation: fade 1s linear; }
@keyframes flash { 0%,100% {background-color:#fff;} 50% {background-color:#FF4B4B;} }
@keyframes fade { from {opacity:0;} to {opacity:1;} }
h1, h2, h3 { text-align: center !important; color: #FF4B4B; transition: all 0.5s ease; }
.stButton>button { font-size: 18px; }
</style>
""", unsafe_allow_html=True)

# --- Google Sheet (לקריאת שאלות בלבד) ---
SHEET_ID = "1TXdTlGeOrthRKf5Ax6YNk6xLaiwnflDVqpMv89ksnP8"
def get_sheet_data(sheet):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet}"
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except:
        return None

# --- YouTube Embed ---
def youtube_embed(url):
    if not isinstance(url, str):
        return None
    try:
        if "watch?v=" in url:
            vid = url.split("watch?v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            vid = url.split("youtu.be/")[1].split("?")[0]
        else:
            return None
        return f"https://www.youtube.com/embed/{vid}?autoplay=1&mute=1&playsinline=1&rel=0"
    except:
        return None

def show_video(url, flash=False, fade=False):
    embed = youtube_embed(url)
    if embed:
        effect = "flash" if flash else "fade" if fade else ""
        st.markdown(f"""
        <iframe class="{effect}"
            width="100%" 
            height="420" 
            src="{embed}" 
            frameborder="0" 
            allow="autoplay; encrypted-media"
            allowfullscreen>
        </iframe>
        """, unsafe_allow_html=True)
        st.caption("אם הסרטון לא מתחיל - לחצו ▶️")
    else:
        st.warning("⚠️ בעיה בלינק של הוידאו")

# --- סאונד דרמטי ---
def play_sound(file_path):
    if Path(file_path).exists():
        st.audio(file_path)
    else:
        st.warning("סאונד לא נמצא")

# --- כניסה ---
if "user_name" not in st.session_state:
    st.title("🎂 חוגגים 50 לאליענה!")
    name = st.text_input("הכניסו שם כדי להצטרף:")
    if st.button("אני מוכן/ה!", use_container_width=True):
        if name:
            st.session_state.user_name = name
            st.rerun()
    st.stop()

# --- טעינת שאלות ---
df_questions = get_sheet_data("Questions")
if df_questions is None:
    st.error("בעיה בטעינת הנתונים מהגיליון")
    st.stop()

# --- משתנים פנימיים ---
if "local_state" not in st.session_state:
    st.session_state.local_state = "welcome"
if "local_q" not in st.session_state:
    st.session_state.local_q = 1
if "score" not in st.session_state:
    st.session_state.score = 0
if "timer" not in st.session_state:
    st.session_state.timer = 0
if "timer_start" not in st.session_state:
    st.session_state.timer_start = None

curr_q = st.session_state.local_q
q_row = df_questions[df_questions["id"] == curr_q]
if q_row.empty:
    st.warning("אין עוד שאלות זמינות")
    st.stop()
q = q_row.iloc[0]
state = st.session_state.local_state

# --- פאנל ניהול ---
with st.sidebar:
    st.title("🎮 שליטה")
    if st.button("Intro 🎬"):
        st.session_state.local_state = "intro"
    if st.button("שאלה ❓"):
        st.session_state.local_state = "question"
        st.session_state.timer = 10
        st.session_state.timer_start = time.time()
    if st.button("Reveal 🎉"):
        st.session_state.local_state = "reveal"
        play_sound("drama_sound.mp3")
    if st.button("שאלה הבאה ➡️"):
        st.session_state.local_q += 1
        st.session_state.local_state = "question"
        st.session_state.timer = 10
        st.session_state.timer_start = time.time()

# --- מצבים ---
if state == "welcome":
    st.header(f"🎉 היי {st.session_state.user_name}, מתחילים את החגיגה!")
    st.caption("לחצו על 'Intro 🎬' בסיידבר כדי להתחיל")

elif state == "intro":
    st.header("הנה זה מתחיל...")
    show_video(q.get("host_intro_video"))

elif state == "question":
    st.header("❓ הצביעו עכשיו!")
    
    if isinstance(q.get("options_image"), str):
        st.image(q.get("options_image"), use_container_width=True)
    
    st.subheader(q.get("question_text", ""))

    # טיימר עם ספירה לאחור ואפקטים
    if st.session_state.timer_start:
        elapsed = int(time.time() - st.session_state.timer_start)
        remaining = max(0, st.session_state.timer - elapsed)
        st.progress(remaining / st.session_state.timer)
        st.caption(f"נותרו {remaining} שניות")
        if remaining == 0:
            st.session_state.local_state = "reveal"
            play_sound("drama_sound.mp3")
            st.session_state.timer_start = None
            st.rerun()

    # הצבעה עם ניקוד
    cols = st.columns(4)
    for i, opt in enumerate(["A", "B", "C", "D"]):
        if cols[i].button(opt, use_container_width=True):
            if opt == q.get("correct_answer"):
                st.session_state.score += 1
            st.balloons()
            st.success(f"הצבעת {opt}!")

elif state == "reveal":
    st.header(f"🎉 והתשובה היא...",)
    show_video(q.get("reveal_video"), flash=True)
    st.success(f"התשובה הנכונה: {q.get('correct_answer')}")
    st.subheader(f"ניקוד נוכחי: {st.session_state.score}")

# --- הפעלה מחדש רק כשצריך ---
if "last_state" not in st.session_state:
    st.session_state.last_state = state
if st.session_state.last_state != state:
    st.session_state.last_state = state
    st.experimental_rerun()
