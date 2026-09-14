from django.core.management.base import BaseCommand
from django.utils import timezone
from crm_takip.models import (
    PrototipAdimTanimi,
    PrototipSureci,
    PrototipAdimKaydi,
    PrototipGecmisLog,
    MusteriKarti
)

ADIMLAR_DATA = [
    {
        "adim_no": 1,
        "faz": "FAZ1",
        "baslik": "Prototip Talebinin Alınması ve Süreç Girdilerinin Temini",
        "faaliyet_tanimi": "Prototip talebi gelir ve talebe ilişkin bilgi ve belgeler süreç girdisi olarak temin edilir.",
        "sorumlular": "Satış-Analiz Sorumlusu, Fabrika Müdürü, Proje Sorumlusu",
        "ilgili_dokumanlar": "Müşteri Portalı, Teknik Dokümanlar, E-mail",
        "karar_adimi_mi": False
    },
    {
        "adim_no": 2,
        "faz": "FAZ1",
        "baslik": "Talep ve Teknik Dokümanların İncelenmesi, Proje Ekibinin Belirlenmesi",
        "faaliyet_tanimi": "Talep ile gelen bilgi, belge ve teknik dokümanların incelenir, ön değerlendirme yapılarak proje ekibinin belirlenir.",
        "sorumlular": "Fabrika Müdürü, Proje Sorumlusu",
        "ilgili_dokumanlar": "E-mail, Toplantı Notu",
        "karar_adimi_mi": False
    },
    {
        "adim_no": 3,
        "faz": "FAZ1",
        "baslik": "Ön Değerlendirme Uygunluğu ve Prototip İmalat Fizibilitesi",
        "faaliyet_tanimi": "Ön değerlendirme uygun mu? İlgili prototip imalatı gerçekleştirilebilir mi?",
        "sorumlular": "Proje Ekibi",
        "ilgili_dokumanlar": "-",
        "karar_adimi_mi": True
    },
    {
        "adim_no": 4,
        "faz": "FAZ1",
        "baslik": "Prototip Niteliğinin Müşteri ile Sorgulanması ve Kapsam Belirleme",
        "faaliyet_tanimi": "Yapılacak prototipin niteliği, müşteri ile iletişime geçilerek sorgulanır. Yapılacak ürün prototip üretimi sonrası seri üretimde kullanılacak mı, ya da mühendislik değişikliği yapılacak mı?",
        "sorumlular": "Proje Sorumlusu",
        "ilgili_dokumanlar": "Teknik Dokümanlar, E-mail",
        "karar_adimi_mi": True
    },
    {
        "adim_no": 5,
        "faz": "FAZ1",
        "baslik": "Geçici Ürün Ağaçlarının veya BOM Listesinin Hazırlanması",
        "faaliyet_tanimi": "Geçici Ürün ağaçlarının veya BOM List hazırlanır.",
        "sorumlular": "Proje Sorumlusu",
        "ilgili_dokumanlar": "Teknik Dokümanlar, E-mail",
        "karar_adimi_mi": False
    },
    {
        "adim_no": 6,
        "faz": "FAZ1",
        "baslik": "Yeni Hammadde Taslak Speklerinin Hazırlanması ve Satınalmaya İletimi",
        "faaliyet_tanimi": "Yeni bir hammadde var ise taslak hammadde speklerinin hazırlanarak, tedarikçi ve fiyat araştırması için satınalma departmanına iletilir.",
        "sorumlular": "Proje Sorumlusu",
        "ilgili_dokumanlar": "G-Star / Solidworks / PDF, E-mail, Müşteri Teknik Dokümanları",
        "karar_adimi_mi": False
    },
    {
        "adim_no": 7,
        "faz": "FAZ1",
        "baslik": "Satınalma Tedarik Koşulları ve Fiyat Bilgilerinin Temini",
        "faaliyet_tanimi": "Satın alma taleplerine ilişkin tedarik koşulları ve fiyat bilgilerinin satınalma bölümünden eksiksiz olarak temin edilmesi.",
        "sorumlular": "Fabrika Müdürü, Proje Sorumlusu, Satınalma Sorumlusu",
        "ilgili_dokumanlar": "Teknik Dokümanlar, E-mail",
        "karar_adimi_mi": False
    },
    {
        "adim_no": 8,
        "faz": "FAZ1",
        "baslik": "Maliyet ve Teklif Sonucunun Fabrika Müdürü / Satış Analiz Sorumlusuna İletilmesi",
        "faaliyet_tanimi": "Sonucun müşteri ile gerekli görüşmeleri yapmak üzere Fabrika Müdürü / Satış Analiz Sorumlusuna iletilmesi.",
        "sorumlular": "Satış-Analiz Sorumlusu, Fabrika Müdürü, Proje Sorumlusu",
        "ilgili_dokumanlar": "Excel BOM List, E-mail",
        "karar_adimi_mi": False
    },
    {
        "adim_no": 9,
        "faz": "FAZ1",
        "baslik": "Müşteri Başlangıç Onayı Kontrolü",
        "faaliyet_tanimi": "Müşteri ile yapılan görüşmeler sonucunda müşteri başlangıç için onay verdi mi?",
        "sorumlular": "Satış-Analiz Sorumlusu, Fabrika Müdürü, Proje Sorumlusu",
        "ilgili_dokumanlar": "Müşteri Portalı, E-mail",
        "karar_adimi_mi": True
    },
    {
        "adim_no": 10,
        "faz": "FAZ2",
        "baslik": "Müşteri Termininin Değerlendirilmesi ve Bilgilendirme",
        "faaliyet_tanimi": "Müşterinin belirlediği terminin değerlendirilerek Proje Sorumlusu tarafından Fabrika Müdürü ve/veya Müşteri bilgilendirilir.",
        "sorumlular": "Fabrika Müdürü, Proje Sorumlusu",
        "ilgili_dokumanlar": "E-mail",
        "karar_adimi_mi": False
    },
    {
        "adim_no": 11,
        "faz": "FAZ2",
        "baslik": "Makine, Ekipman, Kalıp ve Ölçüm Cihazı Final Şartnamesinin İletilmesi",
        "faaliyet_tanimi": "Proje ihtiyacı makine, ekipman, kalıp, ölçüm cihazı final şartnamesi hazırlanarak, tedarik edilmek üzere satın alma sorumlusuna iletilir.",
        "sorumlular": "Proje Sorumlusu, Üretim Sorumlusu, Planlama Sorumlusu",
        "ilgili_dokumanlar": "Erp Sistemi, E-mail",
        "karar_adimi_mi": False
    },
    {
        "adim_no": 12,
        "faz": "FAZ2",
        "baslik": "Yeni Hammadde Speklerinin Satınalma ve Kaliteye İletilmesi",
        "faaliyet_tanimi": "Yeni bir hammadde kullanımı var ise hammadde spekleri hazırlanarak tedarik planlama, satınalma ve kalite/giriş kalite kontrol sorumlularına iletilir, gerekirse proje hammadde&bileşen ihtiyacı satınalmaya bildirilir.",
        "sorumlular": "Proje Sorumlusu, İlgili Bölümler",
        "ilgili_dokumanlar": "Teknik Dokümanlar, E-mail, Erp Sistemi",
        "karar_adimi_mi": False
    },
    {
        "adim_no": 13,
        "faz": "FAZ2",
        "baslik": "Satınalma ve Tedarik Termin Tarihlerinin Takibi ve Aksaklık Bildirimi",
        "faaliyet_tanimi": "Satınalma ve tedarik bölümünden bildirilen hammadde, malzeme ve/veya makine, ekipman termin tarihleri kontrol edilir, terminde aksamaya yol açacak durumlar Fabrika Müdürüne ve/veya Müşteriye bildirilir.",
        "sorumlular": "Proje Sorumlusu",
        "ilgili_dokumanlar": "E-mail",
        "karar_adimi_mi": False
    },
    {
        "adim_no": 14,
        "faz": "FAZ2",
        "baslik": "ERP Numune Stok Kodunun Açılması ve Geçici Ürün Ağacının Oluşturulması",
        "faaliyet_tanimi": "Ürün ve ürün ile ilgili işlemlerin takibini sağlamak için numune stok kodu açılır ve geçici ürün ağacı oluşturulur.",
        "sorumlular": "Proje Sorumlusu",
        "ilgili_dokumanlar": "Teknik Dokümanlar, E-mail, Erp Sistemi",
        "karar_adimi_mi": False
    },
    {
        "adim_no": 15,
        "faz": "FAZ3",
        "baslik": "Prototip Üretim Bilgi/Belgelerinin Hazırlanması ve Üretim Talebinin Açılması",
        "faaliyet_tanimi": "Prototip üretimi için gerekli bilgi ve belgeler hazırlanır, ilgili birimlere dağıtılarak prototip üretim talebi açılır.",
        "sorumlular": "Proje Sorumlusu",
        "ilgili_dokumanlar": "Erp Sistemi, Çizim Programı, Malzeme Teknik Bilgi Listeleri, PMK-EK-001 - PMP-EK-001 Numune bildirim formu",
        "karar_adimi_mi": False
    },
    {
        "adim_no": 16,
        "faz": "FAZ3",
        "baslik": "Depodan Hammadde Teslimi ve Prototip İmalatının Gerçekleştirilmesi",
        "faaliyet_tanimi": "Prototip üretimi için tedarik edilen hammaddeler depodan teslim alınarak prototip üretiminin gerçekleştirilmesi sağlanır.",
        "sorumlular": "Üretim Sorumlusu, Hammadde Sorumlusu",
        "ilgili_dokumanlar": "Erp Sistemi, Malzeme Teknik Bilgi Listeleri, PMK-EK-001 - PMP-EK-001 Numune bildirim formu",
        "karar_adimi_mi": False
    },
    {
        "adim_no": 17,
        "faz": "FAZ3",
        "baslik": "Üretilen Prototip Numunelerin Kalite Kontrol ve Ölçümlerinin Yapılması",
        "faaliyet_tanimi": "Üretilen prototip numunelerin müşteri talepleri doğrultusunda kalite kontrol ve ölçümlerinin yapılması sağlanır.",
        "sorumlular": "Kalite Sorumlusu",
        "ilgili_dokumanlar": "PMG-EK-001 ISIR Formu (Initial Sample Inspection Report)",
        "karar_adimi_mi": False
    },
    {
        "adim_no": 18,
        "faz": "FAZ3",
        "baslik": "Prototip Numune Ölçüm Sonuçları Uygun mu?",
        "faaliyet_tanimi": "Üretilen numunelerin ölçüm sonuçları müşteri talep ve şartnamelerine uygun mu?",
        "sorumlular": "Kalite Sorumlusu",
        "ilgili_dokumanlar": "PMG-EK-001 ISIR Formu",
        "karar_adimi_mi": True
    },
    {
        "adim_no": 19,
        "faz": "FAZ3",
        "baslik": "Prototip Numunenin Müşteriye Sevki ve Müşteri Yetkilisinin Bilgilendirilmesi",
        "faaliyet_tanimi": "Kontrolleri tamamlanarak onaylanan prototip numune, beraberinde gerekli belgeler ile müşteriye sevk edilir ve talebi yapan müşteri yetkilisi bilgilendirilir.",
        "sorumlular": "Üretim Planlama Sorumlusu, Proje Sorumlusu",
        "ilgili_dokumanlar": "E-mail, Erp Sistemi, İrsaliye",
        "karar_adimi_mi": False
    },
    {
        "adim_no": 20,
        "faz": "FAZ3",
        "baslik": "Müşteri Gönderilen Prototip Numuneyi ve Belgeleri Onayladı mı?",
        "faaliyet_tanimi": "Gönderilen prototip numune ve ilişkili belgeler müşteri tarafından onaylandı mı?",
        "sorumlular": "Proje Sorumlusu",
        "ilgili_dokumanlar": "Müşteri Portalı, Teknik Dokümanlar, E-mail",
        "karar_adimi_mi": True
    },
    {
        "adim_no": 21,
        "faz": "FAZ4",
        "baslik": "Prototip Üretim Sonrası Ürün Reçetesinin Kontrolü ve Değişiklik Bildirimi",
        "faaliyet_tanimi": "Prototip üretim sonrasında ürün ile ilgili ürün reçetesi kontrol edilir, değişiklik tespiti durumunda Satış Analiz Sorumlusu ve/veya Fabrika Müdürüne bilgi verilir.",
        "sorumlular": "Proje Sorumlusu",
        "ilgili_dokumanlar": "E-mail, Erp Sistemi, Excel",
        "karar_adimi_mi": False
    },
    {
        "adim_no": 22,
        "faz": "FAZ4",
        "baslik": "Sürecin Kapatılması ve İlgili Birimlerin Bilgilendirilmesi",
        "faaliyet_tanimi": "Süreç kapatılıp, ilgili birimler bilgilendirilir.",
        "sorumlular": "Proje Sorumlusu, Satış Analiz Sorumlusu",
        "ilgili_dokumanlar": "E-mail, Erp Sistemi",
        "karar_adimi_mi": False
    },
    {
        "adim_no": 23,
        "faz": "FAZ4",
        "baslik": "Süreç Etkinliğinin Gözden Geçirilmesi, Dijitalleşme ve Öğrenilmiş Dersler",
        "faaliyet_tanimi": "Süreç ve sonuçlar gözden geçirilerek gerekiyorsa iyileştirme yapılır, dijital ortama taşınır, edinilen bilgi ve deneyimler paylaşılır.",
        "sorumlular": "Proje Sorumlusu, Satış Analiz Sorumlusu",
        "ilgili_dokumanlar": "Öğrenilmiş Dersler Formu",
        "karar_adimi_mi": True
    }
]

