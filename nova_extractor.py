#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🔥 ULTIMATE WEB CRAWLER 🔥                                  ║
║           Termux Compatible - With Login Support                            ║
║                                                                               ║
║  ✅ NO Playwright Required - Works on Termux/Android                          ║
║  ✅ Login & Session Management                                                ║
║  ✅ Cookie Support                                                            ║
║  ✅ Async Multi-threaded Crawling                                             ║
║  ✅ Smart Duplicate Detection (Bloom Filter)                                  ║
║  ✅ Intelligent Rate Limiting                                                 ║
║  ✅ robots.txt Compliance                                                     ║
║  ✅ Recursive Crawling with Depth Control                                     ║
║  ✅ Error Recovery & Retry Mechanism                                          ║
║  ✅ SQLite Database Storage                                                   ║
║  ✅ Export to Multiple Formats (JSON, CSV, TXT)                               ║
║  ✅ Graceful Ctrl+C Handling - Saves Partial Results                          ║
║  ✅ Bulletproof Output Generation & Path Resolution                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import aiohttp
import sqlite3
import json
import csv
import logging
import hashlib
import random
import time
import re
import os
import sys
import signal
import traceback
import webbrowser
import hmac
import base64
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
from urllib.robotparser import RobotFileParser
from dataclasses import dataclass, field
from typing import Set, Dict, List, Optional, Any
from datetime import datetime
from collections import deque
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.FileHandler('crawler.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════════
# COLOR CODES FOR TERMINAL
# ═════════════════════════════════════════════════════════════════════════════

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# ═════════════════════════════════════════════════════════════════════════════
# LICENSE MANAGEMENT
# ═════════════════════════════════════════════════════════════════════════════

LICENSE_SECRET_KEY = b"super_secret_admin_key_12345_termux_crawler"
LICENSE_FILE = "license.key"

def validate_license(license_key: str):
    try:
        if '.' not in license_key:
            return False, "Invalid license format."
        payload_b64, signature = license_key.split('.', 1)
        payload_bytes = base64.b64decode(payload_b64)
        
        expected_signature = hmac.new(LICENSE_SECRET_KEY, payload_bytes, hashlib.sha256).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return False, "Invalid license signature (Tampered or wrong key)."
            
        payload = json.loads(payload_bytes.decode('utf-8'))
        expires_str = payload.get('expires')
        expires_dt = datetime.strptime(expires_str, "%Y-%m-%d %H:%M:%S")
        
        if datetime.now() > expires_dt:
            return False, f"License expired on {expires_str}."
            
        return True, f"Valid until {expires_str}"
    except Exception as e:
        return False, f"Error validating license: {str(e)}"

def check_and_prompt_license() -> bool:
    # Check if license file exists
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, 'r', encoding='utf-8') as f:
                saved_key = f.read().strip()
            if saved_key:
                is_valid, msg = validate_license(saved_key)
                if is_valid:
                    print(f"\n{Colors.GREEN}✅ License Active: {msg}{Colors.END}")
                    time.sleep(1.5)
                    return True
                else:
                    print(f"\n{Colors.WARNING}⚠️ Saved license invalid: {msg}{Colors.END}")
        except Exception:
            pass
            
    # If not valid or missing, prompt
    while True:
        print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}🔒 LICENSE ACTIVATION REQUIRED{Colors.END}")
        print(f"{Colors.YELLOW}📢 To get or renew a license, contact: {Colors.BOLD}@bgxhost{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        
        print(f"    {Colors.GREEN}[1]{Colors.END} 🔑 Enter License Key")
        print(f"    {Colors.GREEN}[2]{Colors.END} 🚀 Get License Key (Opens @bgxhost)")
        print(f"    {Colors.GREEN}[3]{Colors.END} ❌ Exit Tool")
        
        choice = input(f"    {Colors.YELLOW}Select an option (1/2/3): {Colors.END}").strip()
        
        if choice == '2':
            open_link_in_android("https://t.me/bgxhost")
            print(f"    {Colors.GREEN}✅ Opening Telegram... Please message @bgxhost for a license key.{Colors.END}")
            print(f"    {Colors.YELLOW}💡 Come back here and select option 1 once you receive your key.{Colors.END}")
            time.sleep(2)
            continue
            
        elif choice == '3':
            return False
            
        elif choice == '1':
            key_input = input(f"\n    {Colors.YELLOW}Enter your license key: {Colors.END}").strip()
            if not key_input:
                print(f"    {Colors.FAIL}❌ License key cannot be empty!{Colors.END}")
                continue
                
            is_valid, msg = validate_license(key_input)
            if is_valid:
                print(f"    {Colors.GREEN}✅ {msg}{Colors.END}")
                try:
                    with open(LICENSE_FILE, 'w', encoding='utf-8') as f:
                        f.write(key_input)
                except Exception:
                    pass
                time.sleep(1.5)
                return True
            else:
                print(f"    {Colors.FAIL}❌ {msg}{Colors.END}")
                print(f"    {Colors.YELLOW}👉 Please contact {Colors.BOLD}@bgxhost{Colors.END}{Colors.YELLOW} on Telegram to get a valid license.{Colors.END}")
                time.sleep(2)
        else:
            print(f"    {Colors.FAIL}❌ Invalid choice!{Colors.END}")
            time.sleep(1)


# ═════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═════════════════════════════════════════════════════════════════════════════

@dataclass
class CrawlConfig:
    """Configuration for the crawler"""
    start_url: str
    max_depth: int = 3
    max_pages: int = 1000
    concurrency: int = 10
    delay: float = 1.0
    respect_robots: bool = True
    use_proxy: Optional[str] = None
    login_url: Optional[str] = None
    login_data: Optional[Dict] = None
    cookies: Optional[str] = None
    headers: Optional[Dict] = None
    output_dir: str = "crawl_output"
    database_name: str = "crawler.db"
    user_agent_rotation: bool = True
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 2.0
    allowed_domains: Optional[List[str]] = None
    exclude_patterns: List[str] = field(default_factory=lambda: [
        r'\.(pdf|jpg|jpeg|png|gif|css|js|zip|tar|gz|rar|exe|mp3|mp4|avi|mov|svg|webp)$',
        r'mailto:',
        r'tel:',
        r'javascript:',
        r'#',
        r'facebook\.com',
        r'twitter\.com',
        r'instagram\.com',
        r'linkedin\.com',
        r'youtube\.com',
        r'google\.com'
    ])
    follow_redirects: bool = True
    extract_emails: bool = True
    extract_phones: bool = True
    save_html: bool = False


# ═════════════════════════════════════════════════════════════════════════════
# BLOOM FILTER FOR DUPLICATE DETECTION
# ═════════════════════════════════════════════════════════════════════════════

class BloomFilter:
    """Memory-efficient duplicate detection using Bloom Filter"""
    
    def __init__(self, size: int = 1000000, hash_count: int = 7):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = [0] * size
        self.seeds = [i for i in range(hash_count)]
    
    def _hash(self, item: str, seed: int) -> int:
        hash_val = hashlib.md5(f"{item}:{seed}".encode()).hexdigest()
        return int(hash_val, 16) % self.size
    
    def add(self, item: str):
        for seed in self.seeds:
            index = self._hash(item, seed)
            self.bit_array[index] = 1
    
    def contains(self, item: str) -> bool:
        for seed in self.seeds:
            index = self._hash(item, seed)
            if self.bit_array[index] == 0:
                return False
        return True


# ═════════════════════════════════════════════════════════════════════════════
# RATE LIMITER
# ═════════════════════════════════════════════════════════════════════════════

class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, rate: float, burst: int = 10):
        self.rate = rate
        self.burst = burst
        self.tokens = burst
        self.last_update = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1


