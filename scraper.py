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

def ilan_detay_gorselini_bul(detay_url):
    """İlanın detay sayfasına giderek sayfadaki resmi / afişi bulur."""
    try:
        print(f"[*] İlan detay sayfası taranıyor: {detay_url}")
        response = requests.get(detay_url, impersonate="chrome", timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # İlan detay sayfasındaki içerik alanında yer alan görselleri arıyoruz
            # Genellikle ilan detay fotoğrafları içerik div'leri içinde yer alır
            img_tag = soup.find('div', class_='ilan-detay') or soup.find('article') or soup.find('main')
            if img_tag:
                img = img_tag.find('img', src=True)
                if img:
                    gorsel_url = img['src']
                    if gorsel_url.startswith('/'):
                        gorsel_url = f"https://ilan.memurlar.net{gorsel_url}"
                    elif not gorsel_url.startswith('http'):
                        gorsel_url = f"https://{gorsel_url}"
                    print(f"[+] İlanın orijinal görseli bulundu: {gorsel_url}")
                    return gorsel_url
                    
            # Alternatif olarak sayfadaki ilk büyük resmi seç
            all_imgs = soup.find_all('img', src=True)
            for img in all_imgs:
                src = img['src']
                if 'ilan' in src.lower() or 'upload' in src.lower() or 'images' in src.lower():
                    if src.startswith('/'):
                        return f"https://ilan.memurlar.net{src}"
                    elif src.startswith('http'):
                        return src
                        
    except Exception as e:
        print(f"[-] Detay görseli alınırken hata oluştu: {e}")
        
    # Eğer detayda görsel bulunamazsa varsayılan şık bir kurumsal görsel dön
    return "https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=1080"

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
        
        linkler = soup.find_all('a', href=True)
        paylasilanlar = paylasilanlari_yukle()
        
        for link_tag in linkler:
            baslik = link_tag.get_text(strip=True)
            link = link_tag['href']
            
            if not link or len(baslik) < 15:
                continue
                
            if '/ilan/' in link.lower() or 'detay' in link.lower():
                if link.startswith('/'):
                    link = f"https://ilan.memurlar.net{link}"
                elif not link.startswith('http'):
                    continue
                    
                ilan_id = link
                
                if ilan_id not in paylasilanlar:
                    print(f"[+] Yeni ilan bulundu: {baslik[:60]}...")
                    
                    # İlanın kendi içindeki gerçek görseli çekiyoruz
                    gercek_gorsel_url = ilan_detay_gorselini_bul(link)
                    
                    return {
                        "id": ilan_id,
                        "baslik": baslik,
                        "link": link,
                        "gorsel": gercek_gorsel_url,
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