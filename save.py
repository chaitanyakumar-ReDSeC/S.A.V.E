"""
S.A.V.E (Stream Audio Video Extractor)
--------------------------------------
A professional-grade command-line utility designed to streamline the 
extraction and downloading of media content from web streams. 

Author: Chaitanya Kumar Sathivada
"""

import os
import shutil
import signal
import sys
import subprocess
import json
import time

# --- COLOR PALETTE ---
RED = '\033[91m'
WHITE = '\033[97m'
CYAN = '\033[96m' 
GREEN = '\033[92m'
GRAY = '\033[90m'
BOLD = '\033[1m'
RESET = '\033[0m'

def check_dependency(name):
    """Verifies if a specific system tool is installed and available in PATH."""
    return shutil.which(name) is not None

def verify_dependencies():
    """Validates presence of core tools; redirects to settings if missing."""
    if not check_dependency("yt-dlp") or not check_dependency("ffmpeg"):
        print(f"\n{RED}{BOLD}!!{RESET} {RED}CRITICAL: Dependencies (yt-dlp/ffmpeg) not found.{RESET}")
        print(f"{GRAY}Redirecting to System Configuration...{RESET}")
        time.sleep(2)
        return False
    return True

def clear_screen():
    """Clears the console output for a cleaner UI experience."""
    os.system('cls' if os.name == 'nt' else 'clear')

def render_ui(status, path):
    """Renders the S.A.V.E branded UI with status information."""
    clear_screen()
    yt_stat = f"{GREEN}READY" if check_dependency("yt-dlp") else f"{RED}MISSING"
    ff_stat = f"{GREEN}READY" if check_dependency("ffmpeg") else f"{RED}MISSING"
    
    # Split the status string to color the dynamic parts
    # Assumes format: "Mode | Value | Value"
    parts = status.split(" | ")
    colored_status = f"{WHITE}{parts[0]}"
    for part in parts[1:]:
        colored_status += f"{WHITE} | {GREEN}{part}"
    
    print(f"{RED}{BOLD}")
    print(" ╔══════════════════════════════════════════════════════════════════╗")
    print(" ║              ███████╗    █████╗   ██╗   ██╗  ███████╗            ║")
    print(" ║              ██╔════╝   ██╔══██╗  ██║   ██║  ██╔════╝            ║")
    print(" ║              ███████╗   ███████║  ██║   ██║  █████╗              ║")
    print(" ║              ╚════██║   ██╔══██║  ╚██╗ ██╔╝  ██╔══╝              ║")
    print(" ║              ███████║██╗██║  ██║██╗╚████╔╝██╗███████╗            ║")
    print(" ║              ╚══════╝╚═╝╚═╝  ╚═╝╚═╝ ╚═══╝ ╚═╝╚══════╝            ║")
    print(" ║                                                                  ║")
    print(" ║                  (Stream Audio Video Extractor)                  ║")
    print(" ║                                                                  ║")
    print(f" ║{RESET}{WHITE}                Credits: Chaitanya Kumar Sathivada                {RED}{BOLD}║")
    print(f" ║{RESET}{WHITE}            GitHub: https://github.com/ChaitanyaKumarS2403        {RED}{BOLD}║")
    print(" ╚══════════════════════════════════════════════════════════════════╝")
    print(f"{RESET}")
    print(f"{RED}" + "="*70 + f"{RESET}")
    print(f"{GRAY} PATH:    {WHITE}{path}")
    print(f"{GRAY} MODE:    {colored_status}{RESET}")
    print(f"{GRAY} MODULES: {WHITE}yt-dlp ({yt_stat}{WHITE}) | ffmpeg ({ff_stat}{WHITE})\n")

def invalid_msg():
    """Handles and notifies user of invalid menu selection inputs."""
    print(f"\n {RED}>> INVALID INPUT. PRESS ENTER TO RETURN. <<{RESET}")
    input()

def run_cmd(ps_script, check=True):
    """Executes PowerShell commands as a subprocess."""
    subprocess.run(["powershell", "-Command", ps_script], check=check)

def install_dependencies():
    """Triggers elevated PowerShell to install required dependencies via winget."""
    print(f"\n {CYAN}>> Initializing Dependency Deployment...{RESET}")
    script = (
        'Start-Process powershell -Verb RunAs -Wait -ArgumentList "-ExecutionPolicy", "Bypass", "-Command", '
        '\"& { winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements; '
        'winget install -e --id yt-dlp.yt-dlp --accept-source-agreements --accept-package-agreements; }\"'
    )
    run_cmd(script)
    os.execv(sys.executable, ['python'] + sys.argv)

def update_dependencies():
    """Updates existing dependencies to their latest versions."""
    script = 'winget upgrade --id Gyan.FFmpeg; winget upgrade --id yt-dlp.yt-dlp'
    run_cmd(script, check=False)
    input(f"\n {CYAN}>> Update complete. Press Enter to proceed.{RESET}")

def uninstall_dependencies():
    """Removes all installed dependencies from the system."""
    script = 'winget uninstall --id yt-dlp.yt-dlp; winget uninstall --id Gyan.FFmpeg; winget uninstall --id yt-dlp.FFmpeg'
    run_cmd(script)
    os.execv(sys.executable, ['python'] + sys.argv)

