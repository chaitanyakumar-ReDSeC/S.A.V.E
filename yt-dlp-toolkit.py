import os
import shutil
import signal
import sys
import subprocess
import ctypes

# Colors
RED = '\033[91m'
WHITE = '\033[97m'
BOLD = '\033[1m'
RESET = '\033[0m'

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def check_dependency(name):
    """Checks if a command-line tool is installed."""
    return shutil.which(name) is not None

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def restart_script():
    """Restarts the current python script to refresh environment variables."""
    print(f"\n{RED}RELAUNCHING TOOLKIT TO LOAD DEPENDENCIES...{RESET}")
    os.execv(sys.executable, ['python'] + sys.argv)

def print_header(path):
    clear_screen()
    yt_status = f"{WHITE}INSTALLED" if check_dependency("yt-dlp") else f"{RED}MISSING"
    ff_status = f"{WHITE}INSTALLED" if check_dependency("ffmpeg") else f"{RED}MISSING"
    
    print(f"{RED}{BOLD}" + "="*70)
    print("""
            ╻ ╻╺┳╸   ╺┳┓╻  ┏━┓   ╺┳╸┏━┓┏━┓╻  ╻┏ ╻╺┳╸
            ┗┳┛ ┃ ╺━╸ ┃┃┃  ┣━┛╺━╸ ┃ ┃ ┃┃ ┃┃  ┣┻┓┃ ┃ 
             ╹  ╹    ╺┻┛┗━╸╹      ╹ ┗━┛┗━┛┗━╸╹ ╹╹ ╹ 
    """)
    print(f"{WHITE}                   Chaitanya Kumar Sathivada{RED}")
    print("="*70 + f"{RESET}")
    print(f"{WHITE}         {RED}STATUS{WHITE}: yt-dlp ({yt_status}{WHITE}) | ffmpeg ({ff_status}{WHITE}){RESET}")
    print("")
    print(f" Please install the dependencies in {RED}Settings [4]{WHITE} if they are {RED}MISSING{RESET}.")
    print(f"{RED}" + "-"*70 + f"{RESET}")
    print(f"{WHITE}{BOLD} SAVING TO:{RESET} {RED}{path}{RESET}")
    print("")
    print(f"{WHITE} You can {RED}change{WHITE} the download path in {RED}Settings [4]{WHITE}.")
    print(f"{RED}" + "-"*70 + f"{RESET}")

def install_dependencies():
    """Installs dependencies and automatically restarts the toolkit."""
    print(f"\n{WHITE}Requesting Administrative Privileges, Please choose '{RED}Yes{WHITE}' to continue...{RESET}")
    
    ps_command = (
        'Start-Process powershell -Verb RunAs -ArgumentList "-ExecutionPolicy", "Bypass", "-Command", '
        '\"& { Write-Host \'Installing dependencies... please wait.\' -ForegroundColor Cyan; '
        'winget install -e --id yt-dlp.yt-dlp --accept-source-agreements --accept-package-agreements; '
        'winget install -e --id yt-dlp.FFmpeg --accept-source-agreements --accept-package-agreements; }\"'
    )
    
    try:
        subprocess.run(["powershell", "-Command", ps_command])
        print(f"\n{WHITE}Installation window triggered. {RED}Wait for it to close...{RESET}")
        print("")
        input(f"{WHITE}Once the blue window disappears, press {RED}[ENTER]{WHITE} to refresh the toolkit.{RESET}")
        restart_script()
    except Exception as e:
        print(f"{RED}Please try again, Failed to launch elevation: {e}{RESET}")

