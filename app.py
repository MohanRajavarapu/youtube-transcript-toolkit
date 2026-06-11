import streamlit as st
import os
from fetcher import fetch_transcript
from cleaner import clean_transcript
from summarizer import summarize_transcript
from pipeline import run_pipeline

st.set_page_config(page_title="YouTube Transcript Toolkit", page_icon="🎬")
st.title("🎬 YouTube Transcript Toolkit")

# API Key input
api_key = st.sidebar.text_input("Anthropic API Key", type="password")
if api_key:
    os.environ["ANTHROPIC_API_KEY"] = api_key

# Video URL input
video_url = st.text_input("YouTube URL or Video ID", placeholder="https://www.youtube.com/watch?v=...")

# Mode selector
mode = st.selectbox("Summary Mode", ["brief", "detailed", "bullets", "outline"])

# Action buttons
col1, col2, col3, col4 = st.columns(4)

if col1.button("📄 Fetch"):
    with st.spinner("Fetching transcript..."):
        result = fetch_transcript(video_url)
        st.text_area("Raw Transcript", result, height=300)

if col2.button("✨ Clean"):
    with st.spinner("Cleaning with AI..."):
        result = clean_transcript(video_url)
        st.text_area("Cleaned Transcript", result, height=300)

if col3.button("📝 Summarize"):
    with st.spinner("Summarizing..."):
        result = summarize_transcript(video_url, mode=mode)
        st.markdown(result)

if col4.button("🚀 Full Pipeline"):
    with st.spinner("Running full pipeline..."):
        transcript, cleaned, summary = run_pipeline(video_url, mode=mode)
        st.subheader("Raw Transcript")
        st.text_area("", transcript, height=200)
        st.subheader("Cleaned")
        st.text_area("", cleaned, height=200)
        st.subheader("Summary")
        st.markdown(summary)