DEMO_PROTOTIP_DATA = [
    {
        "kod": "PRT-2026-001",
        "ad": "Yeni Nesil R290 Kompresör Bağlantı Dirseği Prototipi",
        "musteri_adi": "Arçelik A.Ş.",
        "parca_kodu": "PRT-ARC-9912",
        "revizyon_no": "Rev.01",
        "prototip_tipi": "YENI_TASARIM",
        "urun_grubu": "Kondenser & Sogutma",
        "ilgili_fabrika": "Teleset 1 (Manisa)",
        "guncel_adim_no": 16,
        "durum": "DEVAM_EDIYOR",
        "aciklama": "Arçelik Çayırova Ar-Ge talebi doğrultusunda R290 gazına uygun bakır-alüminyum geçiş dirseği prototip üretimi."
    },
    {
        "kod": "PRT-2026-002",
        "ad": "Vestel Çamaşır Makinesi Üst Travers Sacı Ağırlık Azaltma Prototipi",
        "musteri_adi": "Vestel Beyaz Eşya",
        "parca_kodu": "PRT-VES-4421",
        "revizyon_no": "Rev.02",
        "prototip_tipi": "VAVE_MALIYET",
        "urun_grubu": "Metal Parca & Sac",
        "ilgili_fabrika": "Teleset 2 (Manisa)",
        "guncel_adim_no": 8,
        "durum": "DEVAM_EDIYOR",
        "aciklama": "VAVE projesi kapsamında 1.2mm sacdan 1.0mm yüksek mukavemetli saca geçiş deneme prototipi."
    },
    {
        "kod": "PRT-2026-003",
        "ad": "BSH Bosch Fırın Yan Gövde Kablo Demeti Fikstür Prototipi",
        "musteri_adi": "BSH Bosch Hausgeräte GmbH",
        "parca_kodu": "PRT-BSH-1108",
        "revizyon_no": "Rev.01",
        "prototip_tipi": "MUSTERI_TEST",
        "urun_grubu": "Kablo Grubu",
        "ilgili_fabrika": "Teleset (Kocaeli)",
        "guncel_adim_no": 23,
        "durum": "BASARIYLA_TAMAMLANDI",
        "aciklama": "BSH fırın hattı için numune kablo seti başarıyla imal edildi, ISIR onayı alındı ve süreç arşivlendi."
    }
]


