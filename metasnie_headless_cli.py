#!/usr/bin/env python3
"""
METASNIE ULTRA-SPEED CHECKER
- No logging overhead
- Max concurrency (1000+)
- Direct urllib3 for checking
- Minimal Python overhead
"""

import asyncio
import aiohttp
import json
import os
import sys
import time
import threading
import urllib3
import re
import uuid
from urllib.parse import urlencode

urllib3.disable_warnings()

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

def load_config_from_env():
    return {
        "loop_mode": os.getenv("LOOP_MODE", "true").lower() == "true",
        "snipe_mode": os.getenv("SNIPE_MODE", "true").lower() == "true",
        "webhook_enabled": os.getenv("WEBHOOK_ENABLED", "true").lower() == "true",
        "webhook_url": os.getenv("WEBHOOK_URL", ""),
        "selected_list": os.getenv("NAMES_LIST", "lists/names.txt"),
        "timeout_total": float(os.getenv("TIMEOUT_TOTAL", 0.3)),
        "timeout_connect": float(os.getenv("TIMEOUT_CONNECT", 0.05)),
    }

def load_creds():
    try:
        with open("creds/creds.json") as f:
            return json.load(f)
    except:
        return []

def load_names(path):
    try:
        with open(path) as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

# ─────────────────────────────────────────────────────────────────────────────
# ULTRA-FAST CHECKER (MINIMAL OVERHEAD)
# ─────────────────────────────────────────────────────────────────────────────

class UltraFastChecker:
    def __init__(self, cfg):
        self.cfg = cfg
        self.running = False
        self._cache = set()
        self._found = 0
        self._checks = 0
        self._sniper = None
        self.t_start = 0
    
    def set_sniper(self, sniper):
        self._sniper = sniper
    
    async def run(self, names):
        self.running = True
        self._cache.clear()
        self._found = 0
        self._checks = 0
        self.t_start = time.perf_counter()
        
        print(f"[START] {len(names)} names | Loop: {self.cfg['loop_mode']}")
        
        tc = self.cfg["timeout_total"]
        cc = self.cfg["timeout_connect"]
        loop_mode = self.cfg["loop_mode"]
        
        _timeout = aiohttp.ClientTimeout(total=tc, connect=cc)
        _hdrs = {"User-Agent": "Mozilla/5.0"}
        
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
        
        # Stats only
        async def _stats_loop():
            last_check = [0]
            while self.running:
                await asyncio.sleep(2)
                el = time.perf_counter() - self.t_start
                cps = self._checks / el if el > 0 else 0
                delta = self._checks - last_check[0]
                print(f"[CPS] {cps:.0f}/s | Found: {self._found} | Total: {self._checks}")
                last_check[0] = self._checks
        
        # Per-name worker
        async def _worker(name):
            sem = asyncio.Semaphore(1000)  # MAX concurrency
            
            while self.running:
                await sem.acquire()
                if not self.running:
                    sem.release()
                    break
                
                asyncio.create_task(self._check(session, name, sem))
                self._checks += 1
                
                if not loop_mode:
                    for _ in range(1000):
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
    
    async def _check(self, session, name, sem):
        """ULTRA-FAST check - zero overhead."""
        try:
            async with session.get(
                f"https://horizon.meta.com/profile/{name}/",
                allow_redirects=False,
                timeout=self.cfg["timeout_total"]
            ) as r:
                loc = r.headers.get("Location", "")
                
                # Fast status parse
                if r.status in (301, 302, 303, 307, 308):
                    result = "AVAILABLE" if loc == "https://horizon.meta.com/" else "TAKEN"
                elif r.status == 200:
                    result = "AVAILABLE" if f"/profile/{name}" not in str(r.url) else "TAKEN"
                elif r.status == 404:
                    result = "AVAILABLE"
                elif r.status == 429:
                    result = "RATE"
                else:
                    result = None
                
                if result == "AVAILABLE" and name not in self._cache:
                    self._cache.add(name)
                    self._found += 1
                    print(f"🎯 AVAILABLE: {name}")
                    
                    if self.cfg["snipe_mode"] and self._sniper:
                        self._sniper.fire(name)
                    
                    if self.cfg["webhook_enabled"]:
                        self._send_webhook(name)
        
        except:
            pass
        
        finally:
            sem.release()
    
    def _send_webhook(self, name):
        try:
            import requests
            requests.post(self.cfg["webhook_url"], json={"content": f"🎯 `{name}`"}, timeout=5)
        except:
            pass

# ─────────────────────────────────────────────────────────────────────────────
# ULTRA-FAST SNIPER
# ─────────────────────────────────────────────────────────────────────────────

class UltraFastSniper:
    def __init__(self, creds):
        self.creds = creds
        self.snipers = [FastSniperAccount(c) for c in creds]
    
    def warm_all(self):
        print(f"[WARM] {len(self.snipers)} accounts")
        ok = 0
        for s in self.snipers:
            if s.warm():
                ok += 1
        print(f"[READY] {ok}/{len(self.snipers)}")
        return ok > 0
    
    def fire(self, name):
        threads = []
        for idx, sniper in enumerate(self.snipers):
            t = threading.Thread(target=sniper.fire, args=(name,), daemon=True)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join(timeout=2)

class FastSniperAccount:
    def __init__(self, cred):
        import ssl
        self.profile_id = cred['PROFILE_ID']
        self.fs_token = cred['fs']
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        self.pool = urllib3.HTTPSConnectionPool(
            'accountscenter.meta.com', port=443, maxsize=1, block=True,
            timeout=urllib3.Timeout(connect=0.05, read=3),
            ssl_context=ctx,
        )
        
        self.tokens = None
        self._headers = None
        self._base = None
    
    def warm(self):
        try:
            r = self.pool.request('GET', f'/profiles/{self.profile_id}/username/',
                headers={'User-Agent': 'Mozilla/5.0', 'Cookie': f'fs={self.fs_token}'},
                preload_content=True)
            
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
                'cookie': f'fs={self.fs_token}',
            }
            
            self._base = {
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
        if not self.tokens:
            return
        
        try:
            vars = json.dumps({
                'client_mutation_id': str(uuid.uuid4()),
                'family_device_id': 'device_id_fetch_datr',
                'identity_ids': [self.profile_id],
                'target_fx_identifier': self.profile_id,
                'username': username,
                'interface': 'FRL_WEB',
            })
            
            body = dict(self._base)
            body['variables'] = vars
            
            self.pool.request('POST', '/api/graphql/',
                body=urlencode(body).encode('utf-8'),
                headers=self._headers,
                preload_content=True)
        except:
            pass

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    cfg = load_config_from_env()
    
    names = load_names(cfg["selected_list"])
    if not names:
        print("[ERROR] No names")
        sys.exit(1)
    
    print(f"[LOAD] {len(names)} names")
    
    creds = load_creds()
    sniper = None
    
    if cfg["snipe_mode"] and creds:
        print(f"[LOAD] {len(creds)} accounts")
        sniper = UltraFastSniper(creds)
        sniper.warm_all()
    
    checker = UltraFastChecker(cfg)
    if sniper:
        checker.set_sniper(sniper)
    
    try:
        asyncio.run(checker.run(names))
    except KeyboardInterrupt:
        print("\n[STOP]")
        checker.running = False

if __name__ == "__main__":
    main()
