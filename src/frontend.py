from __future__ import annotations

import argparse
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Sequence

import gradio as gr

from src.service import run_email_finder_service

COMPANY_HEADERS = [
    "company",
    "website",
    "emails",
    "pages_scanned",
    "pages_with_hits",
    "status",
    "error",
]

PAGE_HEADERS = [
    "company",
    "website",
    "page_url",
    "emails",
    "batch_status",
    "error",
]

ERROR_HEADERS = ["company", "website", "page_url", "error"]

APP_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

:root {
  --olostep-primary: #635bff;
  --olostep-bg: #f9fafb;
  --olostep-text: #13152b;
  --olostep-muted: #5c6370;
  --olostep-border: #dce0f0;
  --olostep-success: #0f8f5f;
  --olostep-error: #c2362b;
}

.gradio-container,
html.dark .gradio-container {
  --body-background-fill: #f9fafb !important;
  --body-background-fill-dark: #f9fafb !important;
  --body-text-color: #13152b !important;
  --body-text-color-subdued: #48506b !important;
  --background-fill-primary: #ffffff !important;
  --background-fill-secondary: #f4f6ff !important;
  --block-background-fill: #ffffff !important;
  --block-title-text-color: #171d43 !important;
  --block-label-text-color: #13152b !important;
  --block-border-color: #dce0f0 !important;
  --border-color-primary: #dce0f0 !important;
  --input-background-fill: #ffffff !important;
  --input-border-color: #ccd3eb !important;
  --input-placeholder-color: #7a839f !important;
  --button-primary-background-fill: #635bff !important;
  --button-primary-background-fill-hover: #534ae6 !important;
  --button-primary-text-color: #ffffff !important;
  --button-secondary-background-fill: #eceffd !important;
  --button-secondary-background-fill-hover: #e2e6ff !important;
  --button-secondary-text-color: #1b224d !important;
  --button-secondary-border-color: #cdd4f7 !important;
}

body, .gradio-container {
  background: radial-gradient(circle at 12% 10%, rgba(99, 91, 255, 0.09), rgba(99, 91, 255, 0) 42%), var(--olostep-bg);
  color: var(--olostep-text);
  font-family: 'IBM Plex Sans', sans-serif;
  color-scheme: light;
}

#olostep-shell {
  max-width: 1220px;
  margin: 0 auto;
  padding: 18px 20px 30px;
}

.brand-hero {
  border: 1px solid rgba(99, 91, 255, 0.32);
  border-radius: 18px;
  padding: 22px;
  background: linear-gradient(145deg, rgba(99, 91, 255, 0.2), rgba(255, 255, 255, 0.92));
  box-shadow: 0 16px 30px rgba(19, 21, 43, 0.08);
  animation: rise 240ms ease-out;
}

.brand-hero h1 {
  margin: 0;
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.9rem;
  line-height: 1.2;
  color: #111111;
}

.brand-hero p {
  margin: 10px 0 0;
  color: #2f355f;
  font-size: 0.97rem;
  font-weight: 500;
}

.zone-card {
  border: 1px solid var(--olostep-border);
  border-radius: 16px;
  padding: 14px 16px 16px;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 12px 26px rgba(19, 21, 43, 0.06);
  animation: rise 280ms ease-out;
}

.zone-title h2 {
  margin: 0 0 8px;
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.14rem;
  letter-spacing: 0.01em;
  color: #171d43;
}

.zone-card,
.zone-card label,
.zone-card .prose,
.zone-card .prose *,
.zone-card [data-testid="markdown"] * {
  color: var(--olostep-text) !important;
  opacity: 1 !important;
}

.zone-card .prose p,
.zone-card .prose li,
.zone-card [data-testid="markdown"] p,
.zone-card [data-testid="markdown"] li {
  color: #2e355d !important;
  line-height: 1.55;
}

.zone-card .prose h1,
.zone-card .prose h2,
.zone-card .prose h3,
.zone-card [data-testid="markdown"] h1,
.zone-card [data-testid="markdown"] h2,
.zone-card [data-testid="markdown"] h3 {
  color: #171d43 !important;
}

.zone-card input,
.zone-card textarea,
.zone-card [data-testid="textbox"],
.zone-card [data-testid="file-upload"],
.zone-card [data-testid="file-upload-dropzone"],
.zone-card [data-testid="dataframe"] {
  background: #ffffff !important;
  color: var(--olostep-text) !important;
  border-color: var(--olostep-border) !important;
}

