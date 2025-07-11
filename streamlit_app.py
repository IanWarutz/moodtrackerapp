import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="🧠 MoodTracker", page_icon="🧠", layout="centered")

st.title("🧠 MoodTracker – Your Personal Wellbeing Journal")
st.write(
    "Welcome! Track your mood for a week, build healthy habits, and celebrate your progress. "
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
    mood = st.selectbox("How do you feel today?", mood_choices, key=st.session_state.day)
    note = st.text_area("Anything you'd like to add? (optional)", key=f"note_{st.session_state.day}")

    if st.button("Log Mood"):
        # Store the log
        entry = {
            "date": today_str,
            "day": st.session_state.day,
            "mood": mood,
            "note": note
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
        st.experimental_rerun()

else:
    # --- Week summary ---
    st.header("🎉 Week Complete! Here's Your Mood Journey:")
    log_df = pd.DataFrame(st.session_state.logs)
    st.dataframe(log_df[["day", "date", "mood", "note"]])

    # Stats
    mood_counts = log_df["mood"].value_counts()
    most_common = mood_counts.idxmax()
    positive_days = log_df["mood"].isin(POSITIVE_MOODS).sum()
    negative_days = log_df["mood"].isin(NEGATIVE_MOODS).sum()
    streak = st.session_state.max_streak

    st.write(f"**Most frequent mood:** {most_common}")
    st.write(f"**Positive days:** {positive_days} / 7")
    st.write(f"**Longest positive streak:** {streak} day(s)")

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

    # Download logs
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
        st.experimental_rerun()

# --- Footer encouragement ---
st.markdown("---")
st.markdown("💡 *Keep checking in with yourself. Small steps build big habits!*")