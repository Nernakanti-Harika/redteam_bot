import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from dotenv import load_dotenv

from redteam.probes import MITIGATIONS
from redteam.runner import risk_score, run, summarize
from redteam.target import make_target


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

load_dotenv()

st.set_page_config(
    page_title="Red Team Bot",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 17px;
        color: #777;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 25px;
        font-weight: 650;
        margin-top: 30px;
        margin-bottom: 15px;
    }

    .security-box {
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #ddd;
        margin-bottom: 20px;
    }

    .footer {
        text-align: center;
        color: #888;
        margin-top: 40px;
        padding: 20px;
        border-top: 1px solid #ddd;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">🛡️ Red Team Bot</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "AI Chatbot Security Testing & Vulnerability Assessment"
    "</div>",
    unsafe_allow_html=True,
)

st.info(
    "⚠️ Test only chatbots you own or have permission to test. "
    "This tool runs security probes to identify common weaknesses."
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("⚙️ Scan Configuration")

kind = st.sidebar.selectbox(
    "Target chatbot",
    [
        "Mock - weak",
        "Mock - hardened",
        "Gemini - weak",
        "Gemini - hardened",
    ],
)

st.sidebar.markdown("---")

st.sidebar.caption(
    "💡 Mock targets work offline.\n\n"
    "🤖 Gemini targets require GEMINI_API_KEY in your .env file."
)

run_scan = st.sidebar.button(
    "🚀 Run Red Team Scan",
    type="primary",
    use_container_width=True,
)


# --------------------------------------------------
# RUN SCAN
# --------------------------------------------------

if run_scan:
    try:
        with st.spinner("🔍 Running security probes..."):

            target = make_target(kind)
            df = run(target)

        st.session_state.setdefault("history", {})[kind] = df
        st.session_state["latest"] = kind

        st.success("✅ Security scan completed successfully!")

    except Exception as e:
        st.error(f"❌ Could not run scan: {e}")


# --------------------------------------------------
# INITIAL MESSAGE
# --------------------------------------------------

if "latest" not in st.session_state:

    st.markdown(
        """
        <div class="security-box">

        ### 🚀 Start a Security Scan

        Select a chatbot from the sidebar and click
        **Run Red Team Scan**.

        The scanner will test the chatbot for:

        - 🔓 Prompt Injection
        - 🧠 System Prompt Leakage
        - 🧪 Jailbreak Attempts
        - 🔐 Sensitive Data Leakage
        - ⚠️ Hallucination / Unverifiable Responses

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.stop()


# --------------------------------------------------
# LOAD RESULTS
# --------------------------------------------------

kind = st.session_state["latest"]
df = st.session_state["history"][kind]

summ = summarize(df)

score = risk_score(df)
failed_count = int((~df.passed).sum())
total_probes = len(df)
avg_latency = df.latency_s.mean()


# --------------------------------------------------
# TARGET INFORMATION
# --------------------------------------------------

st.markdown(
    f'<div class="section-title">🎯 Scan Results — {kind}</div>',
    unsafe_allow_html=True,
)


# --------------------------------------------------
# KPI METRICS
# --------------------------------------------------

c1, c2, c3 = st.columns(3)

c1.metric(
    "🛡️ Risk Score",
    f"{score:.1f}",
    help="Lower risk score is better.",
)

c2.metric(
    "❌ Failed Probes",
    f"{failed_count} / {total_probes}",
    help="Number of security tests that failed.",
)

c3.metric(
    "⚡ Average Latency",
    f"{avg_latency:.2f}s",
    help="Average chatbot response time.",
)


# --------------------------------------------------
# SECURITY STATUS
# --------------------------------------------------

if failed_count == 0:

    st.success(
        "🟢 SECURITY STATUS: No weaknesses found by this probe set. "
        "All security probes passed!"
    )

elif score < 30:

    st.warning(
        "🟡 SECURITY STATUS: Low risk. "
        "Some weaknesses were detected."
    )

else:

    st.error(
        "🔴 SECURITY STATUS: High risk. "
        "Multiple security weaknesses were detected."
    )


# --------------------------------------------------
# VULNERABILITY CHART
# --------------------------------------------------

st.markdown(
    '<div class="section-title">📊 Vulnerability Analysis</div>',
    unsafe_allow_html=True,
)

fig, ax = plt.subplots(figsize=(9, 4))

sns.barplot(
    data=summ,
    y="category",
    x="vuln_rate_%",
    color="#d9534f",
    ax=ax,
)

ax.set_xlim(0, 100)
ax.set_xlabel("Vulnerability Rate (%)")
ax.set_ylabel("")

st.pyplot(fig)


# --------------------------------------------------
# BEFORE VS AFTER
# --------------------------------------------------

hist = st.session_state["history"]

if len(hist) > 1:

    st.markdown(
        '<div class="section-title">🔄 Before vs After</div>',
        unsafe_allow_html=True,
    )

    comparison = {
        k: {
            "Risk Score": risk_score(v),
            "Failed Probes": int((~v.passed).sum()),
        }
        for k, v in hist.items()
    }

    st.table(comparison)


# --------------------------------------------------
# RESULTS TABLE
# --------------------------------------------------

st.markdown(
    '<div class="section-title">📋 Detailed Security Results</div>',
    unsafe_allow_html=True,
)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
)


# --------------------------------------------------
# DOWNLOAD REPORT
# --------------------------------------------------

st.download_button(
    label="📥 Download CSV Security Report",
    data=df.to_csv(index=False),
    file_name="redteam_security_report.csv",
    mime="text/csv",
    use_container_width=True,
)


# --------------------------------------------------
# SUGGESTED FIXES
# --------------------------------------------------

failed = summ[summ.failed > 0].category

if len(failed):

    st.markdown(
        '<div class="section-title">🔧 Suggested Fixes</div>',
        unsafe_allow_html=True,
    )

    for category in failed:

        st.warning(
            f"**{category}**\n\n"
            f"{MITIGATIONS[category]}"
        )

else:

    st.markdown(
        '<div class="section-title">🔒 Security Status</div>',
        unsafe_allow_html=True,
    )

    st.success(
        "✅ No weaknesses found by this probe set. "
        "All tested security categories passed."
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown(
    """
    <div class="footer">
        🛡️ <b>Red Team Bot</b><br>
        AI Chatbot Security Testing & Vulnerability Assessment<br>
        Built with Python • Streamlit • Pandas • Matplotlib
    </div>
    """,
    unsafe_allow_html=True,
)