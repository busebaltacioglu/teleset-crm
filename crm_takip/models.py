from django.db import models
from django.utils import timezone


class SurecAdimTanimi(models.Model):
    """
    15 Adımlık Pazarlama Süreci Master Verisi
    """
    adim_no = models.PositiveSmallIntegerField(unique=True, verbose_name="Adım Numarası")
    baslik = models.CharField(max_length=255, verbose_name="Süreç Adımı Başlığı")
    faaliyet_tanimi = models.TextField(verbose_name="Faaliyet Tanımı")
    sorumlular_raci = models.TextField(verbose_name="Sorumlular (RACI)")
    ilgili_dokumanlar = models.TextField(verbose_name="İlgili Dokümanlar", blank=True, null=True)
    dijital_platformlar = models.TextField(verbose_name="Dijital Platformlar", blank=True, null=True)
    karar_adimi_mi = models.BooleanField(default=False, verbose_name="Karar / Onay Adımı mı?")
    
    FAZ_CHOICES = [
        ('FAZ1', 'Faz 1: Pazar & Strateji Planlama (Adım 1-6)'),
        ('FAZ2', 'Faz 2: Müşteri Teması & Talep Alma (Adım 7-10)'),
        ('FAZ3', 'Faz 3: Ön Mutabakat & Değerlendirme (Adım 11-12)'),
        ('FAZ4', 'Faz 4: Tedarikçi Onayı, Teklif & Kapanış (Adım 13-15)'),
    ]
    faz = models.CharField(max_length=10, choices=FAZ_CHOICES, default='FAZ1', verbose_name="Süreç Fazı")

    class Meta:
        ordering = ['adim_no']
        verbose_name = "Süreç Adım Tanımı"
        verbose_name_plural = "Süreç Adım Tanımları"

    def __str__(self):
        return f"{self.adim_no}. {self.baslik}"

    @property
    def dokuman_listesi(self):
        if not self.ilgili_dokumanlar:
            return []
        items = []
        for line in self.ilgili_dokumanlar.replace('\r\n', '\n').split('\n'):
            for part in line.split(','):
                cleaned = part.strip()
                if cleaned:
                    items.append(cleaned)
        return items

    @property
    def platform_listesi(self):
        if not self.dijital_platformlar:
            return []
        items = []
        for line in self.dijital_platformlar.replace('\r\n', '\n').split('\n'):
            for part in line.split(','):
                cleaned = part.strip()
                if cleaned:
                    items.append(cleaned)
        return items


class HedefPazarKanvas(models.Model):
    """
    Teleset Hedef Ülke Stratejisi ve 360° Pazar Kanvası (2025-2028 Strateji Belgesi)
    """
    ulke_kodu = models.CharField(max_length=10, unique=True, verbose_name="Ülke Kodu")
    ulke_adi = models.CharField(max_length=100, verbose_name="Hedef Ülke Adı")
    bayrak_emoji = models.CharField(max_length=10, default="", blank=True, verbose_name="Bayrak")
    oncelik_sinifi = models.CharField(max_length=50, default="Birincil Pazar", verbose_name="Pazar Sınıfı")
    
    # 6 Blok Kanvas
    genel_gorunum = models.TextField(verbose_name="1. Ülke Genel Görünüm")
    sektor_pazari = models.TextField(verbose_name="2. Beyaz Eşya / Sektör Pazarı")
    one_cikan_sirketler = models.TextField(verbose_name="3. Öne Çıkan Şirketler & Müşteriler")
    egilimler_ve_zorluklar = models.TextField(verbose_name="4. Eğilimler ve Zorluklar")
    vergilendirme_ve_gumruk = models.TextField(verbose_name="5. Vergilendirme & Gümrükleme")
    teleset_degerlendirmesi = models.TextField(verbose_name="6. Teleset Açısından Değerlendirme")
    
    # 2025-2028 Stratejik Değerlendirme
    kritik_basari_faktorleri = models.TextField(blank=True, null=True, verbose_name="Teleset İçin 3 Kritik Başarı Faktörü")
    ana_kaldirac = models.TextField(blank=True, null=True, verbose_name="1 Ana Kaldıraç")
    ana_risk = models.TextField(blank=True, null=True, verbose_name="1 Ana Risk")
    hizli_kazanim = models.TextField(blank=True, null=True, verbose_name="1 Hızlı Kazanım")
    stratejik_bahis = models.TextField(blank=True, null=True, verbose_name="Stratejik Bahis (2025–2028)")
    
    # SWOT Analizi Sonuçlarına Dayalı Stratejik Yaklaşım
    swot_guclu_yonler = models.TextField(blank=True, null=True, verbose_name="Güçlü Yönlerden Yararlanma Stratejileri")
    swot_zayif_yonler = models.TextField(blank=True, null=True, verbose_name="Zayıf Yönleri Minimize Etme Stratejileri")
    swot_firsatlar = models.TextField(blank=True, null=True, verbose_name="Fırsatları Değerlendirme Stratejileri")
    swot_tehditler = models.TextField(blank=True, null=True, verbose_name="Tehditleri Azaltma Stratejileri")
    
    # 6P Stratejik Hedefleri (2025–2028)
    hedef_6p_urun = models.TextField(blank=True, null=True, verbose_name="3.1 Ürün (Product) Hedefleri")
    hedef_6p_fiyat = models.TextField(blank=True, null=True, verbose_name="3.2 Fiyat (Price) Hedefleri")
    hedef_6p_yer_dagitim = models.TextField(blank=True, null=True, verbose_name="3.3 Yer (Place) / Dağıtım Hedefleri")
    hedef_6p_promosyon = models.TextField(blank=True, null=True, verbose_name="3.4 Promosyon (Promotion) Hedefleri")
    hedef_6p_insan = models.TextField(blank=True, null=True, verbose_name="3.5 İnsan (People) Hedefleri")
    hedef_6p_surec = models.TextField(blank=True, null=True, verbose_name="3.6 Süreç (Process) Hedefleri")
    
    # Öncelikli Eylemler, Fuarlar ve Yayınlar
    oncelikli_eylemler = models.TextField(blank=True, null=True, verbose_name="4. Öncelikli Eylemler (2025–2028)")
    hedef_fuarlar = models.TextField(blank=True, null=True, verbose_name="Hedef Sektörel Fuarlar & Etkinlikler")
    sektorel_yayinlar = models.TextField(blank=True, null=True, verbose_name="Sektörel Yayınlar & Medya")

    hedef_urunler = models.CharField(max_length=255, default="Kondanser, Kablo Grubu, Metal Parça, Kalıp", verbose_name="Hedef Ürün Grupları")
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)

    @property
    def hedef_urun_listesi(self):
        if not self.hedef_urunler:
            return []
        return [u.strip() for u in self.hedef_urunler.split(',') if u.strip()]

    class Meta:
        ordering = ['ulke_adi']
        verbose_name = "Hedef Pazar Kanvası"
        verbose_name_plural = "Hedef Pazar Kanvasları"

    def __str__(self):
        return f"{self.bayrak_emoji} {self.ulke_adi} ({self.oncelik_sinifi})"


class MusteriKarti(models.Model):
    """
    Stratejik Müşteri Portföy Kartı (CPM & 360° Müşteri Görünümü)
    """
    TIER_CHOICES = [
        ('Tier 1 - KAM', 'Tier 1 - KAM (Stratejik Ana Müşteri)'),
        ('Tier 2 - Growth', 'Tier 2 - Growth (Büyüme Odaklı Müşteri)'),
        ('Tier 3 - Standart', 'Tier 3 - Standart Müşteri'),
    ]

    STRATEGY_CHOICES = [
        ('Protect', 'Protect (İlişkiyi Koru & Derinleştir)'),
        ('Grow', 'Grow (Cüzdan Payını ve Hacmi Büyüt)'),
        ('Harvest', 'Harvest (Kârlılık Odaklı Yönet)'),
        ('Re-engineer', 'Re-engineer (Süreç & Maliyet İyileştirme)'),
        ('Start', 'Start (Yeni Başlangıç / Geliştirme)'),
    ]

    kod = models.CharField(max_length=20, unique=True, verbose_name="Müşteri Kodu (FRM-XX)")
    ad = models.CharField(max_length=200, verbose_name="Firma Resmi Unvanı")
    kisa_ad = models.CharField(max_length=50, verbose_name="Kısa / Marka Adı")
    ulke = models.CharField(max_length=100, verbose_name="Ülke")
    sehir = models.CharField(max_length=100, blank=True, null=True, verbose_name="Şehir / Tesis Lokasyonu")
    
    tier = models.CharField(max_length=30, choices=TIER_CHOICES, default='Tier 1 - KAM', verbose_name="Müşteri Segmenti (Tier)")
    strateji = models.CharField(max_length=30, choices=STRATEGY_CHOICES, default='Protect', verbose_name="CPM Stratejisi")
    
    yillik_ciro_eur = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name="Yıllık Ciro (€)")
    cuzdan_payi_yuzde = models.PositiveSmallIntegerField(default=50, verbose_name="Cüzdan Payı (SOW %)")
    aktif_proje_sayisi = models.PositiveSmallIntegerField(default=1, verbose_name="Aktif Proje Sayısı")
    
    kam_satis_lideri = models.CharField(max_length=100, default="Buse Nur BALTACIOĞLU", verbose_name="KAM Satış Lideri")
    kam_muhendislik_lideri = models.CharField(max_length=100, default="Ahmet AK (Kalıp & Projeci Md.)", verbose_name="KAM Projeci Lideri")
    kam_kalite_lideri = models.CharField(max_length=100, default="Mehmet YILMAZ (Kalite Güvence Md.)", verbose_name="KAM Kalite Lideri")
    
    aktif_urunler = models.TextField(blank=True, null=True, verbose_name="Aktif Üretilen Parçalar / Ürünler")
    sozlesme_durumu = models.CharField(max_length=150, default="STG-TL-001 (Aktif)", verbose_name="Sözleşme & Onay Durumu")
    churn_riski = models.CharField(max_length=50, default="0.05 (Düşük Risk)", verbose_name="Müşteri Kayıp Riski")
    notlar = models.TextField(blank=True, null=True, verbose_name="Stratejik Notlar / Özet")

    class Meta:
        ordering = ['-yillik_ciro_eur']
        verbose_name = "Müşteri Kartı"
        verbose_name_plural = "Müşteri Kartları"

    def __str__(self):
        return f"{self.kisa_ad} ({self.tier})"

    @property
    def yillik_ciro_m_str(self):
        val = float(self.yillik_ciro_eur) / 1000000.0
        return f"{val:.2f}"

    @property
    def clv_m_str(self):
        val = (float(self.yillik_ciro_eur) * 3.76) / 1000000.0
        return f"{val:.1f}"


class MusteriTesisi(models.Model):
    """
    Müşteriye Ait Fabrika / Tesis Lokasyonu (Örn: Bosch Manisa, Bosch Romanya, Bosch Almanya, BSH Çerkezköy)
    """
    musteri = models.ForeignKey(MusteriKarti, on_delete=models.CASCADE, related_name="tesisler", verbose_name="Müşteri Grubu")
    tesis_adi = models.CharField(max_length=150, verbose_name="Tesis / Fabrika Adı")
    lokasyon = models.CharField(max_length=150, verbose_name="Şehir / Ülke")
    kod = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tesis Kodu")
    
    clv_m = models.CharField(max_length=50, default="45.8 M€", verbose_name="Yaşam Boyu Değer (CLV)")
    churn_skoru = models.CharField(max_length=50, default="0.05", verbose_name="Terk (Churn) Skoru")
    churn_durumu = models.CharField(max_length=50, default="Düşük Risk", verbose_name="Churn Durumu")
    yillik_ciro_str = models.CharField(max_length=50, default="€ 12.18M", verbose_name="Yıllık Ciro")
    ciro_alt_bilgi = models.CharField(max_length=100, default="1.284 Stok Kodu", verbose_name="Ciro Alt Bilgi")
    cuzdan_payi_yuzde = models.PositiveSmallIntegerField(default=58, verbose_name="Cüzdan Payı %")
    cuzdan_alt_bilgi = models.CharField(max_length=100, default="Sac & Kablo Grubu", verbose_name="Cüzdan Alt Bilgi")
    
    destek_sayisi = models.PositiveSmallIntegerField(default=9, verbose_name="Destek / Talep Sayısı")
    npi_proje_sayisi = models.PositiveSmallIntegerField(default=28, verbose_name="NPI Proje Sayısı")
    teklif_sayisi = models.PositiveSmallIntegerField(default=9, verbose_name="Teklif (SAT) Sayısı")
    sevkiyat_sayisi = models.PositiveSmallIntegerField(default=9, verbose_name="Sevkiyat Sayısı")
    
    kam_satis_lideri = models.CharField(max_length=100, default="BUSE NUR BALTACIOĞLU (İş Geliştirme)", verbose_name="Satış Lead")
    kam_muhendislik_lideri = models.CharField(max_length=100, default="YİĞİT EFE BİLİR (İş Çözümleri Mühendisi)", verbose_name="Kalıp/Projeci Lead")
    kam_kalite_lideri = models.CharField(max_length=100, default="METİN YAVAŞ (Bakım & Kalite Şefi)", verbose_name="Kalite Lead")
    
    yetkili_adi = models.CharField(max_length=150, default="Klaus Schmidt", verbose_name="Müşteri Yetkilisi")
    yetkili_unvan = models.CharField(max_length=150, default="Global Satınalma Direktörü", verbose_name="Yetkili Unvanı")
    yetkili_email = models.CharField(max_length=150, default="klaus.schmidt@bsh.com", verbose_name="Yetkili E-Posta")
    yetkili_telefon = models.CharField(max_length=50, blank=True, null=True, verbose_name="Yetkili Telefon")
    
    son_etkilesim = models.CharField(max_length=200, default="Dün 14:30 - Yeni SIMPAC 400T Kalıp İncelemesi", verbose_name="Son Etkileşim")
    sira = models.PositiveSmallIntegerField(default=1, verbose_name="Sıralama")

    class Meta:
        ordering = ['sira', 'id']
        verbose_name = "Müşteri Tesisi"
        verbose_name_plural = "Müşteri Tesisleri"

    def __str__(self):
        return f"{self.musteri.kisa_ad} - {self.tesis_adi}"


