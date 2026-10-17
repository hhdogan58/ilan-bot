import json
import os
from playwright.sync_api import sync_playwright

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
    print("[*] Playwright ile gerçek tarayıcı (Chromium) başlatılıyor...")
    
    with sync_playwright() as p:
        # Tarayıcıyı arka planda (headless) açıyoruz
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        try:
            print(f"[i] SBB sayfasına bağlanılıyor: {URL}")
            # Cloudflare korumasını geçmesi için sayfanın tam yüklenmesini bekliyoruz
            page.goto(URL, timeout=60000, wait_until="networkidle")
            
            # Ekstra güvenlik kontrolü için 4 saniye bekleme
            page.wait_for_timeout(4000)
            
            print("[+] Sayfa yüklendi, ilanlar taranıyor...")
            
            # Sayfadaki tüm bağlantıları ve başlıkları topluyoruz
            ilanlar_data = page.evaluate("""() => {
                const links = Array.from(document.querySelectorAll('a'));
                return links.map(a => ({
                    baslik: a.innerText.trim(),
                    href: a.href
                })).filter(item => item.baslik.length > 15 && (item.href.includes('ilan') || item.href.includes('detay') || item.href.includes('Goster')));
            }""")
            
            browser.close()
            
            paylasilanlar = paylasilanlari_yukle()
            
            for ilan in ilanlar_data:
                baslik = ilan['baslik']
                link = ilan['href']
                
                ilan_id = link
                
                if ilan_id not in paylasilanlar:
                    print(f"[+] SBB'de yeni ilan bulundu: {baslik[:60]}...")
                    gorsel_url = "https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=1080"
                    
                    return {
                        "id": ilan_id,
                        "baslik": baslik,
                        "link": link,
                        "gorsel": gorsel_url,
                        "kurum": "Resmi Kamu Kurumu (SBB)",
                        "tarih": "Güncel"
                    }
                    
            print("[-] SBB'de paylaşılacak yeni ilan bulunamadı.")
            return None

        except Exception as e:
            print(f"[-] Playwright tarama hatası: {e}")
            try:
                browser.close()
            except:
                pass
            return None

if __name__ == "__main__":
    yeni_ilani_bul()