from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from crm_takip.models import (
    MuhendislikDegisikligiAdimTanimi,
    MuhendislikDegisikligiSureci,
    MuhendislikDegisikligiAdimKaydi,
    MuhendislikDegisikligiGecmisLog,
    MusteriKarti
)

class Command(BaseCommand):
    help = '34 Adımlık Mühendislik Değişikliği Süreci Master Adımlarını ve Demo Verilerini Yükler'

    def handle(self, *args, **kwargs):
        adilar_verisi = [
            {
                'adim_no': 1,
                'baslik': 'Değişiklik Talebinin Alınması ve Doküman Temini',
                'faaliyet_tanimi': '1. Müşteri veya iç proses kaynaklı değişiklik talebi alınır. Talep ile birlikte gönderilen tüm bilgi, belge ve teknik dokümanlar temin edilir.',
                'sorumlular': 'Satış-Analiz Sorumlusu, Fabrika Müdürü, Proje Sorumlusu',
                'ilgili_dokumanlar': 'Müşteri Portalı, Teknik Dokümanlar, E-mail',
                'faz': 'FAZ1',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 2,
                'baslik': 'Talep, Belge ve Numune Ön Değerlendirmesi',
                'faaliyet_tanimi': '2. Talep ile iletilen bilgi, belge ve teknik dokümanlar ile varsa numuneler incelenerek ön değerlendirme yapılır; mevcut numunelerin geçerliliği müşteri ile teyit edilir ve gerekli olması halinde yeni alınan şahit numune etiketlenerek, fotoğraflanarak kayıt altına alınır.',
                'sorumlular': 'Proje Sorumlusu',
                'ilgili_dokumanlar': 'Müşteri Teknik Dokümanları',
                'faz': 'FAZ1',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 3,
                'baslik': 'Teknik ve Makine / Ekipman Uygulanabilirlik Kontrolü',
                'faaliyet_tanimi': '3. Revizyonun teknik spesifikasyonlarda belirtildiği şekilde uygulanabilirliği ve üretimin mevcut makine ve ekipmanlarla gerçekleştirilebilirliği kontrol edilir.',
                'sorumlular': 'Proje Sorumlusu',
                'ilgili_dokumanlar': 'Teknik Dokümanlar, E-mail',
                'faz': 'FAZ1',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 4,
                'baslik': 'Öğrenilmiş Derslerin Gözden Geçirilmesi',
                'faaliyet_tanimi': '4. Öğrenilmiş Dersler gözden geçirilir.',
                'sorumlular': 'Proje Sorumlusu, İlgili Bölümler',
                'ilgili_dokumanlar': 'Öğrenilmiş Dersler Formu',
                'faz': 'FAZ1',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 5,
                'baslik': 'Etki Analizlerinin Yapılması ve FMEA Güncelleme',
                'faaliyet_tanimi': '5. Değişikliğin maliyet, kalite, teslimat, proses, iş güvenliği ve müşteri açısından etkileri belirlenir. FMEA yapılır veya mevcut FMEA güncellenir.',
                'sorumlular': 'Proje Sorumlusu, Kalite Kontrol Sorumlusu',
                'ilgili_dokumanlar': 'KLG-EK-004 Hata Türü ve Etkileri Analiz Formu (FMEA)',
                'faz': 'FAZ1',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 6,
                'baslik': 'Hammadde / Bileşen Kontrolü ve Tedarikçi Araştırması',
                'faaliyet_tanimi': '6. Teknik spesifikasyonlarda belirtilen hammadde ve bileşenlerde değişiklik olup olmadığı kontrol edilir; değişiklik mevcutsa, yeni tedarikçi araştırılması ve fiyat çalışması için gerekli bilgiler satınalma birimine iletilir.',
                'sorumlular': 'Proje Sorumlusu',
                'ilgili_dokumanlar': 'Excel BOM List, Erp Sistemi, E-mail',
                'faz': 'FAZ1',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 7,
                'baslik': 'Mevcut Stok & Lot Etki Analizi',
                'faaliyet_tanimi': '7. Mevcut stokların değişiklikten etkilenip etkilenmeyeceği analiz edilir. Eski stokların kullanılıp kullanılmayacağı planlama veya proje tarafından müşteriye sorulur.',
                'sorumlular': 'Satış-Analiz Sorumlusu, Fabrika Müdürü, Proje Sorumlusu',
                'ilgili_dokumanlar': 'PMG-TL-002 Yeni Ürün Devreye Alma ve Mühendislik Değişiklikleri Talimatı',
                'faz': 'FAZ1',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 8,
                'baslik': 'Eski Stokların Kullanımına İlişkin Müşteri Kararı ve Bilgilendirme',
                'faaliyet_tanimi': '8. Müşterinin onayı ve yönlendirmesi doğrultusunda eski lot/stokların kullanımına ilişkin müşteri kararı, ilgili birimlere bilgilendirme mailiyle iletilir.',
                'sorumlular': 'Proje Sorumlusu, Planlama Sorumlusu',
                'ilgili_dokumanlar': 'E-mail',
                'faz': 'FAZ1',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 9,
                'baslik': 'Teknik Analiz Detayları ve Revizyon Teklifi Paylaşımı',
                'faaliyet_tanimi': '9. Teknik analiz detayları hazırlanarak Satış Analiz Sorumlusu ve Fabrika müdürüne iletilir. Revizyon teklifi termin süresiyle birlikte müşteri ile paylaşılır.',
                'sorumlular': 'Satış-Analiz Sorumlusu, Fabrika Müdürü, Proje Sorumlusu',
                'ilgili_dokumanlar': 'Müşteri Portalı, Teknik Dokümanlar, E-mail',
                'faz': 'FAZ1',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 10,
                'baslik': 'Müşteri Fiyat ve Zaman Planı Onayı',
                'faaliyet_tanimi': '10. Müşteriden değişikliğin başlaması için gerekli fiyat onayı ve zaman planı uygunluğuna dair onay alındıktan sonra değişiklik başlatılır.',
                'sorumlular': 'Satış-Analiz Sorumlusu, Fabrika Müdürü, Proje Sorumlusu',
                'ilgili_dokumanlar': 'Müşteri Portalı, Teknik Dokümanlar, E-mail',
                'faz': 'FAZ1',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 11,
                'baslik': 'Yeni Ürün Devreye Alma Süreci Kapsam Değerlendirmesi',
                'faaliyet_tanimi': '11. Talep edilen Mühendislik değişikliği, yeni ürün devreye alma süreci olarak değerlendirilecek kapsamda mıdır?',
                'sorumlular': 'Fabrika Müdürü, Proje Sorumlusu',
                'ilgili_dokumanlar': '-',
                'faz': 'FAZ1',
                'karar_adimi_mi': True,
            },
            {
                'adim_no': 12,
                'baslik': 'Nihai Verilerin İncelenmesi, Paylaşımı ve Şahit Numune Kaydı',
                'faaliyet_tanimi': '12. Proje sorumlusu revizyon sürecinde nihai verileri inceler ve ilgili birimlerle paylaşır. Numunelerin geçerliliği müşteri ile teyit edilir; gerekli durumlarda alınan yeni şahit numune etiketlenerek kayıt altına alınır, eski numuneler ise prosedüre uygun şekilde imha edilir veya hurdaya ayrılır.',
                'sorumlular': 'Proje Sorumlusu',
                'ilgili_dokumanlar': 'E-mail',
                'faz': 'FAZ2',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 13,
                'baslik': 'Geçici Ürün Ağaçlarının (BOM) Hazırlanması',
                'faaliyet_tanimi': '13. Geçici ürün ağaçları (BOM) hazırlanır.',
                'sorumlular': 'Proje Sorumlusu',
                'ilgili_dokumanlar': 'Erp Sistemi',
                'faz': 'FAZ2',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 14,
                'baslik': 'Proses Akış Şemasının Revizyonu',
                'faaliyet_tanimi': '14. Proses akış şeması gözden geçirilir ve gerekirse revize edilir.',
                'sorumlular': 'Proje Sorumlusu, Üretim Sorumlusu, Kalite Sorumlusu',
                'ilgili_dokumanlar': 'İş-Akış Şeması, KLT-EK-056 / ÜRK-EK-003',
                'faz': 'FAZ2',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 15,
                'baslik': 'Kontrol Planının Gözden Geçirilmesi ve Revizyonu',
                'faaliyet_tanimi': '15. Kontrol Planı gözden geçirilir ve gerekirse revize edilir.',
                'sorumlular': 'Proje Sorumlusu, Kalite Sorumlusu',
                'ilgili_dokumanlar': 'Erp Sistemi / MES, KLG-EK-031 Kalite Kontrol Planı',
                'faz': 'FAZ2',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 16,
                'baslik': 'Numune Üretim Talebi ve Belgelerin Hazırlanması',
                'faaliyet_tanimi': '16. Numune üretimi için gerekli bilgi ve belgeler hazırlanır, ilgili birimlere iletilir ve numune üretim talebi açılır.',
                'sorumlular': 'Proje Sorumlusu',
                'ilgili_dokumanlar': 'Teknik Dokümanlar, E-mail, PMK-EK-001 - PMP-EK-001 Numune bildirim formu',
                'faz': 'FAZ2',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 17,
                'baslik': 'Final Hammadde Spesifikasyonları ve Tedarik İhtiyaç Bildirimi',
                'faaliyet_tanimi': '17. Yeni bir hammadde kullanımı varsa, final hammadde spesifikasyonları hazırlanır ve tedarik planlama, satın alma ile kalite/giriş kalite kontrol sorumlularına iletilir; gerekirse ön seri üretim için hammadde ve bileşen ihtiyaçları da satın alma veya tedarik planlama birimine bildirilir.',
                'sorumlular': 'Proje Sorumlusu, İlgili Bölümler',
                'ilgili_dokumanlar': 'NETSIS / G-Star / Solidwords / E-mail / PDF / Müşteri Teknik Dokümanları',
                'faz': 'FAZ2',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 18,
                'baslik': 'Hammadde Temini ve Numune Üretiminin Gerçekleştirilmesi',
                'faaliyet_tanimi': '18. Numune üretimi için tedarik edilen hammaddelerin üretime ulaşması sağlanır, numune üretimi gerçekleştirilir ve süreci takip edilir.',
                'sorumlular': 'Proje Sorumlusu, Üretim Sorumlusu, Hammadde Sorumlusu',
                'ilgili_dokumanlar': 'Erp Sistemi, Çizim Programı, Malzeme Teknik Bilgi Listeleri, PMK-EK-001 - PMP-EK-001 Numune bildirim formu / PMG-EK-009 Numune Takip Formu, Sevk Talimatları',
                'faz': 'FAZ2',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 19,
                'baslik': 'Numune Kalite Kontrol ve Ölçüm Çalışmaları',
                'faaliyet_tanimi': '19. Üretilen numunelerin kalite kontrol ölçümlerinin yapılması sağlanır.',
                'sorumlular': 'Kalite Sorumlusu',
                'ilgili_dokumanlar': 'PMG-EK-001 ISIR Formu (Initial Sample Inspection Report)',
                'faz': 'FAZ3',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 20,
                'baslik': 'Numune ISIR Ölçüm Uygunluk Kontrolü',
                'faaliyet_tanimi': '20. Üretilen numunelerin ölçüm sonuçları müşteri talep ve şartnamelerine uygun mu?',
                'sorumlular': 'Kalite Sorumlusu',
                'ilgili_dokumanlar': 'PMG-EK-001 ISIR Formu (Initial Sample Inspection Report)',
                'faz': 'FAZ3',
                'karar_adimi_mi': True,
            },
            {
                'adim_no': 21,
                'baslik': 'Onaylı Numunenin Müşteriye Sevkiyatı ve Kanıt Kaydı',
                'faaliyet_tanimi': '21. Kontrolleri tamamlanmış ve onaylanmış numune, gerekli belgelerle birlikte müşteriye sevk edilir. Sevk öncesi numunenin fotoğrafı çekilir ve kanıt dokümanı olarak saklanır. Talebi yapan müşteri yetkilisi bilgilendirilir.',
                'sorumlular': 'Proje Sorumlusu',
                'ilgili_dokumanlar': 'E-mail, Erp Sistemi',
                'faz': 'FAZ3',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 22,
                'baslik': 'Müşteri Numune Onayı',
                'faaliyet_tanimi': '22. Müşteri, sevk edilen numuneyi onayladı mı?',
                'sorumlular': 'Proje Sorumlusu',
                'ilgili_dokumanlar': 'Müşteri Portalı, Teknik Dokümanlar, E-mail',
                'faz': 'FAZ3',
                'karar_adimi_mi': True,
            },
            {
                'adim_no': 23,
                'baslik': 'Müşteri Ön Seri Üretim Talebi Değerlendirmesi',
                'faaliyet_tanimi': '23. Müşterinin yapılan revizyona ilişkin ön seri üretim talebi var mı?',
                'sorumlular': 'Üretim Planlama Sorumlusu, Proje Sorumlusu',
                'ilgili_dokumanlar': 'Müşteri Portalı, E-mail',
                'faz': 'FAZ3',
                'karar_adimi_mi': True,
            },
            {
                'adim_no': 24,
                'baslik': 'Ön Seri Üretim Planlama ve İş Emri Açılması',
                'faaliyet_tanimi': '24. Ön seri üretim talebi Planlama Sorumlusu veya Proje Sorumlusuna müşteri tarafından bildirilir; ön seri üretim planlanır, iş emri oluşturulur ve ön seri üretim gerçekleştirilir.',
                'sorumlular': 'Üretim Planlama Sorumlusu, Proje Sorumlusu',
                'ilgili_dokumanlar': 'Müşteri Portalı, E-mail',
                'faz': 'FAZ3',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 25,
                'baslik': 'Makine ve Proses Yeterlilik Analizleri (CMK/CPK)',
                'faaliyet_tanimi': '25. Müşteri talebine göre proses ve/veya makine yeterlilik çalışmaları (CMK/CPK) yapılır.',
                'sorumlular': 'Kalite Sorumlusu',
                'ilgili_dokumanlar': 'KLG-EK-002 Makine / Proses Yeterlilik Analizi Talimatı',
                'faz': 'FAZ3',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 26,
                'baslik': 'Ön Seri Çıkış Kalite Kontrol Raporu Hazırlanması',
                'faaliyet_tanimi': '26. Ön seri üretim ürünlerinin kalite kontrol ve ölçümleri yapılır, Çıkış Kalite Kontrol Raporu hazırlanır.',
                'sorumlular': 'Kalite Sorumlusu',
                'ilgili_dokumanlar': 'KLG-EK-014 Çıkış Kalite Kontrol Raporu',
                'faz': 'FAZ3',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 27,
                'baslik': 'Müşteri Ön Seri Üretim Onayı',
                'faaliyet_tanimi': '27. Gönderilen ön seri üretim sonrası müşteri onayı verildi mi?',
                'sorumlular': 'Proje Sorumlusu',
                'ilgili_dokumanlar': 'E-mail, Müşteri Portalı',
                'faz': 'FAZ3',
                'karar_adimi_mi': True,
            },
            {
                'adim_no': 28,
                'baslik': 'Mamul Stok Kodu ve Seri Ürün Ağacı (BOM) Oluşturma',
                'faaliyet_tanimi': '28. Numune stok kodu ile oluşturulan geçici ürün ağaçları kontrol edilir ve mamul stok kodu ile yeniden oluşturulur. Numune aşamasında yapılan değişiklikler varsa, ürün ağacındaki bu değişiklikler Satış Analiz Sorumlusu ve/veya Fabrika Müdürüne bildirilir.',
                'sorumlular': 'Proje Sorumlusu',
                'ilgili_dokumanlar': 'Erp Sistemi, E-mail',
                'faz': 'FAZ4',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 29,
                'baslik': 'Teknik Resim & Dokümanların Dağıtımı ve Arşivleme',
                'faaliyet_tanimi': '29. Güncellenen teknik resim/dokümanlar yayımlanır; eski versiyonlar sistemden kaldırılır.',
                'sorumlular': 'Proje Sorumlusu',
                'ilgili_dokumanlar': 'E-mail, Bölüm Ortak Klasörleri, PMG-EK-004 Teknik Doküman Dağıtım Çizelgesi (Sadece Kondenser Bölümü)',
                'faz': 'FAZ4',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 30,
                'baslik': 'Ambalajlama ve İstifleme Talimatı Revizyonu',
                'faaliyet_tanimi': '30. Ambalajlama talimatı kontrol edilir ve gerekirse revize edilir.',
                'sorumlular': 'Proje Sorumlusu',
                'ilgili_dokumanlar': 'Erp Sistemi, İstifleme Sevk Talimatları, E-mail',
                'faz': 'FAZ4',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 31,
                'baslik': 'Şahit Numune Alınması ve Eski Numunelerin İmhası',
                'faaliyet_tanimi': '31. Müşteri, şahit numune sağlıyorsa, numune alınır ve kanıt olarak saklanır. Eski numuneler, ilgili talimata uygun olarak imha edilir veya kullanımdan kaldırılır.',
                'sorumlular': 'Proje Sorumlusu, Kalite Sorumlusu',
                'ilgili_dokumanlar': 'Şahit Numune Listesi, PMG-TL-002 Yeni Ürün Devreye Alma ve Mühendislik Değişiklikleri Talimatı',
                'faz': 'FAZ4',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 32,
                'baslik': 'Seri Üretim Siparişi Alımı ve Seri Üretime Geçiş',
                'faaliyet_tanimi': '32. Müşteriden alınan onay dokümanları, ilgili ürün klasörüne veya numune onay klasörüne kaydedilir. Onaylanan ürüne ilişkin müşteriden seri üretim siparişi alındıktan sonra seri üretime geçiş tamamlanır.',
                'sorumlular': 'Proje Sorumlusu',
                'ilgili_dokumanlar': 'Bölüm İlgili Klasörleri, Erp Sistemi / İş Emri',
                'faz': 'FAZ4',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 33,
                'baslik': 'Süreç İyileştirme, Dijitalleşme ve Öğrenilmiş Dersler',
                'faaliyet_tanimi': '33. Süreç ve sonuçlar düzenli olarak gözden geçirilir ve iyileştirilir, dijital ortama taşınır; edinilen bilgi ve deneyim paylaşılır.',
                'sorumlular': 'Proje Sorumlusu, Satış Analiz Sorumlusu',
                'ilgili_dokumanlar': 'PMG-EK-002 Yeni Ürün Üretilebilirlik Analiz Formu, Öğrenilmiş Dersler Formu',
                'faz': 'FAZ4',
                'karar_adimi_mi': False,
            },
            {
                'adim_no': 34,
                'baslik': 'Seri Üretim Reçete Kontrolü ve Süreç Kapanışı',
                'faaliyet_tanimi': '34. Seri üretim sonrası ürün reçetesi kontrol edilir; değişiklik tespit edilirse Satış Analiz Sorumlusu ve/veya Fabrika Müdürüne bildirilir.',
                'sorumlular': 'Proje Sorumlusu',
                'ilgili_dokumanlar': 'Erp Sistemi, E-mail',
                'faz': 'FAZ4',
                'karar_adimi_mi': False,
            },
        ]

        # 1. Master Adımları Yükle
        for veri in adilar_verisi:
            adim, created = MuhendislikDegisikligiAdimTanimi.objects.update_or_create(
                adim_no=veri['adim_no'],
                defaults=veri
            )

        self.stdout.write(self.style.SUCCESS("Mühendislik Değişikliği Süreci 34 Master Adımı Başarıyla Güncellendi!"))

        # 2. Demo Projeleri Oluştur
        demo_projeler = [
            {
                'kod': 'ECO-2026-001',
                'ad': 'BSH Buzdolabı Kondenser Boru Çapı & Büküm Yarıçapı Revizyonu',
                'musteri_adi': 'BSH Bosch Hausgeräte GmbH',
                'parca_kodu': 'KND-BSH-8820',
                'revizyon_no': 'Rev.02',
                'degisiklik_nedeni': 'MUSTERI_TALEBI',
                'urun_grubu': 'Kondenser & Sogutucu',
                'ilgili_fabrika': 'Teleset 1 (Manisa)',
                'durum': 'DEVAM_EDIYOR',
                'guncel_adim_no': 6,
                'hedef_tamamlanma_tarihi': (timezone.now() + timedelta(days=45)).date(),
                'aciklama': 'Müşteri Ar-Ge talebi doğrultusunda kondenser boru büküm yarıçapı R12 -> R10 olarak revize edilmektedir.',
            },
            {
                'kod': 'ECO-2026-002',
                'ad': 'Beko Çamaşır Makinesi Inox Ön Panel Sac Kalınlığı Optimizasyonu (VAVE)',
                'musteri_adi': 'Beko Europe B.V.',
                'parca_kodu': 'PNL-BK-409',
                'revizyon_no': 'Rev.03',
                'degisiklik_nedeni': 'MALIYET_IYILESTIRME',
                'urun_grubu': 'Metal Parca & Sac',
                'ilgili_fabrika': 'Teleset 2 (Çerkezköy)',
                'durum': 'REVIZYONDA',
                'guncel_adim_no': 20,
                'hedef_tamamlanma_tarihi': (timezone.now() + timedelta(days=60)).date(),
                'aciklama': 'Yıllık hammadde tasarrufu amacıyla 0.80mm sac kalınlığı 0.70mm yüksek mukavemetli sac ile ikame edilmektedir.',
            },
            {
                'kod': 'ECO-2026-003',
                'ad': 'Whirlpool Kurutucu Kablo Demeti Soket & Klemens Değişikliği',
                'musteri_adi': 'Whirlpool Corporation',
                'parca_kodu': 'KBL-WP-1044',
                'revizyon_no': 'Rev.01',
                'degisiklik_nedeni': 'HAMMADDE_TEDARIK',
                'urun_grubu': 'Kablo Gruplari',
                'ilgili_fabrika': 'Teleset 1 (Manisa)',
                'durum': 'BASARIYLA_TAMAMLANDI',
                'guncel_adim_no': 34,
                'hedef_tamamlanma_tarihi': timezone.now().date(),
                'aciklama': 'Tedarikçi klemens termin sıkıntısı nedeniyle alternatif onaylı soket parça koduna geçiş başarıyla tamamlanmıştır.',
            }
        ]

        for p_data in demo_projeler:
            musteri_karti = MusteriKarti.objects.filter(kisa_ad__icontains=p_data['musteri_adi'].split()[0]).first()
            p_data['musteri_karti'] = musteri_karti

            surec, created = MuhendislikDegisikligiSureci.objects.get_or_create(
                kod=p_data['kod'],
                defaults=p_data
            )

            if created:
                # 34 adımı oluştur
                adımlar = MuhendislikDegisikligiAdimTanimi.objects.all().order_by('adim_no')
                for a in adımlar:
                    if a.adim_no < surec.guncel_adim_no:
                        durum = 'TAMAMLANDI'
                        karar = 'Onaylandı'
                    elif a.adim_no == surec.guncel_adim_no:
                        durum = 'DEVAM_EDIYOR'
                        karar = None
                    else:
                        durum = 'BEKLIYOR'
                        karar = None

                    if surec.kod == 'ECO-2026-003':
                        durum = 'TAMAMLANDI'
                        karar = 'Onaylandı'

                    MuhendislikDegisikligiAdimKaydi.objects.create(
                        surec=surec,
                        adim=a,
                        durum=durum,
                        karar_sonucu=karar,
                        tamamlayan='Buse Nur Baltacıoğlu' if durum == 'TAMAMLANDI' else None,
                        tamamlanma_tarihi=timezone.now() if durum == 'TAMAMLANDI' else None,
                        notlar='Otomatik demo oluşturuldu.' if durum == 'TAMAMLANDI' else ''
                    )

                MuhendislikDegisikligiGecmisLog.objects.create(
                    surec=surec,
                    islem=f"Mühendislik Değişikliği Başlatıldı: {surec.kod}",
                    detay=f"{surec.ad} konulu değişiklik talebi sisteme tanımlandı.",
                    yapan='Buse Nur Baltacıoğlu'
                )

        self.stdout.write(self.style.SUCCESS("Mühendislik Değişikliği Süreci 34 Adımı ve Demo Verileri Başarıyla Yüklendi!"))