class MusteriEtkilesimZamanTuneli(models.Model):
    """
    360° Müşteri Profili Kronolojik Aktivite ve Süreç Zaman Tüneli
    """
    musteri = models.ForeignKey(MusteriKarti, on_delete=models.CASCADE, related_name="etkilesimler", verbose_name="Müşteri")
    tesis = models.ForeignKey(MusteriTesisi, on_delete=models.SET_NULL, null=True, blank=True, related_name="etkilesimler", verbose_name="İlgili Tesis")
    
    kod = models.CharField(max_length=50, default="SAT-EK-005", verbose_name="Süreç / Form Kodu")
    baslik = models.CharField(max_length=200, verbose_name="Aktivite Başlığı")
    aciklama = models.TextField(verbose_name="Açıklama / Detay")
    sorumlu = models.CharField(max_length=100, default="Buse Nur BALTACIOĞLU", verbose_name="Sorumlu Kişi")
    tarih = models.DateField(default=timezone.now, verbose_name="İşlem Tarihi")
    donem_ay_yil = models.CharField(max_length=50, default="EYLÜL 2026", verbose_name="Dönem Başlığı")
    ikon = models.CharField(max_length=50, default="bi-file-earmark-text-fill", verbose_name="Bootstrap İkonu")
    ikon_bg = models.CharField(max_length=50, default="bg-warning", verbose_name="İkon Arka Planı")

    class Meta:
        ordering = ['-tarih', '-id']
        verbose_name = "Müşteri Etkileşim Kaydı"
        verbose_name_plural = "Müşteri Etkileşim Kayıtları"

    def __str__(self):
        return f"{self.musteri.kisa_ad} - {self.baslik} ({self.tarih})"



class UrunGrubuKarti(models.Model):
    """
    Teleset Ürün Grubu & Üretim Kabiliyet Kartı
    """
    kod = models.CharField(max_length=50, unique=True, verbose_name="Ürün Grubu Kodu")
    baslik = models.CharField(max_length=150, verbose_name="Ürün Grubu Başlığı")
    ikon = models.CharField(max_length=50, default="bi-box-seam", verbose_name="Bootstrap İkonu")
    ana_fabrika = models.CharField(max_length=150, verbose_name="Ana Üretim Fabrikası")
    
    kabiliyetler = models.TextField(verbose_name="Makine Parkı & Üretim Kabiliyetleri")
    referans_parcalar = models.TextField(verbose_name="Referans Parçalar & Ürünler")
    yillik_kapasite = models.CharField(max_length=150, verbose_name="Yıllık Üretim Kapasitesi")
    hedef_sektorler = models.CharField(max_length=255, default="Beyaz Eşya, Otomotiv, İklimlendirme", verbose_name="Hedef Sektörler")
    kalite_standartlari = models.CharField(max_length=255, default="ISO 9001, IATF 16949, ISO 14001, ISO 45001", verbose_name="Kalite Standartları")

    class Meta:
        ordering = ['kod']
        verbose_name = "Ürün Grubu Kartı"
        verbose_name_plural = "Ürün Grubu Kartları"

    def __str__(self):
        return self.baslik


class PazarlamaProjesi(models.Model):
    """
    Pazarlama Sürecine Tabi Olan Müşteri / Fırsat / Proje Kaydı
    """
    DURUM_CHOICES = [
        ('DEVAM_EDIYOR', 'Devam Ediyor'),
        ('TEKLIF_SURECINDE', 'Ürün Teklif Sürecine Aktarıldı'),
        ('BASARIYLA_KAPATILDI', 'Başarıyla Kapatıldı'),
        ('OLUMSUZ_KAPATILDI', 'Olumsuz Sonuçlandı / Kapatıldı'),
        ('ASKIDA', 'Askıda / Beklemede'),
    ]

    URUN_GRUBU_CHOICES = [
        ('Metal Parca & Sac', 'Metal Parça & Sac Şekillendirme'),
        ('Kondanser & Sogutma', 'Kondanser & Soğutma'),
        ('Kondenser & Sogutma', 'Kondanser & Soğutma (Eski)'),
        ('Kablo Grubu', 'Kablo Grubu & Demetleri'),
        ('Kalıp & Fikstür', 'Kalıp, Fikstür & Aparat'),
        ('Montaj ve Kaynak', 'Montaj ve Kaynak'),
        ('Plastik Enjeksiyon', 'Plastik Enjeksiyon'),
        ('Batarya & EV Bilesenleri', 'Batarya & EV Bileşenleri'),
        ('Genel / Diger', 'Genel / Diğer'),
    ]

    FABRIKA_CHOICES = [
        ('PRESHANE', 'PRESHANE'),
        ('KALIPHANE', 'KALIPHANE'),
        ('CERKEZKOY', 'CERKEZKOY'),
        ('KABLOGR', 'KABLOGR'),
        ('KONDANSER', 'KONDANSER'),
        ('MANISA ORTAK', 'MANISA ORTAK'),
    ]

    kod = models.CharField(max_length=50, unique=True, verbose_name="Proje / Fırsat Kodu")
    ad = models.CharField(max_length=200, verbose_name="Proje / Fırsat Başlığı")
    musteri_adi = models.CharField(max_length=150, verbose_name="Hedef Müşteri / Firma")
    musteri_karti = models.ForeignKey(MusteriKarti, on_delete=models.SET_NULL, null=True, blank=True, related_name="projeler", verbose_name="Müşteri Portföy Kartı")
    
    hedef_ulke = models.CharField(max_length=100, verbose_name="Hedef Ülke / Pazar")
    hedef_pazar_kanvasi = models.ForeignKey(HedefPazarKanvas, on_delete=models.SET_NULL, null=True, blank=True, related_name="projeler", verbose_name="İlişkili Ülke Kanvası")
    
    urun_grubu = models.CharField(max_length=100, choices=URUN_GRUBU_CHOICES, default='Metal Parca & Sac', verbose_name="Ürün Grubu")
    urun_grubu_karti = models.ForeignKey(UrunGrubuKarti, on_delete=models.SET_NULL, null=True, blank=True, related_name="projeler", verbose_name="İlişkili Ürün Grubu Kartı")
    
    ilgili_fabrika = models.CharField(max_length=100, choices=FABRIKA_CHOICES, default='PRESHANE', verbose_name="İlgili Fabrika / Ana Departman")
    
    sorumlu_pazarlama_uzmani = models.CharField(max_length=100, default='BUSE NUR BALTACIOĞLU', verbose_name="Pazarlama Uzmanı (R)")
    sorumlu_satis_muduru = models.CharField(max_length=100, default='YİĞİT EFE BİLİR', verbose_name="Satış & Pazarlama Müdürü (A)")
    
    durum = models.CharField(max_length=30, choices=DURUM_CHOICES, default='DEVAM_EDIYOR', verbose_name="Süreç Durumu")
    guncel_adim_no = models.PositiveSmallIntegerField(default=1, verbose_name="Güncel Adım No")
    
    tahmini_butce = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Tahmini Bütçe (EUR/TL)")
    beklenen_ciro = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Beklenen Yıllık Ciro (EUR)")
    
    aciklama = models.TextField(blank=True, null=True, verbose_name="Genel Proje Notu / Özeti")
    
    olusturma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    guncelleme_tarihi = models.DateTimeField(auto_now=True, verbose_name="Son Güncelleme")

    class Meta:
        ordering = ['-guncelleme_tarihi']
        verbose_name = "Pazarlama Süreci"
        verbose_name_plural = "Pazarlama Süreçleri"

    def __str__(self):
        return f"{self.kod} - {self.musteri_adi} ({self.ad})"

    @property
    def tamamlanma_yuzdesi(self):
        toplam_adim = 15
        tamamlanan = self.adim_kayitlari.filter(durum__in=['TAMAMLANDI', 'PAS_GECILDI']).count()
        return int((tamamlanan / toplam_adim) * 100)

    @property
    def guncel_adim(self):
        return self.adim_kayitlari.filter(adim__adim_no=self.guncel_adim_no).first()


class ProjeAdimKaydi(models.Model):
    DURUM_CHOICES = [
        ('BEKLIYOR', 'Bekliyor'),
        ('DEVAM_EDIYOR', 'Devam Ediyor / Aktif'),
        ('TAMAMLANDI', 'Tamamlandı (Onaylandı)'),
        ('REVIZYON_YONLENDIRILDI', 'Geriye Revizyona Gönderildi'),
        ('PAS_GECILDI', 'Pas Geçildi / Muaf'),
    ]

    proje = models.ForeignKey(PazarlamaProjesi, on_delete=models.CASCADE, related_name='adim_kayitlari', verbose_name="Proje")
    adim = models.ForeignKey(SurecAdimTanimi, on_delete=models.PROTECT, verbose_name="Süreç Adımı")
    durum = models.CharField(max_length=30, choices=DURUM_CHOICES, default='BEKLIYOR', verbose_name="Durum")
    
    tamamlayan = models.CharField(max_length=100, blank=True, null=True, verbose_name="İşlemi Yapan")
    tamamlanma_tarihi = models.DateTimeField(blank=True, null=True, verbose_name="Tamamlanma Tarihi")
    
    karar_sonucu = models.CharField(max_length=100, blank=True, null=True, verbose_name="Verilen Karar")
    notlar = models.TextField(blank=True, null=True, verbose_name="Adım Notları / Gerekçe / Müşteri Geri Bildirimi")
    dokuman_referansi = models.CharField(max_length=255, blank=True, null=True, verbose_name="Doküman Linki / Referans No")
    
    tamamlanan_dokumanlar = models.TextField(blank=True, default='', verbose_name="Tamamlanan / Tiklenen Dokümanlar")
    tamamlanan_platformlar = models.TextField(blank=True, default='', verbose_name="Kullanılan / Tiklenen Platformlar")

    @property
    def tamamlanan_dokuman_listesi(self):
        if not self.tamamlanan_dokumanlar:
            return []
        return [d.strip() for d in self.tamamlanan_dokumanlar.splitlines() if d.strip()]

    @property
    def tamamlanan_platform_listesi(self):
        if not self.tamamlanan_platformlar:
            return []
        return [p.strip() for p in self.tamamlanan_platformlar.splitlines() if p.strip()]

    class Meta:
        ordering = ['adim__adim_no']
        unique_together = ('proje', 'adim')
        verbose_name = "Proje Adım Kaydı"
        verbose_name_plural = "Proje Adım Kayıtları"

    def __str__(self):
        return f"{self.proje.kod} - Adım {self.adim.adim_no} ({self.get_durum_display()})"


class ProjeGecmisLog(models.Model):
    proje = models.ForeignKey(PazarlamaProjesi, on_delete=models.CASCADE, related_name='tarihce_kayitlari', verbose_name="Proje")
    islem = models.CharField(max_length=255, verbose_name="Yapılan İşlem")
    detay = models.TextField(blank=True, null=True, verbose_name="İşlem Detayı")
    yapan = models.CharField(max_length=100, default='Sistem', verbose_name="İşlemi Yapan")
    tarih = models.DateTimeField(default=timezone.now, verbose_name="İşlem Tarihi")

    class Meta:
        ordering = ['-tarih']
        verbose_name = "Proje Geçmiş Logu"
        verbose_name_plural = "Proje Geçmiş Logları"

    def __str__(self):
        return f"{self.proje.kod} - {self.islem} ({self.tarih.strftime('%d.%m.%Y %H:%M')})"


class MusteriIliskileriAdimTanimi(models.Model):
    """
    11 Adımlık Müşteri İlişkileri Süreci Master Verisi (Doküman No: EYS-EK-028)
    """
    adim_no = models.PositiveSmallIntegerField(unique=True, verbose_name="Adım Numarası")
    baslik = models.CharField(max_length=255, verbose_name="Süreç Adımı Başlığı")
    faaliyet_tanimi = models.TextField(verbose_name="Faaliyet Tanımı")
    sorumlular = models.TextField(verbose_name="Sorumlular")
    ilgili_dokumanlar = models.TextField(verbose_name="İlgili Dokümanlar", blank=True, null=True)
    karar_adimi_mi = models.BooleanField(default=False, verbose_name="Karar / Kriter Adımı mı?")
    
    FAZ_CHOICES = [
        ('FAZ1', 'Faz 1: Müşteri Tanımlama & İhtiyaç Analizi (Adım 1-4)'),
        ('FAZ2', 'Faz 2: Performans Ölçümü & Kriter Kontrolü (Adım 5-6)'),
        ('FAZ3', 'Faz 3: Memnuniyet Anketleri & İyileştirme Aksiyonları (Adım 7-9)'),
        ('FAZ4', 'Faz 4: YGG Raporlama & Dijital İzleme (Adım 10-11)'),
    ]
    faz = models.CharField(max_length=10, choices=FAZ_CHOICES, default='FAZ1', verbose_name="Süreç Fazı")

    class Meta:
        ordering = ['adim_no']
        verbose_name = "Müşteri İlişkileri Adım Tanımı"
        verbose_name_plural = "Müşteri İlişkileri Adım Tanımları"

    def __str__(self):
        return f"{self.adim_no}. {self.baslik}"

    @property
    def dokuman_listesi(self):
        if not self.ilgili_dokumanlar:
            return []
        items = []
        for line in self.ilgili_dokumanlar.replace('\r\n', '\n').split('\n'):
            for part in line.split(','):
                cleaned = part.strip()
                if cleaned:
                    items.append(cleaned)
        return items


