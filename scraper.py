from curl_cffi import requests
from bs4 import BeautifulSoup
import json
import os

# Resmi SBB İlan Portalı
URL = "https://kamuilan.sbb.gov.tr/"
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
    print("[*] Resmi SBB İlan Portalı (kamuilan.sbb.gov.tr) taranıyor...")
    
    try:
        response = requests.get(URL, impersonate="chrome", timeout=25)
        print(f"[i] SBB Sunucu Yanıt Kodu: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[-] SBB sayfasına erişilemedi! Kod: {response.status_code}")
            return None
            
        print("[+] SBB ana sayfası başarıyla getirildi, ilanlar analiz ediliyor...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # SBB sitesindeki ilan bağlantılarını ve kartlarını tarıyoruz
        linkler = soup.find_all('a', href=True)
        paylasilanlar = paylasilanlari_yukle()
        
        for link_tag in linkler:
            baslik = link_tag.get_text(strip=True)
            link = link_tag['href']
            
            # Anlamlı uzunlukta ve ilan barındıran bağlantıları filtrele
            if not link or len(baslik) < 15:
                continue
                
            if 'ilan' in link.lower() or 'detay' in link.lower() or 'Goster' in link:
                # SBB link yapısını tam adrese dönüştürme
                if link.startswith('http'):
                    ilan_url = link
                elif link.startswith('/'):
                    ilan_url = f"https://kamuilan.sbb.gov.tr{link}"
                else:
                    ilan_url = f"https://kamuilan.sbb.gov.tr/{link}"
                    
                ilan_id = ilan_url
                
                if ilan_id not in paylasilanlar:
                    print(f"[+] SBB'de yeni ilan bulundu: {baslik[:60]}...")
                    
                    # Şık kurumsal varsayılan görsel
                    gorsel_url = "https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=1080"
                    
                    return {
                        "id": ilan_id,
                        "baslik": baslik,
                        "link": ilan_url,
                        "gorsel": gorsel_url,
                        "kurum": "Resmi Kamu Kurumu (SBB)",
                        "tarih": "Güncel"
                    }
                
        print("[-] SBB'de paylaşılacak yeni ilan bulunamadı.")
        return None

    except Exception as e:
        print(f"[-] SBB bağlantı hatası oluştu: {e}")
        return None

if __name__ == "__main__":
    yeni_ilani_bul()