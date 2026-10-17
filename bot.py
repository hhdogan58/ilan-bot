import os
import time
import requests

# Token'ın başına 'r' harfi koyarak ham metin (raw string) olarak tanımlıyoruz
ACCESS_TOKEN = r"EAAdx2vMKhsQBSzL14RS5gvhKlJExuZAxViuNThTBFEAqljitBtBvQcYSGoDcnZCqjIjHnAuYBnlnHqo9b49GGwlS5u5j6dWxiuH5FSM7ooIWbHtPKVNQb5mdb6ZBcUrQsMxPkky2B2gjtdk8NZBEUlqgV2if49U2S3hgMfzhzA8SzjZAhWUpRAhfvcFDIJVkF7LamqOZAd7HSM01i92PTe6YF3VCXnzZCVCoEb5sf98t1VFiBDlkbndHIPOTXzrVih3PZAhoUjlleUZAo"
INSTAGRAM_ACCOUNT_ID = "17841459578691000"


def post_to_instagram(image_url, caption):
    """Instagram Graph API kullanarak görsel ve açıklama paylaşır."""
    base_url = f"https://graph.facebook.com/v26.0/{INSTAGRAM_ACCOUNT_ID}"

    # 1. Aşama: Medya Konteyneri Oluştur
    container_url = f"{base_url}/media"
    payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN,
    }

    print("[*] Medya konteyneri oluşturuluyor...")
    response = requests.post(container_url, data=payload)
    res_data = response.json()

    if "id" not in res_data:
        print(f"[-] Hata (Konteyner): {res_data}")
        return False

    creation_id = res_data["id"]
    print(f"[+] Başarılı! Konteyner ID: {creation_id}")

    # Instagram'ın görseli işlemesi için kısa bir süre bekliyoruz
    print("[*] Instagram görseli işliyor, 5 saniye bekleniyor...")
    time.sleep(5)

    # 2. Aşama: Konteyneri Yayınla
    publish_url = f"{base_url}/media_publish"
    publish_payload = {
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN,
    }

    print("[*] Gönderi yayınlanıyor...")
    pub_response = requests.post(publish_url, data=publish_payload)
    pub_data = pub_response.json()

    if "id" in pub_data:
        print(f"[SUCCESS] Harika! Gönderi yayınlandı. ID: {pub_data['id']}")
        return True
    else:
        print(f"[-] Hata (Yayınlama): {pub_data}")
        return False


if __name__ == "__main__":
    # Test Amaçlı Örnek İlan Paylaşımı
    TEST_IMAGE = "https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=1080"
    TEST_CAPTION = """📢 KAMU PERSONELİ ALIM İLANI (TEST)

Bu gönderi Python ve Instagram Graph API ile tamamen otomatik olarak paylaşılmıştır.

#kamuilanı #kpss #memuralımı #kamuilansbb"""

    post_to_instagram(TEST_IMAGE, TEST_CAPTION)