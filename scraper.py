
import json
import os
import traceback
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

URL = "https://kamuilan.sbb.gov.tr/"
DOSYA_PAYLASILANLAR = "paylasilanlar.json"

FALLBACK_IMAGE = (
    "https://images.unsplash.com/"
    "photo-1586281380349-632531db7ed4?w=1080"
)


def paylasilanlari_yukle():
    if not os.path.exists(DOSYA_PAYLASILANLAR):
        return []

    try:
        with open(DOSYA_PAYLASILANLAR, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data if isinstance(data, list) else []

    except (OSError, json.JSONDecodeError) as exc:
        print(f"[UYARI] İlan geçmişi okunamadı: {exc}")
        return []


def paylasilanlari_kaydet(paylasilanlar_listesi):
    with open(DOSYA_PAYLASILANLAR, "w", encoding="utf-8") as f:
        json.dump(
            paylasilanlar_listesi,
            f,
            ensure_ascii=False,
            indent=4
        )


def yeni_ilani_bul():
    print("[*] Playwright ile Chromium başlatılıyor...")

    with sync_playwright() as p:
        browser = None

        try:
            browser = p.chromium.launch(headless=True)

            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                locale="tr-TR",
                accept_downloads=False,
            )

            page = context.new_page()
            page.set_default_timeout(15000)

            # Ağ yanıtlarını kaydet; özellikle ana sayfanın durumunu izle.
            page.on(
                "response",
                lambda response: print(
                    f"[HTTP] {response.status} {response.url}"
                )
                if response.url.rstrip("/") == URL.rstrip("/")
                else None
            )

            print(f"[i] SBB sayfasına bağlanılıyor: {URL}")

            try:
                response = page.goto(
                    URL,
                    timeout=60000,
                    wait_until="domcontentloaded"
                )
            except PlaywrightTimeoutError:
                print("[UYARI] Sayfa yükleme zaman aşımı; içerik kontrol ediliyor.")
                response = None

            if response:
                print(f"[DEBUG] Ana sayfa HTTP: {response.status}")
                print(f"[DEBUG] Son URL: {page.url}")
            else:
                print(f"[DEBUG] Son URL: {page.url}")

            try:
                page.locator("body").wait_for(state="visible", timeout=15000)
            except PlaywrightTimeoutError:
                print("[HATA] Sayfa gövdesi yüklenemedi.")
                return None

            page.wait_for_timeout(3000)

            baslik = page.title()
            metin = page.locator("body").inner_text()[:6000]

            print(f"[DEBUG] Sayfa başlığı: {baslik}")
            print("[DEBUG] Sayfa metninin ilk 6000 karakteri:")
            print(metin)

            # Koruma veya erişim hatalarını teşhis et.
            metin_kucuk = metin.lower()
            engel_ifadeleri = [
                "verify you are human",
                "checking your browser",
                "attention required",
                "access denied",
                "just a moment",
                "erişim engellendi",
            ]

            if any(ifade in metin_kucuk for ifade in engel_ifadeleri):
                print(
                    "[UYARI] Sayfada erişim doğrulaması veya "
                    "engelleme mesajı olabilir."
                )

            # Önce sayfadaki bütün bağlantıları topla.
            baglantilar = page.locator("a").evaluate_all("""
                elements => elements.map(a => ({
                    baslik: (a.innerText || a.textContent || '').trim(),
                    href: a.href
                }))
            """)

            print(f"[DEBUG] Toplam bağlantı: {len(baglantilar)}")
            print("[DEBUG] İlk 40 bağlantı:")

            for item in baglantilar[:40]:
                print(
                    f"  - Başlık: {item['baslik'][:120]!r} "
                    f"| URL: {item['href']}"
                )

            # Site içindeki anlamlı bağlantıları aday olarak seç.
            ana_host = urlparse(URL).netloc.lower()
            adaylar = []
            gorulenler = set()

            genel_metinler = {
                "ana sayfa",
                "anasayfa",
                "giriş",
                "giris",
                "çıkış",
                "cikis",
                "iletişim",
                "iletisim",
                "detay",
                "incele",
                "devamını oku",
                "devamini oku",
                "ara",
                "filtrele",
                "temizle",
                "önceki",
                "sonraki",
            }

            for item in baglantilar:
                baslik = " ".join(item["baslik"].split())
                link = item["href"]

                if not baslik or len(baslik) < 15:
                    continue

                if baslik.casefold() in genel_metinler:
                    continue

                parsed = urlparse(link)

                if parsed.scheme not in ("http", "https"):
                    continue

                # Başka sitelere ait bağlantıları ilan sayma.
                if parsed.netloc.lower() != ana_host:
                    continue

                if link.rstrip("/") == URL.rstrip("/"):
                    continue

                if link in gorulenler:
                    continue

                gorulenler.add(link)

                adaylar.append({
                    "baslik": baslik,
                    "link": link,
                })

            print(f"[DEBUG] Site içi anlamlı bağlantı adayı: {len(adaylar)}")

            for item in adaylar[:30]:
                print(f"[ADAY] {item['baslik'][:100]} | {item['link']}")

            # Tarayıcıyı, gerekli veriler alındıktan sonra kapat.
            browser.close()
            browser = None

            paylasilanlar = paylasilanlari_yukle()

            for ilan in adaylar:
                ilan_id = ilan["link"]

                if ilan_id in paylasilanlar:
                    continue

                print(f"[+] Yeni bağlantı adayı: {ilan['baslik'][:100]}")

                return {
                    "id": ilan_id,
                    "baslik": ilan["baslik"],
                    "link": ilan["link"],
                    "gorsel": FALLBACK_IMAGE,
                    "kurum": "SBB Kamu İlanları",
                    "tarih": "Kontrol edilmeli",
                }

            print("[-] Paylaşılacak yeni ilan bulunamadı.")
            print(
                "[i] Aday sayısı sıfırsa sayfa HTML yapısı veya "
                "ilanların yüklenme yöntemi incelenmeli."
            )
            print(
                "[i] Adaylar mevcut ama hepsi geçmişteyse "
                "paylasilanlar.json kontrol edilmeli."
            )

            return None

        except Exception as exc:
            print(f"[HATA] SBB taraması başarısız: {exc}")
            traceback.print_exc()
            return None

        finally:
            if browser:
                try:
                    browser.close()
                except Exception:
                    pass


if __name__ == "__main__":
    ilan = yeni_ilani_bul()
    print("[SONUÇ]", json.dumps(ilan, ensure_ascii=False, indent=2))
