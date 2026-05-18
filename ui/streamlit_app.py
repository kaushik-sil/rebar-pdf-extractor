from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

import sys

# Ensure project root is on sys.path so `src` package can be imported when
# running Streamlit from other working directories.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pipeline import run_extraction_pipeline

DEMO_PASSWORD = os.environ.get("DEMO_PASSWORD", "demo123")


def header_card(title: str, value: str, status: str) -> str:
        # Polished card with softer palette and status badge
        status_colors = {
                "Complete": ("#e6fff0", "#16a34a", "✅"),
                "In Progress": ("#fff8e6", "#d97706", "⏳"),
                "Skipped": ("#f3f4f6", "#6b7280", "⛔"),
        }
        bg, accent, icon = status_colors.get(status, ("#f3f4f6", "#6b7280", ""))
        return f"""
<div style='padding:18px;border-radius:14px;background:{bg};box-shadow:0 6px 18px rgba(15,23,42,0.06);border:1px solid rgba(15,23,42,0.03);'>
    <div style='display:flex;justify-content:space-between;align-items:center;'>
        <div style='max-width:78%'>
            <div style='font-size:15px;font-weight:700;color:#0f172a;margin-bottom:6px'>{title}</div>
            <div style='font-size:20px;font-weight:800;color:#04263a'>{value}</div>
        </div>
        <div style='text-align:right'>
            <div style='display:inline-block;padding:8px;border-radius:10px;background:{accent};color:white;font-weight:700'>{icon}</div>
        </div>
    </div>
    <div style='color:#334155;font-size:13px;margin-top:12px'>{status}</div>
</div>
"""


def authenticate() -> bool:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    st.sidebar.title("Demo access")
    if st.session_state.authenticated:
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            safe_rerun()
        st.sidebar.success("Authenticated")
        return True

    password = st.sidebar.text_input("Enter demo password", type="password")
    if st.sidebar.button("Login"):
        if password == DEMO_PASSWORD:
            st.session_state.authenticated = True
            safe_rerun()
        else:
            st.sidebar.error("Invalid password. Try demo123.")
    st.sidebar.info("Demo password: demo123")
    return False


def show_pipeline_summary(result: dict[str, object]) -> None:
    pipeline = result.get("pipeline", {})
    status_rows = [
        ("Upload PDF", "Ready", "Complete"),
        ("Text extraction", "Ready", "Complete"),
        ("OCR merge", "Enabled" if pipeline.get("ocr_enabled") else "Skipped", "Complete"),
        ("Parse items", "Ready", "Complete"),
        ("CSV export", "Ready", "Complete"),
    ]

    # Two-row layout for better visual balance
    first_row = st.columns([1, 1, 1])
    second_row = st.columns([1, 1, 1])
    cols = first_row + second_row
    for idx, (title, value, status) in enumerate(status_rows):
        cols[idx].markdown(header_card(title, value, status), unsafe_allow_html=True)

    # small spacer
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


def safe_rerun() -> None:
    """Attempt to rerun the Streamlit script; fall back to stopping the script if rerun API is unavailable."""
    rerun = getattr(st, "experimental_rerun", None)
    if callable(rerun):
        try:
            rerun()
            return
        except Exception:
            pass
    # Last-resort fallback: stop execution so Streamlit will re-run on next interaction
    try:
        st.stop()
    except Exception:
        # If even st.stop is unavailable, do nothing
        return


def render_result(result: dict[str, object]) -> None:
    if result["success"]:
        st.success("Extraction completed successfully.")
        st.metric("Pages processed", str(result["page_count"]))
        st.metric("Rows extracted", str(result["rows"]))
        if result["warnings"]:
            st.warning("Warnings: " + " | ".join(result["warnings"]))
        if Path(result["output_csv"]).exists():
            df = pd.read_csv(result["output_csv"])
            st.write("### Extracted CSV preview")
            st.dataframe(df.head(10))
            st.download_button(
                "Download CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name=Path(result["output_csv"]).name,
                mime="text/csv",
            )
    else:
        st.error("Extraction failed: " + "; ".join(result.get("warnings", [])))


def main() -> None:
    st.set_page_config(page_title="Rebar PDF Extractor Demo", layout="wide")
    st.title("Rebar PDF Extractor — Demo UI")

    if not authenticate():
        st.info("Please log in with the demo password to view the UI.")
        return

    tabs = st.tabs(["Pipeline", "Extraction", "Samples", "About"])

    with tabs[0]:
        st.subheader("Pipeline status")
        st.markdown(
            "This demo illustrates the core extraction workflow in a clean UI shell."
        )
        st.markdown(
            "Use the Extraction tab to run a sample PDF through the demo pipeline and review status cards."
        )
        show_pipeline_summary({"pipeline": {"ocr_enabled": True}})

    with tabs[1]:
        st.subheader("Run extraction")
        pdf_file = st.file_uploader("Upload a structural drawing PDF", type=["pdf"])
        use_ocr = st.checkbox("Enable OCR fallback", value=True)
        output_path = st.text_input("Output CSV file", "output/ui_extract.csv")
        if st.button("Start extraction"):
            if not pdf_file:
                st.error("Upload a PDF file to continue.")
            else:
                temp_dir = Path(tempfile.mkdtemp())
                temp_dir.mkdir(parents=True, exist_ok=True)
                pdf_path = temp_dir / pdf_file.name
                with open(pdf_path, "wb") as handle:
                    handle.write(pdf_file.getbuffer())

                # Run pipeline with spinner and robust error capture
                try:
                    with st.spinner("Running extraction..."):
                        result = run_extraction_pipeline(pdf_path, Path(output_path), use_ocr=use_ocr)
                    render_result(result)
                except Exception as exc:  # capture unexpected exceptions
                    import traceback

                    tb = traceback.format_exc()
                    log_dir = Path("output")
                    log_dir.mkdir(parents=True, exist_ok=True)
                    log_file = log_dir / "ui_error.log"
                    with open(log_file, "a", encoding="utf-8") as f:
                        f.write("\n---\n")
                        f.write(tb)

                    st.error("Extraction failed with an unexpected error. See log below.")
                    st.code(tb)
                    st.write(f"Log written to: {log_file}")

    with tabs[2]:
        st.subheader("Sample files")
        st.markdown(
            "Upload your own PDF or use the included sample plan in `input/sample_plan.pdf` for a quick demo."
        )
        st.markdown(
            "- Sample plan: `input/sample_plan.pdf`\n- Demo output: `output/extracted.csv`"
        )
        if st.button("Create sample plan PDF"):
            from scripts.create_sample_pdf import main as create_sample
            create_sample()
            st.success("Sample PDF generated at input/sample_plan.pdf")

    with tabs[3]:
        st.subheader("About this demo")
        st.markdown(
            "This UI is a prototype showcase for a rebar plan extraction pipeline. It is built for demo and client proposal purposes, not as a finished production app."
        )
        st.markdown(
            "#### Features included:\n" 
            "- Password gated demo UI\n" 
            "- Pipeline status cards\n" 
            "- PDF upload and extraction flow\n" 
            "- CSV preview and download\n"
        )
        st.info("Run with: streamlit run ui/streamlit_app.py")


if __name__ == "__main__":
    main()
