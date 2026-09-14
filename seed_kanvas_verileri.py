import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "teleset_crm_core.settings")
django.setup()

from crm_takip.models import HedefPazarKanvas

kanvas_listesi = [
    {
        "ulke_kodu": "DE",
        "ulke_adi": "Almanya",
        "bayrak_emoji": "",
        "oncelik_sinifi": "Birincil Pazar (Stratejik)",
        "genel_gorunum": "• Avrupa'nın en büyük sanayi ekonomisi (GSYH = 4,6 trilyon USD).\n• Beyaz eşyada Ar-Ge ve enerji verimliliği öncüsü.\n• Enerji dönüşümü yatırımları hız kazandı.\n• Türkiye'den karayoluyla 3–4 günde teslimat.",
        "sektor_pazari": "• Avrupa'nın en büyük pazarı (= 13 milyar EUR, 2024).\n• Premium & ankastre payı yüksek, enerji verimliliği odaklı.\n• E-ticaret güçlü (MediaMarkt, Saturn, Otto, Amazon).\n• OEM montaj + ileri komponent ekosistemi entegre.",
        "one_cikan_sirketler": "• BSH Hausgeräte – Münih, Dillingen, Traunreut\n• Miele & Cie. KG – Gütersloh (premium segment lideri)\n• Liebherr Hausgeräte – Ochsenhausen (soğutma)\n• Constructa–Neff (BSH) – Münih (ankastre)\n• AEG (Electrolux) – Nürnberg, Rothenburg",
        "egilimler_ve_zorluklar": "• IoT/smart home entegrasyonu hız kazanıyor.\n• 2030 karbon nötr üretim hedefi.\n• İşçilik maliyetleri yüksek; üretim Doğu Avrupa'ya kayıyor.\n• CE, RoHS, WEEE süreçlerinin maliyeti artıyor.",
        "vergilendirme_ve_gumruk": "• Türkiye–AB Gümrük Birliği: %0 gümrük vergisi.\n• KDV: %19 (mahsuba tabi).\n• Gümrükleme: Karayolu sevkiyatta 2–3 gün.\n• Zorunlu: CE, REACH, RoHS; enerji etiketleme.",
        "teleset_degerlendirmesi": "• B/S/H/, Electrolux, BEKO ilişkilerini derinleştirme fırsatı.\n• Türkiye menşeli komponentlere yüksek ilgi (kısa teslim).\n• Teleset: MES–ERP, ISO 9001/14001/45001 uyumlu.\n• Hedef Ürünler: Kondenser, Kablo grubu, Metal parça, Kalıp.",
        "hedef_urunler": "Kondenser, Kablo Grubu, Metal Parça, Kalıp"
    },
    {
        "ulke_kodu": "PL",
        "ulke_adi": "Polonya",
        "bayrak_emoji": "",
        "oncelik_sinifi": "Birincil Pazar (Üretim Üssü)",
        "genel_gorunum": "• Orta Avrupa'nın üretim ve lojistik merkezi; AB üyesi, GSYH = 850 milyar USD.\n• Türkiye'den 2–3 günde karayolu teslimat.\n• Düşük enerji & işçilik maliyeti, gelişmiş altyapı.\n• Yatırım ortamı güçlü, ihracat yönelimli sanayi yapısı.",
        "sektor_pazari": "• Avrupa'nın en büyük üretim üslerinden biri.\n• OEM odaklı üretim: Whirlpool, Beko/Arctic, Electrolux, Samsung, Amica.\n• Üretimin %80'i ihracata gidiyor (AB içi dağıtım).\n• Enerji verimliliği & ankastre ürün segmenti yükselişte.",
        "one_cikan_sirketler": "• Whirlpool Poland – Wrocław, Radomsko\n• Electrolux Poland – Oława, Żarów\n• Amica S.A. – Wronki\n• Beko/Arctic Poland – Łódź bölgesi\n• Samsung Poland – Żyrardów",
        "egilimler_ve_zorluklar": "• AB enerji & karbon standartları -> dönüşüm baskısı.\n• İşgücü maliyetleri artıyor, nitelikli personel kıtlığı.\n• Yerli komponent tedarikine geçiş destekleniyor.\n• 'Green Industry 2030' karbon azaltım programı yürürlükte.",
        "vergilendirme_ve_gumruk": "• AB Gümrük Birliği: %0 gümrük.\n• KDV: %23 (mahsuba tabi).\n• Gümrükleme süresi: 2–3 gün.\n• Zorunlu: CE, RoHS, WEEE.",
        "teleset_degerlendirmesi": "• BSH, Beko, Electrolux, Whirlpool ile mevcut ilişkiler güçlendirilebilir.\n• Kondanser & Kablo Grubu için lojistik avantaj çok yüksek.\n• Türkiye menşeli komponentlere talep artıyor.\n• MES–ERP, ISO 9001/14001/45001 uyumuyla rekabet avantajı.",
        "hedef_urunler": "Kondanser, Kablo Grubu, Metal Parça"
    },
    {
        "ulke_kodu": "IT",
        "ulke_adi": "İtalya",
        "bayrak_emoji": "",
        "oncelik_sinifi": "Birincil Pazar (Tasarım & Montaj)",
        "genel_gorunum": "• Avrupa'nın 3. büyük sanayi ekonomisi (GSYH = 2,3 trilyon USD).\n• Güçlü mühendislik altyapısı, yüksek kalite beklentisi.\n• Türkiye'den 2–3 günde karayolu teslimat.\n• Kuzey bölgeleri (Lombardia, Veneto, Emilia-Romagna) sanayi merkezidir.",
        "sektor_pazari": "• Avrupa'nın tasarım ve montaj üssü – estetik & ankastre ürünlerde lider.\n• Üretim hacmi güçlü: Whirlpool, Electrolux, Candy-Hoover, Indesit, Arçelik/Defy.\n• Yerli tedarik zinciri gelişmiş, dış komponent tedariği enerji verimliliği odaklı.\n• İç pazar doygun ama ihracat odaklı üretim sürüyor.",
        "one_cikan_sirketler": "• Whirlpool EMEA HQ & Cassinetta Tesisi – Lombardiya\n• Electrolux Italy – Pordenone, Forlì, Susegana\n• Candy-Hoover Group (Haier Europe) – Brugherio\n• Indesit / Ariston (Whirlpool) – Fabriano\n• Arçelik/Defy İtalya Ofisi – Milano",
        "egilimler_ve_zorluklar": "• Yüksek enerji maliyetleri, üretim Doğu Avrupa'ya kayıyor.\n• Sürdürülebilir ürün ve karbon nötr üretim gündemde.\n• Kalifiye işgücü ve AR-GE odaklı üretim ön planda.\n• E-ticaret ve özel ankastre segmenti büyüyor.",
        "vergilendirme_ve_gumruk": "• AB Gümrük Birliği: %0 gümrük.\n• KDV: %22 (mahsuba tabi).\n• Gümrükleme süresi: 2–3 gün.\n• Zorunlu: CE, RoHS, REACH.",
        "teleset_degerlendirmesi": "• Electrolux, Whirlpool, Haier Europe ile mevcut iş birlikleri genişletilebilir.\n• Kondanser, Metal Parça, Kalıp ürünlerinde güçlü potansiyel.\n• İtalya, Avrupa'ya açılan stratejik referans pazardır.\n• Kalite ve izlenebilirlik sertifikaları rekabet avantajı sağlar.",
        "hedef_urunler": "Kondanser, Metal Parça, Kalıp"
    },
    {
        "ulke_kodu": "ES",
        "ulke_adi": "İspanya",
        "bayrak_emoji": "",
        "oncelik_sinifi": "İkincil / Stratejik Pazar",
        "genel_gorunum": "• Güney Avrupa'nın sanayi ve lojistik merkezlerinden biri.\n• GSYH = 1,7 trilyon USD, AB'nin 4. büyük ekonomisi.\n• Türkiye'den 3–4 günde karayolu teslimat, denizyolu güçlü alternatif.\n• Endüstri kümelenmeleri: Katalonya, Bask, Navarra, Madrid bölgeleri.",
        "sektor_pazari": "• BSH, Electrolux, Fagor, Teka gibi markalarla uzun geçmişe sahip üretim ekosistemi.\n• Ürün gamı: soğutucu, ankastre, çamaşır & bulaşık makineleri.\n• İç pazar yüksek enerji sınıfı & ankastre ürünlere yöneliyor.\n• Yenileme pazarı (replacement market) hızla büyüyor.",
        "one_cikan_sirketler": "• BSH España (Balay, Bosch, Siemens) – Zaragoza, Santander\n• Electrolux España – Madrid & Girona\n• Fagor Industrial / CNA Group – Basque Country\n• Teka Industrial S.A. – Santander\n• Aspes / Cata / Orbegozo – yerli markalar",
        "egilimler_ve_zorluklar": "• Enerji maliyetleri & işçilik giderleri yüksek.\n• Yeşil dönüşüm ve yenilenebilir enerji yatırımları hız kazandı.\n• AB enerji etiketi değişimleri üretimi etkiliyor.\n• Tedarik zincirinde yerli–Avrupa içi komponent tercihi öne çıkıyor.",
        "vergilendirme_ve_gumruk": "• AB Gümrük Birliği: %0 gümrük.\n• KDV: %21 (mahsuba tabi).\n• Gümrükleme süresi: 3–4 gün.\n• Zorunlu: CE, RoHS, REACH.",
        "teleset_degerlendirmesi": "• BSH, Electrolux iş birliklerinin güçlendirilmesi öncelikli fırsat.\n• Kondanser, Kablo Grubu, Metal Parça ürünleri için uygun pazar.\n• Lojistik avantaj: kısa teslimat ve AB içi üretim entegrasyonu.\n• MES–ERP uyumlu sistem yapısı rekabet avantajı sağlar.",
        "hedef_urunler": "Kondanser, Kablo Grubu, Metal Parça"
    },
    {
        "ulke_kodu": "PT",
        "ulke_adi": "Portekiz",
        "bayrak_emoji": "",
        "oncelik_sinifi": "İkincil / Entegre Pazar",
        "genel_gorunum": "• Güney Avrupa'nın sanayi ve lojistik merkezlerinden biri.\n• GSYH = 280 milyar USD, AB üyesi ekonomi.\n• Türkiye'den 3–4 günde karayolu teslimat, denizyolu güçlü alternatif.\n• Endüstri kümelenmeleri: Porto, Aveiro, Lizbon, Coimbra bölgeleri.",
        "sektor_pazari": "• Üretim ölçeği sınırlı ancak ithalat ve montaj ağı güçlü.\n• Bosch/Siemens, Whirlpool, Teka, Candy markalarının üretim & montaj operasyonları mevcut.\n• İç pazarda enerji verimliliği ve ankastre ürün talebi artıyor.\n• OEM/ODM tedarikçileri genellikle İspanya ve Fransa ile entegre çalışıyor.",
        "one_cikan_sirketler": "• BSH Electrodomésticos Portugal – Aveiro\n• Whirlpool Portugal – Coimbra bölgesi\n• Teka Portugal – Santo Tirso\n• Candy-Hoover Portugal (Haier Europe) – Braga\n• Grupo Mecwide – Metal işleme ve fabrika ekipmanı üretimi",
        "egilimler_ve_zorluklar": "• Enerji maliyetleri artmakta, ancak yenilenebilir enerji kullanımı yaygın.\n• Küçük iç pazar, yüksek ithalat bağımlılığı.\n• İşçilik maliyeti düşük, teknik personel kalitesi yükseliyor.\n• AB fonlarıyla sanayi dijitalleşmesi ve enerji dönüşümü destekleniyor.",
        "vergilendirme_ve_gumruk": "• AB Gümrük Birliği: %0 gümrük.\n• KDV: %23 (mahsuba tabi).\n• Gümrükleme süresi: 4–5 gün.\n• Zorunlu: CE, RoHS, REACH.",
        "teleset_degerlendirmesi": "• BSH, Whirlpool, Teka gibi müşterilerle tedarik yakınlığı yüksek.\n• Kondanser, Kablo Grubu ve Metal komponent ürünlerinde uygun maliyetli giriş pazarı.\n• İspanya–Portekiz ikili pazar stratejisiyle sinerji sağlanabilir.\n• Kısa termin süreleri, AB içi avantaj ve ISO sertifikasyon uyumu öne çıkar.",
        "hedef_urunler": "Kondanser, Kablo Grubu, Metal Komponent"
    }
]

for k in kanvas_listesi:
    obj, created = HedefPazarKanvas.objects.update_or_create(
        ulke_kodu=k["ulke_kodu"],
        defaults=k
    )
    print(f"{obj.ulke_adi} Kanvas Karti -> {'Olusturuldu' if created else 'Guncellendi'}")
print("Tum 5 Ulke Kanvas Is Modeli basariyla yuklendi!")
