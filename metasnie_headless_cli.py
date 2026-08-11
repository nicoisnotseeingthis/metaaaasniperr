#!/usr/bin/env python3
"""
METASNIE HEADLESS CLI - FULL LOGGING VERSION
Runs without GUI. Shows every name checked in logs.
"""

import argparse
import asyncio
import aiohttp
import json
import os
import sys
import time
import threading
import random
from urllib.parse import urlencode
import re
import uuid

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG LOADING
# ─────────────────────────────────────────────────────────────────────────────

def load_config_from_env():
    """Load config from environment variables (for GitHub Actions)."""
    return {
        "concurrency": int(os.getenv("CONCURRENCY", 500)),
        "loop_mode": os.getenv("LOOP_MODE", "true").lower() == "true",
        "snipe_mode": os.getenv("SNIPE_MODE", "true").lower() == "true",
        "webhook_enabled": os.getenv("WEBHOOK_ENABLED", "true").lower() == "true",
        "webhook_url": os.getenv("WEBHOOK_URL", ""),
        "selected_list": os.getenv("NAMES_LIST", "lists/names.txt"),
        "timeout_total": float(os.getenv("TIMEOUT_TOTAL", 0.5)),
        "timeout_connect": float(os.getenv("TIMEOUT_CONNECT", 0.1)),
    }

def load_config_from_file(path):
    """Load config from JSON file."""
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return {}

def load_creds():
    """Load credentials from creds/creds.json."""
    try:
        with open("creds/creds.json") as f:
            return json.load(f)
    except:
        return []

def load_names(path):
    """Load names from file."""
    try:
        with open(path) as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

# ─────────────────────────────────────────────────────────────────────────────
# PROXY ROTATION
# ─────────────────────────────────────────────────────────────────────────────

class ProxyRotator:
    """Rotates through proxies to avoid rate limiting."""
    
    def __init__(self, proxy_string):
        """
        proxy_string: comma-separated list or newline-separated
        "http://user:pass@host:port,http://..."
        """
        if not proxy_string:
            self.proxies = [None]  # Direct connection
        else:
            proxies = [p.strip() for p in proxy_string.replace('\n', ',').split(',') if p.strip()]
            # Convert to full proxy URL format if needed
            self.proxies = [
                p if p.startswith('http') else f'http://{p}' 
                for p in proxies
            ]
        
        self.index = 0
    
    def get_next(self):
        """Get next proxy in rotation."""
        proxy = self.proxies[self.index % len(self.proxies)]
        self.index += 1
        return proxy

# ─────────────────────────────────────────────────────────────────────────────
# FAST CHECKER (NO GUI) - WITH DETAILED LOGGING
# ─────────────────────────────────────────────────────────────────────────────

