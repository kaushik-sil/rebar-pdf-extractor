from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from src.pipeline import run_extraction_pipeline

DEMO_PASSWORD = os.environ.get("DEMO_PASSWORD", "demo123")


def header_card(title: str, value: str, status: str) -> str:
    color = "#d1f7dd" if status == "Complete" else "#fff3cd"
    icon = "✅" if status == "Complete" else "⏳"
    return f"""
<div style='padding:20px;border-radius:18px;background:{color};box-shadow:0 8px 24px rgba(0,0,0,0.08);'>
  <div style='display:flex;justify-content:space-between;align-items:center;'>
    <div>
      <h4 style='margin:0'>{title}</h4>
      <p style='margin:0;font-size:22px;font-weight:700'>{value}</p>
    </div>
    <div style='font-size:24px'>{icon}</div>
  </div>
  <div style='color:#3d3d3d;font-size:14px;margin-top:10px'>{status}</div>
</div>
"""


def authenticate() -> bool:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    st.sidebar.title("Demo access")
    if st.session_state.authenticated:
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.experimental_rerun()
        st.sidebar.success("Authenticated")
        return True

    password = st.sidebar.text_input("Enter demo password", type="password")
    if st.sidebar.button("Login"):
        if password == DEMO_PASSWORD:
            st.session_state.authenticated = True
            st.experimental_rerun()
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

    cols = st.columns(3)
    for idx, (title, value, status) in enumerate(status_rows):
        cols[idx % 3].markdown(header_card(title, value, status), unsafe_allow_html=True)


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
                result = run_extraction_pipeline(pdf_path, Path(output_path), use_ocr=use_ocr)
                render_result(result)

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