class MusteriIliskileriSureci(models.Model):
    """
    Müşteri İlişkileri Süreci Takip Kaydı (EYS-EK-028)
    """
    DURUM_CHOICES = [
        ('DEVAM_EDIYOR', 'Devam Ediyor'),
        ('UYGUNSUZLUK_YONETIMINDE', 'Uygunsuzluk Yönetimi Sürecinde'),
        ('BASARIYLA_TAMAMLANDI', 'Başarıyla Tamamlandı'),
        ('ASKIDA', 'Askıda / Beklemede'),
    ]

    kod = models.CharField(max_length=50, unique=True, verbose_name="Süreç Kodu")
    ad = models.CharField(max_length=200, verbose_name="Süreç Başlığı / Konusu")
    musteri_adi = models.CharField(max_length=150, verbose_name="Müşteri / Firma Adı")
    musteri_karti = models.ForeignKey(MusteriKarti, on_delete=models.SET_NULL, null=True, blank=True, related_name="musteri_iliskileri_surecleri", verbose_name="Müşteri Portföy Kartı")
    
    donem = models.CharField(max_length=50, default="2026 Yıllık", verbose_name="İzleme Dönemi / Yıl")
    ilgili_fabrika = models.CharField(max_length=100, choices=PazarlamaProjesi.FABRIKA_CHOICES, default='PRESHANE', verbose_name="İlgili Fabrika")
    
    sorumlu_eys = models.CharField(max_length=100, default='BUSE NUR BALTACIOĞLU', verbose_name="EYS Sorumlusu")
    sorumlu_surec_sahibi = models.CharField(max_length=100, default='ONUR TUNCER', verbose_name="Süreç Sahibi / İyileştirme Ekibi")
    
    durum = models.CharField(max_length=30, choices=DURUM_CHOICES, default='DEVAM_EDIYOR', verbose_name="Süreç Durumu")
    guncel_adim_no = models.PositiveSmallIntegerField(default=1, verbose_name="Güncel Adım No")
    
    memnuniyet_puani = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="Müşteri Memnuniyet Puanı (0-100)")
    aciklama = models.TextField(blank=True, null=True, verbose_name="Süreç Özeti / İlk Notlar")
    
    olusturma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    guncelleme_tarihi = models.DateTimeField(auto_now=True, verbose_name="Son Güncelleme")

    class Meta:
        ordering = ['-guncelleme_tarihi']
        verbose_name = "Müşteri İlişkileri Süreci"
        verbose_name_plural = "Müşteri İlişkileri Süreçleri"

    def __str__(self):
        return f"{self.kod} - {self.musteri_adi} ({self.ad})"

    @property
    def tamamlanma_yuzdesi(self):
        toplam_adim = 11
        tamamlanan = self.adim_kayitlari.filter(durum__in=['TAMAMLANDI', 'PAS_GECILDI']).count()
        return int((tamamlanan / toplam_adim) * 100)

    @property
    def guncel_adim(self):
        return self.adim_kayitlari.filter(adim__adim_no=self.guncel_adim_no).first()


class MusteriIliskileriAdimKaydi(models.Model):
    DURUM_CHOICES = [
        ('BEKLIYOR', 'Bekliyor'),
        ('DEVAM_EDIYOR', 'Devam Ediyor / Aktif'),
        ('TAMAMLANDI', 'Tamamlandı (Onaylandı)'),
        ('UYGUNSUZLUK_ACILDI', 'Uygunsuzluk Yönetimi Süreci Başlatıldı'),
        ('PAS_GECILDI', 'Pas Geçildi / Muaf'),
    ]

    surec = models.ForeignKey(MusteriIliskileriSureci, on_delete=models.CASCADE, related_name='adim_kayitlari', verbose_name="Müşteri İlişkileri Süreci")
    adim = models.ForeignKey(MusteriIliskileriAdimTanimi, on_delete=models.PROTECT, verbose_name="Süreç Adımı")
    durum = models.CharField(max_length=30, choices=DURUM_CHOICES, default='BEKLIYOR', verbose_name="Durum")
    
    tamamlayan = models.CharField(max_length=100, blank=True, null=True, verbose_name="İşlemi Yapan")
    tamamlanma_tarihi = models.DateTimeField(blank=True, null=True, verbose_name="Tamamlanma Tarihi")
    
    karar_sonucu = models.CharField(max_length=100, blank=True, null=True, verbose_name="Verilen Karar (OK / NOK)")
    notlar = models.TextField(blank=True, null=True, verbose_name="Adım Notları / Değerlendirme / Aksiyon")
    dokuman_referansi = models.CharField(max_length=255, blank=True, null=True, verbose_name="Doküman Linki / Form No")

    class Meta:
        ordering = ['adim__adim_no']
        unique_together = ('surec', 'adim')
        verbose_name = "Müşteri İlişkileri Adım Kaydı"
        verbose_name_plural = "Müşteri İlişkileri Adım Kayıtları"

    def __str__(self):
        return f"{self.surec.kod} - Adım {self.adim.adim_no} ({self.get_durum_display()})"


class MusteriIliskileriGecmisLog(models.Model):
    surec = models.ForeignKey(MusteriIliskileriSureci, on_delete=models.CASCADE, related_name='tarihce_kayitlari', verbose_name="Müşteri İlişkileri Süreci")
    islem = models.CharField(max_length=255, verbose_name="Yapılan İşlem")
    detay = models.TextField(blank=True, null=True, verbose_name="İşlem Detayı")
    yapan = models.CharField(max_length=100, default='Sistem', verbose_name="İşlemi Yapan")
    tarih = models.DateTimeField(default=timezone.now, verbose_name="İşlem Tarihi")

    class Meta:
        ordering = ['-tarih']
        verbose_name = "Müşteri İlişkileri Geçmiş Logu"
        verbose_name_plural = "Müşteri İlişkileri Geçmiş Logları"

    def __str__(self):
        return f"{self.surec.kod} - {self.islem} ({self.tarih.strftime('%d.%m.%Y %H:%M')})"


# ==============================================================================
# ÜRÜN TEKLİF SÜRECİ (15 ADIM) MODELLERİ
# ==============================================================================

class UrunTeklifAdimTanimi(models.Model):
    """
    15 Adımlık Ürün Teklif Süreci Master Verisi
    """
    adim_no = models.PositiveSmallIntegerField(unique=True, verbose_name="Adım Numarası")
    baslik = models.CharField(max_length=255, verbose_name="Süreç Adımı Başlığı")
    faaliyet_tanimi = models.TextField(verbose_name="Faaliyet Tanımı")
    sorumlular = models.TextField(verbose_name="Sorumlular")
    ilgili_dokumanlar = models.TextField(verbose_name="İlgili Dokümanlar", blank=True, null=True)
    karar_adimi_mi = models.BooleanField(default=False, verbose_name="Karar / Kriter Adımı mı?")

    FAZ_CHOICES = [
        ('FAZ1', 'Faz 1: Fiyat Stratejisi & Yönetim Onayı (Adım 1-3)'),
        ('FAZ2', 'Faz 2: RFQ Alımı, Maliyet Analizi & Teklif Değerlendirme (Adım 4-8)'),
        ('FAZ3', 'Faz 3: Teklif İletimi, Müşteri Geri Bildirimi & Revizyon (Adım 9-12)'),
        ('FAZ4', 'Faz 4: Fiyat Stratejisi Kontrolü, Kapanış & Sürekli İyileştirme (Adım 13-15)'),
    ]
    faz = models.CharField(max_length=10, choices=FAZ_CHOICES, default='FAZ1', verbose_name="Süreç Fazı")

    class Meta:
        ordering = ['adim_no']
        verbose_name = "Ürün Teklif Adım Tanımı"
        verbose_name_plural = "Ürün Teklif Adım Tanımları"

    def __str__(self):
        return f"{self.adim_no}. {self.baslik}"

    @property
    def dokuman_listesi(self):
        if not self.ilgili_dokumanlar:
            return []
        items = []
        for line in self.ilgili_dokumanlar.replace('\r\n', '\n').split('\n'):
            for part in line.split(','):
                cleaned = part.strip()
                if cleaned:
                    items.append(cleaned)
        return items


class UrunTeklifSureci(models.Model):
    """
    Ürün Teklif Süreci Takip Kaydı (15 Adım)
    """
    DURUM_CHOICES = [
        ('DEVAM_EDIYOR', 'Devam Ediyor'),
        ('YONETIM_ONAYINDA', 'Yönetim Onayında'),
        ('MUSTERIYE_ILETILDI', 'Teklif Müşteriye İletildi'),
        ('REVIZYONDA', 'Revizyon Aşamasında'),
        ('BASARIYLA_TAMAMLANDI', 'Başarıyla Tamamlandı'),
        ('OLUMSUZ_KAPATILDI', 'Olumsuz Kapatıldı'),
    ]

    kod = models.CharField(max_length=50, unique=True, verbose_name="Teklif Süreç Kodu")
    ad = models.CharField(max_length=200, verbose_name="Teklif / Proje Başlığı")
    musteri_adi = models.CharField(max_length=150, verbose_name="Müşteri / Firma Adı")
    musteri_karti = models.ForeignKey(MusteriKarti, on_delete=models.SET_NULL, null=True, blank=True, related_name="urun_teklif_surecleri", verbose_name="Müşteri Portföy Kartı")
    
    donem = models.CharField(max_length=50, default="2026 Yıllık", verbose_name="Dönem / Yıl")
    ilgili_fabrika = models.CharField(max_length=100, choices=PazarlamaProjesi.FABRIKA_CHOICES, default='PRESHANE', verbose_name="İlgili Fabrika")
    urun_grubu = models.CharField(max_length=100, choices=PazarlamaProjesi.URUN_GRUBU_CHOICES, default='Metal Parca & Sac', verbose_name="Ürün Grubu")
    
    sorumlu_satis_analiz_uzmani = models.CharField(max_length=100, default='METİN YAVAŞ', verbose_name="Satış Analiz Uzmanı")
    sorumlu_satis_uzmani = models.CharField(max_length=100, default='BUSE NUR BALTACIOĞLU', verbose_name="Satış Uzmanı")
    sorumlu_satis_yoneticisi = models.CharField(max_length=100, default='ONUR TUNCER', verbose_name="Satış Yöneticisi")
    
    durum = models.CharField(max_length=30, choices=DURUM_CHOICES, default='DEVAM_EDIYOR', verbose_name="Teklif Durumu")
    guncel_adim_no = models.PositiveSmallIntegerField(default=1, verbose_name="Güncel Adım No")
    
    teklif_tutari = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="Toplam Teklif Tutarı / Ciro (EUR)")
    aciklama = models.TextField(blank=True, null=True, verbose_name="Süreç Özeti / Notlar")
    
    olusturma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    guncelleme_tarihi = models.DateTimeField(auto_now=True, verbose_name="Son Güncelleme")

    class Meta:
        ordering = ['-guncelleme_tarihi']
        verbose_name = "Ürün Teklif Süreci"
        verbose_name_plural = "Ürün Teklif Süreçleri"

    def __str__(self):
        return f"{self.kod} - {self.musteri_adi} ({self.ad})"

    @property
    def tamamlanma_yuzdesi(self):
        toplam_adim = 15
        tamamlanan = self.adim_kayitlari.filter(durum__in=['TAMAMLANDI', 'PAS_GECILDI']).count()
        return int((tamamlanan / toplam_adim) * 100)

    @property
    def guncel_adim(self):
        return self.adim_kayitlari.filter(adim__adim_no=self.guncel_adim_no).first()


class UrunTeklifAdimKaydi(models.Model):
    DURUM_CHOICES = [
        ('BEKLIYOR', 'Bekliyor'),
        ('DEVAM_EDIYOR', 'Devam Ediyor / Aktif'),
        ('TAMAMLANDI', 'Tamamlandı (Onaylandı)'),
        ('REVIZYON_YONLENDIRILDI', 'Geriye Revizyona Gönderildi'),
        ('PAS_GECILDI', 'Pas Geçildi / Muaf'),
    ]

    surec = models.ForeignKey(UrunTeklifSureci, on_delete=models.CASCADE, related_name='adim_kayitlari', verbose_name="Ürün Teklif Süreci")
    adim = models.ForeignKey(UrunTeklifAdimTanimi, on_delete=models.PROTECT, verbose_name="Süreç Adımı")
    durum = models.CharField(max_length=30, choices=DURUM_CHOICES, default='BEKLIYOR', verbose_name="Durum")
    
    tamamlayan = models.CharField(max_length=100, blank=True, null=True, verbose_name="İşlemi Yapan")
    tamamlanma_tarihi = models.DateTimeField(blank=True, null=True, verbose_name="Tamamlanma Tarihi")
    
    karar_sonucu = models.CharField(max_length=100, blank=True, null=True, verbose_name="Verilen Karar (OK / NOK / EVET / HAYIR)")
    notlar = models.TextField(blank=True, null=True, verbose_name="Adım Notları / Değerlendirme / Aksiyon")
    dokuman_referansi = models.CharField(max_length=255, blank=True, null=True, verbose_name="Doküman Linki / Form No")

    class Meta:
        ordering = ['adim__adim_no']
        unique_together = ('surec', 'adim')
        verbose_name = "Ürün Teklif Adım Kaydı"
        verbose_name_plural = "Ürün Teklif Adım Kayıtları"

    def __str__(self):
        return f"{self.surec.kod} - Adım {self.adim.adim_no} ({self.get_durum_display()})"


class UrunTeklifGecmisLog(models.Model):
    surec = models.ForeignKey(UrunTeklifSureci, on_delete=models.CASCADE, related_name='tarihce_kayitlari', verbose_name="Ürün Teklif Süreci")
    islem = models.CharField(max_length=255, verbose_name="Yapılan İşlem")
    detay = models.TextField(blank=True, null=True, verbose_name="İşlem Detayı")
    yapan = models.CharField(max_length=100, default='Sistem', verbose_name="İşlemi Yapan")
    tarih = models.DateTimeField(default=timezone.now, verbose_name="İşlem Tarihi")

    class Meta:
        ordering = ['-tarih']
        verbose_name = "Ürün Teklif Geçmiş Logu"
        verbose_name_plural = "Ürün Teklif Geçmiş Logları"

    def __str__(self):
        return f"{self.surec.kod} - {self.islem} ({self.tarih.strftime('%d.%m.%Y %H:%M')})"


# ==============================================================================
# SÖZLEŞMENİN DEĞERLENDİRİLMESİ SÜRECİ (15 ADIM) MODELLERİ
# ==============================================================================

