"""
Autopen Tools — all pentest tools wrapped as LangChain Tool objects.
Each tool runs a subprocess command and returns summarised output.
"""

import subprocess
from langchain_core.tools import Tool
from agent.summariser import summarise


def _run(cmd: str, tool_name: str = "", timeout: int = 180) -> str:
    """Execute a shell command and return summarised output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = result.stdout + result.stderr
        return summarise(output.strip(), tool_name) or f"[{tool_name}] Command completed with no output."
    except subprocess.TimeoutExpired:
        return f"[{tool_name}] Timed out. Skipping."
    except Exception as e:
        return f"[{tool_name}] Error: {str(e)}"


def whois_lookup(target: str) -> str:
    return _run(f"whois {target}", "whois", timeout=30)

def theharvester_scan(target: str) -> str:
    return _run(f"theHarvester -d {target} -l 50 -b duckduckgo,crtsh", "theHarvester", timeout=120)

def subfinder_scan(target: str) -> str:
    return _run(f"subfinder -d {target} -silent -timeout 30", "subfinder", timeout=60)

def nmap_ping_sweep(target: str) -> str:
    return _run(f"nmap -sn {target}", "nmap-ping", timeout=60)

def nmap_full_scan(target: str) -> str:
    return _run(f"nmap -sV -sC --open -T4 --top-ports 1000 {target}", "nmap-full", timeout=180)

def whatweb_scan(target: str) -> str:
    return _run(f"whatweb --color=never {target}", "whatweb", timeout=60)

def feroxbuster_scan(target: str) -> str:
    return _run(
        f"feroxbuster -u {target} -w /usr/share/wordlists/dirb/common.txt "
        f"--silent --no-recursion -t 20 --timeout 10 --time-limit 3m",
        "feroxbuster", timeout=240
    )

def nikto_scan(target: str) -> str:
    return _run(f"nikto -h {target} -nointeractive -maxtime 120", "nikto", timeout=180)

def searchsploit_search(query: str) -> str:
    return _run(f"searchsploit {query} --colour=false", "searchsploit", timeout=30)

def sqlmap_scan(target: str) -> str:
    return _run(
        f"sqlmap -u {target} --batch --level=2 --risk=1 --timeout=30 --output-dir=/tmp/sqlmap",
        "sqlmap", timeout=300
    )

def hydra_bruteforce(args: str) -> str:
    parts = args.strip().split()
    if len(parts) < 4:
        return "[hydra] Invalid args. Expected: <target> <service> <userlist> <passlist>"
    target, service, userlist, passlist = parts[0], parts[1], parts[2], parts[3]
    return _run(f"hydra -L {userlist} -P {passlist} {target} {service} -t 4 -f", "hydra", timeout=300)

def metasploit_run(module_args: str) -> str:
    cmd = f'msfconsole -q -x "{module_args}; exit"'
    return _run(cmd, "metasploit", timeout=300)

def linpeas_run(target_info: str) -> str:
    return _run("bash /tmp/linpeas.sh 2>/dev/null", "linpeas", timeout=120)

def netcat_connect(args: str) -> str:
    parts = args.strip().split()
    if len(parts) < 2:
        return "[netcat] Invalid args. Expected: <ip> <port>"
    ip, port = parts[0], parts[1]
    return _run(f"nc -nv -w 3 {ip} {port}", "netcat", timeout=10)


def get_tools() -> list:
    return [
        Tool(name="whois_lookup", func=whois_lookup,
             description="Domain registration lookup. Input: domain only e.g. example.com (NO http://)."),
        Tool(name="theharvester_scan", func=theharvester_scan,
             description="OSINT gathering — emails, subdomains, IPs. Input: domain only e.g. example.com (NO http://)."),
        Tool(name="subfinder_scan", func=subfinder_scan,
             description="Passive subdomain enumeration. Input: domain only e.g. example.com (NO http://)."),
        Tool(name="nmap_ping_sweep", func=nmap_ping_sweep,
             description="Ping sweep to discover live hosts. Input: IP or CIDR e.g. 192.168.1.0/24."),
        Tool(name="nmap_full_scan", func=nmap_full_scan,
             description="Port scan with service detection — top 1000 ports. Input: hostname or IP ONLY, no http:// e.g. testphp.vulnweb.com or 192.168.1.1."),
        Tool(name="whatweb_scan", func=whatweb_scan,
             description="Web technology fingerprinting. Input: full URL e.g. http://target.com."),
        Tool(name="feroxbuster_scan", func=feroxbuster_scan,
             description="Fast directory and file brute forcing. Input: full URL e.g. http://target.com."),
        Tool(name="nikto_scan", func=nikto_scan,
             description="Web vulnerability scanner. Input: full URL e.g. http://target.com."),
        Tool(name="searchsploit_search", func=searchsploit_search,
             description="Search Exploit-DB offline for known exploits. Input: service name and version e.g. 'nginx 1.19' or 'PHP 5.6'."),
        Tool(name="sqlmap_scan", func=sqlmap_scan,
             description="SQL injection testing. Input: full URL with parameters e.g. http://target.com/page?id=1."),
        Tool(name="hydra_bruteforce", func=hydra_bruteforce,
             description="Brute force logins. Input: '<target> <service> <userlist> <passlist>'."),
        Tool(name="metasploit_run", func=metasploit_run,
             description="Run Metasploit exploit. Input: semicolon-separated msfconsole commands."),
        Tool(name="linpeas_run", func=linpeas_run,
             description="Local privilege escalation enumeration. Input: any string."),
        Tool(name="netcat_connect", func=netcat_connect,
             description="Banner grabbing with netcat. Input: '<ip> <port>'."),
    ]