# ═════════════════════════════════════════════════════════════════════════════
# DATABASE MANAGER
# ═════════════════════════════════════════════════════════════════════════════

class DatabaseManager:
    """SQLite database manager for storing crawl results"""
    
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                parent_url TEXT,
                depth INTEGER,
                title TEXT,
                status_code INTEGER,
                content_type TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                crawled_at TIMESTAMP,
                html_content TEXT,
                text_content TEXT,
                meta_description TEXT,
                meta_keywords TEXT,
                h1_tags TEXT,
                email_addresses TEXT,
                phone_numbers TEXT,
                error_message TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crawl_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                depth INTEGER,
                parent_url TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT UNIQUE NOT NULL,
                cookies TEXT,
                headers TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_link(self, data: Dict):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO links 
                (url, parent_url, depth, title, status_code, content_type, 
                 crawled_at, html_content, text_content, meta_description, 
                 meta_keywords, h1_tags, email_addresses, phone_numbers, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('url'),
                data.get('parent_url'),
                data.get('depth'),
                data.get('title'),
                data.get('status_code'),
                data.get('content_type'),
                datetime.now(),
                data.get('html_content'),
                data.get('text_content'),
                data.get('meta_description'),
                data.get('meta_keywords'),
                json.dumps(data.get('h1_tags', [])),
                json.dumps(data.get('emails', [])),
                json.dumps(data.get('phones', [])),
                data.get('error')
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Database error: {e}")
        finally:
            conn.close()
    
    def add_to_queue(self, url: str, depth: int, parent_url: str):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO crawl_queue (url, depth, parent_url)
                VALUES (?, ?, ?)
            ''', (url, depth, parent_url))
            conn.commit()
        except:
            pass
        finally:
            conn.close()
    
    def get_all_links(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT url, parent_url, depth, title, status_code, 
                   discovered_at, email_addresses, phone_numbers
            FROM links ORDER BY discovered_at
        ''')
        
        columns = [description[0] for description in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        conn.close()
        return results
    
    def save_session(self, domain: str, cookies: str, headers: str):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO sessions (domain, cookies, headers) VALUES (?, ?, ?)', (domain, cookies, headers))
        conn.commit()
        conn.close()
    
    def get_session(self, domain: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT cookies, headers FROM sessions WHERE domain = ?', (domain,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return {'cookies': result[0], 'headers': result[1]}
        return None


# ═════════════════════════════════════════════════════════════════════════════
# URL UTILITIES
# ═════════════════════════════════════════════════════════════════════════════

class URLNormalizer:
    @staticmethod
    def normalize(url: str) -> str:
        try:
            parsed = urlparse(url)
            scheme = parsed.scheme.lower()
            netloc = parsed.netloc.lower()
            if ':' in netloc:
                host, port = netloc.rsplit(':', 1)
                if (scheme == 'http' and port == '80') or (scheme == 'https' and port == '443'):
                    netloc = host
            path = parsed.path.rstrip('/')
            if not path: path = '/'
            if parsed.query:
                params = parse_qs(parsed.query, keep_blank_values=True)
                sorted_params = sorted(params.items())
                query = urlencode(sorted_params, doseq=True)
            else:
                query = ''
            return urlunparse((scheme, netloc, path, '', query, ''))
        except Exception as e:
            logger.error(f"URL normalization error: {e}")
            return url
    
    @staticmethod
    def get_domain(url: str) -> str:
        try:
            return urlparse(url).netloc.lower()
        except:
            return ""


# ═════════════════════════════════════════════════════════════════════════════
# CONTENT EXTRACTOR
# ═════════════════════════════════════════════════════════════════════════════

class ContentExtractor:
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]')
    
    @classmethod
    def extract_emails(cls, text: str) -> List[str]:
        return list(set(cls.EMAIL_PATTERN.findall(text)))
    
    @classmethod
    def extract_phones(cls, text: str) -> List[str]:
        phones = cls.PHONE_PATTERN.findall(text)
        return list(set([re.sub(r'[^\d+]', '', p) for p in phones if len(re.sub(r'[^\d]', '', p)) >= 10]))
    
    @staticmethod
    def extract_links(html: str, base_url: str) -> Set[str]:
        links = set()
        href_pattern = re.compile(r'href=["\'](.*?)["\']', re.IGNORECASE)
        for match in href_pattern.findall(html):
            if match and not match.startswith(('data:', 'javascript:', 'mailto:', 'tel:', '#')):
                links.add(urljoin(base_url, match))
        
        src_pattern = re.compile(r'src=["\'](.*?)["\']', re.IGNORECASE)
        for match in src_pattern.findall(html):
            if match and not match.startswith('data:'):
                links.add(urljoin(base_url, match))
        
        action_pattern = re.compile(r'action=["\'](.*?)["\']', re.IGNORECASE)
        for match in action_pattern.findall(html):
            if match:
                links.add(urljoin(base_url, match))
                
        return links
    
    @staticmethod
    def extract_meta_data(html: str) -> Dict[str, str]:
        meta_data = {}
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        meta_data['title'] = title_match.group(1).strip() if title_match else ''
        
        desc_match = re.search(r'<meta[^>]*?name=["\']description["\'][^>]*?content=["\'](.*?)["\']', html, re.IGNORECASE)
        if not desc_match:
            desc_match = re.search(r'<meta[^>]*?content=["\'](.*?)["\'][^>]*?name=["\']description["\']', html, re.IGNORECASE)
        meta_data['description'] = desc_match.group(1) if desc_match else ''
        
        kw_match = re.search(r'<meta[^>]*?name=["\']keywords["\'][^>]*?content=["\'](.*?)["\']', html, re.IGNORECASE)
        if not kw_match:
            kw_match = re.search(r'<meta[^>]*?content=["\'](.*?)["\'][^>]*?name=["\']keywords["\']', html, re.IGNORECASE)
        meta_data['keywords'] = kw_match.group(1) if kw_match else ''
        
        h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
        meta_data['h1_tags'] = [re.sub(r'<[^>]+>', '', h1).strip() for h1 in h1_matches]
        return meta_data


# ═════════════════════════════════════════════════════════════════════════════
# ROBOTS CHECKER
# ═════════════════════════════════════════════════════════════════════════════

class RobotsChecker:
    def __init__(self):
        self.parsers: Dict[str, RobotFileParser] = {}
    
    async def can_fetch(self, url: str, user_agent: str = '*') -> bool:
        domain = URLNormalizer.get_domain(url)
        if domain not in self.parsers:
            robots_url = f"https://{domain}/robots.txt"
            parser = RobotFileParser()
            parser.set_url(robots_url)
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(robots_url, timeout=10, ssl=False) as response:
                        if response.status == 200:
                            parser.parse((await response.text()).split('\n'))
                            self.parsers[domain] = parser
                        else:
                            return True
            except:
                return True
        
        parser = self.parsers.get(domain)
        if parser:
            return parser.can_fetch(user_agent, url)
        return True


# ═════════════════════════════════════════════════════════════════════════════
# LOGIN HANDLER
# ═════════════════════════════════════════════════════════════════════════════

class LoginHandler:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.logged_in = False
        self.cookies = {}
    
    async def login(self, login_url: str, credentials: Dict[str, str], method: str = 'post') -> bool:
        try:
            logger.info(f"🔐 Attempting login to: {login_url}")
            async with self.session.get(login_url, ssl=False) as response:
                login_html = await response.text()
            
            csrf_token = self._extract_csrf(login_html)
            if csrf_token:
                credentials['csrf_token'] = csrf_token
                logger.info(f"🔑 CSRF token extracted")
            
            if method.lower() == 'post':
                async with self.session.post(login_url, data=credentials, ssl=False, allow_redirects=True) as response:
                    if response.status in [200, 302]:
                        self.logged_in = True
                        logger.info(f"✅ Login successful!")
                        return True
            else:
                async with self.session.get(login_url, params=credentials, ssl=False) as response:
                    if response.status == 200:
                        self.logged_in = True
                        logger.info(f"✅ Login successful!")
                        return True
            logger.error(f"❌ Login failed with status: {response.status}")
            return False
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False
    
    def _extract_csrf(self, html: str) -> Optional[str]:
        patterns = [r'name=["\']csrf_token["\'] value=["\'](.*?)["\']', r'name=["\']_token["\'] value=["\'](.*?)["\']', r'"csrfToken":\s*"(.*?)"']
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match: return match.group(1)
        return None
    
    def set_cookies(self, cookie_string: str):
        try:
            cookies = {}
            for item in cookie_string.split(';'):
                if '=' in item:
                    key, value = item.strip().split('=', 1)
                    cookies[key] = value
            self.cookies = cookies
            logger.info(f"🍪 Cookies set: {len(cookies)} cookies")
        except Exception as e:
            logger.error(f"❌ Cookie parsing error: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# MAIN CRAWLER
# ═════════════════════════════════════════════════════════════════════════════

class UltimateCrawler:
    def __init__(self, config: CrawlConfig):
        self.config = config
        self.visited = BloomFilter(size=10000000)
        self.db = DatabaseManager(config.database_name)
        self.rate_limiter = RateLimiter(1.0 / config.delay)
        self.robots_checker = RobotsChecker()
        self.url_normalizer = URLNormalizer()
        self.content_extractor = ContentExtractor()
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(config.concurrency)
        self.stats = {'total': 0, 'success': 0, 'failed': 0, 'start_time': None, 'depth_reached': 0}
        self.running = True
        self.login_handler: Optional[LoginHandler] = None
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)
    
    def _load_user_agents(self) -> List[str]:
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Android 14; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0',
            'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        ]
    
    def get_random_user_agent(self) -> str:
        return random.choice(self._load_user_agents())
    
    async def init_session(self):
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=10, ttl_dns_cache=300, use_dns_cache=True)
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5', 'DNT': '1', 'Connection': 'keep-alive', 'Upgrade-Insecure-Requests': '1'
        }
        if self.config.headers: headers.update(self.config.headers)
        
        cookie_jar = aiohttp.CookieJar()
        if self.config.cookies and os.path.exists(self.config.cookies):
            with open(self.config.cookies, 'r') as f:
                cookie_data = json.load(f)
                for domain, cookies in cookie_data.items():
                    for name, value in cookies.items():
                        cookie_jar.update_cookies({name: value}, f"https://{domain}")
        
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout, headers=headers, cookie_jar=cookie_jar)
        self.login_handler = LoginHandler(self.session)
        
        if self.config.cookies and not os.path.exists(self.config.cookies):
            logger.info("🍪 Parsing cookie string...")
            target_domain = URLNormalizer.get_domain(self.config.start_url)
            for item in self.config.cookies.split(';'):
                if '=' in item:
                    key, value = item.strip().split('=', 1)
                    cookie_jar.update_cookies({key: value}, f"https://{target_domain}")
            logger.info("✅ Cookie string applied to session!")
        
        if self.config.login_url and self.config.login_data:
            await self.login_handler.login(self.config.login_url, self.config.login_data)
    
    async def close(self):
        if self.session: await self.session.close()
        logger.info("🧹 Resources cleaned up")
    
    def should_crawl(self, url: str) -> bool:
        if self.config.allowed_domains:
            if not any(d in self.url_normalizer.get_domain(url) for d in self.config.allowed_domains): return False
        for pattern in self.config.exclude_patterns:
            if re.search(pattern, url, re.IGNORECASE): return False
        if self.visited.contains(self.url_normalizer.normalize(url)): return False
        return True
    
    async def fetch_url(self, url: str, retry: int = 0) -> Dict[str, Any]:
        if self.config.respect_robots:
            if not await self.robots_checker.can_fetch(url): return {'success': False, 'error': 'Blocked by robots.txt'}
        
        await self.rate_limiter.acquire()
        try:
            async with self.session.get(url, headers={'User-Agent': self.get_random_user_agent()}, allow_redirects=self.config.follow_redirects, ssl=False) as response:
                return {'success': True, 'content': await response.text(), 'status_code': response.status, 'content_type': response.headers.get('Content-Type', ''), 'final_url': str(response.url)}
        except Exception as e:
            if retry < self.config.retry_attempts:
                await asyncio.sleep(self.config.retry_delay * (retry + 1))
                return await self.fetch_url(url, retry + 1)
            return {'success': False, 'error': str(e)}
    
    async def process_page(self, url: str, depth: int, parent_url: str) -> Set[str]:
        self.visited.add(self.url_normalizer.normalize(url))
        self.stats['total'] += 1
        if depth > self.stats['depth_reached']: self.stats['depth_reached'] = depth
        logger.info(f"🔍 [{depth}] Crawling: {url[:80]}...")
        
        result = await self.fetch_url(url)
        new_links = set()
        page_data = {'url': url, 'parent_url': parent_url, 'depth': depth, 'title': '', 'status_code': None, 'content_type': '', 'html_content': '', 'text_content': '', 'meta_description': '', 'meta_keywords': '', 'h1_tags': [], 'emails': [], 'phones': [], 'error': None}
        
        if result['success']:
            self.stats['success'] += 1
            html = result['content']
            meta = self.content_extractor.extract_meta_data(html)
            page_data.update({'title': meta.get('title', ''), 'status_code': result.get('status_code'), 'content_type': result.get('content_type', ''), 'html_content': html if self.config.save_html else '', 'text_content': re.sub(r'<[^>]+>', ' ', html), 'meta_description': meta.get('description', ''), 'meta_keywords': meta.get('keywords', ''), 'h1_tags': meta.get('h1_tags', [])})
            
            if self.config.extract_emails: page_data['emails'] = self.content_extractor.extract_emails(html)
            if self.config.extract_phones: page_data['phones'] = self.content_extractor.extract_phones(html)
            
            if depth < self.config.max_depth:
                for link in self.content_extractor.extract_links(html, url):
                    if self.should_crawl(link):
                        norm_link = self.url_normalizer.normalize(link)
                        if not self.visited.contains(norm_link):
                            new_links.add(link)
                            self.db.add_to_queue(link, depth + 1, url)
            
            logger.info(f"✅ Success: {page_data['title'][:50] if page_data['title'] else 'No title'} | +{len(new_links)} links")
        else:
            self.stats['failed'] += 1
            page_data['error'] = result.get('error', 'Unknown error')
            logger.error(f"❌ Failed: {url} - {page_data['error']}")
        
        self.db.save_link(page_data)
        return new_links
    
    async def crawl_worker(self, queue: asyncio.Queue):
        while self.running:
            try:
                url, depth, parent_url = await asyncio.wait_for(queue.get(), timeout=1.0)
                try:
                    async with self.semaphore:
                        new_links = await self.process_page(url, depth, parent_url)
                        for link in new_links:
                            await queue.put((link, depth + 1, url))
                finally:
                    queue.task_done()
                
                if self.stats['total'] >= self.config.max_pages:
                    logger.info(f"📊 Max pages ({self.config.max_pages}) reached")
                    self.running = False
                    break
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker error: {e}")
    
    async def start_crawling(self):
        logger.info("🚀 Starting Ultimate Web Crawler...")
        logger.info(f"📍 Target: {self.config.start_url}")
        logger.info(f"📊 Max Depth: {self.config.max_depth} | Max Pages: {self.config.max_pages}")
        logger.info(f"💡 Press {Colors.BOLD}Ctrl+C{Colors.END} to stop gracefully (results will be saved)")
        if self.config.login_url: logger.info(f"🔐 Login URL: {self.config.login_url}")
        
        self.stats['start_time'] = datetime.now()
        await self.init_session()
        
        queue = asyncio.Queue()
        self.visited.add(self.url_normalizer.normalize(self.config.start_url))
        await queue.put((self.config.start_url, 0, None))
        
        workers = [asyncio.create_task(self.crawl_worker(queue)) for _ in range(self.config.concurrency)]
        interrupted = False
        
        try:
            while self.running:
                try:
                    await asyncio.wait_for(queue.join(), timeout=0.5)
                    break
                except asyncio.TimeoutError:
                    continue
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.warning("🛑 Ctrl+C detected! Stopping crawler gracefully...")
            self.running = False
            interrupted = True
            try:
                await asyncio.wait_for(queue.join(), timeout=10.0)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                logger.warning("⚠️ Timeout waiting for tasks to finish. Forcing shutdown.")
        except Exception as e:
            logger.error(f"❌ Unexpected error in main loop: {e}")
            self.running = False
            interrupted = True
        finally:
            print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
            print(f"{Colors.CYAN}💾 FINALLY BLOCK: Generating reports...{Colors.END}")
            print(f"{Colors.CYAN}{'='*60}{Colors.END}")
            try:
                self.generate_reports()
            except Exception as e:
                print(f"{Colors.FAIL}❌ Critical Error in generate_reports: {e}{Colors.END}")
                traceback.print_exc()
            
            for worker in workers:
                if not worker.done():
                    worker.cancel()
            await asyncio.gather(*workers, return_exceptions=True)
            await self.close()
            
            duration = datetime.now() - self.stats['start_time']
            logger.info("=" * 60)
            logger.info("📊 CRAWL STATISTICS")
            logger.info("=" * 60)
            logger.info(f"⏱️  Duration: {duration}")
            logger.info(f"🔗 Total URLs: {self.stats['total']}")
            logger.info(f"✅ Successful: {self.stats['success']}")
            logger.info(f"❌ Failed: {self.stats['failed']}")
            logger.info(f"📏 Max Depth Reached: {self.stats['depth_reached']}")
            if interrupted:
                logger.info(f"⚠️  Status: {Colors.WARNING}Interrupted by user - Partial results saved{Colors.END}")
            else:
                logger.info(f"🎉 Status: {Colors.GREEN}Completed successfully{Colors.END}")
            logger.info("=" * 60)
    
    def generate_reports(self):
        """Bulletproof report generation with visible console output"""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.CYAN}💾 SAVING RESULTS TO DISK{Colors.END}")
        print(f"{Colors.CYAN}📂 Database: {self.config.database_name}{Colors.END}")
        print(f"{Colors.CYAN}📁 Output Dir: {self.config.output_dir}{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        try:
            links = self.db.get_all_links()
            print(f"   {Colors.GREEN}✔{Colors.END} Retrieved {len(links)} links from database.")
            
            if not links:
                print(f"   {Colors.WARNING}⚠️  No links to export - database is empty.{Colors.END}")
                print(f"   {Colors.CYAN}💡 Tip: Check 'crawler.log' for 'Database error' messages.{Colors.END}")
                return
            
            output_path = Path(self.config.output_dir).resolve()
            output_path.mkdir(parents=True, exist_ok=True)
            print(f"   {Colors.GREEN}✔{Colors.END} Output directory resolved to: {Colors.BOLD}{output_path}{Colors.END}")
            
            json_path = output_path / 'crawl_results.json'
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(links, f, indent=2, ensure_ascii=False, default=str)
            print(f"   {Colors.GREEN}✔{Colors.END} Saved JSON: {json_path.name} ({json_path.stat().st_size:,} bytes)")
            
            csv_path = output_path / 'crawl_results.csv'
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=links[0].keys())
                writer.writeheader()
                writer.writerows(links)
            print(f"   {Colors.GREEN}✔{Colors.END} Saved CSV: {csv_path.name} ({csv_path.stat().st_size:,} bytes)")
            
            txt_path = output_path / 'all_urls.txt'
            with open(txt_path, 'w', encoding='utf-8') as f:
                for link in links:
                    f.write(f"{link['url']}\n")
            print(f"   {Colors.GREEN}✔{Colors.END} Saved TXT: {txt_path.name} ({txt_path.stat().st_size:,} bytes)")
            
            summary_path = output_path / 'summary.txt'
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("ULTIMATE WEB CRAWLER - SUMMARY REPORT\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Target: {self.config.start_url}\n")
                f.write(f"Total URLs: {len(links)}\n")
                f.write(f"Successful: {self.stats['success']}\n")
                f.write(f"Failed: {self.stats['failed']}\n\n")
                f.write("ALL DISCOVERED URLS:\n")
                f.write("-" * 60 + "\n")
                for i, link in enumerate(links, 1):
                    f.write(f"{i}. {link['url']}\n")
                    if link.get('title'): f.write(f"   Title: {link['title']}\n")
            print(f"   {Colors.GREEN}✔{Colors.END} Saved Summary: {summary_path.name} ({summary_path.stat().st_size:,} bytes)")
            
            print(f"{Colors.GREEN}✅ All files successfully saved!{Colors.END}\n")
            
        except Exception as e:
            print(f"\n{Colors.FAIL}❌ CRITICAL ERROR during report generation:{Colors.END}")
            print(f"{Colors.FAIL}{e}{Colors.END}")
            traceback.print_exc()


