import os
import time
import json
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

# ==================== AYARLAR ====================
ACCESS_TOKEN = r"EAAdx2vMKhs...[TOKEN_BURAYA]"  # Aktif Access Token'ın
INSTAGRAM_ACCOUNT_ID = "17841459578691000"       # Instagram Business ID
HISTORY_FILE = "paylasilanlar.json"

# ==================== 1. GÖRSEL ÜRETİCİ ====================
def create_post_image(main_title, output_path="ilan_gorsel.jpg"):
    width, height = 1080, 1080
    color_bg = (255, 255, 255)
    color_header_bg = (180, 20, 25)
    color_text_header = (255, 255, 255)
    color_text_main = (30, 30, 30)
    color_text_footer = (120, 120, 120)

    image = Image.new("RGB", (width, height), color=color_bg)
    draw = ImageDraw.Draw(image)

    # Üst Kurumsal Kırmızı Bant
    header_height = 140
    draw.rectangle([0, 0, width, header_height], fill=color_header_bg)

    try:
        font_header = ImageFont.truetype("arial.ttf", 55)
        font_main = ImageFont.truetype("arial.ttf", 60)
        font_footer = ImageFont.truetype("arial.ttf", 35)
    except IOError:
        font_header = ImageFont.load_default()
        font_main = ImageFont.load_default()
        font_footer = ImageFont.load_default()

    # Üst Başlık: "KamuİlanSBB"
    header_text = "KamuİlanSBB"
    header_bbox = draw.textbbox((0, 0), header_text, font=font_header)
    header_width = header_bbox[2] - header_bbox[0]
    header_x = (width - header_width) / 2
    header_y = (header_height - (header_bbox[3] - header_bbox[1])) / 2 - 10
    draw.text((header_x, header_y), header_text, fill=color_text_header, font=font_header)

    # Ana Başlık Yerleşimi (Word Wrap)
    margin = 90
    y_text = header_height + 120
    words = main_title.split()
    line = ""
    for word in words:
        test_line = line + word + " "
        bbox = draw.textbbox((0, 0), test_line, font=font_main)
        text_width = bbox[2] - bbox[0]
        if text_width <= width - (2 * margin):
            line = test_line
        else:
            draw.text((margin, y_text), line, fill=color_text_main, font=font_main)
            y_text += 80
            line = word + " "
    if line:
        draw.text((margin, y_text), line, fill=color_text_main, font=font_main)
        
    # Alt Bilgi
    footer_text = "instagram.com/kamuilansbb"
    footer_bbox = draw.textbbox((0, 0), footer_text, font=font_footer)
    footer_width = footer_bbox[2] - footer_bbox[0]
    footer_x = width - footer_width - 60
    footer_y = height - 70
    draw.text((footer_x, footer_y), footer_text, fill=color_text_footer, font=font_footer)
    
    image.save(output_path, quality=95)
    print(f"[+] İlan görseli oluşturuldu: {output_path}")

# ==================== 2. GEÇMİŞ KONTROLÜ ====================
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

# ==================== 3. INSTAGRAM PAYLAŞIM ====================
def publish_to_instagram(image_path, caption_text):
    # Not: GitHub Actions aşamasında local resim public URL'ye dönecek.
    # Şimdilik test için harici erişilebilir bir örnek görsel URL veya yerel yükleme yöntemi kullanılır.
    # Graph API doğrudan yerel dosya yolu kabul etmediği için bulut aşamasında raw.githubusercontent linki verilecektir.
    print("[*] Instagram API üzerinden paylaşım simüle ediliyor...")
    # (Önceki bot.py içindeki requests.post mantığı buraya entegre edilecek)
    return True

# ==================== 4. ANA ÇALIŞTIRMA ====================
def check_and_post():
    url = "https://kamuilan.sbb.gov.tr/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    print("[*] SBB ilanları taranıyor...")
    res = requests.get(url, headers=headers, timeout=15)
    if res.status_code != 200:
        print("[-] Siteye erişilemedi.")
        return

    soup = BeautifulSoup(res.text, 'html.parser')
    history = load_history()
    
    # Sitedeki ilan linklerini bulma
    links = soup.find_all('a')
    for link in links:
        title = link.get_text(strip=True)
        href = link.get('href')
        
        # İlan detay linki içeren ve anlamlı başlıklara sahip olanları seç
        if href and "ilanDetay.aspx" in href and len(title) > 20:
            if href not in history:
                print(f"\n[YENİ İLAN YAKALANDI]: {title}")
                
                # 1. Görseli Üret
                create_post_image(title)
                
                # 2. Geçmişe ekle ve kaydet (Tekrar atmasın)
                history.append(href)
                save_history(history)
                
                print("[+] İlan işlendi ve kayıt altına alındı!")
                break # Test için ilk yeni ilanda duralım
            else:
                print("[i] Bu ilan daha önce paylaşılmış, geçiliyor.")
                break

if __name__ == "__main__":
    check_and_post()