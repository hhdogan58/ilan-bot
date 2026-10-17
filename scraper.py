from curl_cffi import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://ilan.memurlar.net/"
DOSYA_PAYLASILANLAR = "paylasilanlar.json"

def paylasilanlari_yukle():
    if os.path.exists(DOSYA_PAYLASILANLAR):
        try:
            with open(DOSYA_PAYLASILANLAR, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def paylasilanlari_kaydet(paylasilanlar_listesi):
    with open(DOSYA_PAYLASILANLAR, "w", encoding="utf-8") as f:
        json.dump(paylasilanlar_listesi, f, ensure_ascii=False, indent=4)

def yeni_ilani_bul():
    print("[*] https://ilan.memurlar.net/ ana sayfası taranıyor...")
    
    try:
        response = requests.get(URL, impersonate="chrome", timeout=20)
        print(f"[i] Sunucu Yanıt Kodu: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[-] Sayfaya erişilemedi! Kod: {response.status_code}")
            return None
            
        print("[+] Sayfa başarıyla getirildi, ilanlar analiz ediliyor...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # İlan ana sayfasındaki tüm linkleri tarıyoruz
        linkler = soup.find_all('a', href=True)
        paylasilanlar = paylasilanlari_yukle()
        
        for link_tag in linkler:
            baslik = link_tag.get_text(strip=True)
            link = link_tag['href']
            
            # Anlamlı başlık ve ilan içeren bağlantıları filtrele
            if not link or len(baslik) < 15:
                continue
                
            # İlan detay sayfalarına ait link yapıları
            if '/ilan/' in link.lower() or 'detay' in link.lower():
                if link.startswith('/'):
                    link = f"https://ilan.memurlar.net{link}"
                elif not link.startswith('http'):
                    continue
                    
                ilan_id = link
                
                if ilan_id not in paylasilanlar:
                    print(f"[+] Yeni ilan bulundu: {baslik[:60]}...")
                    return {
                        "id": ilan_id,
                        "baslik": baslik,
                        "link": link,
                        "kurum": "Kamu Kurumu",
                        "tarih": "Güncel"
                    }
                
        print("[-] Paylaşılacak yeni ilan bulunamadı.")
        return None

    except Exception as e:
        print(f"[-] Bağlantı hatası oluştu: {e}")
        return None

if __name__ == "__main__":
    yeni_ilani_bul()