class SozlesmeAdimTanimi(models.Model):
    """
    15 Adımlık Sözleşmenin Değerlendirilmesi Süreci Master Verisi
    """
    adim_no = models.PositiveSmallIntegerField(unique=True, verbose_name="Adım Numarası")
    baslik = models.CharField(max_length=255, verbose_name="Süreç Adımı Başlığı")
    faaliyet_tanimi = models.TextField(verbose_name="Faaliyet Tanımı")
    sorumlular = models.TextField(verbose_name="Sorumlular")
    ilgili_dokumanlar = models.TextField(verbose_name="İlgili Dokümanlar", blank=True, null=True)
    karar_adimi_mi = models.BooleanField(default=False, verbose_name="Karar / Kriter Adımı mı?")

    FAZ_CHOICES = [
        ('FAZ1', 'Faz 1: Sözleşme Kabulü, Hukuki İnceleme & Uygunluk (Adım 1-4)'),
        ('FAZ2', 'Faz 2: Şartlar, Risk Değerlendirmesi & Yönetim Onayı (Adım 5-8)'),
        ('FAZ3', 'Faz 3: Müşteri Bilgilendirmesi, Müzakere & Karşılıklı İmza (Adım 9-12)'),
        ('FAZ4', 'Faz 4: EYS Entegrasyonu, Kapanış & Öğrenilmiş Dersler (Adım 13-15)'),
    ]
    faz = models.CharField(max_length=10, choices=FAZ_CHOICES, default='FAZ1', verbose_name="Süreç Fazı")

    class Meta:
        ordering = ['adim_no']
        verbose_name = "Sözleşme Adım Tanımı"
        verbose_name_plural = "Sözleşme Adım Tanımları"

    def __str__(self):
        return f"{self.adim_no}. {self.baslik}"

    @property
    def dokuman_listesi(self):
        if not self.ilgili_dokumanlar:
            return []
        items = []
        for line in self.ilgili_dokumanlar.replace('\r\n', '\n').split('\n'):
            for part in line.split(','):
                cleaned = part.strip()
                if cleaned:
                    items.append(cleaned)
        return items


class SozlesmeSureci(models.Model):
    """
    Sözleşmenin Değerlendirilmesi Süreci Takip Kaydı (15 Adım)
    """
    SOZLESME_TIPI_CHOICES = [
        ('GIZLILIK', 'Gizlilik Sözleşmesi (NDA)'),
        ('KALITE', 'Kalite Güvence Anlaşması (QAA)'),
        ('PLANLAMA_LOJISTIK', 'Planlama & Lojistik Sözleşmesi'),
        ('SURDURULEBILIRLIK', 'Sürdürülebilirlik & Çevre Protokolü'),
        ('SATIS', 'Genel Satış / Tedarik Çerçeve Sözleşmesi'),
        ('MAKINE_KALIP', 'Makine, Kalıp & Ekipman Yatırım Sözleşmesi'),
        ('DIGER', 'Diğer Ticari Sözleşmeler'),
    ]

    DURUM_CHOICES = [
        ('DEVAM_EDIYOR', 'Devam Ediyor'),
        ('HUKUKI_INCELEMEDE', 'Hukuki İncelemede'),
        ('YONETIM_ONAYINDA', 'Yönetim Onayında'),
        ('MUSTERI_MUZAKERESINDE', 'Müşteri Müzakeresinde'),
        ('BASARIYLA_TAMAMLANDI', 'Başarıyla İmzalandı & Tamamlandı'),
        ('OLUMSUZ_KAPATILDI', 'Mutabakat Sağlanamadı / İptal'),
    ]

    kod = models.CharField(max_length=50, unique=True, verbose_name="Sözleşme Süreç Kodu")
    ad = models.CharField(max_length=200, verbose_name="Sözleşme Konusu / Başlığı")
    musteri_adi = models.CharField(max_length=150, verbose_name="Müşteri / Firma Adı")
    musteri_karti = models.ForeignKey(MusteriKarti, on_delete=models.SET_NULL, null=True, blank=True, related_name="sozlesme_surecleri", verbose_name="Müşteri Portföy Kartı")
    
    sozlesme_tipi = models.CharField(max_length=40, choices=SOZLESME_TIPI_CHOICES, default='SATIS', verbose_name="Sözleşme Tipi")
    donem = models.CharField(max_length=50, default="2026 Yıllık", verbose_name="Dönem / Yıl")
    ilgili_fabrika = models.CharField(max_length=100, choices=PazarlamaProjesi.FABRIKA_CHOICES, default='PRESHANE', verbose_name="İlgili Fabrika")
    
    baslangic_tarihi = models.DateField(null=True, blank=True, verbose_name="Başlangıç Tarihi")
    bitis_tarihi = models.DateField(null=True, blank=True, verbose_name="Bitiş Tarihi")

    sorumlu_satis_uzmani = models.CharField(max_length=100, default='BUSE NUR BALTACIOĞLU', verbose_name="Satış Uzmanı")
    sorumlu_satis_yoneticisi = models.CharField(max_length=100, default='ONUR TUNCER', verbose_name="Satış Yöneticisi")
    sorumlu_fabrika_muduru = models.CharField(max_length=100, default='MUHARREM FURKAN TARHAN', verbose_name="Fabrika Müdürü")
    sorumlu_hukuk = models.CharField(max_length=100, default='Hukuk Müşaviri', verbose_name="Şirket Hukuk Müşaviri / Avukat")
    
    durum = models.CharField(max_length=30, choices=DURUM_CHOICES, default='DEVAM_EDIYOR', verbose_name="Sözleşme Durumu")
    guncel_adim_no = models.PositiveSmallIntegerField(default=1, verbose_name="Güncel Adım No")
    
    aciklama = models.TextField(blank=True, null=True, verbose_name="Süreç Özeti / Başlangıç Notları")
    
    olusturma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    guncelleme_tarihi = models.DateTimeField(auto_now=True, verbose_name="Son Güncelleme")

    class Meta:
        ordering = ['-guncelleme_tarihi']
        verbose_name = "Sözleşme Değerlendirme Süreci"
        verbose_name_plural = "Sözleşme Değerlendirme Süreçleri"

    def __str__(self):
        return f"{self.kod} - {self.musteri_adi} ({self.ad})"

    @property
    def tamamlanma_yuzdesi(self):
        toplam_adim = 15
        tamamlanan = self.adim_kayitlari.filter(durum__in=['TAMAMLANDI', 'PAS_GECILDI']).count()
        return int((tamamlanan / toplam_adim) * 100)

    @property
    def guncel_adim(self):
        return self.adim_kayitlari.filter(adim__adim_no=self.guncel_adim_no).first()


class SozlesmeAdimKaydi(models.Model):
    DURUM_CHOICES = [
        ('BEKLIYOR', 'Bekliyor'),
        ('DEVAM_EDIYOR', 'Devam Ediyor / Aktif'),
        ('TAMAMLANDI', 'Tamamlandı (Onaylandı)'),
        ('MUZAKEREYE_YONLENDIRILDI', 'Müşteri Müzakeresine Yönlendirildi'),
        ('PAS_GECILDI', 'Pas Geçildi / Muaf'),
    ]

    surec = models.ForeignKey(SozlesmeSureci, on_delete=models.CASCADE, related_name='adim_kayitlari', verbose_name="Sözleşme Süreci")
    adim = models.ForeignKey(SozlesmeAdimTanimi, on_delete=models.PROTECT, verbose_name="Süreç Adımı")
    durum = models.CharField(max_length=30, choices=DURUM_CHOICES, default='BEKLIYOR', verbose_name="Durum")
    
    tamamlayan = models.CharField(max_length=100, blank=True, null=True, verbose_name="İşlemi Yapan")
    tamamlanma_tarihi = models.DateTimeField(blank=True, null=True, verbose_name="Tamamlanma Tarihi")
    
    karar_sonucu = models.CharField(max_length=100, blank=True, null=True, verbose_name="Verilen Karar (OK / NOK)")
    notlar = models.TextField(blank=True, null=True, verbose_name="Adım Notları / Değerlendirme / Hukuki Görüş")
    dokuman_referansi = models.CharField(max_length=255, blank=True, null=True, verbose_name="Doküman Linki / Form No")

    class Meta:
        ordering = ['adim__adim_no']
        unique_together = ('surec', 'adim')
        verbose_name = "Sözleşme Adım Kaydı"
        verbose_name_plural = "Sözleşme Adım Kayıtları"

    def __str__(self):
        return f"{self.surec.kod} - Adım {self.adim.adim_no} ({self.get_durum_display()})"


class SozlesmeGecmisLog(models.Model):
    surec = models.ForeignKey(SozlesmeSureci, on_delete=models.CASCADE, related_name='tarihce_kayitlari', verbose_name="Sözleşme Süreci")
    islem = models.CharField(max_length=255, verbose_name="Yapılan İşlem")
    detay = models.TextField(blank=True, null=True, verbose_name="İşlem Detayı")
    yapan = models.CharField(max_length=100, default='Sistem', verbose_name="İşlemi Yapan")
    tarih = models.DateTimeField(default=timezone.now, verbose_name="İşlem Tarihi")

    class Meta:
        ordering = ['-tarih']
        verbose_name = "Sözleşme Geçmiş Logu"
        verbose_name_plural = "Sözleşme Geçmiş Logları"

    def __str__(self):
        return f"{self.surec.kod} - {self.islem} ({self.tarih.strftime('%d.%m.%Y %H:%M')})"


# ==============================================================================
# YENİ ÜRÜN DEVREYE ALMA SÜRECİ (45 ADIM - APQP / NPI) MODELLERİ
# ==============================================================================

class YeniUrunAdimTanimi(models.Model):
    """
    45 Adımlık Yeni Ürün Devreye Alma Süreci Master Verisi
    """
    adim_no = models.PositiveSmallIntegerField(unique=True, verbose_name="Adım Numarası")
    baslik = models.CharField(max_length=255, verbose_name="Süreç Adımı Başlığı")
    faaliyet_tanimi = models.TextField(verbose_name="Faaliyet Tanımı")
    sorumlular = models.TextField(verbose_name="Sorumlular")
    ilgili_dokumanlar = models.TextField(verbose_name="İlgili Dokümanlar", blank=True, null=True)
    karar_adimi_mi = models.BooleanField(default=False, verbose_name="Karar / Onay Adımı mı?")

    FAZ_CHOICES = [
        ('FAZ1', 'Faz 1: Talep, Ön Değerlendirme & Fizibilite (Adım 1-12)'),
        ('FAZ2', 'Faz 2: Proje Başlatma, Planlama & Tedarik Hazırlığı (Adım 13-19)'),
        ('FAZ3', 'Faz 3: Numune Üretimi, Doğrulama & Müşteri Onayı (Adım 20-30)'),
        ('FAZ4', 'Faz 4: Ön Seri Üretim, MSA, Yeterlilik & PPAP (Adım 31-39)'),
        ('FAZ5', 'Faz 5: Kapanış, Seri Üretime Geçiş & İyileştirme (Adım 40-45)'),
    ]
    faz = models.CharField(max_length=10, choices=FAZ_CHOICES, default='FAZ1', verbose_name="Süreç Fazı")

    class Meta:
        ordering = ['adim_no']
        verbose_name = "Yeni Ürün Adım Tanımı"
        verbose_name_plural = "Yeni Ürün Adım Tanımları"

    def __str__(self):
        return f"{self.adim_no}. {self.baslik}"

    @property
    def dokuman_listesi(self):
        if not self.ilgili_dokumanlar:
            return []
        items = []
        for line in self.ilgili_dokumanlar.replace('\r\n', '\n').split('\n'):
            for part in line.split(','):
                cleaned = part.strip()
                if cleaned:
                    items.append(cleaned)
        return items


class YeniUrunDevreyeAlmaSureci(models.Model):
    """
    Yeni Ürün Devreye Alma Süreci Takip Kaydı (45 Adım)
    """
    DURUM_CHOICES = [
        ('DEVAM_EDIYOR', 'Devam Ediyor'),
        ('UYGUNSUZLUK_YONETIMINDE', 'DÖF / Uygunsuzluk Sürecinde'),
        ('REVIZYONDA', 'Revizyon Aşamasında'),
        ('BASARIYLA_TAMAMLANDI', 'Başarıyla Seri Üretime Alındı & Kapatıldı'),
        ('OLUMSUZ_KAPATILDI', 'Müşteri Onayı Alınamadı / Kapatıldı'),
        ('ASKIDA', 'Askıda / Beklemede'),
    ]

    URUN_GRUBU_CHOICES = [
        ('Kondanser & Sogutma', 'Kondanser & Soğutma Grubu'),
        ('Kondenser & Sogutma', 'Kondanser & Soğutma Grubu (Eski)'),
        ('Metal Parca & Sac', 'Metal Parça & Sac Şekillendirme'),
        ('Kablo Grubu', 'Kablo Grubu & Demetleri'),
        ('Kalıp & Fikstür', 'Kalıp, Fikstür & Aparat'),
        ('Montaj ve Kaynak', 'Montaj ve Kaynak'),
        ('Plastik Enjeksiyon', 'Plastik Enjeksiyon'),
        ('Batarya & EV Bilesenleri', 'Batarya & EV Bileşenleri'),
        ('Genel / Diger', 'Genel / Diğer'),
    ]

    FABRIKA_CHOICES = [
        ('PRESHANE', 'PRESHANE'),
        ('KALIPHANE', 'KALIPHANE'),
        ('CERKEZKOY', 'CERKEZKOY'),
        ('KABLOGR', 'KABLOGR'),
        ('KONDANSER', 'KONDANSER'),
        ('MANISA ORTAK', 'MANISA ORTAK'),
    ]

    kod = models.CharField(max_length=50, unique=True, verbose_name="NPI Proje Kodu")
    ad = models.CharField(max_length=200, verbose_name="Ürün / Proje Adı")
    musteri_adi = models.CharField(max_length=150, verbose_name="Müşteri / Firma Adı")
    musteri_karti = models.ForeignKey(MusteriKarti, on_delete=models.SET_NULL, null=True, blank=True, related_name="yeni_urun_surecleri", verbose_name="Müşteri Portföy Kartı")

    urun_grubu = models.CharField(max_length=100, choices=URUN_GRUBU_CHOICES, default='Kondanser & Sogutma', verbose_name="Ürün Grubu")
    urun_grubu_karti = models.ForeignKey(UrunGrubuKarti, on_delete=models.SET_NULL, null=True, blank=True, related_name="yeni_urun_surecleri", verbose_name="İlişkili Ürün Grubu Kartı")

    ilgili_fabrika = models.CharField(max_length=100, choices=FABRIKA_CHOICES, default='PRESHANE', verbose_name="Üretim Fabrikası / Ana Departman")

    parca_kodu = models.CharField(max_length=100, blank=True, null=True, verbose_name="Müşteri / Teleset Parça Kodu")
    hedef_seri_uretim_tarihi = models.DateField(null=True, blank=True, verbose_name="Hedef Seri Üretime Geçiş Tarihi")
    yillik_hedef_adet = models.PositiveIntegerField(null=True, blank=True, verbose_name="Yıllık Hedef Adet")

    sorumlu_proje_lideri = models.CharField(max_length=100, default='BUSE NUR BALTACIOĞLU', verbose_name="Proje Sorumlusu")
    sorumlu_fabrika_muduru = models.CharField(max_length=100, default='ONUR TUNCER', verbose_name="Fabrika Müdürü")
    sorumlu_satis_analiz = models.CharField(max_length=100, default='MUHARREM FURKAN TARHAN', verbose_name="Satış-Analiz Sorumlusu")
    sorumlu_kalite = models.CharField(max_length=100, default='METİN YAVAŞ', verbose_name="Kalite Sorumlusu")

    durum = models.CharField(max_length=35, choices=DURUM_CHOICES, default='DEVAM_EDIYOR', verbose_name="Süreç Durumu")
    guncel_adim_no = models.PositiveSmallIntegerField(default=1, verbose_name="Güncel Adım No")

    aciklama = models.TextField(blank=True, null=True, verbose_name="Proje Kapsamı & Notlar")

    olusturma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    guncelleme_tarihi = models.DateTimeField(auto_now=True, verbose_name="Son Güncelleme")

    class Meta:
        ordering = ['-guncelleme_tarihi']
        verbose_name = "Yeni Ürün Devreye Alma Süreci"
        verbose_name_plural = "Yeni Ürün Devreye Alma Süreçleri"

    def __str__(self):
        return f"{self.kod} - {self.musteri_adi} ({self.ad})"

    @property
    def tamamlanma_yuzdesi(self):
        toplam_adim = 45
        tamamlanan = self.adim_kayitlari.filter(durum__in=['TAMAMLANDI', 'PAS_GECILDI']).count()
        return int((tamamlanan / toplam_adim) * 100)

    @property
    def guncel_adim(self):
        return self.adim_kayitlari.filter(adim__adim_no=self.guncel_adim_no).first()