def get_available_qualities(url, mode='video'):
    """Queries stream metadata to list available resolutions and formats."""
    print(f"\n {CYAN}>> Fetching manifest data...{RESET}")
    try:
        result = subprocess.run(['yt-dlp', '-j', '--no-warnings', url], capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            print(f"\n {RED}!! ERROR: {result.stderr.splitlines()[0]}{RESET}")
            return None
        
        info = json.loads(result.stdout)
        formats = info.get('formats', [])
        options = []
        
        if mode == 'video':
            video_streams = sorted([f for f in formats if f.get('height') and f.get('vcodec') != 'none'], 
                                   key=lambda x: x['height'], reverse=True)
            seen = set()
            unique = [f for f in video_streams if f['height'] not in seen and not seen.add(f['height'])]
            for i, f in enumerate(unique[:10], 1):
                print(f" {GRAY}[{i}]{WHITE} {f['height']}p - {f['ext'].upper()}")
                options.append(f['format_id'])
        
        choice = input(f"\n {CYAN}>> Select index (// to back): {RESET}")
        if choice == '//': return None
        return options[int(choice)-1] if choice.isdigit() and 1 <= int(choice) <= len(options) else None
    except Exception as e:
        print(f"\n {RED}!! Error: {e}{RESET}")
        return None

def run_downloader():
    """Main application loop managing user navigation and download execution."""
    current_path = os.path.join(os.path.expanduser("~"), "Downloads")
    template = "%(playlist_title&%s/|)s%(title)s.%(ext)s"

    while True:
        render_ui("IDLE", current_path)
        print(f" {BOLD}MAIN MENU{RESET}")
        print(f" {GRAY}├─ [1] Audio Extraction\n ├─ [2] Video Extraction\n ├─ [3] System Settings\n └─ [E] Exit")
        choice = input(f"\n {CYAN}>> Choice: {RESET}").lower()
        
        if choice == 'e': break
        elif choice == '1':
            if not verify_dependencies(): choice = '3'
            else:
                fmt_in = input(f" {GRAY}Select Format [1] MP3  [2] WAV  [3] M4A  [//] Back\n {CYAN}>> {RESET}")
                if fmt_in == '//': continue
                if fmt_in not in ['1', '2', '3']: invalid_msg(); continue
                fmt = 'wav' if fmt_in == '2' else ('m4a' if fmt_in == '3' else 'mp3')
                render_ui(f"Audio Mode | Format: {fmt.upper()}", current_path)
                while True:
                    url = input(f" {CYAN}URL (// to back): {RESET}")
                    if url == '//': break
                    
                    cmd = ['yt-dlp', '-x', '--audio-format', fmt, '--add-metadata']
                    if fmt in ['mp3', 'm4a']: cmd.append('--embed-thumbnail')
                    cmd.extend(['-P', current_path, '-o', template, url])
                    
                    res = subprocess.run(cmd)
                    status = f"{GREEN}SUCCESS" if res.returncode == 0 else f"{RED}FAILURE"
                    print(f"\n {status}{RESET}")
        
        elif choice == '2':
            if not verify_dependencies(): choice = '3'
            else:
                ext_in = input(f" {GRAY}Select Container [1] MKV  [2] MP4  [//] Back\n {CYAN}>> {RESET}")
                if ext_in == '//': continue
                if ext_in not in ['1', '2']: invalid_msg(); continue
                
                meth_in = input(f" {GRAY}Select Method [1] Fetch-Quality  [2] Default (1080p)  [//] Back\n {CYAN}>> {RESET}")
                if meth_in == '//': continue
                if meth_in not in ['1', '2']: invalid_msg(); continue
                
                ext, method = ('mp4' if ext_in == '2' else 'mkv'), ('Default (1080p)' if meth_in == '2' else 'FetchQuality')
                render_ui(f"Video Mode | {ext.upper()} | {method}", current_path)
                while True:
                    url = input(f" {CYAN}URL (// to back): {RESET}")
                    if url == '//': break
                    
                    f_sel = "bv*[height<=1080]+ba/b" if method == 'Default (1080p)' else None
                    if not f_sel:
                        format_id = get_available_qualities(url, 'video')
                        if not format_id: continue
                        f_sel = f"{format_id}+ba/b"
                    
                    if f_sel:
                        cmd = ['yt-dlp', '-f', f_sel, '--add-metadata', '--embed-thumbnail', '-P', current_path, '-o', template]
                        cmd += ['--recode-video', 'mp4'] if ext == 'mp4' else ['--merge-output-format', 'mkv']
                        res = subprocess.run(cmd + [url])
                        status = f"{GREEN}SUCCESS" if res.returncode == 0 else f"{RED}FAILURE"
                        print(f"\n {status}{RESET}")
        
        if choice == '3':
            while True:
                render_ui("SYSTEM SETTINGS", current_path)
                print(f" {BOLD}SETTINGS MENU{RESET}")
                print(f" {GRAY}├─ [1] Change Path\n ├─ [2] Install/Reinstall Modules\n ├─ [3] Uninstall Modules\n ├─ [4] Check for Updates\n └─ [//] Back")
                s = input(f"\n {CYAN}>> Option: {RESET}").lower()
                if s == '//': break
                elif s == '1': current_path = input(f" {CYAN}>> New Path: {RESET}"); break
                elif s == '2': install_dependencies()
                elif s == '3': uninstall_dependencies()
                elif s == '4': update_dependencies(); break
                else: invalid_msg()
        elif choice not in ['1', '2', '3', '//']: invalid_msg()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))
    run_downloader()