class HeadlessChecker:
    """Fast async checker without GUI - shows every check."""
    
    def __init__(self, cfg, proxies=None):
        self.cfg = cfg
        self.proxy_rotator = ProxyRotator(proxies) if proxies else ProxyRotator("")
        self.running = False
        self.paused = False
        self._cache = set()
        self._found = 0
        self._total_checks = 0
        self._sniper = None
    
    def set_sniper(self, sniper):
        """Set the sniper pool (for auto-claiming)."""
        self._sniper = sniper
    
    async def run(self, names):
        """Run checker on names."""
        self.running = True
        self._cache.clear()
        self._found = 0
        self._total_checks = 0
        
        print(f"[INFO] Starting checker with {len(names)} names")
        print(f"[INFO] Snipe mode: {self.cfg.get('snipe_mode')}")
        print()
        
        tc = float(self.cfg.get("timeout_total", 0.5))
        cc = float(self.cfg.get("timeout_connect", 0.1))
        loop_mode = self.cfg.get("loop_mode", True)
        
        _timeout = aiohttp.ClientTimeout(total=tc, connect=cc)
        _hdrs = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15",
            "Accept-Language": "en-US",
        }
        
        conn = aiohttp.TCPConnector(
            limit=0, limit_per_host=0,
            use_dns_cache=True, ttl_dns_cache=600,
            keepalive_timeout=60,
            enable_cleanup_closed=True,
            force_close=False,
            ssl=False,
        )
        
        session = aiohttp.ClientSession(
            connector=conn,
            headers=_hdrs,
            timeout=_timeout,
            connector_owner=True,
            trust_env=True,
        )
        
        # Stats loop
        t_start = time.perf_counter()
        
        async def _stats_loop():
            while self.running:
                await asyncio.sleep(1)
                el = time.perf_counter() - t_start
                cps = self._total_checks / el if el > 0 else 0
                cycle = self._total_checks // max(len(names), 1)
                print(f"[STATS] Cycle: {cycle} | Found: {self._found} | Checks: {self._total_checks} | CPS: {cps:.1f}")
        
        # Per-name worker
        async def _worker(name):
            sem = asyncio.Semaphore(5)  # 5 concurrent per name
            
            while self.running:
                while self.paused and self.running:
                    await asyncio.sleep(0.02)
                
                if not self.running:
                    break
                
                await sem.acquire()
                
                if not self.running:
                    sem.release()
                    break
                
                asyncio.create_task(self._check(session, name, sem))
                self._total_checks += 1
                
                if not loop_mode:
                    for _ in range(5):
                        await sem.acquire()
                    break
        
        try:
            workers = [asyncio.create_task(_worker(n)) for n in names]
            stats_task = asyncio.create_task(_stats_loop())
            
            await asyncio.gather(*workers, return_exceptions=True)
            
            stats_task.cancel()
        
        finally:
            await session.close()
            self.running = False
            print("[INFO] Checker stopped")
    
    async def _check(self, session, name, sem):
        """Check single name (with proxy rotation) - FULL LOGGING."""
        url = f"https://horizon.meta.com/profile/{name}/"
        proxy = self.proxy_rotator.get_next()
        
        try:
            async with session.get(url, proxy=proxy, allow_redirects=False, timeout=5) as r:
                status = r.status
                location = r.headers.get("Location", "")
                
                # Parse status
                if status in (301, 302, 303, 307, 308):
                    if location == "https://horizon.meta.com/":
                        result = "AVAILABLE"
                    elif f"/profile/{name}" in location:
                        result = "TAKEN"
                    else:
                        result = "UNKNOWN"
                elif status == 200:
                    result = "TAKEN" if f"/profile/{name}" in str(r.url) else "AVAILABLE"
                elif status == 404:
                    result = "AVAILABLE"
                elif status == 429:
                    result = "RATE"
                else:
                    result = "UNKNOWN"
                
                # LOG EVERYTHING
                if result == "AVAILABLE":
                    if name not in self._cache:
                        self._cache.add(name)
                        self._found += 1
                        print(f"🎯 [AVAILABLE] {name} ← FOUND!")
                        
                        # Fire sniper if enabled
                        if self.cfg.get("snipe_mode") and self._sniper:
                            self._sniper.fire(name)
                        
                        # Send webhook
                        if self.cfg.get("webhook_enabled"):
                            self._send_webhook(name)
                elif result == "TAKEN":
                    print(f"[TAKEN] {name}")
                elif result == "RATE":
                    print(f"⚠️ [RATE] {name}")
                else:
                    print(f"[{result}] {name}")
        
        except asyncio.TimeoutError:
            print(f"⏱️ [TIMEOUT] {name}")
        except Exception as e:
            print(f"❌ [ERROR] {name} - {str(e)[:30]}")
        
        finally:
            sem.release()
    
    def _send_webhook(self, name):
        """Send Discord webhook notification."""
        url = self.cfg.get("webhook_url")
        if not url:
            return
        
        try:
            import requests
            requests.post(url, json={
                "content": f"🎯 **AVAILABLE** `{name}`",
                "username": "Metasnie Sniper"
            }, timeout=5)
        except:
            pass

# ─────────────────────────────────────────────────────────────────────────────
# FAST SNIPER (ULTRA-OPTIMIZED)
# ─────────────────────────────────────────────────────────────────────────────

class UltraFastSniper:
    """Ultra-fast urllib3-based sniper."""
    
    def __init__(self, creds):
        import urllib3
        urllib3.disable_warnings()
        
        self.creds = creds
        self.snipers = [UltraSniperAccount(c) for c in creds]
    
    def warm_all(self):
        """Pre-warm all accounts."""
        print(f"[INFO] Warming {len(self.snipers)} accounts...")
        threads = []
        success = [0]
        lock = threading.Lock()
        
        def _warm(sniper):
            if sniper.warm():
                with lock:
                    success[0] += 1
        
        for sniper in self.snipers:
            t = threading.Thread(target=_warm, args=(sniper,), daemon=True)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join(timeout=5)
        
        print(f"[INFO] {success[0]}/{len(self.snipers)} accounts ready")
        return success[0] > 0
    
    def fire(self, name):
        """Fire all accounts simultaneously."""
        print(f"[SNIPE] Firing {len(self.snipers)} accounts for '{name}'")
        threads = []
        results = {}
        lock = threading.Lock()
        
        def _fire(idx, sniper):
            result = sniper.fire(name)
            with lock:
                results[idx] = result
                if result.get('success'):
                    print(f"✅ [SUCCESS] Account {idx+1} claimed '{name}'")
        
        for idx, sniper in enumerate(self.snipers):
            t = threading.Thread(target=_fire, args=(idx, sniper), daemon=True)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join(timeout=5)
        
        return results