class YeniUrunAdimKaydi(models.Model):
    DURUM_CHOICES = [
        ('BEKLIYOR', 'Bekliyor'),
        ('DEVAM_EDIYOR', 'Devam Ediyor / Aktif'),
        ('TAMAMLANDI', 'Tamamlandı (Onaylandı)'),
        ('REVIZYON_YONLENDIRILDI', 'Geriye Revizyona Gönderildi'),
        ('PAS_GECILDI', 'Pas Geçildi / Muaf'),
    ]

    surec = models.ForeignKey(YeniUrunDevreyeAlmaSureci, on_delete=models.CASCADE, related_name='adim_kayitlari', verbose_name="Yeni Ürün Süreci")
    adim = models.ForeignKey(YeniUrunAdimTanimi, on_delete=models.PROTECT, verbose_name="Süreç Adımı")
    durum = models.CharField(max_length=30, choices=DURUM_CHOICES, default='BEKLIYOR', verbose_name="Durum")

    tamamlayan = models.CharField(max_length=100, blank=True, null=True, verbose_name="İşlemi Yapan")
    tamamlanma_tarihi = models.DateTimeField(blank=True, null=True, verbose_name="Tamamlanma Tarihi")

    karar_sonucu = models.CharField(max_length=100, blank=True, null=True, verbose_name="Verilen Karar (OK / NOK / EVET / HAYIR)")
    notlar = models.TextField(blank=True, null=True, verbose_name="Adım Notları / Değerlendirme / Teknik Çıktı")
    dokuman_referansi = models.CharField(max_length=255, blank=True, null=True, verbose_name="Doküman Linki / Form No")

    class Meta:
        ordering = ['adim__adim_no']
        unique_together = ('surec', 'adim')
        verbose_name = "Yeni Ürün Adım Kaydı"
        verbose_name_plural = "Yeni Ürün Adım Kayıtları"

    def __str__(self):
        return f"{self.surec.kod} - Adım {self.adim.adim_no} ({self.get_durum_display()})"


class YeniUrunGecmisLog(models.Model):
    surec = models.ForeignKey(YeniUrunDevreyeAlmaSureci, on_delete=models.CASCADE, related_name='tarihce_kayitlari', verbose_name="Yeni Ürün Süreci")
    islem = models.CharField(max_length=255, verbose_name="Yapılan İşlem")
    detay = models.TextField(blank=True, null=True, verbose_name="İşlem Detayı")
    yapan = models.CharField(max_length=100, default='Sistem', verbose_name="İşlemi Yapan")
    tarih = models.DateTimeField(default=timezone.now, verbose_name="İşlem Tarihi")

    class Meta:
        ordering = ['-tarih']
        verbose_name = "Yeni Ürün Geçmiş Logu"
        verbose_name_plural = "Yeni Ürün Geçmiş Logları"

    def __str__(self):
        return f"{self.surec.kod} - {self.islem} ({self.tarih.strftime('%d.%m.%Y %H:%M')})"


# ==============================================================================
# MÜHENDİSLİK DEĞİŞİKLİĞİ SÜRECİ (34 ADIM - ECO / ECM) MODELLERİ
# ==============================================================================

class MuhendislikDegisikligiAdimTanimi(models.Model):
    """
    34 Adımlık Mühendislik Değişikliği Süreci Master Verisi
    """
    adim_no = models.PositiveSmallIntegerField(unique=True, verbose_name="Adım Numarası")
    baslik = models.CharField(max_length=255, verbose_name="Süreç Adımı Başlığı")
    faaliyet_tanimi = models.TextField(verbose_name="Faaliyet Tanımı")
    sorumlular = models.TextField(verbose_name="Sorumlular")
    ilgili_dokumanlar = models.TextField(verbose_name="İlgili Dokümanlar", blank=True, null=True)
    karar_adimi_mi = models.BooleanField(default=False, verbose_name="Karar / Kriter Adımı mı?")

    FAZ_CHOICES = [
        ('FAZ1', 'Faz 1: Değişiklik Talebi, Değerlendirme, Maliyet & Müşteri Onayı (Adım 1-11)'),
        ('FAZ2', 'Faz 2: Teknik Hazırlık, BOM, Proses & Numune Üretimi (Adım 12-18)'),
        ('FAZ3', 'Faz 3: Numune ISIR Ölçümü, Müşteri Onayı & Ön Seri Üretim (Adım 19-27)'),
        ('FAZ4', 'Faz 4: Seri Üretime Geçiş, Dokümantasyon, Kapanış & İyileştirme (Adım 28-34)'),
    ]
    faz = models.CharField(max_length=10, choices=FAZ_CHOICES, default='FAZ1', verbose_name="Süreç Fazı")

    class Meta:
        ordering = ['adim_no']
        verbose_name = "Mühendislik Değişikliği Adım Tanımı"
        verbose_name_plural = "Mühendislik Değişikliği Adım Tanımları"

    def __str__(self):
        return f"{self.adim_no}. {self.baslik}"

    @property
    def dokuman_listesi(self):
        if not self.ilgili_dokumanlar:
            return []
        items = []
        for line in self.ilgili_dokumanlar.replace('\r\n', '\n').split('\n'):
            for part in line.split(','):
                cleaned = part.strip()
                if cleaned and cleaned != '-':
                    items.append(cleaned)
        return items


class MuhendislikDegisikligiSureci(models.Model):
    """
    Mühendislik Değişikliği Süreci Takip Kaydı (34 Adım)
    """
    DEGISIKLIK_NEDENI_CHOICES = [
        ('MUSTERI_TALEBI', 'Müşteri Revizyon Talebi'),
        ('MALIYET_IYILESTIRME', 'Maliyet İyileştirme & VAVE'),
        ('KALITE_IYILESTIRME', 'Kalite & DÖF Kaynaklı İyileştirme'),
        ('HAMMADDE_TEDARIK', 'Hammadde / Tedarikçi Değişikliği'),
        ('IC_PROSES', 'İç Proses & Makine Parkuru İyileştirme'),
        ('STANDART_MEVZUAT', 'Standart / Mevzuat Değişikliği'),
    ]

    DURUM_CHOICES = [
        ('DEVAM_EDIYOR', 'Devam Ediyor'),
        ('YENI_URUN_SURECINE_AKTARILDI', 'Yeni Ürün Devreye Alma Sürecine Aktarıldı'),
        ('REVIZYONDA', 'Revizyon Aşamasında'),
        ('BASARIYLA_TAMAMLANDI', 'Başarıyla Seri Üretime Alındı & Kapatıldı'),
        ('OLUMSUZ_KAPATILDI', 'İptal / Olumsuz Kapatıldı'),
    ]

    kod = models.CharField(max_length=50, unique=True, verbose_name="Değişiklik Kodu (ECO)")
    ad = models.CharField(max_length=200, verbose_name="Değişiklik Konusu / Başlığı")
    musteri_adi = models.CharField(max_length=150, verbose_name="Müşteri / Firma Adı")
    musteri_karti = models.ForeignKey(MusteriKarti, on_delete=models.SET_NULL, null=True, blank=True, related_name="muhendislik_degisiklikleri", verbose_name="Müşteri Portföy Kartı")
    ana_proje = models.ForeignKey('AnaProje', on_delete=models.SET_NULL, null=True, blank=True, related_name="eco_iterasyonlari", verbose_name="Bağlı Ana Proje")

    parca_kodu = models.CharField(max_length=100, blank=True, null=True, verbose_name="Parça Kodu / No")
    revizyon_no = models.CharField(max_length=50, default="Rev.01", verbose_name="Revizyon No")
    degisiklik_nedeni = models.CharField(max_length=40, choices=DEGISIKLIK_NEDENI_CHOICES, default='MUSTERI_TALEBI', verbose_name="Değişiklik Nedeni")

    urun_grubu = models.CharField(max_length=100, choices=PazarlamaProjesi.URUN_GRUBU_CHOICES, default='Metal Parca & Sac', verbose_name="Ürün Grubu")
    ilgili_fabrika = models.CharField(max_length=100, choices=PazarlamaProjesi.FABRIKA_CHOICES, default='PRESHANE', verbose_name="İlgili Fabrika")

    hedef_tamamlanma_tarihi = models.DateField(null=True, blank=True, verbose_name="Hedef Tamamlanma Tarihi")

    sorumlu_proje_sorumlusu = models.CharField(max_length=100, default='BUSE NUR BALTACIOĞLU', verbose_name="Proje Sorumlusu (R)")
    sorumlu_fabrika_muduru = models.CharField(max_length=100, default='ONUR TUNCER', verbose_name="Fabrika Müdürü (A)")
    sorumlu_satis_analiz = models.CharField(max_length=100, default='METİN YAVAŞ', verbose_name="Satış-Analiz Sorumlusu (C)")
    sorumlu_kalite = models.CharField(max_length=100, default='MUHARREM FURKAN TARHAN', verbose_name="Kalite Sorumlusu (C)")

    durum = models.CharField(max_length=40, choices=DURUM_CHOICES, default='DEVAM_EDIYOR', verbose_name="Süreç Durumu")
    guncel_adim_no = models.PositiveSmallIntegerField(default=1, verbose_name="Güncel Adım No")

    aciklama = models.TextField(blank=True, null=True, verbose_name="Değişiklik Özeti / Başlangıç Notları")

    olusturma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    guncelleme_tarihi = models.DateTimeField(auto_now=True, verbose_name="Son Güncelleme")

    class Meta:
        ordering = ['-guncelleme_tarihi']
        verbose_name = "Mühendislik Değişikliği Süreci"
        verbose_name_plural = "Mühendislik Değişikliği Süreçleri"

    def __str__(self):
        return f"{self.kod} - {self.musteri_adi} ({self.ad})"

    @property
    def tamamlanma_yuzdesi(self):
        toplam_adim = 34
        tamamlanan = self.adim_kayitlari.filter(durum__in=['TAMAMLANDI', 'PAS_GECILDI']).count()
        return int((tamamlanan / toplam_adim) * 100)

    @property
    def guncel_adim(self):
        return self.adim_kayitlari.filter(adim__adim_no=self.guncel_adim_no).first()


class MuhendislikDegisikligiAdimKaydi(models.Model):
    DURUM_CHOICES = [
        ('BEKLIYOR', 'Bekliyor'),
        ('DEVAM_EDIYOR', 'Devam Ediyor / Aktif'),
        ('TAMAMLANDI', 'Tamamlandı (Onaylandı)'),
        ('REVIZYON_YONLENDIRILDI', 'Geriye Revizyona Gönderildi'),
        ('PAS_GECILDI', 'Pas Geçildi / Muaf'),
    ]

    surec = models.ForeignKey(MuhendislikDegisikligiSureci, on_delete=models.CASCADE, related_name='adim_kayitlari', verbose_name="Mühendislik Değişikliği Süreci")
    adim = models.ForeignKey(MuhendislikDegisikligiAdimTanimi, on_delete=models.PROTECT, verbose_name="Süreç Adımı")
    durum = models.CharField(max_length=30, choices=DURUM_CHOICES, default='BEKLIYOR', verbose_name="Durum")

    tamamlayan = models.CharField(max_length=100, blank=True, null=True, verbose_name="İşlemi Yapan")
    tamamlanma_tarihi = models.DateTimeField(blank=True, null=True, verbose_name="Tamamlanma Tarihi")

    karar_sonucu = models.CharField(max_length=150, blank=True, null=True, verbose_name="Verilen Karar")
    notlar = models.TextField(blank=True, null=True, verbose_name="Adım Notları / Değerlendirme / Teknik Çıktı")
    dokuman_referansi = models.CharField(max_length=255, blank=True, null=True, verbose_name="Doküman Linki / Form No")

    class Meta:
        ordering = ['adim__adim_no']
        unique_together = ('surec', 'adim')
        verbose_name = "Mühendislik Değişikliği Adım Kaydı"
        verbose_name_plural = "Mühendislik Değişikliği Adım Kayıtları"

    def __str__(self):
        return f"{self.surec.kod} - Adım {self.adim.adim_no} ({self.get_durum_display()})"


