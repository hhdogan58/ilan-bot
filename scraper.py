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
        response = requests.get(URL, impersonate="chrome", timeout=25)
        print(f"[i] Sunucu Yanıt Kodu: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[-] Sayfaya erişilemedi! Kod: {response.status_code}")
            return None
            
        print("[+] Sayfa başarıyla getirildi, ilanlar analiz ediliyor...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        linkler = soup.find_all('a', href=True)
        paylasilanlar = paylasilanlari_yukle()
        
        for link_tag in linkler:
            baslik = link_tag.get_text(strip=True)
            link = link_tag['href']
            
            if not link or len(baslik) < 15:
                continue
                
            if '/ilan/' in link.lower() or 'detay' in link.lower():
                # Kesin ve temiz URL oluşturma (Çift domain/slash hatası önleme)
                if link.startswith('http'):
                    ilan_url = link
                elif link.startswith('/'):
                    ilan_url = f"https://ilan.memurlar.net{link}"
                else:
                    ilan_url = f"https://ilan.memurlar.net/{link}"
                
                # Eğer link içinde mükerrer domain oluştuysa temizle
                ilan_url = ilan_url.replace("https://ilan.memurlar.net//ilan.memurlar.net/", "https://ilan.memurlar.net/")
                
                ilan_id = ilan_url
                
                if ilan_id not in paylasilanlar:
                    print(f"[+] Yeni ilan bulundu: {baslik[:60]}...")
                    gorsel_url = "https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=1080"
                    
                    return {
                        "id": ilan_id,
                        "baslik": baslik,
                        "link": ilan_url,
                        "gorsel": gorsel_url,
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