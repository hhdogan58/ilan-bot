import requests
from bs4 import BeautifulSoup
import json
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Connection": "keep-alive"
}

DOSYA_PAYLASILANLAR = "paylasilanlar.json"

def paylasilanlari_yukle():
    if os.path.exists(DOSYA_PAYLASILANLAR):
        try:
            with open(DOSYA_PAYLASILANLAR, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def yeni_ilani_bul():
    url = "https://kamuilan.sbb.gov.tr"
    print("[*] SBB ilanları taranıyor...")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        # HTTP hata kodunu detaylı görmek için raise_for_status yerine status kodunu kontrol edelim:
        print(f"[i] Sunucu Yanıt Kodu: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[-] Site reddetti veya engelledi! Kod: {response.status_code}")
            return None
            
        print("[+] Siteye başarıyla erişildi, içerik analiz ediliyor...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Sitedeki tüm linkleri ve başlıkları test amaçlı kontrol edelim
        linkler = soup.find_all('a', href=True)
        print(f"[i] Sayfada toplam {len(linkler)} adet bağlantı bulundu.")
        
        paylasilanlar = paylasilanlari_yukle()
        
        for kart in linkler:
            baslik = kart.get_text(strip=True)
            link = kart.get('href')
            
            # İlan niteliği taşıyan anlamlı bir başlık ve uzunluk arayalım
            if not link or len(baslik) < 20:
                continue
                
            if link.startswith('/'):
                link = f"https://kamuilan.sbb.gov.tr{link}"
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