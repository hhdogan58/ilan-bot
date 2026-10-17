import os
from scraper import yeni_ilani_bul, paylasilanlari_kaydet, paylasilanlari_yukle

def main():
    print("[*] Bot başlatılıyor...")
    
    # Yeni ilanı bul
    ilan = yeni_ilani_bul()
    
    if ilan:
        print(f"[+] Paylaşılacak İlan Seçildi: {ilan['baslik']}")
        print(f"[i] Link: {ilan['link']}")
        
        # Burada Instagram paylaşım fonksiyonun çalışacak (bot.py vb.)
        # Örnek: instagram_paylas(ilan)
        
        # Paylaşılanlara ekle ve kaydet
        paylasilanlar = paylasilanlari_yukle()
        paylasilanlar.append(ilan['id'])
        paylasilanlari_kaydet(paylasilanlar)
        print("[+] İlan başarıyla işlendi ve geçmişe kaydedildi.")
    else:
        print("[-] Paylaşılacak yeni ilan bulunamadı.")

if __name__ == "__main__":
    main()