class Command(BaseCommand):
    help = "23 Adımlık Prototip Süreci Master Adımlarını ve Demo Verilerini Yükler"

    def handle(self, *args, **options):
        # 1. 23 Master Adımı Yükle / Güncelle
        for data in ADIMLAR_DATA:
            adim, created = PrototipAdimTanimi.objects.update_or_create(
                adim_no=data["adim_no"],
                defaults={
                    "faz": data["faz"],
                    "baslik": data["baslik"],
                    "faaliyet_tanimi": data["faaliyet_tanimi"],
                    "sorumlular": data["sorumlular"],
                    "ilgili_dokumanlar": data["ilgili_dokumanlar"],
                    "karar_adimi_mi": data["karar_adimi_mi"]
                }
            )
        self.stdout.write(self.style.SUCCESS("Prototip Süreci 23 Master Adımı Başarıyla Güncellendi!"))

        # 2. Demo Prototip Projeleri
        adim_tanimlari = PrototipAdimTanimi.objects.all().order_by("adim_no")
        for p_data in DEMO_PROTOTIP_DATA:
            if not PrototipSureci.objects.filter(kod=p_data["kod"]).exists():
                musteri = MusteriKarti.objects.filter(kisa_ad__icontains=p_data["musteri_adi"][:4]).first()
                surec = PrototipSureci.objects.create(
                    kod=p_data["kod"],
                    ad=p_data["ad"],
                    musteri_adi=p_data["musteri_adi"],
                    musteri_karti=musteri,
                    parca_kodu=p_data["parca_kodu"],
                    revizyon_no=p_data["revizyon_no"],
                    prototip_tipi=p_data["prototip_tipi"],
                    urun_grubu=p_data["urun_grubu"],
                    ilgili_fabrika=p_data["ilgili_fabrika"],
                    guncel_adim_no=p_data["guncel_adim_no"],
                    durum=p_data["durum"],
                    aciklama=p_data["aciklama"]
                )

                for adim in adim_tanimlari:
                    if p_data["durum"] == "BASARIYLA_TAMAMLANDI":
                        durum = "TAMAMLANDI"
                    else:
                        if adim.adim_no < p_data["guncel_adim_no"]:
                            durum = "TAMAMLANDI"
                        elif adim.adim_no == p_data["guncel_adim_no"]:
                            durum = "DEVAM_EDIYOR"
                        else:
                            durum = "BEKLIYOR"

                    dokuman = adim.dokuman_listesi[0] if adim.dokuman_listesi else ""
                    PrototipAdimKaydi.objects.create(
                        surec=surec,
                        adim=adim,
                        durum=durum,
                        dokuman_referansi=dokuman if durum == "TAMAMLANDI" else ""
                    )

                PrototipGecmisLog.objects.create(
                    surec=surec,
                    islem=f"Prototip Süreci Başlatıldı: {surec.kod}",
                    detay=f"{surec.ad} konulu prototip süreci açıldı.",
                    yapan=surec.sorumlu_proje_sorumlusu
                )

        self.stdout.write(self.style.SUCCESS("Prototip Süreci 23 Adımı ve Demo Verileri Başarıyla Yüklendi!"))
