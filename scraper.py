import requests
from bs4 import BeautifulSoup
import json
import os

# Gerçek bir Windows Chrome tarayıcısının kimlik bilgileri (Cloudflare / WAF engellerini aşmak için)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Connection": "keep-alive"
}

DOSYA_PAYLASILANLAR = "paylasilanlar.json"

def paylasilanlari_yukle():
    """Daha önce paylaşılan ilanların ID/link listesini yükler."""
    if os.path.exists(DOSYA_PAYLASILANLAR):
        try:
            with open(DOSYA_PAYLASILANLAR, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def paylasilanlari_kaydet(paylasilanlar_listesi):
    """Paylaşılan ilanları JSON dosyasına kaydeder."""
    with open(DOSYA_PAYLASILANLAR, "w", encoding="utf-8") as f:
        json.dump(paylasilanlar_listesi, f, ensure_ascii=False, indent=4)

def yeni_ilani_bul():
    """SBB ilan sitesini tarar ve daha önce paylaşılmamış ilk yeni ilanı döndürür."""
    url = "https://kamuilan.sbb.gov.tr"
    print("[*] SBB ilanları taranıyor...")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        print("[+] Siteye başarıyla erişildi, içerik analiz ediliyor...")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # SİTENİN HTML YAPISINA GÖRE GÜNCELLENECEK ALAN:
        # Sitedeki ilan kartlarını/satırlarını seçen CSS seçici (Örn: div.ilan-item, tr.ilan-row vb.)
        # Buradaki etiketleri sitenin güncel HTML yapısına göre doğrulayabilirsiniz.
        ilan_kartlari = soup.find_all('div', class_='ilan-item') # veya 'tr', 'a' vb.
        
        if not ilan_kartlari:
            # Alternatif genel arama denemesi (Eğer özel class bulunamazsa bağlantıları tarar)
            ilan_kartlari = soup.find_all('a', href=True)

        paylasilanlar = paylasilanlari_yukle()
        
        for kart in ilan_kartlari:
            # İlan başlığı ve detay linkini çekme mantığı
            baslik = kart.get_text(strip=True)
            link = kart.get('href') if kart.name == 'a' else (kart.find('a')['href'] if kart.find('a') else None)
            
            if not link or len(baslik) < 15:
                continue
                
            # Eğer link tam adres değilse tamamla
            if link.startswith('/'):
                link = f"https://kamuilan.sbb.gov.tr{link}"
                
            # Benzersiz bir ID olarak linki veya başlığı kullanalım
            ilan_id = link
            
            if ilan_id not in paylasilanlar:
                print([+] Yeni ilan bulundu: {baslik[:50]}...)
                return {
                    "id": ilan_id,
                    "baslik": baslik,
                    "link": link,
                    "kurum": "Kamu Kurumu", # Siteden çekilen yapıya göre detaylandırılabilir
                    "tarih": "Güncel"
                }
                
        print("[-] Paylaşılacak yeni ilan bulunamadı (Tüm ilanlar zaten paylaşılmış).")
        return None

    except Exception as e:
        print(f"[-] Siteye erişilemedi veya hata oluştu: {e}")
        return None

if __name__ == "__main__":
    # Manuel test için
    yeni_ilani_bul()