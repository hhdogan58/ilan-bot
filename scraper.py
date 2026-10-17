import requests
from bs4 import BeautifulSoup

def test_sbb_scrape():
    url = "https://kamuilan.sbb.gov.tr/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print("[*] kamuilan.sbb.gov.tr adresine istek atılıyor...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"[+] Bağlantı Durum Kodu (Status Code): {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Sayfa başlığını yazdır
            title = soup.title.string if soup.title else "Başlık bulunamadı"
            print(f"[+] Sayfa Başlığı: {title.strip()}")
            
            print("\n[*] Sayfada bulunan bazı bağlantılar ve başlıklar analiz ediliyor:")
            print("-" * 50)
            
            # Sayfedaki tüm linkleri tarayıp ilan benzeri metinleri listeleyelim
            links = soup.find_all('a')
            count = 0
            for link in links:
                text = link.get_text(strip=True)
                href = link.get('href')
                # Kısa veya boş olmayan, anlamlı uzunluktaki metinleri filtrele
                if text and len(text) > 15:
                    print(f"-> Başlık: {text[:70]}...")
                    print(f"   Link: {href}")
                    print("-" * 30)
                    count += 1
                    if count >= 10:  # İlk 10 örneği gösterelim
                        break
        else:
            print(f"[-] Siteye erişilemedi. Kod: {response.status_code}")
            
    except Exception as e:
        print("[-] İstek sırasında bir hata oluştu:", e)

if __name__ == "__main__":
    test_sbb_scrape()