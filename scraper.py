import requests
from bs4 import BeautifulSoup
import json
import os

# Engelsiz ve doğrudan veri çeken açık RSS kaynağı
RSS_URL = "https://www.memurlar.net/xml/news.xml"

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
    print("[*] Engelsiz kaynak taranıyor...")
    
    try:
        response = requests.get(RSS_URL, timeout=15)
        print(f"[i] Sunucu Yanıt Kodu: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[-] Kaynağa erişilemedi! Kod: {response.status_code}")
            return None
            
        print("[+] Kaynaktan veriler başarıyla alındı, analiz ediliyor...")
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        print(f"[i] Akışta toplam {len(items)} adet içerik bulundu.")
        paylasilanlar = paylasilanlari_yukle()
        
        for item in items:
            baslik = item.title.text if item.title else ""
            link = item.link.text if item.link else ""
            
            if not link or len(baslik) < 10:
                continue
                
            ilan_id = link
            
            if ilan_id not in paylasilanlar:
                print(f"[+] Yeni ilan bulundu: {baslik[:60]}...")
                return {
                    "id": ilan_id,
                    "baslik": baslik,
                    "link": link,
                    "kurum": "Kamu / Memur Alımı",
                    "tarih": "Güncel"
                }
                
        print("[-] Paylaşılacak yeni ilan bulunamadı.")
        return None

    except Exception as e:
        print(f"[-] Bağlantı hatası oluştu: {e}")
        return None

if __name__ == "__main__":
    yeni_ilani_bul()