def uninstall_dependencies():
    """Uninstalls dependencies and updates status in-app."""
    print(f"\n{WHITE}Requesting Administrative Privileges, Please choose '{RED}Yes{WHITE}' to continue...{RESET}")
    
    ps_command = (
        'Start-Process powershell -Verb RunAs -ArgumentList "-ExecutionPolicy", "Bypass", "-Command", '
        '\"& { Write-Host \'Uninstalling dependencies... please wait.\' -ForegroundColor Red; '
        'winget uninstall --id yt-dlp.yt-dlp; '
        'winget uninstall --id yt-dlp.FFmpeg; '
        'winget uninstall --id Gyan.FFmpeg; '
        'winget uninstall --id ffmpeg; }\"'
    )
    
    try:
        subprocess.run(["powershell", "-Command", ps_command])
        print(f"\n{WHITE}Uninstallation window triggered. {RED}Wait for it to close...{RESET}")
        print("")
        input(f"{WHITE}Once the blue window disappears, press {RED}[ENTER]{WHITE} to continue.{RESET}")
    except Exception as e:
        print(f"{RED}Failed to launch elevation: {e}{RESET}")

def get_available_qualities(url, mode):
    """Fetches available formats and returns a list of options."""
    print(f"\n{RED}FETCHING AVAILABLE QUALITIES...{RESET}")
    # -j provides JSON metadata, which is cleaner to parse than raw text
    cmd = ['yt-dlp', '-j', url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return None

        import json
        info = json.loads(result.stdout)
        formats = info.get('formats', [])
        
        options = []
        print(f"\n{WHITE}AVAILABLE QUALITIES:{RESET}")
        
        if mode == 'audio':
            # Get all audio-only streams and sort by bitrate
            audio_streams = [f for f in formats if f.get('vcodec') == 'none' and (f.get('abr') or f.get('tbr'))]
            audio_streams.sort(key=lambda x: x.get('abr', x.get('tbr', 0)), reverse=True)
            
            for i, f in enumerate(audio_streams[:10], 1):
                bitrate = f.get('abr') or f.get('tbr')
                print(f"  {RED}[{i}]{WHITE} {bitrate}kbps - {f['ext'].upper()} (ID: {f['format_id']})")
                options.append(f['format_id'])
                
        else: # Video mode
            # Filter for streams with video, unique heights, sorted descending
            seen_heights = set()
            video_streams = [f for f in formats if f.get('height') and f.get('height') not in seen_heights and seen_heights.add(f.get('height')) or True]
            video_streams = [f for f in video_streams if f.get('vcodec') != 'none']
            video_streams.sort(key=lambda x: x.get('height', 0), reverse=True)
            
            for i, f in enumerate(video_streams, 1):
                print(f"  {RED}[{i}]{WHITE} {f['height']}p - {f['ext'].upper()} {f.get('fps', '')}fps")
                options.append(f['format_id'])

        choice = input(f"\n{WHITE}Select Quality Number: {RESET}").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice)-1]
    except Exception as e:
        print(f"{RED}Error fetching qualities: {e}{RESET}")
    return None

