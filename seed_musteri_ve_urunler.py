import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "teleset_crm_core.settings")
django.setup()

from crm_takip.models import MusteriKarti, UrunGrubuKarti

# 1. MÜŞTERİ KARTLARI (10 Stratejik OEM Cari)
musteriler = [
    {
        "kod": "FRM-01",
        "ad": "BSH Ev Aletleri San. ve Tic. A.Ş.",
        "kisa_ad": "BSH",
        "ulke": "Almanya / Türkiye",
        "sehir": "Münih / Çerkezköy",
        "tier": "Tier 1 - KAM",
        "strateji": "Protect",
        "yillik_ciro_eur": 12180000,
        "cuzdan_payi_yuzde": 58,
        "aktif_proje_sayisi": 28,
        "kam_satis_lideri": "Pazarlama Uzmanı",
        "kam_muhendislik_lideri": "Ahmet AK (Kalıp & Projeci Md.)",
        "kam_kalite_lideri": "Mehmet YILMAZ (Kalite Mühendisi)",
        "aktif_urunler": "Fırın Yan Gövde Sacı (400T), Kombi Kablo Demetleri, Buzdolabı Kondanserleri",
        "sozlesme_durumu": "Aktif Sözleşme (2028'e Kadar Geçerli)",
        "churn_riski": "Düşük (Yeşil)",
        "notlar": "Teleset'in toplam cirosunun %32'sini oluşturan en stratejik global OEM ortağı."
    },
    {
        "kod": "FRM-02",
        "ad": "Beko / Arçelik A.Ş. (Türkiye & Romanya)",
        "kisa_ad": "BEKO",
        "ulke": "Romanya / Türkiye",
        "sehir": "Gaesti / Çerkezköy",
        "tier": "Tier 1 - KAM",
        "strateji": "Protect",
        "yillik_ciro_eur": 11920000,
        "cuzdan_payi_yuzde": 52,
        "aktif_proje_sayisi": 25,
        "kam_satis_lideri": "Pazarlama Uzmanı",
        "kam_muhendislik_lideri": "Cemil ÇELİK (Pres Hatları Md.)",
        "kam_kalite_lideri": "Hakan KILIÇ (Proses Kalite)",
        "aktif_urunler": "Arctic Çamaşır Kablo Gruplama, Kombi Metal Şasi, Tel-Boru Kondanser",
        "sozlesme_durumu": "Aktif Sözleşme (2027 Romanya & TR)",
        "churn_riski": "Düşük (Yeşil)",
        "notlar": "Türkiye ve Romanya fabrikalarına eşzamanlı parça tedariği sağlanan ana ihracat carisi."
    },
    {
        "kod": "FRM-03",
        "ad": "Vestel Beyaz Eşya San. ve Tic. A.Ş.",
        "kisa_ad": "VESTEL",
        "ulke": "Türkiye",
        "sehir": "Manisa OSB",
        "tier": "Tier 1 - KAM",
        "strateji": "Protect",
        "yillik_ciro_eur": 8450000,
        "cuzdan_payi_yuzde": 45,
        "aktif_proje_sayisi": 19,
        "kam_satis_lideri": "Pazarlama Uzmanı",
        "kam_muhendislik_lideri": "Ahmet AK (Kalıp & Projeci Md.)",
        "kam_kalite_lideri": "Serdar DEMİR (Giriş Kalite Md.)",
        "aktif_urunler": "Buzdolabı Dinamik Kondanser, Çamaşır Tambur ve Arka Sacı, Kablo Demetleri",
        "sozlesme_durumu": "Yıllık Çerçeve Anlaşması Aktif (2026-2027)",
        "churn_riski": "Düşük (Yeşil)",
        "notlar": "Manisa OSB lokasyon avantajıyla JIT (Tam Zamanında) teslimat yapılan stratejik cari."
    },
    {
        "kod": "FRM-04",
        "ad": "Electrolux Group (İtalya, Polonya, İsveç)",
        "kisa_ad": "ELECTROLUX",
        "ulke": "İtalya / Polonya",
        "sehir": "Pordenone / Oława",
        "tier": "Tier 1 - KAM",
        "strateji": "Grow",
        "yillik_ciro_eur": 7800000,
        "cuzdan_payi_yuzde": 38,
        "aktif_proje_sayisi": 16,
        "kam_satis_lideri": "Pazarlama Uzmanı",
        "kam_muhendislik_lideri": "Cemil ÇELİK (Pres Hatları Md.)",
        "kam_kalite_lideri": "Mehmet YILMAZ (Kalite Mühendisi)",
        "aktif_urunler": "Ankastre Fırın Sac Parçaları, Bulaşık Makinesi Kablo Grupları, Kondanser",
        "sozlesme_durumu": "Global Tedarik Sözleşmesi Aktif",
        "churn_riski": "Orta (Sarı)",
        "notlar": "İtalya ve Polonya tesislerine ihracat hacmi hızla büyüyen stratejik hesap."
    },
    {
        "kod": "FRM-05",
        "ad": "Whirlpool EMEA / Beko Europe",
        "kisa_ad": "WHIRLPOOL",
        "ulke": "İtalya / Polonya",
        "sehir": "Cassinetta / Wrocław",
        "tier": "Tier 1 - KAM",
        "strateji": "Protect",
        "yillik_ciro_eur": 6900000,
        "cuzdan_payi_yuzde": 35,
        "aktif_proje_sayisi": 14,
        "kam_satis_lideri": "Pazarlama Uzmanı",
        "kam_muhendislik_lideri": "Ahmet AK (Kalıp & Projeci Md.)",
        "kam_kalite_lideri": "Hakan KILIÇ (Proses Kalite)",
        "aktif_urunler": "Kurutucu Isı Pompası Kondanserleri, Çamaşır Şasi Sac Parçaları, Kablo Demeti",
        "sozlesme_durumu": "Tedarikçi Onay Sertifikası Aktif",
        "churn_riski": "Düşük (Yeşil)",
        "notlar": "Beko Europe birleşmesi sonrasında sipariş hacimleri konsolide edilen küresel OEM."
    },
    {
        "kod": "FRM-06",
        "ad": "Miele & Cie. KG",
        "kisa_ad": "MIELE",
        "ulke": "Almanya",
        "sehir": "Gütersloh",
        "tier": "Tier 2 - Growth",
        "strateji": "Grow",
        "yillik_ciro_eur": 3400000,
        "cuzdan_payi_yuzde": 22,
        "aktif_proje_sayisi": 8,
        "kam_satis_lideri": "Pazarlama Uzmanı",
        "kam_muhendislik_lideri": "Ahmet AK (Kalıp & Projeci Md.)",
        "kam_kalite_lideri": "Serdar DEMİR (Giriş Kalite Md.)",
        "aktif_urunler": "Premium Ankastre Sac Komponentleri, Yüksek Isı Kablo Demetleri",
        "sozlesme_durumu": "RFQ ve Kalite Onayı Aktif",
        "churn_riski": "Düşük (Yeşil)",
        "notlar": "Premium segmentte yüksek toleranslı ve katma değerli parça üretimi yapılan hedef cari."
    },
    {
        "kod": "FRM-07",
        "ad": "Liebherr Hausgeräte GmbH",
        "kisa_ad": "LIEBHERR",
        "ulke": "Almanya",
        "sehir": "Ochsenhausen",
        "tier": "Tier 2 - Growth",
        "strateji": "Grow",
        "yillik_ciro_eur": 2850000,
        "cuzdan_payi_yuzde": 18,
        "aktif_proje_sayisi": 6,
        "kam_satis_lideri": "Pazarlama Uzmanı",
        "kam_muhendislik_lideri": "Cemil ÇELİK (Pres Hatları Md.)",
        "kam_kalite_lideri": "Mehmet YILMAZ (Kalite Mühendisi)",
        "aktif_urunler": "Özel Soğutma Kondanserleri, Paslanmaz Sac Şekillendirme",
        "sozlesme_durumu": "Yıllık Sipariş Sözleşmesi",
        "churn_riski": "Düşük (Yeşil)",
        "notlar": "Soğutma grubunda premium teknolojik kondanser talebi olan stratejik Alman OEM."
    },
    {
        "kod": "FRM-08",
        "ad": "Haier Europe (Candy-Hoover Group)",
        "kisa_ad": "HAIER / CANDY",
        "ulke": "İtalya",
        "sehir": "Brugherio",
        "tier": "Tier 2 - Growth",
        "strateji": "Grow",
        "yillik_ciro_eur": 2500000,
        "cuzdan_payi_yuzde": 15,
        "aktif_proje_sayisi": 5,
        "kam_satis_lideri": "Pazarlama Uzmanı",
        "kam_muhendislik_lideri": "Ahmet AK (Kalıp & Projeci Md.)",
        "kam_kalite_lideri": "Hakan KILIÇ (Proses Kalite)",
        "aktif_urunler": "Çamaşır ve Bulaşık Kablo Ağaçları, Pres Parçaları",
        "sozlesme_durumu": "Tedarikçi Çerçeve Sözleşmesi",
        "churn_riski": "Orta (Sarı)",
        "notlar": "Eskişehir ve İtalya hatları için yeni ürün geliştirme projeleri devam ediyor."
    },
    {
        "kod": "FRM-09",
        "ad": "Amica S.A.",
        "kisa_ad": "AMICA",
        "ulke": "Polonya",
        "sehir": "Wronki",
        "tier": "Tier 2 - Growth",
        "strateji": "Grow",
        "yillik_ciro_eur": 1950000,
        "cuzdan_payi_yuzde": 20,
        "aktif_proje_sayisi": 4,
        "kam_satis_lideri": "Pazarlama Uzmanı",
        "kam_muhendislik_lideri": "Cemil ÇELİK (Pres Hatları Md.)",
        "kam_kalite_lideri": "Mehmet YILMAZ (Kalite Mühendisi)",
        "aktif_urunler": "Fırın ve Ocak Yan Sac Panelleri, Isıtıcı Kablo Grupları",
        "sozlesme_durumu": "Aktif Tedarikçi Kaydı",
        "churn_riski": "Düşük (Yeşil)",
        "notlar": "Polonya pazarında yerel tedarik payını artırmayı hedefleyen büyüme odaklı müşteri."
    },
    {
        "kod": "FRM-10",
        "ad": "Teka Industrial S.A.",
        "kisa_ad": "TEKA",
        "ulke": "İspanya / Portekiz",
        "sehir": "Santander / Santo Tirso",
        "tier": "Tier 3 - Standart",
        "strateji": "Grow",
        "yillik_ciro_eur": 1200000,
        "cuzdan_payi_yuzde": 12,
        "aktif_proje_sayisi": 3,
        "kam_satis_lideri": "Pazarlama Uzmanı",
        "kam_muhendislik_lideri": "Ahmet AK (Kalıp & Projeci Md.)",
        "kam_kalite_lideri": "Serdar DEMİR (Giriş Kalite Md.)",
        "aktif_urunler": "Eviye ve Ankastre Sac Komponentleri, Kablo Grupları",
        "sozlesme_durumu": "Onaylı Tedarikçi",
        "churn_riski": "Düşük (Yeşil)",
        "notlar": "İber Yarımadası (İspanya-Portekiz) sinerjisi kapsamında cüzdan payı artırılacak müşteri."
    }
]

