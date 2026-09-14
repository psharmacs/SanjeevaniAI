import streamlit as st
import pandas as pd
import time

from simulator import HeartRateSimulator
from validator import HeartRateValidator
from processor import HeartRateProcessor
from analyzer import HeartRateAnalyzer
from alert_manager import HeartRateAlertManager


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Sanjeevani AI",
    page_icon="❤️",
    layout="wide"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .title {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: gray;
        margin-bottom: 25px;
    }

    .status {
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 20px;
    }

    .normal {
        background-color: #d4edda;
        color: #155724;
    }

    .watch {
        background-color: #fff3cd;
        color: #856404;
    }

    .alert {
        background-color: #f8d7da;
        color: #721c24;
    }

    .artifact {
        background-color: #e2e3e5;
        color: #383d41;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="title">❤️ SANJEEVANI AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Continuous Heart Rate Monitoring System'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "running" not in st.session_state:

    st.session_state.running = False


if "history" not in st.session_state:

    st.session_state.history = []


if "system_initialized" not in st.session_state:

    st.session_state.system_initialized = False


# ============================================================
# INITIALIZE SYSTEM
# ============================================================

if not st.session_state.system_initialized:

    st.session_state.simulator = HeartRateSimulator(
        interval=1
    )

    st.session_state.validator = HeartRateValidator()

    st.session_state.processor = HeartRateProcessor(
        history_size=12,
        artifact_jump=25
    )

    st.session_state.analyzer = HeartRateAnalyzer(
        watch_threshold=90,
        alert_threshold=100,
        sustained_readings=4,
        trend_window=4,
        trend_change_threshold=2
    )

    st.session_state.alert_manager = HeartRateAlertManager(
        cooldown_seconds=30
    )

    st.session_state.system_initialized = True


# ============================================================
# CONTROL BUTTONS
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:

    if st.button(
        "▶️ START MONITORING",
        use_container_width=True
    ):

        st.session_state.running = True


with col2:

    if st.button(
        "⏹️ STOP",
        use_container_width=True
    ):

        st.session_state.running = False


with col3:

    if st.button(
        "🔄 RESET",
        use_container_width=True
    ):

        st.session_state.running = False

        st.session_state.history = []

        st.session_state.simulator = (
            HeartRateSimulator(
                interval=1
            )
        )

        st.session_state.processor = (
            HeartRateProcessor(
                history_size=12,
                artifact_jump=25
            )
        )

        st.session_state.alert_manager = (
            HeartRateAlertManager(
                cooldown_seconds=30
            )
        )

        st.rerun()


# ============================================================
# SYSTEM STATUS
# ============================================================

if st.session_state.running:

    st.success(
        "🟢 Monitoring is running"
    )

else:

    st.info(
        "⚪ Monitoring is stopped"
    )


# ============================================================
# PLACEHOLDERS
# ============================================================

status_placeholder = st.empty()

metrics_placeholder = st.empty()

chart_placeholder = st.empty()

details_placeholder = st.empty()


# ============================================================
# PROCESS READING
# ============================================================

def process_reading(reading):

    timestamp = reading["timestamp"]

    heart_rate = reading["heart_rate"]

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    validation = (
        st.session_state.validator.validate_reading(
            {
                "timestamp": timestamp,
                "heart_rate": heart_rate
            }
        )
    )

    # --------------------------------------------------------
    # INVALID
    # --------------------------------------------------------

    if not validation["valid"]:

        analysis = {
            "status": "NO_DATA",
            "reason": validation["reason"]
        }

        alert = (
            st.session_state.alert_manager.handle(
                analysis
            )
        )

        return {
            "reading": reading,
            "validation": validation,
            "processor": None,
            "analyzer": analysis,
            "alert": alert
        }

    # --------------------------------------------------------
    # PROCESSOR
    # --------------------------------------------------------

    processed = (
        st.session_state.processor.process(
            heart_rate
        )
    )

    # --------------------------------------------------------
    # ANALYZER
    # --------------------------------------------------------

    analysis = (
        st.session_state.analyzer.analyze(
            processed
        )
    )

    # --------------------------------------------------------
    # ALERT MANAGER
    # --------------------------------------------------------

    alert = (
        st.session_state.alert_manager.handle(
            analysis
        )
    )

    return {
        "reading": reading,
        "validation": validation,
        "processor": processed,
        "analyzer": analysis,
        "alert": alert
    }


# ============================================================
# DISPLAY RESULT
# ============================================================

def display_result(result):

    reading = result["reading"]

    processor = result["processor"]

    analyzer = result["analyzer"]

    alert = result["alert"]

    hr = reading["heart_rate"]

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    status = analyzer["status"]

    if processor is not None:

        if processor["artifact"]:

            status_class = "artifact"

            status_text = "⚠️ SENSOR ARTIFACT"

        elif status == "ALERT":

            status_class = "alert"

            status_text = "🚨 ALERT"

        elif status == "WATCH":

            status_class = "watch"

            status_text = "⚠️ WATCH"

        else:

            status_class = "normal"

            status_text = "✅ NORMAL"

    else:

        status_class = "artifact"

        status_text = "⚠️ NO DATA"

    status_placeholder.markdown(
        f"""
        <div class="status {status_class}">
            {status_text}
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    if processor is not None:

        c1, c2, c3, c4, c5 = (
            metrics_placeholder.columns(5)
        )

        c1.metric(
            "❤️ Heart Rate",
            f"{hr} BPM"
        )

        c2.metric(
            "📈 Smoothed HR",
            f"{processor['smoothed_hr']} BPM"
        )

        c3.metric(
            "📊 Average HR",
            f"{processor['average_hr']} BPM"
        )

        c4.metric(
            "Trend",
            processor["trend"]
        )

        c5.metric(
            "Priority",
            alert["priority"]
        )

    # --------------------------------------------------------
    # CHART
    # --------------------------------------------------------

    if len(st.session_state.history) > 0:

        chart_rows = []

        for item in st.session_state.history:

            chart_rows.append(
                {
                    "Time": item["reading"]["timestamp"],
                    "Heart Rate": item["reading"]["heart_rate"]
                }
            )

        df = pd.DataFrame(
            chart_rows
        )

        df["Time"] = pd.to_datetime(
            df["Time"]
        )

        df = df.set_index(
            "Time"
        )

        chart_placeholder.line_chart(
            df["Heart Rate"]
        )

    # --------------------------------------------------------
    # DETAILS
    # --------------------------------------------------------

    with details_placeholder.container():

        left, right = st.columns(2)

        with left:

            st.subheader(
                "🔍 Processing"
            )

            st.write(
                f"**Timestamp:** "
                f"{reading['timestamp']}"
            )

            st.write(
                f"**Validation:** "
                f"{result['validation']['valid']}"
            )

            st.write(
                f"**Validation Reason:** "
                f"{result['validation']['reason']}"
            )

            if processor is not None:

                st.write(
                    f"**Accepted:** "
                    f"{processor['accepted']}"
                )

                st.write(
                    f"**Artifact:** "
                    f"{processor['artifact']}"
                )

                st.write(
                    f"**Trend:** "
                    f"{processor['trend']}"
                )

        with right:

            st.subheader(
                "🚨 Analysis"
            )

            st.write(
                f"**Status:** "
                f"{analyzer['status']}"
            )

            st.write(
                f"**Reason:** "
                f"{analyzer['reason']}"
            )

            st.write(
                f"**Action:** "
                f"{alert['action']}"
            )

            st.write(
                f"**Priority:** "
                f"{alert['priority']}"
            )

            st.write(
                f"**Notification:** "
                f"{alert['notification']}"
            )


# ============================================================
# CONTINUOUS MONITORING
# ============================================================

if st.session_state.running:

    # --------------------------------------------------------
    # Get ONE new reading
    # --------------------------------------------------------

    reading = (
        st.session_state.simulator.generate_reading()
    )

    # --------------------------------------------------------
    # Send reading through entire system
    # --------------------------------------------------------

    result = process_reading(
        reading
    )

    # --------------------------------------------------------
    # Store result
    # --------------------------------------------------------

    st.session_state.history.append(
        result
    )

    # Keep dashboard history manageable

    if len(st.session_state.history) > 60:

        st.session_state.history = (
            st.session_state.history[-60:]
        )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    display_result(
        result
    )

    # --------------------------------------------------------
    # Wait
    # --------------------------------------------------------

    time.sleep(1)

    # --------------------------------------------------------
    # Refresh dashboard
    # --------------------------------------------------------

    st.rerun()


# ============================================================
# LAST RESULT
# ============================================================

elif len(st.session_state.history) > 0:

    display_result(
        st.session_state.history[-1]
    )


# ============================================================
# PIPELINE
# ============================================================

st.markdown("---")

st.subheader(
    "🔄 Monitoring Pipeline"
)

st.code(
    """
Simulator
    ↓
Raw Heart Rate
    ↓
Validator
    ↓
Processor
    ↓
Artifact Detection + Smoothing
    ↓
Analyzer
    ↓
Trend + Sustained HR Analysis
    ↓
Alert Manager
    ↓
Streamlit Dashboard
""",
    language="text"
)


# ============================================================
# DISCLAIMER
# ============================================================

st.markdown("---")

st.caption(
    "Sanjeevani AI • Continuous Simulation Mode • "
    "Simulation data only — not medical advice."
)