class MuhendislikDegisikligiGecmisLog(models.Model):
    surec = models.ForeignKey(MuhendislikDegisikligiSureci, on_delete=models.CASCADE, related_name='tarihce_kayitlari', verbose_name="Mühendislik Değişikliği Süreci")
    islem = models.CharField(max_length=255, verbose_name="Yapılan İşlem")
    detay = models.TextField(blank=True, null=True, verbose_name="İşlem Detayı")
    yapan = models.CharField(max_length=100, default='Sistem', verbose_name="İşlemi Yapan")
    tarih = models.DateTimeField(default=timezone.now, verbose_name="İşlem Tarihi")

    class Meta:
        ordering = ['-tarih']
        verbose_name = "Mühendislik Değişikliği Geçmiş Logu"
        verbose_name_plural = "Mühendislik Değişikliği Geçmiş Logları"

    def __str__(self):
        return f"{self.surec.kod} - {self.islem} ({self.tarih.strftime('%d.%m.%Y %H:%M')})"


# ==============================================================================
# 7. PROTOTİP SÜRECİ (23 ADIM - PROTOTYPE MANAGEMENT) MODELLERİ
# ==============================================================================

class PrototipAdimTanimi(models.Model):
    """
    23 Adımlık Prototip Süreci Master Verisi
    """
    adim_no = models.PositiveSmallIntegerField(unique=True, verbose_name="Adım Numarası")
    baslik = models.CharField(max_length=255, verbose_name="Süreç Adımı Başlığı")
    faaliyet_tanimi = models.TextField(verbose_name="Faaliyet Tanımı")
    sorumlular = models.TextField(verbose_name="Sorumlular")
    ilgili_dokumanlar = models.TextField(verbose_name="İlgili Dokümanlar", blank=True, null=True)
    karar_adimi_mi = models.BooleanField(default=False, verbose_name="Karar / Kriter Adımı mı?")

    FAZ_CHOICES = [
        ('FAZ1', 'Faz 1: Talep, Ön Değerlendirme & Müşteri Başlangıç Onayı (Adım 1-9)'),
        ('FAZ2', 'Faz 2: Teknik Hazırlık, Tedarik & ERP Numune BOM (Adım 10-14)'),
        ('FAZ3', 'Faz 3: Prototip İmalatı, ISIR Ölçümü & Müşteri Doğrulaması (Adım 15-20)'),
        ('FAZ4', 'Faz 4: Reçete Kontrolü, Kapanış & Öğrenilmiş Dersler (Adım 21-23)'),
    ]
    faz = models.CharField(max_length=10, choices=FAZ_CHOICES, default='FAZ1', verbose_name="Süreç Fazı")

    class Meta:
        ordering = ['adim_no']
        verbose_name = "Prototip Adım Tanımı"
        verbose_name_plural = "Prototip Adım Tanımları"

    def __str__(self):
        return f"{self.adim_no}. {self.baslik}"

    @property
    def dokuman_listesi(self):
        if not self.ilgili_dokumanlar:
            return []
        items = []
        for line in self.ilgili_dokumanlar.replace('\r\n', '\n').split('\n'):
            for part in line.split(','):
                cleaned = part.strip()
                if cleaned and cleaned != '-':
                    items.append(cleaned)
        return items


class PrototipSureci(models.Model):
    """
    Prototip Süreci Takip Kaydı (23 Adım)
    """
    PROTOTIP_TIPI_CHOICES = [
        ('YENI_TASARIM', 'Yeni Tasarım Prototipi'),
        ('MALZEME_DENEME', 'Malzeme / Hammadde Değişikliği Prototipi'),
        ('VAVE_MALIYET', 'Maliyet İyileştirme / VAVE Prototipi'),
        ('MUSTERI_TEST', 'Müşteri Fonksiyonel Test Prototipi'),
        ('PROSES_DENEME', 'İç Proses & Kalıp Doğrulama Prototipi'),
    ]

    DURUM_CHOICES = [
        ('DEVAM_EDIYOR', 'Devam Ediyor'),
        ('YENI_URUN_SURECINE_AKTARILDI', 'Yeni Ürün Devreye Alma Sürecine Aktarıldı'),
        ('REVIZYONDA', 'Revizyon Aşamasında'),
        ('BASARIYLA_TAMAMLANDI', 'Başarıyla Tamamlandı & Arşivlendi'),
        ('OLUMSUZ_KAPATILDI', 'Müşteri Onayı Alınamadı / İptal'),
    ]

    kod = models.CharField(max_length=50, unique=True, verbose_name="Prototip Kodu (PRT)")
    ad = models.CharField(max_length=200, verbose_name="Prototip Konusu / Proje Adı")
    musteri_adi = models.CharField(max_length=150, verbose_name="Müşteri / Firma Adı")
    musteri_karti = models.ForeignKey(MusteriKarti, on_delete=models.SET_NULL, null=True, blank=True, related_name="prototip_surecleri", verbose_name="Müşteri Portföy Kartı")
    ana_proje = models.ForeignKey('AnaProje', on_delete=models.SET_NULL, null=True, blank=True, related_name="prototip_iterasyonlari", verbose_name="Bağlı Ana Proje")

    parca_kodu = models.CharField(max_length=100, blank=True, null=True, verbose_name="Parça / Numune Kodu")
    revizyon_no = models.CharField(max_length=50, default="Rev.01", verbose_name="Revizyon No")
    prototip_tipi = models.CharField(max_length=40, choices=PROTOTIP_TIPI_CHOICES, default='YENI_TASARIM', verbose_name="Prototip Tipi")

    urun_grubu = models.CharField(max_length=100, choices=PazarlamaProjesi.URUN_GRUBU_CHOICES, default='Metal Parca & Sac', verbose_name="Ürün Grubu")
    ilgili_fabrika = models.CharField(max_length=100, choices=PazarlamaProjesi.FABRIKA_CHOICES, default='PRESHANE', verbose_name="İlgili Fabrika")

    hedef_tamamlanma_tarihi = models.DateField(null=True, blank=True, verbose_name="Hedef Tamamlanma Tarihi")

    sorumlu_proje_sorumlusu = models.CharField(max_length=100, default='BUSE NUR BALTACIOĞLU', verbose_name="Proje Sorumlusu (R)")
    sorumlu_fabrika_muduru = models.CharField(max_length=100, default='ONUR TUNCER', verbose_name="Fabrika Müdürü (A)")
    sorumlu_satis_analiz = models.CharField(max_length=100, default='METİN YAVAŞ', verbose_name="Satış-Analiz Sorumlusu (C)")
    sorumlu_kalite = models.CharField(max_length=100, default='MUHARREM FURKAN TARHAN', verbose_name="Kalite Sorumlusu (C)")

    durum = models.CharField(max_length=40, choices=DURUM_CHOICES, default='DEVAM_EDIYOR', verbose_name="Süreç Durumu")
    guncel_adim_no = models.PositiveSmallIntegerField(default=1, verbose_name="Güncel Adım No")

    aciklama = models.TextField(blank=True, null=True, verbose_name="Prototip Özeti / Başlangıç Notları")

    olusturma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    guncelleme_tarihi = models.DateTimeField(auto_now=True, verbose_name="Son Güncelleme")

    class Meta:
        ordering = ['-guncelleme_tarihi']
        verbose_name = "Prototip Süreci"
        verbose_name_plural = "Prototip Süreçleri"

    def __str__(self):
        return f"{self.kod} - {self.musteri_adi} ({self.ad})"

    @property
    def tamamlanma_yuzdesi(self):
        toplam_adim = 23
        tamamlanan = self.adim_kayitlari.filter(durum__in=['TAMAMLANDI', 'PAS_GECILDI']).count()
        return int((tamamlanan / toplam_adim) * 100)

    @property
    def guncel_adim(self):
        return self.adim_kayitlari.filter(adim__adim_no=self.guncel_adim_no).first()


class PrototipAdimKaydi(models.Model):
    DURUM_CHOICES = [
        ('BEKLIYOR', 'Bekliyor'),
        ('DEVAM_EDIYOR', 'Devam Ediyor / Aktif'),
        ('TAMAMLANDI', 'Tamamlandı (Onaylandı)'),
        ('REVIZYON_YONLENDIRILDI', 'Geriye Revizyona Gönderildi'),
        ('PAS_GECILDI', 'Pas Geçildi / Muaf'),
    ]

    surec = models.ForeignKey(PrototipSureci, on_delete=models.CASCADE, related_name='adim_kayitlari', verbose_name="Prototip Süreci")
    adim = models.ForeignKey(PrototipAdimTanimi, on_delete=models.PROTECT, verbose_name="Süreç Adımı")
    durum = models.CharField(max_length=30, choices=DURUM_CHOICES, default='BEKLIYOR', verbose_name="Durum")

    tamamlayan = models.CharField(max_length=100, blank=True, null=True, verbose_name="İşlemi Yapan")
    tamamlanma_tarihi = models.DateTimeField(blank=True, null=True, verbose_name="Tamamlanma Tarihi")

    karar_sonucu = models.CharField(max_length=150, blank=True, null=True, verbose_name="Verilen Karar")
    notlar = models.TextField(blank=True, null=True, verbose_name="Adım Notları / Değerlendirme / Teknik Çıktı")
    dokuman_referansi = models.CharField(max_length=255, blank=True, null=True, verbose_name="Doküman Linki / Form No")

    class Meta:
        ordering = ['adim__adim_no']
        unique_together = ('surec', 'adim')
        verbose_name = "Prototip Adım Kaydı"
        verbose_name_plural = "Prototip Adım Kayıtları"

    def __str__(self):
        return f"{self.surec.kod} - Adım {self.adim.adim_no} ({self.get_durum_display()})"


class PrototipGecmisLog(models.Model):
    surec = models.ForeignKey(PrototipSureci, on_delete=models.CASCADE, related_name='tarihce_kayitlari', verbose_name="Prototip Süreci")
    islem = models.CharField(max_length=255, verbose_name="Yapılan İşlem")
    detay = models.TextField(blank=True, null=True, verbose_name="İşlem Detayı")
    yapan = models.CharField(max_length=100, default='Sistem', verbose_name="İşlemi Yapan")
    tarih = models.DateTimeField(default=timezone.now, verbose_name="İşlem Tarihi")

    class Meta:
        ordering = ['-tarih']
        verbose_name = "Prototip Geçmiş Logu"
        verbose_name_plural = "Prototip Geçmiş Logları"

    def __str__(self):
        return f"{self.surec.kod} - {self.islem} ({self.tarih.strftime('%d.%m.%Y %H:%M')})"


# ==========================================
# 8. ÜRÜN SERİ ÜRETİM SONLANDIRMA SÜRECİ / EOP (6 ADIM)
# ==========================================

class EOPSurecAdimTanimi(models.Model):
    """
    6 Adımlık Ürün Seri Üretim Sonlandırma Süreci / EOP Master Verisi
    """
    adim_no = models.PositiveSmallIntegerField(unique=True, verbose_name="Adım Numarası")
    baslik = models.CharField(max_length=255, verbose_name="Süreç Adımı Başlığı")
    faaliyet_tanimi = models.TextField(verbose_name="Faaliyet Tanımı")
    sorumlular = models.CharField(max_length=255, verbose_name="Sorumlular")
    ilgili_dokumanlar = models.TextField(verbose_name="İlgili Dokümanlar", blank=True, null=True)
    karar_adimi_mi = models.BooleanField(default=False, verbose_name="Karar / Onay Adımı mı?")

    FAZ_CHOICES = [
        ('FAZ1', 'Faz 1: EOP Bildirimi & Talep Analizi (Adım 1-2)'),
        ('FAZ2', 'Faz 2: Stok & Üretim Varlıkları Tasfiyesi (Adım 3-4)'),
        ('FAZ3', 'Faz 3: Sistem Kapatma & Süreç Kapanışı (Adım 5-6)'),
    ]
    faz = models.CharField(max_length=10, choices=FAZ_CHOICES, default='FAZ1', verbose_name="Süreç Fazı")

    class Meta:
        ordering = ['adim_no']
        verbose_name = "EOP Süreç Adım Tanımı"
        verbose_name_plural = "EOP Süreç Adım Tanımları"

    def __str__(self):
        return f"{self.adim_no}. {self.baslik}"

    @property
    def dokuman_listesi(self):
        if not self.ilgili_dokumanlar:
            return []
        items = []
        for line in self.ilgili_dokumanlar.replace('\r\n', '\n').split('\n'):
            for part in line.split(','):
                cleaned = part.strip()
                if cleaned:
                    items.append(cleaned)
        return items

    @property
    def sorumlu_listesi(self):
        if not self.sorumlular:
            return []
        return [s.strip() for s in self.sorumlular.split(',') if s.strip()]