# ═════════════════════════════════════════════════════════════════════════════
# PANEL INTERFACE
# ═════════════════════════════════════════════════════════════════════════════

class CrawlerPanel:
    def __init__(self):
        self.config = {
            'max_depth': 3, 'max_pages': 1000, 'concurrency': 10, 'delay': 1.0,
            'respect_robots': True, 'extract_emails': True, 'extract_phones': True,
            'save_html': False, 'proxy': None, 'output_dir': 'crawl_output',
            'database_name': 'crawler.db', 'login_url': None, 'login_data': {}, 'cookies': None
        }
    
    def clear(self):
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def banner(self):
        return f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║   ██╗   ██╗██╗  ████████╗██╗███╗   ███╗ █████╗ ████████╗███████╗         ║
║   ██║   ██║██║  ╚══██╔══╝██║████╗ ████║██╔══██╗╚══██╔══╝██╔════╝         ║
║   ██║   ██║██║     ██║   ██║██╔████╔██║███████║   ██║   █████╗           ║
║   ██║   ██║██║     ██║   ██║██║╚██╔╝██║██╔══██║   ██║   ██╔══╝           ║
║   ╚██████╔╝███████╗██║   ██║██║ ╚═╝ ██║██║  ██║   ██║   ███████╗         ║
║    ╚═════╝ ╚══════╝╚═╝   ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝         ║
║                                                                          ║
║              {Colors.GREEN}🔥 ULTIMATE WEB CRAWLER 🔥{Colors.CYAN}                              ║
║         Termux Compatible - Login Support                                ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝{Colors.END}
        """
    
    def print_menu(self):
        self.clear()
        print(self.banner())
        print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.BOLD}                          MAIN MENU                                      {Colors.END}{Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}╠══════════════════════════════════════════════════════════════════════════╣{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.END}  {Colors.GREEN}[1]{Colors.END} 🚀 Start Crawling (Quick Mode)                                    {Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.END}  {Colors.GREEN}[2]{Colors.END} 🔐 Crawl with Login (Session Support)                            {Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.END}  {Colors.GREEN}[3]{Colors.END} ⚙️  Advanced Crawling (Custom Settings)                           {Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.END}  {Colors.GREEN}[4]{Colors.END} 🔍 View Current Settings                                          {Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.END}  {Colors.GREEN}[5]{Colors.END} 📝 Configure Settings                                            {Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.END}  {Colors.GREEN}[6]{Colors.END} 📊 View Database / Results                                        {Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.END}  {Colors.GREEN}[7]{Colors.END} 🗑️  Clear Database                                                {Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.END}  {Colors.GREEN}[8]{Colors.END} 📁 Open Output Folder                                             {Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.END}  {Colors.GREEN}[9]{Colors.END} ❌ Exit                                                           {Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════╝{Colors.END}")
        print()
    
    def print_settings(self):
        self.clear()
        print(self.banner())
        print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.BOLD}                       CURRENT SETTINGS                                   {Colors.END}{Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}╠══════════════════════════════════════════════════════════════════════════╣{Colors.END}")
        settings = [
            f"Max Crawl Depth        : {Colors.WARNING}{self.config['max_depth']}{Colors.END}",
            f"Max Pages              : {Colors.WARNING}{self.config['max_pages']}{Colors.END}",
            f"Concurrent Workers     : {Colors.WARNING}{self.config['concurrency']}{Colors.END}",
            f"Request Delay (sec)    : {Colors.WARNING}{self.config['delay']}{Colors.END}",
            f"Respect robots.txt     : {Colors.WARNING}{'✅ YES' if self.config['respect_robots'] else '❌ NO'}{Colors.END}",
            f"Extract Emails         : {Colors.WARNING}{'✅ YES' if self.config['extract_emails'] else '❌ NO'}{Colors.END}",
            f"Extract Phone Numbers  : {Colors.WARNING}{'✅ YES' if self.config['extract_phones'] else '❌ NO'}{Colors.END}",
            f"Save HTML Content      : {Colors.WARNING}{'✅ YES' if self.config['save_html'] else '❌ NO'}{Colors.END}",
            f"Proxy Server           : {Colors.WARNING}{self.config['proxy'] or 'None'}{Colors.END}",
            f"Login URL              : {Colors.WARNING}{self.config['login_url'] or 'None'}{Colors.END}",
            f"Output Directory       : {Colors.WARNING}{self.config['output_dir']}{Colors.END}",
            f"Database               : {Colors.WARNING}{self.config['database_name']}{Colors.END}"
        ]
        for setting in settings:
            print(f"{Colors.CYAN}║{Colors.END}  {setting:<{68}}{Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════╝{Colors.END}")
        print()
        input(f"    {Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def quick_crawl(self):
        self.clear()
        print(self.banner())
        print(f"\n    {Colors.GREEN}🚀 QUICK CRAWL MODE{Colors.END}\n")
        url = input(f"    Enter target URL: ").strip()
        if not url:
            print(f"    {Colors.FAIL}❌ URL cannot be empty!{Colors.END}")
            time.sleep(2)
            return
        if not url.startswith(('http://', 'https://')): url = 'https://' + url
        print(f"\n    {Colors.CYAN}🎯 Target:{Colors.END} {url}")
        print(f"    {Colors.CYAN}📊 Settings:{Colors.END} Depth={self.config['max_depth']}, Pages={self.config['max_pages']}\n")
        if input(f"    Start crawling? (y/n): ").strip().lower() == 'y':
            self.run_crawler(url)
        else:
            print(f"    {Colors.WARNING}⚠️  Cancelled{Colors.END}")
            time.sleep(1)
    
    def crawl_with_login(self):
        self.clear()
        print(self.banner())
        print(f"\n    {Colors.GREEN}🔐 CRAWL WITH LOGIN{Colors.END}\n")
        url = input(f"    Enter target URL (after login): ").strip()
        if not url:
            print(f"    {Colors.FAIL}❌ URL cannot be empty!{Colors.END}")
            time.sleep(2)
            return
        if not url.startswith(('http://', 'https://')): url = 'https://' + url
        login_url = input(f"    Enter login page URL: ").strip()
        print(f"\n    {Colors.CYAN}Enter login credentials:{Colors.END}")
        username_field = input(f"    Username field name [username]: ").strip() or "username"
        password_field = input(f"    Password field name [password]: ").strip() or "password"
        username = input(f"    Your username/email: ").strip()
        password = input(f"    Your password: ").strip()
        print(f"\n    {Colors.CYAN}Optional - Paste cookies from browser (or press Enter):{Colors.END}")
        cookies = input(f"    Cookie string: ").strip()
        
        custom_config = self.config.copy()
        custom_config['login_url'] = login_url
        custom_config['login_data'] = {username_field: username, password_field: password}
        if cookies: custom_config['cookies'] = cookies
        
        print(f"\n    {Colors.GREEN}🎯 Target:{Colors.END} {url}")
        print(f"    {Colors.GREEN}🔐 Login:{Colors.END} {login_url}\n")
        if input(f"    Start crawling with login? (y/n): ").strip().lower() == 'y':
            self.run_crawler(url, custom_config)
        else:
            print(f"    {Colors.WARNING}⚠️  Cancelled{Colors.END}")
            time.sleep(1)
    
    def advanced_crawl(self):
        self.clear()
        print(self.banner())
        print(f"\n    {Colors.GREEN}⚙️  ADVANCED CRAWL MODE{Colors.END}\n")
        url = input(f"    Enter target URL: ").strip()
        if not url:
            print(f"    {Colors.FAIL}❌ URL cannot be empty!{Colors.END}")
            time.sleep(2)
            return
        if not url.startswith(('http://', 'https://')): url = 'https://' + url
        print(f"\n    {Colors.CYAN}Custom settings (press Enter for defaults):{Colors.END}\n")
        depth = input(f"    Max Depth [{self.config['max_depth']}]: ").strip()
        pages = input(f"    Max Pages [{self.config['max_pages']}]: ").strip()
        workers = input(f"    Concurrent Workers [{self.config['concurrency']}]: ").strip()
        delay = input(f"    Delay (sec) [{self.config['delay']}]: ").strip()
        proxy = input(f"    Proxy (http://host:port) [{self.config['proxy'] or 'None'}]: ").strip()
        
        custom_config = self.config.copy()
        if depth: custom_config['max_depth'] = int(depth)
        if pages: custom_config['max_pages'] = int(pages)
        if workers: custom_config['concurrency'] = int(workers)
        if delay: custom_config['delay'] = float(delay)
        if proxy: custom_config['proxy'] = proxy
        
        print(f"\n    {Colors.GREEN}🎯 Target:{Colors.END} {url}")
        print(f"    {Colors.GREEN}📊 Config:{Colors.END} Depth={custom_config['max_depth']}, Pages={custom_config['max_pages']}\n")
        if input(f"    Start crawling? (y/n): ").strip().lower() == 'y':
            self.run_crawler(url, custom_config)
        else:
            print(f"    {Colors.WARNING}⚠️  Cancelled{Colors.END}")
            time.sleep(1)
    
    def run_crawler(self, url, custom_config=None):
        config_dict = custom_config or self.config
        config = CrawlConfig(
            start_url=url, max_depth=config_dict['max_depth'], max_pages=config_dict['max_pages'],
            concurrency=config_dict['concurrency'], delay=config_dict['delay'], respect_robots=config_dict['respect_robots'],
            extract_emails=config_dict['extract_emails'], extract_phones=config_dict['extract_phones'],
            save_html=config_dict['save_html'], use_proxy=config_dict.get('proxy'), login_url=config_dict.get('login_url'),
            login_data=config_dict.get('login_data'), cookies=config_dict.get('cookies'),
            output_dir=config_dict['output_dir'], database_name=config_dict['database_name']
        )
        print(f"\n    {Colors.GREEN}🚀 Starting crawler...{Colors.END}\n")
        crawler = None
        try:
            crawler = UltimateCrawler(config)
            asyncio.run(crawler.start_crawling())
            print(f"\n    {Colors.GREEN}✅ Crawling completed!{Colors.END}")
            print(f"    {Colors.CYAN}📁 Results saved in: {config_dict['output_dir']}/{Colors.END}")
        except KeyboardInterrupt:
            print(f"\n    {Colors.WARNING}🛑 Crawling interrupted by user!{Colors.END}")
            if crawler:
                print(f"    {Colors.CYAN}💾 Forcing final save before exit...{Colors.END}")
                try:
                    crawler.generate_reports()
                except Exception as e:
                    print(f"    {Colors.FAIL}❌ Save error: {e}{Colors.END}")
            print(f"    {Colors.CYAN}📁 Partial results have been saved in: {config_dict['output_dir']}/{Colors.END}")
        except Exception as e:
            print(f"\n    {Colors.FAIL}❌ Error: {e}{Colors.END}")
            if crawler:
                print(f"    {Colors.CYAN}💾 Forcing final save after error...{Colors.END}")
                try:
                    crawler.generate_reports()
                except Exception as save_err:
                    print(f"    {Colors.FAIL}❌ Save error: {save_err}{Colors.END}")
        input(f"\n    {Colors.CYAN}Press Enter to return to Main Menu...{Colors.END}")
    
    def view_database(self):
        self.clear()
        print(self.banner())
        try:
            db = DatabaseManager(self.config['database_name'])
            links = db.get_all_links()
            if not links:
                print(f"\n    {Colors.WARNING}⚠️  No data in database{Colors.END}")
            else:
                print(f"\n    {Colors.GREEN}📊 Total URLs in database: {len(links)}{Colors.END}\n")
                for i, link in enumerate(links[:30], 1):
                    title = link.get('title', 'No title')[:40]
                    print(f"    {Colors.CYAN}{i:3}.{Colors.END} {link['url'][:55]}")
                    if title: print(f"        {Colors.WARNING}Title: {title}{Colors.END}")
                if len(links) > 30: print(f"\n    {Colors.WARNING}... and {len(links) - 30} more URLs{Colors.END}")
        except Exception as e:
            print(f"\n    {Colors.FAIL}❌ Error: {e}{Colors.END}")
        input(f"\n    {Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def clear_database(self):
        self.clear()
        print(self.banner())
        print(f"\n    {Colors.FAIL}⚠️  WARNING: This will delete all crawl data!{Colors.END}\n")
        if input(f"    Type 'DELETE' to confirm: ").strip() == 'DELETE':
            try:
                for f in [self.config['database_name'], 'crawler.log']:
                    if os.path.exists(f):
                        os.remove(f)
                        print(f"    {Colors.GREEN}✅ Deleted: {f}{Colors.END}")
                if os.path.exists(self.config['output_dir']):
                    import shutil
                    shutil.rmtree(self.config['output_dir'])
                    print(f"    {Colors.GREEN}✅ Deleted: {self.config['output_dir']}/{Colors.END}")
                print(f"\n    {Colors.GREEN}✅ All data cleared!{Colors.END}")
            except Exception as e:
                print(f"\n    {Colors.FAIL}❌ Error: {e}{Colors.END}")
        else:
            print(f"\n    {Colors.WARNING}⚠️  Cancelled{Colors.END}")
        time.sleep(2)
    
    def open_output(self):
        self.clear()
        print(self.banner())
        
        output_dir = self.config['output_dir']
        path = Path(output_dir).resolve()
        
        print(f"\n    {Colors.CYAN}📁 Output Directory Information{Colors.END}")
        print(f"    {Colors.CYAN}{'=' * 60}{Colors.END}")
        print(f"    {Colors.GREEN}Configured Name:{Colors.END}  {output_dir}")
        print(f"    {Colors.GREEN}Absolute Path:{Colors.END}    {path}")
        print(f"    {Colors.GREEN}Current Dir:{Colors.END}      {os.getcwd()}")
        print()
        
        if path.exists():
            print(f"    {Colors.GREEN}✅ Directory exists{Colors.END}")
            try:
                files = [f for f in os.listdir(path) if os.path.isfile(path / f)]
                print(f"    {Colors.GREEN}Total Files:{Colors.END}    {len(files)}")
                print()
                
                if files:
                    print(f"    {Colors.GREEN}📄 Files in directory:{Colors.END}\n")
                    total_size = 0
                    for f in sorted(files):
                        full_path = path / f
                        size = full_path.stat().st_size
                        total_size += size
                        size_str = f"{size/1024:.1f} KB" if size >= 1024 else f"{size} B"
                        ext = os.path.splitext(f)[1].upper()
                        print(f"    {Colors.CYAN}📄{Colors.END} {f:<40} {Colors.WARNING}{size_str:>10}{Colors.END}  {Colors.GREEN}{ext}{Colors.END}")
                    
                    print()
                    print(f"    {Colors.GREEN}Total Size:{Colors.END}     {total_size:,} bytes ({total_size/1024:.1f} KB)")
                    
                    print()
                    print(f"    {Colors.CYAN}🔍 Expected Files Check:{Colors.END}")
                    for exp_file in ['crawl_results.json', 'crawl_results.csv', 'all_urls.txt', 'summary.txt']:
                        if exp_file in files:
                            print(f"    {Colors.GREEN}✅{Colors.END} {exp_file}")
                        else:
                            print(f"    {Colors.FAIL}❌{Colors.END} {exp_file} {Colors.WARNING}(missing){Colors.END}")
                else:
                    print(f"    {Colors.WARNING}⚠️  Directory is empty{Colors.END}")
                    print(f"    {Colors.CYAN}💡 Tip: The crawler might have failed to save. Check the console output above for errors.{Colors.END}")
            except Exception as e:
                print(f"    {Colors.FAIL}❌ Error reading directory: {e}{Colors.END}")
        else:
            print(f"    {Colors.FAIL}❌ Directory does not exist{Colors.END}")
            print(f"    {Colors.CYAN}💡 Creating directory...{Colors.END}")
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"    {Colors.GREEN}✅ Created: {path}{Colors.END}")
            except Exception as e:
                print(f"    {Colors.FAIL}❌ Error creating directory: {e}{Colors.END}")
        
        print()
        input(f"    {Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def config_menu(self):
        while True:
            self.clear()
            print(self.banner())
            print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════════╗{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.BOLD}                      CONFIGURATION MENU                                 {Colors.END}{Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}╠══════════════════════════════════════════════════════════════════════════╣{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.END}  {Colors.GREEN}[1]{Colors.END} Max Crawl Depth          : {Colors.WARNING}{self.config['max_depth']}{Colors.END}                             {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.END}  {Colors.GREEN}[2]{Colors.END} Max Pages                : {Colors.WARNING}{self.config['max_pages']}{Colors.END}                          {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.END}  {Colors.GREEN}[3]{Colors.END} Concurrent Workers       : {Colors.WARNING}{self.config['concurrency']}{Colors.END}                             {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.END}  {Colors.GREEN}[4]{Colors.END} Request Delay            : {Colors.WARNING}{self.config['delay']}{Colors.END}                            {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.END}  {Colors.GREEN}[5]{Colors.END} Respect robots.txt       : {Colors.WARNING}{'ON' if self.config['respect_robots'] else 'OFF'}{Colors.END}                            {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.END}  {Colors.GREEN}[6]{Colors.END} Extract Emails           : {Colors.WARNING}{'ON' if self.config['extract_emails'] else 'OFF'}{Colors.END}                            {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.END}  {Colors.GREEN}[7]{Colors.END} Extract Phone Numbers    : {Colors.WARNING}{'ON' if self.config['extract_phones'] else 'OFF'}{Colors.END}                            {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.END}  {Colors.GREEN}[8]{Colors.END} Save HTML Content        : {Colors.WARNING}{'ON' if self.config['save_html'] else 'OFF'}{Colors.END}                            {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.END}  {Colors.GREEN}[9]{Colors.END} Set Proxy                : {Colors.WARNING}{self.config['proxy'] or 'None'}{Colors.END}                        {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.END}  {Colors.GREEN}[10]{Colors.END} 🔙 Back to Main Menu                                          {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════════════════╝{Colors.END}")
            print()
            
            choice = input(f"    {Colors.GREEN}Enter choice (1-10): {Colors.END}").strip()
            if choice == '1':
                v = input(f"    Max Depth [{self.config['max_depth']}]: ").strip()
                if v: self.config['max_depth'] = int(v)
            elif choice == '2':
                v = input(f"    Max Pages [{self.config['max_pages']}]: ").strip()
                if v: self.config['max_pages'] = int(v)
            elif choice == '3':
                v = input(f"    Workers [{self.config['concurrency']}]: ").strip()
                if v: self.config['concurrency'] = int(v)
            elif choice == '4':
                v = input(f"    Delay [{self.config['delay']}]: ").strip()
                if v: self.config['delay'] = float(v)
            elif choice == '5': self.config['respect_robots'] = not self.config['respect_robots']
            elif choice == '6': self.config['extract_emails'] = not self.config['extract_emails']
            elif choice == '7': self.config['extract_phones'] = not self.config['extract_phones']
            elif choice == '8': self.config['save_html'] = not self.config['save_html']
            elif choice == '9': self.config['proxy'] = input(f"    Proxy (http://host:port): ").strip() or None
            elif choice == '10': break
    
    def run(self):
        while True:
            self.print_menu()
            choice = input(f"    {Colors.GREEN}Enter your choice (1-9): {Colors.END}").strip()
            if choice == '1': self.quick_crawl()
            elif choice == '2': self.crawl_with_login()
            elif choice == '3': self.advanced_crawl()
            elif choice == '4': self.print_settings()
            elif choice == '5': self.config_menu()
            elif choice == '6': self.view_database()
            elif choice == '7': self.clear_database()
            elif choice == '8': self.open_output()
            elif choice == '9':
                self.clear()
                print(f"\n    {Colors.GREEN}👋 Goodbye!{Colors.END}\n")
                print(f"    {Colors.CYAN}🔗 Visit: {Colors.BOLD}https://t.me/CardSELLER789{Colors.END}\n")
                break
            else:
                print(f"    {Colors.FAIL}❌ Invalid choice!{Colors.END}")
                time.sleep(1)


# ═════════════════════════════════════════════════════════════════════════════
# TERMUX / ANDROID SMART LINK OPENER
# ═════════════════════════════════════════════════════════════════════════════

def open_link_in_android(url):
    """
    Smart link opener for Android/Termux:
    1. If Telegram app is installed -> Opens directly in Telegram
    2. If Telegram is not installed -> Opens in default browser
    """
    # Step 1: Try to open in Telegram app directly using package name
    # -p flag specifies the package name for Telegram
    telegram_result = os.system(f"am start -a android.intent.action.VIEW -d '{url}' -p org.telegram.messenger >/dev/null 2>&1")
    
    # Step 2: If Telegram failed (not installed), fallback to default browser
    if telegram_result != 0:
        os.system(f"am start -a android.intent.action.VIEW -d '{url}' >/dev/null 2>&1")


def main():
    telegram_link = "https://t.me/CardSELLER789"
    admin_link = "https://t.me/bgxhost"
    
    # 1. Tool Execute হওয়ার সময় Redirect/Show
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}🔗 Join our Telegram Channel:{Colors.END}")
    print(f"{Colors.BOLD}{Colors.YELLOW}{telegram_link}{Colors.END}")
    print(f"{Colors.GREEN}👑 Admin / License Support:{Colors.END}")
    print(f"{Colors.BOLD}{Colors.YELLOW}{admin_link}{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")
    
    open_link_in_android(telegram_link)

    # --- LICENSE CHECK INTEGRATION ---
    if not check_and_prompt_license():
        print(f"{Colors.FAIL}❌ Access Denied. Exiting...{Colors.END}")
        input("Press Enter to exit...")
        sys.exit(1)
    # -------------------------------

    try:
        panel = CrawlerPanel()
        panel.run()
    except KeyboardInterrupt:
        pass
    finally:
        # 2. Tool Exit হওয়ার সময় (স্বাভাবিক বা Ctrl+C যাই হোক) Redirect/Show
        print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.GREEN}🔗 Join our Telegram Channel:{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}{telegram_link}{Colors.END}")
        print(f"{Colors.GREEN}👑 Admin / License Support:{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}{admin_link}{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")
        
        open_link_in_android(telegram_link)


if __name__ == '__main__':
    main()