#input-zone [data-testid="file-upload-dropzone"] {
  border: 1.5px dashed #b8bff0 !important;
  background: linear-gradient(180deg, #f8f9ff 0%, #ffffff 100%) !important;
}

#input-zone [data-testid="file-upload-dropzone"] * {
  color: #323b69 !important;
}

#progress-zone .prose code,
#progress-zone [data-testid="markdown"] code {
  background: #eef0ff !important;
  color: #2a2f55 !important;
}

#progress-zone [data-testid="textbox"] textarea {
  background: #f7f8ff !important;
  color: #1f264f !important;
  font-family: "SFMono-Regular", Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 0.86rem;
  line-height: 1.45;
  max-height: 220px !important;
  overflow-y: auto !important;
  white-space: pre-wrap !important;
}

#progress-zone button:not(#run-btn) {
  background: #eceffd !important;
  color: #1b224d !important;
  border: 1px solid #cdd4f7 !important;
}

#run-btn {
  background: var(--olostep-primary);
  border-color: var(--olostep-primary);
  color: #ffffff !important;
  font-weight: 600;
  box-shadow: 0 8px 18px rgba(99, 91, 255, 0.24);
}

#run-btn:hover {
  background: #534ae6 !important;
}

#results-zone [role="tablist"] button {
  color: #2a315d !important;
  background: #eff2ff !important;
  border: 1px solid #d7ddf7 !important;
}

#results-zone [role="tablist"] button[aria-selected="true"] {
  color: #ffffff !important;
  background: #635bff !important;
  border-color: #635bff !important;
}

#results-zone th {
  background: #eef1ff !important;
  color: #1b224d !important;
  font-weight: 600 !important;
}

#results-zone td {
  background: #ffffff !important;
  color: #1f264f !important;
}

#results-zone table,
#results-zone th,
#results-zone td {
  border-color: #d8def2 !important;
}

@keyframes rise {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.zone-card code,
.zone-card pre code,
.zone-card .prose code,
.zone-card [data-testid="markdown"] code {
  background: #f1f3ff !important;
  color: #000000 !important;
  padding: 2px 6px;
  border-radius: 6px;
  border: 1px solid #d8def2;
}
/* Fix file upload label */
#input-zone label,
#input-zone .wrap label,
#input-zone [data-testid="file-upload"] label {
  color: #000000 !important;
  background: transparent !important;
}

/* Fix small code tags inside markdown (website, url, domain etc.) */
.zone-card code,
.zone-card [data-testid="markdown"] code {
  background: #eef1ff !important;
  color: #000000 !important;
  border: 1px solid #d8def2;
  padding: 2px 6px;
  border-radius: 6px;
}
/* Fix labels like Company CSV and Download Output Files */
label,
.gradio-container label,
[data-testid="file-upload"] label,
[data-testid="file-download"] label {
  background: transparent !important;
  color: #000000 !important;
}

/* Fix any label badges Gradio may render */
label span {
  background: transparent !important;
  color: #000000 !important;
}

/* Fix file upload text colors - make all text white for better contrast */
#input-zone [data-testid="file-upload"] *,
#input-zone [data-testid="file-upload-dropzone"] *,
#input-zone .file-preview,
#input-zone .file-preview *,
#input-zone .file-name,
#input-zone .file-size,
#input-zone [data-testid="uploaded-file"] *,
#input-zone [data-testid="file-upload-preview"] *,
#input-zone .file-preview-part,
#input-zone .file-preview-part *,
#input-zone .file-preview__file-name,
#input-zone .file-preview__file-size,
#input-zone .file-preview__file-name *,
#input-zone .file-preview__file-size *,
#input-zone .file-preview__remove-button * {
  color: #ffffff !important;
}

/* Ensure the dropzone text is also white */
#input-zone [data-testid="file-upload-dropzone"] span,
#input-zone [data-testid="file-upload-dropzone"] p,
#input-zone [data-testid="file-upload-dropzone"] div {
  color: #ffffff !important;
}