class EOPSureci(models.Model):
    """
    Ürün Seri Üretim Sonlandırma Süreci / EOP Takip Kaydı (6 Adım)
    """
    DURUM_CHOICES = [
        ('DEVAM_EDIYOR', 'Devam Ediyor'),
        ('STOK_TASFIYESINDE', 'Stok Tasfiyesi / Değerlendirme Aşamasında'),
        ('VARLIK_DEVRI_TAMAMLANDI', 'Üretim Varlıkları Tasfiyesi Tamamlandı'),
        ('BASARIYLA_KAPATILDI', 'Başarıyla Tamamlandı & Kapatıldı'),
        ('IPTAL_EDILDI', 'İptal Edildi'),
    ]

    kod = models.CharField(max_length=50, unique=True, verbose_name="EOP Takip Kodu (EOP)")
    urun_kodu = models.CharField(max_length=100, verbose_name="Sonlandırılacak Ürün / Parça Kodu")
    urun_adi = models.CharField(max_length=200, verbose_name="Ürün Adı / Proje Tanımı")
    musteri_adi = models.CharField(max_length=150, verbose_name="Müşteri / Firma Adı")
    musteri_karti = models.ForeignKey(MusteriKarti, on_delete=models.SET_NULL, null=True, blank=True, related_name="eop_surecleri", verbose_name="Müşteri Portföy Kartı")

    urun_grubu = models.CharField(max_length=100, choices=PazarlamaProjesi.URUN_GRUBU_CHOICES, default='Kondanser & Sogutma', verbose_name="Ürün Grubu")
    ilgili_fabrika = models.CharField(max_length=100, choices=PazarlamaProjesi.FABRIKA_CHOICES, default='PRESHANE', verbose_name="İlgili Fabrika")

    eop_bildirim_tarihi = models.DateField(default=timezone.now, verbose_name="EOP Bildirim Tarihi")
    seri_uretim_bitis_tarihi = models.DateField(null=True, blank=True, verbose_name="Seri Üretim Bitiş Tarihi")
    yedek_parca_servis_suresi_yil = models.PositiveSmallIntegerField(default=10, verbose_name="Yedek Parça Servis Yükümlülüğü (Yıl)")

    sorumlu_proje_sorumlusu = models.CharField(max_length=100, default='BUSE NUR BALTACIOĞLU', verbose_name="Proje Sorumlusu (R)")
    sorumlu_fabrika_muduru = models.CharField(max_length=100, default='ONUR TUNCER', verbose_name="Fabrika Müdürü (A)")
    sorumlu_satis_analiz = models.CharField(max_length=100, default='METİN YAVAŞ', verbose_name="Satış-Analiz Sorumlusu (C)")
    sorumlu_planlama = models.CharField(max_length=100, default='MUHARREM FURKAN TARHAN', verbose_name="Planlama Sorumlusu (C)")
    sorumlu_uretim = models.CharField(max_length=100, default='YİĞİT EFE BİLİR', verbose_name="Üretim Sorumlusu (C)")

    durum = models.CharField(max_length=40, choices=DURUM_CHOICES, default='DEVAM_EDIYOR', verbose_name="Süreç Durumu")
    guncel_adim_no = models.PositiveSmallIntegerField(default=1, verbose_name="Güncel Adım No")

    aciklama = models.TextField(blank=True, null=True, verbose_name="EOP Açıklaması / Müşteri Bildirim Notları")

    olusturma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    guncelleme_tarihi = models.DateTimeField(auto_now=True, verbose_name="Son Güncelleme")

    class Meta:
        ordering = ['-guncelleme_tarihi']
        verbose_name = "Ürün Seri Üretim Sonlandırma (EOP) Süreci"
        verbose_name_plural = "Ürün Seri Üretim Sonlandırma (EOP) Süreçleri"

    def __str__(self):
        return f"{self.kod} - {self.musteri_adi} ({self.urun_adi})"

    @property
    def tamamlanma_yuzdesi(self):
        toplam_adim = 6
        tamamlanan = self.adim_kayitlari.filter(durum__in=['TAMAMLANDI', 'PAS_GECILDI']).count()
        return int((tamamlanan / toplam_adim) * 100)

    @property
    def guncel_adim(self):
        return self.adim_kayitlari.filter(adim__adim_no=self.guncel_adim_no).first()


class EOPAdimKaydi(models.Model):
    DURUM_CHOICES = [
        ('BEKLIYOR', 'Bekliyor'),
        ('DEVAM_EDIYOR', 'Devam Ediyor / Aktif'),
        ('TAMAMLANDI', 'Tamamlandı (Onaylandı)'),
        ('PAS_GECILDI', 'Pas Geçildi / Muaf'),
    ]

    surec = models.ForeignKey(EOPSureci, on_delete=models.CASCADE, related_name='adim_kayitlari', verbose_name="EOP Süreci")
    adim = models.ForeignKey(EOPSurecAdimTanimi, on_delete=models.PROTECT, verbose_name="Süreç Adımı")
    durum = models.CharField(max_length=30, choices=DURUM_CHOICES, default='BEKLIYOR', verbose_name="Durum")

    tamamlayan = models.CharField(max_length=100, blank=True, null=True, verbose_name="İşlemi Yapan")
    tamamlanma_tarihi = models.DateTimeField(blank=True, null=True, verbose_name="Tamamlanma Tarihi")

    karar_sonucu = models.CharField(max_length=150, blank=True, null=True, verbose_name="Verilen Karar / Mutabakat")
    notlar = models.TextField(blank=True, null=True, verbose_name="Adım Notları / Değerlendirme / Çıktı")
    dokuman_referansi = models.CharField(max_length=255, blank=True, null=True, verbose_name="Doküman Linki / Form No")

    class Meta:
        ordering = ['adim__adim_no']
        unique_together = ('surec', 'adim')
        verbose_name = "EOP Adım Kaydı"
        verbose_name_plural = "EOP Adım Kayıtları"

    def __str__(self):
        return f"{self.surec.kod} - Adım {self.adim.adim_no} ({self.get_durum_display()})"


class EOPGecmisLog(models.Model):
    surec = models.ForeignKey(EOPSureci, on_delete=models.CASCADE, related_name='tarihce_kayitlari', verbose_name="EOP Süreci")
    islem = models.CharField(max_length=255, verbose_name="Yapılan İşlem")
    detay = models.TextField(blank=True, null=True, verbose_name="İşlem Detayı")
    yapan = models.CharField(max_length=100, default='Sistem', verbose_name="İşlemi Yapan")
    tarih = models.DateTimeField(default=timezone.now, verbose_name="İşlem Tarihi")

    class Meta:
        ordering = ['-tarih']
        verbose_name = "EOP Geçmiş Logu"
        verbose_name_plural = "EOP Geçmiş Logları"

    def __str__(self):
        return f"{self.surec.kod} - {self.islem} ({self.tarih.strftime('%d.%m.%Y %H:%M')})"


class FaaliyetKaydi(models.Model):
    """
    Kullanıcı ve Personel Bazlı Faaliyet, Ajanda, Görev ve Destek Talepleri
    (Seyahat, Toplantı, Fuar, Destek Talebi)
    """
    TUR_CHOICES = [
        ('SEYAHAT', 'Müşteri / İş Seyahati'),
        ('TOPLANTI', 'Müşteri / İç Toplantı'),
        ('FUAR', 'Fuar & Sektörel Etkinlik'),
        ('DESTEK', 'Destek & Aksiyon Talebi'),
    ]

    ONCELIK_CHOICES = [
        ('DUSUK', 'Düşük'),
        ('ORTA', 'Orta'),
        ('YUKSEK', 'Yüksek'),
        ('KRITIK', 'Kritik / Acil'),
    ]

    DURUM_CHOICES = [
        ('PLANLANDI', 'Planlandı'),
        ('DEVAM_EDIYOR', 'Devam Ediyor / Hazırlık'),
        ('ONAYDA', 'Yönetici Onayında'),
        ('TAMAMLANDI', 'Tamamlandı'),
        ('IPTAL', 'İptal Edildi'),
    ]

    tur = models.CharField(max_length=20, choices=TUR_CHOICES, default='TOPLANTI', verbose_name="Faaliyet / Talep Türü")
    baslik = models.CharField(max_length=255, verbose_name="Faaliyet / Talep Başlığı")
    sorumlu_kisi = models.CharField(max_length=120, default='Buse Nur Baltacıoğlu', verbose_name="Sorumlu Personel")
    
    musteri = models.ForeignKey(
        'MusteriKarti', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='faaliyetler', 
        verbose_name="İlişkili Müşteri"
    )
    musteri_adi = models.CharField(max_length=255, blank=True, null=True, verbose_name="Müşteri / Firma Adı")
    lokasyon = models.CharField(max_length=255, blank=True, null=True, verbose_name="Lokasyon / Yer / Kanal")
    
    baslangic_tarihi = models.DateField(default=timezone.now, verbose_name="Başlangıç Tarihi")
    bitis_tarihi = models.DateField(default=timezone.now, verbose_name="Bitiş Tarihi")
    saat_araligi = models.CharField(max_length=60, default='09:00 - 10:30', blank=True, null=True, verbose_name="Saat / Zaman Dilimi")
    
    oncelik = models.CharField(max_length=20, choices=ONCELIK_CHOICES, default='ORTA', verbose_name="Öncelik Seviyesi")
    durum = models.CharField(max_length=20, choices=DURUM_CHOICES, default='PLANLANDI', verbose_name="Durum")
    
    aciklama = models.TextField(blank=True, null=True, verbose_name="Açıklama, Gündem & Notlar")
    tahmini_butce = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, blank=True, null=True, verbose_name="Tahmini Bütçe / Masraf")
    
    olusturan = models.CharField(max_length=100, default='Buse Nur Baltacıoğlu', verbose_name="Oluşturan")
    olusturuldu_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    guncellendi_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        ordering = ['baslangic_tarihi', 'durum']
        verbose_name = "Faaliyet / Talep Kaydı"
        verbose_name_plural = "Faaliyet & Talep Kayıtları"

    def __str__(self):
        return f"[{self.get_tur_display()}] {self.baslik} ({self.sorumlu_kisi})"

    @property
    def tur_ikonu(self):
        icons = {
            'SEYAHAT': 'bi-airplane-fill',
            'TOPLANTI': 'bi-people-fill',
            'FUAR': 'bi-shop-window',
            'DESTEK': 'bi-headset',
        }
        return icons.get(self.tur, 'bi-calendar-event')

    @property
    def tur_renk(self):
        colors = {
            'SEYAHAT': '#0ea5e9',
            'TOPLANTI': '#10b981',
            'FUAR': '#8b5cf6',
            'DESTEK': '#f59e0b',
        }
        return colors.get(self.tur, '#22609d')

    @property
    def oncelik_badge_class(self):
        classes = {
            'DUSUK': 'bg-light text-secondary border',
            'ORTA': 'bg-primary-subtle text-primary border border-primary-subtle',
            'YUKSEK': 'bg-warning-subtle text-warning-emphasis border border-warning-subtle',
            'KRITIK': 'bg-danger-subtle text-danger border border-danger-subtle',
        }
        return classes.get(self.oncelik, 'bg-light text-dark')

    @property
    def durum_badge_class(self):
        classes = {
            'PLANLANDI': 'bg-secondary-subtle text-secondary border border-secondary-subtle',
            'DEVAM_EDIYOR': 'bg-info-subtle text-info border border-info-subtle',
            'ONAYDA': 'bg-warning-subtle text-warning-emphasis border border-warning-subtle',
            'TAMAMLANDI': 'bg-success-subtle text-success border border-success-subtle',
            'IPTAL': 'bg-danger-subtle text-danger border border-danger-subtle',
        }
        return classes.get(self.durum, 'bg-light text-dark')


