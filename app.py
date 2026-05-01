import streamlit as st
import streamlit.components.v1 as components
from graph import run_stratumai
from email_sender import send_report_email, generate_pdf
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.units import mm
from io import BytesIO
import threading
import schedule
import time
from datetime import time as dt_time
import re
import os
import hashlib
from datetime import datetime, timedelta

@st.cache_data(ttl=21600)  # 6 hours
def cached_stratumai(company):
    return run_stratumai(company)

# ─────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────
st.set_page_config(
    page_title="StratumAI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────
# CSS
# ─────────────────────────────────────────
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
        background-color: #0A0A0F;
        color: #E2E8F0;
    }

    #MainMenu, header, footer {visibility: hidden;}

    .hero-title {
        font-size: 4.5rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(270deg, #00F2FE, #4FACFE, #7F00FF, #E100FF);
        background-size: 800% 800%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-shift 8s ease infinite;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    .hero-subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #94A3B8;
        margin-top: -10px;
        margin-bottom: 40px;
        letter-spacing: 1px;
    }
    @keyframes gradient-shift {
        0%   { background-position: 0%   50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0%   50%; }
    }
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5) !important;
        padding: 20px;
    }
    button[kind="primary"] {
        background: linear-gradient(90deg, #4FACFE 0%, #00F2FE 100%);
        border: none;
        color: #000 !important;
        font-weight: 700;
        border-radius: 8px;
        box-shadow: 0 0 15px rgba(79, 172, 254, 0.4);
        transition: all 0.3s ease-in-out;
    }
    button[kind="primary"]:hover {
        transform: scale(1.02);
        box-shadow: 0 0 30px rgba(79, 172, 254, 0.8);
    }
    button[kind="secondary"] {
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        background: rgba(255, 255, 255, 0.02);
        transition: all 0.2s ease;
    }
    button[kind="secondary"]:hover {
        border-color: #4FACFE;
        color: #4FACFE;
        background: rgba(79, 172, 254, 0.05);
    }
    .stTextInput input {
        background-color: rgba(0, 0, 0, 0.5) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px;
    }
    .stTextInput input:focus {
        border-color: #4FACFE !important;
        box-shadow: 0 0 10px rgba(79, 172, 254, 0.3) !important;
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #E2E8F0;
        margin-bottom: 4px;
    }
    .section-sub {
        font-size: 0.85rem;
        color: #64748B;
        margin-bottom: 16px;
    }
    </style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# SCHEDULER BACKGROUND THREAD
# Runs schedule jobs without blocking UI
# ─────────────────────────────────────────
def run_scheduler_thread():
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start background scheduler thread once
if "scheduler_thread_started" not in st.session_state:
    t = threading.Thread(target=run_scheduler_thread, daemon=True)
    t.start()
    st.session_state["scheduler_thread_started"] = True

# Track scheduled jobs in session state
if "scheduled_jobs" not in st.session_state:
    st.session_state["scheduled_jobs"] = []


# ─────────────────────────────────────────
# HERO SECTION
# ─────────────────────────────────────────
st.markdown("<div class='hero-title'>StratumAI</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-subtitle'>Multi-Agent Competitive Intelligence System</div>",
            unsafe_allow_html=True)

# ─────────────────────────────────────────
# TABS — Analysis | Scheduler
# ─────────────────────────────────────────
tab1, tab2 = st.tabs(["🔍 Analyze Company", "📅 Weekly Scheduler"])


# ════════════════════════════════════════
# TAB 1 — ANALYZE
# ════════════════════════════════════════
with tab1:
    spacer1, main_col, spacer2 = st.columns([0.5, 3, 0.5])

    with main_col:
        with st.container(border=True):

            with st.form(key="search_form", clear_on_submit=False):
                col_input, col_btn = st.columns([6.5, 3.5])
                with col_input:
                    company_name = st.text_input(
                        "Company",
                        placeholder="Enter target (e.g., Zepto, Salesforce)...",
                        label_visibility="collapsed"
                    )
                with col_btn:
                    analyze_button = st.form_submit_button(
                        "Initialize Agents ⚡",
                        use_container_width=True,
                        type="primary"
                    )

            st.markdown(
                "<center><small style='color:#64748B;'>POPULAR TARGETS</small></center><br>",
                unsafe_allow_html=True
            )
            q1, q2, q3, q4, q5 = st.columns(5)
            if q1.button("Zepto",      use_container_width=True): st.session_state["quick"] = "Zepto"
            if q2.button("Razorpay",   use_container_width=True): st.session_state["quick"] = "Razorpay"
            if q3.button("Flipkart",   use_container_width=True): st.session_state["quick"] = "Flipkart"
            if q4.button("CRED",       use_container_width=True): st.session_state["quick"] = "CRED"
            if q5.button("Salesforce", use_container_width=True): st.session_state["quick"] = "Salesforce"

    # Resolve company
    quick_company = st.session_state.get("quick", None)
    final_company = quick_company if quick_company else company_name
    existing_report = st.session_state.get("report")
    existing_company = st.session_state.get("final_company")
    if "quick" in st.session_state:
        del st.session_state["quick"]

    # ── AGENT EXECUTION ──
    if analyze_button or quick_company or (existing_report and final_company == existing_company):
        if not final_company.strip():
            st.error("⚠️ Target designation required.")
        else:
            # Autoscroll
            # st.html("""
            #     <script>
            #         function scrollToAnchor() {
            #             // Use document directly instead of window.parent.document
            #             var anchor = document.getElementById('intercept-anchor');
            #             if (anchor) {
            #                 anchor.scrollIntoView({ behavior: 'smooth', block: 'start' });
            #             } else {
            #                 setTimeout(scrollToAnchor, 200);
            #             }
            #         }
            #         setTimeout(scrollToAnchor, 300);
            #     </script>
            # """)
            components.html("""
                <script>
                    function scrollToAnchor() {
                        var anchor = window.parent.document.getElementById('intercept-anchor');
                        if (anchor) {
                            anchor.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        } else {
                            setTimeout(scrollToAnchor, 200);
                        }
                    }
                    setTimeout(scrollToAnchor, 300);
                </script>
            """, height=0)

            st.markdown("<div id='intercept-anchor'></div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown(f"### 📡 Intercepting Data for: **{final_company.upper()}**")
                st.divider()

                s1, s2, s3, s4 = st.columns(4)
                with s1: research_status  = st.status("🔍 Research Agent",  expanded=False)
                with s2: sentiment_status = st.status("💬 Sentiment Agent", expanded=False)
                with s3: financial_status = st.status("💰 Financial Agent", expanded=False)
                with s4: writer_status    = st.status("✍️ Writer Agent",    expanded=False)

                success = False

                if analyze_button or quick_company:
                    with st.spinner("Neural network processing..."):
                        try:
                            start_time = time.time()
                            report = cached_stratumai(final_company)

                            st.session_state["report"] = report
                            st.session_state["final_company"] = final_company
                            time_taken = round(time.time() - start_time, 2)

                            research_status.update( label="🔍 Research Agent [OK]",  state="complete")
                            sentiment_status.update(label="💬 Sentiment Agent [OK]", state="complete")
                            financial_status.update(label="💰 Financial Agent [OK]", state="complete")
                            writer_status.update(   label="✍️ Writer Agent [OK]",    state="complete")

                            success = True
                        except Exception as e:
                            research_status.update( label="🔍 Research Agent [ERR]",  state="error")
                            sentiment_status.update(label="💬 Sentiment Agent [ERR]", state="error")
                            financial_status.update(label="💰 Financial Agent [ERR]", state="error")
                            writer_status.update(   label="✍️ Writer Agent [ERR]",    state="error")
                            st.error(f"System Failure: {str(e)}")
                else:
                    report = existing_report
                    final_company = existing_company
                    success = True
                    time_taken = 0

                # with st.spinner("Neural network processing..."):
                #     try:
                #         start_time = time.time()
                #         report     = run_stratumai(final_company)
                #         st.session_state["report"]         = report
                #         st.session_state["final_company"]  = final_company 
                #         success = True
                #         time_taken = round(time.time() - start_time, 2)

                #         research_status.update( label="🔍 Research Agent [OK]",  state="complete")
                #         sentiment_status.update(label="💬 Sentiment Agent [OK]", state="complete")
                #         financial_status.update(label="💰 Financial Agent [OK]", state="complete")
                #         writer_status.update(   label="✍️ Writer Agent [OK]",    state="complete")
                #         success = True

                #     except Exception as e:
                #         research_status.update( label="🔍 Research Agent [ERR]",  state="error")
                #         sentiment_status.update(label="💬 Sentiment Agent [ERR]", state="error")
                #         financial_status.update(label="💰 Financial Agent [ERR]", state="error")
                #         writer_status.update(   label="✍️ Writer Agent [ERR]",    state="error")
                #         st.error(f"System Failure: {str(e)}")

            # ── RESULTS ──
            if success:
                st.markdown("<br>", unsafe_allow_html=True)

                with st.container(border=True):
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Target Acquired", final_company)
                    m2.metric("Nodes Active",    "4 Agents")
                    m3.metric("Latency",         f"{time_taken}s")

                    st.divider()
                    st.markdown("## 📑 Intelligence Brief")
                    st.markdown(report)
                    st.divider()

                    st.markdown("<div class='section-header'>📤 Export or Send Report</div>",
                                unsafe_allow_html=True)
                    st.markdown("<div class='section-sub'>Download the report or email it directly to yourself</div>",
                                unsafe_allow_html=True)

                    # Row 1 — Downloads
                    st.download_button(
                        label="📥 Download as PDF",
                        data=generate_pdf(final_company, report),
                        file_name=f"{final_company.lower()}_intel.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        type="primary"
                    )
                    st.markdown("<br>", unsafe_allow_html=True)

                    # Row 2 — Email to myself
                    with st.container(border=True):
                        st.markdown("**📧 Email this report to yourself**")
                        st.caption("Enter your email and hit Send — you'll receive the full report with PDF attached")

                        with st.form(key="email_form"):
                            email_col, send_col = st.columns([3, 1])
                            with email_col:
                                recipient_email = st.text_input(
                                    "Your email",
                                    placeholder="your@email.com",
                                    label_visibility="collapsed"
                                )
                            with send_col:
                                send_btn = st.form_submit_button(
                                    "Send 📨",
                                    use_container_width=True,
                                    type="primary"
                                )

                        if send_btn:
                            saved_report   = st.session_state.get("report")
                            saved_company  = st.session_state.get("final_company")

                            if not recipient_email.strip():
                                st.error("Please enter your email address.")
                            elif not re.match(r"[^@]+@[^@]+\.[^@]+", recipient_email):
                                st.error("Please enter a valid email address.")
                            elif not saved_report or not saved_company:
                                st.error("No report found. Please run the analysis first.")
                            else:
                                with st.spinner("Connecting to mail server and sending..."):
                                    try:
                                        send_report_email(saved_company, saved_report, recipient_email)
                                        st.success(f"✅ Report sent to {recipient_email}!")
                                        st.toast("📧 Email sent successfully!")
                                    except Exception as e:
                                        st.error(f"Failed to send: {str(e)}")
                                        st.exception(e)


# ════════════════════════════════════════
# TAB 2 — SCHEDULER
# ════════════════════════════════════════
with tab2:
    spacer1, sched_col, spacer2 = st.columns([0.5, 3, 0.5])

    with sched_col:
        st.markdown("<br>", unsafe_allow_html=True)

        # ── Setup form ──
        with st.container(border=True):
            st.markdown("<div class='section-header'>⚙️ Configure Weekly Reports</div>",
                        unsafe_allow_html=True)
            st.markdown("<div class='section-sub'>Set it once — every Monday at 9am you get a full intelligence brief in your inbox</div>",
                        unsafe_allow_html=True)

            with st.form(key="scheduler_form"):
                companies_input = st.text_input(
                    "Companies to track (comma separated)",
                    placeholder="Zepto, Razorpay, Flipkart, CRED...",
                    help="Add as many companies as you want"
                )
                recipient_sched = st.text_input(
                    "Send weekly reports to",
                    placeholder="your@email.com"
                )
                schedule_day = st.selectbox(
                    "Send every",
                    ["Monday", "Tuesday", "Wednesday",
                     "Thursday", "Friday", "Saturday", "Sunday"]
                )
                schedule_time = st.time_input(
                    "At what time",
                    value=dt_time(9, 0)
                )

                schedule_btn = st.form_submit_button(
                    "📅 Activate Weekly Scheduler",
                    use_container_width=True,
                    type="primary"
                )

            if schedule_btn:
                if not companies_input.strip():
                    st.error("Please enter at least one company.")
                elif not recipient_sched.strip() or "@" not in recipient_sched:
                    st.error("Please enter a valid email address.")
                else:
                    companies_list = [c.strip() for c in companies_input.split(",") if c.strip()]
                    time_str = f"{schedule_time.hour:02d}:{schedule_time.minute:02d}"

                    # Build the job function
                    def weekly_job(companies=companies_list, recipient=recipient_sched):
                        for company in companies:
                            try:
                                report = cached_stratumai(company)
                                send_report_email(company, report, recipient)
                                time.sleep(10)
                            except Exception as e:
                                print(f"Scheduler error for {company}: {e}")

                    # Schedule it
                    day_map = {
                        "Monday":    schedule.every().monday,
                        "Tuesday":   schedule.every().tuesday,
                        "Wednesday": schedule.every().wednesday,
                        "Thursday":  schedule.every().thursday,
                        "Friday":    schedule.every().friday,
                        "Saturday":  schedule.every().saturday,
                        "Sunday":    schedule.every().sunday,
                    }
                    day_map[schedule_day].at(time_str).do(weekly_job)

                    # Save to session state for display
                    job_info = {
                        "companies": companies_list,
                        "recipient": recipient_sched,
                        "day":       schedule_day,
                        "time":      time_str,
                        "next_run":  str(schedule.next_run())
                    }
                    st.session_state["scheduled_jobs"].append(job_info)
                    st.success(f"✅ Scheduler activated! Reports will be sent every {schedule_day} at {time_str}")

        # ── Active jobs display ──
        if st.session_state["scheduled_jobs"]:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown("<div class='section-header'>📋 Active Schedules</div>",
                            unsafe_allow_html=True)
                st.markdown("<div class='section-sub'>Running in the background automatically</div>",
                            unsafe_allow_html=True)

                for i, job in enumerate(st.session_state["scheduled_jobs"]):
                    with st.container(border=True):
                        info_col, del_col = st.columns([5, 1])

                        with info_col:
                            # Smaller text instead of st.metric
                            st.markdown(f"""
                                <div style='font-size:0.78rem;color:#94A3B8;line-height:2'>
                                    🏢 <b style='color:#E2E8F0'>{', '.join(job['companies'])}</b><br>
                                    📅 Every <b style='color:#E2E8F0'>{job['day']}</b> at <b style='color:#E2E8F0'>{job['time']}</b><br>
                                    📧 Sending to <b style='color:#4FACFE'>{job['recipient']}</b><br>
                                    ⏰ Next run: <span style='color:#64748B'>{job['next_run']}</span>
                                </div>
                            """, unsafe_allow_html=True)

                        with del_col:
                            if st.button(
                                "🗑️ Delete",
                                key=f"del_{i}",
                                use_container_width=True
                            ):
                                st.session_state["scheduled_jobs"].pop(i)
                                st.rerun()

        else:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown("""
                    <div style='text-align:center;padding:40px;color:#64748B'>
                        <div style='font-size:3rem'>📭</div>
                        <div style='font-size:1.1rem;margin-top:12px'>No active schedules</div>
                        <div style='font-size:0.85rem;margin-top:6px'>Configure one above to start receiving weekly briefs</div>
                    </div>
                """, unsafe_allow_html=True)

        # ── Send now button ──
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<div class='section-header'>🚀 Send All Reports Right Now</div>",
                        unsafe_allow_html=True)
            st.markdown("<div class='section-sub'>Don't wait for Monday — trigger all scheduled reports instantly</div>",
                        unsafe_allow_html=True)

            send_now_btn = st.button(
                "⚡ Run All Scheduled Reports Now",
                use_container_width=True,
                type="primary",
                disabled=len(st.session_state["scheduled_jobs"]) == 0
            )

            if send_now_btn:
                for job in st.session_state["scheduled_jobs"]:
                    for company in job["companies"]:
                        with st.spinner(f"Processing {company}..."):
                            try:
                                report = cached_stratumai(company)
                                send_report_email(company, report, job["recipient"])
                                st.success(f"✅ {company} report sent to {job['recipient']}")
                                time.sleep(10)
                            except Exception as e:
                                st.error(f"❌ Failed for {company}: {str(e)}")

# ─────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────
st.divider()
st.caption("🧠StratumAI — Built with LangGraph multi-agent architecture")