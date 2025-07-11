import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="🧠 MoodTracker", page_icon="🧠", layout="centered")

st.title("🧠 MoodTracker – Your Personal Wellbeing Journal")

# --- Small Advertisement ---
st.markdown(
    """
    <div style="border:2px solid #A3BFFA; border-radius:10px; padding:10px; background-color:#F0F8FF; margin-bottom:20px;">
        <h4 style="color:#2C5282; margin:0;">🌟 Take Charge of Your Mind – <b>loopbreakerMD</b>!</h4>
        <p style="margin:0; color:#2C5282;">
            For confidential support and professional care, reach out to <b>loopbreakerMD@gmail.com</b>.<br>
            <i>Your journey to better mental wellbeing starts now!</i>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Data Privacy Notice and Consent ---
st.info(
    "🔒 **Data Collection & Privacy Notice**\n\n"
    "To help us understand wellbeing trends, we collect some basic demographic information (age, gender, profession) along with your mood logs. "
    "All your data will be kept confidential and securely stored. By continuing, you consent to participate in this data collection. "
    "If you do not consent, you will not be able to use the mood tracker."
)

if "consent_given" not in st.session_state:
    st.session_state.consent_given = None

if st.session_state.consent_given is None:
    consent = st.radio(
        "Do you consent to the collection and safe storage of your demographic data and mood logs?",
        ["Yes, I consent", "No, I do not consent"],
        index=None
    )
    if consent == "Yes, I consent":
        st.session_state.consent_given = True
        st.rerun()
    elif consent == "No, I do not consent":
        st.session_state.consent_given = False
        st.warning("You must provide consent to use the Mood Tracker. Thank you for considering.")
        st.stop()
else:
    if not st.session_state.consent_given:
        st.warning("You must provide consent to use the Mood Tracker. Thank you for considering.")
        st.stop()

# --- Demographics Collection ---
if "demographics" not in st.session_state:
    with st.form("demographics_form", clear_on_submit=False):
        st.subheader("Tell us a bit about yourself (demographics)")
        age = st.number_input("Age", min_value=0, max_value=120, step=1)
        gender = st.selectbox("Gender", options=["", "Prefer not to say", "Female", "Male", "Non-binary", "Other"])
        profession = st.text_input("Profession (e.g., Student, Engineer, Teacher, etc.)")
        submitted = st.form_submit_button("Submit Demographics")
        if submitted:
            if age < 14:
                st.error("Sorry, you must be at least 14 years old to use MoodTracker.")
                st.stop()
            elif not (age and gender and profession.strip()):
                st.error("Please fill in all fields before proceeding.")
                st.stop()
            else:
                st.session_state.demographics = {
                    "age": int(age),
                    "gender": gender,
                    "profession": profession.strip()
                }
                st.success("Demographics saved! Thank you.")
                st.rerun()

if "demographics" not in st.session_state:
    st.stop()

st.write(
    f"Welcome, {st.session_state.demographics['profession']}! "
    "Track your mood for a week, build healthy habits, and celebrate your progress. "
    "Let’s boost your self-awareness and mental wellbeing!"
)

# --- Mood options and categories ---
MOOD_OPTIONS = [
    ("😄 Happy", "positive"),
    ("🤩 Excited", "positive"),
    ("🧘 Calm", "positive"),
    ("😐 Neutral", "neutral"),
    ("😔 Sad", "negative"),
    ("😰 Anxious", "negative"),
    ("😴 Tired", "negative")
]
POSITIVE_MOODS = {m for m, cat in MOOD_OPTIONS if cat == "positive"}
NEGATIVE_MOODS = {m for m, cat in MOOD_OPTIONS if cat == "negative"}
ALERT_MOODS = {"😔 Sad", "😰 Anxious", "😴 Tired"}

# --- Session state initialization ---
if "logs" not in st.session_state:
    st.session_state.logs = []
if "day" not in st.session_state:
    st.session_state.day = 1
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "max_streak" not in st.session_state:
    st.session_state.max_streak = 0
if "reminder_sent" not in st.session_state:
    st.session_state.reminder_sent = False

# --- Friendly Reminder if user hasn't logged today ---
today_str = datetime.date.today().isoformat()
if st.session_state.logs:
    last_entry = st.session_state.logs[-1]
    if last_entry["date"] != today_str and not st.session_state.reminder_sent:
        st.info("👋 Don’t forget to log your mood today! Consistency builds insight.")
        st.session_state.reminder_sent = True

# --- Mood logging section ---
if st.session_state.day <= 7:
    st.header(f"Day {st.session_state.day}")
    mood_choices = [m for m, _ in MOOD_OPTIONS]
    mood = st.selectbox("How do you feel today?", [""] + mood_choices, key=st.session_state.day)
    note = st.text_area("Anything you'd like to add? (optional)", key=f"note_{st.session_state.day}")

    if st.button("Log Mood"):
        # Require a mood to be picked
        if not mood:
            st.error("Please select your mood for today before logging.")
            st.stop()
        # Store the log, including demographics for each entry (for analysis)
        entry = {
            "date": today_str,
            "day": st.session_state.day,
            "mood": mood,
            "note": note,
            "age": st.session_state.demographics["age"],
            "gender": st.session_state.demographics["gender"],
            "profession": st.session_state.demographics["profession"]
        }
        st.session_state.logs.append(entry)

        # Streak logic
        if mood in POSITIVE_MOODS:
            st.session_state.streak += 1
            if st.session_state.streak > st.session_state.max_streak:
                st.session_state.max_streak = st.session_state.streak
        else:
            st.session_state.streak = 0  # reset on non-positive mood

        # Feedback and affirmation
        if mood in POSITIVE_MOODS:
            st.success("🌟 Great job! Keep the positivity going!")
        elif mood in NEGATIVE_MOODS:
            st.warning("Remember: It's okay to have tough days. Tomorrow is a new chance.")
        else:
            st.info("Staying neutral is part of the human experience!")

        # Motivational, streak-based notification
        if st.session_state.streak > 0:
            st.balloons()
            st.info(f"🔥 You're on a {st.session_state.streak}-day positive streak! Keep it up!")
        
        # Friendly affirmation
        st.write("💬 *Every mood is valid. Thank you for taking care of yourself today!*")
        
        st.session_state.day += 1
        st.rerun()

else:
    # --- Week summary ---
    st.header("🎉 Week Complete! Here's Your Mood Journey:")
    log_df = pd.DataFrame(st.session_state.logs)
    st.dataframe(log_df[["day", "date", "mood", "note", "age", "gender", "profession"]])

    # Stats
    mood_counts = log_df["mood"].value_counts()
    most_common = mood_counts.idxmax()
    positive_days = log_df["mood"].isin(POSITIVE_MOODS).sum()
    negative_days = log_df["mood"].isin(NEGATIVE_MOODS).sum()
    streak = st.session_state.max_streak

    st.write(f"**Most frequent mood:** {most_common}")
    st.write(f"**Positive days:** {positive_days} / 7")
    st.write(f"**Longest positive streak:** {streak} day(s)")

    # --- Encourage seeking help if ALERT_MOODS for at least two days ---
    alert_days = log_df["mood"].isin(ALERT_MOODS).sum()
    if alert_days >= 2:
        st.error("💡 It seems you've experienced sadness, anxiety, or tiredness for at least two days this week. Consider reaching out to a professional for support at loopbreakerMD@gmail.com 💪✨")

    # Personalised feedback
    if positive_days >= 5:
        st.success("🌈 You're doing amazing! Celebrate your positive energy this week.")
    elif negative_days >= 4:
        st.warning("Be gentle with yourself – tough weeks happen. Consider reaching out to someone you trust.")
    else:
        st.info("A balanced week! Remember, all feelings are part of your journey.")

    # Positive reinforcement
    st.write("👏 *You showed dedication by logging your mood each day. Self-awareness is the first step to self-care!*")

    # Mood chart
    st.write("#### Mood frequency chart")
    st.bar_chart(mood_counts)

    # Download logs (with demographics)
    csv = log_df.to_csv(index=False).encode()
    st.download_button(
        label="Download my mood log (CSV)",
        data=csv,
        file_name='mood_log.csv',
        mime='text/csv'
    )

    # Restart option
    if st.button("Restart Mood Tracker"):
        st.session_state.logs = []
        st.session_state.day = 1
        st.session_state.streak = 0
        st.session_state.max_streak = 0
        st.session_state.reminder_sent = False
        st.session_state.demographics = None
        st.session_state.consent_given = None
        st.rerun()

# --- Footer encouragement ---
st.markdown("---")
st.markdown("💡 *Keep checking in with yourself. Small steps build big habits!*")
