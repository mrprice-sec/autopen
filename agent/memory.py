"""
Autopen Step Memory — tracks completed actions within an engagement.
Prevents the agent from repeating tools it has already run.
"""


class StepMemory:
    def __init__(self):
        self.completed_steps: list[dict] = []
        self.current_phase: str = "Recon"

    def record(self, action: str, action_input: str, observation: str):
        if not self.already_ran(action, action_input):
            self.completed_steps.append({
                "action": action,
                "input": action_input,
                "observation": observation[:200],
            })
            self._update_phase()

    def _update_phase(self):
        tools_run = [s["action"] for s in self.completed_steps]
        if any(t in tools_run for t in ["sqlmap_scan", "hydra_bruteforce", "metasploit_run"]):
            self.current_phase = "Reporting"
        elif "searchsploit_search" in tools_run:
            self.current_phase = "Exploitation"
        elif any(t in tools_run for t in ["nikto_scan", "feroxbuster_scan", "nmap_full_scan"]):
            self.current_phase = "Vulnerability Analysis"
        elif any(t in tools_run for t in ["whatweb_scan", "nmap_ping_sweep"]):
            self.current_phase = "Scanning"

    def already_ran(self, action: str, action_input: str) -> bool:
        for step in self.completed_steps:
            if step["action"] == action and step["input"].strip() == action_input.strip():
                return True
        return False

    def get_summary(self) -> str:
        if not self.completed_steps:
            return "No steps completed yet. Start with Recon phase."
        lines = [f"Current Phase: {self.current_phase}"]
        lines.append("Already completed (DO NOT repeat any of these):")
        for i, step in enumerate(self.completed_steps, 1):
            lines.append(f"  {i}. {step['action']}({step['input'][:60]}) -> done")
        return "\n".join(lines)

    def reset(self):
        self.completed_steps = []
        self.current_phase = "Recon"
