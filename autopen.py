#!/usr/bin/env python3
"""
Autopen — Fully Autonomous AI-Driven Penetration Testing Framework
Final Year Project | Mr Price

Usage:
    autopen.py --target <target> --mode <web|network|full|ctf> [--verbose]
"""

import argparse
import sys
import yaml
from rich.console import Console
from rich.panel import Panel

from agent.core import build_agent, run_engagement
from report.generator import generate_report

console = Console()

BANNER = """
 █████╗ ██╗   ██╗████████╗ ██████╗ ██████╗ ███████╗███╗   ██╗
██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗██╔══██╗██╔════╝████╗  ██║
███████║██║   ██║   ██║   ██║   ██║██████╔╝█████╗  ██╔██╗ ██║
██╔══██║██║   ██║   ██║   ██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║
██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║     ███████╗██║ ╚████║
╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝
        Autonomous AI Penetration Testing Framework
        Powered by qwen2.5:3b | LangChain | Ollama
"""

MODE_DESCRIPTIONS = {
    "web":     "[cyan]Web Application Pentest[/cyan] — Recon, scanning, web vuln exploitation",
    "network": "[cyan]Network Pentest[/cyan]         — Host discovery, port scan, service exploitation",
    "full":    "[cyan]Full Engagement[/cyan]          — Web + Network combined",
    "ctf":     "[bold red]CTF Mode[/bold red]                 — Aggressive flag-hunting, max exploitation",
}


def load_config(path: str) -> dict:
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        console.print(f"[red][!] Config file not found: {path}[/red]")
        sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Autopen — Autonomous AI Penetration Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Modes:\n"
            "  web      Standard web application pentest\n"
            "  network  Network/host pentest\n"
            "  full     Web + network combined\n"
            "  ctf      Aggressive CTF flag-hunting mode\n"
        )
    )
    parser.add_argument("--target", required=True,
                        help="Target IP, domain, URL, or CIDR range")
    parser.add_argument("--mode", required=True,
                        choices=["web", "network", "full", "ctf"],
                        help="Engagement mode")
    parser.add_argument("--verbose", action="store_true",
                        help="Show agent reasoning live")
    parser.add_argument("--config", default="config.yaml",
                        help="Path to config file (default: config.yaml)")
    return parser.parse_args()


def main():
    args = parse_args()

    console.print(f"[bold cyan]{BANNER}[/bold cyan]")

    config = load_config(args.config)
    verbose = args.verbose or config["agent"].get("verbose", False)

    mode_label = MODE_DESCRIPTIONS.get(args.mode, args.mode.upper())

    # CTF mode gets a red warning panel
    if args.mode == "ctf":
        console.print(Panel(
            "[bold red]WARNING: CTF MODE ACTIVE[/bold red]\n"
            "Agent will use aggressive exploitation techniques.\n"
            "Only use against targets you own or have explicit permission to test.",
            border_style="red"
        ))

    console.print(Panel(
        f"[bold]Target:[/bold] {args.target}\n"
        f"[bold]Mode:[/bold]   {mode_label}\n"
        f"[bold]Model:[/bold]  {config['model']['name']}\n"
        f"[bold]Verbose:[/bold] {verbose}",
        title="[bold green]Engagement Started[/bold green]",
        border_style="green"
    ))

    console.print("\n[yellow][*] Building agent...[/yellow]")

    try:
        executor = build_agent(config, verbose=verbose, mode=args.mode)
    except Exception as e:
        console.print(f"[red][!] Failed to build agent: {e}[/red]")
        sys.exit(1)

    console.print("[yellow][*] Agent ready. Starting engagement...[/yellow]\n")

    try:
        result = run_engagement(executor, args.target, args.mode)
    except KeyboardInterrupt:
        console.print("\n[red][!] Engagement interrupted by user.[/red]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red][!] Engagement failed: {e}[/red]")
        sys.exit(1)

    console.print("\n[green][+] Engagement complete. Generating report...[/green]")

    output_dir = config["output"]["dir"]
    md_path, json_path = generate_report(args.target, args.mode, result, output_dir)

    console.print(Panel(
        f"[bold green]Markdown Report:[/bold green] {md_path}\n"
        f"[bold green]JSON Log:[/bold green]        {json_path}",
        title="[bold green]Reports Saved[/bold green]",
        border_style="green"
    ))


if __name__ == "__main__":
    main()
