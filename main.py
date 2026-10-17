import os
from scraper import yeni_ilani_bul, paylasilanlari_kaydet, paylasilanlari_yukle
from bot import post_to_instagram

def main():
    print("[*] Bot başlatılıyor...")
    
    # 1. Yeni ilanı bul
    ilan = yeni_ilani_bul()
    
    if ilan:
        print(f"[+] Paylaşılacak İlan Seçildi: {ilan['baslik']}")
        print(f"[i] Link: {ilan['link']}")
        
        # Instagram'da paylaşılacak görsel (İstersen sabit bir kamu/ofis görseli kullanabilirsin)
        image_url = "https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=1080"
        
        # Instagram Açıklama Metni (Caption)
        caption = f"📢 YENİ KAMU İLANI!\n\n" \
                  f"📌 {ilan['baslik']}\n\n" \
                  f"🔗 Detaylar için bağlantı:\n{ilan['link']}\n\n" \
                  f"#kamuilanları #memuralımı #işilanı #kpss #kamupersoneli"
        
        print("[*] Instagram gönderisi tetikleniyor...")
        basarili = post_to_instagram(image_url, caption)
        
        if basarili:
            # Paylaşılanlara ekle ve kaydet ki bir daha mükerrer paylaşılmasın
            paylasilanlar = paylasilanlari_yukle()
            paylasilanlar.append(ilan['id'])
            paylasilanlari_kaydet(paylasilanlar)
            print("[+] İlan başarıyla Instagram'da paylaşıldı ve geçmişe kaydedildi.")
        else:
            print("[-] Instagram paylaşımı başarısız oldu, tekrar denenecek.")
    else:
        print("[-] Paylaşılacak yeni ilan bulunamadı.")

if __name__ == "__main__":
    main()