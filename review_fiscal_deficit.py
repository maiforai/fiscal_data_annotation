import streamlit as st
import json
import pandas as pd
import os
from datetime import datetime

# ---------- CONFIG ----------
st.set_page_config(page_title="Fiscal Deficit Review", layout="wide")
DATA_PATH = "../fiscal_deficit_results_sampled.json"
SAVE_PATH = "../fiscal_deficit_review_results.csv"

# ---------- CUSTOM CSS ----------
st.markdown(
    """
    <style>
    body {
        background-color: #ffffff;
        color: #000000;
    }
    .stButton>button {
        margin: 5px;
    }
    .stProgress > div > div {
        background-color: #4CAF50 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- LOAD DATA ----------
with open(DATA_PATH, "r") as f:
    data = json.load(f)

# ---------- SESSION STATE INIT ----------
if "fiscal_index" not in st.session_state:
    st.session_state["fiscal_index"] = 0
if "submitted" not in st.session_state:
    st.session_state["submitted"] = False

# ---------- SCORING INSTRUCTION (ALWAYS VISIBLE) ----------
st.markdown(
    """
    ### 📌 Scoring Rules (Focus on **FUTURE** Fiscal Deficit Direction)
    > 1 = **VERY NEGATIVE**: Clear indication that fiscal deficit will increase significantly  
    > 2 = **SOMEWHAT NEGATIVE**: Any hint that fiscal deficit might increase (even slightly) or stay above target levels  
    > 3 = **NEUTRAL**: No clear prediction about future fiscal deficit, or suggests deficit will stay at current levels  
    > 4 = **SOMEWHAT POSITIVE**: Indication that fiscal deficit will decrease slightly or gradually  
    > 5 = **VERY POSITIVE**: Strong indication that fiscal deficit will decrease significantly or move to a surplus  
    ➡️ **PREDICTED FUTURE DIRECTION of fiscal deficit, not just current levels**
    """,
    unsafe_allow_html=True,
)

# ---------- NAVIGATION BUTTONS ----------
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("⬅️ Prev"):
        if st.session_state.fiscal_index > 0:
            st.session_state.submitted = False
            st.session_state.fiscal_index -= 1

with col2:
    if st.button("➡️ Next"):
        if st.session_state.fiscal_index < len(data) - 1:
            st.session_state.submitted = False
            st.session_state.fiscal_index += 1

# ---------- GET CURRENT ARTICLE ----------
index = st.session_state.fiscal_index
if index >= len(data):
    st.success("🎉 All articles reviewed!")
    st.balloons()
    st.stop()
article = data[index]

# ---------- DISPLAY PROGRESS ----------
st.markdown(f"### Progress: Article {index + 1} of {len(data)}")
progress = (index + 1) / len(data)
st.progress(progress)

# ---------- DISPLAY ARTICLE METADATA ----------
st.markdown(f"### 📰 {article['headline']}")
st.markdown(f"**🗓 Date:** {article['date']}  |  **🌐 Source:** {article['source']}")
st.markdown(f"[🔗 Original Link]({article['url']})", unsafe_allow_html=True)
st.markdown("---")

# ---------- DISPLAY FIELDS ----------
st.subheader("🧼 Cleaned Article:")
st.write(article["cleaned_article"])
st.subheader("🔢 Model Score (Predicted Deficit Score):")
st.markdown(
    f"<div style='font-size: 24px; font-weight: bold;'>{article.get('deficit_score', 'N/A')}</div>",
    unsafe_allow_html=True,
)
st.subheader("🧠 Model's Deficit Analysis:")
st.write(article.get("deficit_analysis", "N/A"))

# ---------- FORM FOR INPUT ----------
with st.form(key="review_form", clear_on_submit=True):
    st.subheader("📝 Reviewer Feedback")
    approval = st.radio("Do you approve the model's deficit score?", ["Approve", "Reject"], horizontal=True)
    comments = st.text_area("💬 Suggestions or Reviewer Comments")
    correct_score = st.selectbox(
        "🛠️ If you rejected the model’s score, what should it have been?",
        options=["NA (no issue)", 1, 2, 3, 4, 5],
        index=0,
        format_func=lambda x: str(x),
    )
    submitted = st.form_submit_button("📥 Submit Review")
    if submitted:
        review_entry = {
            "date": article["date"],
            "headline": article["headline"],
            "url": article["url"],
            "source": article["source"],
            "cleaned_article": article["cleaned_article"],
            "deficit_score": article.get("deficit_score", ""),
            "deficit_analysis": article.get("deficit_analysis", ""),
            "review_decision": approval,
            "review_comments": comments,
            "corrected_score": correct_score,
            "review_time": datetime.now().isoformat(),
            "review_user": "REVIEWER_NAME",
        }
        # Save to CSV
        if os.path.exists(SAVE_PATH):
            df = pd.read_csv(SAVE_PATH)
            df = pd.concat([df, pd.DataFrame([review_entry])], ignore_index=True)
        else:
            df = pd.DataFrame([review_entry])
        df.to_csv(SAVE_PATH, index=False)
        st.session_state.submitted = True
        st.success("✅ Review saved successfully!")
        st.rerun()

# ---------- SUBMISSION INDICATION ----------
if st.session_state.submitted:
    st.success("✅ You have successfully submitted this review!")
else:
    st.warning("⚠️ You have not submitted a review for this article yet.")
    #st.rerun()  # Replace st.experimental_rerun() with st.rerun()