class UltraSniperAccount:
    """Single account sniper (urllib3)."""
    
    def __init__(self, cred):
        import urllib3
        import ssl
        
        self.profile_id = cred['PROFILE_ID']
        self.fs_token = cred['fs']
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        self.pool = urllib3.HTTPSConnectionPool(
            'accountscenter.meta.com', port=443, maxsize=1, block=True,
            timeout=urllib3.Timeout(connect=0.1, read=5),
            ssl_context=ctx,
        )
        
        self.tokens = None
        self._headers = None
        self._base_data = None
    
    def warm(self):
        """Fetch tokens and prepare."""
        try:
            r = self.pool.request(
                'GET',
                f'/profiles/{self.profile_id}/username/',
                headers={
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X)',
                    'Cookie': f'fs={self.fs_token}; locale=en_US',
                },
                preload_content=True,
            )
            
            html = r.data.decode('utf-8', errors='ignore')
            
            dtsg = re.search(r'DTSGInitialData",\[\],\{"token":"([^"]+)"', html)
            lsd = re.search(r'"LSD",\[\],\{"token":"([^"]+)"\}', html)
            rev = re.search(r'"client_revision":(\d+)', html)
            hsi = re.search(r'"haste_session":"([^"]+)"', html)
            
            self.tokens = {
                'fb_dtsg': dtsg.group(1) if dtsg else '',
                'lsd': lsd.group(1) if lsd else '',
                '__rev': rev.group(1) if rev else '1',
                '__hsi': hsi.group(1) if hsi else '',
            }
            
            self._headers = {
                'x-fb-lsd': self.tokens['lsd'],
                'x-fb-friendly-name': 'useFXIMUpdateUsernameMutation',
                'x-asbd-id': '359341',
                'content-type': 'application/x-www-form-urlencoded',
                'cookie': f'fs={self.fs_token}; locale=en_US',
            }
            
            self._base_data = {
                'av': self.profile_id,
                'fb_dtsg': self.tokens['fb_dtsg'],
                'lsd': self.tokens['lsd'],
                '__rev': self.tokens['__rev'],
                '__hsi': self.tokens['__hsi'],
                'doc_id': '9672408826128267',
                'fb_api_req_friendly_name': 'useFXIMUpdateUsernameMutation',
                'fb_api_caller_class': 'RelayModern',
                'server_timestamps': 'true',
            }
            
            return True
        except:
            return False
    
    def fire(self, username):
        """Claim username."""
        if not self.tokens:
            return {'success': False, 'error': 'not_warmed'}
        
        try:
            variables = json.dumps({
                'client_mutation_id': str(uuid.uuid4()),
                'family_device_id': 'device_id_fetch_datr',
                'identity_ids': [self.profile_id],
                'target_fx_identifier': self.profile_id,
                'username': username,
                'interface': 'FRL_WEB',
            })
            
            body_dict = dict(self._base_data)
            body_dict['variables'] = variables
            body = urlencode(body_dict).encode('utf-8')
            
            r = self.pool.request(
                'POST',
                '/api/graphql/',
                body=body,
                headers=self._headers,
                preload_content=True,
            )
            
            result = json.loads(r.data.decode('utf-8'))
            mut = result.get('data', {}).get('fxim_update_identity_username') or {}
            err = mut.get('error')
            
            if err:
                return {'success': False, 'error': str(err)[:50]}
            
            return {'success': True, 'error': None}
        
        except Exception as e:
            return {'success': False, 'error': str(e)[:50]}

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Metasnie Headless CLI")
    parser.add_argument("--config", help="Config JSON file", default="checker_config.json")
    parser.add_argument("--names", help="Names list file", default="lists/names.txt")
    parser.add_argument("--proxies", help="Comma-separated proxies", default="")
    parser.add_argument("--webhook", help="Discord webhook URL", default="")
    parser.add_argument("--snipe", action="store_true", help="Enable snipe mode", default=True)
    parser.add_argument("--env", action="store_true", help="Load config from environment")
    
    args = parser.parse_args()
    
    # Load config
    if args.env:
        cfg = load_config_from_env()
        print("[INFO] Loaded config from environment variables")
    else:
        cfg = load_config_from_file(args.config)
        if not cfg:
            cfg = load_config_from_env()
    
    # Override with CLI args
    if args.webhook:
        cfg["webhook_enabled"] = True
        cfg["webhook_url"] = args.webhook
    
    if args.names:
        cfg["selected_list"] = args.names
    
    cfg["snipe_mode"] = args.snipe
    
    print("[CONFIG]")
    print(f"  Names: {cfg.get('selected_list')}")
    print(f"  Snipe mode: {cfg.get('snipe_mode')}")
    print(f"  Webhook: {cfg.get('webhook_enabled')}")
    print()
    
    # Load names
    names = load_names(cfg.get("selected_list", "lists/names.txt"))
    if not names:
        print("[ERROR] No names loaded")
        sys.exit(1)
    
    print(f"[INFO] Loaded {len(names)} names")
    print()
    
    # Load creds and start sniper
    creds = load_creds()
    sniper = None
    
    if cfg.get("snipe_mode") and creds:
        print(f"[INFO] Loaded {len(creds)} credentials")
        sniper = UltraFastSniper(creds)
        if not sniper.warm_all():
            print("[WARN] Sniper accounts not ready")
            sniper = None
    
    print()
    
    # Create checker
    checker = HeadlessChecker(cfg, proxies=args.proxies)
    if sniper:
        checker.set_sniper(sniper)
    
    # Run
    print("[START] Checker running... (Press Ctrl+C to stop)")
    print()
    
    try:
        asyncio.run(checker.run(names))
    except KeyboardInterrupt:
        print("\n[STOP] Stopped by user")
        checker.running = False

if __name__ == "__main__":
    main()