/* Style the file preview container */
#input-zone .file-preview {
  background: #2a2f55 !important;
  border: 1px solid #4a5280 !important;
  border-radius: 8px;
  padding: 8px;
  margin-top: 8px;
}
"""


def _timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


def _summary_placeholder() -> str:
    return "\n".join(
        [
            "### Summary",
            "- Companies processed: `0`",
            "- Companies with emails: `0`",
            "- Total unique emails: `0`",
            "- Status counts: `n/a`",
        ]
    )


def _summary_markdown(summary: Dict[str, Any], output_dir: str) -> str:
    status_counts = summary.get("status_counts", {})
    if status_counts:
        status_text = ", ".join(
            f"{key}={value}" for key, value in sorted(status_counts.items())
        )
    else:
        status_text = "n/a"

    return "\n".join(
        [
            "### Summary",
            f"- Companies processed: `{summary.get('companies_processed', 0)}`",
            f"- Companies with emails: `{summary.get('companies_with_emails', 0)}`",
            f"- Total unique emails: `{summary.get('total_unique_emails', 0)}`",
            f"- Pages scanned: `{summary.get('total_pages_scanned', 0)}`",
            f"- Pages with hits: `{summary.get('total_pages_with_hits', 0)}`",
            f"- Status counts: `{status_text}`",
            f"- Output directory: `{output_dir}`",
        ]
    )


def _status_from_message(message: str) -> str:
    lowered = message.lower()
    if "pre-check" in lowered:
        return "### Status: Pre-check"
    if "mapping" in lowered or "mapped " in lowered:
        return "### Status: Mapping"
    if "batching" in lowered or "batch " in lowered:
        return "### Status: Batching"
    if "retrieving" in lowered:
        return "### Status: Retrieving"
    if "aggregating" in lowered:
        return "### Status: Aggregating"
    if "completed" in lowered:
        return "### Status: Completed"
    return "### Status: Running"


def _company_rows(items: Sequence[Dict[str, Any]]) -> List[List[Any]]:
    rows: List[List[Any]] = []
    for item in items:
        rows.append(
            [
                item.get("company", ""),
                item.get("website", ""),
                ";".join(item.get("emails", [])),
                item.get("pages_scanned", 0),
                item.get("pages_with_hits", 0),
                item.get("status", ""),
                item.get("error", ""),
            ]
        )
    return rows


def _page_rows(items: Sequence[Dict[str, Any]]) -> List[List[Any]]:
    rows: List[List[Any]] = []
    for item in items:
        rows.append(
            [
                item.get("company", ""),
                item.get("website", ""),
                item.get("page_url", ""),
                ";".join(item.get("emails", [])),
                item.get("batch_status", ""),
                item.get("error", ""),
            ]
        )
    return rows


def _error_rows(items: Sequence[Dict[str, Any]]) -> List[List[Any]]:
    rows: List[List[Any]] = []
    for item in items:
        rows.append(
            [
                item.get("company", ""),
                item.get("website", ""),
                item.get("page_url", ""),
                item.get("error", ""),
            ]
        )
    return rows


def _disable_run_button() -> gr.Button:
    return gr.Button(value="Running...", interactive=False)


def _enable_run_button() -> gr.Button:
    return gr.Button(value="Run Email Finder", interactive=True)


def _clear_results():
    return (
        "### Status: Ready",
        _summary_placeholder(),
        "",
        [],
        [],
        [],
        None,
    )


async def _run_with_stream(
    csv_file_path: str | None,
):
    logs: List[str] = []
    summary_text = _summary_placeholder()
    status_text = "### Status: Ready"

    if not csv_file_path:
        logs.append(f"{_timestamp()} | Upload a CSV file to start.")
        yield (
            "### Status: Input required",
            summary_text,
            "\n".join(logs),
            [],
            [],
            [],
            None,
        )
        return

    log_queue: asyncio.Queue[str] = asyncio.Queue()

    def on_progress(message: str) -> None:
        log_queue.put_nowait(message)

    async def runner() -> Dict[str, Any]:
        return await run_email_finder_service(
            csv_file_path=csv_file_path,
            output_dir=None,
            progress_callback=on_progress,
        )

    task = asyncio.create_task(runner())

    logs.append(f"{_timestamp()} | Starting run for: {csv_file_path}")
    yield (status_text, summary_text, "\n".join(logs), [], [], [], None)

    while not task.done() or not log_queue.empty():
        emitted = False
        while not log_queue.empty():
            message = log_queue.get_nowait()
            status_text = _status_from_message(message)
            logs.append(f"{_timestamp()} | {message}")
            emitted = True

        if emitted:
            yield (status_text, summary_text, "\n".join(logs), [], [], [], None)

        await asyncio.sleep(0.15)

    try:
        result = task.result()
    except Exception as exc:
        logs.append(f"{_timestamp()} | ERROR | {exc}")
        error_data = [["", "", "", str(exc)]]
        yield (
            "### Status: Failed",
            summary_text,
            "\n".join(logs),
            [],
            [],
            error_data,
            None,
        )
        return

    output_files = list(result.get("output_files", {}).values())
    company_data = _company_rows(result.get("company_results", []))
    page_data = _page_rows(result.get("page_results", []))
    error_data = _error_rows(result.get("errors", []))

    summary_text = _summary_markdown(
        result.get("summary", {}),
        result.get("output_dir", ""),
    )

    logs.append(f"{_timestamp()} | Completed successfully.")
    yield (
        "### Status: Completed",
        summary_text,
        "\n".join(logs),
        company_data,
        page_data,
        error_data,
        output_files,
    )


def build_demo() -> gr.Blocks:
    with gr.Blocks(title="Olostep Email Finder") as demo:
        with gr.Column(elem_id="olostep-shell"):
            gr.HTML(
                """
                <section class="brand-hero">
                  <h1>Olostep Email Finder</h1>
                  <p>Upload a company-domain CSV, run extraction with Olostep, review results, and download artifacts.</p>
                </section>
                """
            )

            with gr.Column(elem_classes=["zone-card"], elem_id="input-zone"):
                gr.HTML('<div class="zone-title"><h2>Input</h2></div>')
                csv_file = gr.File(
                    label="Company CSV",
                    file_types=[".csv"],
                    type="filepath",
                )
                gr.Markdown(
                    "Required CSV column: `website` or `url` or `domain`. "
                    "Optional company columns: `company` or `name`."
                )

            with gr.Column(elem_classes=["zone-card"], elem_id="progress-zone"):
                gr.HTML('<div class="zone-title"><h2>Run & Progress</h2></div>')
                with gr.Row():
                    run_btn = gr.Button(
                        "Run Email Finder",
                        variant="primary",
                        elem_id="run-btn",
                    )
                    clear_btn = gr.Button("Clear Results")
                with gr.Accordion("Run Details", open=False):
                    status_md = gr.Markdown("### Status: Ready")
                    summary_md = gr.Markdown(_summary_placeholder())
                    logs_box = gr.Textbox(
                        label="Progress Log",
                        lines=10,
                        max_lines=10,
                        interactive=False,
                        buttons=["copy"],
                    )

            with gr.Column(elem_classes=["zone-card"], elem_id="results-zone"):
                gr.HTML('<div class="zone-title"><h2>Results</h2></div>')
                downloads = gr.File(
                    label="Download Output Files",
                    file_count="multiple",
                )
                with gr.Tabs():
                    with gr.TabItem("Company Results"):
                        company_table = gr.Dataframe(
                            headers=COMPANY_HEADERS,
                            datatype=[
                                "str",
                                "str",
                                "str",
                                "number",
                                "number",
                                "str",
                                "str",
                            ],
                            value=[],
                            interactive=False,
                            wrap=True,
                        )
                    with gr.TabItem("Page Results"):
                        page_table = gr.Dataframe(
                            headers=PAGE_HEADERS,
                            datatype=["str", "str", "str", "str", "str", "str"],
                            value=[],
                            interactive=False,
                            wrap=True,
                        )
                    with gr.TabItem("Errors"):
                        error_table = gr.Dataframe(
                            headers=ERROR_HEADERS,
                            datatype=["str", "str", "str", "str"],
                            value=[],
                            interactive=False,
                            wrap=True,
                        )

            run_event = run_btn.click(
                fn=_disable_run_button,
                outputs=[run_btn],
                queue=False,
            )

            run_event = run_event.then(
                fn=_run_with_stream,
                inputs=[csv_file],
                outputs=[
                    status_md,
                    summary_md,
                    logs_box,
                    company_table,
                    page_table,
                    error_table,
                    downloads,
                ],
            )

            run_event.then(
                fn=_enable_run_button,
                outputs=[run_btn],
                queue=False,
            )

            clear_btn.click(
                fn=_clear_results,
                outputs=[
                    status_md,
                    summary_md,
                    logs_box,
                    company_table,
                    page_table,
                    error_table,
                    downloads,
                ],
                queue=False,
            )

    return demo


def launch_gradio(
    host: str = "127.0.0.1",
    port: int = 7860,
    share: bool = False,
) -> None:
    demo = build_demo()
    demo.queue(default_concurrency_limit=1)
    demo.launch(server_name=host, server_port=port, share=share, css=APP_CSS)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch the Olostep Gradio frontend.")
    parser.add_argument("--host", default="127.0.0.1", help="Host for Gradio server.")
    parser.add_argument(
        "--port", type=int, default=7860, help="Port for Gradio server."
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="Enable Gradio share links.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    launch_gradio(host=args.host, port=args.port, share=args.share)
