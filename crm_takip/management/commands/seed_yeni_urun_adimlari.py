from django.core.management.base import BaseCommand
from crm_takip.models import (
    YeniUrunAdimTanimi,
    YeniUrunDevreyeAlmaSureci,
    YeniUrunAdimKaydi,
    YeniUrunGecmisLog,
    MusteriKarti,
    UrunGrubuKarti,
)
from django.utils import timezone


class Command(BaseCommand):
    help = "45 Adımlık Yeni Ürün Devreye Alma Süreci (APQP/NPI) master verilerini ve demo süreçleri yükler."

    def handle(self, *args, **options):
        adimlari_tanimla()
        demo_surecleri_olustur()
        self.stdout.write(self.style.SUCCESS("Yeni Ürün Devreye Alma Süreci 45 Adımı ve Demo Verileri Başarıyla Yüklendi!"))


ADIMLAR_DATA = [
    {
        "adim_no": 1,
        "baslik": "Yeni Ürün Talebi ve Girdi Belgelerinin Temini",
        "faaliyet_tanimi": "1. Yeni ürün talebi gelir ve talebe ilişkin bilgi ile belgeler süreç girdisi olarak temin edilir.",
        "sorumlular": "Satış-Analiz Sorumlusu, Fabrika Müdürü, Proje Sorumlusu",
        "ilgili_dokumanlar": "Müşteri Portalı, Teknik Dokümanlar, E-mail",
        "karar_adimi_mi": False,
        "faz": "FAZ1",
    },
    {
        "adim_no": 2,
        "baslik": "Talep, Belge ve Numune Ön Değerlendirmesi",
        "faaliyet_tanimi": "2. Talep ile birlikte iletilen bilgi, belge, teknik dökümanlar ve varsa numune incelenerek ön değerlendirme yapılır. Ön değerlendirme çalışması uygun mu?",
        "sorumlular": "Proje Sorumlusu, Fabrika Müdürü",
        "ilgili_dokumanlar": "E-mail, Toplantı Notu",
        "karar_adimi_mi": True,
        "faz": "FAZ1",
    },
    {
        "adim_no": 3,
        "baslik": "Standart Dışı Proseslerin Satış Departmanına İletilmesi",
        "faaliyet_tanimi": "3. Projenin standart üretim proseslerimize uygun olmaması durumunda, stratejik değerlendirme yapılmak üzere konu satış departmanına iletilir.",
        "sorumlular": "Satış-Analiz Sorumlusu, Fabrika Müdürü, Proje Sorumlusu",
        "ilgili_dokumanlar": "E-mail, Toplantı Notu (Satış Süreci)",
        "karar_adimi_mi": False,
        "faz": "FAZ1",
    },
    {
        "adim_no": 4,
        "baslik": "Fizibilite Proje Ekibinin Belirlenmesi",
        "faaliyet_tanimi": "4. Fizibilite çalışması için proje ekibi belirlenir.",
        "sorumlular": "Fabrika Müdürü, Proje Sorumlusu",
        "ilgili_dokumanlar": "E-mail, Toplantı Notu, eBA Doküman ve İş Akışı Yönetim Sistemi",
        "karar_adimi_mi": False,
        "faz": "FAZ1",
    },
    {
        "adim_no": 5,
        "baslik": "Yeni Hammadde Spesifikasyonları ve Fiyat Araştırması",
        "faaliyet_tanimi": "5. Yeni bir hammadde varsa, taslak hammadde spesifikasyonları hazırlanır ve tedarikçi ile fiyat araştırması yapılması için satın alma departmanına iletilir. Belirtilen hammadde için onaylı tedarikçi varsa, bu bilgi de satın alma birimi ile paylaşılır.",
        "sorumlular": "Proje Sorumlusu",
        "ilgili_dokumanlar": "Teknik Dokümanlar, E-mail, eBA Doküman ve İş Akışı Yönetim Sistemi (Satınalma ve Tedarik Süreci)",
        "karar_adimi_mi": False,
        "faz": "FAZ1",
    },
    {
        "adim_no": 6,
        "baslik": "Yeni Makine, Ekipman ve Kalıp Şartnamesi Hazırlığı",
        "faaliyet_tanimi": "6. Yeni bir makine, ekipman, kalıp veya ölçüm cihazı gereksinimi varsa, teknik şartname hazırlanır ve tedarikçi ile fiyat araştırması yapılması için satın alma departmanına iletilir.",
        "sorumlular": "Proje Sorumlusu",
        "ilgili_dokumanlar": "G-Star / Solidworks, E-mail, Müşteri Teknik Dokümanları, eBA Doküman ve İş Akışı Yönetim Sistemi (Satınalma ve Tedarik Süreci)",
        "karar_adimi_mi": False,
        "faz": "FAZ1",
    },
    {
        "adim_no": 7,
        "baslik": "Satın Alma Fiyat ve Tedarik Şartnamelerinin Temini",
        "faaliyet_tanimi": "7. Satın alma bölümünden talep edilen fiyat bilgileri ve tedarik şartnameleri takip edilerek eksiksiz olarak temin edilir.",
        "sorumlular": "Fabrika Müdürü, Proje Sorumlusu, Satınalma Sorumlusu",
        "ilgili_dokumanlar": "Teknik Doküman, E-mail, Netsis",
        "karar_adimi_mi": False,
        "faz": "FAZ1",
    },
    {
        "adim_no": 8,
        "baslik": "Öğrenilmiş Dersler İncelemesi ve Fizibilite Çalışması",
        "faaliyet_tanimi": "8. Öğrenilmiş Dersler gözden geçirilir ve fizibilite çalışması yapılır.",
        "sorumlular": "Proje Ekibi",
        "ilgili_dokumanlar": "Fizibilite Planı, PMG-TL-002 Yeni Ürün Devreye Alma ve Mühendislik Değişiklikleri Talimatı, Öğrenilmiş Dersler Formu, eBA Doküman ve İş Akışı Yönetim Sistemi",
        "karar_adimi_mi": False,
        "faz": "FAZ1",
    },
    {
        "adim_no": 9,
        "baslik": "Fizibilite Çalışması Sonucu Uygunluk Değerlendirmesi",
        "faaliyet_tanimi": "9. Fizibilite çalışması sonucu uygun mu?",
        "sorumlular": "Proje Ekibi",
        "ilgili_dokumanlar": "eBA Doküman ve İş Akışı Yönetim Sistemi",
        "karar_adimi_mi": True,
        "faz": "FAZ1",
    },
    {
        "adim_no": 10,
        "baslik": "Geçici Ürün Ağacı (BOM List) ve Şahit Numune Kaydı",
        "faaliyet_tanimi": "10. Geçici ürün ağacı (BOM List) hazırlanır; teklif için alınan numune varsa, şahit numune olarak müşteriye ait şekilde kanıt niteliğinde saklanır, üzerine etiket yapıştırılır ve fotoğrafı çekilir.",
        "sorumlular": "Proje Sorumlusu",
        "ilgili_dokumanlar": "Teknik Dokümanlar, PMG-TL-002 Yeni Ürün Devreye Alma ve Mühendislik Değişiklikleri Talimatı, Excel BOM List, eBA Doküman ve İş Akışı Yönetim Sistemi",
        "karar_adimi_mi": False,
        "faz": "FAZ1",
    },
    {
        "adim_no": 11,
        "baslik": "Teknik Analiz Detaylarının Toplanması ve BOM/Fizibilite Paylaşımı",
        "faaliyet_tanimi": "11. Teknik analiz detayları toplanır; fizibilitesi uygun olan projeler için BOM listesi oluşturulur, uygun olmayan projeler için ise Fizibilite Raporu doğrultusunda stratejik değerlendirme ve müşteri ile gerekli görüşmelerin yapılması amacıyla Fabrika Müdürü / Satış Analiz Sorumlusuna bilgi verilir.",
        "sorumlular": "Satış-Analiz Sorumlusu, Fabrika Müdürü, Proje Sorumlusu",
        "ilgili_dokumanlar": "Excel BOM List, E-mail, Fizibilite Planı, eBA Doküman ve İş Akışı Yönetim Sistemi (Satış Süreci)",
        "karar_adimi_mi": False,
        "faz": "FAZ1",
    },
    {
        "adim_no": 12,
        "baslik": "Müşteri Proje Başlangıç Onayı",
        "faaliyet_tanimi": "12. Müşteri ile yapılan görüşmeler sonucunda proje başlangıcı için onay verildi mi?",
        "sorumlular": "Satış-Analiz Sorumlusu, Fabrika Müdürü, Proje Sorumlusu",
        "ilgili_dokumanlar": "Müşteri Portalı, E-mail",
        "karar_adimi_mi": True,
        "faz": "FAZ1",
    },
    {
        "adim_no": 13,
        "baslik": "Final Data / Fizibilite İncelemesi ve Proje Bilgilendirme Toplantısı",
        "faaliyet_tanimi": "13. Proje sorumlusu, final dataları ve Ön Teklif Fizibilite planını ve teklif aşamasında alınan şahit numune varsa inceler, başlatılan proje ile ilgili proje grubunu belirler ve yeni ürün bilgilendirme toplantısı yapar.",
        "sorumlular": "Proje Sorumlusu",
        "ilgili_dokumanlar": "PMG-EK-002 Yeni Ürün Üretilebilirlik Analiz Formu, Fizibilite Planı, E-mail, eBA Doküman ve İş Akışı Yönetim Sistemi",
        "karar_adimi_mi": False,
        "faz": "FAZ2",
    },
    {
        "adim_no": 14,
        "baslik": "Proje Zaman Planının Oluşturulması",
        "faaliyet_tanimi": "14. Müşterinin belirlediği proje takvimi göz önünde bulundurularak proje zaman planı oluşturulur; müşteri taleplerine uyulmayan durumlarda Proje Sorumlusu, Fabrika Müdürünü ve/veya Müşteriyi bilgilendirir.",
        "sorumlular": "Fabrika Müdürü, Proje Sorumlusu",
        "ilgili_dokumanlar": "PMG-EK-002 Yeni Ürün Üretilebilirlik Analiz Formu, E-mail",
        "karar_adimi_mi": False,
        "faz": "FAZ2",
    },
    {
        "adim_no": 15,
        "baslik": "Makine, Ekipman, Kalıp Final Şartnamesi ve Satın Alma İletimi",
        "faaliyet_tanimi": "15. Proje kapsamında ihtiyaç duyulan makine, ekipman, kalıp veya ölçüm cihazının final şartnamesi hazırlanır ve tedarik edilmek üzere satın alma sorumlusuna iletilir.",
        "sorumlular": "Proje Sorumlusu, Üretim Sorumlusu, Planlama Sorumlusu",
        "ilgili_dokumanlar": "Erp Sistemi, E-mail (Satınalma ve Tedarik Süreci)",
        "karar_adimi_mi": False,
        "faz": "FAZ2",
    },
    {
        "adim_no": 16,
        "baslik": "Final Hammadde Spesifikasyonları ve Ön Seri Tedarik Bildirimi",
        "faaliyet_tanimi": "16. Yeni bir hammadde kullanımı varsa, final hammadde spesifikasyonları hazırlanır ve tedarik planlama, satın alma ile kalite/giriş kalite kontrol sorumlularına iletilir; gerekirse ön seri üretim için hammadde ve bileşen ihtiyaçları da satın alma veya tedarik planlama birimine bildirilir.",
        "sorumlular": "Proje Sorumlusu / İlgili Bölümler",
        "ilgili_dokumanlar": "Erp Sistemi, E-mail (Satınalma ve Tedarik Süreci)",
        "karar_adimi_mi": False,
        "faz": "FAZ2",
    },
    {
        "adim_no": 17,
        "baslik": "Termin Tarihleri Kontrolü ve Zaman Planı Takibi",
        "faaliyet_tanimi": "17. Satınalma ve tedarik bölümünden bildirilen hammadde, malzeme ve/veya makine-ekipman termin tarihleri kontrol edilir; zaman planında aksamaya yol açabilecek durumlar Fabrika Müdürüne ve/veya Müşteriye bildirilir.",
        "sorumlular": "Proje Sorumlusu",
        "ilgili_dokumanlar": "PMG-EK-002 Yeni Ürün Üretilebilirlik Analiz Formu, E-mail",
        "karar_adimi_mi": False,
        "faz": "FAZ2",
    },
    {
        "adim_no": 18,
        "baslik": "Proses Akış Şemasının Hazırlanması veya Kontrolü",
        "faaliyet_tanimi": "18. Proses akış şeması hazırlanır veya mevcut şema kontrol edilir.",
        "sorumlular": "Proje Sorumlusu, Üretim Sorumlusu, Kalite Sorumlusu",
        "ilgili_dokumanlar": "İş-Akış Şeması (KLT-EK-056 / ÜRK-EK-003)",
        "karar_adimi_mi": False,
        "faz": "FAZ2",
    },
    {
        "adim_no": 19,
        "baslik": "Yerleşim Planı, Altyapı Hazırlığı ve Kurulum Kabulü",
        "faaliyet_tanimi": "19. İş akış planı dikkate alınarak proje için temin edilecek makine ve ekipmanlara göre yerleşim planı gözden geçirilir; gerekiyorsa düzenleme yapılır ve/veya altyapı hazırlığı değerlendirilir. Tedarik tamamlandığında kabul ve kurulum işlemleri takip edilir.",
        "sorumlular": "Satın Alma Sorumlusu, Proje Sorumlusu, Bakım Sorumlusu, Üretim Sorumlusu, İSG Uzmanı",
        "ilgili_dokumanlar": "Erp Sistemi, G-Star / Solidworks, E-mail, PDF, Müşteri Teknik Dokümanları (Yatırımlar ve Tesis Yön. Süreci)",
        "karar_adimi_mi": False,
        "faz": "FAZ2",
    },
    {
        "adim_no": 20,
        "baslik": "ERP Numune Stok Kodu ve Geçici Ürün Ağacı Açılışı",
        "faaliyet_tanimi": "20. Ürün ve ilgili işlemlerin takibini sağlamak amacıyla ERP sisteminde numune stok kodu açılır ve geçici ürün ağacı oluşturulur.",
        "sorumlular": "Proje Sorumlusu",
        "ilgili_dokumanlar": "Erp Sistemi, PMG-TL-002 Yeni Ürün Devreye Alma ve Mühendislik Değişiklikleri Talimatı",
        "karar_adimi_mi": False,
        "faz": "FAZ3",
    },
    {
        "adim_no": 21,
        "baslik": "Proses Hata Türü ve Etkileri Analizi (FMEA)",
        "faaliyet_tanimi": "21. Proses Hata Türü ve Etkileri analizi yapılır.",
        "sorumlular": "Proje Ekibi",
        "ilgili_dokumanlar": "KLG-EK-004 Hata Türü ve Etkileri Analiz Formu (FMEA)",
        "karar_adimi_mi": False,
        "faz": "FAZ3",
    },
    {
        "adim_no": 22,
        "baslik": "Kritik Noktaların Belirlenmesi ve Kontrol Planı Hazırlığı",
        "faaliyet_tanimi": "22. Kontrol planının hazırlanabilmesi için teknik resim ve müşteri şartnamesi üzerindeki kritik noktalar belirlenir, ilgili operasyon bilgileri kalite birimine iletilir.",
        "sorumlular": "Proje Sorumlusu, Kalite Sorumlusu",
        "ilgili_dokumanlar": "KLG-EK-031 Kalite Kontrol Planı, Erp Sistemi / MES",
        "karar_adimi_mi": False,
        "faz": "FAZ3",
    },
    {
        "adim_no": 23,
        "baslik": "Numune Üretim Talebi Açılması ve Parametrelerin Belirlenmesi",
        "faaliyet_tanimi": "23. Numune üretimi için gerekli bilgi ve belgeler hazırlanır, ilgili birimlere iletilir ve numune üretim talebi açılır. Makine yeterlilik talebi varsa numune sayısı buna göre belirlenir.",
        "sorumlular": "Proje Sorumlusu",
        "ilgili_dokumanlar": "Erp Sistemi, Çizim Programı, Malzeme Teknik Bilgi Listeleri, PMK-EK-001 - PMP-EK-001 Numune bildirim formu / PMG-EK-009 Numune Talep Formu, Sevk Talimatları",
        "karar_adimi_mi": False,
        "faz": "FAZ3",
    },
    {
        "adim_no": 24,
        "baslik": "Numune Üretiminin Gerçekleştirilmesi ve Süreç Takibi",
        "faaliyet_tanimi": "24. Numune üretimi için tedarik edilen hammaddelerin üretime ulaşması sağlanır, numune üretimi gerçekleştirilir ve süreci takip edilir.",
        "sorumlular": "Üretim Sorumlusu, Hammadde Sorumlusu",
        "ilgili_dokumanlar": "Erp Sistemi, Malzeme Teknik Bilgi Listeleri, PMK-EK-001 - PMP-EK-001 Numune bildirim formu, Sevk Talimatları",
        "karar_adimi_mi": False,
        "faz": "FAZ3",
    },
    {
        "adim_no": 25,
        "baslik": "Numunelerin Kalite Kontrol ve Ölçümleri (ISIR)",
        "faaliyet_tanimi": "25. Üretilen numunelerin kalite kontrol ve ölçümleri yapılır.",
        "sorumlular": "Kalite Sorumlusu",
        "ilgili_dokumanlar": "PMG-EK-001 ISIR Formu (Initial Sample Inspection Report)",
        "karar_adimi_mi": False,
        "faz": "FAZ3",
    },
    {
        "adim_no": 26,
        "baslik": "Numune Ölçüm Sonuçlarının Uygunluğu",
        "faaliyet_tanimi": "26. Numune ölçüm sonuçları, müşteri taleplerine, varsa teklif aşamasında gönderilen şahit numuneye ve şartnamelere uygun mu?",
        "sorumlular": "Kalite Sorumlusu",
        "ilgili_dokumanlar": "PMG-EK-001 ISIR Formu",
        "karar_adimi_mi": True,
        "faz": "FAZ3",
    },
    {
        "adim_no": 27,
        "baslik": "Numunenin Fotoğraflanması, Belgelerle Müşteriye Sevki",
        "faaliyet_tanimi": "27. Kontrolleri tamamlanmış ve onaylanmış numune, gerekli belgelerle birlikte müşteriye sevk edilir. Sevk öncesi numunenin fotoğrafı çekilir ve kanıt dokümanı olarak saklanır. Talebi yapan müşteri yetkilisi bilgilendirilir.",
        "sorumlular": "Üretim Planlama Sorumlusu, Proje Sorumlusu",
        "ilgili_dokumanlar": "E-mail, Erp Sistemi, PMG-TL-002 Yeni Ürün Devreye Alma ve Mühendislik Değişiklikleri Talimatı",
        "karar_adimi_mi": False,
        "faz": "FAZ3",
    },
    {
        "adim_no": 28,
        "baslik": "Müşteri Numune Onayı",
        "faaliyet_tanimi": "28. Gönderilen numune ve ilişkili belgeler müşteri tarafından onaylandı mı?",
        "sorumlular": "Proje Sorumlusu",
        "ilgili_dokumanlar": "Müşteri Portalı, Teknik Dokümanlar, E-mail",
        "karar_adimi_mi": True,
        "faz": "FAZ3",
    },
    {
        "adim_no": 29,
        "baslik": "Teknik Dokümanlar, Operatör Talimatları ve Şahit Numune Saklama",
        "faaliyet_tanimi": "29. Üretim için gerekli teknik ve destek dokümanlar hazırlanır veya kontrol edilir; ayrıca sistem dokümantasyonu gözden geçirilir ve gerekli revizyonlar yapılır. Müşteri, şahit numune sağlıyorsa, numune alınır ve kanıt olarak saklanır.",
        "sorumlular": "Proje Sorumlusu, Kalite Sorumlusu",
        "ilgili_dokumanlar": "PMG-TL-002 Yeni Ürün Devreye Alma ve Mühendislik Değişiklikleri Talimatı, Operatör Talimatları, Kablo Kesim Listeleri, Ambalaj ve Sevk Talimatları, PMG-EK-004 Teknik Doküman Dağıtım Çizelgesi",
        "karar_adimi_mi": False,
        "faz": "FAZ3",
    },
    {
        "adim_no": 30,
        "baslik": "Mamul Stok Kodu Açılışı ve Kesin Ürün Ağacı Oluşturma",
        "faaliyet_tanimi": "30. Numune stok kodu ile oluşturulan geçici ürün ağaçları kontrol edilir ve mamul stok kodu ile yeniden oluşturulur. Numune aşamasında yapılan değişiklikler varsa, ürün ağacındaki bu değişiklikler Satış Analiz Sorumlusu ve/veya Fabrika Müdürüne bildirilir.",
        "sorumlular": "Proje Sorumlusu",
        "ilgili_dokumanlar": "Erp Sistemi, E-mail",
        "karar_adimi_mi": False,
        "faz": "FAZ3",
    },
    {
        "adim_no": 31,
        "baslik": "Ön Seri Üretim Planlama ve İş Emri Oluşturma",
        "faaliyet_tanimi": "31. Ön seri üretim talebi, Planlama Sorumlusu veya Proje Sorumlusuna bildirilir; ön seri üretim planlanır, iş emri oluşturulur ve gerçekleştirilir.",
        "sorumlular": "Üretim Planlama Sorumlusu, Proje Sorumlusu",
        "ilgili_dokumanlar": "Müşteri Portalı, E-mail",
        "karar_adimi_mi": False,
        "faz": "FAZ4",
    },
    {
        "adim_no": 32,
        "baslik": "Ölçüm Sistemi Yeterliliği (MSA) Çalışmaları",
        "faaliyet_tanimi": "32. Ölçüm sistemi yeterliliği ve MSA çalışmaları gözden geçirilir ve takibi sağlanır.",
        "sorumlular": "Kalite Sorumlusu",
        "ilgili_dokumanlar": "KYG-EK-023 MSA Formu",
        "karar_adimi_mi": False,
        "faz": "FAZ4",
    },
    {
        "adim_no": 33,
        "baslik": "MSA Sonuçları Sistem Gereklilikleri Kontrolü",
        "faaliyet_tanimi": "33. MSA sonuçları sistem gerekliliklerini karşılıyor mu?",
        "sorumlular": "Kalite Sorumlusu",
        "ilgili_dokumanlar": "KYG-EK-023 MSA Formu (Uygunsuzluk Yönetimi Süreci)",
        "karar_adimi_mi": True,
        "faz": "FAZ4",
    },
    {
        "adim_no": 34,
        "baslik": "Proses ve/veya Makine Yeterlilik Çalışması (Cpk / Ppk)",
        "faaliyet_tanimi": "34. Proses ve/veya makine yeterlilik çalışması yapılır.",
        "sorumlular": "Kalite Sorumlusu",
        "ilgili_dokumanlar": "KLG-EK-002 Makine / Proses Yeterlilik Analizi Talimatı",
        "karar_adimi_mi": False,
        "faz": "FAZ4",
    },
    {
        "adim_no": 35,
        "baslik": "Proses / Makine Yeterlilik Sonuçları Uygunluğu",
        "faaliyet_tanimi": "35. Proses ve/veya makine yeterlilik çalışması sonuçları sistem gerekliliklerini karşılıyor mu?",
        "sorumlular": "Kalite Sorumlusu",
        "ilgili_dokumanlar": "KLG-EK-002 Makine / Proses Yeterlilik Analizi Talimatı (Uygunsuzluk Yönetimi)",
        "karar_adimi_mi": True,
        "faz": "FAZ4",
    },
    {
        "adim_no": 36,
        "baslik": "Ön Seri Üretim Kalite Kontrol ve Ölçümleri",
        "faaliyet_tanimi": "36. Ön seri üretim ürünlerinin kalite kontrol ve ölçümleri yapılır, sonuçlar Çıkış Kalite Kontrol raporuna kaydedilir.",
        "sorumlular": "Kalite Sorumlusu",
        "ilgili_dokumanlar": "KLG-EK-014 Çıkış Kalite Kontrol Raporu",
        "karar_adimi_mi": False,
        "faz": "FAZ4",
    },
    {
        "adim_no": 37,
        "baslik": "Ön Seri Ürün Kalite Ölçüm Sonuçları Uygunluğu",
        "faaliyet_tanimi": "37. Ön seri üretim ürünlerinin kalite kontrol ve ölçüm sonuçları müşteri talep ve şartnamelerini karşılıyor mu?",
        "sorumlular": "Kalite Sorumlusu, Proje Sorumlusu",
        "ilgili_dokumanlar": "KLG-EK-014 Çıkış Kalite Kontrol Raporu",
        "karar_adimi_mi": True,
        "faz": "FAZ4",
    },
    {
        "adim_no": 38,
        "baslik": "PPAP Dosyası / Ürün Dosyası Hazırlığı ve Müşteriye Sevkiyat",
        "faaliyet_tanimi": "38. Müşteri talebine göre PPAP dosyası veya ürün dosyası hazırlanarak ön seri ürün sevkiyatıyla paralel şekilde müşteriye gönderilir.",
        "sorumlular": "Proje Sorumlusu, Kalite Kontrol Sorumlusu, Üretim Sorumlusu, Kalite Sistem Yöneticisi",
        "ilgili_dokumanlar": "Bölüm Ortak Klasörleri",
        "karar_adimi_mi": False,
        "faz": "FAZ4",
    },
    {
        "adim_no": 39,
        "baslik": "Müşteri Ön Seri Üretim ve PPAP Onayı",
        "faaliyet_tanimi": "39. Ön seri üretim müşteri onayı aldı mı?",
        "sorumlular": "Proje Sorumlusu",
        "ilgili_dokumanlar": "Müşteri Portalı, E-mail",
        "karar_adimi_mi": True,
        "faz": "FAZ4",
    },
    {
        "adim_no": 40,
        "baslik": "Proje Kapanış Toplantısı ve Seri Üretim Önerileri",
        "faaliyet_tanimi": "40. Proje kapanış toplantısı yapılır; numune ve ön seri üretim aşamalarında karşılaşılan durumlar, seri üretim için gerekli tedbirler ve önerilerle birlikte proje ekibiyle paylaşılır.",
        "sorumlular": "Proje Sorumlusu",
        "ilgili_dokumanlar": "PMG-EK-002 Yeni Ürün Üretilebilirlik Analiz Formu (Dochuman Programına Aktarımı) / E-mail",
        "karar_adimi_mi": False,
        "faz": "FAZ5",
    },
    {
        "adim_no": 41,
        "baslik": "Müşteri Memnuniyet Anketi Gönderimi",
        "faaliyet_tanimi": "41. Proje sonuçlandırıldıktan sonra, yürütülen proje ile ilgili müşteri memnuniyetini değerlendirmek amacıyla müşteriye anket gönderilir.",
        "sorumlular": "Proje Sorumlusu",
        "ilgili_dokumanlar": "Yeni Ürün devreye Alma / Proje Kapanışı Sonrası Anketi, E-mail",
        "karar_adimi_mi": False,
        "faz": "FAZ5",
    },
    {
        "adim_no": 42,
        "baslik": "Onay Dokümanlarının Arşivlenmesi ve Seri Üretim Siparişi",
        "faaliyet_tanimi": "42. Müşteriden alınan onay dokümanları, ilgili ürün klasörüne veya numune onay klasörüne kaydedilir. Onaylanan ürüne ilişkin müşteriden seri üretim siparişi alındıktan sonra seri üretime geçiş tamamlanır.",
        "sorumlular": "Proje Ekibi",
        "ilgili_dokumanlar": "İş Emri, Bölüm İlgili Klasörler, E-mail",
        "karar_adimi_mi": False,
        "faz": "FAZ5",
    },
    {
        "adim_no": 43,
        "baslik": "Seri Üretim Sonrası Fizibilite ve Reçete Kontrolü",
        "faaliyet_tanimi": "43. Seri üretim sonrasında ürün ile ilgili fizibilite planı ile ürün reçetesinin kontrol edilmesi, değişiklik tespiti durumunda Satış Analiz Sorumlusu ve/veya Fabrika Müdürüne bildirilmesi",
        "sorumlular": "Proje Sorumlusu",
        "ilgili_dokumanlar": "E-mail, Erp Sistemi (Satış Süreci)",
        "karar_adimi_mi": False,
        "faz": "FAZ5",
    },
    {
        "adim_no": 44,
        "baslik": "Sürecin Kapatılması ve Performans Raporlaması (ESYS)",
        "faaliyet_tanimi": "44. Süreç kapatılır ve süreç performansı takip edilerek raporlanır",
        "sorumlular": "Proje Sorumlusu, Satış Analiz Sorumlusu",
        "ilgili_dokumanlar": "Entegre Süreç Yönetimi Sistemi (ESYS)",
        "karar_adimi_mi": False,
        "faz": "FAZ5",
    },
    {
        "adim_no": 45,
        "baslik": "Süreç İyileştirme, Dijitalleştirme ve YGG Paylaşımı",
        "faaliyet_tanimi": "45. Süreç ve sonuçlar düzenli olarak gözden geçirilir ve iyileştirilir, dijital ortama taşınır; edinilen bilgi ve deneyim paylaşılır.",
        "sorumlular": "Proje Sorumlusu, Satış Analiz Sorumlusu",
        "ilgili_dokumanlar": "PMG-EK-002 Yeni Ürün Üretilebilirlik Analiz Formu, Öğrenilmiş Dersler Formu, YGG Toplantıları",
        "karar_adimi_mi": False,
        "faz": "FAZ5",
    },
]


