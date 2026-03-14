"""
Autopen Agent Core — LangChain ReAct agent powered by qwen2.5:3b via Ollama.
Includes short-term step memory and CTF mode.
"""

from langchain.agents import create_react_agent
from langchain.agents.agent import AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain_ollama import OllamaLLM
from agent.tools import get_tools
from agent.memory import StepMemory


PENTEST_PROMPT = (
    "You are Autopen, a fully autonomous penetration testing AI running on Kali Linux.\n"
    "You are performing a professional penetration test with full authorisation.\n"
    "\n"
    "STRICT RULES:\n"
    "1. Extract domain only (no http://) for: whois_lookup, theharvester_scan, subfinder_scan.\n"
    "2. Use full URL (http://...) for: whatweb_scan, feroxbuster_scan, nikto_scan, sqlmap_scan.\n"
    "3. Use hostname or IP ONLY (no http://) for: nmap_full_scan, nmap_ping_sweep.\n"
    "4. If a tool fails or returns nothing — skip it, move on immediately.\n"
    "5. NEVER run the same Action + Action Input twice. Check completed steps.\n"
    "6. Work through phases IN ORDER: Recon -> Scanning -> Vuln Analysis -> Exploitation -> Report.\n"
    "7. After scanning, run searchsploit_search on every service/version found.\n"
    "8. After vuln analysis, attempt at least one exploitation tool.\n"
    "9. Write Final Answer only after exploitation phase.\n"
    "\n"
    "COMPLETED STEPS (DO NOT REPEAT):\n"
    "{memory}\n"
    "\n"
    "AVAILABLE TOOLS:\n"
    "{tools}\n"
    "\n"
    "FORMAT:\n"
    "Thought: <reasoning>\n"
    "Action: <tool from [{tool_names}]>\n"
    "Action Input: <input>\n"
    "Observation: <result>\n"
    "\n"
    "When done:\n"
    "Thought: All phases complete.\n"
    "Final Answer: <structured pentest report>\n"
    "\n"
    "Task: {input}\n"
    "{agent_scratchpad}"
)

CTF_PROMPT = (
    "You are a CTF player in a Capture The Flag competition.\n"
    "Your ONLY goal is to find the hidden flag on the target.\n"
    "Flag format is typically FLAG{{...}}, CTF{{...}}, or HTB{{...}}.\n"
    "The flag ONLY appears after successful exploitation.\n"
    "\n"
    "MINDSET: Be aggressive. Chain vulnerabilities. Try everything.\n"
    "\n"
    "ATTACK ORDER:\n"
    "1. whatweb_scan — fingerprint the target\n"
    "2. nmap_full_scan — discover open ports and services\n"
    "3. feroxbuster_scan + nikto_scan — find all entry points\n"
    "4. searchsploit_search — find exploits for every service found\n"
    "5. sqlmap_scan — test ALL URL parameters for SQLi\n"
    "6. hydra_bruteforce — brute force any login pages found\n"
    "7. metasploit_run — exploit any known CVEs\n"
    "8. linpeas_run — if shell obtained, hunt flag on filesystem\n"
    "\n"
    "RULES:\n"
    "1. Use hostname/IP only for nmap_full_scan (no http://).\n"
    "2. Use full URL for whatweb_scan, feroxbuster_scan, nikto_scan, sqlmap_scan.\n"
    "3. NEVER repeat same Action + Action Input.\n"
    "4. If tool fails — immediately try a different attack vector.\n"
    "\n"
    "COMPLETED STEPS (DO NOT REPEAT):\n"
    "{memory}\n"
    "\n"
    "AVAILABLE TOOLS:\n"
    "{tools}\n"
    "\n"
    "FORMAT:\n"
    "Thought: <reasoning>\n"
    "Action: <tool from [{tool_names}]>\n"
    "Action Input: <input>\n"
    "Observation: <result>\n"
    "\n"
    "When flag found or all options exhausted:\n"
    "Thought: Done.\n"
    "Final Answer: <flag + full attack summary>\n"
    "\n"
    "Task: {input}\n"
    "{agent_scratchpad}"
)


_memory = StepMemory()


def _wrap_tools_with_memory(tools: list, memory: StepMemory) -> list:
    """Wrap each tool to block repeats and record steps live."""
    wrapped = []
    for tool in tools:
        original_func = tool.func

        def make_wrapper(func, name):
            def wrapper(input_str: str) -> str:
                if memory.already_ran(name, input_str):
                    return f"[{name}] Already ran with this input. Skipping — try a different tool or input."
                result = func(input_str)
                memory.record(name, input_str, result)
                return result
            return wrapper

        wrapped.append(Tool(
            name=tool.name,
            func=make_wrapper(original_func, tool.name),
            description=tool.description,
        ))
    return wrapped


def build_agent(config: dict, verbose: bool = False, mode: str = "web") -> AgentExecutor:
    model_name = config["model"]["name"]
    base_url = config["model"]["base_url"]
    max_iterations = config["agent"]["max_iterations"]
    temperature = 0.4 if mode == "ctf" else 0.1

    llm = OllamaLLM(
        model=model_name,
        base_url=base_url,
        temperature=temperature,
    )

    raw_tools = get_tools()
    tools = _wrap_tools_with_memory(raw_tools, _memory)

    prompt_template = CTF_PROMPT if mode == "ctf" else PENTEST_PROMPT
    prompt = PromptTemplate.from_template(prompt_template)
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=verbose,
        max_iterations=max_iterations,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )

    return executor


def run_engagement(executor: AgentExecutor, target: str, mode: str) -> dict:
    global _memory
    _memory.reset()

    if mode == "ctf":
        task = (
            f"Target: {target}\n"
            "Mode: CTF CHALLENGE\n"
            "\n"
            "Find and capture the hidden flag on this target.\n"
            "The flag only appears after successful exploitation.\n"
            "Be aggressive. Chain attacks. Do not stop until flag is found."
        )
    else:
        mode_context = {
            "web": (
                "WEB APPLICATION target.\n"
                "Order: whois_lookup -> theharvester_scan -> whatweb_scan -> "
                "nmap_full_scan -> nikto_scan -> feroxbuster_scan -> "
                "searchsploit_search -> sqlmap_scan -> Final Answer."
            ),
            "network": (
                "NETWORK/HOST target.\n"
                "Order: nmap_ping_sweep -> nmap_full_scan -> searchsploit_search -> "
                "hydra_bruteforce or metasploit_run -> Final Answer."
            ),
            "full": (
                "FULL engagement (web + network).\n"
                "Order: whois_lookup -> nmap_ping_sweep -> nmap_full_scan -> "
                "whatweb_scan -> nikto_scan -> feroxbuster_scan -> "
                "searchsploit_search -> sqlmap_scan -> Final Answer."
            ),
        }
        task = (
            f"Target: {target}\n"
            f"Mode: {mode.upper()}\n"
            f"{mode_context.get(mode, '')}\n"
            "\n"
            "Execute ALL phases. Do not stop until Final Answer is written.\n"
            "Skip any tool that fails and move to the next."
        )

    result = executor.invoke({
        "input": task,
        "memory": _memory.get_summary(),
    })

    return result
