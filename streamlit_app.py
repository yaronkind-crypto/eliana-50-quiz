import streamlit as st
import pandas as pd
import time

# --- הגדרות עמוד ---
st.set_page_config(page_title="מבצע אליענה 50", layout="centered")

# --- עיצוב ---
st.markdown("""
<style>
.block-container { padding-top: 2rem; max-width: 800px !important; }
iframe { border-radius: 15px; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); }
h1, h2, h3 { text-align: center !important; color: #FF4B4B; }
</style>
""", unsafe_allow_html=True)

# --- Google Sheet ---
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
        
        return f"https://www.youtube.com/embed/{vid}?autoplay=1&mute=1&controls=1"
    except:
        return None

def show_video(url):
    embed = youtube_embed(url)
    
    if embed:
        st.markdown(f"""
        <iframe 
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

# --- כניסה ---
if "user_name" not in st.session_state:
    st.title("🎂 חוגגים 50 לאליענה!")
    name = st.text_input("הכניסו שם כדי להצטרף:")
    
    if st.button("אני מוכן/ה!", use_container_width=True):
        if name:
            st.session_state.user_name = name
            st.rerun()
    
    st.stop()

# --- טעינת נתונים ---
df_control = get_sheet_data("Control")
df_questions = get_sheet_data("Questions")

if df_control is None or df_questions is None:
    st.error("בעיה בטעינת הנתונים מהגיליון")
    st.stop()

curr_q = int(df_control.iloc[0]["current_q"])
state = df_control.iloc[0]["state"]

q_row = df_questions[df_questions["id"] == curr_q]

if q_row.empty:
    st.warning("אין שאלה זמינה כרגע")
    st.stop()

q = q_row.iloc[0]

# --- מצבים ---
if state in ["welcome", "intro"]:
    st.header("הנה זה מתחיל..." if state == "welcome" else f"שאלה {curr_q}")
    
    show_video(q.get("host_intro_video"))

elif state == "question":
    st.header("הצביעו עכשיו!")

    if isinstance(q.get("options_image"), str):
        st.image(q.get("options_image"), use_container_width=True)

    st.subheader(q.get("question_text", ""))

    cols = st.columns(4)
    for i, opt in enumerate(["A", "B", "C", "D"]):
        if cols[i].button(opt, use_container_width=True):
            st.balloons()
            st.success(f"הצבעת {opt}!")

elif state == "reveal":
    st.header("והתשובה היא...")
    
    show_video(q.get("reveal_video"))

    st.success(f"התשובה הנכונה: {q.get('correct_answer')}")

# --- ריענון ---
time.sleep(3)
st.rerun()
