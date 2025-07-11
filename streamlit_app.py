import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="🧠 MoodTracker", page_icon="🧠", layout="centered")

st.title("🧠 MoodTracker – Your Personal Wellbeing Journal")

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
            if not (age and gender and profession.strip()):
                st.error("Please enter your age, gender, and profession.")
                st.stop()
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

# --- Use a PNG/JPG Plutchik Emotion Wheel (royalty-free, always visible, HD) ---
# HD Plutchik emotion wheel, safe to use: https://commons.wikimedia.org/wiki/File:Plutchik-wheel.png
# Direct PNG (2048x2048): https://upload.wikimedia.org/wikipedia/commons/3/3a/Plutchik-wheel.png
PLUTCHIK_WHEEL_PNG = "https://upload.wikimedia.org/wikipedia/commons/3/3a/Plutchik-wheel.png"
st.markdown("#### Choose your emotion by referencing the wheel below (click to enlarge):")
st.image(PLUTCHIK_WHEEL_PNG, caption="Plutchik's Emotion Wheel (click to enlarge)", use_container_width=True)

# The full set of emotions on the Plutchik wheel (24 emotions)
PLUTCHIK_EMOTIONS = {
    "Joy": ["Serenity", "Joy", "Ecstasy"],
    "Trust": ["Acceptance", "Trust", "Admiration"],
    "Fear": ["Apprehension", "Fear", "Terror"],
    "Surprise": ["Distraction", "Surprise", "Amazement"],
    "Sadness": ["Pensiveness", "Sadness", "Grief"],
    "Disgust": ["Boredom", "Disgust", "Loathing"],
    "Anger": ["Annoyance", "Anger", "Rage"],
    "Anticipation": ["Interest", "Anticipation", "Vigilance"]
}

# For a user-friendly selection, all emotions in a single list with family for grouping
emotion_options = []
for family, emotions in PLUTCHIK_EMOTIONS.items():
    for emotion in emotions:
        emotion_options.append(f"{family}: {emotion}")

# --- Mood categories as sets for O(1) membership checking ---
POSITIVE_FAMILIES = {"Joy", "Trust", "Anticipation"}
NEGATIVE_FAMILIES = {"Fear", "Sadness", "Disgust", "Anger"}
NEUTRAL_FAMILIES = {"Surprise"}

# --- Session state initialization (all O(1) assignments) ---
for key, value in [
    ("logs", []),
    ("day", 1),
    ("streak", 0),
    ("max_streak", 0),
    ("reminder_sent", False)
]:
    if key not in st.session_state:
        st.session_state[key] = value

# --- Reminder if user hasn't logged today (O(1), no search) ---
today_str = datetime.date.today().isoformat()
if st.session_state.logs:
    last_entry = st.session_state.logs[-1]
    if last_entry["date"] != today_str and not st.session_state.reminder_sent:
        st.info("👋 Don’t forget to log your mood today! Consistency builds insight.")
        st.session_state.reminder_sent = True

# --- Mood logging section (all O(1) operations) ---
if st.session_state.day <= 7:
    st.header(f"Day {st.session_state.day}")
    st.markdown("**Select the emotion that best describes your current feeling:**")
    selected_emotion = st.selectbox(
        "Emotion (refer to the wheel above):",
        [""] + emotion_options,
        key=f"emotion_{st.session_state.day}"
    )
    note = st.text_area("Anything you'd like to add? (optional)", key=f"note_{st.session_state.day}")

    if st.button("Log Mood"):
        if not selected_emotion or selected_emotion.strip() == "":
            st.error("Please select an emotion from the wheel before proceeding.")
            st.stop()
        family, emotion = selected_emotion.split(":", 1)
        family = family.strip()
        emotion = emotion.strip()
        if family in POSITIVE_FAMILIES:
            mood_category = "positive"
            st.success("🌟 Great job! Keep the positivity going!")
        elif family in NEGATIVE_FAMILIES:
            mood_category = "negative"
            st.warning("Remember: It's okay to have tough days. Tomorrow is a new chance.")
        else:
            mood_category = "neutral"
            st.info("Staying neutral is part of the human experience!")

        entry = {
            "date": today_str,
            "day": st.session_state.day,
            "mood": f"{family}: {emotion}",
            "note": note,
            "age": st.session_state.demographics["age"],
            "gender": st.session_state.demographics["gender"],
            "profession": st.session_state.demographics["profession"],
            "mood_category": mood_category
        }
        st.session_state.logs.append(entry)

        # Streak logic
        if mood_category == "positive":
            st.session_state.streak += 1
            if st.session_state.streak > st.session_state.max_streak:
                st.session_state.max_streak = st.session_state.streak
        else:
            st.session_state.streak = 0

        if st.session_state.streak > 0:
            st.balloons()
            st.info(f"🔥 You're on a {st.session_state.streak}-day positive streak! Keep it up!")

        st.write("💬 *Every mood is valid. Thank you for taking care of yourself today!*")

        st.session_state.day += 1
        st.rerun()

else:
    # --- Week summary ---
    st.header("🎉 Week Complete! Here's Your Mood Journey:")
    log_df = pd.DataFrame(st.session_state.logs)
    st.dataframe(log_df[["day", "date", "mood", "note", "age", "gender", "profession", "mood_category"]])

    # O(n) but n <= 7, so effectively O(1) for stats
    mood_counts = log_df["mood"].value_counts()
    most_common = mood_counts.idxmax()
    positive_days = (log_df["mood_category"] == "positive").sum()
    negative_days = (log_df["mood_category"] == "negative").sum()
    streak = st.session_state.max_streak

    st.write(f"**Most frequent mood:** {most_common}")
    st.write(f"**Positive days:** {positive_days} / 7")
    st.write(f"**Longest positive streak:** {streak} day(s)")

    if positive_days >= 5:
        st.success("🌈 You're doing amazing! Celebrate your positive energy this week.")
    elif negative_days >= 4:
        st.warning("Be gentle with yourself – tough weeks happen. Consider reaching out to someone you trust.")
    else:
        st.info("A balanced week! Remember, all feelings are part of your journey.")

    st.write("👏 *You showed dedication by logging your mood each day. Self-awareness is the first step to self-care!*")
    st.write("#### Mood frequency chart")
    st.bar_chart(mood_counts)

    # O(n) to_csv and download, n small
    csv = log_df.to_csv(index=False).encode()
    st.download_button(
        label="Download my mood log (CSV)",
        data=csv,
        file_name='mood_log.csv',
        mime='text/csv'
    )

    # O(1) restart
    if st.button("Restart Mood Tracker"):
        for key in ["logs", "day", "streak", "max_streak", "reminder_sent", "demographics", "consent_given"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

st.markdown("---")
st.markdown("💡 *Keep checking in with yourself. Small steps build big habits!*")
