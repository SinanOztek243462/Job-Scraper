import threading
import time
import datetime
import database as db
from utils.scrape_runner import run_scrape_for_profile

_SCANNER_STARTED = False

def _scanner_loop():
    while True:
        try:
            configs = db.get_all_loadout_configs()
            now = datetime.datetime.now()
            
            for name, cfg in configs.items():
                if cfg.get("auto_scan", 0):
                    interval_minutes = cfg.get("auto_scan_interval", 60)
                    last_scan_str = cfg.get("last_scan_time")
                    
                    should_scan = False
                    if not last_scan_str:
                        should_scan = True
                    else:
                        try:
                            # SQLite CURRENT_TIMESTAMP is UTC. Since we use Python datetime.now(), 
                            # we might have a timezone offset, but for simple interval checking 
                            # it's usually fine if we just compare the raw strings or parse them.
                            # Better: let's just parse it directly.
                            last_scan = datetime.datetime.strptime(last_scan_str, "%Y-%m-%d %H:%M:%S")
                            delta = datetime.datetime.utcnow() - last_scan # CURRENT_TIMESTAMP is UTC
                            if delta.total_seconds() >= interval_minutes * 60:
                                should_scan = True
                        except ValueError:
                            should_scan = True
                            
                    if should_scan:
                        print(f"[AutoScanner] Starting background scan for profile: {name}")
                        try:
                            saved = run_scrape_for_profile(name, show_ui=False)
                            print(f"[AutoScanner] Finished. Saved {saved} new jobs for {name}.")
                        except Exception as inner_e:
                            print(f"[AutoScanner] Failed to scrape {name}: {inner_e}")
                        finally:
                            db.update_last_scan_time(name)
                        
                        # Wait 15 seconds before scanning another profile to be polite
                        time.sleep(15)
                        
        except Exception as e:
            print(f"[AutoScanner] Error in main loop: {e}")
            
        # Sleep for 5 minutes before checking all profiles again
        time.sleep(300)

def start_auto_scanner():
    global _SCANNER_STARTED
    if not _SCANNER_STARTED:
        t = threading.Thread(target=_scanner_loop, daemon=True)
        t.start()
        _SCANNER_STARTED = True
        print("[AutoScanner] Daemon thread started.")
