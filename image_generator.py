from PIL import Image, ImageDraw, ImageFont
import os

def create_modern_post_image(main_title, output_path="ilan_gorsel_modern.jpg"):
    # 1. Instagram Kare Gönderi Boyutu (1080x1080)
    width, height = 1080, 1080
    
    # 2. Renk Paleti (Kurumsal & Sade)
    color_bg = (255, 255, 255)            # Saf Beyaz Arka Plan
    color_header_bg = (180, 20, 25)       # Kurumsal Kırmızı (Üst Bant)
    color_text_header = (255, 255, 255)    # Beyaz (Üst Başlık)
    color_text_main = (30, 30, 30)        # Koyu Gri (Ana İlan Metni)
    color_text_footer = (120, 120, 120)    # Açık Gri (Alt Bilgi)

    # 3. Görseli ve Çizim Tuvalini Oluştur
    image = Image.new("RGB", (width, height), color=color_bg)
    draw = ImageDraw.Draw(image)

    # 4. Üst Kurumsal Kırmızı Bant
    header_height = 140
    draw.rectangle([0, 0, width, header_height], fill=color_header_bg)

    # 5. Fontları Yükle
    try:
        # Öncelikli olarak aynı klasördeki Poppins fontuna bakar, yoksa Arial kullanır
        if os.path.exists("Poppins-Bold.ttf"):
            font_header = ImageFont.truetype("Poppins-Bold.ttf", 60)
            font_main = ImageFont.truetype("Poppins-Medium.ttf", 65)
            font_footer = ImageFont.truetype("Poppins-Regular.ttf", 35)
        else:
            font_header = ImageFont.truetype("arial.ttf", 55)
            font_main = ImageFont.truetype("arial.ttf", 60)
            font_footer = ImageFont.truetype("arial.ttf", 35)
    except IOError:
        font_header = ImageFont.load_default()
        font_main = ImageFont.load_default()
        font_footer = ImageFont.load_default()

    # 6. Üst Başlığı Yaz: "KamuİlanSBB" (Ortalı)
    header_text = "KamuİlanSBB"
    header_bbox = draw.textbbox((0, 0), header_text, font=font_header)
    header_width = header_bbox[2] - header_bbox[0]
    header_x = (width - header_width) / 2
    header_y = (header_height - (header_bbox[3] - header_bbox[1])) / 2 - 10
    draw.text((header_x, header_y), header_text, fill=color_text_header, font=font_header)

    # 7. Ana İlan Başlığını Yaz (Word wrap / Alta Kaydırma)
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
            y_text += 85
            line = word + " "
    if line:
        draw.text((margin, y_text), line, fill=color_text_main, font=font_main)
        
    # 8. Alt Bilgi: Instagram Kullanıcı Adı
    footer_text = "instagram.com/kamuilansbb"
    footer_bbox = draw.textbbox((0, 0), footer_text, font=font_footer)
    footer_width = footer_bbox[2] - footer_bbox[0]
    footer_x = width - footer_width - 60
    footer_y = height - 70
    draw.text((footer_x, footer_y), footer_text, fill=color_text_footer, font=font_footer)
    
    # 9. Görseli Kaydet
    image.save(output_path, quality=95)
    print(f"[+] Modern ilan görseli başarıyla oluşturuldu: {output_path}")

if __name__ == "__main__":
    ornek_ilan = "SAĞLIK BAKANLIĞI 15.000 SÖZLEŞMELİ PERSONEL ALIMI YAPACAK!"
    create_modern_post_image(ornek_ilan)