def run_downloader():
    default_path = os.path.join(os.path.expanduser("~"), "Downloads")
    current_path = default_path

    while True:
        print_header(current_path)
        print(f"{BOLD}{RED}SELECT MODE {WHITE}by entering the option value:{RESET}\n")
        print(f"  {RED}[1]{RESET} {WHITE}Download {RED}Audio{WHITE} (MP3){RESET}")
        print(f"  {RED}[2]{RESET} {WHITE}Download {RED}Video{WHITE} (MP4/MKV){RESET}")
        print(f"  {RED}[3]{RESET} {WHITE}Download Thumbnail / Cover{RESET}")
        print(f"  {RED}[4]{RESET} {RED}Settings{RESET}")
        print(f"  {RED}[E]{RESET} {WHITE}Exit Toolkit{RESET}")
        print(f"{RED}" + "-"*70 + f"{RESET}")
        
        choice = input(f"\n{WHITE}{BOLD}Choose the {RED}MODE : {RESET}").strip().lower()

        if choice == 'e':
            break
        
        if choice == '4':
            while True:
                clear_screen()
                print(f"{RED}{BOLD}----------- SETTINGS -----------{RESET}\n")
                print(f"  {RED}[P]{RESET} {WHITE}Change Download Path{RESET}")
                print(f"  {RED}[I]{RESET} {WHITE}Install/Update Dependencies{RESET}")
                print(f"  {RED}[U]{RESET} {WHITE}Uninstall Dependencies{RESET}")
                print(f"  {RED}[B]{RESET} {WHITE}Back to Main Menu{RESET}")
                
                s_choice = input(f"\n{WHITE}Select Option: {RESET}").strip().lower()
                
                if s_choice == 'p':
                    new_path = input(f"\n{WHITE}ENTER NEW SYSTEM PATH:{RED} > {RESET}").strip()
                    if new_path and os.path.exists(new_path):
                        current_path = new_path
                        print(f"{WHITE}Path updated.{RESET}")
                    else:
                        print(f"{RED}Error: Path not found.{RESET}")
                    input("Press Enter...")
                
                elif s_choice == 'i':
                    install_dependencies()
                
                elif s_choice == 'u':
                    confirm = input(f"\n{RED}Are you sure you want to uninstall? (y/n): {RESET}").strip().lower()
                    if confirm == 'y':
                        uninstall_dependencies()
                
                elif s_choice == 'b':
                    break
            continue

        if choice not in ['1', '2', '3']:
            continue

        if not check_dependency("yt-dlp") or not check_dependency("ffmpeg"):
            print(f"\n{RED}ERROR: yt-dlp or ffmpeg not found!{RESET}")
            print("")
            print(f"{WHITE}Please go to {RED}Settings [4]{WHITE} and select {RED}Install [I]{WHITE}.{RESET}")
            input("\nPress Enter to return...")
            continue

        while True:
            mode_map = {'1': "[AUDIO MODE]", '2': "[VIDEO MODE]", '3': "[THUMBNAIL MODE]"}
            print(f"\n{RED}{BOLD}CURRENT MODE: {WHITE}{mode_map[choice]}{RESET}")
            print(f"{WHITE}Type {RED}//{WHITE} and press {RED}[ENTER]{WHITE} to go back.{RESET}")
            url = input(f"{WHITE}Paste URL: {RESET}").strip()

            if url.lower() == '//': break
            if not url: continue

            output_template = "%(playlist_title&%s/|)s%(title)s.%(ext)s"
            cmd = []

            if choice == '1':
                # 'bestaudio/best' grabs the highest quality source automatically
                cmd = [
                    'yt-dlp', 
                    '-f', 'bestaudio/best', 
                    '-x', 
                    '--audio-format', 'mp3', 
                    '--audio-quality', '0',  # '0' tells ffmpeg to use the highest VBR/quality of the source
                    '--embed-thumbnail', 
                    '--convert-thumbnails', 'jpg', 
                    '--embed-metadata', 
                    '-P', current_path, 
                    '-o', output_template, 
                    url
                ]
            
            elif choice == '2':
                selected_format = get_available_qualities(url, 'video')
                if selected_format:
                    # We use 'selected_format+ba/b' to ensure we get the best audio with the chosen video ID
                    f_selector = f"{selected_format}+ba/b"
                    
                    print(f"\n{WHITE}CHOOSE FORMAT: {RESET}")
                    print(f"{WHITE}{RED}  [A]{WHITE} MKV ({RED}Fastest{WHITE}){RESET}")
                    print(f"{WHITE}{RED}  [B]{WHITE} MP4 ({RED}Slow{WHITE}){RESET}")
                    v_choice = input(f"{WHITE}Format > {RESET}").strip().lower()
                    
                    if v_choice == 'b':
                        cmd = ['yt-dlp', '-f', f_selector, '--recode-video', 'mp4', '--embed-metadata', '-P', current_path, '-o', output_template, url]
                    else:
                        cmd = ['yt-dlp', '-f', f_selector, '--merge-output-format', 'mkv', '--embed-metadata', '-P', current_path, '-o', output_template, url]


            if cmd:
                print(f"\n{RED}----------- INITIALIZING DOWNLOAD -----------{RESET}")
                try:
                    subprocess.run(cmd)
                    print(f"\n{RED}----------- DOWNLOAD COMPLETE -----------{RESET}")
                    # Removed the input() wait here to allow instant re-prompting
                except KeyboardInterrupt:
                    print(f"\n{RED}!!! CANCELLED !!!{RESET}")
                    input("\nPress Enter to continue...")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))
    os.system("") 
    run_downloader()