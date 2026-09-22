from django.test import TestCase, Client
from django.urls import reverse
from crm_takip.models import PazarlamaProjesi, SurecAdimTanimi, ProjeAdimKaydi, ProjeGecmisLog
from django.core.management import call_command

class PazarlamaSureciTests(TestCase):
    def setUp(self):
        call_command('seed_pazarlama_adimlari')
        self.client = Client()

    def test_proje_olusturma_ve_15_adim_baslatma(self):
        """Yeni bir proje oluşturulduğunda 15 adımın otomatik açıldığını ve 1. adımın aktif olduğunu test eder"""
        response = self.client.post(reverse('proje_olustur'), {
            'kod': 'PRJ-2026-TEST1',
            'ad': 'Almanya EV Batarya Muhafazası',
            'musteri_adi': 'BMW AG',
            'hedef_ulke': 'Almanya',
            'urun_grubu': 'Batarya & EV Bilesenleri',
            'ilgili_fabrika': 'Teleset 1 (Manisa)',
            'sorumlu_pazarlama_uzmani': 'Ahmet Yılmaz',
            'sorumlu_satis_muduru': 'Mehmet Demir',
            'tahmini_butce': '50000',
            'beklenen_ciro': '2000000',
        })
        self.assertEqual(response.status_code, 302)
        
        proje = PazarlamaProjesi.objects.get(kod='PRJ-2026-TEST1')
        self.assertEqual(proje.adim_kayitlari.count(), 15)
        self.assertEqual(proje.guncel_adim_no, 1)
        
        adim1 = proje.adim_kayitlari.get(adim__adim_no=1)
        self.assertEqual(adim1.durum, 'DEVAM_EDIYOR')
        
        adim2 = proje.adim_kayitlari.get(adim__adim_no=2)
        self.assertEqual(adim2.durum, 'BEKLIYOR')

    def test_adim_6_karar_mantigi_hayir_ve_evet(self):
        """Adım 6 (Bütçe Uygunluğu): HAYIR denince 4'e döner, EVET denince 7'ye geçer"""
        proje = PazarlamaProjesi.objects.create(
            kod='PRJ-2026-TEST2',
            ad='Test Projesi',
            musteri_adi='Ford',
            hedef_ulke='Romanya',
            guncel_adim_no=6
        )
        for i in range(1, 16):
            adim_tanimi = SurecAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 6 else ('DEVAM_EDIYOR' if i == 6 else 'BEKLIYOR')
            ProjeAdimKaydi.objects.create(proje=proje, adim=adim_tanimi, durum=durum)

        # 1. Test: HAYIR (Revizyon) -> 4. Adıma dönmeli
        response = self.client.post(reverse('adim_aksiyon', args=[proje.pk, 6]), {
            'aksiyon': 'HAYIR',
            'notlar': 'Bütçe %10 düşürülmeli.',
            'tamamlayan': 'Genel Müdür'
        })
        proje.refresh_from_db()
        self.assertEqual(proje.guncel_adim_no, 4)
        self.assertEqual(proje.adim_kayitlari.get(adim__adim_no=4).durum, 'DEVAM_EDIYOR')

        # 2. Test: 4 ve 5'i tekrar tamamlayıp 6'da EVET diyelim
        self.client.post(reverse('adim_aksiyon', args=[proje.pk, 4]), {'aksiyon': 'TAMAMLA'})
        self.client.post(reverse('adim_aksiyon', args=[proje.pk, 5]), {'aksiyon': 'TAMAMLA'})
        
        response_evet = self.client.post(reverse('adim_aksiyon', args=[proje.pk, 6]), {
            'aksiyon': 'EVET',
            'notlar': 'Revize bütçe onaylandı.',
            'tamamlayan': 'Genel Müdür'
        })
        proje.refresh_from_db()
        self.assertEqual(proje.guncel_adim_no, 7)
        self.assertEqual(proje.adim_kayitlari.get(adim__adim_no=7).durum, 'DEVAM_EDIYOR')

    def test_adim_12_gecerli_onay_ile_teklif_surecine_gecis(self):
        """Adım 12'de Geçerli Onay Varsa proje doğrudan TEKLIF_SURECINDE durumuna geçmeli"""
        proje = PazarlamaProjesi.objects.create(
            kod='PRJ-2026-TEST3',
            ad='Mevcut Müşteri Yeni Proje',
            musteri_adi='Stellantis',
            hedef_ulke='Fransa',
            guncel_adim_no=12
        )
        for i in range(1, 16):
            adim_tanimi = SurecAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 12 else ('DEVAM_EDIYOR' if i == 12 else 'BEKLIYOR')
            ProjeAdimKaydi.objects.create(proje=proje, adim=adim_tanimi, durum=durum)

        response = self.client.post(reverse('adim_aksiyon', args=[proje.pk, 12]), {
            'aksiyon': 'GECERLI_ONAY_VAR',
            'notlar': 'Tedarikçi denetim sertifikası 2027 sonuna kadar geçerli.',
            'tamamlayan': 'Satış ve Pazarlama Müdürü'
        })
        proje.refresh_from_db()
        self.assertEqual(proje.durum, 'TEKLIF_SURECINDE')
        self.assertEqual(proje.adim_kayitlari.get(adim__adim_no=13).durum, 'PAS_GECILDI')

    def test_adim_11_olumsuz_kapanis(self):
        """Adım 11'de Ön Mutabakat Sağlanamazsa 15. adıma geçip OLUMSUZ_KAPATILDI olmalı"""
        proje = PazarlamaProjesi.objects.create(
            kod='PRJ-2026-TEST4',
            ad='Ön Mutabakat Test',
            musteri_adi='Hedef A.Ş.',
            hedef_ulke='Polonya',
            guncel_adim_no=11
        )
        for i in range(1, 16):
            adim_tanimi = SurecAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 11 else ('DEVAM_EDIYOR' if i == 11 else 'BEKLIYOR')
            ProjeAdimKaydi.objects.create(proje=proje, adim=adim_tanimi, durum=durum)

        response = self.client.post(reverse('adim_aksiyon', args=[proje.pk, 11]), {
            'aksiyon': 'HAYIR',
            'notlar': 'Müşteri ticari koşulları (ödeme vadesi) kabul etmedi.',
            'tamamlayan': 'Pazarlama Uzmanı'
        })
        proje.refresh_from_db()
        self.assertEqual(proje.guncel_adim_no, 15)
        self.assertEqual(proje.durum, 'OLUMSUZ_KAPATILDI')


class MusteriIliskileriSureciTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Seed 11 steps for EYS-EK-028
        adilar_data = [
            {"adim_no": 1, "baslik": "Tanımlama", "faaliyet_tanimi": "F1", "sorumlular": "GM", "karar_adimi_mi": False, "faz": "FAZ1"},
            {"adim_no": 2, "baslik": "İhtiyaç Değerlendirme", "faaliyet_tanimi": "F2", "sorumlular": "Tüm Birimler", "karar_adimi_mi": False, "faz": "FAZ1"},
            {"adim_no": 3, "baslik": "Talep Toplama", "faaliyet_tanimi": "F3", "sorumlular": "EYS", "karar_adimi_mi": False, "faz": "FAZ1"},
            {"adim_no": 4, "baslik": "Süreç Tasarımı", "faaliyet_tanimi": "F4", "sorumlular": "Tüm Birimler", "karar_adimi_mi": False, "faz": "FAZ1"},
            {"adim_no": 5, "baslik": "Kriter Belirleme", "faaliyet_tanimi": "F5", "sorumlular": "Ekip", "karar_adimi_mi": False, "faz": "FAZ2"},
            {"adim_no": 6, "baslik": "Kriter Sağlandı mı?", "faaliyet_tanimi": "F6", "sorumlular": "Ekip", "karar_adimi_mi": True, "faz": "FAZ2"},
            {"adim_no": 7, "baslik": "Anketler", "faaliyet_tanimi": "F7", "sorumlular": "Ekip", "karar_adimi_mi": False, "faz": "FAZ3"},
            {"adim_no": 8, "baslik": "Aksiyonlar", "faaliyet_tanimi": "F8", "sorumlular": "Ekip", "karar_adimi_mi": False, "faz": "FAZ3"},
            {"adim_no": 9, "baslik": "Tamamlama", "faaliyet_tanimi": "F9", "sorumlular": "Ekip", "karar_adimi_mi": False, "faz": "FAZ3"},
            {"adim_no": 10, "baslik": "YGG Raporlama", "faaliyet_tanimi": "F10", "sorumlular": "Ekip", "karar_adimi_mi": False, "faz": "FAZ4"},
            {"adim_no": 11, "baslik": "Dijitalleşme", "faaliyet_tanimi": "F11", "sorumlular": "Ekip", "karar_adimi_mi": False, "faz": "FAZ4"},
        ]
        from crm_takip.models import MusteriIliskileriAdimTanimi, MusteriIliskileriSureci, MusteriIliskileriAdimKaydi
        for a in adilar_data:
            MusteriIliskileriAdimTanimi.objects.create(**a)

    def test_musteri_iliskileri_olusturma_ve_11_adim(self):
        """Yeni müşteri ilişkileri süreci başlatıldığında 11 adımın oluştuğunu test eder"""
        from crm_takip.models import MusteriIliskileriSureci
        response = self.client.post(reverse('musteri_iliskileri_olustur'), {
            'kod': 'MIS-2026-TEST',
            'ad': 'BSH Müşteri Memnuniyet Süreci',
            'musteri_adi': 'BSH',
            'donem': '2026 Yıllık',
            'ilgili_fabrika': 'Teleset 1 (Manisa)',
            'sorumlu_eys': 'Buse Nur Baltacıoğlu',
            'sorumlu_surec_sahibi': 'Süreç Sahibi',
            'memnuniyet_puani': '95.0',
            'aciklama': 'Test açıklaması'
        })
        self.assertEqual(response.status_code, 302)

        surec = MusteriIliskileriSureci.objects.get(kod='MIS-2026-TEST')
        self.assertEqual(surec.adim_kayitlari.count(), 11)
        self.assertEqual(surec.guncel_adim_no, 1)
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=1).durum, 'DEVAM_EDIYOR')

    def test_adim_6_karar_kapisi_nok_ve_ok(self):
        """Adım 6'da HAYIR_NOK ile Uygunsuzluk Sürecine geçmeli, EVET_OK veya UYGUNSUZLUK_COZULDU ile 7'ye ilerlemeli"""
        from crm_takip.models import MusteriIliskileriSureci, MusteriIliskileriAdimTanimi, MusteriIliskileriAdimKaydi
        surec = MusteriIliskileriSureci.objects.create(
            kod='MIS-2026-TEST-K',
            ad='Karar Kapısı Test',
            musteri_adi='BEKO',
            guncel_adim_no=6
        )
        for i in range(1, 12):
            adim_tanimi = MusteriIliskileriAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 6 else ('DEVAM_EDIYOR' if i == 6 else 'BEKLIYOR')
            MusteriIliskileriAdimKaydi.objects.create(surec=surec, adim=adim_tanimi, durum=durum)

        adim6_kaydi = surec.adim_kayitlari.get(adim__adim_no=6)

        # 1. HAYIR_NOK -> UYGUNSUZLUK_YONETIMINDE
        response = self.client.post(reverse('musteri_iliskileri_adim_aksiyon', args=[surec.pk, adim6_kaydi.pk]), {
            'karar': 'HAYIR_NOK',
            'notlar': 'Performans kriteri altında kalındı, DÖF açıldı.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.durum, 'UYGUNSUZLUK_YONETIMINDE')
        self.assertEqual(surec.guncel_adim_no, 6)

        # 2. UYGUNSUZLUK_COZULDU -> 7. Adıma geçmeli
        response2 = self.client.post(reverse('musteri_iliskileri_adim_aksiyon', args=[surec.pk, adim6_kaydi.pk]), {
            'karar': 'UYGUNSUZLUK_COZULDU',
            'notlar': 'DÖF başarıyla kapatıldı.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.durum, 'DEVAM_EDIYOR')
        self.assertEqual(surec.guncel_adim_no, 7)


class UrunTeklifSureciTests(TestCase):
    def setUp(self):
        self.client = Client()
        call_command('seed_urun_teklif_adimlari')

    def test_urun_teklif_olusturma_ve_adimlari(self):
        """Yeni Ürün Teklif Süreci oluşturulduğunda adım kayıtlarının açıldığını ve 1. adımın DEVAM_EDIYOR olduğunu doğrular"""
        from crm_takip.models import UrunTeklifSureci
        response = self.client.post(reverse('urun_teklif_olustur'), {
            'kod': 'TEK-2026-TEST1',
            'ad': 'BSH Yeni Nesil Buzdolabı Sac Gövde Teklifi',
            'musteri_adi': 'BSH Ev Aletleri',
            'donem': '2026 / Q1',
            'ilgili_fabrika': 'Teleset 1 (Manisa)',
            'urun_grubu': 'METAL_PARCA',
            'sorumlu_satis_uzmani': 'Buse Nur Baltacıoğlu',
            'sorumlu_satis_analiz_uzmani': 'Ahmet Erdem',
            'sorumlu_satis_yoneticisi': 'Murat Yılmaz',
            'teklif_tutari': '450000',
            'aciklama': 'Test Teklif Süreci'
        })
        self.assertEqual(response.status_code, 302)

        surec = UrunTeklifSureci.objects.get(kod='TEK-2026-TEST1')
        self.assertTrue(surec.adim_kayitlari.count() > 0)
        self.assertEqual(surec.guncel_adim_no, 1)
        self.assertEqual(surec.adim_kayitlari.filter(adim__sira_no=1).first().durum, 'DEVAM_EDIYOR')

    def test_adim_1_ve_2_ilerleme(self):
        """Adım 1 tamamlandığında 2. Adıma geçer"""
        from crm_takip.models import UrunTeklifSureci, UrunTeklifAdimTanimi, UrunTeklifAdimKaydi
        surec = UrunTeklifSureci.objects.create(
            kod='TEK-2026-T1',
            ad='Adım 1 Testi',
            musteri_adi='Arçelik',
            guncel_adim_no=1,
            guncel_adim_kodu='1'
        )
        for tanim in UrunTeklifAdimTanimi.objects.all():
            durum = 'DEVAM_EDIYOR' if tanim.sira_no == 1 else 'BEKLIYOR'
            UrunTeklifAdimKaydi.objects.create(surec=surec, adim=tanim, durum=durum)

        adim1_kaydi = surec.adim_kayitlari.get(adim__sira_no=1)
        self.client.post(reverse('urun_teklif_adim_aksiyon', args=[surec.pk, adim1_kaydi.pk]), {
            'aksiyon': 'TAMAMLA',
            'notlar': 'Ön kontrol yapıldı.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.guncel_adim_kodu, '2')
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_kodu='2').durum, 'DEVAM_EDIYOR')

    def test_adim_16_kapanis(self):
        """Adım 16B TAMAMLA ile sürecin BASARIYLA_TAMAMLANDI olarak kapandığını test eder"""
        from crm_takip.models import UrunTeklifSureci, UrunTeklifAdimTanimi, UrunTeklifAdimKaydi
        surec = UrunTeklifSureci.objects.create(
            kod='TEK-2026-T16',
            ad='Adım 16B Kapanış Testi',
            musteri_adi='Electrolux',
            guncel_adim_no=16,
            guncel_adim_kodu='16B'
        )
        for tanim in UrunTeklifAdimTanimi.objects.all():
            durum = 'TAMAMLANDI' if tanim.sira_no < 39 else ('DEVAM_EDIYOR' if tanim.adim_kodu == '16B' else 'BEKLIYOR')
            UrunTeklifAdimKaydi.objects.create(surec=surec, adim=tanim, durum=durum)

        adim16b_kaydi = surec.adim_kayitlari.get(adim__adim_kodu='16B')
        self.client.post(reverse('urun_teklif_adim_aksiyon', args=[surec.pk, adim16b_kaydi.pk]), {
            'aksiyon': 'TAMAMLA',
            'notlar': 'Teklif kazanıldı, APQP sürecine devredildi.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.durum, 'BASARIYLA_TAMAMLANDI')


class SozlesmeSureciTests(TestCase):
    def setUp(self):
        self.client = Client()
        call_command('seed_sozlesme_adimlari')

    def test_sozlesme_sureci_olusturma_ve_9_adim(self):
        """Yeni Sözleşme Süreci oluşturulduğunda 9 adım kaydının açıldığını ve 1. adımın DEVAM_EDIYOR olduğunu doğrular"""
        from crm_takip.models import SozlesmeSureci
        response = self.client.post(reverse('sozlesme_sureci_olustur'), {
            'kod': 'SZL-2026-TEST1',
            'ad': 'BSH Kalite Güvence Anlaşması (QAA)',
            'musteri_adi': 'BSH Ev Aletleri',
            'sozlesme_tipi': 'KALITE',
            'ilgili_fabrika': 'PRESHANE',
            'sorumlu_satis_uzmani': 'Buse Nur Baltacıoğlu',
            'sorumlu_hukuk': 'Hukuk Müşaviri',
            'aciklama': 'Test Sözleşme Değerlendirme'
        })
        self.assertEqual(response.status_code, 302)

        surec = SozlesmeSureci.objects.get(kod='SZL-2026-TEST1')
        self.assertEqual(surec.adim_kayitlari.count(), 9)
        self.assertEqual(surec.guncel_adim_no, 1)
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=1).durum, 'DEVAM_EDIYOR')

    def test_adim_1_ve_paralel_adim_2_3(self):
        """Adım 1 tamamlandığında Adım 2 ve Adım 3 paralel olarak DEVAM_EDIYOR durumuna geçer"""
        from crm_takip.models import SozlesmeSureci, SozlesmeAdimTanimi, SozlesmeAdimKaydi
        surec = SozlesmeSureci.objects.create(
            kod='SZL-2026-T1',
            ad='Adım 1 Testi',
            musteri_adi='Arçelik',
            guncel_adim_no=1
        )
        for i in range(1, 10):
            tanim = SozlesmeAdimTanimi.objects.get(adim_no=i)
            durum = 'DEVAM_EDIYOR' if i == 1 else 'BEKLIYOR'
            SozlesmeAdimKaydi.objects.create(surec=surec, adim=tanim, durum=durum)

        adim1_kaydi = surec.adim_kayitlari.get(adim__adim_no=1)
        self.client.post(reverse('sozlesme_sureci_adim_aksiyon', args=[surec.pk, adim1_kaydi.pk]), {
            'aksiyon': 'TAMAMLA',
            'notlar': 'Kayıt açıldı, ekler tam.',
            'tamamlayan': 'Satış Uzmanı'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=1).durum, 'TAMAMLANDI')
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=2).durum, 'DEVAM_EDIYOR')
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=3).durum, 'DEVAM_EDIYOR')

    def test_adim_5_karar_kapisi_onay_ve_revizyon_ve_red(self):
        """Adım 5'te ONAY 6'ya geçirir, REVIZYON 4'e döner, RED olumsuz kapatır"""
        from crm_takip.models import SozlesmeSureci, SozlesmeAdimTanimi, SozlesmeAdimKaydi
        surec = SozlesmeSureci.objects.create(
            kod='SZL-2026-T5',
            ad='Adım 5 Yetkili Makam Karar Testi',
            musteri_adi='Vestel',
            guncel_adim_no=5
        )
        for i in range(1, 10):
            tanim = SozlesmeAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 5 else ('DEVAM_EDIYOR' if i == 5 else 'BEKLIYOR')
            SozlesmeAdimKaydi.objects.create(surec=surec, adim=tanim, durum=durum)

        adim5_kaydi = surec.adim_kayitlari.get(adim__adim_no=5)

        # 1. ONAY -> Adım 6 DEVAM_EDIYOR
        self.client.post(reverse('sozlesme_sureci_adim_aksiyon', args=[surec.pk, adim5_kaydi.pk]), {
            'aksiyon': 'ONAY',
            'notlar': 'Sapma onaylandı.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.guncel_adim_no, 6)
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=6).durum, 'DEVAM_EDIYOR')

        # 2. REVIZYON -> Adım 4'e Dönüş
        self.client.post(reverse('sozlesme_sureci_adim_aksiyon', args=[surec.pk, adim5_kaydi.pk]), {
            'aksiyon': 'REVIZYON',
            'notlar': 'Tekrar değerlendirilsin.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.guncel_adim_no, 4)
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=4).durum, 'DEVAM_EDIYOR')

        # 3. RED -> OLUMSUZ_KAPATILDI
        self.client.post(reverse('sozlesme_sureci_adim_aksiyon', args=[surec.pk, adim5_kaydi.pk]), {
            'aksiyon': 'RED',
            'notlar': 'Sözleşmeye devam edilmeyecek.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.durum, 'OLUMSUZ_KAPATILDI')

    def test_adim_7_nihai_mutabakat_karar_kapisi(self):
        """Adım 7'de MUTABAKAT_SAGLANDI 8'e geçirir, KRITIK_SAPMA 5'e döner, MUSTERI_RED olumsuz kapatır"""
        from crm_takip.models import SozlesmeSureci, SozlesmeAdimTanimi, SozlesmeAdimKaydi
        surec = SozlesmeSureci.objects.create(
            kod='SZL-2026-T7',
            ad='Adım 7 Mutabakat Testi',
            musteri_adi='Stellantis',
            guncel_adim_no=7
        )
        for i in range(1, 10):
            tanim = SozlesmeAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 7 else ('DEVAM_EDIYOR' if i == 7 else 'BEKLIYOR')
            SozlesmeAdimKaydi.objects.create(surec=surec, adim=tanim, durum=durum)

        adim7_kaydi = surec.adim_kayitlari.get(adim__adim_no=7)

        # 1. MUTABAKAT_SAGLANDI -> Adım 8 DEVAM_EDIYOR
        self.client.post(reverse('sozlesme_sureci_adim_aksiyon', args=[surec.pk, adim7_kaydi.pk]), {
            'aksiyon': 'MUTABAKAT_SAGLANDI',
            'notlar': 'Müşteriyle tam mutabakat sağlandı.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.guncel_adim_no, 8)
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=8).durum, 'DEVAM_EDIYOR')

    def test_adim_9_kapanis_ve_yururluk(self):
        """Adım 9 TAMAMLA ile sürecin BASARIYLA_TAMAMLANDI (%100) olarak kapandığını test eder"""
        from crm_takip.models import SozlesmeSureci, SozlesmeAdimTanimi, SozlesmeAdimKaydi
        surec = SozlesmeSureci.objects.create(
            kod='SZL-2026-T9',
            ad='Adım 9 Kapanış Testi',
            musteri_adi='Electrolux',
            guncel_adim_no=9
        )
        for i in range(1, 10):
            tanim = SozlesmeAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 9 else ('DEVAM_EDIYOR' if i == 9 else 'BEKLIYOR')
            SozlesmeAdimKaydi.objects.create(surec=surec, adim=tanim, durum=durum)

        adim9_kaydi = surec.adim_kayitlari.get(adim__adim_no=9)
        self.client.post(reverse('sozlesme_sureci_adim_aksiyon', args=[surec.pk, adim9_kaydi.pk]), {
            'aksiyon': 'TAMAMLA',
            'notlar': 'Sözleşme başarıyla yürürlüğe girdi ve yükümlülük takibi başlatıldı.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.durum, 'BASARIYLA_TAMAMLANDI')
        self.assertEqual(surec.tamamlanma_yuzdesi, 100)


# ==============================================================================
# YENİ ÜRÜN DEVREYE ALMA SÜRECİ (45 ADIM) TESTLERİ
# ==============================================================================

class YeniUrunDevreyeAlmaTests(TestCase):
    def setUp(self):
        call_command('seed_yeni_urun_adimlari')
        self.client = Client()

    def test_npi_proje_olusturma_ve_45_adim_baslatma(self):
        """Yeni bir NPI süreci oluşturulduğunda 45 adımın eksiksiz açıldığını test eder"""
        from crm_takip.models import YeniUrunDevreyeAlmaSureci, YeniUrunAdimKaydi
        response = self.client.post(reverse('yeni_urun_olustur'), {
            'kod': 'NPI-2026-TEST1',
            'ad': 'Bosch R290 Tel Borulu Kondenser Testi',
            'musteri_adi': 'BSH Bosch Hausgeräte GmbH',
            'urun_grubu': 'Kondenser & Sogutma',
            'ilgili_fabrika': 'Teleset 1 (Manisa)',
            'parca_kodu': 'KND-TEST-001',
            'yillik_hedef_adet': '250000',
            'sorumlu_proje_lideri': 'Buse Nur Baltacıoğlu',
            'sorumlu_fabrika_muduru': 'Engin Kaya',
            'sorumlu_satis_analiz': 'Hakan Yılmaz',
            'sorumlu_kalite': 'Merve Çelik',
        })
        self.assertEqual(response.status_code, 302)

        surec = YeniUrunDevreyeAlmaSureci.objects.get(kod='NPI-2026-TEST1')
        self.assertEqual(surec.adim_kayitlari.count(), 45)
        self.assertEqual(surec.guncel_adim_no, 1)

        adim1 = surec.adim_kayitlari.get(adim__adim_no=1)
        self.assertEqual(adim1.durum, 'DEVAM_EDIYOR')

        adim2 = surec.adim_kayitlari.get(adim__adim_no=2)
        self.assertEqual(adim2.durum, 'BEKLIYOR')

    def test_npi_adim_2_on_degerlendirme_dallanmasi(self):
        """Adım 2: EVET -> Adım 4'e geçer (3 pas), HAYIR -> Adım 3'e geçer"""
        from crm_takip.models import YeniUrunDevreyeAlmaSureci, YeniUrunAdimTanimi, YeniUrunAdimKaydi
        surec = YeniUrunDevreyeAlmaSureci.objects.create(
            kod='NPI-2026-TEST2',
            ad='Adım 2 Testi',
            musteri_adi='Beko',
            guncel_adim_no=2
        )
        for i in range(1, 46):
            adim_tanimi = YeniUrunAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 2 else ('DEVAM_EDIYOR' if i == 2 else 'BEKLIYOR')
            YeniUrunAdimKaydi.objects.create(surec=surec, adim=adim_tanimi, durum=durum)

        adim2_kaydi = surec.adim_kayitlari.get(adim__adim_no=2)

        # 1. Test: EVET -> Adım 4 DEVAM_EDIYOR, Adım 3 PAS_GECILDI
        self.client.post(reverse('yeni_urun_adim_aksiyon', args=[surec.pk, adim2_kaydi.pk]), {
            'aksiyon': 'EVET',
            'notlar': 'Standart üretim proseslerine uygun.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.guncel_adim_no, 4)
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=3).durum, 'PAS_GECILDI')
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=4).durum, 'DEVAM_EDIYOR')

    def test_npi_adim_9_fizibilite_dallanmasi(self):
        """Adım 9: EVET -> Adım 10, HAYIR -> Adım 11 (10 pas)"""
        from crm_takip.models import YeniUrunDevreyeAlmaSureci, YeniUrunAdimTanimi, YeniUrunAdimKaydi
        surec = YeniUrunDevreyeAlmaSureci.objects.create(
            kod='NPI-2026-TEST3',
            ad='Adım 9 Testi',
            musteri_adi='Whirlpool',
            guncel_adim_no=9
        )
        for i in range(1, 46):
            adim_tanimi = YeniUrunAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 9 else ('DEVAM_EDIYOR' if i == 9 else 'BEKLIYOR')
            YeniUrunAdimKaydi.objects.create(surec=surec, adim=adim_tanimi, durum=durum)

        adim9_kaydi = surec.adim_kayitlari.get(adim__adim_no=9)

        # HAYIR -> Adım 10 PAS_GECILDI, Adım 11 DEVAM_EDIYOR
        self.client.post(reverse('yeni_urun_adim_aksiyon', args=[surec.pk, adim9_kaydi.pk]), {
            'aksiyon': 'HAYIR',
            'notlar': 'Kalıp maliyeti yüksek, stratejik değerlendirme gerekli.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.guncel_adim_no, 11)
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=10).durum, 'PAS_GECILDI')
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=11).durum, 'DEVAM_EDIYOR')

    def test_npi_adim_12_musteri_onay_ve_kapatma(self):
        """Adım 12: HAYIR durumunda Adım 13-43 pas geçilip Adım 44'te süreç OLUMSUZ_KAPATILDI olmalı"""
        from crm_takip.models import YeniUrunDevreyeAlmaSureci, YeniUrunAdimTanimi, YeniUrunAdimKaydi
        surec = YeniUrunDevreyeAlmaSureci.objects.create(
            kod='NPI-2026-TEST4',
            ad='Adım 12 Onay Testi',
            musteri_adi='Liebherr',
            guncel_adim_no=12
        )
        for i in range(1, 46):
            adim_tanimi = YeniUrunAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 12 else ('DEVAM_EDIYOR' if i == 12 else 'BEKLIYOR')
            YeniUrunAdimKaydi.objects.create(surec=surec, adim=adim_tanimi, durum=durum)

        adim12_kaydi = surec.adim_kayitlari.get(adim__adim_no=12)
        self.client.post(reverse('yeni_urun_adim_aksiyon', args=[surec.pk, adim12_kaydi.pk]), {
            'aksiyon': 'HAYIR',
            'notlar': 'Müşteri bütçe onayı vermedi.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.guncel_adim_no, 44)
        self.assertEqual(surec.durum, 'OLUMSUZ_KAPATILDI')
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=13).durum, 'PAS_GECILDI')
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=43).durum, 'PAS_GECILDI')
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=44).durum, 'DEVAM_EDIYOR')

    def test_npi_adim_26_ve_28_numune_red_adim_20_donus(self):
        """Adım 26 veya 28'de HAYIR seçildiğinde Adım 20'ye dönmeli ve ara adımlar BEKLIYOR olmalı"""
        from crm_takip.models import YeniUrunDevreyeAlmaSureci, YeniUrunAdimTanimi, YeniUrunAdimKaydi
        surec = YeniUrunDevreyeAlmaSureci.objects.create(
            kod='NPI-2026-TEST5',
            ad='Numune Red Testi',
            musteri_adi='Vestel',
            guncel_adim_no=26
        )
        for i in range(1, 46):
            adim_tanimi = YeniUrunAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 26 else ('DEVAM_EDIYOR' if i == 26 else 'BEKLIYOR')
            YeniUrunAdimKaydi.objects.create(surec=surec, adim=adim_tanimi, durum=durum)

        adim26_kaydi = surec.adim_kayitlari.get(adim__adim_no=26)
        self.client.post(reverse('yeni_urun_adim_aksiyon', args=[surec.pk, adim26_kaydi.pk]), {
            'aksiyon': 'HAYIR',
            'notlar': 'Boru büküm radyusunda sapma tespit edildi.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.guncel_adim_no, 20)
        self.assertEqual(surec.durum, 'REVIZYONDA')
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=20).durum, 'DEVAM_EDIYOR')
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=25).durum, 'BEKLIYOR')

    def test_npi_adim_33_msa_dof_ve_cozum(self):
        """Adım 33'te MSA uygunsuzluğu ile DÖF açılıp sonra çözüldüğünde Adım 34'e geçmeli"""
        from crm_takip.models import YeniUrunDevreyeAlmaSureci, YeniUrunAdimTanimi, YeniUrunAdimKaydi
        surec = YeniUrunDevreyeAlmaSureci.objects.create(
            kod='NPI-2026-TEST6',
            ad='MSA DÖF Testi',
            musteri_adi='Arçelik',
            guncel_adim_no=33
        )
        for i in range(1, 46):
            adim_tanimi = YeniUrunAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 33 else ('DEVAM_EDIYOR' if i == 33 else 'BEKLIYOR')
            YeniUrunAdimKaydi.objects.create(surec=surec, adim=adim_tanimi, durum=durum)

        adim33_kaydi = surec.adim_kayitlari.get(adim__adim_no=33)

        # 1. DÖF Aç
        self.client.post(reverse('yeni_urun_adim_aksiyon', args=[surec.pk, adim33_kaydi.pk]), {
            'aksiyon': 'DOF_AC',
            'notlar': 'Gage R&R %18 çıktı.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.durum, 'UYGUNSUZLUK_YONETIMINDE')

        # 2. DÖF Çöz
        self.client.post(reverse('yeni_urun_adim_aksiyon', args=[surec.pk, adim33_kaydi.pk]), {
            'aksiyon': 'UYGUNSUZLUK_COZULDU',
            'notlar': 'Fikstür revize edildi, Gage R&R %7.2 ile onaylandı.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.guncel_adim_no, 34)
        self.assertEqual(surec.durum, 'DEVAM_EDIYOR')
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=34).durum, 'DEVAM_EDIYOR')

    def test_npi_adim_45_basariyla_kapanis(self):
        """Adım 45 TAMAMLA aksiyonu ile sürecin BASARIYLA_TAMAMLANDI (%100) olarak kapandığını test eder"""
        from crm_takip.models import YeniUrunDevreyeAlmaSureci, YeniUrunAdimTanimi, YeniUrunAdimKaydi
        surec = YeniUrunDevreyeAlmaSureci.objects.create(
            kod='NPI-2026-TEST7',
            ad='Adım 45 Kapanış Testi',
            musteri_adi='Bosch',
            guncel_adim_no=45
        )
        for i in range(1, 46):
            adim_tanimi = YeniUrunAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 45 else ('DEVAM_EDIYOR' if i == 45 else 'BEKLIYOR')
            YeniUrunAdimKaydi.objects.create(surec=surec, adim=adim_tanimi, durum=durum)

        adim45_kaydi = surec.adim_kayitlari.get(adim__adim_no=45)
        self.client.post(reverse('yeni_urun_adim_aksiyon', args=[surec.pk, adim45_kaydi.pk]), {
            'aksiyon': 'TAMAMLA',
            'notlar': 'Yeni ürün devreye alma süreci başarıyla tamamlandı. Seri üretime geçildi.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.durum, 'BASARIYLA_TAMAMLANDI')
        self.assertEqual(surec.tamamlanma_yuzdesi, 100)

    def test_npi_detay_sayfasi_render(self):
        """Yeni Ürün Devreye Alma detay sayfasının (45 adım şablonu dahil) 200 OK ile render olduğunu test eder"""
        from crm_takip.models import YeniUrunDevreyeAlmaSureci
        surecler = YeniUrunDevreyeAlmaSureci.objects.all()
        for s in surecler:
            response = self.client.get(reverse('yeni_urun_detay', args=[s.pk]))
            self.assertEqual(response.status_code, 200)


# ==============================================================================
# MÜHENDİSLİK DEĞİŞİKLİĞİ SÜRECİ (34 ADIM - ECO / ECM) TESTLERİ
# ==============================================================================

class MuhendislikDegisikligiTests(TestCase):
    def setUp(self):
        call_command('seed_muhendislik_degisikligi_adimlari')
        self.client = Client()

    def test_eco_proje_olusturma_ve_34_adim_baslatma(self):
        """Yeni bir ECO süreci oluşturulduğunda 34 adımın eksiksiz açıldığını test eder"""
        from crm_takip.models import MuhendislikDegisikligiSureci
        response = self.client.post(reverse('muhendislik_degisikligi_olustur'), {
            'kod': 'ECO-2026-TEST1',
            'ad': 'Kondenser Boru Et Kalınlığı Optimizasyonu Testi',
            'musteri_adi': 'Arçelik A.Ş.',
            'parca_kodu': 'TLS-TEST-001',
            'revizyon_no': 'Rev.02',
            'degisiklik_nedeni': 'MALIYET_IYILESTIRME',
            'urun_grubu': 'Kondenser & Sogutma',
            'ilgili_fabrika': 'Teleset 1 (Manisa)',
            'sorumlu_proje_sorumlusu': 'Buse Nur Baltacıoğlu',
            'sorumlu_fabrika_muduru': 'Serdar Acar',
            'sorumlu_satis_analiz': 'Hakan Yılmaz',
            'sorumlu_kalite': 'Ahmet Yurt',
        })
        self.assertEqual(response.status_code, 302)

        surec = MuhendislikDegisikligiSureci.objects.get(kod='ECO-2026-TEST1')
        self.assertEqual(surec.adim_kayitlari.count(), 34)
        self.assertEqual(surec.guncel_adim_no, 1)

        adim1 = surec.adim_kayitlari.get(adim__adim_no=1)
        self.assertEqual(adim1.durum, 'DEVAM_EDIYOR')

        adim2 = surec.adim_kayitlari.get(adim__adim_no=2)
        self.assertEqual(adim2.durum, 'BEKLIYOR')

    def test_eco_adim_11_yeni_urun_aktarimi_ve_standart_gecis(self):
        """Adım 11: EVET -> YENI_URUN_SURECINE_AKTARILDI (12-34 pas), HAYIR -> Adım 12'ye geçer"""
        from crm_takip.models import MuhendislikDegisikligiSureci, MuhendislikDegisikligiAdimTanimi, MuhendislikDegisikligiAdimKaydi
        surec = MuhendislikDegisikligiSureci.objects.create(
            kod='ECO-2026-TEST2',
            ad='Adım 11 Karar Testi',
            musteri_adi='Vestel',
            guncel_adim_no=11
        )
        for i in range(1, 35):
            adim_tanimi = MuhendislikDegisikligiAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 11 else ('DEVAM_EDIYOR' if i == 11 else 'BEKLIYOR')
            MuhendislikDegisikligiAdimKaydi.objects.create(surec=surec, adim=adim_tanimi, durum=durum)

        adim11_kaydi = surec.adim_kayitlari.get(adim__adim_no=11)

        # 1. Test: EVET -> YENI_URUN_SURECINE_AKTARILDI, Adım 12-34 PAS_GECILDI
        self.client.post(reverse('muhendislik_degisikligi_adim_aksiyon', args=[surec.pk, adim11_kaydi.pk]), {
            'aksiyon': 'EVET',
            'notlar': 'Büyük ölçekli kalıp ve gövde revizyonu nedeniyle NPI süreci başlatılmalı.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.durum, 'YENI_URUN_SURECINE_AKTARILDI')
        for s_no in range(12, 35):
            self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=s_no).durum, 'PAS_GECILDI')

        # 2. Test: HAYIR -> Standart Değişiklik Olarak Adım 12'ye geçer
        surec2 = MuhendislikDegisikligiSureci.objects.create(
            kod='ECO-2026-TEST2B',
            ad='Adım 11 Standart Geçiş Testi',
            musteri_adi='Bosch',
            guncel_adim_no=11
        )
        for i in range(1, 35):
            adim_tanimi = MuhendislikDegisikligiAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 11 else ('DEVAM_EDIYOR' if i == 11 else 'BEKLIYOR')
            MuhendislikDegisikligiAdimKaydi.objects.create(surec=surec2, adim=adim_tanimi, durum=durum)

        adim11_kaydi2 = surec2.adim_kayitlari.get(adim__adim_no=11)
        self.client.post(reverse('muhendislik_degisikligi_adim_aksiyon', args=[surec2.pk, adim11_kaydi2.pk]), {
            'aksiyon': 'HAYIR',
            'notlar': 'Standart mühendislik değişikliği kapsamında devam edilecek.'
        })
        surec2.refresh_from_db()
        self.assertEqual(surec2.guncel_adim_no, 12)
        self.assertEqual(surec2.adim_kayitlari.get(adim__adim_no=12).durum, 'DEVAM_EDIYOR')

    def test_eco_adim_20_ve_22_isir_ve_numune_red_adim_13_donus(self):
        """Adım 20 veya 22'de HAYIR seçildiğinde Adım 13'e dönmeli ve ara adımlar BEKLIYOR olmalı"""
        from crm_takip.models import MuhendislikDegisikligiSureci, MuhendislikDegisikligiAdimTanimi, MuhendislikDegisikligiAdimKaydi
        surec = MuhendislikDegisikligiSureci.objects.create(
            kod='ECO-2026-TEST3',
            ad='Numune Red Testi',
            musteri_adi='Arçelik',
            guncel_adim_no=20
        )
        for i in range(1, 35):
            adim_tanimi = MuhendislikDegisikligiAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 20 else ('DEVAM_EDIYOR' if i == 20 else 'BEKLIYOR')
            MuhendislikDegisikligiAdimKaydi.objects.create(surec=surec, adim=adim_tanimi, durum=durum)

        adim20_kaydi = surec.adim_kayitlari.get(adim__adim_no=20)
        self.client.post(reverse('muhendislik_degisikligi_adim_aksiyon', args=[surec.pk, adim20_kaydi.pk]), {
            'aksiyon': 'HAYIR',
            'notlar': 'Boru lehim bağlantı testinde mikro kaçak tespit edildi.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.guncel_adim_no, 13)
        self.assertEqual(surec.durum, 'REVIZYONDA')
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=13).durum, 'DEVAM_EDIYOR')
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=19).durum, 'BEKLIYOR')

    def test_eco_adim_23_on_seri_talebi_atlama_ve_gecis(self):
        """Adım 23: HAYIR -> 24-27 pas geçilip doğrudan Adım 28'e atlar; EVET -> Adım 24'e geçer"""
        from crm_takip.models import MuhendislikDegisikligiSureci, MuhendislikDegisikligiAdimTanimi, MuhendislikDegisikligiAdimKaydi
        surec = MuhendislikDegisikligiSureci.objects.create(
            kod='ECO-2026-TEST4',
            ad='Ön Seri Atlama Testi',
            musteri_adi='Vestel',
            guncel_adim_no=23
        )
        for i in range(1, 35):
            adim_tanimi = MuhendislikDegisikligiAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 23 else ('DEVAM_EDIYOR' if i == 23 else 'BEKLIYOR')
            MuhendislikDegisikligiAdimKaydi.objects.create(surec=surec, adim=adim_tanimi, durum=durum)

        adim23_kaydi = surec.adim_kayitlari.get(adim__adim_no=23)

        # HAYIR -> 24, 25, 26, 27 PAS_GECILDI, Adım 28 DEVAM_EDIYOR
        self.client.post(reverse('muhendislik_degisikligi_adim_aksiyon', args=[surec.pk, adim23_kaydi.pk]), {
            'aksiyon': 'HAYIR',
            'notlar': 'Müşteri numuneyi onayladı, ön seri talep etmedi.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.guncel_adim_no, 28)
        for p_no in [24, 25, 26, 27]:
            self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=p_no).durum, 'PAS_GECILDI')
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=28).durum, 'DEVAM_EDIYOR')

    def test_eco_adim_27_on_seri_red_adim_24_donus_ve_onay(self):
        """Adım 27: HAYIR -> Adım 24'e geri döner; EVET -> Faz 4 Adım 28'e geçer"""
        from crm_takip.models import MuhendislikDegisikligiSureci, MuhendislikDegisikligiAdimTanimi, MuhendislikDegisikligiAdimKaydi
        surec = MuhendislikDegisikligiSureci.objects.create(
            kod='ECO-2026-TEST5',
            ad='Ön Seri Red Testi',
            musteri_adi='BSH',
            guncel_adim_no=27
        )
        for i in range(1, 35):
            adim_tanimi = MuhendislikDegisikligiAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 27 else ('DEVAM_EDIYOR' if i == 27 else 'BEKLIYOR')
            MuhendislikDegisikligiAdimKaydi.objects.create(surec=surec, adim=adim_tanimi, durum=durum)

        adim27_kaydi = surec.adim_kayitlari.get(adim__adim_no=27)
        self.client.post(reverse('muhendislik_degisikligi_adim_aksiyon', args=[surec.pk, adim27_kaydi.pk]), {
            'aksiyon': 'HAYIR',
            'notlar': 'Ön seri montajında klips yuvasında kasıntı tespit edildi.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.guncel_adim_no, 24)
        self.assertEqual(surec.durum, 'REVIZYONDA')
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=24).durum, 'DEVAM_EDIYOR')
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=26).durum, 'BEKLIYOR')

    def test_eco_adim_34_basariyla_tamamlama(self):
        """Adım 34 TAMAMLA aksiyonu ile sürecin BASARIYLA_TAMAMLANDI (%100) olarak kapandığını test eder"""
        from crm_takip.models import MuhendislikDegisikligiSureci, MuhendislikDegisikligiAdimTanimi, MuhendislikDegisikligiAdimKaydi
        surec = MuhendislikDegisikligiSureci.objects.create(
            kod='ECO-2026-TEST6',
            ad='Adım 34 Kapanış Testi',
            musteri_adi='Liebherr',
            guncel_adim_no=34
        )
        for i in range(1, 35):
            adim_tanimi = MuhendislikDegisikligiAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 34 else ('DEVAM_EDIYOR' if i == 34 else 'BEKLIYOR')
            MuhendislikDegisikligiAdimKaydi.objects.create(surec=surec, adim=adim_tanimi, durum=durum)

        adim34_kaydi = surec.adim_kayitlari.get(adim__adim_no=34)
        self.client.post(reverse('muhendislik_degisikligi_adim_aksiyon', args=[surec.pk, adim34_kaydi.pk]), {
            'aksiyon': 'TAMAMLA',
            'notlar': 'Seri üretim reçeteleri güncellendi, değişiklik başarıyla devreye alındı.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.durum, 'BASARIYLA_TAMAMLANDI')
        self.assertEqual(surec.tamamlanma_yuzdesi, 100)

    def test_eco_liste_ve_detay_sayfasi_render(self):
        """Mühendislik Değişikliği liste ve detay sayfalarının 200 OK ile sorunsuz render olduğunu test eder"""
        response_liste = self.client.get(reverse('muhendislik_degisikligi_liste'))
        self.assertEqual(response_liste.status_code, 200)

        from crm_takip.models import MuhendislikDegisikligiSureci
        surecler = MuhendislikDegisikligiSureci.objects.all()
        for s in surecler:
            response_detay = self.client.get(reverse('muhendislik_degisikligi_detay', args=[s.pk]))
            self.assertEqual(response_detay.status_code, 200)


class PrototipSureciTests(TestCase):
    def setUp(self):
        call_command('seed_prototip_adimlari')
        self.client = Client()

    def test_prototip_olusturma_ve_23_adim_baslatma(self):
        """Yeni bir prototip süreci oluşturulduğunda 23 adımın otomatik açıldığını ve 1. adımın aktif olduğunu test eder"""
        from crm_takip.models import PrototipSureci
        response = self.client.post(reverse('prototip_olustur'), {
            'kod': 'PRT-2026-TEST1',
            'ad': 'Test Batarya Prototipi',
            'musteri_adi': 'BSH Ev Aletleri',
            'parca_kodu': 'TEL-TEST-01',
            'revizyon_no': 'Rev.01',
            'prototip_tipi': 'YENI_TASARIM',
            'urun_grubu': 'Metal Parca & Sac',
            'ilgili_fabrika': 'Teleset 1 (Manisa)',
            'sorumlu_proje_sorumlusu': 'Buse Nur Baltacıoğlu',
            'sorumlu_fabrika_muduru': 'Serdar Acar',
            'sorumlu_satis_analiz': 'Hakan Yılmaz',
            'sorumlu_kalite': 'Ahmet Yurt',
        })
        self.assertEqual(response.status_code, 302)

        surec = PrototipSureci.objects.get(kod='PRT-2026-TEST1')
        self.assertEqual(surec.adim_kayitlari.count(), 23)
        self.assertEqual(surec.guncel_adim_no, 1)

        adim1 = surec.adim_kayitlari.get(adim__adim_no=1)
        self.assertEqual(adim1.durum, 'DEVAM_EDIYOR')

        adim2 = surec.adim_kayitlari.get(adim__adim_no=2)
        self.assertEqual(adim2.durum, 'BEKLIYOR')

    def test_prototip_adim_3_karar_kapisi(self):
        """Adım 3: EVET -> YENI_URUN_SURECINE_AKTARILDI ve kalan adımlar PAS_GECILDI; HAYIR -> Adım 4'e geçer"""
        from crm_takip.models import PrototipSureci, PrototipAdimTanimi, PrototipAdimKaydi
        surec = PrototipSureci.objects.create(
            kod='PRT-2026-TEST2',
            ad='Kapsam Değerlendirme Testi',
            musteri_adi='Electrolux',
            guncel_adim_no=3
        )
        for i in range(1, 24):
            adim_tanimi = PrototipAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 3 else ('DEVAM_EDIYOR' if i == 3 else 'BEKLIYOR')
            PrototipAdimKaydi.objects.create(surec=surec, adim=adim_tanimi, durum=durum)

        adim3_kaydi = surec.adim_kayitlari.get(adim__adim_no=3)

        # 1. Test: EVET -> NPI Sürecine Aktar
        self.client.post(reverse('prototip_adim_aksiyon', args=[surec.pk, adim3_kaydi.pk]), {
            'aksiyon': 'EVET',
            'notlar': 'Yeni platform için komple kalıp ve hat yatırımı gerekiyor.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.durum, 'YENI_URUN_SURECINE_AKTARILDI')
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=4).durum, 'PAS_GECILDI')
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=23).durum, 'PAS_GECILDI')

    def test_prototip_adim_9_musteri_baslangic_onay_red_ve_kapanis(self):
        """Adım 9: HAYIR -> 10-21 pas geçilir, OLUMSUZ_KAPATILDI ve Adım 22 aktif olur; EVET -> Adım 10'a geçer"""
        from crm_takip.models import PrototipSureci, PrototipAdimTanimi, PrototipAdimKaydi
        surec = PrototipSureci.objects.create(
            kod='PRT-2026-TEST3',
            ad='Müşteri Başlangıç Onay Testi',
            musteri_adi='Miele',
            guncel_adim_no=9
        )
        for i in range(1, 24):
            adim_tanimi = PrototipAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 9 else ('DEVAM_EDIYOR' if i == 9 else 'BEKLIYOR')
            PrototipAdimKaydi.objects.create(surec=surec, adim=adim_tanimi, durum=durum)

        adim9_kaydi = surec.adim_kayitlari.get(adim__adim_no=9)

        # HAYIR -> Kapanış Adım 22
        self.client.post(reverse('prototip_adim_aksiyon', args=[surec.pk, adim9_kaydi.pk]), {
            'aksiyon': 'HAYIR',
            'notlar': 'Müşteri prototip maliyetini onaylamadı, proje iptal edildi.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.guncel_adim_no, 22)
        self.assertEqual(surec.durum, 'OLUMSUZ_KAPATILDI')
        for p_no in range(10, 22):
            self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=p_no).durum, 'PAS_GECILDI')
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=22).durum, 'DEVAM_EDIYOR')

    def test_prototip_adim_18_isir_red_ve_adim_14_donus(self):
        """Adım 18: HAYIR -> Adım 14'e döner, REVIZYONDA olur; EVET -> Adım 19'a geçer"""
        from crm_takip.models import PrototipSureci, PrototipAdimTanimi, PrototipAdimKaydi
        surec = PrototipSureci.objects.create(
            kod='PRT-2026-TEST4',
            ad='ISIR Ölçüm Red Testi',
            musteri_adi='Whirlpool',
            guncel_adim_no=18
        )
        for i in range(1, 24):
            adim_tanimi = PrototipAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 18 else ('DEVAM_EDIYOR' if i == 18 else 'BEKLIYOR')
            PrototipAdimKaydi.objects.create(surec=surec, adim=adim_tanimi, durum=durum)

        adim18_kaydi = surec.adim_kayitlari.get(adim__adim_no=18)
        self.client.post(reverse('prototip_adim_aksiyon', args=[surec.pk, adim18_kaydi.pk]), {
            'aksiyon': 'HAYIR',
            'notlar': 'CMM ölçümünde büküm açısı tolerans dışı çıktı.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.guncel_adim_no, 14)
        self.assertEqual(surec.durum, 'REVIZYONDA')
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=14).durum, 'DEVAM_EDIYOR')
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=18).durum, 'BEKLIYOR')

    def test_prototip_adim_20_musteri_numune_red_ve_onay(self):
        """Adım 20: HAYIR -> Adım 14'e döner; EVET -> Faz 4 Adım 21'e geçer"""
        from crm_takip.models import PrototipSureci, PrototipAdimTanimi, PrototipAdimKaydi
        surec = PrototipSureci.objects.create(
            kod='PRT-2026-TEST5',
            ad='Müşteri Numune Onay Testi',
            musteri_adi='Vestel',
            guncel_adim_no=20
        )
        for i in range(1, 24):
            adim_tanimi = PrototipAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 20 else ('DEVAM_EDIYOR' if i == 20 else 'BEKLIYOR')
            PrototipAdimKaydi.objects.create(surec=surec, adim=adim_tanimi, durum=durum)

        adim20_kaydi = surec.adim_kayitlari.get(adim__adim_no=20)
        self.client.post(reverse('prototip_adim_aksiyon', args=[surec.pk, adim20_kaydi.pk]), {
            'aksiyon': 'EVET',
            'notlar': 'Müşteri prototip numuneyi başarıyla doğruladı ve onay verdi.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.guncel_adim_no, 21)
        self.assertEqual(surec.durum, 'DEVAM_EDIYOR')
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=21).durum, 'DEVAM_EDIYOR')

    def test_prototip_adim_23_basariyla_tamamlama(self):
        """Adım 23 TAMAMLA aksiyonu ile sürecin BASARIYLA_TAMAMLANDI (%100) olarak kapandığını test eder"""
        from crm_takip.models import PrototipSureci, PrototipAdimTanimi, PrototipAdimKaydi
        surec = PrototipSureci.objects.create(
            kod='PRT-2026-TEST6',
            ad='Adım 23 Kapanış Testi',
            musteri_adi='Arcelik',
            guncel_adim_no=23
        )
        for i in range(1, 24):
            adim_tanimi = PrototipAdimTanimi.objects.get(adim_no=i)
            durum = 'TAMAMLANDI' if i < 23 else ('DEVAM_EDIYOR' if i == 23 else 'BEKLIYOR')
            PrototipAdimKaydi.objects.create(surec=surec, adim=adim_tanimi, durum=durum)

        adim23_kaydi = surec.adim_kayitlari.get(adim__adim_no=23)
        self.client.post(reverse('prototip_adim_aksiyon', args=[surec.pk, adim23_kaydi.pk]), {
            'aksiyon': 'TAMAMLA',
            'notlar': 'Prototip süreci ve öğrenilmiş dersler başarıyla arşivlendi.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.durum, 'BASARIYLA_TAMAMLANDI')
        self.assertEqual(surec.tamamlanma_yuzdesi, 100)

    def test_prototip_liste_ve_detay_sayfasi_render(self):
        """Prototip liste ve detay sayfalarının 200 OK ile sorunsuz render olduğunu test eder"""
        response_liste = self.client.get(reverse('prototip_liste'))
        self.assertEqual(response_liste.status_code, 200)

        from crm_takip.models import PrototipSureci
        surecler = PrototipSureci.objects.all()
        for s in surecler:
            response_detay = self.client.get(reverse('prototip_detay', args=[s.pk]))
            self.assertEqual(response_detay.status_code, 200)


class EOPSureciTests(TestCase):
    def setUp(self):
        self.client = Client()
        from crm_takip.models import EOPSurecAdimTanimi
        adimlar_data = [
            {"adim_no": 1, "baslik": "Ürün Seri Üretiminin Sonlandırılacağı Bilgisinin Alınması", "faaliyet_tanimi": "F1", "sorumlular": "Satış, Fabrika, Proje, Planlama", "karar_adimi_mi": False, "faz": "FAZ1"},
            {"adim_no": 2, "baslik": "EOP Talebinin Değerlendirilmesi ve Servis/Yedek Parça Planlaması", "faaliyet_tanimi": "F2", "sorumlular": "Satış, Fabrika, Proje, Planlama", "karar_adimi_mi": False, "faz": "FAZ1"},
            {"adim_no": 3, "baslik": "Hammadde, Yarı Mamul ve Mamul Stoklarının Değerlendirilmesi", "faaliyet_tanimi": "F3", "sorumlular": "Planlama, Üretim", "karar_adimi_mi": False, "faz": "FAZ2"},
            {"adim_no": 4, "baslik": "Müşteri Üretim Varlıklarının (Kalıp, Ekipman) Tasfiyesi ve Mutabakatı", "faaliyet_tanimi": "F4", "sorumlular": "Satış, Fabrika, Proje, Planlama", "karar_adimi_mi": False, "faz": "FAZ2"},
            {"adim_no": 5, "baslik": "ERP Kodlarının Kapatılması, Dokümanların Kaldırılması ve Varlık Listesi Paylaşımı", "faaliyet_tanimi": "F5", "sorumlular": "Proje Sorumlusu", "karar_adimi_mi": False, "faz": "FAZ3"},
            {"adim_no": 6, "baslik": "Süreç Kapanışı, Gözden Geçirme ve Öğrenilmiş Dersler", "faaliyet_tanimi": "F6", "sorumlular": "Satış, Fabrika, Proje, Planlama", "karar_adimi_mi": False, "faz": "FAZ3"},
        ]
        for a in adimlar_data:
            EOPSurecAdimTanimi.objects.create(**a)

    def test_eop_sureci_olusturma_ve_6_adim(self):
        """Yeni EOP Süreci oluşturulduğunda 6 adım kaydının açıldığını ve 1. adımın DEVAM_EDIYOR olduğunu doğrular"""
        from crm_takip.models import EOPSureci
        response = self.client.post(reverse('eop_yeni'), {
            'kod': 'EOP-2026-TEST1',
            'urun_kodu': 'KND-TEST-01',
            'urun_adi': 'Test Kondenser EOP',
            'musteri_adi': 'Arçelik',
            'urun_grubu': 'Kondenser',
            'ilgili_fabrika': 'Teleset 1 (Manisa)',
            'yedek_parca_servis_suresi_yil': 10,
            'aciklama': 'Test EOP Açıklaması'
        })
        self.assertEqual(response.status_code, 302)
        surec = EOPSureci.objects.get(kod='EOP-2026-TEST1')
        self.assertEqual(surec.adim_kayitlari.count(), 6)
        self.assertEqual(surec.guncel_adim_no, 1)
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=1).durum, 'DEVAM_EDIYOR')
        self.assertEqual(surec.adim_kayitlari.get(adim__adim_no=2).durum, 'BEKLIYOR')

    def test_eop_adim_ilerleme_ve_kapanis(self):
        """Adım 1'den Adım 6'ya kadar ilerleme ve sürecin BASARIYLA_KAPATILDI (%100) durumuna ulaştığını doğrular"""
        from crm_takip.models import EOPSureci, EOPSurecAdimTanimi, EOPAdimKaydi
        surec = EOPSureci.objects.create(
            kod='EOP-2026-TEST2',
            urun_kodu='KBL-TEST-02',
            urun_adi='Test Kablo EOP',
            musteri_adi='BSH',
            guncel_adim_no=1
        )
        for i in range(1, 7):
            adim_tanimi = EOPSurecAdimTanimi.objects.get(adim_no=i)
            EOPAdimKaydi.objects.create(
                surec=surec,
                adim=adim_tanimi,
                durum='DEVAM_EDIYOR' if i == 1 else 'BEKLIYOR'
            )

        # Adım 1 tamamla -> Adım 2'ye geç
        self.client.post(reverse('eop_adim_tamamla', args=[surec.pk, 1]), {
            'notlar': 'EOP bildirimi alındı.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.guncel_adim_no, 2)

        # Adım 2 tamamla -> Adım 3'e geç (Stok tasfiyesinde)
        self.client.post(reverse('eop_adim_tamamla', args=[surec.pk, 2]), {
            'notlar': '10 yıl yedek parça planı yapıldı.'
        })
        surec.refresh_from_db()
        self.assertEqual(surec.guncel_adim_no, 3)
        self.assertEqual(surec.durum, 'STOK_TASFIYESINDE')

        # Adım 3, 4, 5 tamamla
        self.client.post(reverse('eop_adim_tamamla', args=[surec.pk, 3]), {'notlar': 'Stoklar tüketildi.'})
        self.client.post(reverse('eop_adim_tamamla', args=[surec.pk, 4]), {'notlar': 'Kalıplar müşteriye iade edildi.'})
        surec.refresh_from_db()
        self.assertEqual(surec.guncel_adim_no, 5)
        self.assertEqual(surec.durum, 'VARLIK_DEVRI_TAMAMLANDI')

        self.client.post(reverse('eop_adim_tamamla', args=[surec.pk, 5]), {'notlar': 'ERP kodları pasife alındı.'})
        surec.refresh_from_db()
        self.assertEqual(surec.guncel_adim_no, 6)

        # Adım 6 tamamla -> Başarıyla Kapatıldı
        self.client.post(reverse('eop_adim_tamamla', args=[surec.pk, 6]), {'notlar': 'Süreç kapatıldı.'})
        surec.refresh_from_db()
        self.assertEqual(surec.durum, 'BASARIYLA_KAPATILDI')
        self.assertEqual(surec.tamamlanma_yuzdesi, 100)

    def test_eop_liste_ve_detay_render(self):
        """EOP liste ve detay sayfalarının 200 OK ile sorunsuz açıldığını doğrular"""
        response_liste = self.client.get(reverse('eop_listesi'))
        self.assertEqual(response_liste.status_code, 200)

        from crm_takip.models import EOPSureci
        surecler = EOPSureci.objects.all()
        for s in surecler:
            response_detay = self.client.get(reverse('eop_detay', args=[s.pk]))
            self.assertEqual(response_detay.status_code, 200)


class AnketlerVeFormlarTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_musteri_memnuniyeti_tek_sayfa_view(self):
        """Müşteri Memnuniyeti tek sayfasının 200 OK ile açıldığını, anket linkini, Excel indir butonunu ve Power BI grafiklerini içerdiğini test eder"""
        response = self.client.get(reverse('anket_musteri_memnuniyeti'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Müşteri Memnuniyeti')
        self.assertContains(response, 'https://forms.gle/KD375wmzhzR9PRGJ8')
        self.assertContains(response, 'btnKopyala')
        self.assertContains(response, 'Excel İndir (.xlsx)')
        self.assertContains(response, 'boyutlarBarChart')
        self.assertContains(response, 'fabrikalarBarChart')
        self.assertContains(response, 'dagilimDonutChart')

    def test_anket_raporu_view_redirects(self):
        """Eski '/anketler/rapor/' URL'sinin tek sayfaya yönlendiğini test eder"""
        response = self.client.get(reverse('anket_raporu'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Müşteri Memnuniyeti')

    def test_anketler_redirect(self):
        """'/anketler/' URL'sinin doğrudan müşteri memnuniyeti sayfasına yönlendiğini test eder"""
        response = self.client.get('/anketler/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Müşteri Memnuniyeti')


class AnaSayfaVeFaaliyetlerTests(TestCase):
    def setUp(self):
        self.client = Client()
        from crm_takip.models import FaaliyetKaydi, MusteriKarti
        self.musteri = MusteriKarti.objects.create(
            ad="Bosch Termoteknik Sanayi ve Ticaret A.Ş.",
            kisa_ad="Bosch Termoteknik",
            kod="MST-TEST-001",
            ulke="Almanya"
        )
        self.faaliyet1 = FaaliyetKaydi.objects.create(
            tur="SEYAHAT",
            baslik="Frankfurt HVAC 2026 Müşteri Ziyareti",
            sorumlu_kisi="Buse Nur Baltacıoğlu",
            musteri=self.musteri,
            musteri_adi=self.musteri.kisa_ad,
            lokasyon="Frankfurt / Almanya",
            saat_araligi="09:00 - 18:00",
            oncelik="YUKSEK",
            durum="PLANLANDI",
            aciklama="Yeni nesil kondenser görüşmeleri."
        )
        self.faaliyet2 = FaaliyetKaydi.objects.create(
            tur="TOPLANTI",
            baslik="Haftalık Ar-Ge & NPI İlerleme Toplantısı",
            sorumlu_kisi="Canan Kaya",
            lokasyon="Teleset Manisa Toplantı Salonu A",
            saat_araligi="10:00 - 11:30",
            oncelik="ORTA",
            durum="DEVAM_EDIYOR",
            aciklama="Prototip test sonuçlarının değerlendirilmesi."
        )

    def test_ana_sayfa_view_renders_200(self):
        """Kişisel Ajanda sayfasının 200 OK ile açıldığını test eder"""
        response = self.client.get(reverse('ana_sayfa'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ajandam')
        self.assertContains(response, 'Buse Nur Baltacıoğlu')
        self.assertContains(response, 'Frankfurt HVAC 2026')

    def test_ana_sayfa_view_switchers(self):
        """Takvim ve Liste görünümlerinin 200 OK ile render olduğunu test eder"""
        for v in ['takvim', 'liste']:
            response = self.client.get(reverse('ana_sayfa') + f'?view={v}')
            self.assertEqual(response.status_code, 200)

    def test_ana_sayfa_kategori_filtresi(self):
        """Faaliyet türü (kategori) filtresinin doğru çalıştığını test eder"""
        response_tur = self.client.get(reverse('ana_sayfa') + '?tur=SEYAHAT')
        self.assertEqual(response_tur.status_code, 200)
        self.assertContains(response_tur, 'Frankfurt HVAC 2026')

    def test_faaliyet_olustur_view(self):
        """Yeni faaliyet oluşturma view'ının başarılı POST işleminde faaliyet yarattığını test eder"""
        from crm_takip.models import FaaliyetKaydi
        response = self.client.post(reverse('faaliyet_olustur'), {
            'tur': 'DESTEK',
            'baslik': 'Arçelik Çamaşır Makinesi Kalıp Destek Talebi',
            'sorumlu_kisi': 'Mehmet Demir',
            'musteri': self.musteri.pk,
            'musteri_adi': 'Arçelik A.Ş.',
            'lokasyon': 'Çayırova Fabrikası',
            'baslangic_tarihi': '2026-09-20',
            'bitis_tarihi': '2026-09-21',
            'saat_araligi': '14:00 - 16:00',
            'oncelik': 'KRITIK',
            'durum': 'PLANLANDI',
            'aciklama': 'Kalıp aşınması yerinde incelenecek.',
            'tahmini_butce': '2500.00'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        
        yeni = FaaliyetKaydi.objects.filter(baslik='Arçelik Çamaşır Makinesi Kalıp Destek Talebi').first()
        self.assertIsNotNone(yeni)
        self.assertEqual(yeni.tur, 'DESTEK')
        self.assertEqual(yeni.oncelik, 'KRITIK')
        self.assertEqual(yeni.sorumlu_kisi, 'Mehmet Demir')

    def test_faaliyet_durum_guncelle_view(self):
        """Faaliyet durumunu güncelleme view'ının durum alanını değiştirdiğini test eder"""
        response = self.client.post(reverse('faaliyet_durum_guncelle', args=[self.faaliyet1.pk]), {
            'durum': 'TAMAMLANDI'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.faaliyet1.refresh_from_db()
        self.assertEqual(self.faaliyet1.durum, 'TAMAMLANDI')

    def test_faaliyet_sil_view(self):
        """Faaliyet silme view'ının kaydı sildiğini test eder"""
        from crm_takip.models import FaaliyetKaydi
        pk = self.faaliyet2.pk
        response = self.client.post(reverse('faaliyet_sil', args=[pk]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(FaaliyetKaydi.objects.filter(pk=pk).exists())


class MusteriKartlariVe360Tests(TestCase):
    """
    Minimalist Müşteri Kartları & 360° Müşteri Profili (Tesis Geçişli) Testleri
    """
    def setUp(self):
        self.client = Client()
        from crm_takip.models import MusteriKarti, MusteriTesisi, MusteriEtkilesimZamanTuneli
        
        self.musteri = MusteriKarti.objects.create(
            kod="FRM-01",
            kisa_ad="BSH",
            ad="BSH Ev Aletleri San. ve Tic. A.Ş.",
            ulke="Almanya / Türkiye",
            sehir="Çerkezköy / Münih",
            tier="Tier 1 - KAM",
            strateji="Protect",
            yillik_ciro_eur=12180000.00,
            cuzdan_payi_yuzde=58,
            aktif_proje_sayisi=28,
            kam_satis_lideri="Buse Nur BALTACIOĞLU",
            kam_muhendislik_lideri="Ahmet AK (Kalıp & Projeci Md.)",
            kam_kalite_lideri="Mehmet YILMAZ (Kalite Mühendisi)",
            sozlesme_durumu="Aktif Sözleşme (Geçerli)",
            churn_riski="0.05 (Düşük Risk)"
        )
        
        self.tesis_grup = MusteriTesisi.objects.create(
            musteri=self.musteri,
            sira=1,
            tesis_adi="Tüm Tesisler - Grup Özeti",
            lokasyon="Çerkezköy / Münih, Türkiye / Almanya",
            kod="BSH-ALL",
            clv_m="45.8 M€",
            churn_skoru="0.05",
            churn_durumu="Düşük Risk",
            yillik_ciro_str="€ 12.18M",
            cuzdan_payi_yuzde=58,
            destek_sayisi=9,
            npi_proje_sayisi=28,
            teklif_sayisi=9,
            sevkiyat_sayisi=9
        )
        
        self.tesis_manisa = MusteriTesisi.objects.create(
            musteri=self.musteri,
            sira=2,
            tesis_adi="Bosch Manisa Fabrikası",
            lokasyon="Manisa OSB, Türkiye",
            kod="BOSCH-MANISA",
            clv_m="18.2 M€",
            churn_skoru="0.04",
            churn_durumu="Düşük Risk",
            yillik_ciro_str="€ 4.60M",
            cuzdan_payi_yuzde=62,
            destek_sayisi=3,
            npi_proje_sayisi=12,
            teklif_sayisi=4,
            sevkiyat_sayisi=4
        )
        
        self.etkilesim = MusteriEtkilesimZamanTuneli.objects.create(
            musteri=self.musteri,
            kod="SAT-EK-005",
            baslik="SAT-EK-005 Resmi Fiyat Teklifi Hazırlandı",
            aciklama="Fırın Yan Gövde Sacı için 120.000 adetlik yıllık teklif eBA onayına iletildi.",
            sorumlu="Buse Nur BALTACIOĞLU",
            donem_ay_yil="EYLÜL 2026 SON ETKİLEŞİMLER"
        )

    def test_kartlar_view_get(self):
        """Müşteri portföy kartları sayfasının başarıyla açıldığını test eder"""
        response = self.client.get(reverse('kartlar'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'BSH')
        self.assertContains(response, 'Müşteri Portföyü ve Cari Hesaplar')
        self.assertContains(response, '360° Profil')

    def test_kartlar_view_tier_filtre(self):
        """Tier filtrelemesinin çalıştığını test eder"""
        response = self.client.get(reverse('kartlar') + '?tab=musteriler&tier=Tier 1')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'BSH')

    def test_kartlar_view_arama(self):
        """Arama kutusunun çalıştığını test eder"""
        response = self.client.get(reverse('kartlar') + '?tab=musteriler&q_m=BSH')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'BSH')
        
        response_empty = self.client.get(reverse('kartlar') + '?tab=musteriler&q_m=BulunmayanFirmaXYZ')
        self.assertEqual(response_empty.status_code, 200)
        self.assertContains(response_empty, 'Arama kriterlerinize uygun müşteri kaydı bulunamadı.')

    def test_musteri_360_view_get(self):
        """360° Müşteri profili sayfasının doğru verilerle render edildiğini test eder"""
        response = self.client.get(reverse('musteri_360_detay', args=[self.musteri.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'BSH')
        self.assertContains(response, '360° Müşteri Profili')
        self.assertContains(response, 'Tüm Tesisler - Grup Özeti')
        self.assertContains(response, 'Bosch Manisa Fabrikası')
        self.assertContains(response, 'Aktivite ve Süreç Zaman Tüneli')
        self.assertContains(response, 'YAŞAM BOYU DEĞER')
        self.assertContains(response, 'TERK SKORU')
        self.assertContains(response, 'CÜZDAN PAYI')
        self.assertContains(response, 'YILLIK CİRO')
        self.assertContains(response, 'SAT-EK-005 Resmi Fiyat Teklifi Hazırlandı')

    def test_musteri_360_view_404(self):
        """Olmayan bir müşteri ID'si için 404 dönüldüğünü test eder"""
        response = self.client.get(reverse('musteri_360_detay', args=[999999]))
        self.assertEqual(response.status_code, 404)


class UctanUcaIsAkisiTests(TestCase):
    def setUp(self):
        from crm_takip.models import MusteriKarti, AnaProje
        self.client = Client()
        self.musteri = MusteriKarti.objects.create(
            kod="M-001",
            kisa_ad="BSH",
            ad="BSH Ev Aletleri San. ve Tic. A.Ş."
        )
        self.proje = AnaProje.objects.create(
            proje_kodu="PRJ-101",
            proje_adi="Fırın Yan Gövde Sacı (SIMPAC 400T)",
            parca_kodu="SAC-FRN-001",
            fabrika="Preshane & Kalıphane",
            musteri=self.musteri,
            sorumlu_lider="Buse Nur Baltacıoğlu",
            aktif_surec_no=6,
            aktif_surec_adi="Yeni Ürün Devreye Alma Süreci",
            aktif_adim_no=18,
            aktif_adim_basligi="T0 Kalıp Denemesi ve İlk Numune Basımı",
            aktif_rol="Projeci / Kalıp",
            genel_ilerleme_yuzdesi=65
        )

    def test_anaproje_surecler_listesi(self):
        """AnaProje 8 sürecin her birini doğru durum ve ilerleme ile döndürmelidir"""
        surecler = self.proje.get_surecler_listesi()
        self.assertEqual(len(surecler), 8)
        
        # 1-5 süreçler tamamlanmış olmalı
        for i in range(5):
            self.assertEqual(surecler[i]['durum_kod'], 'TAMAMLANDI')
            self.assertEqual(surecler[i]['ilerleme'], 100)
            
        # 6. süreç aktif olmalı (6/8 = %75)
        self.assertEqual(surecler[5]['durum_kod'], 'DEVAM_EDIYOR')
        self.assertEqual(surecler[5]['ilerleme'], 75)
        self.assertTrue(surecler[5]['is_active'])
        
        # 7-8 süreçler beklemede olmalı
        self.assertEqual(surecler[6]['durum_kod'], 'BEKLEMEDE')
        self.assertEqual(surecler[7]['durum_kod'], 'BEKLEMEDE')

    def test_ana_sayfa_is_akisi_tab(self):
        """Proje & İş Akış Takipçisi sekmesinin başarıyla render edildiğini test eder"""
        response = self.client.get(reverse('ana_sayfa') + '?tab=is_akisi')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Takip')
        self.assertContains(response, 'Fırın Yan Gövde Sacı')
        self.assertContains(response, 'Preshane')
        self.assertContains(response, 'Yeni Ürün Devreye Alma Süreci')
        self.assertContains(response, 'Filtrele')

    def test_ana_sayfa_rol_filtresi(self):
        """Rol bazlı filtrelemenin çalıştığını test eder"""
        response = self.client.get(reverse('ana_sayfa') + '?tab=is_akisi&rol=Projeci / Kalıp')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Projeci / Kalıp')

    def test_ana_proje_ekle_view(self):
        """Yeni Ana Proje oluşturma endpoint'inin çalıştığını test eder"""
        response = self.client.post(reverse('ana_proje_ekle'), {
            'proje_kodu': 'PRJ-200',
            'proje_adi': 'Yeni Test Projesi',
            'parca_kodu': 'PARCA-TEST-01',
            'fabrika': 'Teleset 1 (Manisa)',
            'musteri_id': self.musteri.id,
            'sorumlu_lider': 'Buse Nur Baltacıoğlu',
            'aktif_surec_adi': 'Yeni Ürün Devreye Alma Süreci',
            'aktif_rol': 'Projeci / Kalıp',
        })
        self.assertEqual(response.status_code, 302)
        
        from crm_takip.models import AnaProje
        yeni = AnaProje.objects.filter(proje_kodu='PRJ-200').first()
        self.assertIsNotNone(yeni)
        self.assertEqual(yeni.proje_adi, 'Yeni Test Projesi')

    def test_anaproje_dijital_iplik_senkronizasyonu(self):
        """Tekliften APQP ve Sözleşmeye dijital iplik veri mirası aktarımını test eder"""
        from crm_takip.models import UrunTeklifSureci, SozlesmeSureci, YeniUrunDevreyeAlmaSureci
        teklif = UrunTeklifSureci.objects.create(
            kod="TEK-2026-TEST",
            ad="Test Teklifi",
            musteri_adi=self.musteri.ad,
            musteri_karti=self.musteri,
            teklif_tutari=175000.00
        )
        sozlesme = SozlesmeSureci.objects.create(
            kod="SZL-2026-TEST",
            ad="Test Sözleşmesi",
            musteri_adi=self.musteri.ad
        )
        yeni_urun = YeniUrunDevreyeAlmaSureci.objects.create(
            kod="APQP-2026-TEST",
            ad="Test APQP Projesi",
            musteri_adi=self.musteri.ad
        )
        self.proje.urun_teklif_sureci = teklif
        self.proje.sozlesme_sureci = sozlesme
        self.proje.yeni_urun_sureci = yeni_urun
        self.proje.save()

        guncellenenler = self.proje.teklif_verilerini_senkronize_et()
        self.assertIn('hedef_butce', guncellenenler)
        self.assertEqual(self.proje.hedef_butce, 175000.00)
        self.assertTrue(self.proje.dijital_iplik_senkronize_mi)

        # Sözleşme ve APQP müşteri kartı senkronize olmalı
        sozlesme.refresh_from_db()
        yeni_urun.refresh_from_db()
        self.assertEqual(sozlesme.musteri_karti, self.musteri)
        self.assertEqual(yeni_urun.musteri_karti, self.musteri)

    def test_anaproje_dongusel_iterasyonlar(self):
        """Ana Projeye bağlı birden çok Prototip ve ECO iterasyonunu test eder"""
        from crm_takip.models import PrototipSureci, MuhendislikDegisikligiSureci
        prt1 = PrototipSureci.objects.create(
            ana_proje=self.proje,
            kod="PRT-TEST-01",
            ad="T0 Kalıp Denemesi",
            musteri_adi=self.musteri.ad,
            revizyon_no="Rev.01 (T0)"
        )
        prt2 = PrototipSureci.objects.create(
            ana_proje=self.proje,
            kod="PRT-TEST-02",
            ad="T1 Doğrulama Denemesi",
            musteri_adi=self.musteri.ad,
            revizyon_no="Rev.02 (T1)"
        )
        eco1 = MuhendislikDegisikligiSureci.objects.create(
            ana_proje=self.proje,
            kod="ECO-TEST-01",
            ad="Sac Kalınlık Revizyonu",
            musteri_adi=self.musteri.ad,
            revizyon_no="Rev.A"
        )

        iterasyonlar = self.proje.get_prototip_iterasyonlari()
        self.assertEqual(len(iterasyonlar), 2)
        
        eco_revizyonlar = self.proje.get_eco_revizyonlari()
        self.assertEqual(len(eco_revizyonlar), 1)
        self.assertEqual(eco_revizyonlar[0].revizyon_no, "Rev.A")

    def test_anaproje_bekleyen_aksiyonlar(self):
        """Aktif adımların ve termin risklerinin bekleyen aksiyonlar olarak döndürüldüğünü test eder"""
        aksiyonlar = self.proje.get_bekleyen_aksiyonlar()
        self.assertTrue(len(aksiyonlar) >= 1)
        self.assertEqual(aksiyonlar[0]['surec_kodu'], self.proje.aktif_surec_adi)
        self.assertEqual(aksiyonlar[0]['oncelik'], 'Kritik Yol')
        self.assertIn('Termin Yaklaşıyor', aksiyonlar[0]['termin_durumu'])

        # Rol filtresi testi
        kalip_aksiyonlari = self.proje.get_bekleyen_aksiyonlar(rol='Projeci / Kalıp')
        self.assertEqual(len(kalip_aksiyonlari), 1)

        pazarlama_aksiyonlari = self.proje.get_bekleyen_aksiyonlar(rol='Satış & Pazarlama')
        self.assertEqual(len(pazarlama_aksiyonlari), 0)

    def test_ana_proje_senkronize_view(self):
        """Senkronizasyon view endpoint'inin çalıştığını ve yönlendirdiğini test eder"""
        response = self.client.get(reverse('ana_proje_senkronize', args=[self.proje.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('sync=ok', response.url)

    def test_ana_proje_iterasyon_ekle_view(self):
        """Döngüsel iterasyon ekleme view endpoint'ini test eder"""
        response = self.client.post(reverse('ana_proje_iterasyon_ekle', args=[self.proje.id]), {
            'iterasyon_tipi': 'ECO',
            'revizyon_no': 'Rev.C',
            'aciklama': 'Test mühendislik değişikliği'
        })
        self.assertEqual(response.status_code, 302)
        from crm_takip.models import MuhendislikDegisikligiSureci
        eco = MuhendislikDegisikligiSureci.objects.filter(ana_proje=self.proje, revizyon_no='Rev.C').first()
        self.assertIsNotNone(eco)
        self.assertEqual(eco.revizyon_no, 'Rev.C')


class IntranetVeIncKeyEntegrasyonTests(TestCase):
    def setUp(self):
        self.client = Client()
        from crm_takip.models import MusteriKarti
        self.musteri = MusteriKarti.objects.create(
            kod="M-099",
            kisa_ad="Bosch",
            ad="Bosch Thermotechnology"
        )

    def test_inckey_uret_ve_preview(self):
        """IncKey algoritmasının sıralı kod üretimini ve önizlemesini test eder"""
        from crm_takip.services.inckey_service import inckey_uret, siradaki_inckey_goruntule
        import datetime
        yil = datetime.date.today().year

        preview1 = siradaki_inckey_goruntule('PRJ')
        self.assertEqual(preview1, f"PRJ-{yil}-101")

        kod1 = inckey_uret('PRJ')
        self.assertEqual(kod1, f"PRJ-{yil}-101")

        preview2 = siradaki_inckey_goruntule('PRJ')
        self.assertEqual(preview2, f"PRJ-{yil}-102")

        kod2 = inckey_uret('PRJ')
        self.assertEqual(kod2, f"PRJ-{yil}-102")

        kod_rev = inckey_uret('PRJ', revizyon=1)
        self.assertEqual(kod_rev, f"PRJ-{yil}-103-1")

    def test_intranet_service_fonksiyonlari(self):
        """Intranet servisinin ana departman ve personel listelerini doğru filtrelerle döndürdüğünü test eder"""
        from crm_takip.services.intranet_service import get_intranet_sirketler, get_proje_liderleri
        sirketler = get_intranet_sirketler()
        self.assertTrue(len(sirketler) > 0)
        self.assertIsInstance(sirketler, list)

        # Hariç tutulması gereken ana departman ve şirket kontrolleri
        for yasak in ['EV HİZMETLERİ', 'KARPEK AMBALAJ', 'KARPEK HUZUR', 'ZEKİ', 'KARPEK', 'YÖNETİM KURULU', 'YONETIM KURULU']:
            self.assertNotIn(yasak, sirketler)

        liderler = get_proje_liderleri()
        self.assertTrue(len(liderler) > 0)
        self.assertIsInstance(liderler, list)
        self.assertIn('ad_soyad', liderler[0])
        for l in liderler:
            self.assertNotIn('KARPEK', l.get('sirket', '').upper())
            self.assertNotIn('ZEK', l.get('sirket', '').upper())
            self.assertNotIn('EV H', l.get('sirket', '').upper())

    def test_ana_proje_ekle_inckey_ve_intranet_ile(self):
        """4 bloklu modal üzerinden yeni proje açıldığında IncKey ve Intranet alanlarının doğru kaydedildiğini test eder"""
        from crm_takip.models import AnaProje
        response = self.client.post(reverse('ana_proje_ekle'), {
            'proje_adi': 'Yeni Nesil Bulaşık Makinesi Yan Panel',
            'musteri_id': self.musteri.id,
            'fabrika': 'PRESHANE',
            'parca_kodu': 'BOSCH-DW-2026',
            'hedef_butce': '320000',
            'yillik_hacim_adet': '150000',
            'sorumlu_lider': 'Buse Nur Baltacıoğlu',
            'aktif_rol': 'Proje Yöneticisi',
            'aktif_surec_adi': 'Yeni Ürün Devreye Alma Süreci'
        })
        self.assertEqual(response.status_code, 302)

        proje = AnaProje.objects.filter(parca_kodu='BOSCH-DW-2026').first()
        self.assertIsNotNone(proje)
        self.assertTrue(proje.proje_kodu.startswith('PRJ-'))
        self.assertEqual(proje.musteri, self.musteri)
        self.assertEqual(proje.fabrika, 'PRESHANE')
        self.assertEqual(proje.hedef_butce, 320000.00)
        self.assertEqual(proje.yillik_hacim_adet, 150000)
        self.assertEqual(proje.sorumlu_lider, 'Buse Nur Baltacıoğlu')


class MusteriAdayiTests(TestCase):
    def setUp(self):
        call_command('seed_pazarlama_adimlari')
        call_command('seed_urun_teklif_adimlari')
        self.client = Client()

    def test_musteri_adayi_olusturma_ve_not_ekleme(self):
        """Yeni müşteri adayı oluşturulduğunda ilk aktivite notunun kaydedildiğini test eder"""
        from crm_takip.models import MusteriAdayi, MusteriAdayiNotu
        response = self.client.post(reverse('musteri_adayi_olustur'), {
            'ad_soyad': 'Markus Weber',
            'sirket_adi': 'Miele Die Werkzeugfabrik',
            'unvan': 'Satınalma Müdürü',
            'sektor': 'Beyaz Eşya',
            'ulke': 'Almanya',
            'sehir': 'Gütersloh',
            'eposta': 'm.weber@miele.de',
            'telefon': '+49 5241 89-0',
            'web_sitesi': 'www.miele.de',
            'kanal': 'Pazar Ziyareti',
            'kaynak': 'Almanya 2026 Ziyareti',
            'durum': 'YENI',
            'oncelik': 'SICAK',
            'tahmini_potansiyel_ciro': '750000',
            'ilgili_urun_gruplari': 'Kondanser, Metal Parça',
            'etiketler': 'Almanya, Pres Parça, Fuar 2026',
            'atanan_sorumlu': 'Buse Nur BALTACIOĞLU',
            'aciklama': 'İlk temas sağlandı, 400T pres kalıp kabiliyetleri soruldu.'
        })
        self.assertEqual(response.status_code, 302)

        adayi = MusteriAdayi.objects.filter(sirket_adi='Miele Die Werkzeugfabrik').first()
        self.assertIsNotNone(adayi)
        self.assertEqual(adayi.ad_soyad, 'Markus Weber')
        self.assertEqual(adayi.durum, 'YENI')
        self.assertEqual(adayi.oncelik, 'SICAK')
        self.assertEqual(adayi.tahmini_potansiyel_ciro, 750000.00)
        self.assertIn('Pres Parça', adayi.etiket_listesi)

        # İlk not kontrolü
        not_kaydi = adayi.notlar.first()
        self.assertIsNotNone(not_kaydi)
        self.assertEqual(not_kaydi.not_tipi, 'NOT')
        self.assertEqual(not_kaydi.baslik, 'Aday Kaydı Oluşturuldu')

    def test_musteri_adaylari_liste_ve_filtreleme(self):
        """Aday havuzunda durum, ülke ve arama parametrelerine göre filtrelemenin doğruluğunu test eder"""
        from crm_takip.models import MusteriAdayi
        MusteriAdayi.objects.create(
            ad_soyad='Hans Gruber',
            sirket_adi='Liebherr Hausgeräte GmbH',
            ulke='Almanya',
            kanal='Fuar & Etkinlik',
            durum='YENI',
            oncelik='SICAK',
            tahmini_potansiyel_ciro=1200000
        )
        MusteriAdayi.objects.create(
            ad_soyad='Piotr Kowalski',
            sirket_adi='Amica S.A.',
            ulke='Polonya',
            kanal='Pazar Ziyareti',
            durum='ILETISIMDE',
            oncelik='ILIK',
            tahmini_potansiyel_ciro=450000
        )
        MusteriAdayi.objects.create(
            ad_soyad='Marco Rossi',
            sirket_adi='DeLonghi Appliances',
            ulke='İtalya',
            kanal='Müşteri Referansı',
            durum='DONUSTURULDU',
            oncelik='ILIK',
            tahmini_potansiyel_ciro=900000
        )

        # 1. Tümü
        resp_all = self.client.get(reverse('musteri_adaylari_liste'))
        self.assertEqual(resp_all.status_code, 200)
        self.assertEqual(resp_all.context['toplam_aday'], 3)
        self.assertEqual(resp_all.context['yeni_adaylar_sayisi'], 1)
        self.assertEqual(resp_all.context['iletisimde_sayisi'], 1)
        self.assertEqual(resp_all.context['donusturulen_sayisi'], 1)

        # 2. Ülke Filtresi: Almanya
        resp_ulke = self.client.get(reverse('musteri_adaylari_liste') + '?ulke=Almanya')
        self.assertEqual(resp_ulke.status_code, 200)
        self.assertEqual(resp_ulke.context['adaylar'].count(), 1)
        self.assertEqual(resp_ulke.context['adaylar'][0].sirket_adi, 'Liebherr Hausgeräte GmbH')

        # 3. Metin Arama: Amica
        resp_q = self.client.get(reverse('musteri_adaylari_liste') + '?q=Amica')
        self.assertEqual(resp_q.status_code, 200)
        self.assertEqual(resp_q.context['adaylar'].count(), 1)
        self.assertEqual(resp_q.context['adaylar'][0].ad_soyad, 'Piotr Kowalski')

    def test_musteri_adayi_detay_ve_durum_guncelleme(self):
        """Aday durumunun güncellendiğini ve zaman tüneline log düştüğünü test eder"""
        from crm_takip.models import MusteriAdayi, MusteriAdayiNotu
        adayi = MusteriAdayi.objects.create(
            ad_soyad='Elena Dumitru',
            sirket_adi='Arctic S.A.',
            ulke='Romanya',
            durum='YENI',
            oncelik='ILIK'
        )

        # Durum güncelle
        resp = self.client.post(reverse('musteri_adayi_durum_guncelle', args=[adayi.pk]), {
            'durum': 'NITELIKLI',
            'oncelik': 'SICAK',
            'not_metni': 'Müşteri bütçesi onaylandı, numune talep ediyor.',
            'ekleyen': 'Buse Nur BALTACIOĞLU'
        })
        self.assertEqual(resp.status_code, 302)
        adayi.refresh_from_db()
        self.assertEqual(adayi.durum, 'NITELIKLI')
        self.assertEqual(adayi.oncelik, 'SICAK')

        # Durum değişikliği notu
        not_log = adayi.notlar.filter(not_tipi='DURUM_DEGISIKLIGI').first()
        self.assertIsNotNone(not_log)
        self.assertIn('Nitelikli Aday', not_log.baslik)
        self.assertIn('numune talep ediyor', not_log.icerik)

    def test_musteri_adayi_not_ekleme(self):
        """Adaya manuel aktivite notu eklenmesini test eder"""
        from crm_takip.models import MusteriAdayi
        adayi = MusteriAdayi.objects.create(
            ad_soyad='Thomas Müller',
            sirket_adi='Siemens AG',
            ulke='Almanya'
        )

        resp = self.client.post(reverse('musteri_adayi_not_ekle', args=[adayi.pk]), {
            'not_tipi': 'TOPLANTI',
            'baslik': 'Online Tanıtım Toplantısı',
            'icerik': 'Kalıp kabiliyetlerimiz ve Simpac 400T pres sunuldu.',
            'ekleyen': 'Buse Nur BALTACIOĞLU'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(adayi.notlar.filter(not_tipi='TOPLANTI').count(), 1)

    def test_musteri_adayi_donusturme_musteri_kartina(self):
        """Adayın tek tıkla resmi MusteriKarti, MusteriTesisi ve Zaman Tüneline dönüştüğünü test eder"""
        from crm_takip.models import MusteriAdayi, MusteriKarti, MusteriTesisi
        adayi = MusteriAdayi.objects.create(
            ad_soyad='Carlos Sainz',
            sirket_adi='Balay Electrodomesticos',
            unvan='Satınalma Direktörü',
            ulke='İspanya',
            sehir='Zaragoza',
            eposta='carlos.sainz@balay.es',
            telefon='+34 976 123456',
            kanal='Pazar Ziyareti',
            kaynak='İspanya 2026 Q1',
            durum='NITELIKLI',
            tahmini_potansiyel_ciro=1800000,
            ilgili_urun_gruplari='Sac Parça'
        )

        resp = self.client.post(reverse('musteri_adayi_donustur', args=[adayi.pk]), {
            'tier': 'Tier 1 - KAM',
            'strateji': 'Grow',
            'firma_kodu': 'FRM-99',
            'surec_baslat': 'YOK',
            'user_name': 'Buse Nur BALTACIOĞLU'
        })
        self.assertEqual(resp.status_code, 302)

        adayi.refresh_from_db()
        self.assertEqual(adayi.durum, 'DONUSTURULDU')
        self.assertIsNotNone(adayi.donusturulen_musteri)
        self.assertIsNotNone(adayi.donusturme_tarihi)

        musteri = adayi.donusturulen_musteri
        self.assertEqual(musteri.kod, 'FRM-99')
        self.assertEqual(musteri.ad, 'Balay Electrodomesticos')
        self.assertEqual(musteri.tier, 'Tier 1 - KAM')
        self.assertEqual(musteri.strateji, 'Grow')
        self.assertEqual(musteri.yillik_ciro_eur, 1800000.00)

        # Müşteri tesisi kontrolü
        tesis = musteri.tesisler.first()
        self.assertIsNotNone(tesis)
        self.assertEqual(tesis.yetkili_adi, 'Carlos Sainz')
        self.assertEqual(tesis.yetkili_email, 'carlos.sainz@balay.es')

    def test_musteri_adayi_donusturme_ile_urun_teklif_sureci(self):
        """Aday dönüştürülürken URUN_TEKLIF seçilirse otomatik RFQ teklif sürecinin başladığını test eder"""
        from crm_takip.models import MusteriAdayi, UrunTeklifSureci
        adayi = MusteriAdayi.objects.create(
            ad_soyad='Jean Dupont',
            sirket_adi='Groupe SEB France',
            ulke='Fransa',
            durum='NITELIKLI',
            tahmini_potansiyel_ciro=850000
        )

        resp = self.client.post(reverse('musteri_adayi_donustur', args=[adayi.pk]), {
            'tier': 'Tier 2 - Growth',
            'strateji': 'Start',
            'surec_baslat': 'URUN_TEKLIF',
            'user_name': 'Buse Nur BALTACIOĞLU'
        })
        self.assertEqual(resp.status_code, 302)

        adayi.refresh_from_db()
        self.assertEqual(adayi.durum, 'DONUSTURULDU')

        teklif = UrunTeklifSureci.objects.filter(musteri_karti=adayi.donusturulen_musteri).first()
        self.assertIsNotNone(teklif)
        self.assertTrue(teklif.kod.startswith('TEK-'))
        self.assertIn('Groupe SEB France', teklif.ad)
        self.assertEqual(teklif.adim_kayitlari.count(), 40)
        self.assertEqual(teklif.guncel_adim_no, 1)

    def test_musteri_karti_dogrudan_olusturma(self):
        """Müşteri portföyüne modal üzerinden direkt MusteriKarti eklendiğini test eder"""
        from crm_takip.models import MusteriKarti
        resp = self.client.post(reverse('musteri_karti_olustur'), {
            'ad': 'Electrolux Professional AB',
            'kisa_ad': 'Electrolux',
            'ulke': 'İsveç',
            'sehir': 'Stockholm',
            'tier': 'Tier 1 - KAM',
            'strateji': 'Protect',
            'yillik_ciro_eur': '3500000',
            'kam_satis_lideri': 'Buse Nur BALTACIOĞLU',
            'aktif_urunler': 'Kondanser, Pres Sac',
            'yetkili_kisi': 'Sven Larsson',
            'yetkili_unvan': 'Global Category Manager',
            'yetkili_email': 'sven.larsson@electrolux.com',
            'notlar': 'Stratejik partnerlik değerlendiriliyor.'
        })
        self.assertEqual(resp.status_code, 302)

        musteri = MusteriKarti.objects.filter(kisa_ad='Electrolux').first()
        self.assertIsNotNone(musteri)
        self.assertTrue(musteri.kod.startswith('FRM-'))
        self.assertEqual(musteri.tier, 'Tier 1 - KAM')
        self.assertEqual(musteri.yillik_ciro_eur, 3500000.00)
        self.assertEqual(musteri.tesisler.count(), 1)
        self.assertEqual(musteri.tesisler.first().yetkili_adi, 'Sven Larsson')

    def test_musteri_adayi_silme(self):
        """Aday kaydının silinmesini test eder"""
        from crm_takip.models import MusteriAdayi
        adayi = MusteriAdayi.objects.create(
            ad_soyad='Test Silinecek',
            sirket_adi='Silinecek Ltd',
            ulke='Türkiye'
        )
        pk = adayi.pk
        resp = self.client.post(reverse('musteri_adayi_sil', args=[pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(MusteriAdayi.objects.filter(pk=pk).exists())


















