#!/usr/bin/env python3
"""
screenshot_engine.py
Professional screenshot and evidence capture engine.
Takes full-page screenshots, mobile views, and organizes evidence for H1 reports.
"""

import os
import time
import json
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import io

class ScreenshotEngine:
    def __init__(self, output_dir="evidence"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.driver = None
        self.evidence_log = []
    
    def init_driver(self, headless=True):
        """Initialize Chrome WebDriver with optimal settings"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")
        
        # Essential arguments for stability
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        # Performance
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            print("[+] Chrome WebDriver initialized")
        except Exception as e:
            print(f"[!] Failed to initialize Chrome: {e}")
            print("    Make sure chromedriver is installed and in PATH")
            raise
    
    def capture_fullpage(self, url, filename_prefix="screenshot"):
        """Capture full-page screenshot (desktop view)"""
        if not self.driver:
            self.init_driver()
        
        try:
            print(f"[*] Loading {url}...")
            self.driver.get(url)
            
            # Wait for page load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_at_least_one_of(
                    (By.TAG_NAME, "body")
                )
            )
            time.sleep(2)  # Additional wait for dynamic content
            
            # Get full page dimensions
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            # Set window size to capture full page
            self.driver.set_window_size(1920, total_height)
            time.sleep(1)
            
            # Take screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_fullpage_{timestamp}.png"
            filepath = self.output_dir / filename
            
            self.driver.save_screenshot(str(filepath))
            
            evidence = {
                "type": "screenshot",
                "view": "desktop_fullpage",
                "url": url,
                "filename": filename,
                "filepath": str(filepath),
                "timestamp": datetime.utcnow().isoformat(),
                "dimensions": f"1920x{total_height}"
            }
            self.evidence_log.append(evidence)
            
            print(f"[+] Captured: {filename}")
            return filepath
            
        except Exception as e:
            print(f"[!] Screenshot failed: {e}")
            return None
    
    def capture_mobile(self, url, filename_prefix="screenshot"):
        """Capture mobile view screenshot"""
        if not self.driver:
            self.init_driver()
        
        try:
            # Set mobile viewport
            mobile_emulation = {
                "deviceMetrics": {"width": 375, "height": 812, "pixelRatio": 3.0},
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
            }
            
            # Restart driver with mobile settings
            self.driver.quit()
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
            self.driver = webdriver.Chrome(options=chrome_options)
            
            print(f"[*] Loading {url} (mobile view)...")
            self.driver.get(url)
            time.sleep(2)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_mobile_{timestamp}.png"
            filepath = self.output_dir / filename
            
            self.driver.save_screenshot(str(filepath))
            
            evidence = {
                "type": "screenshot",
                "view": "mobile",
                "url": url,
                "filename": filename,
                "filepath": str(filepath),
                "timestamp": datetime.utcnow().isoformat(),
                "dimensions": "375x812"
            }
            self.evidence_log.append(evidence)
            
            print(f"[+] Captured mobile: {filename}")
            return filepath
            
        except Exception as e:
            print(f"[!] Mobile screenshot failed: {e}")
            return None
    
    def capture_element(self, url, css_selector, filename_prefix="element"):
        """Capture specific element on page"""
        if not self.driver:
            self.init_driver()
        
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
            )
            
            element = self.driver.find_element(By.CSS_SELECTOR, css_selector)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_element_{timestamp}.png"
            filepath = self.output_dir / filename
            
            element.screenshot(str(filepath))
            
            evidence = {
                "type": "screenshot",
                "view": "element",
                "url": url,
                "selector": css_selector,
                "filename": filename,
                "filepath": str(filepath),
                "timestamp": datetime.utcnow().isoformat()
            }
            self.evidence_log.append(evidence)
            
            print(f"[+] Captured element: {filename}")
            return filepath
            
        except Exception as e:
            print(f"[!] Element screenshot failed: {e}")
            return None
    
    def capture_network_evidence(self, url, filename_prefix="network"):
        """Capture network requests/responses"""
        if not self.driver:
            self.init_driver()
        
        try:
            # Enable network logging
            self.driver.execute_cdp_cmd("Network.enable", {})
            
            # Navigate to URL
            self.driver.get(url)
            time.sleep(3)
            
            # Get network logs
            logs = self.driver.execute_script(
                "return window.performance.getEntries();"
            )
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_network_{timestamp}.json"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(logs, f, indent=2)
            
            evidence = {
                "type": "network_log",
                "url": url,
                "filename": filename,
                "filepath": str(filepath),
                "timestamp": datetime.utcnow().isoformat(),
                "entries_count": len(logs)
            }
            self.evidence_log.append(evidence)
            
            print(f"[+] Captured network log: {filename} ({len(logs)} entries)")
            return filepath
            
        except Exception as e:
            print(f"[!] Network capture failed: {e}")
            return None
    
    def capture_http_response(self, url, filename_prefix="response"):
        """Capture raw HTTP response"""
        import requests
        
        try:
            print(f"[*] Fetching HTTP response from {url}...")
            resp = requests.get(url, timeout=15, allow_redirects=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save headers
            headers_file = f"{filename_prefix}_headers_{timestamp}.txt"
            headers_path = self.output_dir / headers_file
            with open(headers_path, 'w') as f:
                f.write(f"URL: {url}\n")
                f.write(f"Status: {resp.status_code}\n")
                f.write(f"Time: {datetime.utcnow().isoformat()}\n\n")
                f.write("=== Response Headers ===\n")
                for k, v in resp.headers.items():
                    f.write(f"{k}: {v}\n")
            
            # Save body (truncated if too large)
            body_file = f"{filename_prefix}_body_{timestamp}.txt"
            body_path = self.output_dir / body_file
            with open(body_path, 'w', encoding='utf-8') as f:
                content = resp.text[:100000]  # Limit to 100KB
                f.write(content)
            
            evidence = {
                "type": "http_response",
                "url": url,
                "status_code": resp.status_code,
                "headers_file": headers_file,
                "body_file": body_file,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.evidence_log.append(evidence)
            
            print(f"[+] Captured HTTP response: {headers_file}, {body_file}")
            return headers_path, body_path
            
        except Exception as e:
            print(f"[!] HTTP capture failed: {e}")
            return None, None
    
    def generate_evidence_report(self, target_url):
        """Generate organized evidence report"""
        report = {
            "target": target_url,
            "timestamp": datetime.utcnow().isoformat(),
            "evidence_count": len(self.evidence_log),
            "evidence": self.evidence_log
        }
        
        report_file = self.output_dir / f"evidence_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n[+] Evidence report saved: {report_file}")
        print(f"[+] Total evidence items: {len(self.evidence_log)}")
        
        return report_file
    
    def cleanup(self):
        """Close driver and cleanup"""
        if self.driver:
            self.driver.quit()
            print("[+] WebDriver closed")

def main():
    """CLI for screenshot engine"""
    import argparse
    parser = argparse.ArgumentParser(description="Screenshot & Evidence Capture Engine")
    parser.add_argument("url", help="Target URL")
    parser.add_argument("--fullpage", action="store_true", help="Capture full page")
    parser.add_argument("--mobile", action="store_true", help="Capture mobile view")
    parser.add_argument("--element", help="CSS selector for element capture")
    parser.add_argument("--network", action="store_true", help="Capture network logs")
    parser.add_argument("--http", action="store_true", help="Capture HTTP response")
    parser.add_argument("--all", action="store_true", help="Capture all evidence types")
    parser.add_argument("--output", default="evidence", help="Output directory")
    
    args = parser.parse_args()
    
    engine = ScreenshotEngine(output_dir=args.output)
    
    try:
        if args.all:
            print("\n[+] Capturing all evidence types...")
            engine.capture_fullpage(args.url)
            engine.capture_mobile(args.url)
            engine.capture_network_evidence(args.url)
            engine.capture_http_response(args.url)
        else:
            if args.fullpage:
                engine.capture_fullpage(args.url)
            if args.mobile:
                engine.capture_mobile(args.url)
            if args.element:
                engine.capture_element(args.url, args.element)
            if args.network:
                engine.capture_network_evidence(args.url)
            if args.http:
                engine.capture_http_response(args.url)
        
        # Generate evidence report
        engine.generate_evidence_report(args.url)
        
    finally:
        engine.cleanup()

if __name__ == "__main__":
    main()