def adimlari_tanimla():
    for item in ADIMLAR_DATA:
        YeniUrunAdimTanimi.objects.update_or_create(
            adim_no=item["adim_no"],
            defaults={
                "baslik": item["baslik"],
                "faaliyet_tanimi": item["faaliyet_tanimi"],
                "sorumlular": item["sorumlular"],
                "ilgili_dokumanlar": item["ilgili_dokumanlar"],
                "karar_adimi_mi": item["karar_adimi_mi"],
                "faz": item["faz"],
            }
        )


def demo_surecleri_olustur():
    bosch = MusteriKarti.objects.filter(kisa_ad__icontains="Bosch").first()
    beko = MusteriKarti.objects.filter(kisa_ad__icontains="Beko").first()
    whirlpool = MusteriKarti.objects.filter(kisa_ad__icontains="Whirlpool").first()

    kondenser_ug = UrunGrubuKarti.objects.filter(baslik__icontains="Kondenser").first()
    metal_ug = UrunGrubuKarti.objects.filter(baslik__icontains="Metal").first()
    kablo_ug = UrunGrubuKarti.objects.filter(baslik__icontains="Kablo").first()

    # 1. Proje: Bosch Yeni Nesil R290 Tel Borulu Kondenser Devreye Alma (Adım 23'te)
    p1, created = YeniUrunDevreyeAlmaSureci.objects.get_or_create(
        kod="NPI-2026-001",
        defaults={
            "ad": "Yeni Nesil R290 Tel Borulu Kondenser NPI",
            "musteri_adi": "BSH Bosch Hausgeräte GmbH",
            "musteri_karti": bosch,
            "urun_grubu": "Kondenser & Sogutma",
            "urun_grubu_karti": kondenser_ug,
            "ilgili_fabrika": "Teleset 1 (Manisa)",
            "parca_kodu": "KND-BSH-R290-V3",
            "yillik_hedef_adet": 250000,
            "sorumlu_proje_lideri": "Buse Nur Baltacıoğlu",
            "sorumlu_fabrika_muduru": "Engin Kaya",
            "sorumlu_satis_analiz": "Hakan Yılmaz",
            "sorumlu_kalite": "Merve Çelik",
            "durum": "DEVAM_EDIYOR",
            "guncel_adim_no": 23,
            "aciklama": "Bosch eco-serisi yeni buzdolapları için özel tasarlanmış yüksek verimli tel borulu kondenser NPI projesi. Faz 1 ve 2 başarıyla tamamlandı, numune üretim parametreleri belirleniyor.",
        }
    )
    if created:
        for adim in YeniUrunAdimTanimi.objects.all():
            if adim.adim_no < 23:
                durum = 'TAMAMLANDI'
            elif adim.adim_no == 23:
                durum = 'DEVAM_EDIYOR'
            else:
                durum = 'BEKLIYOR'
            YeniUrunAdimKaydi.objects.create(
                surec=p1,
                adim=adim,
                durum=durum,
                tamamlayan="Buse Nur Baltacıoğlu" if durum == 'TAMAMLANDI' else None,
                tamamlanma_tarihi=timezone.now() if durum == 'TAMAMLANDI' else None
            )
        YeniUrunGecmisLog.objects.create(
            surec=p1,
            islem="NPI Projesi Başlatıldı",
            detay="Bosch R290 Kondenser projesi başlatıldı ve Adım 23'e kadar olan tasarım/planlama adımları onaylandı.",
            yapan="Buse Nur Baltacıoğlu"
        )

    # 2. Proje: Beko Inox Sac Yan Panel & Şasi Pres Kalıbı NPI (Adım 33'te DÖF sürecinde)
    p2, created2 = YeniUrunDevreyeAlmaSureci.objects.get_or_create(
        kod="NPI-2026-002",
        defaults={
            "ad": "Inox Sac Yan Panel & Şasi Pres Kalıbı Devreye Alma",
            "musteri_adi": "Beko Europe B.V.",
            "musteri_karti": beko,
            "urun_grubu": "Metal Parca & Sac",
            "urun_grubu_karti": metal_ug,
            "ilgili_fabrika": "Teleset 2 (Manisa)",
            "parca_kodu": "PNL-BK-INOX-700",
            "yillik_hedef_adet": 400000,
            "sorumlu_proje_lideri": "Caner Demir",
            "sorumlu_fabrika_muduru": "Engin Kaya",
            "sorumlu_satis_analiz": "Hakan Yılmaz",
            "sorumlu_kalite": "Merve Çelik",
            "durum": "UYGUNSUZLUK_YONETIMINDE",
            "guncel_adim_no": 33,
            "aciklama": "Beko Inox çamaşır makinesi şasisi yan panel sac şekillendirme ve kalıp doğrulama. Adım 33'te MSA Gage R&R %14 çıktığı için DÖF açılarak fikstür revizyonu yapılıyor.",
        }
    )
    if created2:
        for adim in YeniUrunAdimTanimi.objects.all():
            if adim.adim_no < 33:
                durum = 'TAMAMLANDI'
            elif adim.adim_no == 33:
                durum = 'DEVAM_EDIYOR'
            else:
                durum = 'BEKLIYOR'
            YeniUrunAdimKaydi.objects.create(
                surec=p2,
                adim=adim,
                durum=durum,
                tamamlayan="Caner Demir" if durum == 'TAMAMLANDI' else None,
                tamamlanma_tarihi=timezone.now() if durum == 'TAMAMLANDI' else None,
                karar_sonucu="HAYIR (MSA Gage R&R Uygunsuzluğu -> DÖF)" if adim.adim_no == 33 else None
            )
        YeniUrunGecmisLog.objects.create(
            surec=p2,
            islem="Adım 33: MSA Uygunsuzluğu Tespit Edildi",
            detay="Ölçüm sistemi yeterliliği sınır değerde kaldığından Uygunsuzluk Yönetim Süreci (DÖF-2026-08) tetiklendi.",
            yapan="Merve Çelik"
        )

    # 3. Proje: Whirlpool Bulaşık Makinesi Ana Kablo Demeti (Adım 1'de yeni başladı)
    p3, created3 = YeniUrunDevreyeAlmaSureci.objects.get_or_create(
        kod="NPI-2026-003",
        defaults={
            "ad": "Whirlpool W-Series Bulaşık Makinesi Ana Kablo Demeti",
            "musteri_adi": "Whirlpool Corporation",
            "musteri_karti": whirlpool,
            "urun_grubu": "Kablo Grubu",
            "urun_grubu_karti": kablo_ug,
            "ilgili_fabrika": "Teleset 3 (Kocaeli)",
            "parca_kodu": "HNS-WHR-DSH-99",
            "yillik_hedef_adet": 180000,
            "sorumlu_proje_lideri": "Buse Nur Baltacıoğlu",
            "sorumlu_fabrika_muduru": "Serdar Acar",
            "sorumlu_satis_analiz": "Hakan Yılmaz",
            "sorumlu_kalite": "Ahmet Yurt",
            "durum": "DEVAM_EDIYOR",
            "guncel_adim_no": 1,
            "aciklama": "Yeni nesil bulaşık makinesi için otomotiv standartlarında su geçirmez konnektörlü kablo grubu devreye alma süreci başlangıcı.",
        }
    )
    if created3:
        for adim in YeniUrunAdimTanimi.objects.all():
            YeniUrunAdimKaydi.objects.create(
                surec=p3,
                adim=adim,
                durum='DEVAM_EDIYOR' if adim.adim_no == 1 else 'BEKLIYOR'
            )
        YeniUrunGecmisLog.objects.create(
            surec=p3,
            islem="NPI Süreci Başlatıldı",
            detay="Müşteri teknik dokümanları ve şartnameleri sisteme yüklendi.",
            yapan="Buse Nur Baltacıoğlu"
        )