class AnaProje(models.Model):
    """
    Uçtan Uca 8 Süreci Birleştiren Master Proje / Dijital İplik (Digital Thread) Modeli
    1. Müşteri İlişkileri Süreci
    2. Pazarlama Süreci
    3. Ürün Teklif Süreci
    4. Sözleşme Değerlendirme Süreci
    5. Prototip Süreci
    6. Yeni Ürün Devreye Alma Süreci
    7. Mühendislik Değişikliği Süreci
    8. Ürün Seri Üretim Sonlandırma Süreci (EOP)
    """
    FABRIKA_CHOICES = [
        ('PRESHANE', 'PRESHANE'),
        ('KALIPHANE', 'KALIPHANE'),
        ('CERKEZKOY', 'CERKEZKOY'),
        ('KABLOGR', 'KABLOGR'),
        ('KONDANSER', 'KONDANSER'),
        ('MANISA ORTAK', 'MANISA ORTAK'),
    ]

    proje_kodu = models.CharField(max_length=50, unique=True, verbose_name="Proje Kodu")
    proje_adi = models.CharField(max_length=200, verbose_name="Proje Başlığı")
    bolum = models.CharField(max_length=100, default='Kalıphane', verbose_name="Bölüm / Departman")
    urun_grubu = models.CharField(max_length=100, default='Kurutucu', verbose_name="Ürün Grubu")
    parca_kodu = models.CharField(max_length=100, blank=True, default='', verbose_name="Parça / Kalıp Kodu")
    parca_adi = models.CharField(max_length=200, blank=True, default='', verbose_name="Parça Adı")
    yillik_frc_miktar = models.BigIntegerField(default=0, verbose_name="Yıllık FRC Miktar (Adet)")
    
    proje_hedef_tarihi_str = models.CharField(max_length=50, default='', blank=True, verbose_name="Proje Hedef Tarihi")
    proje_baslangic_tarihi_str = models.CharField(max_length=50, default='', blank=True, verbose_name="Proje Başlangıç Tarihi")
    proje_bitis_tarihi_str = models.CharField(max_length=50, default='', blank=True, verbose_name="Proje Bitiş Tarihi")
    proje_onay_tarihi_str = models.CharField(max_length=50, default='', blank=True, verbose_name="Proje Onay Tarihi")
    aciklama_notu = models.TextField(default='', blank=True, verbose_name="Açıklama / Durum Notu")

    fabrika = models.CharField(max_length=100, choices=FABRIKA_CHOICES, default='PRESHANE', verbose_name="Ana Departman / Bölüm")
    
    musteri = models.ForeignKey(
        'MusteriKarti', 
        on_delete=models.CASCADE, 
        related_name='ana_projeler', 
        verbose_name="Cari / Müşteri"
    )
    tesis = models.ForeignKey(
        'MusteriTesisi', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='ana_projeler',
        verbose_name="Müşteri Tesisi / Lokasyonu"
    )
    
    sorumlu_lider = models.CharField(max_length=120, default='Buse Nur Baltacıoğlu', verbose_name="Proje Lideri")
    hedef_sop_tarihi = models.DateField(null=True, blank=True, verbose_name="Hedef Seri Üretim Tarihi")
    genel_ilerleme_yuzdesi = models.IntegerField(default=50, verbose_name="Genel İlerleme %")
    
    # Dijital İplik (Digital Thread) Parametreleri
    hedef_butce = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, default=125000.00, verbose_name="Hedef Proje / Teklif Bütçesi (EUR)")
    yillik_hacim_adet = models.IntegerField(default=50000, verbose_name="Yıllık Tahmini Hacim (Adet)")
    kalip_goz_sayisi = models.IntegerField(default=4, verbose_name="Kalıp Göz Sayısı")
    hammadde_cinsi = models.CharField(max_length=120, default="DC01 Galvaniz Sac / 1.20mm", blank=True, verbose_name="Hammadde / Spesifikasyon")
    dijital_iplik_senkronize_mi = models.BooleanField(default=True, verbose_name="Teklif & APQP Veri Senkronizasyonu Aktif mi?")

    # Aktif Süreç ve Adım Bilgisi
    aktif_surec_no = models.IntegerField(default=6, verbose_name="Aktif Süreç No (1-8)")
    aktif_surec_adi = models.CharField(max_length=120, default="Yeni Ürün Devreye Alma Süreci", verbose_name="Aktif Süreç Adı")
    aktif_adim_no = models.IntegerField(default=18, verbose_name="Aktif Adım No")
    aktif_adim_basligi = models.CharField(max_length=255, default="T0 Kalıp Denemesi ve İlk Numune Basımı", verbose_name="Aktif Adım Başlığı")
    aktif_rol = models.CharField(max_length=100, default="Projeci / Kalıp", verbose_name="Aktif Rol Sorumlusu")
    aktif_durum_aciklamasi = models.CharField(max_length=255, default="Kalıp denemesi tamamlandı, CMM boyutsal ölçüm raporu bekleniyor.", verbose_name="Durum Özeti / Not")
    
    durum = models.CharField(max_length=50, default="Devam Ediyor", verbose_name="Proje Genel Durumu")
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    guncellenme_tarihi = models.DateTimeField(auto_now=True)

    # 8 Süreçle Birebir İlişki (Opsiyonel / Bağlantılı)
    musteri_iliskileri_sureci = models.ForeignKey('MusteriIliskileriSureci', null=True, blank=True, on_delete=models.SET_NULL, related_name='bagli_ana_projeler')
    pazarlama_sureci = models.ForeignKey('PazarlamaProjesi', null=True, blank=True, on_delete=models.SET_NULL, related_name='bagli_ana_projeler')
    urun_teklif_sureci = models.ForeignKey('UrunTeklifSureci', null=True, blank=True, on_delete=models.SET_NULL, related_name='bagli_ana_projeler')
    sozlesme_sureci = models.ForeignKey('SozlesmeSureci', null=True, blank=True, on_delete=models.SET_NULL, related_name='bagli_ana_projeler')
    prototip_sureci = models.ForeignKey('PrototipSureci', null=True, blank=True, on_delete=models.SET_NULL, related_name='bagli_ana_projeler')
    yeni_urun_sureci = models.ForeignKey('YeniUrunDevreyeAlmaSureci', null=True, blank=True, on_delete=models.SET_NULL, related_name='bagli_ana_projeler')
    muhendislik_degisikligi_sureci = models.ForeignKey('MuhendislikDegisikligiSureci', null=True, blank=True, on_delete=models.SET_NULL, related_name='bagli_ana_projeler')
    eop_sureci = models.ForeignKey('EOPSureci', null=True, blank=True, on_delete=models.SET_NULL, related_name='bagli_ana_projeler')

    class Meta:
        verbose_name = "Uçtan Uca Ana Proje"
        verbose_name_plural = "Uçtan Uca Ana Projeler"
        ordering = ['proje_kodu']

    def __str__(self):
        return f"[{self.proje_kodu}] {self.proje_adi} - {self.musteri.ad if self.musteri else ''}"

    @property
    def uctan_uca_ilerleme_yuzdesi(self):
        """
        8 süreçlik omurgadaki aktif sürecin oranına göre genel uçtan uca ilerleme yüzdesi (Örn: 6/8 = %75).
        """
        if self.aktif_surec_no:
            return int(round((self.aktif_surec_no / 8.0) * 100))
        return self.genel_ilerleme_yuzdesi or 0

    def save(self, *args, **kwargs):
        if self.aktif_surec_no:
            self.genel_ilerleme_yuzdesi = int(round((self.aktif_surec_no / 8.0) * 100))
        super().save(*args, **kwargs)

    def get_surecler_listesi(self):
        """
        8 sürecin her birinin bu proje için canlı durumunu, adım sayısını,
        sorumlu rolünü ve bağlantısını listeler.
        """
        # Temel 8 süreç tanımları
        surec_tanimlari = [
            {
                'no': 1,
                'kod': 'S1',
                'baslik': 'Müşteri İlişkileri Süreci',
                'alt_baslik': 'İlk Temas, Müşteri Profili ve Ziyaret',
                'adim_sayisi': '4 Adım',
                'varsayilan_rol': 'Satış & Pazarlama',
                'url': '/musteri-iliskileri/',
                'ikon': 'bi-people',
            },
            {
                'no': 2,
                'kod': 'S2',
                'baslik': 'Pazarlama Süreci',
                'alt_baslik': '15 Adım Pazar & Bütçe Onay Akışı',
                'adim_sayisi': '15 Adım',
                'varsayilan_rol': 'Satış & Pazarlama',
                'url': '/pazarlama-sureci/',
                'ikon': 'bi-megaphone',
            },
            {
                'no': 3,
                'kod': 'S3',
                'baslik': 'Ürün Teklif Süreci',
                'alt_baslik': 'SAT-EK-005 Maliyet, Fizibilite ve Fiyat',
                'adim_sayisi': '6 Adım',
                'varsayilan_rol': 'Satış & Pazarlama',
                'url': '/urun-teklif-sureci/',
                'ikon': 'bi-calculator',
            },
            {
                'no': 4,
                'kod': 'S4',
                'baslik': 'Sözleşme Değerlendirme Süreci',
                'alt_baslik': 'Gizlilik, Kalite ve Ticari Protokoller',
                'adim_sayisi': '5 Adım',
                'varsayilan_rol': 'Fabrika Müdürü Onayı',
                'url': '/sozlesme-sureci/',
                'ikon': 'bi-file-earmark-check',
            },
            {
                'no': 5,
                'kod': 'S5',
                'baslik': 'Prototip Süreci',
                'alt_baslik': '23 Adım Numune ve CMM Ölçüm Onayı',
                'adim_sayisi': '23 Adım',
                'varsayilan_rol': 'Kalite Güvence',
                'url': '/prototip-sureci/',
                'ikon': 'bi-cpu',
            },
            {
                'no': 6,
                'kod': 'S6',
                'baslik': 'Yeni Ürün Devreye Alma Süreci',
                'alt_baslik': '45 Adım APQP / PPAP ve Kalıp İmalatı',
                'adim_sayisi': '45 Adım',
                'varsayilan_rol': 'Projeci / Kalıp',
                'url': '/yeni-urun-devreye-alma/',
                'ikon': 'bi-gear-wide-connected',
            },
            {
                'no': 7,
                'kod': 'S7',
                'baslik': 'Mühendislik Değişikliği Süreci',
                'alt_baslik': '5 Adım ECN / ECR Revizyon Yönetimi',
                'adim_sayisi': '5 Adım',
                'varsayilan_rol': 'Projeci / Kalıp',
                'url': '/muhendislik-degisikligi/',
                'ikon': 'bi-wrench',
            },
            {
                'no': 8,
                'kod': 'S8',
                'baslik': 'Ürün Seri Üretim Sonlandırma Süreci',
                'alt_baslik': '6 Adım EOP ve Kalıp Arşivleme',
                'adim_sayisi': '6 Adım',
                'varsayilan_rol': 'Üretim & Planlama',
                'url': '/eop-sureci/',
                'ikon': 'bi-box-arrow-right',
            },
        ]

        sonuc = []
        for s in surec_tanimlari:
            s_no = s['no']
            if s_no < self.aktif_surec_no:
                durum_kod = 'TAMAMLANDI'
                durum_etiket = 'Tamamlandı'
                badge_class = 'bg-success-subtle text-success border border-success-subtle'
                ilerleme = 100
                detay = f"Tüm adımlar onaylandı • {s['adim_sayisi']}"
                is_active = False
            elif s_no == self.aktif_surec_no:
                durum_kod = 'DEVAM_EDIYOR'
                durum_etiket = 'Aktif Devam Ediyor'
                badge_class = 'bg-primary-subtle text-primary border border-primary-subtle'
                ilerleme = self.uctan_uca_ilerleme_yuzdesi
                detay = f"Adım {self.aktif_adim_no}: {self.aktif_adim_basligi}"
                is_active = True
            else:
                durum_kod = 'BEKLEMEDE'
                durum_etiket = 'Sıradaki / Beklemede'
                badge_class = 'bg-light text-muted border'
                ilerleme = 0
                detay = f"Önceki süreçlerin tamamlanması bekleniyor"
                is_active = False

            sonuc.append({
                'no': s_no,
                'kod': s['kod'],
                'baslik': s['baslik'],
                'alt_baslik': s['alt_baslik'],
                'adim_sayisi': s['adim_sayisi'],
                'rol': s['varsayilan_rol'],
                'url': s['url'],
                'ikon': s['ikon'],
                'durum_kod': durum_kod,
                'durum_etiket': durum_etiket,
                'badge_class': badge_class,
                'ilerleme': ilerleme,
                'detay': detay,
                'is_active': is_active,
            })
        return sonuc

    def teklif_verilerini_senkronize_et(self):
        """
        Teklif (SAT-EK-005) aşamasındaki bütçe, müşteri ve parça verilerini
        Sözleşme, Prototip ve APQP süreçlerine aktaran Digital Thread köprüsü.
        """
        guncellenenler = []
        if self.urun_teklif_sureci:
            if self.urun_teklif_sureci.teklif_tutari:
                self.hedef_butce = self.urun_teklif_sureci.teklif_tutari
                guncellenenler.append('hedef_butce')
            if self.urun_teklif_sureci.musteri_karti and not self.musteri:
                self.musteri = self.urun_teklif_sureci.musteri_karti
                guncellenenler.append('musteri')
        if self.sozlesme_sureci and self.musteri:
            if not self.sozlesme_sureci.musteri_karti:
                self.sozlesme_sureci.musteri_karti = self.musteri
                self.sozlesme_sureci.save()
                guncellenenler.append('sozlesme_musteri')
        if self.yeni_urun_sureci and self.musteri:
            if not self.yeni_urun_sureci.musteri_karti:
                self.yeni_urun_sureci.musteri_karti = self.musteri
                self.yeni_urun_sureci.save()
                guncellenenler.append('yeni_urun_musteri')
        self.dijital_iplik_senkronize_mi = True
        self.save()
        return guncellenenler

    def get_prototip_iterasyonlari(self):
        """
        Bağlı prototip döngülerini (T0, T1, Malzeme Doğrulama vb.) listeler.
        """
        iterasyonlar = list(self.prototip_iterasyonlari.all().order_by('olusturma_tarihi'))
        if not iterasyonlar and self.prototip_sureci:
            iterasyonlar = [self.prototip_sureci]
        return iterasyonlar

    def get_eco_revizyonlari(self):
        """
        Bağlı mühendislik değişikliklerini (ECO revizyonları) listeler.
        """
        revizyonlar = list(self.eco_iterasyonlari.all().order_by('olusturma_tarihi'))
        if not revizyonlar and self.muhendislik_degisikligi_sureci:
            revizyonlar = [self.muhendislik_degisikligi_sureci]
        return revizyonlar

    def get_bekleyen_aksiyonlar(self, rol=None):
        """
        Projenin aktif süreç ve alt adımlarında kullanıcının rolüne düşen
        en kritik bekleyen aksiyonları ve termin risk durumunu döndürür.
        """
        aksiyonlar = []
        
        # 1. Aktif sürecin güncel adımı (Birincil Kritik Yol)
        aksiyonlar.append({
            'surec_kodu': f"S{self.aktif_surec_no}",
            'surec_adi': self.aktif_surec_adi,
            'adim_no': self.aktif_adim_no,
            'adim_basligi': self.aktif_adim_basligi,
            'rol': self.aktif_rol,
            'oncelik': 'Kritik Yol',
            'oncelik_badge': 'bg-danger-subtle text-danger border border-danger-subtle',
            'termin_durumu': 'Termin Yaklaşıyor (2 Gün)',
            'termin_badge': 'bg-warning-subtle text-warning border border-warning-subtle',
            'url': f"/yeni-urun-devreye-alma/?adim={self.aktif_adim_no}" if self.aktif_surec_no == 6 else "/?tab=is_akisi",
            'not': self.aktif_durum_aciklamasi,
        })
        
        # 2. Döngüsel ECO / Prototip aksiyonları varsa ekle
        for eco in self.get_eco_revizyonlari():
            if eco.durum in ['DEVAM_EDIYOR', 'REVIZYONDA']:
                aksiyonlar.append({
                    'surec_kodu': 'S7 (ECO)',
                    'surec_adi': f"ECO Revizyonu: {eco.kod}",
                    'adim_no': eco.guncel_adim_no,
                    'adim_basligi': f"{eco.ad} - {eco.revizyon_no}",
                    'rol': 'Projeci / Kalıp',
                    'oncelik': 'Yüksek',
                    'oncelik_badge': 'bg-primary-subtle text-primary border border-primary-subtle',
                    'termin_durumu': 'Devam Ediyor',
                    'termin_badge': 'bg-info-subtle text-info border border-info-subtle',
                    'url': '/muhendislik-degisikligi/',
                    'not': f"Revizyon nedeni: {eco.get_degisiklik_nedeni_display()}",
                })

        for prt in self.get_prototip_iterasyonlari():
            if prt.durum in ['DEVAM_EDIYOR', 'REVIZYONDA']:
                aksiyonlar.append({
                    'surec_kodu': 'S5 (PRT)',
                    'surec_adi': f"Prototip İterasyonu: {prt.kod}",
                    'adim_no': prt.guncel_adim_no,
                    'adim_basligi': f"{prt.ad} - {prt.revizyon_no}",
                    'rol': 'Kalite Güvence',
                    'oncelik': 'Orta',
                    'oncelik_badge': 'bg-secondary-subtle text-secondary border border-secondary-subtle',
                    'termin_durumu': 'Numune Doğrulama',
                    'termin_badge': 'bg-light text-muted border',
                    'url': '/prototip-sureci/',
                    'not': f"Prototip tipi: {prt.get_prototip_tipi_display()}",
                })

        # Rol filtresi
        if rol and rol != 'ALL':
            aksiyonlar = [a for a in aksiyonlar if a['rol'].lower() == rol.lower()]
            
        return aksiyonlar


class SistemKodSayaci(models.Model):
    """
    Süreç bazlı tekil artan IncKey sayaç tablosu
    """
    surec_tipi = models.CharField(max_length=20, verbose_name="Süreç Tipi (PRJ, TEK, ECO vb.)")
    yil = models.IntegerField(verbose_name="Yıl")
    son_sira_no = models.IntegerField(default=100, verbose_name="Son Verilen Sıra Numarası")
    guncellenme_tarihi = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('surec_tipi', 'yil')
        verbose_name = "Sistem Kod Sayacı"
        verbose_name_plural = "Sistem Kod Sayaçları"

    def __str__(self):
        return f"{self.surec_tipi}-{self.yil}: {self.son_sira_no}"