for m in musteriler:
    obj, created = MusteriKarti.objects.update_or_create(kod=m["kod"], defaults=m)
    print(f"Musteri: {obj.kisa_ad} -> {'Olusturuldu' if created else 'Guncellendi'}")

# 2. ÜRÜN GRUBU KARTLARI (4 Temel Üretim Kabiliyeti)
urun_gruplari = [
    {
        "kod": "UG-01",
        "baslik": "Metal Parça & Sac Şekillendirme",
        "ikon": "bi-layers-half",
        "ana_fabrika": "Teleset 1 (Manisa) & Teleset Otomotiv",
        "kabiliyetler": "• 60T - 800T Eksantrik ve Hidrolik Pres Hatları\n• Progresif ve Transfer Kalıplama Teknolojisi\n• 3D Lazer Kesim ve CNC Punch Tezgahları\n• Robotik Punta, Gazaltı ve Lazer Kaynak İstasyonları\n• Yüzey İşlem, Çapak Alma ve Yağdan Arındırma",
        "referans_parcalar": "• Fırın Yan Gövde ve Üst Tabla Sacları\n• Çamaşır Makinesi Arka Kapak ve Denge Ağırlık Braketleri\n• Kombi Şasi ve Brülör Muhafazaları\n• EV Batarya Taşıyıcı ve Koruyucu Sac Parçaları",
        "yillik_kapasite": "45.000 Ton Sac İşleme / Yıl",
        "hedef_sektorler": "Beyaz Eşya, Otomotiv, Isıtma/Soğutma, Endüstriyel Ekipman",
        "kalite_standartlari": "ISO 9001, IATF 16949, ISO 14001, ISO 45001"
    },
    {
        "kod": "UG-02",
        "baslik": "Kablo Grubu & Demetleri (Wire Harnessing)",
        "ikon": "bi-bezier2",
        "ana_fabrika": "Teleset 2 (Manisa) & Teleset Global",
        "kabiliyetler": "• Tam Otomatik Kablo Kesme, Açma ve Krimp Basma (Komax)\n• Ultrasonik Kablo Kaynak ve Ekleme İstasyonları\n• %100 Elektriksel Test ve Kısa Devre Kontrol Masaları (Cirris)\n• Termoplastik ve Silikon Enjeksiyon Soketleme\n• Barkodlu ve RFID İzlenebilirlik Sistemi",
        "referans_parcalar": "• Fırın, Ocak ve Davlumbaz Ana Güç ve Sinyal Kablo Ağaçları\n• Buzdolabı ve Dondurucu Gövde/Kapı Kablo Grupları\n• Çamaşır ve Bulaşık Makinesi Motor ve Pompa Tesisatları\n• Kombi ve Isıtma Sistemleri Kontrol Demetleri",
        "yillik_kapasite": "18.000.000 Adet Kablo Grubu / Yıl",
        "hedef_sektorler": "Beyaz Eşya, Tüketici Elektroniği, HVAC, Otomotiv Yan Sanayi",
        "kalite_standartlari": "ISO 9001, IATF 16949, UL / VDE Onaylı Üretim"
    },
    {
        "kod": "UG-03",
        "baslik": "Kondenser & Soğutma Komponentleri",
        "ikon": "bi-snow",
        "ana_fabrika": "Teleset 3 (Kocaeli) & Teleset 1 (Manisa)",
        "kabiliyetler": "• Otomatik Tel-Boru Kondenser Kaynak Hatları\n• CNC Boru Bükme ve Uç Şekillendirme Makineleri\n• Elektrostatik Toz Boya (Katoferez & Epoksi) Fırınlama Hattı\n• Yüksek Basınçlı Helyum Kaçak Testi (Helium Leak Detection)\n• İç Temizlik ve Nem Giderme Vakum İstasyonları",
        "referans_parcalar": "• Ev Tipi Buzdolabı Statik ve Dinamik Tel-Boru Kondenserleri\n• Ticari Soğutucu ve Şişe Soğutucu Isı Değiştiricileri\n• Isı Pompası ve Kurutucu Serpantinleri\n• Şarap Soğutucu ve Dondurucu Arka Kondenserleri",
        "yillik_kapasite": "4.200.000 Adet Kondenser / Yıl",
        "hedef_sektorler": "Ev Tipi ve Ticari Soğutma, HVAC, Isı Pompaları",
        "kalite_standartlari": "ISO 9001, ISO 14001, RoHS, REACH Uyumlu"
    },
    {
        "kod": "UG-04",
        "baslik": "Kalıp, Fikstür & Projeci Mühendislik (Tooling)",
        "ikon": "bi-tools",
        "ana_fabrika": "Teleset Kalıphane (Manisa OSB)",
        "kabiliyetler": "• 3D CAD/CAM Simülasyon ve Modelleme (Siemens NX, AutoForm)\n• Yüksek Hızlı 5 Eksen CNC İşleme Merkezleri\n• Tel Erozyon (Wire EDM) ve Dalma Erozyon Tezgahları\n• 500T Hidrolik Deneme ve Alıştırma Presi\n• CMM 3D Optik ve Dokunmatik Koordinat Ölçüm Cihazı (Zeiss)",
        "referans_parcalar": "• Progresif Sac Şekillendirme ve Kesme Kalıpları\n• Transfer Pres Kalıpları ve Robotik Taşıyıcı Gripperlar\n• Kablo Demeti Montaj ve Elektriksel Test Fikstürleri\n• Kaynak, Punta ve Kontrol Mastarları",
        "yillik_kapasite": "85 Adet Komple Kalıp & 350+ Fikstür / Yıl",
        "hedef_sektorler": "Beyaz Eşya Kalıpçılığı, Otomotiv Sac Parça Kalıpları",
        "kalite_standartlari": "ISO 9001, VDA 6.4 Kalıp Standartları"
    }
]

for u in urun_gruplari:
    obj, created = UrunGrubuKarti.objects.update_or_create(kod=u["kod"], defaults=u)
    print(f"Urun Grubu: {obj.baslik} -> {'Olusturuldu' if created else 'Guncellendi'}")

print("\nTum Musteri ve Urun Grubu Kartlari basariyla yuklendi!")
