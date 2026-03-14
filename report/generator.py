"""
Autopen Report Generator — builds a structured Markdown report from engagement results.
"""

import json
import os
from datetime import datetime


def _sanitise_filename(target: str) -> str:
    return target.replace("http://", "").replace("https://", "").replace("/", "_").replace(":", "-")


def generate_report(target: str, mode: str, result: dict, output_dir: str = "outputs/") -> tuple[str, str]:
    """
    Generate Markdown report and JSON log from engagement result.
    Returns (md_path, json_path).
    """
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_target = _sanitise_filename(target)
    base_name = f"{safe_target}_{timestamp}"

    md_path = os.path.join(output_dir, f"{base_name}.md")
    json_path = os.path.join(output_dir, f"{base_name}.json")

    # --- Build Markdown ---
    steps = result.get("intermediate_steps", [])
    final_output = result.get("output", "No final output.")

    tool_findings = []
    for action, observation in steps:
        tool_findings.append({
            "tool": action.tool,
            "input": action.tool_input,
            "output": observation,
        })

    md = _build_markdown(target, mode, timestamp, tool_findings, final_output)

    with open(md_path, "w") as f:
        f.write(md)

    # --- Build JSON log ---
    log = {
        "target": target,
        "mode": mode,
        "timestamp": timestamp,
        "steps": [
            {
                "tool": f["tool"],
                "input": f["input"],
                "output": f["output"],
            }
            for f in tool_findings
        ],
        "final_output": final_output,
    }

    with open(json_path, "w") as f:
        json.dump(log, f, indent=2)

    return md_path, json_path


def _build_markdown(target: str, mode: str, timestamp: str, findings: list, final_output: str) -> str:
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "# Autopen Penetration Test Report",
        "",
        "---",
        "",
        "## Engagement Details",
        "",
        f"| Field | Value |",
        f"|---|---|",
        f"| Target | `{target}` |",
        f"| Mode | {mode.upper()} |",
        f"| Date | {date_str} |",
        f"| Framework | Autopen (AI-Driven) |",
        f"| Model | llama3.2:3b via Ollama |",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        final_output if final_output else "_No summary generated._",
        "",
        "---",
        "",
        "## Tool Execution Log",
        "",
    ]

    if findings:
        for i, f in enumerate(findings, 1):
            lines += [
                f"### {i}. `{f['tool']}`",
                "",
                f"**Input:** `{f['input']}`",
                "",
                "**Output:**",
                "",
                "```",
                str(f['output'])[:1500],
                "```",
                "",
            ]
    else:
        lines.append("_No tool executions recorded._")

    lines += [
        "---",
        "",
        "## Disclaimer",
        "",
        "> This report was generated autonomously by Autopen. All testing was conducted with authorisation.",
        "> The user is solely responsible for ensuring legal scope compliance.",
        "",
    ]

    return "\n".join(lines)
