from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum
from .models import (
    PazarlamaProjesi, 
    SurecAdimTanimi, 
    ProjeAdimKaydi, 
    ProjeGecmisLog, 
    HedefPazarKanvas,
    MusteriKarti,
    MusteriTesisi,
    MusteriEtkilesimZamanTuneli,
    UrunGrubuKarti,
    MusteriIliskileriAdimTanimi,
    MusteriIliskileriSureci,
    MusteriIliskileriAdimKaydi,
    MusteriIliskileriGecmisLog,
    UrunTeklifAdimTanimi,
    UrunTeklifSureci,
    UrunTeklifAdimKaydi,
    UrunTeklifGecmisLog,
    SozlesmeAdimTanimi,
    SozlesmeSureci,
    SozlesmeAdimKaydi,
    SozlesmeGecmisLog,
    YeniUrunAdimTanimi,
    YeniUrunDevreyeAlmaSureci,
    YeniUrunAdimKaydi,
    YeniUrunGecmisLog,
    MuhendislikDegisikligiAdimTanimi,
    MuhendislikDegisikligiSureci,
    MuhendislikDegisikligiAdimKaydi,
    MuhendislikDegisikligiGecmisLog,
    PrototipAdimTanimi,
    PrototipSureci,
    PrototipAdimKaydi,
    PrototipGecmisLog,
    EOPSurecAdimTanimi,
    EOPSureci,
    EOPAdimKaydi,
    EOPGecmisLog,
    FaaliyetKaydi,
    AnaProje,
    SistemKodSayaci,
    MusteriAdayi,
    MusteriAdayiNotu
)
from .services.intranet_service import get_intranet_sirketler, get_proje_liderleri
from .services.inckey_service import inckey_uret, siradaki_inckey_goruntule
import calendar
import datetime
import json
from django.utils.dateparse import parse_date


def dashboard(request):
    """
    Pazarlama Süreci Ana Paneli: İstatistikler, Proje Listesi ve Filtreleme
    """
    projeler = PazarlamaProjesi.objects.all()

    q = request.GET.get('q', '').strip()
    durum_filtre = request.GET.get('durum', '')
    urun_filtre = request.GET.get('urun_grubu', '')
    fabrika_filtre = request.GET.get('fabrika', '')

    if q:
        projeler = projeler.filter(
            Q(kod__icontains=q) |
            Q(musteri_adi__icontains=q) |
            Q(ad__icontains=q) |
            Q(hedef_ulke__icontains=q)
        )
    if durum_filtre:
        projeler = projeler.filter(durum=durum_filtre)
    if urun_filtre:
        projeler = projeler.filter(urun_grubu=urun_filtre)
    if fabrika_filtre:
        projeler = projeler.filter(ilgili_fabrika=fabrika_filtre)

    toplam_proje = PazarlamaProjesi.objects.count()
    aktif_proje = PazarlamaProjesi.objects.filter(durum='DEVAM_EDIYOR').count()
    teklif_proje = PazarlamaProjesi.objects.filter(durum='TEKLIF_SURECINDE').count()
    kapanan_proje = PazarlamaProjesi.objects.filter(durum__in=['BASARIYLA_KAPATILDI', 'OLUMSUZ_KAPATILDI']).count()

    context = {
        'projeler': projeler,
        'musteriler': MusteriKarti.objects.all()[:6],
        'kanvaslar': HedefPazarKanvas.objects.all(),
        'urun_gruplari_kart': UrunGrubuKarti.objects.all(),
        'toplam_proje': toplam_proje,
        'aktif_proje': aktif_proje,
        'teklif_proje': teklif_proje,
        'kapanan_proje': kapanan_proje,
        'q': q,
        'durum_filtre': durum_filtre,
        'urun_filtre': urun_filtre,
        'fabrika_filtre': fabrika_filtre,
        'urun_gruplari': PazarlamaProjesi.URUN_GRUBU_CHOICES,
        'fabrikalar': PazarlamaProjesi.FABRIKA_CHOICES,
        'durum_listesi': PazarlamaProjesi.DURUM_CHOICES,
    }
    return render(request, 'crm_takip/dashboard.html', context)


def kartlar_view(request):
    """
    Birleşik Müşteri Yönetimi ve Stratejik Kartlar:
    1. Müşteri Kartları (Tier 1 Stratejik, Tier 2 Büyüme, Tier 3 Standart) + 360° Müşteri Profili
    2. Ülke Kartları (Hedef Pazar Kanvasları) + 360° Ülke Profili
    3. Ürün Grubu Kartları (Kapasite & Kabiliyetler) + 360° Ürün Profili
    """
    aktif_sekme = request.GET.get('tab', 'musteriler') # 'musteriler', 'ulkeler', 'urunler'
    
    # 1. Müşteriler Filtreleme
    musteriler = MusteriKarti.objects.all()
    tier_filtre = request.GET.get('tier', 'ALL')
    q_musteri = request.GET.get('q_m', '').strip()

    if tier_filtre != 'ALL':
        musteriler = musteriler.filter(tier__icontains=tier_filtre)
    if q_musteri:
        musteriler = musteriler.filter(
            Q(ad__icontains=q_musteri) |
            Q(kisa_ad__icontains=q_musteri) |
            Q(ulke__icontains=q_musteri) |
            Q(sehir__icontains=q_musteri) |
            Q(kod__icontains=q_musteri) |
            Q(strateji__icontains=q_musteri)
        )

    # İstatistikler ve Rozet Sayıları
    toplam_musteri_sayisi = MusteriKarti.objects.count()
    tier1_sayisi = MusteriKarti.objects.filter(tier__icontains='Tier 1').count()
    tier2_sayisi = MusteriKarti.objects.filter(tier__icontains='Tier 2').count()
    tier3_sayisi = MusteriKarti.objects.filter(tier__icontains='Tier 3').count()

    # 2. Ülkeler Filtreleme
    kanvaslar = HedefPazarKanvas.objects.all()
    oncelik_filtre = request.GET.get('oncelik', 'ALL')
    q_ulke = request.GET.get('q_u', '').strip()

    if oncelik_filtre != 'ALL':
        kanvaslar = kanvaslar.filter(oncelik_sinifi__icontains=oncelik_filtre)
    if q_ulke:
        kanvaslar = kanvaslar.filter(
            Q(ulke_adi__icontains=q_ulke) |
            Q(ulke_kodu__icontains=q_ulke) |
            Q(oncelik_sinifi__icontains=q_ulke) |
            Q(hedef_urunler__icontains=q_ulke) |
            Q(one_cikan_sirketler__icontains=q_ulke)
        )

    # 3. Ürün Grupları Filtreleme
    urun_gruplari = UrunGrubuKarti.objects.all()
    q_urun = request.GET.get('q_p', '').strip()
    if q_urun:
        urun_gruplari = urun_gruplari.filter(
            Q(baslik__icontains=q_urun) |
            Q(kod__icontains=q_urun) |
            Q(ana_fabrika__icontains=q_urun) |
            Q(kabiliyetler__icontains=q_urun) |
            Q(referans_parcalar__icontains=q_urun)
        )

    # İstatistikler
    toplam_musteri_ciro = MusteriKarti.objects.aggregate(Sum('yillik_ciro_eur'))['yillik_ciro_eur__sum'] or 0

    context = {
        'aktif_sekme': aktif_sekme,
        'musteriler': musteriler,
        'toplam_musteri_sayisi': toplam_musteri_sayisi,
        'tier1_sayisi': tier1_sayisi,
        'tier2_sayisi': tier2_sayisi,
        'tier3_sayisi': tier3_sayisi,
        'tier_filtre': tier_filtre,
        'q_m': q_musteri,
        'kanvaslar': kanvaslar,
        'oncelik_filtre': oncelik_filtre,
        'q_u': q_ulke,
        'urun_gruplari': urun_gruplari,
        'q_p': q_urun,
        'toplam_musteri_ciro': toplam_musteri_ciro,
    }
    return render(request, 'crm_takip/kartlar.html', context)


def musteri_360_view(request, pk):
    """
    360° Tek Müşteri Görünümü ve Tesis / Lokasyon Bazlı Yönetim Paneli
    """
    musteri = get_object_or_404(MusteriKarti, pk=pk)
    tesisler = musteri.tesisler.all()
    
    # Otomatik default tesis oluşturma (eğer henüz tanımlanmamışsa)
    if not tesisler.exists():
        MusteriTesisi.objects.create(
            musteri=musteri,
            sira=1,
            tesis_adi="Tüm Tesisler (Grup Özeti)",
            lokasyon=f"{musteri.sehir or ''}, {musteri.ulke}".strip(', '),
            kod=f"{musteri.kisa_ad}-ALL",
            clv_m=f"{musteri.clv_m_str} M€",
            churn_skoru="0.05",
            churn_durumu="Düşük Risk",
            yillik_ciro_str=f"€ {musteri.yillik_ciro_m_str}M",
            ciro_alt_bilgi="Aktif Portföy",
            cuzdan_payi_yuzde=musteri.cuzdan_payi_yuzde,
            cuzdan_alt_bilgi="Sac & Kablo Grubu",
            destek_sayisi=9,
            npi_proje_sayisi=musteri.aktif_proje_sayisi,
            teklif_sayisi=9,
            sevkiyat_sayisi=9,
            kam_satis_lideri=musteri.kam_satis_lideri,
            kam_muhendislik_lideri=musteri.kam_muhendislik_lideri,
            kam_kalite_lideri=musteri.kam_kalite_lideri,
            yetkili_adi=f"{musteri.kisa_ad} Satınalma Lideri",
            yetkili_unvan="Global Satınalma Direktörü",
            yetkili_email=f"contact@{musteri.kisa_ad.lower().replace(' ', '')}.com",
            son_etkilesim="Dün 14:30 - Yeni SIMPAC 400T Kalıp İncelemesi"
        )
        tesisler = musteri.tesisler.all()

    # Zaman Tüneli Etkileşimleri
    etkilesimler = musteri.etkilesimler.all()
    if not etkilesimler.exists():
        MusteriEtkilesimZamanTuneli.objects.create(
            musteri=musteri,
            kod="SAT-EK-005",
            baslik=f"SAT-EK-005 {musteri.kisa_ad} Resmi Fiyat Teklifi Hazırlandı",
            aciklama=f"{musteri.kisa_ad} üretim hatları için 120.000 adetlik yıllık teklif eBA onayına iletildi.",
            sorumlu=musteri.kam_satis_lideri,
            tarih=timezone.now().date(),
            donem_ay_yil="EYLÜL 2026 (SON ETKİLEŞİMLER)",
            ikon="bi-file-earmark-text-fill",
            ikon_bg="bg-warning text-white"
        )
        MusteriEtkilesimZamanTuneli.objects.create(
            musteri=musteri,
            kod="PMG-EK-002",
            baslik="PMG-EK-002 DFM Kalıp Fizibilite Onayı",
            aciklama="SIMPAC 400 Ton Pres kalıp büküm toleransları ±0.1mm onaylandı.",
            sorumlu=musteri.kam_muhendislik_lideri,
            tarih=timezone.now().date(),
            donem_ay_yil="EYLÜL 2026 (SON ETKİLEŞİMLER)",
            ikon="bi-gear-wide-connected",
            ikon_bg="bg-primary text-white"
        )
        etkilesimler = musteri.etkilesimler.all()

    # Dönem bazında gruplama (EYLÜL 2026, AĞUSTOS 2026 vb.)
    donem_gruplari = {}
    for etk in etkilesimler:
        donem = etk.donem_ay_yil
        if donem not in donem_gruplari:
            donem_gruplari[donem] = []
        donem_gruplari[donem].append(etk)

    # Tesisler JSON verisi (Client-side dinamik geçiş için)
    tesisler_data = []
    for t in tesisler:
        tesisler_data.append({
            'id': t.id,
            'tesis_adi': t.tesis_adi,
            'lokasyon': t.lokasyon,
            'kod': t.kod or '',
            'clv_m': t.clv_m,
            'churn_skoru': t.churn_skoru,
            'churn_durumu': t.churn_durumu,
            'yillik_ciro_str': t.yillik_ciro_str,
            'ciro_alt_bilgi': t.ciro_alt_bilgi,
            'cuzdan_payi_yuzde': t.cuzdan_payi_yuzde,
            'cuzdan_alt_bilgi': t.cuzdan_alt_bilgi,
            'destek_sayisi': t.destek_sayisi,
            'npi_proje_sayisi': t.npi_proje_sayisi,
            'teklif_sayisi': t.teklif_sayisi,
            'sevkiyat_sayisi': t.sevkiyat_sayisi,
            'kam_satis_lideri': t.kam_satis_lideri,
            'kam_muhendislik_lideri': t.kam_muhendislik_lideri,
            'kam_kalite_lideri': t.kam_kalite_lideri,
            'yetkili_adi': t.yetkili_adi,
            'yetkili_unvan': t.yetkili_unvan,
            'yetkili_email': t.yetkili_email,
            'yetkili_telefon': t.yetkili_telefon or '',
            'son_etkilesim': t.son_etkilesim
        })

    # Diğer Müşteriler (hızlı geçiş menüsü için)
    diger_musteriler = MusteriKarti.objects.exclude(pk=musteri.pk)

    # İlgili Süreçler
    pazarlama_projeleri = PazarlamaProjesi.objects.filter(
        Q(musteri_karti=musteri) | Q(musteri_adi__icontains=musteri.kisa_ad)
    )

    context = {
        'musteri': musteri,
        'tesisler': tesisler,
        'ilk_tesis': tesisler.first(),
        'donem_gruplari': donem_gruplari,
        'tesisler_json': json.dumps(tesisler_data, ensure_ascii=False),
        'diger_musteriler': diger_musteriler,
        'pazarlama_projeleri': pazarlama_projeleri,
    }
    return render(request, 'crm_takip/musteri_360_detay.html', context)


def kanvas_listesi(request):
    """
    Eski URL desteği için yönlendirme
    """
    return redirect(f"/kartlar/?tab=ulkeler&ulke={request.GET.get('ulke', 'DE')}")


def proje_olustur(request):
    if request.method == 'POST':
        kod = request.POST.get('kod', '').strip()
        ad = request.POST.get('ad', '').strip()
        musteri_adi = request.POST.get('musteri_adi', '').strip()
        hedef_ulke = request.POST.get('hedef_ulke', '').strip()
        urun_grubu = request.POST.get('urun_grubu', 'Metal Parca & Sac')
        ilgili_fabrika = request.POST.get('ilgili_fabrika', 'PRESHANE')
        sorumlu_pazarlama_uzmani = request.POST.get('sorumlu_pazarlama_uzmani', 'BUSE NUR BALTACIOĞLU').strip()
        sorumlu_satis_muduru = request.POST.get('sorumlu_satis_muduru', 'ONUR TUNCER').strip()
        tahmini_butce = request.POST.get('tahmini_butce') or None
        beklenen_ciro = request.POST.get('beklenen_ciro') or None
        aciklama = request.POST.get('aciklama', '').strip()

        year = timezone.now().year
        
        # 1. Otomatik veya manuel kod çakışma önleyici
        if not kod:
            num = 1
            while PazarlamaProjesi.objects.filter(kod=f"PRJ-{year}-{num:03d}").exists():
                num += 1
            kod = f"PRJ-{year}-{num:03d}"
        else:
            if PazarlamaProjesi.objects.filter(kod=kod).exists():
                base_kod = kod
                suffix = 1
                while PazarlamaProjesi.objects.filter(kod=f"{base_kod}-{suffix:02d}").exists():
                    suffix += 1
                kod = f"{base_kod}-{suffix:02d}"
                messages.warning(request, f"'{base_kod}' proje kodu zaten mevcut olduğu için yeni fırsat '{kod}' koduyla açıldı.")

        # İlişkili Müşteri Kartı
        musteri_karti = MusteriKarti.objects.filter(
            Q(kisa_ad__icontains=musteri_adi) | Q(ad__icontains=musteri_adi)
        ).first()

        # Hedef Ülke Kanvası
        kanvas = HedefPazarKanvas.objects.filter(
            Q(ulke_adi__icontains=hedef_ulke) | Q(ulke_kodu__iexact=hedef_ulke)
        ).first()

        # Ürün Grubu Kartı
        ug_karti = UrunGrubuKarti.objects.filter(
            Q(baslik__icontains=urun_grubu[:10]) | Q(kod__icontains=urun_grubu[:5])
        ).first()

        try:
            proje = PazarlamaProjesi.objects.create(
                kod=kod,
                ad=ad,
                musteri_adi=musteri_adi,
                musteri_karti=musteri_karti,
                hedef_ulke=hedef_ulke,
                hedef_pazar_kanvasi=kanvas,
                urun_grubu=urun_grubu,
                urun_grubu_karti=ug_karti,
                ilgili_fabrika=ilgili_fabrika,
                sorumlu_pazarlama_uzmani=sorumlu_pazarlama_uzmani,
                sorumlu_satis_muduru=sorumlu_satis_muduru,
                tahmini_butce=tahmini_butce,
                beklenen_ciro=beklenen_ciro,
                aciklama=aciklama,
                durum='DEVAM_EDIYOR',
                guncel_adim_no=1
            )
        except Exception:
            # Nadir eşzamanlı çakışma durumunda garantili benzersiz kod
            import time
            unique_ts = int(time.time()) % 100000
            kod = f"PRJ-{year}-{unique_ts:05d}"
            proje = PazarlamaProjesi.objects.create(
                kod=kod,
                ad=ad,
                musteri_adi=musteri_adi,
                musteri_karti=musteri_karti,
                hedef_ulke=hedef_ulke,
                hedef_pazar_kanvasi=kanvas,
                urun_grubu=urun_grubu,
                urun_grubu_karti=ug_karti,
                ilgili_fabrika=ilgili_fabrika,
                sorumlu_pazarlama_uzmani=sorumlu_pazarlama_uzmani,
                sorumlu_satis_muduru=sorumlu_satis_muduru,
                tahmini_butce=tahmini_butce,
                beklenen_ciro=beklenen_ciro,
                aciklama=aciklama,
                durum='DEVAM_EDIYOR',
                guncel_adim_no=1
            )

        adim_tanimlari = SurecAdimTanimi.objects.all().order_by('adim_no')
        for adim in adim_tanimlari:
            durum = 'DEVAM_EDIYOR' if adim.adim_no == 1 else 'BEKLIYOR'
            ProjeAdimKaydi.objects.create(
                proje=proje,
                adim=adim,
                durum=durum
            )

        ProjeGecmisLog.objects.create(
            proje=proje,
            islem="Pazarlama Süreci Başlatıldı",
            detay=f"{proje.musteri_adi} firması için pazarlama süreci oluşturuldu. 1. Adım başlatıldı.",
            yapan=sorumlu_pazarlama_uzmani or "Sistem"
        )

        messages.success(request, f"'{proje.kod} - {proje.ad}' pazarlama süreci başarıyla başlatıldı.")
        return redirect('proje_detay', pk=proje.pk)

    return redirect('dashboard')


def proje_detay(request, pk):
    proje = get_object_or_404(PazarlamaProjesi, pk=pk)
    adim_kayitlari = proje.adim_kayitlari.select_related('adim').order_by('adim__adim_no')
    gecmis_loglar = proje.tarihce_kayitlari.all()[:15]
    
    ulke_kanvasi = proje.hedef_pazar_kanvasi
    if not ulke_kanvasi and proje.hedef_ulke:
        ulke_kanvasi = HedefPazarKanvas.objects.filter(
            Q(ulke_adi__icontains=proje.hedef_ulke) | Q(ulke_kodu__iexact=proje.hedef_ulke)
        ).first()

    fazlar = [
        {
            'kod': 'FAZ1',
            'baslik': 'Faz 1: Pazar & Strateji Planlama',
            'adimlar': [a for a in adim_kayitlari if a.adim.adim_no in range(1, 7)]
        },
        {
            'kod': 'FAZ2',
            'baslik': 'Faz 2: Müşteri Teması & Talep Toplama',
            'adimlar': [a for a in adim_kayitlari if a.adim.adim_no in range(7, 11)]
        },
        {
            'kod': 'FAZ3',
            'baslik': 'Faz 3: Ön Mutabakat & Değerlendirme',
            'adimlar': [a for a in adim_kayitlari if a.adim.adim_no in range(11, 13)]
        },
        {
            'kod': 'FAZ4',
            'baslik': 'Faz 4: Tedarikçi Onayı, Teklif & Kapanış',
            'adimlar': [a for a in adim_kayitlari if a.adim.adim_no in range(13, 16)]
        },
    ]

    context = {
        'proje': proje,
        'adim_kayitlari': adim_kayitlari,
        'fazlar': fazlar,
        'gecmis_loglar': gecmis_loglar,
        'tarihce': gecmis_loglar,
        'ulke_kanvasi': ulke_kanvasi,
        'musteri_karti': proje.musteri_karti,
        'urun_grubu_karti': proje.urun_grubu_karti,
    }
    return render(request, 'crm_takip/proje_detay.html', context)


def adim_aksiyon(request, pk, adim_no):
    proje = get_object_or_404(PazarlamaProjesi, pk=pk)
    adim_kaydi = get_object_or_404(ProjeAdimKaydi, proje=proje, adim__adim_no=adim_no)
    
    if request.method == 'POST':
        aksiyon = request.POST.get('aksiyon', 'TAMAMLA')
        notlar = request.POST.get('notlar', '').strip()
        dokuman_ref = request.POST.get('dokuman_referansi', '').strip()
        tamamlayan = request.POST.get('tamamlayan', 'Kullanıcı').strip() or 'Kullanıcı'

        dokumanlar_secili = request.POST.getlist('dokumanlar')
        platformlar_secili = request.POST.getlist('platformlar')
        adim_kaydi.tamamlanan_dokumanlar = "\n".join(dokumanlar_secili)
        adim_kaydi.tamamlanan_platformlar = "\n".join(platformlar_secili)

        if notlar:
            adim_kaydi.notlar = notlar
        if dokuman_ref:
            adim_kaydi.dokuman_referansi = dokuman_ref
        if tamamlayan:
            adim_kaydi.tamamlayan = tamamlayan

        # ARA KAYDET / NOT VE DOKÜMAN GÜNCELLEME EYLEMİ
        if aksiyon in ['KAYDET', 'GUNCELLE']:
            if adim_kaydi.durum == 'BEKLIYOR':
                adim_kaydi.durum = 'DEVAM_EDIYOR'
            adim_kaydi.save()

            ProjeGecmisLog.objects.create(
                proje=proje,
                islem=f"Adım {adim_no}: Doküman / Notlar Kaydedildi",
                detay=f"Adım ara doküman kontrolleri ve açıklama güncellendi. Not: {notlar or 'Girilmedi.'}",
                yapan=tamamlayan
            )
            messages.success(request, f"Adım {adim_no} doküman ve not bilgileri başarıyla kaydedildi.")
            return redirect('proje_detay', pk=proje.pk)

        now = timezone.now()
        adim_kaydi.tamamlanma_tarihi = now

        # 1. STANDART ADIMLAR (1, 2, 3, 4, 5, 7, 8, 13)
        if adim_no in [1, 2, 3, 4, 5, 7, 8, 13]:
            adim_kaydi.durum = 'TAMAMLANDI'
            adim_kaydi.karar_sonucu = 'Tamamlandı'
            adim_kaydi.save()

            sonraki_no = adim_no + 1
            proje.guncel_adim_no = sonraki_no
            proje.save()

            sonraki_kayit = ProjeAdimKaydi.objects.filter(proje=proje, adim__adim_no=sonraki_no).first()
            if sonraki_kayit:
                sonraki_kayit.durum = 'DEVAM_EDIYOR'
                sonraki_kayit.save()

            ProjeGecmisLog.objects.create(
                proje=proje,
                islem=f"Adım {adim_no} Tamamlandı",
                detay=f"{adim_kaydi.adim.baslik} tamamlandı. Sonraki adım: Adım {sonraki_no}.",
                yapan=tamamlayan
            )
            messages.success(request, f"Adım {adim_no} başarıyla tamamlandı. Süreç Adım {sonraki_no}'e geçti.")

        # 2. ADIM 6: Pazarlama Faaliyet ve Bütçe Planı Uygun mu?
        elif adim_no == 6:
            if aksiyon == 'EVET':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'EVET (Bütçe ve Plan Uygun)'
                adim_kaydi.save()

                proje.guncel_adim_no = 7
                proje.save()
                ProjeAdimKaydi.objects.filter(proje=proje, adim__adim_no=7).update(durum='DEVAM_EDIYOR')

                ProjeGecmisLog.objects.create(
                    proje=proje,
                    islem="Adım 6: Bütçe ve Plan Onaylandı",
                    detay="Üst yönetim pazarlama faaliyet ve bütçe planını onayladı. Adım 7 (İlk Temas) başlatıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "Bütçe ve plan onaylandı! Süreç 7. Adıma aktarıldı.")

            elif aksiyon == 'HAYIR':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'HAYIR (Revizyon Gerekli -> Adım 4)'
                adim_kaydi.save()

                proje.guncel_adim_no = 4
                proje.durum = 'REVIZYONDA'
                proje.save()
                ProjeAdimKaydi.objects.filter(proje=proje, adim__adim_no=4).update(durum='DEVAM_EDIYOR')
                ProjeAdimKaydi.objects.filter(proje=proje, adim__adim_no__in=[5, 6]).update(durum='BEKLIYOR', karar_sonucu=None)

                ProjeGecmisLog.objects.create(
                    proje=proje,
                    islem="Adım 6: Bütçe ve Plan Revizyona Gönderildi",
                    detay=f"Gerekçe: {notlar or 'Bütçe/faaliyet revizyonu gerekli.'} Plan yeniden hazırlanmak üzere 4. Adıma yönlendirildi.",
                    yapan=tamamlayan
                )
                messages.warning(request, "Plan revizyon için 4. Adıma geri yönlendirildi.")

        # 3. ADIM 9: Müşteri Talep ve Beklentileri Karşılanabilir mi?
        elif adim_no == 9:
            if aksiyon == 'DEGERLENDIRME_TAMAM':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'Değerlendirme Tamamlandı'
                adim_kaydi.save()

                proje.guncel_adim_no = 10
                proje.save()
                ProjeAdimKaydi.objects.filter(proje=proje, adim__adim_no=10).update(durum='DEVAM_EDIYOR')

                ProjeGecmisLog.objects.create(
                    proje=proje,
                    islem="Adım 9: Karşılanabilirlik Değerlendirmesi Tamamlandı",
                    detay="Müşteri talep/fizibilite değerlendirmesi karara bağlandı. 10. Adıma (Müşteri Bildirimi) geçildi.",
                    yapan=tamamlayan
                )
                messages.success(request, "Değerlendirme karara bağlandı. Müşteriye bildirim için 10. Adıma geçildi.")

            elif aksiyon == 'ILAVE_BILGI':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'İlave Bilgi / Yeniden Değerlendirme -> Adım 8'
                adim_kaydi.save()

                proje.guncel_adim_no = 8
                proje.durum = 'REVIZYONDA'
                proje.save()
                ProjeAdimKaydi.objects.filter(proje=proje, adim__adim_no=8).update(durum='DEVAM_EDIYOR')
                ProjeAdimKaydi.objects.filter(proje=proje, adim__adim_no=9).update(durum='BEKLIYOR', karar_sonucu=None)

                ProjeGecmisLog.objects.create(
                    proje=proje,
                    islem="Adım 9: İlave Bilgi Talebi",
                    detay=f"İlave teknik/ticari bilgi gerektiğinden 8. Adıma geri dönüldü. Not: {notlar}",
                    yapan=tamamlayan
                )
                messages.info(request, "İlave bilgi/talep alımı için 8. Adıma geri yönlendirildi.")

        # 4. ADIM 10: Değerlendirme Sonucunun Müşteriye Bildirilmesi
        elif adim_no == 10:
            if aksiyon == 'MUTABAKATA_GEC':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'Müşteri Bildirimi Tamamlandı -> 11. Adım'
                adim_kaydi.save()

                proje.guncel_adim_no = 11
                proje.save()
                ProjeAdimKaydi.objects.filter(proje=proje, adim__adim_no=11).update(durum='DEVAM_EDIYOR')

                ProjeGecmisLog.objects.create(
                    proje=proje,
                    islem="Adım 10: Bildirim ve Geri Bildirim Alındı",
                    detay="Müşteriye bildirim yapıldı ve geri bildirim alındı. Ön mutabakat değerlendirmesi için 11. Adıma geçildi.",
                    yapan=tamamlayan
                )
                messages.success(request, "Geri bildirim işlendi. 11. Adıma geçildi.")

            elif aksiyon == 'YENIDEN_DEGERLENDIR':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'Müşteri Değişiklik İstedi -> Adım 8'
                adim_kaydi.save()

                proje.guncel_adim_no = 8
                proje.durum = 'REVIZYONDA'
                proje.save()
                ProjeAdimKaydi.objects.filter(proje=proje, adim__adim_no=8).update(durum='DEVAM_EDIYOR')
                ProjeAdimKaydi.objects.filter(proje=proje, adim__adim_no__in=[9, 10]).update(durum='BEKLIYOR', karar_sonucu=None)

                ProjeGecmisLog.objects.create(
                    proje=proje,
                    islem="Adım 10: Müşteri Değişiklik Talebi",
                    detay=f"Müşteri değişiklik istediğinden teknik değerlendirme için 8. Adıma geri dönüldü. Not: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Müşteri talep revizyonu için 8. Adıma geri yönlendirildi.")

        # 5. ADIM 11: Karşılıklı Ön Mutabakat Sağlandı mı?
        elif adim_no == 11:
            if aksiyon == 'EVET':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'EVET (Ön Mutabakat Sağlandı)'
                adim_kaydi.save()

                proje.guncel_adim_no = 12
                proje.save()
                ProjeAdimKaydi.objects.filter(proje=proje, adim__adim_no=12).update(durum='DEVAM_EDIYOR')

                ProjeGecmisLog.objects.create(
                    proje=proje,
                    islem="Adım 11: Ön Mutabakat Sağlandı",
                    detay="Müşteri ile teknik ve ticari koşullarda ön mutabakat sağlandı. 12. Adıma (Tedarikçi Değerlendirme Kontrolü) geçildi.",
                    yapan=tamamlayan
                )
                messages.success(request, "Müşteri ile ön mutabakat sağlandı! 12. Adıma geçildi.")

            elif aksiyon == 'HAYIR':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'HAYIR (Ön Mutabakat Sağlanamadı -> Adım 15)'
                adim_kaydi.save()

                ProjeAdimKaydi.objects.filter(proje=proje, adim__adim_no__in=[12, 13, 14]).update(durum='PAS_GECILDI')
                proje.guncel_adim_no = 15
                proje.durum = 'OLUMSUZ_KAPATILDI'
                proje.save()
                ProjeAdimKaydi.objects.filter(proje=proje, adim__adim_no=15).update(durum='DEVAM_EDIYOR')

                ProjeGecmisLog.objects.create(
                    proje=proje,
                    islem="Adım 11: Ön Mutabakat Sağlanamadı",
                    detay=f"Ön mutabakat sağlanamadığı için süreç kapanış amacıyla 15. Adıma aktarıldı. Gerekçe: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Ön mutabakat sağlanamadı. Süreç kapanış ve raporlama için 15. Adıma aktarıldı.")

            elif aksiyon == 'ILAVE_BILGI':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'İlave Bilgi / Yeniden Değerlendirme -> Adım 8'
                adim_kaydi.save()

                proje.guncel_adim_no = 8
                proje.durum = 'REVIZYONDA'
                proje.save()
                ProjeAdimKaydi.objects.filter(proje=proje, adim__adim_no=8).update(durum='DEVAM_EDIYOR')
                ProjeAdimKaydi.objects.filter(proje=proje, adim__adim_no__in=[9, 10, 11]).update(durum='BEKLIYOR', karar_sonucu=None)

                ProjeGecmisLog.objects.create(
                    proje=proje,
                    islem="Adım 11: İlave Bilgi İhtiyacı",
                    detay="Ön mutabakat için ilave teknik/ticari değerlendirme gerektiğinden 8. Adıma dönüldü.",
                    yapan=tamamlayan
                )
                messages.info(request, "İlave değerlendirme için 8. Adıma dönüldü.")

        # 6. ADIM 12: RFQ Öncesinde Tedarikçi Değerlendirmesi Gerekli mi?
        elif adim_no == 12:
            if aksiyon == 'EVET':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'EVET (Tedarikçi Değerlendirmesi Gerekli -> Adım 13)'
                adim_kaydi.save()

                proje.guncel_adim_no = 13
                proje.save()
                ProjeAdimKaydi.objects.filter(proje=proje, adim__adim_no=13).update(durum='DEVAM_EDIYOR')

                ProjeGecmisLog.objects.create(
                    proje=proje,
                    islem="Adım 12: Tedarikçi Değerlendirmesi Gerekli",
                    detay="Müşterinin tedarikçi denetim/onay süreci talep ettiği netleşti. 13. Adım başlatıldı.",
                    yapan=tamamlayan
                )
                messages.info(request, "Müşteri tedarikçi denetimi talep etti. 13. Adıma geçildi.")

            elif aksiyon == 'GECERLI_ONAY_VAR':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'HAYIR / Geçerli Onay Var -> Doğrudan Ürün Teklif Sürecine Aktarıldı'
                adim_kaydi.save()

                ProjeAdimKaydi.objects.filter(proje=proje, adim__adim_no__in=[13, 14, 15]).update(durum='PAS_GECILDI')
                proje.durum = 'TEKLIF_SURECINDE'
                proje.guncel_adim_no = 12
                proje.save()

                ProjeGecmisLog.objects.create(
                    proje=proje,
                    islem="Ürün Teklif Sürecine Aktarıldı",
                    detay="Geçerli tedarikçi onayı mevcut olduğundan denetim adımları pas geçilerek proje doğrudan Ürün Teklif Sürecine aktarıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "Tebrikler! Geçerli onay mevcut olduğundan proje doğrudan Ürün Teklif Sürecine aktarıldı!")

        # 7. ADIM 14: Müşterinin Tedarikçi Değerlendirme Süreci Olumlu Sonuçlandı mı?
        elif adim_no == 14:
            if aksiyon == 'OLUMLU':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'OLUMLU (Tedarikçi Onayı Alındı -> Ürün Teklif Süreci)'
                adim_kaydi.save()

                ProjeAdimKaydi.objects.filter(proje=proje, adim__adim_no=15).update(durum='PAS_GECILDI')
                proje.durum = 'TEKLIF_SURECINDE'
                proje.guncel_adim_no = 14
                proje.save()

                ProjeGecmisLog.objects.create(
                    proje=proje,
                    islem="Müşteri Tedarikçi Onayı Alındı -> Teklif Süreci",
                    detay="Müşteri nezdindeki tedarikçi değerlendirmesi OLUMLU sonuçlandı. Proje Ürün Teklif Sürecine aktarıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "Tedarikçi değerlendirmesi başarıyla tamamlandı! Proje Ürün Teklif Sürecine aktarıldı.")

            elif aksiyon == 'KOSULLU_AKSIYON':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'Koşullu Onay / Aksiyon Gerekli -> Adım 13'
                adim_kaydi.save()

                proje.guncel_adim_no = 13
                proje.durum = 'REVIZYONDA'
                proje.save()
                ProjeAdimKaydi.objects.filter(proje=proje, adim__adim_no=13).update(durum='DEVAM_EDIYOR')
                ProjeAdimKaydi.objects.filter(proje=proje, adim__adim_no=14).update(durum='BEKLIYOR', karar_sonucu=None)

                ProjeGecmisLog.objects.create(
                    proje=proje,
                    islem="Adım 14: Koşullu Onay (Aksiyon Takibi)",
                    detay=f"Müşteri bulgularına ilişkin aksiyonların tamamlanması için 13. Adıma geri dönüldü. Not: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Koşullu onay aksiyonları için 13. Adıma dönüldü.")

            elif aksiyon == 'OLUMSUZ':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'OLUMSUZ -> Adım 15 (Kapanış)'
                adim_kaydi.save()

                proje.guncel_adim_no = 15
                proje.durum = 'OLUMSUZ_KAPATILDI'
                proje.save()
                ProjeAdimKaydi.objects.filter(proje=proje, adim__adim_no=15).update(durum='DEVAM_EDIYOR')

                ProjeGecmisLog.objects.create(
                    proje=proje,
                    islem="Adım 14: Tedarikçi Değerlendirmesi Olumsuz",
                    detay=f"Tedarikçi değerlendirmesi olumsuz sonuçlandı. Süreç kapanış için 15. Adıma aktarıldı. Gerekçe: {notlar}",
                    yapan=tamamlayan
                )
                messages.error(request, "Tedarikçi değerlendirmesi olumsuz sonuçlandı. Kapanış için 15. Adıma yönlendirildi.")

        # 8. ADIM 15: Sürecin Kapatılması ve Sonuçların Raporlanması
        elif adim_no == 15:
            adim_kaydi.durum = 'TAMAMLANDI'
            adim_kaydi.karar_sonucu = 'Süreç Kapatıldı & Raporlandı'
            adim_kaydi.save()

            if proje.durum not in ['TEKLIF_SURECINDE', 'OLUMSUZ_KAPATILDI']:
                proje.durum = 'BASARIYLA_KAPATILDI'
            proje.guncel_adim_no = 15
            proje.save()

            ProjeGecmisLog.objects.create(
                proje=proje,
                islem="Pazarlama Süreci Kapatıldı",
                detay=f"Pazarlama süreci CRM üzerinde kapatıldı. Öğrenilmiş dersler ve sonuçlar raporlandı. Not: {notlar}",
                yapan=tamamlayan
            )
            messages.info(request, "Pazarlama süreci başarıyla kapatıldı ve raporlandı.")

    return redirect(f"{redirect('proje_detay', pk=pk).url}#adim-{proje.guncel_adim_no}")


def proje_sil(request, pk):
    proje = get_object_or_404(PazarlamaProjesi, pk=pk)
    if request.method == 'POST':
        kod = proje.kod
        proje.delete()
        messages.success(request, f"'{kod}' kodlu proje başarıyla silindi.")
    return redirect('dashboard')


# ==============================================================================
# MÜŞTERİ İLİŞKİLERİ SÜRECİ (EYS-EK-028) GÖRÜNÜMLERİ
# ==============================================================================

def musteri_iliskileri_liste(request):
    """
    EYS-EK-028 Müşteri İlişkileri Süreci Listesi & İstatistik Paneli
    """
    surecler = MusteriIliskileriSureci.objects.all()

    q = request.GET.get('q', '').strip()
    durum_filtre = request.GET.get('durum', '')
    fabrika_filtre = request.GET.get('fabrika', '')
    donem_filtre = request.GET.get('donem', '')

    if q:
        surecler = surecler.filter(
            Q(kod__icontains=q) |
            Q(musteri_adi__icontains=q) |
            Q(ad__icontains=q)
        )
    if durum_filtre:
        surecler = surecler.filter(durum=durum_filtre)
    if fabrika_filtre:
        surecler = surecler.filter(ilgili_fabrika=fabrika_filtre)
    if donem_filtre:
        surecler = surecler.filter(donem__icontains=donem_filtre)

    toplam_surec = MusteriIliskileriSureci.objects.count()
    aktif_surec = MusteriIliskileriSureci.objects.filter(durum='DEVAM_EDIYOR').count()
    uygunsuzluk_surec = MusteriIliskileriSureci.objects.filter(durum='UYGUNSUZLUK_YONETIMINDE').count()
    tamamlanan_surec = MusteriIliskileriSureci.objects.filter(durum='BASARIYLA_TAMAMLANDI').count()
    
    avg_memnuniyet = MusteriIliskileriSureci.objects.filter(memnuniyet_puani__isnull=False).aggregate(Avg('memnuniyet_puani'))['memnuniyet_puani__avg']
    avg_memnuniyet_val = round(avg_memnuniyet, 1) if avg_memnuniyet else 85.0

    context = {
        'surecler': surecler,
        'musteriler': MusteriKarti.objects.all(),
        'toplam_surec': toplam_surec,
        'aktif_surec': aktif_surec,
        'uygunsuzluk_surec': uygunsuzluk_surec,
        'tamamlanan_surec': tamamlanan_surec,
        'avg_memnuniyet': avg_memnuniyet_val,
        'q': q,
        'durum_filtre': durum_filtre,
        'fabrika_filtre': fabrika_filtre,
        'donem_filtre': donem_filtre,
        'fabrikalar': PazarlamaProjesi.FABRIKA_CHOICES,
        'durum_listesi': MusteriIliskileriSureci.DURUM_CHOICES,
    }
    return render(request, 'crm_takip/musteri_iliskileri_liste.html', context)


def musteri_iliskileri_olustur(request):
    """
    Yeni Müşteri İlişkileri Süreci Başlatma (EYS-EK-028 Standart 11 Adım)
    """
    if request.method == 'POST':
        kod = request.POST.get('kod', '').strip()
        ad = request.POST.get('ad', '').strip()
        musteri_adi = request.POST.get('musteri_adi', '').strip()
        donem = request.POST.get('donem', '2026 Yıllık').strip()
        ilgili_fabrika = request.POST.get('ilgili_fabrika', 'PRESHANE')
        sorumlu_eys = request.POST.get('sorumlu_eys', 'BUSE NUR BALTACIOĞLU')
        sorumlu_surec_sahibi = request.POST.get('sorumlu_surec_sahibi', 'ONUR TUNCER')
        memnuniyet_puani = request.POST.get('memnuniyet_puani')
        aciklama = request.POST.get('aciklama', '').strip()

        year = timezone.now().year

        # Otomatik ve çakışmasız kod üretimi
        if not kod:
            counter = 1
            while True:
                candidate_kod = f"MIS-{year}-{counter:03d}"
                if not MusteriIliskileriSureci.objects.filter(kod=candidate_kod).exists():
                    kod = candidate_kod
                    break
                counter += 1
        else:
            if MusteriIliskileriSureci.objects.filter(kod=kod).exists():
                counter = 1
                base_kod = kod
                while True:
                    candidate_kod = f"{base_kod}-{counter:02d}"
                    if not MusteriIliskileriSureci.objects.filter(kod=candidate_kod).exists():
                        kod = candidate_kod
                        break
                    counter += 1
                messages.warning(request, f"Belirttiğiniz süreç kodu mevcut olduğu için benzersiz olarak '{kod}' atandı.")

        # İlişkili Müşteri Kartı
        musteri_karti = MusteriKarti.objects.filter(
            Q(ad__icontains=musteri_adi) | Q(kisa_ad__icontains=musteri_adi)
        ).first()

        try:
            surec = MusteriIliskileriSureci.objects.create(
                kod=kod,
                ad=ad,
                musteri_adi=musteri_adi,
                musteri_karti=musteri_karti,
                donem=donem,
                ilgili_fabrika=ilgili_fabrika,
                sorumlu_eys=sorumlu_eys,
                sorumlu_surec_sahibi=sorumlu_surec_sahibi,
                memnuniyet_puani=float(memnuniyet_puani) if memnuniyet_puani else None,
                aciklama=aciklama,
                durum='DEVAM_EDIYOR',
                guncel_adim_no=1
            )
        except Exception as e:
            messages.error(request, f"Süreç oluşturulurken bir hata oluştu: {str(e)}")
            return redirect('musteri_iliskileri_liste')

        # 11 Standart Adım Kaydının Oluşturulması
        master_adimlar = MusteriIliskileriAdimTanimi.objects.all().order_by('adim_no')
        for adim in master_adimlar:
            durum = 'DEVAM_EDIYOR' if adim.adim_no == 1 else 'BEKLIYOR'
            dokuman = adim.ilgili_dokumanlar.split(',')[0] if adim.ilgili_dokumanlar else ""
            MusteriIliskileriAdimKaydi.objects.create(
                surec=surec,
                adim=adim,
                durum=durum,
                dokuman_referansi=dokuman
            )

        # İlk Log Kaydı
        MusteriIliskileriGecmisLog.objects.create(
            surec=surec,
            islem="Müşteri İlişkileri Süreci Başlatıldı",
            detay=f"EYS-EK-028 standardında 11 adımlık süreç başlatıldı. Başlangıç Adımı: 1. Müşterilerin Tanımlanması. (Dönem: {donem})",
            yapan=sorumlu_eys
        )

        messages.success(request, f"'{surec.kod}' kodlu Müşteri İlişkileri Süreci başarıyla başlatıldı.")
        return redirect('musteri_iliskileri_detay', pk=surec.pk)

    return redirect('musteri_iliskileri_liste')


def musteri_iliskileri_detay(request, pk):
    """
    EYS-EK-028 11 Adımlık İnteraktif Süreç Takip ve Karar Ağacı Ekranı
    """
    surec = get_object_or_404(MusteriIliskileriSureci, pk=pk)
    adim_kayitlari = surec.adim_kayitlari.select_related('adim').order_by('adim__adim_no')

    # Faz grupları (Pazarlama süreciyle birebir aynı yapı)
    fazlar = [
        {
            'faz_kodu': 'FAZ1',
            'baslik': 'FAZ 1: Müşteri Tanımlama & İhtiyaç Analizi',
            'adimlar': [k for k in adim_kayitlari if k.adim.faz == 'FAZ1']
        },
        {
            'faz_kodu': 'FAZ2',
            'baslik': 'FAZ 2: Performans Ölçümü & Kriter Kontrolü',
            'adimlar': [k for k in adim_kayitlari if k.adim.faz == 'FAZ2']
        },
        {
            'faz_kodu': 'FAZ3',
            'baslik': 'FAZ 3: Memnuniyet Anketleri & İyileştirme Aksiyonları',
            'adimlar': [k for k in adim_kayitlari if k.adim.faz == 'FAZ3']
        },
        {
            'faz_kodu': 'FAZ4',
            'baslik': 'FAZ 4: YGG Raporlama & Dijital İzleme',
            'adimlar': [k for k in adim_kayitlari if k.adim.faz == 'FAZ4']
        }
    ]

    tarihce = surec.tarihce_kayitlari.all().order_by('-tarih')

    context = {
        'surec': surec,
        'adim_kayitlari': adim_kayitlari,
        'fazlar': fazlar,
        'tarihce': tarihce,
        'musteri_karti': surec.musteri_karti,
    }
    return render(request, 'crm_takip/musteri_iliskileri_detay.html', context)


def musteri_iliskileri_adim_aksiyon(request, pk, adim_id):
    """
    EYS-EK-028 Adım İlerletme, Ara Kaydetme, Karar Kapısı (Adım 6 OK/NOK) ve Uygunsuzluk Yönetimi
    """
    surec = get_object_or_404(MusteriIliskileriSureci, pk=pk)
    adim_kaydi = MusteriIliskileriAdimKaydi.objects.filter(pk=adim_id, surec=surec).first()
    if not adim_kaydi:
        adim_kaydi = get_object_or_404(MusteriIliskileriAdimKaydi, adim__adim_no=adim_id, surec=surec)
    
    adim_no = adim_kaydi.adim.adim_no

    if request.method == 'POST':
        aksiyon = request.POST.get('aksiyon', '').strip() or request.POST.get('karar', '').strip() or 'TAMAMLA'
        notlar = request.POST.get('notlar', '').strip()
        tamamlayan = request.POST.get('tamamlayan', 'EYS Sorumlusu').strip() or 'EYS Sorumlusu'
        
        if notlar:
            adim_kaydi.notlar = notlar
        if tamamlayan:
            adim_kaydi.tamamlayan = tamamlayan

        # ARA KAYDET / NOT GÜNCELLEME EYLEMİ
        if aksiyon in ['KAYDET', 'GUNCELLE']:
            if adim_kaydi.durum == 'BEKLIYOR':
                adim_kaydi.durum = 'DEVAM_EDIYOR'
            adim_kaydi.save()

            MusteriIliskileriGecmisLog.objects.create(
                surec=surec,
                islem=f"Adım {adim_no}: Notlar Kaydedildi",
                detay=f"Adım açıklama ve değerlendirme notları güncellendi. Not: {notlar or 'Girilmedi.'}",
                yapan=tamamlayan
            )
            messages.success(request, f"Adım {adim_no} not ve değerlendirme bilgileri başarıyla kaydedildi.")
            return redirect(f"{redirect('musteri_iliskileri_detay', pk=surec.pk).url}#adim-{adim_no}")

        now = timezone.now()
        adim_kaydi.tamamlanma_tarihi = now

        # 1. STANDART ADIMLAR (1, 2, 3, 4, 5, 7, 8, 9, 10)
        if adim_no in [1, 2, 3, 4, 5, 7, 8, 9, 10]:
            adim_kaydi.durum = 'TAMAMLANDI'
            adim_kaydi.karar_sonucu = 'Tamamlandı'
            adim_kaydi.save()

            sonraki_adim_no = adim_no + 1
            surec.guncel_adim_no = sonraki_adim_no
            surec.save()

            sonraki_adim_kaydi = MusteriIliskileriAdimKaydi.objects.filter(surec=surec, adim__adim_no=sonraki_adim_no).first()
            if sonraki_adim_kaydi:
                sonraki_adim_kaydi.durum = 'DEVAM_EDIYOR'
                sonraki_adim_kaydi.save()

            MusteriIliskileriGecmisLog.objects.create(
                surec=surec,
                islem=f"Adım {adim_no} Tamamlandı",
                detay=f"{adim_kaydi.adim.baslik} tamamlandı. {sonraki_adim_no}. Adıma geçildi.",
                yapan=tamamlayan
            )
            messages.success(request, f"Adım {adim_no} başarıyla tamamlandı. Süreç Adım {sonraki_adim_no}'e geçti.")

        # 2. ADIM 6: KARAR KAPISI (Belirlenen performans kriterleri sağlanabildi mi?)
        elif adim_no == 6:
            karar = aksiyon

            if karar == 'EVET_OK':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'OK (Performans Kriterleri Sağlandı)'
                adim_kaydi.save()

                surec.durum = 'DEVAM_EDIYOR'
                surec.guncel_adim_no = 7
                surec.save()

                MusteriIliskileriAdimKaydi.objects.filter(surec=surec, adim__adim_no=7).update(durum='DEVAM_EDIYOR')

                MusteriIliskileriGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 6: Performans Kriterleri Onaylandı (OK)",
                    detay=f"Performans kriterleri sağlandı. 7. Adım Müşteri Memnuniyet Anketleri aşamasına geçildi. Değerlendirme: {notlar}",
                    yapan=tamamlayan
                )
                messages.success(request, "Performans kriterleri sağlandı (OK). 7. Adıma geçildi.")

            elif karar == 'HAYIR_NOK':
                adim_kaydi.durum = 'UYGUNSUZLUK_ACILDI'
                adim_kaydi.karar_sonucu = 'NOK (Sağlanamadı - Uygunsuzluk Sürecine Yönlendirildi)'
                adim_kaydi.save()

                surec.durum = 'UYGUNSUZLUK_YONETIMINDE'
                surec.guncel_adim_no = 6
                surec.save()

                MusteriIliskileriGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 6: Performans Kriteri Sağlanamadı (NOK)",
                    detay=f"Performans kriterleri sağlanamadı. Süreç 'Uygunsuzluk Yönetimi Süreci'ne (DÖF) yönlendirildi. Gerekçe: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Performans kriterleri sağlanamadığı için süreç 'Uygunsuzluk Yönetimi Süreci'ne (DÖF) yönlendirildi.")

            elif karar == 'UYGUNSUZLUK_COZULDU':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'DÖF Çözüldü & Kriterler Sağlandı -> Adım 7'
                adim_kaydi.save()

                surec.durum = 'DEVAM_EDIYOR'
                surec.guncel_adim_no = 7
                surec.save()

                MusteriIliskileriAdimKaydi.objects.filter(surec=surec, adim__adim_no=7).update(durum='DEVAM_EDIYOR')

                MusteriIliskileriGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 6: Uygunsuzluk Yönetimi (DÖF) Tamamlandı",
                    detay=f"Düzeltici faaliyetler tamamlandı ve onaylandı. Süreç 7. Adım ile devam ediyor. Not: {notlar}",
                    yapan=tamamlayan
                )
                messages.success(request, "Uygunsuzluk süreci tamamlandı ve kriterler doğrulandı. 7. Adıma geçildi.")

        # 3. ADIM 11: Süreç Etkinliği, Dijitalleşme & Deneyim Paylaşımı (Kapanış)
        elif adim_no == 11:
            adim_kaydi.durum = 'TAMAMLANDI'
            adim_kaydi.karar_sonucu = 'Süreç Tamamlandı & Dijital Ortama Aktarıldı'
            adim_kaydi.save()

            surec.durum = 'BASARIYLA_TAMAMLANDI'
            surec.guncel_adim_no = 11
            surec.save()

            MusteriIliskileriGecmisLog.objects.create(
                surec=surec,
                islem="Müşteri İlişkileri Süreci Tamamlandı",
                detay=f"EYS-EK-028 Müşteri İlişkileri Süreci başarıyla tamamlandı, sonuçlar dijital ortama aktarıldı ve YGG ile paylaşıldı. Kapanış Notu: {notlar}",
                yapan=tamamlayan
            )
            messages.info(request, "Müşteri İlişkileri Süreci başarıyla tamamlandı ve arşivlendi.")

    return redirect(f"{redirect('musteri_iliskileri_detay', pk=pk).url}#adim-{surec.guncel_adim_no}")


def musteri_iliskileri_sil(request, pk):
    surec = get_object_or_404(MusteriIliskileriSureci, pk=pk)
    if request.method == 'POST':
        kod = surec.kod
        surec.delete()
        messages.success(request, f"'{kod}' kodlu Müşteri İlişkileri Süreci başarıyla silindi.")
    return redirect('musteri_iliskileri_liste')


# ==============================================================================
# ÜRÜN TEKLİF SÜRECİ (15 ADIM) GÖRÜNÜMLERİ
# ==============================================================================

def urun_teklif_liste(request):
    """
    Ürün Teklif Süreci Listesi & İstatistik Paneli (16 Master Adım ve Dallanmalar)
    """
    surecler = UrunTeklifSureci.objects.all()

    q = request.GET.get('q', '').strip()
    durum_filtre = request.GET.get('durum', '')
    fabrika_filtre = request.GET.get('fabrika', '')
    donem_filtre = request.GET.get('donem', '')
    urun_filtre = request.GET.get('urun_grubu', '')

    if q:
        surecler = surecler.filter(
            Q(kod__icontains=q) |
            Q(musteri_adi__icontains=q) |
            Q(ad__icontains=q)
        )
    if durum_filtre:
        surecler = surecler.filter(durum=durum_filtre)
    if fabrika_filtre:
        surecler = surecler.filter(ilgili_fabrika=fabrika_filtre)
    if donem_filtre:
        surecler = surecler.filter(donem__icontains=donem_filtre)
    if urun_filtre:
        surecler = surecler.filter(urun_grubu=urun_filtre)

    toplam_surec = UrunTeklifSureci.objects.count()
    aktif_surec = UrunTeklifSureci.objects.filter(durum__in=['DEVAM_EDIYOR', 'REVIZYONDA', 'YONETIM_ONAYINDA']).count()
    iletilen_surec = UrunTeklifSureci.objects.filter(durum='MUSTERIYE_ILETILDI').count()
    tamamlanan_surec = UrunTeklifSureci.objects.filter(durum='BASARIYLA_TAMAMLANDI').count()
    
    toplam_teklif_tutari = UrunTeklifSureci.objects.aggregate(Sum('teklif_tutari'))['teklif_tutari__sum'] or 0

    pazarlama_uzmanlari = get_proje_liderleri()
    intranet_sirketler = get_intranet_sirketler()

    context = {
        'surecler': surecler,
        'musteriler': MusteriKarti.objects.all(),
        'toplam_surec': toplam_surec,
        'aktif_surec': aktif_surec,
        'iletilen_surec': iletilen_surec,
        'tamamlanan_surec': tamamlanan_surec,
        'toplam_teklif_tutari': toplam_teklif_tutari,
        'toplam_tutar_eur': toplam_teklif_tutari,
        'q': q,
        'durum_filtre': durum_filtre,
        'fabrika_filtre': fabrika_filtre,
        'donem_filtre': donem_filtre,
        'urun_filtre': urun_filtre,
        'fabrikalar': PazarlamaProjesi.FABRIKA_CHOICES,
        'urun_gruplari': PazarlamaProjesi.URUN_GRUBU_CHOICES,
        'durum_listesi': UrunTeklifSureci.DURUM_CHOICES,
        'pazarlama_uzmanlari': pazarlama_uzmanlari,
        'intranet_sirketler': intranet_sirketler,
    }
    return render(request, 'crm_takip/urun_teklif_liste.html', context)


def urun_teklif_olustur(request):
    """
    Yeni Ürün Teklif Süreci Başlatma (Resmi Prosedür 16 Master Adım ve Dallanmalar)
    """
    if request.method == 'POST':
        kod = request.POST.get('kod', '').strip()
        ad = request.POST.get('ad', '').strip()
        musteri_adi = request.POST.get('musteri_adi', '').strip()
        musteri_karti_id = request.POST.get('musteri_karti_id', '').strip()
        donem = request.POST.get('donem', '2026 Yıllık').strip()
        ilgili_fabrika = request.POST.get('ilgili_fabrika', 'PRESHANE')
        urun_grubu = request.POST.get('urun_grubu', 'Metal Parca & Sac')
        sorumlu_satis_analiz_uzmani = request.POST.get('sorumlu_satis_analiz_uzmani', 'METİN YAVAŞ')
        sorumlu_satis_uzmani = request.POST.get('sorumlu_satis_uzmani', 'BUSE NUR BALTACIOĞLU')
        sorumlu_satis_yoneticisi = request.POST.get('sorumlu_satis_yoneticisi', 'ONUR TUNCER')
        teklif_tutari_val = request.POST.get('teklif_tutari') or request.POST.get('beklenen_ciro')
        aciklama = request.POST.get('aciklama', '').strip()

        year = timezone.now().year

        if not kod:
            counter = 1
            while True:
                candidate_kod = f"TEK-{year}-{counter:03d}"
                if not UrunTeklifSureci.objects.filter(kod=candidate_kod).exists():
                    kod = candidate_kod
                    break
                counter += 1
        else:
            if UrunTeklifSureci.objects.filter(kod=kod).exists():
                counter = 1
                base_kod = kod
                while True:
                    candidate_kod = f"{base_kod}-{counter:02d}"
                    if not UrunTeklifSureci.objects.filter(kod=candidate_kod).exists():
                        kod = candidate_kod
                        break
                    counter += 1
                messages.warning(request, f"Belirttiğiniz teklif kodu mevcut olduğu için benzersiz olarak '{kod}' atandı.")

        musteri_karti = None
        if musteri_karti_id:
            musteri_karti = MusteriKarti.objects.filter(pk=musteri_karti_id).first()
        if not musteri_karti and musteri_adi:
            musteri_karti = MusteriKarti.objects.filter(
                Q(ad__icontains=musteri_adi) | Q(kisa_ad__icontains=musteri_adi)
            ).first()

        try:
            surec = UrunTeklifSureci.objects.create(
                kod=kod,
                ad=ad,
                musteri_adi=musteri_adi,
                musteri_karti=musteri_karti,
                donem=donem,
                ilgili_fabrika=ilgili_fabrika,
                urun_grubu=urun_grubu,
                sorumlu_satis_analiz_uzmani=sorumlu_satis_analiz_uzmani,
                sorumlu_satis_uzmani=sorumlu_satis_uzmani,
                sorumlu_satis_yoneticisi=sorumlu_satis_yoneticisi,
                teklif_tutari=float(teklif_tutari_val) if teklif_tutari_val else None,
                aciklama=aciklama,
                durum='DEVAM_EDIYOR',
                guncel_adim_kodu='1',
                guncel_adim_no=1
            )
        except Exception as e:
            messages.error(request, f"Ürün teklif süreci oluşturulurken bir hata oluştu: {str(e)}")
            return redirect('urun_teklif_liste')

        master_adimlar = UrunTeklifAdimTanimi.objects.all().order_by('sira_no')
        for adim in master_adimlar:
            durum = 'DEVAM_EDIYOR' if adim.adim_kodu == '1' else 'BEKLIYOR'
            dokuman = adim.ilgili_dokumanlar.split(',')[0].strip() if adim.ilgili_dokumanlar else ""
            UrunTeklifAdimKaydi.objects.create(
                surec=surec,
                adim=adim,
                durum=durum,
                dokuman_referansi=dokuman
            )

        UrunTeklifGecmisLog.objects.create(
            surec=surec,
            islem="Ürün Teklif Süreci Başlatıldı",
            detay=f"Resmi Ürün Teklif Süreci başlatıldı. Başlangıç Adımı: 1. RFQ/Teklif Talebinin Alınması ve Ön Kontrolü. (Dönem: {donem})",
            yapan=sorumlu_satis_uzmani
        )

        messages.success(request, f"'{surec.kod}' kodlu Ürün Teklif Süreci başarıyla başlatıldı.")
        return redirect('urun_teklif_detay', pk=surec.pk)

    return redirect('urun_teklif_liste')


def urun_teklif_detay(request, pk):
    """
    16 Adımlık İnteraktif Ürün Teklif Süreci Takip ve Karar Ekranı (Master Modal & Faz Bazlı)
    """
    surec = get_object_or_404(UrunTeklifSureci, pk=pk)
    adim_kayitlari = surec.adim_kayitlari.select_related('adim').order_by('adim__sira_no')

    # Faz grupları (4 Faz)
    fazlar = [
        {
            'faz_kodu': 'FAZ1',
            'baslik': 'FAZ 1: RFQ Alımı & Ön Fizibilite (Adım 1-4C)',
            'adimlar': [k for k in adim_kayitlari if k.adim.faz == 'FAZ1']
        },
        {
            'faz_kodu': 'FAZ2',
            'baslik': 'FAZ 2: Maliyet & Fiyatlandırma (Adım 5-9C)',
            'adimlar': [k for k in adim_kayitlari if k.adim.faz == 'FAZ2']
        },
        {
            'faz_kodu': 'FAZ3',
            'baslik': 'FAZ 3: Yönetim Onayı & Müşteri Müzakeresi (Adım 10-15C)',
            'adimlar': [k for k in adim_kayitlari if k.adim.faz == 'FAZ3']
        },
        {
            'faz_kodu': 'FAZ4',
            'baslik': 'FAZ 4: Teklif Sonucu, Devreye Alma & Kapanış (Adım 16-16C)',
            'adimlar': [k for k in adim_kayitlari if k.adim.faz == 'FAZ4']
        }
    ]

    tarihce = surec.tarihce_kayitlari.all().order_by('-tarih')
    proje_liderleri = get_proje_liderleri()
    master_adimlar = UrunTeklifAdimTanimi.objects.all().order_by('sira_no')

    context = {
        'surec': surec,
        'adim_kayitlari': adim_kayitlari,
        'fazlar': fazlar,
        'tarihce': tarihce,
        'musteri_karti': surec.musteri_karti,
        'proje_liderleri': proje_liderleri,
        'master_adimlar': master_adimlar,
    }
    return render(request, 'crm_takip/urun_teklif_detay.html', context)


def urun_teklif_adim_aksiyon(request, pk, adim_id):
    """
    Ürün Teklif Süreci Adım İlerletme, Karar Kapıları ve İlgili Adıma Geri Dönüş Yönetimi (40 İstasyon)
    """
    surec = get_object_or_404(UrunTeklifSureci, pk=pk)
    adim_kaydi = UrunTeklifAdimKaydi.objects.filter(pk=adim_id, surec=surec).first()
    if not adim_kaydi:
        adim_kaydi = UrunTeklifAdimKaydi.objects.filter(adim__adim_kodu=str(adim_id), surec=surec).first()
    if not adim_kaydi:
        adim_kaydi = get_object_or_404(UrunTeklifAdimKaydi, adim__adim_no=adim_id, surec=surec)
    
    adim_kodu = adim_kaydi.adim.adim_kodu

    if request.method == 'POST':
        aksiyon = request.POST.get('aksiyon', '').strip() or request.POST.get('karar', '').strip() or 'TAMAMLA'
        notlar = request.POST.get('notlar', '').strip()
        tamamlayan = request.POST.get('tamamlayan', 'Satış Uzmanı').strip() or 'Satış Uzmanı'
        
        if notlar:
            adim_kaydi.notlar = notlar
        if tamamlayan:
            adim_kaydi.tamamlayan = tamamlayan

        # ARA KAYDET / NOT GÜNCELLEME
        if aksiyon in ['KAYDET', 'GUNCELLE']:
            if adim_kaydi.durum == 'BEKLIYOR':
                adim_kaydi.durum = 'DEVAM_EDIYOR'
            adim_kaydi.save()

            UrunTeklifGecmisLog.objects.create(
                surec=surec,
                islem=f"Adım {adim_kodu}: Notlar Kaydedildi",
                detay=f"Adım açıklama ve değerlendirme notları güncellendi. Not: {notlar or 'Girilmedi.'}",
                yapan=tamamlayan
            )
            messages.success(request, f"Adım {adim_kodu} not ve değerlendirme bilgileri başarıyla kaydedildi.")
            return redirect(f"{redirect('urun_teklif_detay', pk=surec.pk).url}#adim-{adim_kodu}")

        def _gecis(hedef_kod, karar_metni, log_islem, log_detay, yeni_durum=None, msg_type='success', msg_text=None):
            adim_kaydi.durum = 'TAMAMLANDI'
            adim_kaydi.karar_sonucu = karar_metni
            adim_kaydi.tamamlanma_tarihi = timezone.now()
            adim_kaydi.save()

            hedef = UrunTeklifAdimKaydi.objects.filter(surec=surec, adim__adim_kodu=hedef_kod).first()
            if hedef:
                hedef.durum = 'DEVAM_EDIYOR'
                hedef.save()

            surec.guncel_adim_kodu = hedef_kod
            num_part = ''.join(filter(str.isdigit, hedef_kod))
            if num_part:
                surec.guncel_adim_no = int(num_part)
            if yeni_durum:
                surec.durum = yeni_durum
            surec.save()

            UrunTeklifGecmisLog.objects.create(
                surec=surec,
                islem=log_islem,
                detay=log_detay,
                yapan=tamamlayan
            )
            if msg_text:
                getattr(messages, msg_type)(request, msg_text)

        # -------------------------------------------------------------
        # 1. ADIM 1: RFQ/Teklif Talebinin Alınması ve Ön Kontrolü
        # -------------------------------------------------------------
        if adim_kodu == '1':
            _gecis('2', 'Tamamlandı', 'Adım 1: RFQ Alımı ve Ön Kontrol Tamamlandı',
                   f"RFQ ve teknik şartnameler incelendi, ön kontroller tamamlandı. Adım 2'ye geçildi. Not: {notlar}",
                   msg_text="Adım 1 tamamlandı. 2. Adıma (Çalışma Takvimi) geçildi.")

        # -------------------------------------------------------------
        # 2. ADIM 2: Teklif Çalışma Takviminin Belirlenmesi ve İş Bölümü
        # -------------------------------------------------------------
        elif adim_kodu == '2':
            _gecis('3', 'Tamamlandı', 'Adım 2: Çalışma Takvimi Belirlendi',
                   f"Teklif teslim tarihi ve birim iş bölümü takvime bağlandı. Adım 3'e geçildi. Not: {notlar}",
                   msg_text="Adım 2 tamamlandı. 3. Adıma (Talebin Sınıflandırılması) geçildi.")

        # -------------------------------------------------------------
        # 3. ADIM 3: Teklif Talebinin Sınıflandırılması ve Yönlendirme
        # -------------------------------------------------------------
        elif adim_kodu == '3':
            if aksiyon == '3A':
                _gecis('3A', 'Mevcut Ürün Fiyat Revizyonu Talebi (3A)', 'Adım 3: Fiyat Revizyonu Olarak Sınıflandırıldı',
                       f"Talep mevcut ürün fiyat revizyonu olarak sınıflandırıldı. Adım 3A'ya yönlendirildi. Not: {notlar}",
                       msg_text="Talep 'Mevcut Ürün Fiyat Revizyonu' (Adım 3A) olarak sınıflandırıldı.")
            elif aksiyon == '3B':
                _gecis('3B', 'Mevcut Müşteri Yeni/Revize Parça Teklifi (3B)', 'Adım 3: Mevcut Müşteri Yeni Parça Olarak Sınıflandırıldı',
                       f"Talep mevcut müşteri yeni/revize parça olarak sınıflandırıldı. Adım 3B'ye yönlendirildi. Not: {notlar}",
                       msg_text="Talep 'Mevcut Müşteri Yeni/Revize Parça' (Adım 3B) olarak sınıflandırıldı.")
            elif aksiyon == '3C':
                _gecis('3C', 'Yeni Müşteri / Yeni İş Teklifi (3C)', 'Adım 3: Yeni Müşteri / Yeni İş Olarak Sınıflandırıldı',
                       f"Talep yeni müşteri / yeni iş teklifi olarak sınıflandırıldı. Adım 3C'ye yönlendirildi. Not: {notlar}",
                       msg_text="Talep 'Yeni Müşteri / Yeni İş Teklifi' (Adım 3C) olarak sınıflandırıldı.")
            else:
                _gecis('4', 'Tamamlandı', 'Adım 3: Sınıflandırma Tamamlandı', f"Teklif sınıflandırıldı. Not: {notlar}")

        # -------------------------------------------------------------
        # 4. ADIM 3A: Mevcut Ürün Fiyat Revizyonu Süreci
        # -------------------------------------------------------------
        elif adim_kodu == '3A':
            if aksiyon in ['TEKNIK_YOK_5', 'ADIM_5', 'EVET']:
                _gecis('5', 'Teknik Değişiklik Yok -> Adım 5 Detaylı Maliyet Analizi', 'Adım 3A: Teknik Değişiklik Yok',
                       f"Teknik/üretimsel değişiklik olmadığından doğrudan maliyet güncellemesi için 5. Adıma aktarıldı. Not: {notlar}",
                       msg_text="Teknik değişiklik bulunmadığından doğrudan 5. Adıma (Maliyet Analizi) geçildi.")
            elif aksiyon in ['TEKNIK_VAR_3B', 'ADIM_3B', 'HAYIR']:
                _gecis('3B', 'Teknik Değişiklik Var -> Adım 3B Yeni/Revize Parça', 'Adım 3A: Teknik Değişiklik Var',
                       f"Kalıp/proses veya teknik değişiklik içerdiğinden 3B Adımına aktarıldı. Not: {notlar}",
                       msg_text="Teknik/kalıp değişikliği içerdiğinden 3B Adımına yönlendirildi.")
            else:
                _gecis('5', 'Tamamlandı', 'Adım 3A: Tamamlandı', f"Fiyat revizyon adımı tamamlandı. Not: {notlar}")

        # -------------------------------------------------------------
        # 5. ADIM 3B: Mevcut Müşteri Yeni / Revize Parça Teklifi
        # -------------------------------------------------------------
        elif adim_kodu == '3B':
            _gecis('4', 'Mevcut Müşteri Parça Talebi Doğrulandı -> Adım 4', 'Adım 3B: Parça Talebi Doğrulandı',
                   f"Mevcut müşteri parça talebi doğrulandı ve 4. Adım Fizibilite Değerlendirmesine aktarıldı. Not: {notlar}",
                   msg_text="3B Adımı tamamlandı. 4. Adıma (Fizibilite ve Risk Değerlendirmesi) geçildi.")

        # -------------------------------------------------------------
        # 6. ADIM 3C: Yeni Müşteri / Yeni İş Teklifi
        # -------------------------------------------------------------
        elif adim_kodu == '3C':
            if aksiyon in ['UYGUN_4', 'ADIM_4', 'EVET', 'TAMAMLA']:
                _gecis('4', 'Müşteri Şartları Uygun -> Adım 4 Fizibilite', 'Adım 3C: Yeni Müşteri Şartları Uygun',
                       f"Yeni müşteri onay ve ticari şartları uygun bulundu. 4. Adım Fizibiliteye aktarıldı. Not: {notlar}",
                       msg_text="Yeni müşteri şartları uygun bulundu. 4. Adıma (Fizibilite) geçildi.")
            elif aksiyon in ['OLUMSUZ_16C', 'ADIM_16C', 'HAYIR']:
                _gecis('16C', 'Müşteri Şartları Uygun Değil -> 16C Olumsuz Kapatma', 'Adım 3C: Yeni Müşteri Şartları Uygun Değil',
                       f"Yeni müşteri ticari/onay şartları karşılanamadığı için süreç 16C Adımında olumsuz kapatıldı. Not: {notlar}",
                       yeni_durum='OLUMSUZ_KAPATILDI', msg_type='warning',
                       msg_text="Yeni müşteri şartları karşılanamadı. Süreç 16C Adımına aktarıldı.")

        # -------------------------------------------------------------
        # 7. ADIM 4: Fizibilite ve Risk Değerlendirmesi
        # -------------------------------------------------------------
        elif adim_kodu == '4':
            if aksiyon in ['4A', 'OLUMLU_5', 'EVET']:
                _gecis('4A', 'Fizibilite Olumlu (4A)', 'Adım 4: Fizibilite Olumlu Sonuçlandı',
                       f"Teknik, mali ve operasyonel fizibilite onaylandı. Adım 4A'ya geçildi. Not: {notlar}",
                       msg_text="Fizibilite değerlendirmesi olumlu sonuçlandı (Adım 4A).")
            elif aksiyon in ['4B', 'UYGUNSUZ_4B', 'HAYIR']:
                _gecis('4B', 'Fizibilite Uygun Değil (4B)', 'Adım 4: Fizibilite Uygun Bulunmadı',
                       f"Kapasite veya teknik kısıtlar nedeniyle uygun bulunmadı. Adım 4B'ye yönlendirildi. Not: {notlar}",
                       msg_type='warning', msg_text="Fizibilite uygun bulunmadı. Adım 4B'ye yönlendirildi.")
            elif aksiyon in ['4C', 'ILAVE_CALISMA_4C']:
                _gecis('4C', 'İlave Bilgi / Risk İyileştirme Gerekli (4C)', 'Adım 4: İlave Bilgi / Risk İyileştirme',
                       f"Risk iyileştirme veya müşteri netleştirmesi gerektiği belirlendi. Adım 4C'ye geçildi. Not: {notlar}",
                       msg_type='info', msg_text="İlave bilgi ve risk çalışması için Adım 4C'ye geçildi.")
            else:
                _gecis('5', 'Tamamlandı', 'Adım 4: Fizibilite Tamamlandı', f"Fizibilite tamamlandı. Not: {notlar}")

        # -------------------------------------------------------------
        # 8. ADIM 4A: Fizibilite ve Risk Değerlendirmesi Olumlu
        # -------------------------------------------------------------
        elif adim_kodu == '4A':
            _gecis('5', 'Fizibilite Onaylandı -> Adım 5 Detaylı Maliyet Analizi', 'Adım 4A: Fizibilite Onaylandı',
                   f"Fizibilite olumlu onaylandı. 5. Adım Detaylı Maliyet Analizi başlatıldı. Not: {notlar}",
                   msg_text="Adım 4A tamamlandı. 5. Adıma (Detaylı Maliyet Analizi) geçildi.")

        # -------------------------------------------------------------
        # 9. ADIM 4B: Fizibilite ve Risk Değerlendirmesi Uygun Değil
        # -------------------------------------------------------------
        elif adim_kodu == '4B':
            if aksiyon in ['ILAVE_CALISMA_4C', '4C']:
                _gecis('4C', 'Müşteri ile Görüşme / Risk İyileştirme -> Adım 4C', 'Adım 4B: Risk İyileştirme Kararı',
                       f"Kısıtların aşılması için müşteri ile görüşme kararı alındı. Adım 4C'ye geçildi. Not: {notlar}",
                       msg_text="Risk iyileştirme ve müşteri görüşmesi için 4C Adımına geçildi.")
            elif aksiyon in ['OLUMSUZ_16C', '16C', 'KAPAT']:
                _gecis('16C', 'Fizibilite Reddedildi -> 16C Olumsuz Kapatma', 'Adım 4B: Fizibilite Reddedildi',
                       f"Fizibilite uygun bulunmadığından teklif çalışması sonlandırıldı. 16C Adımına aktarıldı. Not: {notlar}",
                       yeni_durum='OLUMSUZ_KAPATILDI', msg_type='warning',
                       msg_text="Teklif süreci fizibilite yetersizliği nedeniyle 16C Adımında olumsuz kapatıldı.")

        # -------------------------------------------------------------
        # 10. ADIM 4C: İlave Bilgi / Müşteri ile Görüşme / Risk İyileştirme
        # -------------------------------------------------------------
        elif adim_kodu == '4C':
            if aksiyon in ['YENIDEN_FIZIBILITE_4', '4']:
                _gecis('4', 'Bilgiler Tamamlandı -> Yeniden Fizibilite (Adım 4)', 'Adım 4C: Fizibiliteye Geri Dönüldü',
                       f"Müşteri açıklamaları sonrası yeniden fizibilite değerlendirmesi için 4. Adıma dönüldü. Not: {notlar}",
                       msg_text="İlave bilgilerle yeniden fizibilite değerlendirmesi için 4. Adıma geçildi.")
            elif aksiyon in ['TALEP_REVIZYON_3B', '3B']:
                _gecis('3B', 'Talep Kapsamına Geri Dönüldü (Adım 3B)', 'Adım 4C: Talep Kapsamı Revizyonu',
                       f"Teknik şartname revizyonu sebebiyle 3B Adımına dönüldü. Not: {notlar}",
                       msg_text="Talep kapsamı revizyonu için 3B Adımına geri dönüldü.")
            elif aksiyon in ['OLUMSUZ_16C', '16C', 'KAPAT']:
                _gecis('16C', 'Riskler Giderilemedi -> 16C Olumsuz Kapatma', 'Adım 4C: Riskler Giderilemedi',
                       f"Müşteri ile uzlaşılamadı, süreç 16C Adımına yönlendirildi. Not: {notlar}",
                       yeni_durum='OLUMSUZ_KAPATILDI', msg_type='warning',
                       msg_text="Riskler giderilemediğinden süreç 16C Adımına aktarıldı.")

        # -------------------------------------------------------------
        # 11. ADIM 5: Detaylı Maliyet Analizinin Yapılması
        # -------------------------------------------------------------
        elif adim_kodu == '5':
            _gecis('6', 'Maliyet Analizi Tamamlandı -> Adım 6', 'Adım 5: Maliyet Analizi Tamamlandı',
                   f"Hammadde, işçilik, fason, ambalaj, enerji ve genel gider maliyetleri hesaplandı. Adım 6'ya geçildi. Not: {notlar}",
                   msg_text="Adım 5 tamamlandı. 6. Adıma (Teklif Özet Tablosu) geçildi.")

        # -------------------------------------------------------------
        # 12. ADIM 6: Teklif Özet Tablosunun ve Fiyat Taslağının Hazırlanması
        # -------------------------------------------------------------
        elif adim_kodu == '6':
            _gecis('7', 'Teklif Özet Tablosu Hazırlandı -> Adım 7', 'Adım 6: Teklif Özet Tablosu Hazırlandı',
                   f"Maliyet kalemleri ve fiyat taslağı özet tabloda konsolide edildi. Adım 7'ye geçildi. Not: {notlar}",
                   msg_text="Adım 6 tamamlandı. 7. Adıma (Maliyet Doğrulama) geçildi.")

        # -------------------------------------------------------------
        # 13. ADIM 7: Maliyet ve Fiyat Verilerinin Doğrulanması
        # -------------------------------------------------------------
        elif adim_kodu == '7':
            if aksiyon in ['7A', 'DOGRULANDI_8', 'EVET', 'TAMAMLA']:
                _gecis('7A', 'Maliyet ve Fiyat Doğrulandı (7A)', 'Adım 7: Maliyet ve Fiyat Doğrulandı',
                       f"Maliyet hesaplamaları, birim girdiler ve katsayılar doğrulandı. Adım 7A'ya geçildi. Not: {notlar}",
                       msg_text="Maliyet ve fiyat verileri doğrulandı (Adım 7A).")
            elif aksiyon in ['7B', 'DUZELTME_7B', 'HAYIR']:
                _gecis('7B', 'Düzeltme / Yeniden Hesaplama Gerekli (7B)', 'Adım 7: Düzeltme İhtiyacı Tespit Edildi',
                       f"Maliyet verilerinde uyumsuzluk belirlendi. Adım 7B'ye yönlendirildi. Not: {notlar}",
                       msg_type='warning', msg_text="Maliyet verilerinde düzeltme gerektiği tespit edildi (Adım 7B).")

        # -------------------------------------------------------------
        # 14. ADIM 7A: Maliyet ve Fiyat Doğrulandı
        # -------------------------------------------------------------
        elif adim_kodu == '7A':
            _gecis('8', 'Doğrulandı -> Adım 8 Satış Fiyatlandırması', 'Adım 7A: Doğrulama Onaylandı',
                   f"Doğrulanmış veri seti ile 8. Adım Satış Fiyatlandırmasına geçildi. Not: {notlar}",
                   msg_text="Adım 7A tamamlandı. 8. Adıma (Satış Fiyatlandırması) geçildi.")

        # -------------------------------------------------------------
        # 15. ADIM 7B: Maliyet ve Fiyat Düzeltme / Yeniden Hesaplama
        # -------------------------------------------------------------
        elif adim_kodu == '7B':
            if aksiyon in ['MALIYET_5', '5']:
                _gecis('5', 'Maliyet Analizine Geri Dönüldü (Adım 5)', 'Adım 7B: Maliyet Analizine Revizyon',
                       f"Girdi maliyeti düzeltmesi için 5. Adıma dönüldü. Not: {notlar}",
                       msg_text="Maliyet analizi düzeltmesi için 5. Adıma geri dönüldü.")
            elif aksiyon in ['OZET_6', '6']:
                _gecis('6', 'Teklif Özet Tablosuna Geri Dönüldü (Adım 6)', 'Adım 7B: Özet Tablo Revizyonu',
                       f"Konsolidasyon tablosu düzeltmesi için 6. Adıma dönüldü. Not: {notlar}",
                       msg_text="Teklif özet tablosu düzeltmesi için 6. Adıma geri dönüldü.")

        # -------------------------------------------------------------
        # 16. ADIM 8: Satış Fiyatlandırmasının ve Ticari Koşulların Belirlenmesi
        # -------------------------------------------------------------
        elif adim_kodu == '8':
            _gecis('9', 'Fiyatlandırma ve Ticari Koşullar Belirlendi -> Adım 9', 'Adım 8: Fiyatlandırma Tamamlandı',
                   f"Kâr marjı, ödeme/teslim koşulları ve hedef çarpan hesaplandı. Adım 9'a geçildi. Not: {notlar}",
                   msg_text="Adım 8 tamamlandı. 9. Adıma (Hedef Çarpan Kontrolü) geçildi.")

        # -------------------------------------------------------------
        # 17. ADIM 9: Hedef Çarpan ve Kârlılık Uygunluk Kontrolü
        # -------------------------------------------------------------
        elif adim_kodu == '9':
            if aksiyon in ['9A', 'UYGUN_10', 'EVET', 'TAMAMLA']:
                _gecis('9A', 'Hedef Çarpana ve Kriterlere Uygun (9A)', 'Adım 9: Hedef Çarpana Uygun',
                       f"Kârlılık ve hedef çarpan kriterleri sağlandı. Adım 9A'ya geçildi. Not: {notlar}",
                       msg_text="Hedef çarpan ve kârlılık kriterlerine uygun bulundu (Adım 9A).")
            elif aksiyon in ['9B', 'OZEL_ONAY_9B']:
                _gecis('9B', 'Hedef Çarpan Dışı / Özel Onay Gerektiren Teklif (9B)', 'Adım 9: Özel Onay Kapsamı',
                       f"Hedef çarpan altında kaldığından yetki matrisi ilave onayına sevk edildi. Adım 9B'ye geçildi. Not: {notlar}",
                       msg_type='info', msg_text="Özel yetki matrisi onayı gerektiren durum (Adım 9B).")
            elif aksiyon in ['9C', 'REVIZYON_9C', 'HAYIR']:
                _gecis('9C', 'Fiyat ve Koşulların Revizyonu Gerekli (9C)', 'Adım 9: Revizyon Gereksinimi',
                       f"Kârlılık hedeflerine ulaşılamadığı için revizyon kararı alındı. Adım 9C'ye geçildi. Not: {notlar}",
                       msg_type='warning', msg_text="Fiyat revizyonu gerekliliği tespit edildi (Adım 9C).")

        # -------------------------------------------------------------
        # 18. ADIM 9A: Hedef Çarpana ve Kârlılık Kriterlerine Uygun
        # -------------------------------------------------------------
        elif adim_kodu == '9A':
            _gecis('10', 'Uygunluk Onaylandı -> Adım 10 Teklif Dosyası', 'Adım 9A: Uygunluk Onaylandı',
                   f"Hedef çarpan uygunluğu ile 10. Adım Teklif Dosyası hazırlığına geçildi. Not: {notlar}",
                   msg_text="Adım 9A tamamlandı. 10. Adıma (Teklif Dosyası ve Yönetim Onayı) geçildi.")

        # -------------------------------------------------------------
        # 19. ADIM 9B: Hedef Çarpan Dışı / Özel Onay Gerektiren Teklif
        # -------------------------------------------------------------
        elif adim_kodu == '9B':
            _gecis('10', 'Özel Yetki Onayı ile Uygun -> Adım 10 Teklif Dosyası', 'Adım 9B: Özel Yetki Onayı Alındı',
                   f"Stratejik gerekçeler ve yetki matrisi onayı ile 10. Adıma aktarıldı. Not: {notlar}",
                   msg_text="Özel yetki onayı sağlandı. 10. Adıma (Teklif Dosyası) geçildi.")

        # -------------------------------------------------------------
        # 20. ADIM 9C: Fiyat ve Koşulların Revizyonu
        # -------------------------------------------------------------
        elif adim_kodu == '9C':
            if aksiyon in ['FIYAT_8', '8']:
                _gecis('8', 'Fiyatlandırmaya Geri Dönüldü (Adım 8)', 'Adım 9C: Fiyatlandırma Revizyonu',
                       f"Kâr marjı veya ticari koşul düzeltmesi için 8. Adıma dönüldü. Not: {notlar}",
                       msg_text="Fiyatlandırma revizyonu için 8. Adıma dönüldü.")
            elif aksiyon in ['MALIYET_5', '5']:
                _gecis('5', 'Maliyet Analizine Geri Dönüldü (Adım 5)', 'Adım 9C: Maliyet İyileştirme',
                       f"Maliyet optimizasyonu için 5. Adıma dönüldü. Not: {notlar}",
                       msg_text="Maliyet optimizasyonu için 5. Adıma dönüldü.")
            elif aksiyon in ['RFQ_3B', '3B']:
                _gecis('3B', 'Müşteri RFQ Kapsamına Geri Dönüldü (Adım 3B)', 'Adım 9C: Kapsam Değişikliği',
                       f"Talep kapsamı netleştirmesi için 3B Adımına dönüldü. Not: {notlar}",
                       msg_text="Talep kapsamı netleştirmesi için 3B Adımına dönüldü.")

        # -------------------------------------------------------------
        # 21. ADIM 10: Teklif Dosyasının Nihai Hale Getirilmesi ve Yönetim Onayı
        # -------------------------------------------------------------
        elif adim_kodu == '10':
            _gecis('11', 'Teklif Dosyası Hazırlandı -> Adım 11 Yönetim Nihai Onayı', 'Adım 10: Teklif Dosyası Tamamlandı',
                   f"Teklif mektubu ve ekleri hazırlandı, yönetim nihai onayına sunuldu. Adım 11'e geçildi. Not: {notlar}",
                   yeni_durum='YONETIM_ONAYINDA', msg_text="Adım 10 tamamlandı. 11. Adıma (Yönetim Nihai Onayı) geçildi.")

        # -------------------------------------------------------------
        # 22. ADIM 11: Yönetim Nihai Teklif Onayı
        # -------------------------------------------------------------
        elif adim_kodu == '11':
            if aksiyon in ['11A', 'ONAYLANDI_12', 'EVET', 'TAMAMLA']:
                _gecis('11A', 'Teklif Yönetim Tarafından Onaylandı (11A)', 'Adım 11: Yönetim Onayı Alındı',
                       f"Teklif Genel Müdürlük / Yönetimce onaylandı. Adım 11A'ya geçildi. Not: {notlar}",
                       msg_text="Teklif üst yönetim tarafından onaylandı (Adım 11A).")
            elif aksiyon in ['11B', 'SARTLI_ONAY_11B']:
                _gecis('11B', 'Şartlı Onay / Revizyon Talebi (11B)', 'Adım 11: Şartlı Onay / Revizyon',
                       f"Yönetim koşullu onay vererek revizyon istedi. Adım 11B'ye geçildi. Not: {notlar}",
                       yeni_durum='REVIZYONDA', msg_type='warning',
                       msg_text="Yönetim şartlı onay vererek revizyon talep etti (Adım 11B).")
            elif aksiyon in ['11C', 'RET_11C', 'HAYIR']:
                _gecis('11C', 'Teklif Onaylanmadı (11C)', 'Adım 11: Teklif Onaylanmadı',
                       f"Yönetim teklifi mevcut haliyle onaylamadı. Adım 11C'ye aktarıldı. Not: {notlar}",
                       yeni_durum='REVIZYONDA', msg_type='danger',
                       msg_text="Teklif onaylanmadı (Adım 11C).")

        # -------------------------------------------------------------
        # 23. ADIM 11A: Teklif Yönetim Tarafından Onaylandı
        # -------------------------------------------------------------
        elif adim_kodu == '11A':
            _gecis('12', 'Yönetim Onayladı -> Adım 12 Müşteriye Sunum', 'Adım 11A: Yönetim Onayı Kesinleşti',
                   f"Resmi yönetim onayı ile 12. Adım Müşteriye Sunum aşamasına geçildi. Not: {notlar}",
                   msg_text="Adım 11A tamamlandı. 12. Adıma (Müşteriye Sunum) geçildi.")

        # -------------------------------------------------------------
        # 24. ADIM 11B: Şartlı Onay / Revizyon Talebi
        # -------------------------------------------------------------
        elif adim_kodu == '11B':
            if aksiyon in ['FIYAT_8', '8']:
                _gecis('8', 'Fiyatlandırmaya Geri Dönüldü (Adım 8)', 'Adım 11B: Fiyatlandırma Revizyonu',
                       f"Yönetim koşulları doğrultusunda 8. Adıma dönüldü. Not: {notlar}",
                       msg_text="Fiyatlandırma revizyonu için 8. Adıma dönüldü.")
            elif aksiyon in ['MALIYET_5', '5']:
                _gecis('5', 'Maliyet Analizine Geri Dönüldü (Adım 5)', 'Adım 11B: Maliyet Revizyonu',
                       f"Maliyet girdisi revizyonu için 5. Adıma dönüldü. Not: {notlar}",
                       msg_text="Maliyet analizi revizyonu için 5. Adıma dönüldü.")
            elif aksiyon in ['DOSYA_10', '10']:
                _gecis('10', 'Teklif Dosyasına Geri Dönüldü (Adım 10)', 'Adım 11B: Dosya Revizyonu',
                       f"Mektup / şart revizyonu için 10. Adıma dönüldü. Not: {notlar}",
                       msg_text="Teklif dosyası düzenlemesi için 10. Adıma dönüldü.")
            elif aksiyon in ['RFQ_3B', '3B']:
                _gecis('3B', 'RFQ Adımına Geri Dönüldü (Adım 3B)', 'Adım 11B: Kapsam Revizyonu',
                       f"Talep kapsamı değişikliği için 3B Adımına dönüldü. Not: {notlar}",
                       msg_text="Talep kapsamı değişikliği için 3B Adımına dönüldü.")

        # -------------------------------------------------------------
        # 25. ADIM 11C: Teklif Onaylanmadı
        # -------------------------------------------------------------
        elif adim_kodu == '11C':
            if aksiyon in ['REVIZE_11B', '11B']:
                _gecis('11B', 'Revizyon Kararı Alındı -> Adım 11B', 'Adım 11C: Revizyon Kararı',
                       f"Teklif üzerinde yeniden çalışılması kararlaştırıldı. Adım 11B'ye geçildi. Not: {notlar}",
                       msg_text="Revizyon kararı alındı. Adım 11B'ye geçildi.")
            elif aksiyon in ['OLUMSUZ_16C', '16C', 'KAPAT']:
                _gecis('16C', 'Yönetim Reddetti -> 16C Olumsuz Kapatma', 'Adım 11C: Teklif Reddedildi',
                       f"Yönetim tarafından süreç sonlandırıldı. 16C Adımında olumsuz kapatıldı. Not: {notlar}",
                       yeni_durum='OLUMSUZ_KAPATILDI', msg_type='warning',
                       msg_text="Yönetim reddi ile süreç 16C Adımında olumsuz kapatıldı.")

        # -------------------------------------------------------------
        # 26. ADIM 12: Teklifin Müşteriye Sunulması ve Resmi İletim
        # -------------------------------------------------------------
        elif adim_kodu == '12':
            _gecis('13', 'Teklif Müşteriye İletildi -> Adım 13 Takip', 'Adım 12: Teklif Resmi Olarak İletildi',
                   f"Teklif dosyası resmi yollarla müşteriye sunuldu. 13. Adım Takip süreci başlatıldı. Not: {notlar}",
                   yeni_durum='MUSTERIYE_ILETILDI',
                   msg_text="Adım 12 tamamlandı! Teklif müşteriye iletildi. 13. Adıma geçildi.")

        # -------------------------------------------------------------
        # 27. ADIM 13: Teklifin Müşteri Nezdinde Takibi ve Değerlendirme Süreci
        # -------------------------------------------------------------
        elif adim_kodu == '13':
            _gecis('14', 'Müşteri Takibi Yapıldı -> Adım 14 Karar Değerlendirme', 'Adım 13: Müşteri Takibi Yapıldı',
                   f"Müşteri ile iletişim kuruldu, karar aşaması için 14. Adıma geçildi. Not: {notlar}",
                   msg_text="Adım 13 tamamlandı. 14. Adıma (Müşteri Kararının Değerlendirilmesi) geçildi.")

        # -------------------------------------------------------------
        # 28. ADIM 14: Müşteri Kararının Alınması ve Değerlendirilmesi
        # -------------------------------------------------------------
        elif adim_kodu == '14':
            if aksiyon in ['14A', 'KABUL_14A', 'EVET']:
                _gecis('14A', 'Müşteri Teklifi Kabul Etti (14A)', 'Adım 14: Müşteri Teklifi Kabul Etti',
                       f"Müşteri resmi onay/kabul bildiriminde bulundu. Adım 14A'ya geçildi. Not: {notlar}",
                       msg_text="Müşteri teklifi kabul etti! (Adım 14A)")
            elif aksiyon in ['14B', 'REVIZYON_14B']:
                _gecis('14B', 'Müşteri Revizyon / Karşı Teklif İstedi (14B)', 'Adım 14: Revizyon Talebi Alındı',
                       f"Müşteri fiyat indirimi veya ticari şart revizyonu talep etti. Adım 14B'ye geçildi. Not: {notlar}",
                       yeni_durum='REVIZYONDA', msg_type='info',
                       msg_text="Müşteri revizyon/karşı teklif talep etti (Adım 14B).")
            elif aksiyon in ['14C', 'RET_14C', 'HAYIR']:
                _gecis('14C', 'Müşteri Teklifi Reddetti / İptal (14C)', 'Adım 14: Teklif Reddedildi / İptal',
                       f"Müşteri teklifi reddetti veya proje iptal edildi. Adım 14C'ye geçildi. Not: {notlar}",
                       yeni_durum='OLUMSUZ_KAPATILDI', msg_type='warning',
                       msg_text="Müşteri teklifi reddetti veya proje iptal edildi (Adım 14C).")
            elif aksiyon in ['14D', 'BEKLIYOR_14D']:
                _gecis('14D', 'Müşteri Kararı Bekleniyor (14D)', 'Adım 14: Müşteri Kararı Bekleniyor',
                       f"Müşteri değerlendirmesi devam ediyor. Adım 14D'ye geçildi. Not: {notlar}",
                       msg_type='info', msg_text="Müşteri kararı bekleniyor (Adım 14D).")
            else:
                _gecis('16', 'Tamamlandı', 'Adım 14: Tamamlandı', f"Müşteri kararı işlendi. Not: {notlar}")

        # -------------------------------------------------------------
        # 29. ADIM 14A: Müşteri Teklifi Kabul Etti
        # -------------------------------------------------------------
        elif adim_kodu == '14A':
            if aksiyon in ['FIYAT_KAPAT_16A', '16A']:
                _gecis('16A', 'Fiyat Revizyonu Kapanışına Geçildi -> Adım 16A', 'Adım 14A: Fiyat Revizyonu Kapanışı',
                       f"Fiyat revizyon kabulü kesinleşti. Adım 16A Kapanışına geçildi. Not: {notlar}",
                       msg_text="Fiyat revizyon kapanışı için 16A Adımına geçildi.")
            elif aksiyon in ['DEVREYE_ALMA_16B', '16B']:
                _gecis('16B', 'Yeni Proje Devreye Alma Devrine Geçildi -> Adım 16B', 'Adım 14A: Devreye Alma Devri',
                       f"Yeni parça kabulü kesinleşti. Adım 16B Devreye Alma Devrine geçildi. Not: {notlar}",
                       msg_text="Yeni ürün devreye alma devri için 16B Adımına geçildi.")
            else:
                _gecis('16', 'Kabul Kesinleşti -> Adım 16 Sonuçlandırma', 'Adım 14A: Kabul Onaylandı',
                       f"Kabul bildirimi ile 16. Adım Sonuçlandırma ve Devir aşamasına geçildi. Not: {notlar}",
                       msg_text="Adım 14A tamamlandı. 16. Adıma geçildi.")

        # -------------------------------------------------------------
        # 30. ADIM 14B: Müşteri Revizyon / Karşı Teklif / İndirim Talep Etti
        # -------------------------------------------------------------
        elif adim_kodu == '14B':
            _gecis('15', 'Revizyon Talebi Alındı -> Adım 15 Müzakere Değerlendirmesi', 'Adım 14B: Müzakere Başlatıldı',
                   f"Müşteri revizyon talebi 15. Adım Müzakere Değerlendirmesine aktarıldı. Not: {notlar}",
                   yeni_durum='REVIZYONDA', msg_text="Adım 14B tamamlandı. 15. Adıma (Revizyon Değerlendirmesi) geçildi.")

        # -------------------------------------------------------------
        # 31. ADIM 14C: Müşteri Teklifi Reddetti / Proje İptal Edildi
        # -------------------------------------------------------------
        elif adim_kodu == '14C':
            _gecis('16C', 'Ret / İptal Bildirildi -> 16C Olumsuz Kapatma', 'Adım 14C: Ret / İptal Süreci',
                   f"Ret gerekçesi kaydedilerek 16C Adımına aktarıldı. Not: {notlar}",
                   yeni_durum='OLUMSUZ_KAPATILDI', msg_type='warning',
                   msg_text="Müşteri ret gerekçesiyle süreç 16C Adımına aktarıldı.")

        # -------------------------------------------------------------
        # 32. ADIM 14D: Müşteri Kararı Bekleniyor / Süreç Devam Ediyor
        # -------------------------------------------------------------
        elif adim_kodu == '14D':
            if aksiyon in ['TAKIP_13', '13']:
                _gecis('13', 'Takibe Devam Ediliyor (Adım 13)', 'Adım 14D: Takip Periyodu Uzatıldı',
                       f"Müşteri karar süresi uzadığından 13. Adıma dönüldü. Not: {notlar}",
                       msg_text="Müşteri takibine devam etmek üzere 13. Adıma dönüldü.")
            elif aksiyon in ['KAPSAM_5', '5']:
                _gecis('5', 'Teknik Değişiklik Talebi (Adım 5)', 'Adım 14D: Kapsam Değişikliği',
                       f"Müşteri teknik şartları değiştirdiği için 5. Adıma dönüldü. Not: {notlar}",
                       msg_text="Kapsam değişikliği için 5. Adıma dönüldü.")
            elif aksiyon in ['OLUMSUZ_16C', '16C', 'KAPAT']:
                _gecis('16C', 'Zaman Aşımı / İptal -> 16C Olumsuz Kapatma', 'Adım 14D: Zaman Aşımı Kapatma',
                       f"Süreç zaman aşımına uğradığından 16C Adımında olumsuz kapatıldı. Not: {notlar}",
                       yeni_durum='OLUMSUZ_KAPATILDI', msg_type='warning',
                       msg_text="Zaman aşımı sebebiyle süreç 16C Adımında kapatıldı.")

        # -------------------------------------------------------------
        # 33. ADIM 15: Revizyon / Müzakere Taleplerinin Değerlendirilmesi ve Karar
        # -------------------------------------------------------------
        elif adim_kodu == '15':
            if aksiyon in ['15A', 'YETKI_DAHILI_15A', 'EVET']:
                _gecis('15A', 'Revizyon Talebi Yetki Sınırları İçinde (15A)', 'Adım 15: Yetki Sınırları İçinde Kabul',
                       f"Müzakere talebi mevcut yetki marjları dahilinde onaylandı. Adım 15A'ya geçildi. Not: {notlar}",
                       msg_text="Revizyon talebi yetki sınırları içinde kabul edildi (Adım 15A).")
            elif aksiyon in ['15B', 'YONETIM_ONAYI_15B']:
                _gecis('15B', 'Yeniden Yönetim Onayı Gerektiriyor (15B)', 'Adım 15: Yönetim Onayına Sevk Edildi',
                       f"Yetki marjını aştığı için üst yönetim onayına sevk edildi. Adım 15B'ye geçildi. Not: {notlar}",
                       yeni_durum='YONETIM_ONAYINDA', msg_type='info',
                       msg_text="Revizyon yeniden yönetim onayı gerektiriyor (Adım 15B).")
            elif aksiyon in ['15C', 'KARSILANAMAZ_15C', 'HAYIR']:
                _gecis('15C', 'Talepler Karşılanamıyor / Müzakere Sonlandırıldı (15C)', 'Adım 15: Müzakere Sonlandırıldı',
                       f"Müşteri talepleri karşılanamadığı için müzakere tıkandı. Adım 15C'ye geçildi. Not: {notlar}",
                       msg_type='warning', msg_text="Müşteri talepleri karşılanamıyor (Adım 15C).")

        # -------------------------------------------------------------
        # 34. ADIM 15A: Revizyon Talebi Yetki Sınırları İçinde / Kabul Edilebilir
        # -------------------------------------------------------------
        elif adim_kodu == '15A':
            if aksiyon in ['SUN_12', '12']:
                _gecis('12', 'Revize Teklif Müşteriye Sunuldu (Adım 12)', 'Adım 15A: Revize Teklif İletildi',
                       f"Revize teklif mektubu 12. Adımda müşteriye sunuldu. Not: {notlar}",
                       yeni_durum='MUSTERIYE_ILETILDI',
                       msg_text="Revize teklif müşteriye sunulmak üzere 12. Adıma aktarıldı.")
            elif aksiyon in ['DOSYA_10', '10']:
                _gecis('10', 'Teklif Dosyası Güncellendi (Adım 10)', 'Adım 15A: Dosya Güncellemesi',
                       f"Dosya revizyonu için 10. Adıma aktarıldı. Not: {notlar}",
                       msg_text="Teklif dosyasını güncellemek için 10. Adıma dönüldü.")

        # -------------------------------------------------------------
        # 35. ADIM 15B: Revizyon Talebi Yeniden Yönetim Onayı Gerektiriyor
        # -------------------------------------------------------------
        elif adim_kodu == '15B':
            if aksiyon in ['FIYAT_8', '8']:
                _gecis('8', 'Fiyatlandırmaya Geri Dönüldü (Adım 8)', 'Adım 15B: Fiyatlandırma Revizyonu',
                       f"Fiyat yapısı revizyonu için 8. Adıma dönüldü. Not: {notlar}",
                       msg_text="Fiyat revizyonu için 8. Adıma dönüldü.")
            elif aksiyon in ['MALIYET_5', '5']:
                _gecis('5', 'Maliyet Analizine Geri Dönüldü (Adım 5)', 'Adım 15B: Maliyet Revizyonu',
                       f"Maliyet optimizasyonu için 5. Adıma dönüldü. Not: {notlar}",
                       msg_text="Maliyet analizi için 5. Adıma dönüldü.")
            elif aksiyon in ['RFQ_3B', '3B']:
                _gecis('3B', 'RFQ Kapsamına Geri Dönüldü (Adım 3B)', 'Adım 15B: Kapsam Revizyonu',
                       f"Talep kapsamı revizyonu için 3B Adımına dönüldü. Not: {notlar}",
                       msg_text="Talep kapsamı için 3B Adımına dönüldü.")
            elif aksiyon in ['SUN_12', '12']:
                _gecis('12', 'Yönetim Onayladı -> Adım 12 Müşteriye Sunum', 'Adım 15B: Yönetim Onayladı',
                       f"Yönetim revizyonu onayladı, 12. Adımda müşteriye sunuldu. Not: {notlar}",
                       yeni_durum='MUSTERIYE_ILETILDI',
                       msg_text="Yönetim onayı ile revize teklif müşteriye sunulmak üzere 12. Adıma aktarıldı.")

        # -------------------------------------------------------------
        # 36. ADIM 15C: Müşteri Talepleri Karşılanamıyor / Müzakere Sonlandırıldı
        # -------------------------------------------------------------
        elif adim_kodu == '15C':
            if aksiyon in ['YONETIM_15B', '15B']:
                _gecis('15B', 'Yeniden Yönetim Görüşüne İletildi (Adım 15B)', 'Adım 15C: Yönetim Görüşü',
                       f"Son kez yönetim değerlendirmesi için 15B Adımına aktarıldı. Not: {notlar}",
                       msg_text="Son değerlendirme için 15B Adımına sevk edildi.")
            elif aksiyon in ['MUSTERI_13', '13']:
                _gecis('13', 'Müşteri ile Müzakereye Devam (Adım 13)', 'Adım 15C: Müzakereye Devam',
                       f"Alternatif teklif için müşteri iletişimine 13. Adımda devam edildi. Not: {notlar}",
                       msg_text="Müşteri görüşmelerine devam için 13. Adıma dönüldü.")
            elif aksiyon in ['RET_14C', 'OLUMSUZ_16C', '16C', 'KAPAT']:
                _gecis('16C', 'Müzakere Tıkandı -> 16C Olumsuz Kapatma', 'Adım 15C: Müzakere Başarısız Kapatma',
                       f"Karşılıklı mutabakat sağlanamadı. 16C Adımında olumsuz kapatıldı. Not: {notlar}",
                       yeni_durum='OLUMSUZ_KAPATILDI', msg_type='warning',
                       msg_text="Müzakere sağlanamadığından süreç 16C Adımında olumsuz kapatıldı.")

        # -------------------------------------------------------------
        # 37. ADIM 16: Teklif Sürecinin Sonuçlandırılması ve Devir
        # -------------------------------------------------------------
        elif adim_kodu == '16':
            if aksiyon in ['16A', 'FIYAT_KAPAT_16A']:
                _gecis('16A', 'Fiyat Revizyonu Kapanışına Geçildi (16A)', 'Adım 16: Fiyat Revizyonu Kapanışı',
                       f"Fiyat revizyon kapatma işlemleri için 16A Adımına geçildi. Not: {notlar}",
                       msg_text="Fiyat revizyon kapanışı için 16A Adımına geçildi.")
            elif aksiyon in ['16B', 'DEVREYE_ALMA_16B']:
                _gecis('16B', 'Devreye Alma Devir Kapanışına Geçildi (16B)', 'Adım 16: Devreye Alma Devri',
                       f"Yeni ürün devreye alma devri için 16B Adımına geçildi. Not: {notlar}",
                       msg_text="Yeni ürün devreye alma devri için 16B Adımına geçildi.")
            elif aksiyon in ['16C', 'OLUMSUZ_16C']:
                _gecis('16C', 'Olumsuz Kapanışa Geçildi (16C)', 'Adım 16: Olumsuz Kapanış',
                       f"Olumsuz kapanış işlemleri için 16C Adımına geçildi. Not: {notlar}",
                       yeni_durum='OLUMSUZ_KAPATILDI', msg_type='warning',
                       msg_text="Olumsuz kapanış için 16C Adımına geçildi.")
            else:
                _gecis('16B', 'Tamamlandı -> 16B Devir', 'Adım 16: Tamamlandı', f"Teklif sonuçlandırıldı. Not: {notlar}")

        # -------------------------------------------------------------
        # 38. ADIM 16A: Fiyat Revizyonu Kapanışı ve Sistem Kaydı
        # -------------------------------------------------------------
        elif adim_kodu == '16A':
            adim_kaydi.durum = 'TAMAMLANDI'
            adim_kaydi.karar_sonucu = 'Fiyat Revizyonu Başarıyla Tamamlandı ve Sistemde Güncellendi'
            adim_kaydi.tamamlanma_tarihi = timezone.now()
            adim_kaydi.save()

            surec.durum = 'BASARIYLA_TAMAMLANDI'
            surec.guncel_adim_kodu = '16A'
            surec.guncel_adim_no = 16
            surec.save()

            UrunTeklifGecmisLog.objects.create(
                surec=surec,
                islem="Fiyat Revizyonu Süreci Başarıyla Kapatıldı",
                detay=f"Fiyat revizyonu tamamlandı, ERP/Netsis sistemlerine fiyatlar işlendi ve süreç başarıyla arşivlendi. Kapanış Notu: {notlar}",
                yapan=tamamlayan
            )
            messages.success(request, "Tebrikler! Fiyat Revizyonu Süreci başarıyla tamamlandı ve arşivlendi.")

        # -------------------------------------------------------------
        # 39. ADIM 16B: Yeni Proje / Parça Teklifi Kabul Kapanışı ve Devreye Alma Sürecine Devir
        # -------------------------------------------------------------
        elif adim_kodu == '16B':
            adim_kaydi.durum = 'TAMAMLANDI'
            adim_kaydi.karar_sonucu = 'Teklif Kabul Edildi ve Yeni Ürün Devreye Alma Sürecine Devredildi'
            adim_kaydi.tamamlanma_tarihi = timezone.now()
            adim_kaydi.save()

            surec.durum = 'BASARIYLA_TAMAMLANDI'
            surec.guncel_adim_kodu = '16B'
            surec.guncel_adim_no = 16
            surec.save()

            UrunTeklifGecmisLog.objects.create(
                surec=surec,
                islem="Teklif Süreci Başarıyla Tamamlandı & APQP Devri Yapıldı",
                detay=f"Teklif müşteri tarafından kabul edildi, proje devir toplantısı yapıldı ve APQP/Devreye Alma sürecine devredildi. Kapanış Notu: {notlar}",
                yapan=tamamlayan
            )
            messages.success(request, "Tebrikler! Yeni Ürün Teklifi başarıyla tamamlandı ve Devreye Alma Sürecine devredildi.")

        # -------------------------------------------------------------
        # 40. ADIM 16C: Teklif Sürecinin Olumsuz Kapanışı, Raporlama ve Öğrenilmiş Dersler
        # -------------------------------------------------------------
        elif adim_kodu == '16C':
            adim_kaydi.durum = 'TAMAMLANDI'
            adim_kaydi.karar_sonucu = 'Teklif Süreci Olumsuz Kapatıldı & Öğrenilmiş Dersler Kaydedildi'
            adim_kaydi.tamamlanma_tarihi = timezone.now()
            adim_kaydi.save()

            surec.durum = 'OLUMSUZ_KAPATILDI'
            surec.guncel_adim_kodu = '16C'
            surec.guncel_adim_no = 16
            surec.save()

            UrunTeklifGecmisLog.objects.create(
                surec=surec,
                islem="Teklif Süreci Olumsuz Olarak Kapatıldı",
                detay=f"Teklif süreci olumsuz sonuçlandı. Kayıp analiz raporu oluşturuldu ve öğrenilmiş dersler sistemine işlendi. Kapanış Notu: {notlar}",
                yapan=tamamlayan
            )
            messages.warning(request, "Ürün Teklif Süreci olumsuz sonuçlanarak kapatıldı ve arşivlendi.")

        # -------------------------------------------------------------
        # DİĞER / GENEL FALLBACK ADIMLAR
        # -------------------------------------------------------------
        else:
            adim_kaydi.durum = 'TAMAMLANDI'
            adim_kaydi.karar_sonucu = 'Tamamlandı'
            adim_kaydi.tamamlanma_tarihi = timezone.now()
            adim_kaydi.save()

            next_adim = UrunTeklifAdimTanimi.objects.filter(sira_no__gt=adim_kaydi.adim.sira_no).first()
            if next_adim:
                _gecis(next_adim.adim_kodu, 'Tamamlandı', f"Adım {adim_kodu} Tamamlandı", f"{adim_kaydi.adim.baslik} tamamlandı. {next_adim.adim_kodu} Adımına geçildi.", msg_text=f"Adım {adim_kodu} tamamlandı.")
            else:
                surec.durum = 'BASARIYLA_TAMAMLANDI'
                surec.save()
                messages.success(request, f"Adım {adim_kodu} tamamlandı.")

    return redirect(f"{redirect('urun_teklif_detay', pk=surec.pk).url}#adim-{surec.guncel_adim_kodu}")


def urun_teklif_sil(request, pk):
    surec = get_object_or_404(UrunTeklifSureci, pk=pk)
    if request.method == 'POST':
        kod = surec.kod
        surec.delete()
        messages.success(request, f"'{kod}' kodlu Ürün Teklif Süreci başarıyla silindi.")
    return redirect('urun_teklif_liste')


# ==============================================================================
# SÖZLEŞMENİN DEĞERLENDİRİLMESİ SÜRECİ (15 ADIM) GÖRÜNÜMLERİ
# ==============================================================================

def sozlesme_sureci_liste(request):
    """
    15 Adımlık Sözleşmenin Değerlendirilmesi Süreci Listesi & İstatistik Paneli
    """
    surecler = SozlesmeSureci.objects.all()

    q = request.GET.get('q', '').strip()
    durum_filtre = request.GET.get('durum', '')
    fabrika_filtre = request.GET.get('fabrika', '')
    donem_filtre = request.GET.get('donem', '')
    tip_filtre = request.GET.get('sozlesme_tipi', '')

    if q:
        surecler = surecler.filter(
            Q(kod__icontains=q) |
            Q(musteri_adi__icontains=q) |
            Q(ad__icontains=q)
        )
    if durum_filtre:
        surecler = surecler.filter(durum=durum_filtre)
    if fabrika_filtre:
        surecler = surecler.filter(ilgili_fabrika=fabrika_filtre)
    if donem_filtre:
        surecler = surecler.filter(donem__icontains=donem_filtre)
    if tip_filtre:
        surecler = surecler.filter(sozlesme_tipi=tip_filtre)

    toplam_surec = SozlesmeSureci.objects.count()
    aktif_surec = SozlesmeSureci.objects.filter(durum__in=['DEVAM_EDIYOR', 'HUKUKI_INCELEMEDE', 'YONETIM_ONAYINDA', 'MUSTERI_MUZAKERESINDE']).count()
    muzakere_surec = SozlesmeSureci.objects.filter(durum='MUSTERI_MUZAKERESINDE').count()
    tamamlanan_surec = SozlesmeSureci.objects.filter(durum='BASARIYLA_TAMAMLANDI').count()

    context = {
        'surecler': surecler,
        'musteriler': MusteriKarti.objects.all(),
        'toplam_surec': toplam_surec,
        'aktif_surec': aktif_surec,
        'muzakere_surec': muzakere_surec,
        'tamamlanan_surec': tamamlanan_surec,
        'q': q,
        'durum_filtre': durum_filtre,
        'fabrika_filtre': fabrika_filtre,
        'donem_filtre': donem_filtre,
        'tip_filtre': tip_filtre,
        'fabrikalar': PazarlamaProjesi.FABRIKA_CHOICES,
        'sozlesme_tipleri': SozlesmeSureci.SOZLESME_TIPI_CHOICES,
        'durum_listesi': SozlesmeSureci.DURUM_CHOICES,
        'master_adimlar': SozlesmeAdimTanimi.objects.all().order_by('adim_no'),
    }
    return render(request, 'crm_takip/sozlesme_sureci_liste.html', context)


def sozlesme_sureci_olustur(request):
    """
    Yeni Sözleşme Değerlendirme Süreci Başlatma (9 Standart Adım)
    """
    if request.method == 'POST':
        kod = request.POST.get('kod', '').strip()
        ad = request.POST.get('ad', '').strip()
        musteri_adi = request.POST.get('musteri_adi', '').strip()
        sozlesme_tipi = request.POST.get('sozlesme_tipi', 'SATIS')
        donem = request.POST.get('donem', '2026 Yıllık').strip()
        ilgili_fabrika = request.POST.get('ilgili_fabrika', 'PRESHANE')
        
        baslangic_tarihi = request.POST.get('baslangic_tarihi') or None
        bitis_tarihi = request.POST.get('bitis_tarihi') or None

        sorumlu_satis_uzmani = request.POST.get('sorumlu_satis_uzmani', 'BUSE NUR BALTACIOĞLU')
        sorumlu_satis_yoneticisi = request.POST.get('sorumlu_satis_yoneticisi', 'ONUR TUNCER')
        sorumlu_fabrika_muduru = request.POST.get('sorumlu_fabrika_muduru', 'MUHARREM FURKAN TARHAN')
        sorumlu_hukuk = request.POST.get('sorumlu_hukuk', 'Hukuk Müşaviri')
        aciklama = request.POST.get('aciklama', '').strip()

        year = timezone.now().year

        if not kod:
            counter = 1
            while True:
                candidate_kod = f"SZL-{year}-{counter:03d}"
                if not SozlesmeSureci.objects.filter(kod=candidate_kod).exists():
                    kod = candidate_kod
                    break
                counter += 1
        else:
            if SozlesmeSureci.objects.filter(kod=kod).exists():
                counter = 1
                base_kod = kod
                while True:
                    candidate_kod = f"{base_kod}-{counter:02d}"
                    if not SozlesmeSureci.objects.filter(kod=candidate_kod).exists():
                        kod = candidate_kod
                        break
                    counter += 1
                messages.warning(request, f"Belirttiğiniz sözleşme kodu mevcut olduğu için benzersiz olarak '{kod}' atandı.")

        # İlişkili Müşteri Kartı
        musteri_karti_id = request.POST.get('musteri_karti_id')
        musteri_karti = None
        if musteri_karti_id:
            musteri_karti = MusteriKarti.objects.filter(pk=musteri_karti_id).first()
        if not musteri_karti and musteri_adi:
            musteri_karti = MusteriKarti.objects.filter(
                Q(ad__icontains=musteri_adi) | Q(kisa_ad__icontains=musteri_adi)
            ).first()

        try:
            surec = SozlesmeSureci.objects.create(
                kod=kod,
                ad=ad,
                musteri_adi=musteri_adi,
                musteri_karti=musteri_karti,
                sozlesme_tipi=sozlesme_tipi,
                donem=donem,
                ilgili_fabrika=ilgili_fabrika,
                baslangic_tarihi=baslangic_tarihi,
                bitis_tarihi=bitis_tarihi,
                sorumlu_satis_uzmani=sorumlu_satis_uzmani,
                sorumlu_satis_yoneticisi=sorumlu_satis_yoneticisi,
                sorumlu_fabrika_muduru=sorumlu_fabrika_muduru,
                sorumlu_hukuk=sorumlu_hukuk,
                aciklama=aciklama,
                durum='DEVAM_EDIYOR',
                guncel_adim_no=1
            )
        except Exception as e:
            messages.error(request, f"Sözleşme değerlendirme süreci oluşturulurken hata: {str(e)}")
            return redirect('sozlesme_sureci_liste')

        # 9 Standart Adım Kaydı Oluşturulması
        master_adimlar = SozlesmeAdimTanimi.objects.all().order_by('adim_no')
        for adim in master_adimlar:
            durum = 'DEVAM_EDIYOR' if adim.adim_no == 1 else 'BEKLIYOR'
            dokuman = adim.ilgili_dokumanlar.split(',')[0] if adim.ilgili_dokumanlar else ""
            SozlesmeAdimKaydi.objects.create(
                surec=surec,
                adim=adim,
                durum=durum,
                dokuman_referansi=dokuman
            )

        # İlk Log Kaydı
        SozlesmeGecmisLog.objects.create(
            surec=surec,
            islem="Sözleşme Değerlendirme Süreci Başlatıldı",
            detay=f"9 adımlık standart sözleşme değerlendirme iş akışı başlatıldı. Sözleşme Tipi: {surec.get_sozlesme_tipi_display()}, Fabrika: {ilgili_fabrika}.",
            yapan=sorumlu_satis_uzmani
        )

        messages.success(request, f"'{surec.kod}' kodlu Sözleşme Değerlendirme Süreci başarıyla başlatıldı.")
        return redirect('sozlesme_sureci_detay', pk=surec.pk)

    return redirect('sozlesme_sureci_liste')


def sozlesme_sureci_detay(request, pk):
    """
    9 Adımlık İnteraktif Sözleşme Değerlendirme Süreci Detay ve Karar Ekranı (Minimalist Standart)
    """
    surec = get_object_or_404(SozlesmeSureci, pk=pk)
    adim_kayitlari = surec.adim_kayitlari.select_related('adim').order_by('adim__adim_no')

    # Fazlara göre gruplama (9 Adım)
    faz_tanimlari = [
        ('FAZ1', 'Faz 1: Talep Kaydı & İnceleme (Adım 1-3)'),
        ('FAZ2', 'Faz 2: Değerlendirme & Yetkili Makam Kararı (Adım 4-5)'),
        ('FAZ3', 'Faz 3: Müşteri Müzakeresi & Mutabakat Kontrolü (Adım 6-7)'),
        ('FAZ4', 'Faz 4: Yetkili İmza & Yürürlük Takibi (Adım 8-9)'),
    ]

    fazlar = []
    for faz_kodu, faz_basligi in faz_tanimlari:
        faz_adimlari = [ak for ak in adim_kayitlari if ak.adim.faz == faz_kodu]
        if faz_adimlari:
            fazlar.append({
                'kod': faz_kodu,
                'baslik': faz_basligi,
                'adimlar': faz_adimlari
            })

    master_adimlar = SozlesmeAdimTanimi.objects.all().order_by('adim_no')
    tarihce = surec.tarihce_kayitlari.all().order_by('-tarih')

    context = {
        'surec': surec,
        'adim_kayitlari': adim_kayitlari,
        'fazlar': fazlar,
        'master_adimlar': master_adimlar,
        'tarihce': tarihce,
    }
    return render(request, 'crm_takip/sozlesme_sureci_detay.html', context)


def sozlesme_sureci_adim_aksiyon(request, pk, adim_id):
    """
    9 Adımlık Sözleşme Süreci Adım Tamamlama ve Karar Kapısı Aksiyon Motoru
    """
    surec = get_object_or_404(SozlesmeSureci, pk=pk)
    adim_kaydi = get_object_or_404(SozlesmeAdimKaydi, pk=adim_id, surec=surec)
    adim_no = adim_kaydi.adim.adim_no

    if request.method == 'POST':
        aksiyon = request.POST.get('aksiyon', 'TAMAMLA').strip().upper()
        notlar = request.POST.get('notlar', '').strip()
        tamamlayan = request.POST.get('tamamlayan', 'Satış Uzmanı').strip() or 'Satış Uzmanı'

        if notlar:
            adim_kaydi.notlar = notlar
        if tamamlayan:
            adim_kaydi.tamamlayan = tamamlayan

        # ARA KAYDET / NOT GÜNCELLEME
        if aksiyon in ['KAYDET', 'GUNCELLE']:
            if adim_kaydi.durum == 'BEKLIYOR':
                adim_kaydi.durum = 'DEVAM_EDIYOR'
            adim_kaydi.save()

            SozlesmeGecmisLog.objects.create(
                surec=surec,
                islem=f"Adım {adim_no}: Notlar Kaydedildi",
                detay=f"Sözleşme adım değerlendirme notları güncellendi. Not: {notlar or 'Girilmedi.'}",
                yapan=tamamlayan
            )
            messages.success(request, f"Adım {adim_no} not ve değerlendirme bilgileri kaydedildi.")
            return redirect(f"{redirect('sozlesme_sureci_detay', pk=surec.pk).url}#adim-{adim_no}")

        now = timezone.now()
        adim_kaydi.tamamlanma_tarihi = now

        # -------------------------------------------------------------
        # 1. ADIM 1: Talebin Kaydı ve İnceleme Planının Oluşturulması
        # -------------------------------------------------------------
        if adim_no == 1:
            adim_kaydi.durum = 'TAMAMLANDI'
            adim_kaydi.karar_sonucu = 'Kayıt Açıldı & İnceleme Planı Oluşturuldu (Adım 2 ve Adım 3 Paralel Başlatıldı)'
            adim_kaydi.save()

            # Adım 2 ve 3 paralel olarak DEVAM_EDIYOR durumuna geçer
            SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no__in=[2, 3]).update(durum='DEVAM_EDIYOR')
            surec.guncel_adim_no = 2
            surec.durum = 'DEVAM_EDIYOR'
            surec.save()

            SozlesmeGecmisLog.objects.create(
                surec=surec,
                islem="Adım 1: Talebin Kaydı ve İnceleme Planı Tamamlandı",
                detay="Sözleşme takip kaydı açıldı, ekler kontrol edildi. Atanan Birimler (Adım 2) ve Şirket Hukuk Danışmanı (Adım 3) paralel incelemeye aktarıldı.",
                yapan=tamamlayan
            )
            messages.success(request, "1. Adım tamamlandı! Atanan Birimler İncelemesi (Adım 2) ve Hukuk Danışmanı İncelemesi (Adım 3) paralel olarak başlatıldı.")

        # -------------------------------------------------------------
        # 2. ADIM 2: Atanan Birimlerin İncelemesi
        # -------------------------------------------------------------
        elif adim_no == 2:
            adim_kaydi.durum = 'TAMAMLANDI'
            adim_kaydi.karar_sonucu = 'Atanan Birim İncelemeleri Dochuman Üzerinde Tamamlandı'
            adim_kaydi.save()

            # Adım 3'ün durumunu kontrol et
            adim3_kaydi = SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no=3).first()
            adim3_tamam = adim3_kaydi and adim3_kaydi.durum in ['TAMAMLANDI', 'PAS_GECILDI']

            if adim3_tamam:
                # İkisi de bitti -> Adım 4'e geçilir
                surec.guncel_adim_no = 4
                surec.save()
                SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no=4).update(durum='DEVAM_EDIYOR')
                messages.success(request, "2. Adım tamamlandı! Hukuk incelemesi de hazır olduğundan 4. Adıma (Görüşlerin Birleştirilmesi) geçildi.")
            else:
                surec.guncel_adim_no = 3
                surec.save()
                messages.info(request, "2. Adım (Birim İncelemeleri) tamamlandı. 3. Adım (Hukuk Danışmanı İncelemesi) bekleniyor.")

            SozlesmeGecmisLog.objects.create(
                surec=surec,
                islem="Adım 2: Atanan Birimlerin İncelemesi Tamamlandı",
                detay=f"Sözleşme maddeleri ilgili birimlerce değerlendirildi. Not: {notlar}",
                yapan=tamamlayan
            )

        # -------------------------------------------------------------
        # 3. ADIM 3: Şirket Hukuk Danışmanı İncelemesi
        # -------------------------------------------------------------
        elif adim_no == 3:
            adim_kaydi.durum = 'TAMAMLANDI'
            adim_kaydi.karar_sonucu = 'Yazılı Hukuk Görüşü ve Revizyonlar Dochuman Kaydına Eklendi'
            adim_kaydi.save()

            # Adım 2'nin durumunu kontrol et
            adim2_kaydi = SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no=2).first()
            adim2_tamam = adim2_kaydi and adim2_kaydi.durum in ['TAMAMLANDI', 'PAS_GECILDI']

            if adim2_tamam:
                # İkisi de bitti -> Adım 4'e geçilir
                surec.guncel_adim_no = 4
                surec.save()
                SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no=4).update(durum='DEVAM_EDIYOR')
                messages.success(request, "3. Adım tamamlandı! Birim incelemeleri de hazır olduğundan 4. Adıma (Görüşlerin Birleştirilmesi) geçildi.")
            else:
                surec.guncel_adim_no = 2
                surec.save()
                messages.info(request, "3. Adım (Hukuk İncelemesi) tamamlandı. 2. Adım (Birim İncelemeleri) bekleniyor.")

            SozlesmeGecmisLog.objects.create(
                surec=surec,
                islem="Adım 3: Şirket Hukuk Danışmanı İncelemesi Tamamlandı",
                detay=f"Hukuki görüş ve revizyonlu taslak sisteme yüklendi. Not: {notlar}",
                yapan=tamamlayan
            )

        # -------------------------------------------------------------
        # 4. ADIM 4: Görüşlerin Birleştirilmesi ve Risk Değerlendirmesi
        # -------------------------------------------------------------
        elif adim_no == 4:
            adim_kaydi.durum = 'TAMAMLANDI'
            adim_kaydi.karar_sonucu = 'Birim & Hukuk Görüşleri Birleştirildi, Kritik Sapmalar Belirlendi'
            adim_kaydi.save()

            surec.guncel_adim_no = 5
            surec.durum = 'YONETIM_ONAYINDA'
            surec.save()

            SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no=5).update(durum='DEVAM_EDIYOR')

            SozlesmeGecmisLog.objects.create(
                surec=surec,
                islem="Adım 4: Görüşlerin Birleştirilmesi ve Risk Değerlendirmesi Tamamlandı",
                detay=f"Tüm iç değerlendirmeler tek bir ana kayıtta konsolide edildi. 5. Adıma (Yetkili Makam Kararı) aktarıldı. Not: {notlar}",
                yapan=tamamlayan
            )
            messages.success(request, "4. Adım tamamlandı! Riskler birleştirildi ve 5. Adım (Yetkili Makam Kararı) aşamasına sunuldu.")

        # -------------------------------------------------------------
        # 5. ADIM 5: Kritik Sapma ve Yetkili Makam Kararı (KARAR KAPISI)
        # -------------------------------------------------------------
        elif adim_no == 5:
            if aksiyon in ['ONAY', 'SAPMA_YOK', 'ONAYLANDI', 'DEVAM', 'TAMAMLA']:
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'Kritik Sapma Yok / Sapma Yetkili Makamca Onaylandı -> Adım 6'
                adim_kaydi.save()

                surec.guncel_adim_no = 6
                surec.durum = 'MUSTERI_MUZAKERESINDE'
                surec.save()

                SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no=6).update(durum='DEVAM_EDIYOR')

                SozlesmeGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 5: Yetkili Makam Onayı Alındı (Sapma Yok / Onaylandı)",
                    detay=f"Sözleşme şartları ve sapmalar yetkili makamca onaylandı. Teleset müzakere pozisyonu için 6. Adıma geçildi. Not: {notlar}",
                    yapan=tamamlayan
                )
                messages.success(request, "Yetkili Makam Kararı Onaylandı! 6. Adım Teleset Müzakere Pozisyonu ve Görüşmelerine geçildi.")

            elif aksiyon in ['REVIZYON', 'EK_DEGERLENDIRME', 'DEGERLENDIRMEYE_DON']:
                adim_kaydi.durum = 'MUZAKEREYE_YONLENDIRILDI'
                adim_kaydi.karar_sonucu = 'Ek Değerlendirme / Revizyon İstendi -> 4. Adıma Dönüş'
                adim_kaydi.save()

                surec.guncel_adim_no = 4
                surec.durum = 'DEVAM_EDIYOR'
                surec.save()

                SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no=4).update(durum='DEVAM_EDIYOR')

                SozlesmeGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 5: Yetkili Makam Ek Revizyon / Değerlendirme Talep Etti (Adım 4'e Dönüş)",
                    detay=f"Makam değerlendirmesi sonucunda ek teknik/ticari çalışma istendi. 4. Adıma dönüldü. Gerekçe: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Yetkili makam ek revizyon/değerlendirme talep etti. Süreç 4. Adıma yönlendirildi.")

            elif aksiyon in ['RED', 'DEVAM_EDILMEYECEK', 'IPTAL', 'OLUMSUZ']:
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'Sözleşmeye Devam Edilmeme Kararı Alındı (Ret)'
                adim_kaydi.save()

                # 6, 7, 8, 9 adımlar pas geçilerek olumsuz kapatılır
                SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no__in=[6, 7, 8, 9]).update(durum='PAS_GECILDI')
                surec.durum = 'OLUMSUZ_KAPATILDI'
                surec.save()

                SozlesmeGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 5: Sözleşmeye Devam Edilmeme Kararı (Süreç Olumsuz Kapatıldı)",
                    detay=f"Riskler veya koşullar kabul edilemez bulundu. Sözleşme süreci sonlandırıldı. Gerekçe: {notlar}",
                    yapan=tamamlayan
                )
                messages.error(request, "Sözleşmeye devam edilmeme kararı verildi. Süreç olumsuz olarak kapatıldı.")

        # -------------------------------------------------------------
        # 6. ADIM 6: Teleset Müzakere Pozisyonunun Oluşturulması ve Müşteri Görüşmeleri
        # -------------------------------------------------------------
        elif adim_no == 6:
            adim_kaydi.durum = 'TAMAMLANDI'
            adim_kaydi.karar_sonucu = 'Müzakere Pozisyonu Oluşturuldu, Müşteri Görüşmeleri Tamamlandı'
            adim_kaydi.save()

            surec.guncel_adim_no = 7
            surec.durum = 'DEVAM_EDIYOR'
            surec.save()

            SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no=7).update(durum='DEVAM_EDIYOR')

            SozlesmeGecmisLog.objects.create(
                surec=surec,
                islem="Adım 6: Müzakere Pozisyonu ve Görüşmeler Tamamlandı",
                detay=f"Onaylanan sınırlar dahilinde müşteri müzakeresi yapıldı, revizyonlu metin hazırlandı. 7. Adım (Nihai Mutabakat Kontrolü) aşamasına geçildi. Not: {notlar}",
                yapan=tamamlayan
            )
            messages.success(request, "6. Adım tamamlandı! Müzakereler sonrasında 7. Adım (Nihai Mutabakat ve Metin Kontrolü) aşamasına geçildi.")

        # -------------------------------------------------------------
        # 7. ADIM 7: Nihai Mutabakat ve Sözleşme Metni Kontrolü (KARAR KAPISI)
        # -------------------------------------------------------------
        elif adim_no == 7:
            if aksiyon in ['MUTABAKAT_SAGLANDI', 'ONAY', 'OLUMLU', 'UYGUN', 'TAMAMLA']:
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'Nihai Mutabakat Sağlandı / Kritik Sapma Yok (İmzaya Uygun -> Adım 8)'
                adim_kaydi.save()

                surec.guncel_adim_no = 8
                surec.durum = 'DEVAM_EDIYOR'
                surec.save()

                SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no=8).update(durum='DEVAM_EDIYOR')

                SozlesmeGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 7: Nihai Mutabakat Sağlandı ve Metin Kontrolü Onaylandı",
                    detay=f"Müşteri ile nihai sözleşme metninde tam mutabakata varıldı, kritik sapma bulunmuyor. 8. Adım (Yetkili İmza) aşamasına geçildi. Not: {notlar}",
                    yapan=tamamlayan
                )
                messages.success(request, "Nihai mutabakat sağlandı! 8. Adım Yetkili İmza, Arşivleme ve Dağıtım aşamasına geçildi.")

            elif aksiyon in ['KRITIK_SAPMA_VAR', 'YONETIM_ONAYINA_DON', 'REVIZYON']:
                adim_kaydi.durum = 'MUZAKEREYE_YONLENDIRILDI'
                adim_kaydi.karar_sonucu = 'Yeni Kritik Sapma / Revizyon Gerekli -> Adım 5 Yetkili Makam Onayına Dönüş'
                adim_kaydi.save()

                surec.guncel_adim_no = 5
                surec.durum = 'YONETIM_ONAYINDA'
                surec.save()

                SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no=5).update(durum='DEVAM_EDIYOR')

                SozlesmeGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 7: Yeni Kritik Sapma Sebebiyle Yetkili Makam Onayına Dönüldü (Adım 5'e Dönüş)",
                    detay=f"Müzakere sonucu ortaya çıkan yeni kritik sapmalar için yetkili makam onayına dönüldü. Gerekçe: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Yeni kritik sapma tespit edildi. Süreç 5. Adıma (Yetkili Makam Kararı) yönlendirildi.")

            elif aksiyon in ['MUSTERI_RED', 'IPTAL', 'OLUMSUZ']:
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'Müşteri Şartları Kabul Etmedi / Müzakere Olumsuz Kapatıldı'
                adim_kaydi.save()

                SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no__in=[8, 9]).update(durum='PAS_GECILDI')
                surec.durum = 'OLUMSUZ_KAPATILDI'
                surec.save()

                SozlesmeGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 7: Müşteri Müzakeresi Olumsuz / Ret (Süreç Kapatıldı)",
                    detay=f"Müşteriyle sözleşme koşullarında uzlaşılamadı. Süreç olumsuz kapatıldı. Gerekçe: {notlar}",
                    yapan=tamamlayan
                )
                messages.error(request, "Müşteri ile mutabakat sağlanamadı. Süreç olumsuz olarak kapatıldı.")

        # -------------------------------------------------------------
        # 8. ADIM 8: Yetkili İmza, Arşivleme ve Dağıtım
        # -------------------------------------------------------------
        elif adim_no == 8:
            adim_kaydi.durum = 'TAMAMLANDI'
            adim_kaydi.karar_sonucu = 'Yetkili İmzalar Tamamlandı, Sözleşme Dochuman’a Yüklendi ve İlgili Birimlere Dağıtıldı'
            adim_kaydi.save()

            surec.guncel_adim_no = 9
            surec.durum = 'DEVAM_EDIYOR'
            surec.save()

            SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no=9).update(durum='DEVAM_EDIYOR')

            SozlesmeGecmisLog.objects.create(
                surec=surec,
                islem="Adım 8: Yetkili İmza, Arşivleme ve Dağıtım Tamamlandı",
                detay=f"İmza sirkülerine uygun olarak sözleşme imzalandı ve sisteme arşivlendi. 9. Adım (Sözleşme Yükümlülüklerinin ve Sürelerinin Takibi) aşamasına geçildi. Not: {notlar}",
                yapan=tamamlayan
            )
            messages.success(request, "8. Adım tamamlandı! Sözleşme imzalandı, arşivlendi ve 9. Adım (Yükümlülük & Süre Takibi) aşamasına geçildi.")

        # -------------------------------------------------------------
        # 9. ADIM 9: Sözleşme Yükümlülüklerinin ve Sürelerinin Takibi (NİHAİ ADIM)
        # -------------------------------------------------------------
        elif adim_no == 9:
            if aksiyon in ['TAMAMLA', 'YURURLUKTE_TAKIP', 'ONAY']:
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'Sözleşme Başarıyla Yürürlüğe Alındı & Yükümlülük Takibi Başlatıldı'
                adim_kaydi.save()

                surec.durum = 'BASARIYLA_TAMAMLANDI'
                surec.guncel_adim_no = 9
                surec.save()

                SozlesmeGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 9: Sözleşme Değerlendirme Süreci Başarıyla Tamamlandı",
                    detay=f"Sözleşme yürürlükte aktif olarak takip edilmektedir. Yükümlülükler ilgili birimlere tebliğ edildi. Kapanış Notu: {notlar}",
                    yapan=tamamlayan
                )
                messages.success(request, "Sözleşmenin Değerlendirilmesi Süreci başarıyla tamamlandı ve yürürlüğe alındı!")

            elif aksiyon in ['YENILEME_TALEBI', 'DEGISIKLIK']:
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'Sözleşme Yenileme / Değişiklik Talebi Başlatıldı (1. Adım Döngüsüne Dönüş)'
                adim_kaydi.save()

                surec.durum = 'DEVAM_EDIYOR'
                surec.guncel_adim_no = 1
                surec.save()

                SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no=1).update(durum='DEVAM_EDIYOR')

                SozlesmeGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 9: Sözleşme Yenileme / Revizyon Talebi Başlatıldı",
                    detay=f"Sözleşme süresi veya koşul değişikliği gereksinimiyle yeni sözleşme döngüsü Adım 1 üzerinden başlatıldı. Talep Notu: {notlar}",
                    yapan=tamamlayan
                )
                messages.info(request, "Sözleşme yenileme/değişiklik talebi kaydedildi. Yeni değerlendirme için 1. Adıma yönlendirildi.")

    return redirect(f"{redirect('sozlesme_sureci_detay', pk=pk).url}#adim-{surec.guncel_adim_no}")


def sozlesme_sureci_sil(request, pk):
    surec = get_object_or_404(SozlesmeSureci, pk=pk)
    if request.method == 'POST':
        kod = surec.kod
        surec.delete()
        messages.success(request, f"'{kod}' kodlu Sözleşme Değerlendirme Süreci başarıyla silindi.")
    return redirect('sozlesme_sureci_liste')


# ==============================================================================
# YENİ ÜRÜN DEVREYE ALMA SÜRECİ (45 ADIM) GÖRÜNÜMLERİ
# ==============================================================================

def yeni_urun_liste(request):
    """
    Yeni Ürün Devreye Alma Süreci (APQP / NPI) Listesi ve İstatistikleri
    """
    surecler = YeniUrunDevreyeAlmaSureci.objects.all()

    q = request.GET.get('q', '').strip()
    durum_filtre = request.GET.get('durum', '')
    fabrika_filtre = request.GET.get('fabrika', '')
    urun_filtre = request.GET.get('urun_grubu', '')

    if q:
        surecler = surecler.filter(
            Q(kod__icontains=q) |
            Q(musteri_adi__icontains=q) |
            Q(ad__icontains=q) |
            Q(parca_kodu__icontains=q)
        )

    if durum_filtre:
        surecler = surecler.filter(durum=durum_filtre)

    if fabrika_filtre:
        surecler = surecler.filter(ilgili_fabrika=fabrika_filtre)

    if urun_filtre:
        surecler = surecler.filter(urun_grubu=urun_filtre)

    toplam_surec = YeniUrunDevreyeAlmaSureci.objects.count()
    aktif_surec = YeniUrunDevreyeAlmaSureci.objects.filter(durum__in=['DEVAM_EDIYOR', 'REVIZYONDA']).count()
    uygunsuzluk_surec = YeniUrunDevreyeAlmaSureci.objects.filter(durum='UYGUNSUZLUK_YONETIMINDE').count()
    tamamlanan_surec = YeniUrunDevreyeAlmaSureci.objects.filter(durum='BASARIYLA_TAMAMLANDI').count()

    musteriler = MusteriKarti.objects.all()
    urun_gruplari = UrunGrubuKarti.objects.all()

    context = {
        'surecler': surecler,
        'toplam_surec': toplam_surec,
        'aktif_surec': aktif_surec,
        'uygunsuzluk_surec': uygunsuzluk_surec,
        'tamamlanan_surec': tamamlanan_surec,
        'musteriler': musteriler,
        'urun_gruplari': urun_gruplari,
        'secili_durum': durum_filtre,
        'secili_fabrika': fabrika_filtre,
        'secili_urun': urun_filtre,
        'arama_kelimesi': q,
    }
    return render(request, 'crm_takip/yeni_urun_liste.html', context)


def yeni_urun_olustur(request):
    """
    Yeni Ürün Devreye Alma Süreci Başlatma
    """
    if request.method == 'POST':
        kod = request.POST.get('kod', '').strip()
        ad = request.POST.get('ad', '').strip()
        musteri_adi = request.POST.get('musteri_adi', '').strip()
        musteri_id = request.POST.get('musteri_karti')
        urun_grubu = request.POST.get('urun_grubu', 'Kondenser & Sogutma')
        urun_grubu_id = request.POST.get('urun_grubu_karti')
        ilgili_fabrika = request.POST.get('ilgili_fabrika', 'PRESHANE')
        parca_kodu = request.POST.get('parca_kodu', '').strip()
        hedef_seri_uretim_tarihi = request.POST.get('hedef_seri_uretim_tarihi') or None
        yillik_hedef_adet = request.POST.get('yillik_hedef_adet') or None
        
        sorumlu_proje_lideri = request.POST.get('sorumlu_proje_lideri', 'BUSE NUR BALTACIOĞLU')
        sorumlu_fabrika_muduru = request.POST.get('sorumlu_fabrika_muduru', 'ONUR TUNCER')
        sorumlu_satis_analiz = request.POST.get('sorumlu_satis_analiz', 'METİN YAVAŞ')
        sorumlu_kalite = request.POST.get('sorumlu_kalite', 'MUHARREM FURKAN TARHAN')
        aciklama = request.POST.get('aciklama', '').strip()

        if not kod:
            sayi = YeniUrunDevreyeAlmaSureci.objects.count() + 1
            kod = f"NPI-2026-{sayi:03d}"

        musteri_karti = None
        if musteri_id:
            musteri_karti = MusteriKarti.objects.filter(id=musteri_id).first()
            if not musteri_adi and musteri_karti:
                musteri_adi = musteri_karti.ad

        urun_grubu_karti = None
        if urun_grubu_id:
            urun_grubu_karti = UrunGrubuKarti.objects.filter(id=urun_grubu_id).first()

        surec = YeniUrunDevreyeAlmaSureci.objects.create(
            kod=kod,
            ad=ad or f"{musteri_adi} Yeni Ürün Devreye Alma",
            musteri_adi=musteri_adi or "Müşteri Belirtilmedi",
            musteri_karti=musteri_karti,
            urun_grubu=urun_grubu,
            urun_grubu_karti=urun_grubu_karti,
            ilgili_fabrika=ilgili_fabrika,
            parca_kodu=parca_kodu,
            hedef_seri_uretim_tarihi=hedef_seri_uretim_tarihi,
            yillik_hedef_adet=int(yillik_hedef_adet) if yillik_hedef_adet else None,
            sorumlu_proje_lideri=sorumlu_proje_lideri,
            sorumlu_fabrika_muduru=sorumlu_fabrika_muduru,
            sorumlu_satis_analiz=sorumlu_satis_analiz,
            sorumlu_kalite=sorumlu_kalite,
            durum='DEVAM_EDIYOR',
            guncel_adim_no=1,
            aciklama=aciklama
        )

        # 45 Adımı Oluştur
        master_adimlar = YeniUrunAdimTanimi.objects.all().order_by('adim_no')
        for adim in master_adimlar:
            YeniUrunAdimKaydi.objects.create(
                surec=surec,
                adim=adim,
                durum='DEVAM_EDIYOR' if adim.adim_no == 1 else 'BEKLIYOR'
            )

        YeniUrunGecmisLog.objects.create(
            surec=surec,
            islem="Yeni Ürün Devreye Alma (NPI) Süreci Başlatıldı",
            detay=f"Proje oluşturuldu. Başlangıç Adımı: 1. Yeni Ürün Talebi. Sorumlu: {sorumlu_proje_lideri}",
            yapan=request.POST.get('tamamlayan', 'Buse Nur Baltacıoğlu')
        )

        messages.success(request, f"'{surec.kod}' kodlu Yeni Ürün Devreye Alma süreci başarıyla oluşturuldu.")
        return redirect('yeni_urun_detay', pk=surec.pk)

    return redirect('yeni_urun_liste')


def yeni_urun_detay(request, pk):
    """
    45 Adımlık Yeni Ürün Devreye Alma Süreci Detayı ve İstasyon Yönetimi
    """
    surec = get_object_or_404(YeniUrunDevreyeAlmaSureci, pk=pk)
    adimlar = surec.adim_kayitlari.select_related('adim').all().order_by('adim__adim_no')
    loglar = surec.tarihce_kayitlari.all()

    # Faz Gruplamaları
    faz1_adimlar = [a for a in adimlar if a.adim.faz == 'FAZ1']
    faz2_adimlar = [a for a in adimlar if a.adim.faz == 'FAZ2']
    faz3_adimlar = [a for a in adimlar if a.adim.faz == 'FAZ3']
    faz4_adimlar = [a for a in adimlar if a.adim.faz == 'FAZ4']
    faz5_adimlar = [a for a in adimlar if a.adim.faz == 'FAZ5']

    context = {
        'surec': surec,
        'adimlar': adimlar,
        'faz1_adimlar': faz1_adimlar,
        'faz2_adimlar': faz2_adimlar,
        'faz3_adimlar': faz3_adimlar,
        'faz4_adimlar': faz4_adimlar,
        'faz5_adimlar': faz5_adimlar,
        'loglar': loglar,
        'tarihce': loglar,
    }
    return render(request, 'crm_takip/yeni_urun_detay.html', context)


def yeni_urun_adim_aksiyon(request, pk, adim_id):
    """
    45 Adımlık Yeni Ürün Devreye Alma Sürecinde Adım Tamamlama ve Karar Motoru
    """
    surec = get_object_or_404(YeniUrunDevreyeAlmaSureci, pk=pk)
    adim_kaydi = get_object_or_404(YeniUrunAdimKaydi, surec=surec, id=adim_id)
    adim_no = adim_kaydi.adim.adim_no

    if request.method == 'POST':
        aksiyon = request.POST.get('aksiyon')
        tamamlayan = request.POST.get('tamamlayan') or (request.user.get_full_name() if request.user.is_authenticated and request.user.get_full_name() else 'Buse Nur Baltacıoğlu')
        notlar = request.POST.get('notlar', '').strip()
        dokuman_ref = request.POST.get('dokuman_referansi', '').strip()

        adim_kaydi.tamamlayan = tamamlayan
        adim_kaydi.notlar = notlar
        adim_kaydi.dokuman_referansi = dokuman_ref

        # Ara Kaydet / Not ve Doküman Güncelleme
        if aksiyon in ['KAYDET', 'GUNCELLE']:
            if adim_kaydi.durum == 'BEKLIYOR':
                adim_kaydi.durum = 'DEVAM_EDIYOR'
            adim_kaydi.save()

            YeniUrunGecmisLog.objects.create(
                surec=surec,
                islem=f"Adım {adim_no}: Notlar ve Doküman Kaydedildi",
                detay=f"Not/doküman bilgileri güncellendi. Doküman: {dokuman_ref or '-'}, Not: {notlar or 'Girilmedi.'}",
                yapan=tamamlayan
            )
            messages.success(request, f"Adım {adim_no} not ve doküman bilgileri başarıyla kaydedildi.")
            return redirect(f"{redirect('yeni_urun_detay', pk=surec.pk).url}#adim-{adim_no}")

        adim_kaydi.tamamlanma_tarihi = timezone.now()

        # -------------------------------------------------------------
        # 1. ADIM 2: Talep, Belge ve Numune Ön Değerlendirmesi
        # -------------------------------------------------------------
        if adim_no == 2:
            if aksiyon == 'EVET':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'EVET (Ön Değerlendirme Uygun -> Adım 4 Ekip Belirleme)'
                adim_kaydi.save()

                # Adım 3 standart dışı proses adımı pas geçilir
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no=3).update(durum='PAS_GECILDI', karar_sonucu='Pas Geçildi (Standart Prosese Uygun)')
                surec.guncel_adim_no = 4
                surec.save()
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no=4).update(durum='DEVAM_EDIYOR')

                YeniUrunGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 2: Ön Değerlendirme Onaylandı",
                    detay="Ürün ön değerlendirmesi standart proseslerimize uygun bulundu. 4. Adım (Fizibilite Ekibi Belirleme) başlatıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "Ön değerlendirme onaylandı! Standart prosese uygun olduğu için Adım 4'e geçildi.")

            elif aksiyon == 'HAYIR':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'HAYIR (Standart Dışı Proses -> Satış Departmanı İletimi)'
                adim_kaydi.save()

                surec.guncel_adim_no = 3
                surec.save()
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no=3).update(durum='DEVAM_EDIYOR')

                YeniUrunGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 2: Standart Dışı Proses Tespit Edildi",
                    detay=f"Ürün standart proseslerimize uymadığı için stratejik değerlendirme amacıyla Satış Departmanına iletildi. Not: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Standart dışı proses! Stratejik değerlendirme için konu Adım 3 (Satış Departmanı) aktarıldı.")

        # -------------------------------------------------------------
        # 2. ADIM 9: Fizibilite Çalışması Sonucu Uygun mu?
        # -------------------------------------------------------------
        elif adim_no == 9:
            if aksiyon == 'EVET':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'EVET (Fizibilite Çalışması Uygun)'
                adim_kaydi.save()

                surec.guncel_adim_no = 10
                surec.save()
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no=10).update(durum='DEVAM_EDIYOR')

                YeniUrunGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 9: Fizibilite Onaylandı",
                    detay="Fizibilite çalışması uygun bulundu. Adım 10 (Geçici BOM & Şahit Numune Kaydı) başlatıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "Fizibilite çalışması uygun bulundu! 10. Adıma geçildi.")

            elif aksiyon == 'HAYIR':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'HAYIR (Fizibilite Uygun Değil -> Stratejik Değerlendirme)'
                adim_kaydi.save()

                # Adım 10 pas geçilir, doğrudan Adım 11'e aktarılır
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no=10).update(durum='PAS_GECILDI', karar_sonucu='Pas Geçildi (Fizibilite Uygun Değil)')
                surec.guncel_adim_no = 11
                surec.save()
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no=11).update(durum='DEVAM_EDIYOR')

                YeniUrunGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 9: Fizibilite Olumsuz Sonuçlandı",
                    detay=f"Fizibilite uygun bulunmadı. Rapor doğrultusunda stratejik görüşme için Adım 11'e aktarıldı. Not: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Fizibilite uygun bulunmadı. Satış/Müşteri değerlendirmesi için 11. Adıma aktarıldı.")

        # -------------------------------------------------------------
        # 3. ADIM 12: Müşteri Proje Başlangıç Onayı
        # -------------------------------------------------------------
        elif adim_no == 12:
            if aksiyon == 'EVET':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'EVET (Müşteri Proje Başlangıç Onayı Verdi)'
                adim_kaydi.save()

                surec.guncel_adim_no = 13
                surec.save()
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no=13).update(durum='DEVAM_EDIYOR')

                YeniUrunGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 12: Müşteri Başlangıç Onayı Alındı",
                    detay="Müşteri görüşmeleri neticesinde proje onayı alındı. Faz 2 (Proje Planlama & Tedarik) Adım 13 başlatıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "Müşteri proje onayı verdi! Faz 2 (Adım 13) başlatıldı.")

            elif aksiyon == 'HAYIR':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'HAYIR (Müşteri Projeyi Onaylamadı -> Kapatma)'
                adim_kaydi.save()

                # Adım 13-43 pas geçilir, süreç Adım 44'e aktarılır ve olumsuz kapatılır
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no__gte=13, adim__adim_no__lte=43).update(durum='PAS_GECILDI')
                surec.guncel_adim_no = 44
                surec.durum = 'OLUMSUZ_KAPATILDI'
                surec.save()
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no=44).update(durum='DEVAM_EDIYOR')

                YeniUrunGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 12: Müşteri Onayı Alınamadı -> Süreç Kapatıldı",
                    detay=f"Müşteri proje başlangıcına onay vermediği için proje sonlandırıldı ve raporlama için Adım 44'e aktarıldı. Not: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Müşteri onay vermedi. Proje kapatılmak üzere Adım 44'e aktarıldı.")

        # -------------------------------------------------------------
        # 4. ADIM 26: Numune Ölçüm Sonuçları Uygun mu? (ISIR)
        # -------------------------------------------------------------
        elif adim_no == 26:
            if aksiyon == 'EVET':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'EVET (ISIR Ölçüm Sonuçları Uygun)'
                adim_kaydi.save()

                surec.guncel_adim_no = 27
                surec.save()
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no=27).update(durum='DEVAM_EDIYOR')

                YeniUrunGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 26: Numune Kalite Kontrolü (ISIR) Onaylandı",
                    detay="Numunelerin tüm teknik ölçüm ve tolerans testleri uygun bulundu. Adım 27 (Müşteriye Sevk) başlatıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "Numune kalite kontrolü onaylandı! Numune sevk adımı başlatıldı.")

            elif aksiyon == 'HAYIR':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'HAYIR (Ölçüm Uygunsuzluğu -> Adım 20 Ürün Ağacı / Numune Revizyonu)'
                adim_kaydi.save()

                # Adım 21-26 resetlenir, Adım 20 aktif edilir
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no__in=[21, 22, 23, 24, 25, 26]).update(durum='BEKLIYOR', karar_sonucu=None)
                surec.guncel_adim_no = 20
                surec.durum = 'REVIZYONDA'
                surec.save()
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no=20).update(durum='DEVAM_EDIYOR')

                YeniUrunGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 26: Numune Ölçüm Uygunsuzluğu -> Adım 20'ye Geri Dönüş",
                    detay=f"Ölçüm sonuçları şartnameye uymadığı için ürün ağacı ve üretim parametreleri revizyonu amacıyla 20. Adıma dönüldü. Not: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Numune ölçümleri uygunsuz! Ürün ağacı ve numune hazırlığı için 20. Adıma geri yönlendirildi.")

        # -------------------------------------------------------------
        # 5. ADIM 28: Müşteri Numune Onayı
        # -------------------------------------------------------------
        elif adim_no == 28:
            if aksiyon == 'EVET':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'EVET (Müşteri Numuneyi Onayladı)'
                adim_kaydi.save()

                surec.guncel_adim_no = 29
                surec.save()
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no=29).update(durum='DEVAM_EDIYOR')

                YeniUrunGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 28: Müşteri Numune Onayı Alındı",
                    detay="Müşteri numune ve ISIR belgelerini onayladı. Adım 29 (Teknik Dokümantasyon & Talimatlar) başlatıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "Müşteri numuneyi onayladı! Adım 29'a geçildi.")

            elif aksiyon == 'HAYIR':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'HAYIR (Müşteri Numuneyi Reddetti / Revizyon İstedi -> Adım 20)'
                adim_kaydi.save()

                # Adım 21-28 resetlenir, Adım 20 aktif edilir
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no__gte=21, adim__adim_no__lte=28).update(durum='BEKLIYOR', karar_sonucu=None)
                surec.guncel_adim_no = 20
                surec.durum = 'REVIZYONDA'
                surec.save()
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no=20).update(durum='DEVAM_EDIYOR')

                YeniUrunGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 28: Müşteri Numune Revizyonu İstedi -> Adım 20",
                    detay=f"Müşteri geri bildirimi doğrultusunda numune revizyonu için Adım 20'ye dönüldü. Müşteri Talebi: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Müşteri numune revizyonu istedi. Süreç 20. Adıma geri yönlendirildi.")

        # -------------------------------------------------------------
        # 6. ADIM 33: MSA Sonuçları Sistem Gerekliliklerini Karşılıyor mu?
        # -------------------------------------------------------------
        elif adim_no == 33:
            if aksiyon == 'EVET':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'EVET (MSA Sonuçları Uygun)'
                adim_kaydi.save()

                surec.durum = 'DEVAM_EDIYOR'
                surec.guncel_adim_no = 34
                surec.save()
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no=34).update(durum='DEVAM_EDIYOR')

                YeniUrunGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 33: MSA Yeterliliği Onaylandı",
                    detay="Ölçüm sistemi analiz sonuçları standartlara uygun bulundu. Adım 34 (Makine/Proses Yeterlilik) başlatıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "MSA sonuçları onaylandı! Adım 34 başlatıldı.")

            elif aksiyon == 'HAYIR' or aksiyon == 'DOF_AC':
                adim_kaydi.durum = 'DEVAM_EDIYOR'
                adim_kaydi.karar_sonucu = 'HAYIR (MSA Yetersiz -> DÖF / Uygunsuzluk Süreci Devrede)'
                adim_kaydi.save()

                surec.durum = 'UYGUNSUZLUK_YONETIMINDE'
                surec.save()

                YeniUrunGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 33: MSA Uygunsuzluğu (DÖF Başlatıldı)",
                    detay=f"Ölçüm sistemi yeterliliği sağlanamadığı için Kalite Uygunsuzluk Süreci başlatıldı. DÖF Açıklaması: {notlar}",
                    yapan=tamamlayan
                )
                messages.error(request, "MSA uygunsuzluğu! DÖF / Uygunsuzluk Yönetim Süreci devreye alındı.")

            elif aksiyon == 'UYGUNSUZLUK_COZULDU':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'DÖF Çözüldü (MSA Yeterliliği Sağlandı)'
                adim_kaydi.save()

                surec.durum = 'DEVAM_EDIYOR'
                surec.guncel_adim_no = 34
                surec.save()
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no=34).update(durum='DEVAM_EDIYOR')

                YeniUrunGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 33: DÖF Başarıyla Çözüldü & Kapatıldı",
                    detay=f"Düzeltici Önleyici Faaliyet tamamlandı, ölçüm sistemi doğrulandı. Çözüm Notu: {notlar}",
                    yapan=tamamlayan
                )
                messages.success(request, "DÖF başarıyla tamamlandı! Süreç 34. Adıma aktarıldı.")

        # -------------------------------------------------------------
        # 7. ADIM 35: Proses / Makine Yeterlilik Çalışması Sonuçları Uygun mu?
        # -------------------------------------------------------------
        elif adim_no == 35:
            if aksiyon == 'EVET':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'EVET (Cpk / Ppk Yeterliliği Sağlandı)'
                adim_kaydi.save()

                surec.durum = 'DEVAM_EDIYOR'
                surec.guncel_adim_no = 36
                surec.save()
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no=36).update(durum='DEVAM_EDIYOR')

                YeniUrunGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 35: Proses/Makine Yeterliliği Onaylandı",
                    detay="Cpk/Ppk yeterlilik analizleri başarıyla onaylandı. Adım 36 (Ön Seri Kalite Kontrol) başlatıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "Proses ve makine yeterliliği onaylandı! Adım 36 başlatıldı.")

            elif aksiyon == 'HAYIR' or aksiyon == 'DOF_AC':
                adim_kaydi.durum = 'DEVAM_EDIYOR'
                adim_kaydi.karar_sonucu = 'HAYIR (Yeterlilik Sağlanamadı -> DÖF Sürecinde)'
                adim_kaydi.save()

                surec.durum = 'UYGUNSUZLUK_YONETIMINDE'
                surec.save()

                YeniUrunGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 35: Proses Yeterlilik Uygunsuzluğu (DÖF Başlatıldı)",
                    detay=f"Makine/proses yeterliliği hedeflenen Cpk değerini karşılamadığı için DÖF açıldı. Not: {notlar}",
                    yapan=tamamlayan
                )
                messages.error(request, "Proses yeterlilik uygunsuzluğu! DÖF / Uygunsuzluk Süreci başlatıldı.")

            elif aksiyon == 'UYGUNSUZLUK_COZULDU':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'DÖF Çözüldü (Yeterlilik Sağlandı)'
                adim_kaydi.save()

                surec.durum = 'DEVAM_EDIYOR'
                surec.guncel_adim_no = 36
                surec.save()
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no=36).update(durum='DEVAM_EDIYOR')

                YeniUrunGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 35: DÖF Tamamlandı & Yeterlilik Sağlandı",
                    detay=f"Makine ayar/kalıp iyileştirmesi sonrası yeterlilik sağlandı. Çözüm: {notlar}",
                    yapan=tamamlayan
                )
                messages.success(request, "DÖF tamamlandı! 36. Adıma geçildi.")

        # -------------------------------------------------------------
        # 8. ADIM 37: Ön Seri Ürün Kalite Ölçüm Sonuçları Uygun mu?
        # -------------------------------------------------------------
        elif adim_no == 37:
            if aksiyon == 'EVET':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'EVET (Ön Seri Kalite Ölçümleri Uygun)'
                adim_kaydi.save()

                surec.guncel_adim_no = 38
                surec.save()
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no=38).update(durum='DEVAM_EDIYOR')

                YeniUrunGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 37: Ön Seri Kalite Kontrolü Onaylandı",
                    detay="Ön seri çıkış kalite kontrol raporu onaylandı. Adım 38 (PPAP Dosyası & Sevkiyat) başlatıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "Ön seri kalite kontrolü onaylandı! PPAP hazırlık adımı başlatıldı.")

            elif aksiyon == 'HAYIR':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'HAYIR (Ön Seri Kalite Uygunsuz -> Adım 31 Yeniden Planlama)'
                adim_kaydi.save()

                # Adım 32-37 resetlenir, Adım 31 aktif edilir
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no__in=[32, 33, 34, 35, 36, 37]).update(durum='BEKLIYOR', karar_sonucu=None)
                surec.guncel_adim_no = 31
                surec.durum = 'REVIZYONDA'
                surec.save()
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no=31).update(durum='DEVAM_EDIYOR')

                YeniUrunGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 37: Ön Seri Kalite Reddi -> Adım 31'e Dönüş",
                    detay=f"Ön seri kalite kontrol ölçümleri uygunsuz çıktığı için ön seri üretimin yeniden planlanması amacıyla Adım 31'e dönüldü. Gerekçe: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Ön seri kalite sonuçları uygunsuz! Ön seri üretimi yeniden planlamak için 31. Adıma dönüldü.")

        # -------------------------------------------------------------
        # 9. ADIM 39: Müşteri Ön Seri Üretim ve PPAP Onayı
        # -------------------------------------------------------------
        elif adim_no == 39:
            if aksiyon == 'EVET':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'EVET (Müşteri PPAP & Ön Seri Onayı Verdi)'
                adim_kaydi.save()

                surec.guncel_adim_no = 40
                surec.save()
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no=40).update(durum='DEVAM_EDIYOR')

                YeniUrunGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 39: Müşteri PPAP Onayı Alındı",
                    detay="Müşteri PPAP ve ön seri üretim onayını verdi. Faz 5 (Seri Üretime Geçiş & Kapanış) Adım 40 başlatıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "Tebrikler! Müşteri PPAP ve Ön Seri onayını verdi. Seri üretime geçiş aşaması başlatıldı.")

            elif aksiyon == 'HAYIR':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'HAYIR (Müşteri PPAP Reddetti -> Adım 31 Ön Seri Revizyon)'
                adim_kaydi.save()

                # Adım 32-39 resetlenir, Adım 31 aktif edilir
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no__gte=32, adim__adim_no__lte=39).update(durum='BEKLIYOR', karar_sonucu=None)
                surec.guncel_adim_no = 31
                surec.durum = 'REVIZYONDA'
                surec.save()
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no=31).update(durum='DEVAM_EDIYOR')

                YeniUrunGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 39: Müşteri PPAP Revizyonu İstedi -> Adım 31",
                    detay=f"Müşteri ön seri/PPAP onayı vermediği için ön seri üretim revizyonu amacıyla Adım 31'e dönüldü. Müşteri Talebi: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Müşteri PPAP onayını revizyona gönderdi. Süreç 31. Adıma geri yönlendirildi.")

        # -------------------------------------------------------------
        # 10. DİĞER SIRADAN ADIMLAR
        # -------------------------------------------------------------
        else:
            adim_kaydi.durum = 'TAMAMLANDI'
            adim_kaydi.karar_sonucu = 'Tamamlandı'
            adim_kaydi.save()

            if adim_no < 45:
                sonraki_adim_no = adim_no + 1
                surec.guncel_adim_no = sonraki_adim_no
                surec.save()
                YeniUrunAdimKaydi.objects.filter(surec=surec, adim__adim_no=sonraki_adim_no).update(durum='DEVAM_EDIYOR')

                YeniUrunGecmisLog.objects.create(
                    surec=surec,
                    islem=f"Adım {adim_no}: {adim_kaydi.adim.baslik} Tamamlandı",
                    detay=f"{notlar or 'İşlem tamamlandı ve sonraki adıma aktarıldı.'} Doküman: {dokuman_ref or '-'}",
                    yapan=tamamlayan
                )
                messages.success(request, f"{adim_no}. Adım tamamlandı. {sonraki_adim_no}. Adıma geçildi.")
            else:
                surec.durum = 'BASARIYLA_TAMAMLANDI'
                surec.save()

                YeniUrunGecmisLog.objects.create(
                    surec=surec,
                    islem="Yeni Ürün Devreye Alma Süreci Başarıyla Tamamlandı",
                    detay=f"45 adımlık NPI süreci başarıyla tamamlandı. Seri üretime geçiş tamamlandı, öğrenilmiş dersler kaydedildi. Kapanış Notu: {notlar}",
                    yapan=tamamlayan
                )
                messages.success(request, "Tebrikler! Yeni Ürün Devreye Alma (NPI) Süreci başarıyla tamamlandı ve arşivlendi.")

    return redirect(f"{redirect('yeni_urun_detay', pk=pk).url}#adim-{surec.guncel_adim_no}")


def yeni_urun_sil(request, pk):
    surec = get_object_or_404(YeniUrunDevreyeAlmaSureci, pk=pk)
    if request.method == 'POST':
        kod = surec.kod
        surec.delete()
        messages.success(request, f"'{kod}' kodlu Yeni Ürün Devreye Alma Süreci başarıyla silindi.")
    return redirect('yeni_urun_liste')


# ==============================================================================
# 6. MÜHENDİSLİK DEĞİŞİKLİĞİ SÜRECİ (34 ADIM - ECO / ECM) VIEWS
# ==============================================================================

def muhendislik_degisikligi_liste(request):
    """
    34 Adımlık Mühendislik Değişikliği Süreci (ECO) Ana Listesi
    """
    surecler = MuhendislikDegisikligiSureci.objects.select_related('musteri_karti').all()

    q = request.GET.get('q', '').strip()
    durum_filtre = request.GET.get('durum', '')
    fabrika_filtre = request.GET.get('fabrika', '')
    urun_filtre = request.GET.get('urun_grubu', '')
    neden_filtre = request.GET.get('degisiklik_nedeni', '')

    if q:
        surecler = surecler.filter(
            Q(kod__icontains=q) |
            Q(musteri_adi__icontains=q) |
            Q(ad__icontains=q) |
            Q(parca_kodu__icontains=q)
        )

    if durum_filtre:
        surecler = surecler.filter(durum=durum_filtre)

    if fabrika_filtre:
        surecler = surecler.filter(ilgili_fabrika=fabrika_filtre)

    if urun_filtre:
        surecler = surecler.filter(urun_grubu=urun_filtre)

    if neden_filtre:
        surecler = surecler.filter(degisiklik_nedeni=neden_filtre)

    toplam_surec = MuhendislikDegisikligiSureci.objects.count()
    aktif_surec = MuhendislikDegisikligiSureci.objects.filter(durum='DEVAM_EDIYOR').count()
    revizyon_surec = MuhendislikDegisikligiSureci.objects.filter(durum='REVIZYONDA').count()
    tamamlanan_surec = MuhendislikDegisikligiSureci.objects.filter(durum='BASARIYLA_TAMAMLANDI').count()

    musteri_kartlari = MusteriKarti.objects.all().order_by('kisa_ad')

    context = {
        'surecler': surecler,
        'toplam_surec': toplam_surec,
        'aktif_surec': aktif_surec,
        'revizyon_surec': revizyon_surec,
        'tamamlanan_surec': tamamlanan_surec,
        'musteri_kartlari': musteri_kartlari,
        'q': q,
        'durum_filtre': durum_filtre,
        'fabrika_filtre': fabrika_filtre,
        'urun_filtre': urun_filtre,
        'neden_filtre': neden_filtre,
    }
    return render(request, 'crm_takip/muhendislik_degisikligi_liste.html', context)


def muhendislik_degisikligi_olustur(request):
    """
    Yeni Mühendislik Değişikliği (ECO) Talebi Başlatma ve 34 Adımın Otomatik Oluşturulması
    """
    if request.method == 'POST':
        kod = request.POST.get('kod', '').strip()
        ad = request.POST.get('ad', '').strip()
        musteri_adi = request.POST.get('musteri_adi', '').strip()
        parca_kodu = request.POST.get('parca_kodu', '').strip()
        revizyon_no = request.POST.get('revizyon_no', 'Rev.01').strip()
        degisiklik_nedeni = request.POST.get('degisiklik_nedeni', 'MUSTERI_TALEBI')
        urun_grubu = request.POST.get('urun_grubu', 'Metal Parca & Sac')
        ilgili_fabrika = request.POST.get('ilgili_fabrika', 'PRESHANE')
        hedef_tamamlanma_tarihi = request.POST.get('hedef_tamamlanma_tarihi') or None

        sorumlu_proje_sorumlusu = request.POST.get('sorumlu_proje_sorumlusu', 'BUSE NUR BALTACIOĞLU').strip()
        sorumlu_fabrika_muduru = request.POST.get('sorumlu_fabrika_muduru', 'ONUR TUNCER').strip()
        sorumlu_satis_analiz = request.POST.get('sorumlu_satis_analiz', 'METİN YAVAŞ').strip()
        sorumlu_kalite = request.POST.get('sorumlu_kalite', 'MUHARREM FURKAN TARHAN').strip()

        aciklama = request.POST.get('aciklama', '').strip()

        year = timezone.now().year

        # Otomatik Benzersiz Kod
        if not kod:
            num = 1
            while MuhendislikDegisikligiSureci.objects.filter(kod=f"ECO-{year}-{num:03d}").exists():
                num += 1
            kod = f"ECO-{year}-{num:03d}"
        else:
            if MuhendislikDegisikligiSureci.objects.filter(kod=kod).exists():
                base_kod = kod
                suffix = 1
                while MuhendislikDegisikligiSureci.objects.filter(kod=f"{base_kod}-{suffix:02d}").exists():
                    suffix += 1
                kod = f"{base_kod}-{suffix:02d}"

        # İlişkili Müşteri Kartı Eşleştirme
        musteri_karti = MusteriKarti.objects.filter(
            Q(kisa_ad__icontains=musteri_adi) | Q(ad__icontains=musteri_adi)
        ).first()

        surec = MuhendislikDegisikligiSureci.objects.create(
            kod=kod,
            ad=ad,
            musteri_adi=musteri_adi,
            musteri_karti=musteri_karti,
            parca_kodu=parca_kodu,
            revizyon_no=revizyon_no,
            degisiklik_nedeni=degisiklik_nedeni,
            urun_grubu=urun_grubu,
            ilgili_fabrika=ilgili_fabrika,
            hedef_tamamlanma_tarihi=hedef_tamamlanma_tarihi,
            sorumlu_proje_sorumlusu=sorumlu_proje_sorumlusu,
            sorumlu_fabrika_muduru=sorumlu_fabrika_muduru,
            sorumlu_satis_analiz=sorumlu_satis_analiz,
            sorumlu_kalite=sorumlu_kalite,
            aciklama=aciklama,
            durum='DEVAM_EDIYOR',
            guncel_adim_no=1
        )

        # 34 Adımı Zincirleme Oluştur
        adim_tanimlari = MuhendislikDegisikligiAdimTanimi.objects.all().order_by('adim_no')
        for adim in adim_tanimlari:
            durum = 'DEVAM_EDIYOR' if adim.adim_no == 1 else 'BEKLIYOR'
            MuhendislikDegisikligiAdimKaydi.objects.create(
                surec=surec,
                adim=adim,
                durum=durum
            )

        MuhendislikDegisikligiGecmisLog.objects.create(
            surec=surec,
            islem=f"Mühendislik Değişikliği Başlatıldı: {surec.kod}",
            detay=f"{surec.ad} konulu değişiklik süreci açıldı ve 1. Adım başlatıldı.",
            yapan=sorumlu_proje_sorumlusu
        )

        messages.success(request, f"'{surec.kod}' kodlu Mühendislik Değişikliği Süreci başarıyla oluşturuldu ve 34 adımlık iş akışı başlatıldı!")
        return redirect('muhendislik_degisikligi_detay', pk=surec.pk)

    return redirect('muhendislik_degisikligi_liste')


def muhendislik_degisikligi_detay(request, pk):
    """
    34 Adımlık Mühendislik Değişikliği Süreci Detay Sayfası
    """
    surec = get_object_or_404(MuhendislikDegisikligiSureci, pk=pk)
    adim_kayitlari = surec.adim_kayitlari.select_related('adim').order_by('adim__adim_no')
    tarihce = surec.tarihce_kayitlari.all()[:20]

    faz1_adimlar = [a for a in adim_kayitlari if a.adim.adim_no in range(1, 12)]
    faz2_adimlar = [a for a in adim_kayitlari if a.adim.adim_no in range(12, 19)]
    faz3_adimlar = [a for a in adim_kayitlari if a.adim.adim_no in range(19, 28)]
    faz4_adimlar = [a for a in adim_kayitlari if a.adim.adim_no in range(28, 35)]

    context = {
        'surec': surec,
        'adimlar': adim_kayitlari,
        'faz1_adimlar': faz1_adimlar,
        'faz2_adimlar': faz2_adimlar,
        'faz3_adimlar': faz3_adimlar,
        'faz4_adimlar': faz4_adimlar,
        'tarihce': tarihce,
    }
    return render(request, 'crm_takip/muhendislik_degisikligi_detay.html', context)


def muhendislik_degisikligi_adim_aksiyon(request, pk, adim_id):
    """
    34 Adımlık Mühendislik Değişikliği Süreci Karar ve İlerleme Motoru
    """
    surec = get_object_or_404(MuhendislikDegisikligiSureci, pk=pk)
    adim_kaydi = get_object_or_404(MuhendislikDegisikligiAdimKaydi, surec=surec, id=adim_id)
    adim_no = adim_kaydi.adim.adim_no

    if request.method == 'POST':
        aksiyon = request.POST.get('aksiyon')
        tamamlayan = request.POST.get('tamamlayan') or (request.user.get_full_name() if request.user.is_authenticated and request.user.get_full_name() else 'Buse Nur Baltacıoğlu')
        notlar = request.POST.get('notlar', '').strip()
        dokuman_ref = request.POST.get('dokuman_referansi', '').strip()

        adim_kaydi.tamamlayan = tamamlayan
        adim_kaydi.notlar = notlar
        adim_kaydi.dokuman_referansi = dokuman_ref

        # Ara Kaydet / Not ve Doküman Güncelleme
        if aksiyon in ['KAYDET', 'GUNCELLE']:
            if adim_kaydi.durum == 'BEKLIYOR':
                adim_kaydi.durum = 'DEVAM_EDIYOR'
            adim_kaydi.save()

            MuhendislikDegisikligiGecmisLog.objects.create(
                surec=surec,
                islem=f"Adım {adim_no}: Notlar ve Doküman Kaydedildi",
                detay=f"Not/doküman güncellendi. Doküman: {dokuman_ref or '-'}, Not: {notlar or 'Girilmedi.'}",
                yapan=tamamlayan
            )
            messages.success(request, f"Adım {adim_no} not ve doküman referansı başarıyla kaydedildi.")
            return redirect(f"{redirect('muhendislik_degisikligi_detay', pk=surec.pk).url}#adim-{adim_no}")

        adim_kaydi.tamamlanma_tarihi = timezone.now()

        # -------------------------------------------------------------
        # 1. ADIM 11: Yeni Ürün Devreye Alma Kapsam Değerlendirmesi
        # -------------------------------------------------------------
        if adim_no == 11:
            if aksiyon == 'EVET':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'EVET (Yeni Ürün Devreye Alma Sürecine Aktarıldı)'
                adim_kaydi.save()

                surec.durum = 'YENI_URUN_SURECINE_AKTARILDI'
                surec.save()

                # Kalan adımlar pas geçilir
                MuhendislikDegisikligiAdimKaydi.objects.filter(surec=surec, adim__adim_no__gte=12).update(
                    durum='PAS_GECILDI',
                    karar_sonucu='Yeni Ürün Devreye Alma Sürecine Aktarıldığı İçin Muaf Tutuldu'
                )

                MuhendislikDegisikligiGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 11: Yeni Ürün Sürecine Yönlendirildi",
                    detay=f"Değişikliğin kapsamı gereği 'Yeni Ürün Devreye Alma Süreci' başlatılması kararlaştırıldı. Not: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Değişikliğin boyutu gereği süreç 'Yeni Ürün Devreye Alma Süreci'ne aktarılarak tamamlandı.")

            elif aksiyon == 'HAYIR':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'HAYIR (Standart Mühendislik Değişikliği Olarak Devam)'
                adim_kaydi.save()

                surec.guncel_adim_no = 12
                surec.save()
                MuhendislikDegisikligiAdimKaydi.objects.filter(surec=surec, adim__adim_no=12).update(durum='DEVAM_EDIYOR')

                MuhendislikDegisikligiGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 11: Standart Mühendislik Değişikliği Onaylandı",
                    detay="Değişiklik standart mühendislik değişikliği kapsamında onaylandı. Faz 2 Adım 12 başlatıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "Değerlendirme tamamlandı! Süreç standart değişiklik olarak Faz 2'ye (12. Adım) geçti.")

        # -------------------------------------------------------------
        # 2. ADIM 20: Numune ISIR Ölçüm Sonuçları Uygun mu?
        # -------------------------------------------------------------
        elif adim_no == 20:
            if aksiyon == 'EVET':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'EVET (ISIR Ölçüm Sonuçları Uygun)'
                adim_kaydi.save()

                surec.durum = 'DEVAM_EDIYOR'
                surec.guncel_adim_no = 21
                surec.save()
                MuhendislikDegisikligiAdimKaydi.objects.filter(surec=surec, adim__adim_no=21).update(durum='DEVAM_EDIYOR')

                MuhendislikDegisikligiGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 20: Numune ISIR Ölçümleri Onaylandı",
                    detay="Numune ISIR kalite ölçümleri teknik şartnameye uygun bulundu. Adım 21 (Müşteriye Sevk) başlatıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "ISIR ölçümleri onaylandı! 21. Adım (Müşteriye Sevk) başlatıldı.")

            elif aksiyon == 'HAYIR':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'HAYIR (Ölçüm Uygunsuzluğu -> Adım 13 BOM Revizyonuna Dönüş)'
                adim_kaydi.save()

                # Adım 14-20 resetlenir, Adım 13 aktif edilir
                MuhendislikDegisikligiAdimKaydi.objects.filter(surec=surec, adim__adim_no__gte=14, adim__adim_no__lte=20).update(durum='BEKLIYOR', karar_sonucu=None)
                surec.guncel_adim_no = 13
                surec.durum = 'REVIZYONDA'
                surec.save()
                MuhendislikDegisikligiAdimKaydi.objects.filter(surec=surec, adim__adim_no=13).update(durum='DEVAM_EDIYOR')

                MuhendislikDegisikligiGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 20: Numune ISIR Reddi -> Adım 13'e Dönüş",
                    detay=f"Numune ölçümleri teknik şartnameye uymadı. Geçici BOM ve numune üretimi revizyonu için Adım 13'e dönüldü. Gerekçe: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Numune ISIR ölçümleri uygunsuz! Süreç revizyon amacıyla 13. Adıma geri yönlendirildi.")

        # -------------------------------------------------------------
        # 3. ADIM 22: Müşteri Sevk Edilen Numuneyi Onayladı mı?
        # -------------------------------------------------------------
        elif adim_no == 22:
            if aksiyon == 'EVET':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'EVET (Müşteri Numuneyi Onayladı)'
                adim_kaydi.save()

                surec.durum = 'DEVAM_EDIYOR'
                surec.guncel_adim_no = 23
                surec.save()
                MuhendislikDegisikligiAdimKaydi.objects.filter(surec=surec, adim__adim_no=23).update(durum='DEVAM_EDIYOR')

                MuhendislikDegisikligiGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 22: Müşteri Numune Onayı Alındı",
                    detay="Müşteri numune kontrolünü onayladı. Adım 23 (Ön Seri Üretim Talebi Kontrolü) başlatıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "Müşteri numuneyi onayladı! 23. Adıma geçildi.")

            elif aksiyon == 'HAYIR':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'HAYIR (Müşteri Numuneyi Reddetti -> Adım 13)'
                adim_kaydi.save()

                # Adım 14-22 resetlenir, Adım 13 aktif edilir
                MuhendislikDegisikligiAdimKaydi.objects.filter(surec=surec, adim__adim_no__gte=14, adim__adim_no__lte=22).update(durum='BEKLIYOR', karar_sonucu=None)
                surec.guncel_adim_no = 13
                surec.durum = 'REVIZYONDA'
                surec.save()
                MuhendislikDegisikligiAdimKaydi.objects.filter(surec=surec, adim__adim_no=13).update(durum='DEVAM_EDIYOR')

                MuhendislikDegisikligiGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 22: Müşteri Numune Reddi -> Adım 13'e Dönüş",
                    detay=f"Müşteri numuneyi revizyona gönderdi. Yeniden numune hazırlığı için Adım 13'e dönüldü. Müşteri Talebi: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Müşteri numuneyi onaylamadı. Süreç 13. Adıma geri yönlendirildi.")

        # -------------------------------------------------------------
        # 4. ADIM 23: Müşterinin Ön Seri Üretim Talebi Var mı?
        # -------------------------------------------------------------
        elif adim_no == 23:
            if aksiyon == 'EVET':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'EVET (Ön Seri Üretim Talebi Var -> Adım 24)'
                adim_kaydi.save()

                surec.guncel_adim_no = 24
                surec.save()
                MuhendislikDegisikligiAdimKaydi.objects.filter(surec=surec, adim__adim_no=24).update(durum='DEVAM_EDIYOR')

                MuhendislikDegisikligiGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 23: Ön Seri Üretim Talebi Alındı",
                    detay="Müşteri ön seri üretim talep etti. Adım 24 (Ön Seri Planlama & İş Emri) başlatıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "Ön seri üretim talebi alındı! 24. Adım başlatıldı.")

            elif aksiyon == 'HAYIR':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'HAYIR (Ön Seri Talebi Yok -> Doğrudan Adım 28 Seri BOM)'
                adim_kaydi.save()

                # Adım 24, 25, 26, 27 pas geçilir
                MuhendislikDegisikligiAdimKaydi.objects.filter(surec=surec, adim__adim_no__in=[24, 25, 26, 27]).update(
                    durum='PAS_GECILDI',
                    karar_sonucu='Ön Seri Talebi Olmadığı İçin Pas Geçildi'
                )

                surec.guncel_adim_no = 28
                surec.save()
                MuhendislikDegisikligiAdimKaydi.objects.filter(surec=surec, adim__adim_no=28).update(durum='DEVAM_EDIYOR')

                MuhendislikDegisikligiGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 23: Ön Seri Gerekmedi -> Doğrudan Faz 4'e Geçildi",
                    detay="Müşterinin ön seri talebi bulunmadığından 24-27 adımları pas geçilerek doğrudan Adım 28 (Mamul Stok Kodu & Seri BOM) başlatıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "Ön seri talebi yok; doğrudan 28. Adıma (Seri BOM & Kod Oluşturma) geçildi.")

        # -------------------------------------------------------------
        # 5. ADIM 27: Ön Seri Üretim Sonrası Müşteri Onayı
        # -------------------------------------------------------------
        elif adim_no == 27:
            if aksiyon == 'EVET':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'EVET (Ön Seri Müşteri Tarafından Onaylandı)'
                adim_kaydi.save()

                surec.durum = 'DEVAM_EDIYOR'
                surec.guncel_adim_no = 28
                surec.save()
                MuhendislikDegisikligiAdimKaydi.objects.filter(surec=surec, adim__adim_no=28).update(durum='DEVAM_EDIYOR')

                MuhendislikDegisikligiGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 27: Müşteri Ön Seri Onayını Verdi",
                    detay="Müşteri ön seri üretimi onayladı. Faz 4 (Seri Üretime Geçiş) Adım 28 başlatıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "Müşteri ön seri üretim onayını verdi! Faz 4 (28. Adım) başlatıldı.")

            elif aksiyon == 'HAYIR':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'HAYIR (Ön Seri Reddi -> Adım 24 Yeniden Planlama)'
                adim_kaydi.save()

                # Adım 25-27 resetlenir, Adım 24 aktif edilir
                MuhendislikDegisikligiAdimKaydi.objects.filter(surec=surec, adim__adim_no__in=[25, 26, 27]).update(durum='BEKLIYOR', karar_sonucu=None)
                surec.guncel_adim_no = 24
                surec.durum = 'REVIZYONDA'
                surec.save()
                MuhendislikDegisikligiAdimKaydi.objects.filter(surec=surec, adim__adim_no=24).update(durum='DEVAM_EDIYOR')

                MuhendislikDegisikligiGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 27: Ön Seri Reddi -> Adım 24'e Dönüş",
                    detay=f"Ön seri üretim onaylanmadığı için yeniden planlanmak üzere Adım 24'e dönüldü. Müşteri Geri Bildirimi: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Müşteri ön seriyi onaylamadı. Süreç 24. Adıma (Ön Seri Planlama) geri yönlendirildi.")

        # -------------------------------------------------------------
        # 6. DİĞER SIRADAN ADIMLAR
        # -------------------------------------------------------------
        else:
            adim_kaydi.durum = 'TAMAMLANDI'
            adim_kaydi.karar_sonucu = 'Tamamlandı'
            adim_kaydi.save()

            if adim_no < 34:
                sonraki_adim_no = adim_no + 1
                surec.guncel_adim_no = sonraki_adim_no
                surec.save()
                MuhendislikDegisikligiAdimKaydi.objects.filter(surec=surec, adim__adim_no=sonraki_adim_no).update(durum='DEVAM_EDIYOR')

                MuhendislikDegisikligiGecmisLog.objects.create(
                    surec=surec,
                    islem=f"Adım {adim_no}: {adim_kaydi.adim.baslik} Tamamlandı",
                    detay=f"{notlar or 'İşlem tamamlandı ve sonraki adıma aktarıldı.'} Doküman: {dokuman_ref or '-'}",
                    yapan=tamamlayan
                )
                messages.success(request, f"{adim_no}. Adım tamamlandı. {sonraki_adim_no}. Adıma geçildi.")
            else:
                surec.durum = 'BASARIYLA_TAMAMLANDI'
                surec.save()

                MuhendislikDegisikligiGecmisLog.objects.create(
                    surec=surec,
                    islem="Mühendislik Değişikliği Süreci Başarıyla Tamamlandı",
                    detay=f"34 adımlık mühendislik değişikliği süreci başarıyla tamamlandı. Seri üretime geçiş tamamlandı, reçete kontrolleri yapıldı. Kapanış Notu: {notlar}",
                    yapan=tamamlayan
                )
                messages.success(request, "Tebrikler! Mühendislik Değişikliği (ECO) Süreci başarıyla tamamlandı ve seri üretime alındı.")

    return redirect(f"{redirect('muhendislik_degisikligi_detay', pk=pk).url}#adim-{surec.guncel_adim_no}")


def muhendislik_degisikligi_sil(request, pk):
    surec = get_object_or_404(MuhendislikDegisikligiSureci, pk=pk)
    if request.method == 'POST':
        kod = surec.kod
        surec.delete()
        messages.success(request, f"'{kod}' kodlu Mühendislik Değişikliği Süreci başarıyla silindi.")
    return redirect('muhendislik_degisikligi_liste')


# ==============================================================================
# 7. PROTOTİP SÜRECİ (23 ADIM - PROTOTYPE MANAGEMENT) VIEWS
# ==============================================================================

def prototip_liste(request):
    """
    23 Adımlık Prototip Süreci Ana Listesi ve Filtreleme
    """
    surecler = PrototipSureci.objects.select_related('musteri_karti').all()

    q = request.GET.get('q', '').strip()
    durum_filtre = request.GET.get('durum', '')
    fabrika_filtre = request.GET.get('fabrika', '')
    urun_filtre = request.GET.get('urun_grubu', '')
    tip_filtre = request.GET.get('prototip_tipi', '')

    if q:
        surecler = surecler.filter(
            Q(kod__icontains=q) |
            Q(musteri_adi__icontains=q) |
            Q(ad__icontains=q) |
            Q(parca_kodu__icontains=q)
        )

    if durum_filtre:
        surecler = surecler.filter(durum=durum_filtre)

    if fabrika_filtre:
        surecler = surecler.filter(ilgili_fabrika=fabrika_filtre)

    if urun_filtre:
        surecler = surecler.filter(urun_grubu=urun_filtre)

    if tip_filtre:
        surecler = surecler.filter(prototip_tipi=tip_filtre)

    toplam_surec = PrototipSureci.objects.count()
    aktif_surec = PrototipSureci.objects.filter(durum='DEVAM_EDIYOR').count()
    revizyon_surec = PrototipSureci.objects.filter(durum='REVIZYONDA').count()
    tamamlanan_surec = PrototipSureci.objects.filter(durum='BASARIYLA_TAMAMLANDI').count()

    musteri_kartlari = MusteriKarti.objects.all().order_by('kisa_ad')

    context = {
        'surecler': surecler,
        'toplam_surec': toplam_surec,
        'aktif_surec': aktif_surec,
        'revizyon_surec': revizyon_surec,
        'tamamlanan_surec': tamamlanan_surec,
        'musteri_kartlari': musteri_kartlari,
        'q': q,
        'durum_filtre': durum_filtre,
        'fabrika_filtre': fabrika_filtre,
        'urun_filtre': urun_filtre,
        'tip_filtre': tip_filtre,
    }
    return render(request, 'crm_takip/prototip_liste.html', context)


def prototip_olustur(request):
    """
    Yeni Prototip Süreci Başlatma ve 23 Adımın Otomatik Oluşturulması
    """
    if request.method == 'POST':
        kod = request.POST.get('kod', '').strip()
        ad = request.POST.get('ad', '').strip()
        musteri_adi = request.POST.get('musteri_adi', '').strip()
        parca_kodu = request.POST.get('parca_kodu', '').strip()
        revizyon_no = request.POST.get('revizyon_no', 'Rev.01').strip()
        prototip_tipi = request.POST.get('prototip_tipi', 'YENI_TASARIM')
        urun_grubu = request.POST.get('urun_grubu', 'Metal Parca & Sac')
        ilgili_fabrika = request.POST.get('ilgili_fabrika', 'PRESHANE')
        hedef_tamamlanma_tarihi = request.POST.get('hedef_tamamlanma_tarihi') or None

        sorumlu_proje_sorumlusu = request.POST.get('sorumlu_proje_sorumlusu', 'BUSE NUR BALTACIOĞLU').strip()
        sorumlu_fabrika_muduru = request.POST.get('sorumlu_fabrika_muduru', 'ONUR TUNCER').strip()
        sorumlu_satis_analiz = request.POST.get('sorumlu_satis_analiz', 'METİN YAVAŞ').strip()
        sorumlu_kalite = request.POST.get('sorumlu_kalite', 'MUHARREM FURKAN TARHAN').strip()

        aciklama = request.POST.get('aciklama', '').strip()

        year = timezone.now().year

        if not kod:
            num = 1
            while PrototipSureci.objects.filter(kod=f"PRT-{year}-{num:03d}").exists():
                num += 1
            kod = f"PRT-{year}-{num:03d}"
        else:
            if PrototipSureci.objects.filter(kod=kod).exists():
                base_kod = kod
                suffix = 1
                while PrototipSureci.objects.filter(kod=f"{base_kod}-{suffix:02d}").exists():
                    suffix += 1
                kod = f"{base_kod}-{suffix:02d}"

        musteri_karti = MusteriKarti.objects.filter(
            Q(kisa_ad__icontains=musteri_adi) | Q(ad__icontains=musteri_adi)
        ).first()

        surec = PrototipSureci.objects.create(
            kod=kod,
            ad=ad,
            musteri_adi=musteri_adi,
            musteri_karti=musteri_karti,
            parca_kodu=parca_kodu,
            revizyon_no=revizyon_no,
            prototip_tipi=prototip_tipi,
            urun_grubu=urun_grubu,
            ilgili_fabrika=ilgili_fabrika,
            hedef_tamamlanma_tarihi=hedef_tamamlanma_tarihi,
            sorumlu_proje_sorumlusu=sorumlu_proje_sorumlusu,
            sorumlu_fabrika_muduru=sorumlu_fabrika_muduru,
            sorumlu_satis_analiz=sorumlu_satis_analiz,
            sorumlu_kalite=sorumlu_kalite,
            aciklama=aciklama,
            durum='DEVAM_EDIYOR',
            guncel_adim_no=1
        )

        adim_tanimlari = PrototipAdimTanimi.objects.all().order_by('adim_no')
        for adim in adim_tanimlari:
            durum = 'DEVAM_EDIYOR' if adim.adim_no == 1 else 'BEKLIYOR'
            PrototipAdimKaydi.objects.create(
                surec=surec,
                adim=adim,
                durum=durum
            )

        PrototipGecmisLog.objects.create(
            surec=surec,
            islem=f"Prototip Süreci Başlatıldı: {surec.kod}",
            detay=f"{surec.ad} konulu prototip geliştirme süreci açıldı ve 1. Adım başlatıldı.",
            yapan=sorumlu_proje_sorumlusu
        )

        messages.success(request, f"'{surec.kod}' kodlu Prototip Süreci başarıyla oluşturuldu ve 23 adımlık iş akışı başlatıldı!")
        return redirect('prototip_detay', pk=surec.pk)

    return redirect('prototip_liste')


def prototip_detay(request, pk):
    """
    23 Adımlık Prototip Süreci Detay Sayfası
    """
    surec = get_object_or_404(PrototipSureci, pk=pk)
    adim_kayitlari = surec.adim_kayitlari.select_related('adim').order_by('adim__adim_no')
    tarihce = surec.tarihce_kayitlari.all()[:20]

    faz1_adimlar = [a for a in adim_kayitlari if a.adim.adim_no in range(1, 10)]
    faz2_adimlar = [a for a in adim_kayitlari if a.adim.adim_no in range(10, 15)]
    faz3_adimlar = [a for a in adim_kayitlari if a.adim.adim_no in range(15, 21)]
    faz4_adimlar = [a for a in adim_kayitlari if a.adim.adim_no in range(21, 24)]

    context = {
        'surec': surec,
        'adimlar': adim_kayitlari,
        'faz1_adimlar': faz1_adimlar,
        'faz2_adimlar': faz2_adimlar,
        'faz3_adimlar': faz3_adimlar,
        'faz4_adimlar': faz4_adimlar,
        'tarihce': tarihce,
    }
    return render(request, 'crm_takip/prototip_detay.html', context)


def prototip_adim_aksiyon(request, pk, adim_id):
    """
    23 Adımlık Prototip Süreci Karar ve İlerleme Motoru
    """
    surec = get_object_or_404(PrototipSureci, pk=pk)
    adim_kaydi = get_object_or_404(PrototipAdimKaydi, surec=surec, id=adim_id)
    adim_no = adim_kaydi.adim.adim_no

    if request.method == 'POST':
        aksiyon = request.POST.get('aksiyon')
        tamamlayan = request.POST.get('tamamlayan') or (request.user.get_full_name() if request.user.is_authenticated and request.user.get_full_name() else 'Buse Nur Baltacıoğlu')
        notlar = request.POST.get('notlar', '').strip()
        dokuman_ref = request.POST.get('dokuman_referansi', '').strip()

        adim_kaydi.tamamlayan = tamamlayan
        adim_kaydi.notlar = notlar
        adim_kaydi.dokuman_referansi = dokuman_ref

        # Ara Kaydet / Not ve Doküman Güncelleme
        if aksiyon in ['KAYDET', 'GUNCELLE']:
            if adim_kaydi.durum == 'BEKLIYOR':
                adim_kaydi.durum = 'DEVAM_EDIYOR'
            adim_kaydi.save()

            PrototipGecmisLog.objects.create(
                surec=surec,
                islem=f"Adım {adim_no}: Notlar ve Doküman Kaydedildi",
                detay=f"Not/doküman güncellendi. Doküman: {dokuman_ref or '-'}, Not: {notlar or 'Girilmedi.'}",
                yapan=tamamlayan
            )
            messages.success(request, f"Adım {adim_no} not ve doküman referansı başarıyla kaydedildi.")
            return redirect(f"{redirect('prototip_detay', pk=surec.pk).url}#adim-{adim_no}")

        adim_kaydi.tamamlanma_tarihi = timezone.now()

        # -------------------------------------------------------------
        # 1. ADIM 3: Ön Değerlendirme & Fizibilite Karar Kapısı
        # -------------------------------------------------------------
        if adim_no == 3:
            if aksiyon == 'EVET':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'EVET (Yeni Ürün Devreye Alma Sürecine Aktarıldı)'
                adim_kaydi.save()

                surec.durum = 'YENI_URUN_SURECINE_AKTARILDI'
                surec.save()

                PrototipAdimKaydi.objects.filter(surec=surec, adim__adim_no__gte=4).update(
                    durum='PAS_GECILDI',
                    karar_sonucu='Yeni Ürün Devreye Alma Sürecine Aktarıldığı İçin Muaf Tutuldu'
                )

                PrototipGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 3: Yeni Ürün Sürecine Yönlendirildi",
                    detay=f"Prototip talebi kapsamlı bir NPI süreci gerektirdiğinden 'Yeni Ürün Devreye Alma Süreci'ne aktarıldı. Not: {notlar}",
                    yapan=tamamlayan
                )
                messages.info(request, "Talep boyutu gereği süreç 'Yeni Ürün Devreye Alma Süreci'ne aktarılarak yönlendirildi.")

            elif aksiyon == 'HAYIR':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'HAYIR (Standart Prototip Akışına Devam -> Adım 4)'
                adim_kaydi.save()

                surec.guncel_adim_no = 4
                surec.save()
                PrototipAdimKaydi.objects.filter(surec=surec, adim__adim_no=4).update(durum='DEVAM_EDIYOR')

                PrototipGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 3: Standart Prototip İncelemesi Onaylandı",
                    detay="Prototip imalatı standart prototip süreci kapsamında onaylandı. 4. Adım başlatıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "Ön değerlendirme tamamlandı. 4. Adıma geçildi.")

        # -------------------------------------------------------------
        # 2. ADIM 4: Prototip Niteliği ve Kapsam Sorgusu Karar Kapısı
        # -------------------------------------------------------------
        elif adim_no == 4:
            if aksiyon == 'EVET':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'EVET (Yeni Ürün / Mühendislik Değişikliği Sürecine Aktarıldı)'
                adim_kaydi.save()

                surec.durum = 'YENI_URUN_SURECINE_AKTARILDI'
                surec.save()

                PrototipAdimKaydi.objects.filter(surec=surec, adim__adim_no__gte=5).update(
                    durum='PAS_GECILDI',
                    karar_sonucu='Yeni Ürün / ECO Sürecine Aktarıldığı İçin Muaf Tutuldu'
                )

                PrototipGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 4: NPI / ECO Sürecine Yönlendirildi",
                    detay=f"Müşteri prototipin doğrudan seri üretime / değişikliğe bağlanacağını belirttiğinden ana sürece aktarıldı. Not: {notlar}",
                    yapan=tamamlayan
                )
                messages.info(request, "Müşteri teyidi doğrultusunda süreç ana geliştirme sürecine aktarıldı.")

            elif aksiyon == 'HAYIR':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'HAYIR (Müstakil Prototip İmalatı Olarak Devam -> Adım 5)'
                adim_kaydi.save()

                surec.guncel_adim_no = 5
                surec.save()
                PrototipAdimKaydi.objects.filter(surec=surec, adim__adim_no=5).update(durum='DEVAM_EDIYOR')

                PrototipGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 4: Müstakil Prototip Onayı",
                    detay="Müstakil prototip çalışması olarak devam kararı verildi. Adım 5 (Geçici BOM) başlatıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "Prototip niteliği doğrulandı. 5. Adıma (Geçici BOM) geçildi.")

        # -------------------------------------------------------------
        # 3. ADIM 9: Müşteri Başlangıç Onayı Karar Kapısı
        # -------------------------------------------------------------
        elif adim_no == 9:
            if aksiyon == 'EVET':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'EVET (Müşteri Başlangıç Onayı Verdi)'
                adim_kaydi.save()

                surec.durum = 'DEVAM_EDIYOR'
                surec.guncel_adim_no = 10
                surec.save()
                PrototipAdimKaydi.objects.filter(surec=surec, adim__adim_no=10).update(durum='DEVAM_EDIYOR')

                PrototipGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 9: Müşteri Başlangıç Onayı Alındı",
                    detay="Müşteri prototip maliyet ve şartlarını onayladı. Faz 2 (10. Adım) başlatıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "Müşteri başlangıç onayını verdi! Faz 2 (10. Adım) başlatıldı.")

            elif aksiyon == 'HAYIR':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'HAYIR (Müşteri Başlangıç Onayı Vermedi -> Kapanış Adım 22)'
                adim_kaydi.save()

                PrototipAdimKaydi.objects.filter(surec=surec, adim__adim_no__gte=10, adim__adim_no__lte=21).update(
                    durum='PAS_GECILDI',
                    karar_sonucu='Müşteri Başlangıç Onayı Vermediği İçin Pas Geçildi'
                )

                surec.guncel_adim_no = 22
                surec.durum = 'OLUMSUZ_KAPATILDI'
                surec.save()
                PrototipAdimKaydi.objects.filter(surec=surec, adim__adim_no=22).update(durum='DEVAM_EDIYOR')

                PrototipGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 9: Müşteri Onay Vermedi -> Kapanış",
                    detay=f"Müşteri prototip başlangıç şartlarını onaylamadı. Süreç kapanış için 22. Adıma aktarıldı. Gerekçe: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Müşteri başlangıç onayı vermedi. Süreç kapanış için 22. Adıma aktarıldı.")

        # -------------------------------------------------------------
        # 4. ADIM 18: Numune ISIR Ölçüm Sonuçları Uygun mu?
        # -------------------------------------------------------------
        elif adim_no == 18:
            if aksiyon == 'EVET':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'EVET (ISIR Ölçüm Sonuçları Uygun)'
                adim_kaydi.save()

                surec.durum = 'DEVAM_EDIYOR'
                surec.guncel_adim_no = 19
                surec.save()
                PrototipAdimKaydi.objects.filter(surec=surec, adim__adim_no=19).update(durum='DEVAM_EDIYOR')

                PrototipGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 18: ISIR Kalite Ölçümleri Onaylandı",
                    detay="Üretilen numunelerin ölçümleri teknik şartnameye uygun bulundu. Adım 19 (Müşteriye Sevk) başlatıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "ISIR ölçümleri onaylandı! 19. Adım (Müşteriye Sevk) başlatıldı.")

            elif aksiyon == 'HAYIR':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'HAYIR (Ölçüm Uygunsuzluğu -> Adım 14 BOM/Numune Revizyonuna Dönüş)'
                adim_kaydi.save()

                PrototipAdimKaydi.objects.filter(surec=surec, adim__adim_no__gte=15, adim__adim_no__lte=18).update(durum='BEKLIYOR', karar_sonucu=None)
                surec.guncel_adim_no = 14
                surec.durum = 'REVIZYONDA'
                surec.save()
                PrototipAdimKaydi.objects.filter(surec=surec, adim__adim_no=14).update(durum='DEVAM_EDIYOR')

                PrototipGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 18: ISIR Ölçüm Reddi -> Adım 14'e Dönüş",
                    detay=f"Prototip ölçümleri teknik şartnameye uymadı. Geçici BOM ve numune üretim revizyonu için Adım 14'e dönüldü. Gerekçe: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Numune ölçümleri uygunsuz! Süreç revizyon amacıyla 14. Adıma geri yönlendirildi.")

        # -------------------------------------------------------------
        # 5. ADIM 20: Müşteri Gönderilen Prototip Numuneyi Onayladı mı?
        # -------------------------------------------------------------
        elif adim_no == 20:
            if aksiyon == 'EVET':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'EVET (Müşteri Prototip Numuneyi Onayladı)'
                adim_kaydi.save()

                surec.durum = 'DEVAM_EDIYOR'
                surec.guncel_adim_no = 21
                surec.save()
                PrototipAdimKaydi.objects.filter(surec=surec, adim__adim_no=21).update(durum='DEVAM_EDIYOR')

                PrototipGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 20: Müşteri Prototip Onayı Alındı",
                    detay="Müşteri numune kontrolünü onayladı. Faz 4 (Adım 21 Reçete Kontrolü) başlatıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "Müşteri prototipi onayladı! Faz 4 (21. Adım) başlatıldı.")

            elif aksiyon == 'HAYIR':
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'HAYIR (Müşteri Prototipi Reddetti -> Adım 14)'
                adim_kaydi.save()

                PrototipAdimKaydi.objects.filter(surec=surec, adim__adim_no__gte=15, adim__adim_no__lte=20).update(durum='BEKLIYOR', karar_sonucu=None)
                surec.guncel_adim_no = 14
                surec.durum = 'REVIZYONDA'
                surec.save()
                PrototipAdimKaydi.objects.filter(surec=surec, adim__adim_no=14).update(durum='DEVAM_EDIYOR')

                PrototipGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 20: Müşteri Numune Reddi -> Adım 14'e Dönüş",
                    detay=f"Müşteri prototipi revizyona gönderdi. Yeniden hazırlık için Adım 14'e dönüldü. Müşteri Talebi: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Müşteri prototipi onaylamadı. Süreç 14. Adıma geri yönlendirildi.")

        # -------------------------------------------------------------
        # 6. DİĞER STANDART ADIMLAR
        # -------------------------------------------------------------
        else:
            adim_kaydi.durum = 'TAMAMLANDI'
            adim_kaydi.karar_sonucu = 'Tamamlandı'
            adim_kaydi.save()

            if adim_no < 23:
                sonraki_adim_no = adim_no + 1
                surec.guncel_adim_no = sonraki_adim_no
                surec.save()
                PrototipAdimKaydi.objects.filter(surec=surec, adim__adim_no=sonraki_adim_no).update(durum='DEVAM_EDIYOR')

                PrototipGecmisLog.objects.create(
                    surec=surec,
                    islem=f"Adım {adim_no}: {adim_kaydi.adim.baslik} Tamamlandı",
                    detay=f"{notlar or 'İşlem tamamlandı ve sonraki adıma aktarıldı.'} Doküman: {dokuman_ref or '-'}",
                    yapan=tamamlayan
                )
                messages.success(request, f"{adim_no}. Adım tamamlandı. {sonraki_adim_no}. Adıma geçildi.")
            else:
                surec.durum = 'BASARIYLA_TAMAMLANDI'
                surec.save()

                PrototipGecmisLog.objects.create(
                    surec=surec,
                    islem="Prototip Süreci Başarıyla Tamamlandı",
                    detay=f"23 adımlık prototip süreci başarıyla tamamlandı. Öğrenilmiş dersler arşivlendi. Kapanış Notu: {notlar}",
                    yapan=tamamlayan
                )
                messages.success(request, "Tebrikler! Prototip Süreci başarıyla tamamlandı ve arşivlendi.")

    return redirect(f"{redirect('prototip_detay', pk=pk).url}#adim-{surec.guncel_adim_no}")


def prototip_sil(request, pk):
    surec = get_object_or_404(PrototipSureci, pk=pk)
    if request.method == 'POST':
        kod = surec.kod
        surec.delete()
        messages.success(request, f"'{kod}' kodlu Prototip Süreci başarıyla silindi.")
    return redirect('prototip_liste')


# ==========================================
# 8. ÜRÜN SERİ ÜRETİM SONLANDIRMA SÜRECİ / EOP VIEWS (6 ADIM)
# ==========================================

def eop_listesi_view(request):
    surecler = EOPSureci.objects.all()

    q = request.GET.get('q', '').strip()
    durum_filtre = request.GET.get('durum', '')
    urun_filtre = request.GET.get('urun_grubu', '')

    if q:
        surecler = surecler.filter(
            Q(kod__icontains=q) |
            Q(urun_kodu__icontains=q) |
            Q(urun_adi__icontains=q) |
            Q(musteri_adi__icontains=q)
        )
    if durum_filtre:
        surecler = surecler.filter(durum=durum_filtre)
    if urun_filtre:
        surecler = surecler.filter(urun_grubu=urun_filtre)

    toplam_surec = EOPSureci.objects.count()
    aktif_surec = EOPSureci.objects.filter(durum='DEVAM_EDIYOR').count()
    tasfiye_surec = EOPSureci.objects.filter(durum__in=['STOK_TASFIYESINDE', 'VARLIK_DEVRI_TAMAMLANDI']).count()
    tamamlanan_surec = EOPSureci.objects.filter(durum='BASARIYLA_KAPATILDI').count()

    musteriler = MusteriKarti.objects.all().order_by('kisa_ad')

    context = {
        'surecler': surecler,
        'toplam_surec': toplam_surec,
        'aktif_surec': aktif_surec,
        'tasfiye_surec': tasfiye_surec,
        'tamamlanan_surec': tamamlanan_surec,
        'musteriler': musteriler,
        'q': q,
        'durum_filtre': durum_filtre,
        'urun_filtre': urun_filtre,
    }
    return render(request, 'crm_takip/eop_liste.html', context)


def eop_yeni_view(request):
    if request.method == 'POST':
        kod = request.POST.get('kod', '').strip()
        urun_kodu = request.POST.get('urun_kodu', '').strip()
        urun_adi = request.POST.get('urun_adi', '').strip()
        musteri_adi = request.POST.get('musteri_adi', '').strip()
        musteri_id = request.POST.get('musteri_id')
        urun_grubu = request.POST.get('urun_grubu', 'Kondenser')
        fabrika = request.POST.get('ilgili_fabrika', 'PRESHANE')
        yedek_parca_yil = request.POST.get('yedek_parca_servis_suresi_yil', 10)
        aciklama = request.POST.get('aciklama', '').strip()

        if not kod:
            count = EOPSureci.objects.count() + 1
            kod = f"EOP-2026-{count:03d}"

        musteri_karti = None
        if musteri_id:
            musteri_karti = MusteriKarti.objects.filter(id=musteri_id).first()
            if musteri_karti and not musteri_adi:
                musteri_adi = musteri_karti.kisa_ad

        surec = EOPSureci.objects.create(
            kod=kod,
            urun_kodu=urun_kodu or 'URUN-EOP-001',
            urun_adi=urun_adi or 'EOP Ürün Sonlandırma Projesi',
            musteri_adi=musteri_adi or 'Genel Müşteri',
            musteri_karti=musteri_karti,
            urun_grubu=urun_grubu,
            ilgili_fabrika=fabrika,
            yedek_parca_servis_suresi_yil=int(yedek_parca_yil or 10),
            aciklama=aciklama,
            durum='DEVAM_EDIYOR',
            guncel_adim_no=1
        )

        master_adimlar = EOPSurecAdimTanimi.objects.all().order_by('adim_no')
        for m in master_adimlar:
            EOPAdimKaydi.objects.create(
                surec=surec,
                adim=m,
                durum='DEVAM_EDIYOR' if m.adim_no == 1 else 'BEKLIYOR'
            )

        EOPGecmisLog.objects.create(
            surec=surec,
            islem="EOP Süreci Başlatıldı",
            detay=f"'{surec.kod}' kodlu Ürün Seri Üretim Sonlandırma Süreci sisteme kaydedildi ve 1. Adım aktif edildi.",
            yapan="BUSE NUR BALTACIOĞLU"
        )

        messages.success(request, f"'{surec.kod}' kodlu EOP Süreci başarıyla başlatıldı!")
        return redirect('eop_detay', pk=surec.pk)

    return redirect('eop_listesi')


def eop_detay_view(request, pk):
    surec = get_object_or_404(EOPSureci, pk=pk)
    adim_kayitlari = surec.adim_kayitlari.select_related('adim').order_by('adim__adim_no')

    # Fazlara göre gruplama (Faz 1, Faz 2, Faz 3)
    fazlar = [
        {
            'kod': 'FAZ1',
            'baslik': 'Faz 1: EOP Bildirimi & Talep Analizi (Adım 1-2)',
            'adimlar': [a for a in adim_kayitlari if a.adim.faz == 'FAZ1']
        },
        {
            'kod': 'FAZ2',
            'baslik': 'Faz 2: Stok & Üretim Varlıkları Tasfiyesi (Adım 3-4)',
            'adimlar': [a for a in adim_kayitlari if a.adim.faz == 'FAZ2']
        },
        {
            'kod': 'FAZ3',
            'baslik': 'Faz 3: Sistem Kapatma & Süreç Kapanışı (Adım 5-6)',
            'adimlar': [a for a in adim_kayitlari if a.adim.faz == 'FAZ3']
        },
    ]

    tarihce = surec.tarihce_kayitlari.all().order_by('-tarih')[:15]

    context = {
        'surec': surec,
        'adimlar': adim_kayitlari,
        'fazlar': fazlar,
        'tarihce': tarihce,
        'toplam_adim': 6,
    }
    return render(request, 'crm_takip/eop_detay.html', context)


def eop_adim_tamamla_view(request, pk, adim_no):
    surec = get_object_or_404(EOPSureci, pk=pk)
    adim_kaydi = get_object_or_404(EOPAdimKaydi, surec=surec, adim__adim_no=adim_no)

    if request.method == 'POST':
        tamamlayan = request.POST.get('tamamlayan', 'Buse Nur Baltacıoğlu').strip() or 'Buse Nur Baltacıoğlu'
        notlar = request.POST.get('notlar', '').strip()
        dokuman_ref = request.POST.get('dokuman_referansi', '').strip()
        karar = request.POST.get('karar_sonucu', '').strip() or 'Onaylandı / Mutabakat Sağlandı'

        adim_kaydi.tamamlayan = tamamlayan
        adim_kaydi.notlar = notlar
        adim_kaydi.dokuman_referansi = dokuman_ref
        adim_kaydi.tamamlanma_tarihi = timezone.now()
        adim_kaydi.durum = 'TAMAMLANDI'
        adim_kaydi.karar_sonucu = karar
        adim_kaydi.save()

        if adim_no < 6:
            sonraki_adim_no = adim_no + 1
            surec.guncel_adim_no = sonraki_adim_no

            if adim_no == 2:
                surec.durum = 'STOK_TASFIYESINDE'
            elif adim_no == 4:
                surec.durum = 'VARLIK_DEVRI_TAMAMLANDI'

            surec.save()
            EOPAdimKaydi.objects.filter(surec=surec, adim__adim_no=sonraki_adim_no).update(durum='DEVAM_EDIYOR')

            EOPGecmisLog.objects.create(
                surec=surec,
                islem=f"Adım {adim_no}: {adim_kaydi.adim.baslik} Tamamlandı",
                detay=f"{notlar or 'İşlem tamamlandı ve sonraki adıma aktarıldı.'} Doküman: {dokuman_ref or '-'}",
                yapan=tamamlayan
            )
            messages.success(request, f"{adim_no}. Adım tamamlandı. {sonraki_adim_no}. Adıma geçildi.")
        else:
            surec.durum = 'BASARIYLA_KAPATILDI'
            surec.save()

            EOPGecmisLog.objects.create(
                surec=surec,
                islem="EOP Süreci Başarıyla Tamamlandı & Kapatıldı",
                detay=f"6 adımlık ürün seri üretim sonlandırma süreci başarıyla tamamlandı. Öğrenilmiş dersler arşivlendi. Kapanış Notu: {notlar}",
                yapan=tamamlayan
            )
            messages.success(request, "Tebrikler! Ürün Seri Üretim Sonlandırma (EOP) Süreci başarıyla tamamlandı ve kapatıldı.")

    return redirect(f"{redirect('eop_detay', pk=pk).url}#adim-{surec.guncel_adim_no}")


def eop_sil(request, pk):
    surec = get_object_or_404(EOPSureci, pk=pk)
    if request.method == 'POST':
        kod = surec.kod
        surec.delete()
        messages.success(request, f"'{kod}' kodlu EOP Süreci başarıyla silindi.")
    return redirect('eop_listesi')


import json
from .anket_data import ANKET_RECORDS, CUSTOMER_GROUPS, FACTORIES, DIMENSIONS_META, get_anket_analytics


def anket_musteri_memnuniyeti_view(request):
    """
    Müşteri Memnuniyeti Tek Sayfa Dinamik Yönetim Paneli:
    1. Anket Bağlantısı & Hızlı Kopyalama
    2. Excel İndirme (.xlsx)
    3. Dinamik Müşteri & Fabrika Bazlı Analiz ve Filtreleme
    4. Power BI Tarzı İnteraktif Yönetici Analiz Raporu & Grafikler
    """
    form_url = 'https://forms.gle/KD375wmzhzR9PRGJ8'
    excel_url = 'https://docs.google.com/spreadsheets/d/1cQoc5rn1an-252UE---2qmTUZyMBQ1SIPQKDjiszLd4/export?format=xlsx'

    grup_filtre = request.GET.get('grup', 'ALL')
    fabrika_filtre = request.GET.get('fabrika', 'ALL')

    analytics = get_anket_analytics(grup_filtre, fabrika_filtre)

    context = {
        'analytics': analytics,
        'form_url': form_url,
        'excel_url': excel_url,
        'customer_groups': CUSTOMER_GROUPS,
        'factories': FACTORIES,
        'dimensions_meta': DIMENSIONS_META,
        'anket_records_json': json.dumps(ANKET_RECORDS, ensure_ascii=False),
        'customer_groups_json': json.dumps(CUSTOMER_GROUPS, ensure_ascii=False),
        'factories_json': json.dumps(FACTORIES, ensure_ascii=False),
        'dimensions_meta_json': json.dumps(DIMENSIONS_META, ensure_ascii=False),
        'grup_filtre': grup_filtre,
        'fabrika_filtre': fabrika_filtre,
        'baslik': 'Müşteri Memnuniyeti',
    }
    return render(request, 'crm_takip/anket_musteri_memnuniyeti.html', context)


def anket_raporu_view(request):
    """
    Eski /anketler/rapor/ URL'sini tek sayfa Müşteri Memnuniyeti paneline yönlendirir
    """
    return redirect('anket_musteri_memnuniyeti')


# ==========================================
# 10. ANA SAYFA & YÖNETİCİ ÇALIŞMA ALANI (EXECUTIVE WORKSPACE)
# ==========================================

PERSONEL_LISTESI = [
    {
        'id': 'buse',
        'ad': 'BUSE NUR BALTACIOĞLU',
        'unvan': 'YAZILIM DESTEK PERSONELİ',
        'departman': 'GENEL MÜDÜRLÜK',
        'rol_kodu': 'PAZARLAMA',
        'renk': '#22609d',
        'avatar_text': 'BN',
    },
    {
        'id': 'yigit',
        'ad': 'YİĞİT EFE BİLİR',
        'unvan': 'İŞ ÇÖZÜMLERİ MÜHENDİSİ',
        'departman': 'GENEL MÜDÜRLÜK',
        'rol_kodu': 'SATIS',
        'renk': '#0ea5e9',
        'avatar_text': 'YB',
    },
    {
        'id': 'onur',
        'ad': 'ONUR TUNCER',
        'unvan': 'BİLGİ TEKNOLOJİLERİ MÜDÜRÜ',
        'departman': 'BİLGİ İŞLEM',
        'rol_kodu': 'YONETIM',
        'renk': '#8b5cf6',
        'avatar_text': 'OT',
    },
    {
        'id': 'furkan',
        'ad': 'MUHARREM FURKAN TARHAN',
        'unvan': 'YAZILIM DESTEK SORUMLUSU',
        'departman': 'GENEL MÜDÜRLÜK',
        'rol_kodu': 'ARGE',
        'renk': '#f59e0b',
        'avatar_text': 'FT',
    },
    {
        'id': 'metin',
        'ad': 'METİN YAVAŞ',
        'unvan': 'BAKIM ŞEFİ',
        'departman': 'BAKIM',
        'rol_kodu': 'KALITE',
        'renk': '#10b981',
        'avatar_text': 'MY',
    },
    {
        'id': 'gizem',
        'ad': 'GİZEM ERBAYAT BOĞAN',
        'unvan': 'SİSTEM UZMANI',
        'departman': 'BİLGİ İŞLEM',
        'rol_kodu': 'PLANLAMA',
        'renk': '#ec4899',
        'avatar_text': 'GB',
    },
]


def ana_sayfa_view(request):
    """
    Ana Sayfa - Çift Görünümlü Komuta Merkezi:
    1. Sekme: Ajandam & Faaliyetlerim (Kişisel takvim, seyahat, toplantı, fuar, destek)
    2. Sekme: Proje & İş Akış Takipçisi (Fabrika > Cari > Proje > 8 Süreçlik Uçtan Uca Hat)
    """
    if request.user.is_authenticated and (request.user.first_name or request.user.last_name):
        aktif_kullanici = f"{request.user.first_name} {request.user.last_name}".strip()
    else:
        aktif_kullanici = "Buse Nur Baltacıoğlu"

    # Aktif Ana Sekme (ajanda veya is_akisi)
    tab = request.GET.get('tab', 'ajanda')
    if any(k in request.GET for k in ['fabrika', 'musteri_id', 'proje_id', 'rol']):
        tab = 'is_akisi'

    # -------------------------------------------------------------
    # 1. SEKME: AJANDAM & FAALİYETLERİM VERİLERİ
    # -------------------------------------------------------------
    secili_tur = request.GET.get('tur', '')
    secili_durum = request.GET.get('durum', '')
    secili_gorunum = request.GET.get('view', 'takvim')
    arama_q = request.GET.get('q', '').strip()

    bugun = timezone.now().date()
    try:
        secili_yil = int(request.GET.get('yil', bugun.year))
    except (ValueError, TypeError):
        secili_yil = bugun.year

    try:
        secili_ay = int(request.GET.get('ay', bugun.month))
    except (ValueError, TypeError):
        secili_ay = bugun.month

    faaliyetler = FaaliyetKaydi.objects.filter(sorumlu_kisi=aktif_kullanici).select_related('musteri')

    if secili_tur:
        faaliyetler = faaliyetler.filter(tur=secili_tur)

    if secili_durum:
        faaliyetler = faaliyetler.filter(durum=secili_durum)

    if arama_q:
        faaliyetler = faaliyetler.filter(
            Q(baslik__icontains=arama_q) |
            Q(musteri_adi__icontains=arama_q) |
            Q(lokasyon__icontains=arama_q) |
            Q(aciklama__icontains=arama_q)
        )

    kullanici_tum = FaaliyetKaydi.objects.filter(sorumlu_kisi=aktif_kullanici)
    kategori_sayilari = {
        'toplam': kullanici_tum.count(),
        'seyahat': kullanici_tum.filter(tur='SEYAHAT').count(),
        'toplanti': kullanici_tum.filter(tur='TOPLANTI').count(),
        'fuar': kullanici_tum.filter(tur='FUAR').count(),
        'destek': kullanici_tum.filter(tur='DESTEK').count(),
    }

    cal = calendar.Calendar(firstweekday=0)
    try:
        month_days = cal.monthdatescalendar(secili_yil, secili_ay)
    except Exception:
        secili_yil = bugun.year
        secili_ay = bugun.month
        month_days = cal.monthdatescalendar(secili_yil, secili_ay)

    aylar_tr = [
        "", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
        "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
    ]
    secili_ay_adi = aylar_tr[secili_ay] if 1 <= secili_ay <= 12 else str(secili_ay)

    if secili_ay == 1:
        onceki_ay = 12
        onceki_yil = secili_yil - 1
    else:
        onceki_ay = secili_ay - 1
        onceki_yil = secili_yil

    if secili_ay == 12:
        sonraki_ay = 1
        sonraki_yil = secili_yil + 1
    else:
        sonraki_ay = secili_ay + 1
        sonraki_yil = secili_yil

    secili_gun_str = request.GET.get('gun', '')
    try:
        secili_gun_int = int(secili_gun_str) if secili_gun_str else (bugun.day if secili_yil == bugun.year and secili_ay == bugun.month else 1)
    except (ValueError, TypeError):
        secili_gun_int = 1

    try:
        secili_gun_tarih = datetime.date(secili_yil, secili_ay, secili_gun_int)
    except Exception:
        secili_gun_int = 1
        secili_gun_tarih = datetime.date(secili_yil, secili_ay, 1)

    gun_faaliyetleri = faaliyetler.filter(
        baslangic_tarihi__lte=secili_gun_tarih,
        bitis_tarihi__gte=secili_gun_tarih
    ).order_by('saat_araligi', 'durum')

    aylik_faaliyetler = faaliyetler.filter(
        baslangic_tarihi__year=secili_yil,
        baslangic_tarihi__month=secili_ay
    ).order_by('baslangic_tarihi', 'saat_araligi')

    takvim_haftalari = []
    for week in month_days:
        hafta_gunleri = []
        for day in week:
            is_current_month = (day.month == secili_ay)
            is_today = (day == bugun)
            is_selected = (day == secili_gun_tarih)
            day_faaliyetler = faaliyetler.filter(
                baslangic_tarihi__lte=day,
                bitis_tarihi__gte=day
            )
            hafta_gunleri.append({
                'tarih': day,
                'gun': day.day,
                'is_current_month': is_current_month,
                'is_today': is_today,
                'is_selected': is_selected,
                'faaliyetler': day_faaliyetler,
                'adet': day_faaliyetler.count(),
            })
        takvim_haftalari.append(hafta_gunleri)

    # -------------------------------------------------------------
    # 2. SEKME: PROJE & İŞ AKIŞ TAKİPÇİSİ (UÇTAN UCA 8 SÜREÇ)
    # -------------------------------------------------------------
    fabrika_listesi = [f[0] for f in AnaProje.FABRIKA_CHOICES]
    secili_fabrika = request.GET.get('fabrika', '')
    secili_musteri_id = request.GET.get('musteri_id', '')
    secili_proje_id = request.GET.get('proje_id', '')
    secili_rol = request.GET.get('rol', 'ALL')
    q_proje = request.GET.get('q_proje', '').strip()

    ana_projeler_qs = AnaProje.objects.all().select_related(
        'musteri', 'tesis',
        'musteri_iliskileri_sureci', 'pazarlama_sureci', 'urun_teklif_sureci',
        'sozlesme_sureci', 'prototip_sureci', 'yeni_urun_sureci',
        'muhendislik_degisikligi_sureci', 'eop_sureci'
    ).prefetch_related('prototip_iterasyonlari', 'eco_iterasyonlari').order_by('id')

    if secili_fabrika:
        sf_upper = secili_fabrika.upper()
        if 'PRES' in sf_upper:
            ana_projeler_qs = ana_projeler_qs.filter(
                Q(bolum__icontains='Pres') | Q(fabrika__icontains='PRES')
            )
        elif 'KALIP' in sf_upper:
            ana_projeler_qs = ana_projeler_qs.filter(
                Q(bolum__icontains='Kalıp') | Q(bolum__icontains='Kalip') | Q(fabrika__icontains='KALIP')
            )
        elif 'KONDANSER' in sf_upper:
            ana_projeler_qs = ana_projeler_qs.filter(
                Q(bolum__icontains='Kondanser') | Q(fabrika__icontains='KONDANSER')
            )
        elif 'KABLO' in sf_upper:
            ana_projeler_qs = ana_projeler_qs.filter(
                Q(bolum__icontains='Kablo') | Q(fabrika__icontains='KABLO')
            )
        elif 'CERKEZ' in sf_upper:
            ana_projeler_qs = ana_projeler_qs.filter(
                Q(bolum__icontains='Çerkez') | Q(bolum__icontains='Cerkez') | Q(fabrika__icontains='CERKEZ')
            )
        elif 'MANISA' in sf_upper:
            ana_projeler_qs = ana_projeler_qs.filter(
                Q(bolum__icontains='Manisa') | Q(fabrika__icontains='MANISA')
            )
        else:
            ana_projeler_qs = ana_projeler_qs.filter(
                Q(bolum__icontains=secili_fabrika) | Q(fabrika__icontains=secili_fabrika)
            )

    if secili_musteri_id:
        try:
            ana_projeler_qs = ana_projeler_qs.filter(musteri_id=int(secili_musteri_id))
        except ValueError:
            pass

    if q_proje:
        ana_projeler_qs = ana_projeler_qs.filter(
            Q(proje_kodu__icontains=q_proje) |
            Q(proje_adi__icontains=q_proje) |
            Q(parca_kodu__icontains=q_proje) |
            Q(parca_adi__icontains=q_proje) |
            Q(bolum__icontains=q_proje) |
            Q(musteri__ad__icontains=q_proje) |
            Q(musteri__kisa_ad__icontains=q_proje) |
            Q(aciklama_notu__icontains=q_proje)
        )

    # Seçili Ana Proje
    secili_proje = None
    if secili_proje_id:
        try:
            secili_proje = AnaProje.objects.filter(id=int(secili_proje_id)).first()
        except ValueError:
            secili_proje = None

    if not secili_proje:
        secili_proje = ana_projeler_qs.first() or AnaProje.objects.first()

    # 8 Süreç Listesi
    surecler_listesi = []
    bekleyen_aksiyonlar = []
    prototip_iterasyonlari = []
    eco_revizyonlari = []

    if secili_proje:
        surecler_listesi = secili_proje.get_surecler_listesi()
        if secili_rol and secili_rol != 'ALL':
            for s in surecler_listesi:
                s['rol_eslesiyor'] = (s['rol'].lower() == secili_rol.lower())
        else:
            for s in surecler_listesi:
                s['rol_eslesiyor'] = True

        bekleyen_aksiyonlar = secili_proje.get_bekleyen_aksiyonlar(rol=secili_rol)
        prototip_iterasyonlari = secili_proje.get_prototip_iterasyonlari()
        eco_revizyonlari = secili_proje.get_eco_revizyonlari()

    tum_ana_projeler = AnaProje.objects.all().select_related('musteri').order_by('id')
    musteriler = MusteriKarti.objects.all().order_by('kisa_ad')

    # Portföy Metrikleri (60 Proje Dağılımı)
    toplam_proje_sayisi = AnaProje.objects.count()
    tamamlanan_proje_sayisi = AnaProje.objects.filter(genel_ilerleme_yuzdesi=100).count()
    devam_eden_proje_sayisi = AnaProje.objects.filter(genel_ilerleme_yuzdesi__lt=100).count()
    kaliphane_pres_sayisi = AnaProje.objects.filter(Q(bolum__icontains='Kalıp') | Q(bolum__icontains='Pres')).count()
    kondanser_sayisi = AnaProje.objects.filter(bolum__icontains='Kondanser').count()
    kablo_sayisi = AnaProje.objects.filter(bolum__icontains='Kablo').count()

    # Konsolide Bölüm / Fabrika Listesi
    bolumler_listesi = [
        ('PRESHANE', 'Preshane'),
        ('KALIPHANE', 'Kalıphane'),
        ('KONDANSER', 'Kondanser'),
        ('KABLOGR', 'Kablo Gruplama'),
        ('CERKEZKOY', 'Çerkezköy'),
        ('MANISA ORTAK', 'Manisa Ortak'),
    ]

    # Teleset_Intranet SQL Server Verileri & IncKey
    intranet_sirketler = get_intranet_sirketler()
    proje_liderleri = get_proje_liderleri()
    siradaki_proje_kodu = siradaki_inckey_goruntule('PRJ')

    context = {
        # Sekme kontrolü
        'tab': tab,
        
        # 1. Sekme Ajanda
        'faaliyetler': faaliyetler,
        'aktif_kullanici': aktif_kullanici,
        'kategori_sayilari': kategori_sayilari,
        'secili_tur': secili_tur,
        'secili_durum': secili_durum,
        'secili_gorunum': secili_gorunum,
        'arama_q': arama_q,
        'secili_yil': secili_yil,
        'secili_ay': secili_ay,
        'secili_ay_adi': secili_ay_adi,
        'secili_gun': secili_gun_int,
        'secili_gun_tarih': secili_gun_tarih,
        'gun_faaliyetleri': gun_faaliyetleri,
        'aylik_faaliyetler': aylik_faaliyetler,
        'onceki_ay': onceki_ay,
        'onceki_yil': onceki_yil,
        'sonraki_ay': sonraki_ay,
        'sonraki_yil': sonraki_yil,
        'takvim_haftalari': takvim_haftalari,
        'musteriler': musteriler,
        'bugun': bugun,

        # 2. Sekme Uçtan Uca Proje & İş Akış Takipçisi
        'fabrika_listesi': fabrika_listesi,
        'bolumler_listesi': bolumler_listesi,
        'intranet_sirketler': intranet_sirketler,
        'proje_liderleri': proje_liderleri,
        'siradaki_proje_kodu': siradaki_proje_kodu,
        'secili_fabrika': secili_fabrika,
        'secili_musteri_id': secili_musteri_id,
        'secili_proje_id': secili_proje.id if secili_proje else '',
        'secili_proje': secili_proje,
        'secili_rol': secili_rol,
        'q_proje': q_proje,
        'surecler_listesi': surecler_listesi,
        'tum_ana_projeler': tum_ana_projeler,
        'ana_projeler_qs': ana_projeler_qs,
        'bekleyen_aksiyonlar': bekleyen_aksiyonlar,
        'prototip_iterasyonlari': prototip_iterasyonlari,
        'eco_revizyonlari': eco_revizyonlari,
        'toplam_proje_sayisi': toplam_proje_sayisi,
        'tamamlanan_proje_sayisi': tamamlanan_proje_sayisi,
        'devam_eden_proje_sayisi': devam_eden_proje_sayisi,
        'kaliphane_pres_sayisi': kaliphane_pres_sayisi,
        'kondanser_sayisi': kondanser_sayisi,
        'kablo_sayisi': kablo_sayisi,
    }
    return render(request, 'crm_takip/ana_sayfa.html', context)


def ana_proje_ekle_view(request):
    """
    Yeni Uçtan Uca Ana Proje Oluşturma (IncKey ve Intranet Personel Entegrasyonlu)
    """
    if request.method == 'POST':
        proje_kodu = request.POST.get('proje_kodu', '').strip()
        proje_adi = request.POST.get('proje_adi', '').strip()
        parca_kodu = request.POST.get('parca_kodu', '').strip()
        fabrika = request.POST.get('fabrika', '').strip()
        musteri_id = request.POST.get('musteri_id')
        sorumlu_lider = request.POST.get('sorumlu_lider', 'BUSE NUR BALTACIOĞLU').strip()
        aktif_surec_adi = request.POST.get('aktif_surec_adi', 'Yeni Ürün Devreye Alma Süreci')
        aktif_rol = request.POST.get('aktif_rol', 'Projeci / Kalıp')
        hedef_butce = request.POST.get('hedef_butce', '125000').strip()
        yillik_hacim = request.POST.get('yillik_hacim_adet', '50000').strip()

        if not proje_kodu or 'PRJ' not in proje_kodu:
            proje_kodu = inckey_uret('PRJ')

        musteri = MusteriKarti.objects.filter(id=musteri_id).first() if musteri_id else None

        proje = AnaProje.objects.create(
            proje_kodu=proje_kodu,
            proje_adi=proje_adi,
            parca_kodu=parca_kodu or 'PARCA-001',
            fabrika=fabrika or 'PRESHANE',
            musteri=musteri or MusteriKarti.objects.first(),
            sorumlu_lider=sorumlu_lider,
            aktif_surec_adi=aktif_surec_adi,
            aktif_rol=aktif_rol,
            aktif_surec_no=6,
            hedef_butce=float(hedef_butce) if hedef_butce else 125000.00,
            yillik_hacim_adet=int(yillik_hacim) if yillik_hacim else 50000,
            genel_ilerleme_yuzdesi=75,
        )
        return redirect(f"/?tab=is_akisi&proje_id={proje.id}")

    return redirect("/?tab=is_akisi")


def ana_proje_senkronize_view(request, pk):
    """
    Ana Proje Dijital İplik Veri Senkronizasyonu (Teklif -> APQP & Sözleşme)
    """
    proje = get_object_or_404(AnaProje, pk=pk)
    proje.teklif_verilerini_senkronize_et()
    return redirect(f"/?tab=is_akisi&proje_id={proje.id}&sync=ok")


def ana_proje_iterasyon_ekle_view(request, pk):
    """
    Ana Projeye Yeni Döngüsel İterasyon (ECO Revizyonu veya Prototip Turu) Ekleme
    """
    proje = get_object_or_404(AnaProje, pk=pk)
    if request.method == 'POST':
        iterasyon_tipi = request.POST.get('iterasyon_tipi', 'ECO')
        revizyon_no = request.POST.get('revizyon_no', 'Rev.02')
        aciklama = request.POST.get('aciklama', '')
        
        if iterasyon_tipi == 'ECO':
            eco_count = proje.eco_iterasyonlari.count() + 1
            MuhendislikDegisikligiSureci.objects.create(
                ana_proje=proje,
                kod=f"ECO-{proje.proje_kodu}-{eco_count:02d}",
                ad=f"{proje.proje_adi} - Mühendislik Revizyonu",
                musteri_adi=proje.musteri.ad if proje.musteri else '',
                musteri_karti=proje.musteri,
                parca_kodu=proje.parca_kodu,
                revizyon_no=revizyon_no,
                degisiklik_nedeni='MUSTERI_TALEBI',
                ilgili_fabrika=proje.fabrika,
                sorumlu_proje_sorumlusu=proje.sorumlu_lider,
                aciklama=aciklama or 'Müşteri talebi doğrultusunda başlatılan döngüsel mühendislik değişikliği.',
            )
        elif iterasyon_tipi == 'PROTOTIP':
            prt_count = proje.prototip_iterasyonlari.count() + 1
            PrototipSureci.objects.create(
                ana_proje=proje,
                kod=f"PRT-{proje.proje_kodu}-{prt_count:02d}",
                ad=f"{proje.proje_adi} - Prototip Denemesi",
                musteri_adi=proje.musteri.ad if proje.musteri else '',
                musteri_karti=proje.musteri,
                parca_kodu=proje.parca_kodu,
                revizyon_no=revizyon_no,
                prototip_tipi='PROSES_DENEME',
                ilgili_fabrika=proje.fabrika,
                sorumlu_proje_sorumlusu=proje.sorumlu_lider,
                aciklama=aciklama or 'Kalıp doğrulama ve numune basımı için başlatılan döngüsel prototip iterasyonu.',
            )
    return redirect(f"/?tab=is_akisi&proje_id={proje.id}")


def faaliyet_olustur_view(request):
    """
    Yeni Faaliyet (Seyahat, Toplantı, Fuar, Destek Talebi) Oluşturma
    """
    if request.method == 'POST':
        tur = request.POST.get('tur', 'TOPLANTI')
        baslik = request.POST.get('baslik', '').strip()
        sorumlu_kisi = request.POST.get('sorumlu_kisi', 'Buse Nur Baltacıoğlu')
        musteri_id = request.POST.get('musteri', '')
        musteri_adi = request.POST.get('musteri_adi', '').strip()
        lokasyon = request.POST.get('lokasyon', '').strip()
        baslangic_tarihi_str = request.POST.get('baslangic_tarihi', '')
        bitis_tarihi_str = request.POST.get('bitis_tarihi', '')
        saat_araligi = request.POST.get('saat_araligi', '09:00 - 10:30')
        oncelik = request.POST.get('oncelik', 'ORTA')
        durum = request.POST.get('durum', 'PLANLANDI')
        aciklama = request.POST.get('aciklama', '').strip()
        tahmini_butce_str = request.POST.get('tahmini_butce', '0')

        if not baslik:
            messages.error(request, 'Faaliyet başlığı zorunludur.')
            return redirect(request.META.get('HTTP_REFERER', 'ana_sayfa'))

        musteri_obj = None
        if musteri_id and musteri_id.isdigit():
            musteri_obj = MusteriKarti.objects.filter(pk=int(musteri_id)).first()
            if musteri_obj and not musteri_adi:
                musteri_adi = musteri_obj.kisa_ad or musteri_obj.ad

        baslangic_tarihi = parse_date(baslangic_tarihi_str) if baslangic_tarihi_str else timezone.now().date()
        bitis_tarihi = parse_date(bitis_tarihi_str) if bitis_tarihi_str else baslangic_tarihi

        try:
            tahmini_butce = float(tahmini_butce_str.replace(',', '.')) if tahmini_butce_str else 0.0
        except ValueError:
            tahmini_butce = 0.0

        faaliyet = FaaliyetKaydi.objects.create(
            tur=tur,
            baslik=baslik,
            sorumlu_kisi=sorumlu_kisi,
            musteri=musteri_obj,
            musteri_adi=musteri_adi,
            lokasyon=lokasyon,
            baslangic_tarihi=baslangic_tarihi,
            bitis_tarihi=bitis_tarihi,
            saat_araligi=saat_araligi,
            oncelik=oncelik,
            durum=durum,
            aciklama=aciklama,
            tahmini_butce=tahmini_butce,
            olusturan=sorumlu_kisi
        )

        messages.success(request, f"'{faaliyet.baslik}' faaliyeti başarıyla oluşturuldu.")
        return redirect(request.META.get('HTTP_REFERER', 'ana_sayfa'))

    return redirect('ana_sayfa')


def faaliyet_durum_guncelle_view(request, pk):
    """
    Faaliyet Durumunu Hızlı Güncelleme (Kanban, Takvim veya Liste üzerinden)
    """
    faaliyet = get_object_or_404(FaaliyetKaydi, pk=pk)
    if request.method == 'POST':
        yeni_durum = request.POST.get('durum', '')
        if yeni_durum in dict(FaaliyetKaydi.DURUM_CHOICES):
            faaliyet.durum = yeni_durum
            faaliyet.save()
            messages.success(request, f"'{faaliyet.baslik}' durumu '{faaliyet.get_durum_display()}' olarak güncellendi.")
        else:
            messages.error(request, "Geçersiz durum seçildi.")

    return redirect(request.META.get('HTTP_REFERER', 'ana_sayfa'))


def faaliyet_sil_view(request, pk):
    """
    Faaliyet Kaydını Silme
    """
    faaliyet = get_object_or_404(FaaliyetKaydi, pk=pk)
    if request.method == 'POST':
        baslik = faaliyet.baslik
        faaliyet.delete()
        messages.success(request, f"'{baslik}' faaliyeti başarıyla silindi.")
    return redirect(request.META.get('HTTP_REFERER', 'ana_sayfa'))


# ==============================================================================
# MÜŞTERİ ADAYLARI (LEAD / PROSPECT) & MÜŞTERİ YÖNETİMİ
# ==============================================================================

def musteri_adaylari_liste(request):
    """
    Aday Havuzu - Müşteri Adayları (Leads) Listeleme, Canlı Arama ve Filtreleme
    """
    adaylar = MusteriAdayi.objects.all()

    # Filtre Parametreleri
    q = request.GET.get('q', '').strip()
    durum_filtre = request.GET.get('durum', 'ALL')
    ulke_filtre = request.GET.get('ulke', 'ALL')
    kanal_filtre = request.GET.get('kanal', 'ALL')
    kaynak_filtre = request.GET.get('kaynak', 'ALL')
    oncelik_filtre = request.GET.get('oncelik', 'ALL')

    # Arama Filtresi
    if q:
        adaylar = adaylar.filter(
            Q(ad_soyad__icontains=q) |
            Q(sirket_adi__icontains=q) |
            Q(unvan__icontains=q) |
            Q(eposta__icontains=q) |
            Q(telefon__icontains=q) |
            Q(etiketler__icontains=q) |
            Q(sehir__icontains=q) |
            Q(ulke__icontains=q)
        )

    # Durum Filtresi
    if durum_filtre != 'ALL':
        adaylar = adaylar.filter(durum=durum_filtre)

    # Ülke Filtresi
    if ulke_filtre != 'ALL':
        adaylar = adaylar.filter(ulke=ulke_filtre)

    # Kanal Filtresi
    if kanal_filtre != 'ALL':
        adaylar = adaylar.filter(kanal=kanal_filtre)

    # Kaynak Filtresi
    if kaynak_filtre != 'ALL':
        adaylar = adaylar.filter(kaynak=kaynak_filtre)

    # Öncelik Filtresi
    if oncelik_filtre != 'ALL':
        adaylar = adaylar.filter(oncelik=oncelik_filtre)

    # Metrik Sayaçları
    tum_adaylar = MusteriAdayi.objects.all()
    toplam_aday = tum_adaylar.count()
    yeni_adaylar_sayisi = tum_adaylar.filter(durum='YENI').count()
    iletisimde_sayisi = tum_adaylar.filter(durum='ILETISIMDE').count()
    nitelikli_sayisi = tum_adaylar.filter(durum__in=['NITELIKLI', 'TEKLIF_ASAMASINDA']).count()
    donusturulen_sayisi = tum_adaylar.filter(durum='DONUSTURULDU').count()
    kaybedilen_sayisi = tum_adaylar.filter(durum='KAYBEDILDI').count()
    
    # Aktif Potansiyel Ciro
    aktif_potansiyel_ciro = tum_adaylar.exclude(durum__in=['DONUSTURULDU', 'KAYBEDILDI']).aggregate(
        toplam=Sum('tahmini_potansiyel_ciro')
    )['toplam'] or 0

    # Filtreleme Seçenekleri
    mevcut_ulkeler = sorted(list(set(tum_adaylar.values_list('ulke', flat=True).distinct())))
    mevcut_kaynaklar = sorted(list(set(tum_adaylar.exclude(kaynak__isnull=True).exclude(kaynak__exact='').values_list('kaynak', flat=True).distinct())))

    context = {
        'adaylar': adaylar,
        'toplam_aday': toplam_aday,
        'yeni_adaylar_sayisi': yeni_adaylar_sayisi,
        'iletisimde_sayisi': iletisimde_sayisi,
        'nitelikli_sayisi': nitelikli_sayisi,
        'donusturulen_sayisi': donusturulen_sayisi,
        'kaybedilen_sayisi': kaybedilen_sayisi,
        'aktif_potansiyel_ciro': aktif_potansiyel_ciro,
        'q': q,
        'durum_filtre': durum_filtre,
        'ulke_filtre': ulke_filtre,
        'kanal_filtre': kanal_filtre,
        'kaynak_filtre': kaynak_filtre,
        'oncelik_filtre': oncelik_filtre,
        'mevcut_ulkeler': mevcut_ulkeler,
        'mevcut_kaynaklar': mevcut_kaynaklar,
        'durum_choices': MusteriAdayi.DURUM_CHOICES,
        'kanal_choices': MusteriAdayi.KANAL_CHOICES,
        'oncelik_choices': MusteriAdayi.ONCELIK_CHOICES,
        'sektor_choices': MusteriAdayi.SEKTOR_CHOICES,
    }
    return render(request, 'crm_takip/musteri_adaylari_liste.html', context)


def musteri_adayi_olustur(request):
    """
    Yeni Müşteri Adayı Kaydı Oluşturma (Modal ve Hızlı Form)
    """
    if request.method == 'POST':
        ad_soyad = request.POST.get('ad_soyad', '').strip()
        sirket_adi = request.POST.get('sirket_adi', '').strip()

        if not ad_soyad or not sirket_adi:
            messages.error(request, "Yetkili Adı Soyadı ve Şirket Adı zorunludur.")
            return redirect(request.META.get('HTTP_REFERER', 'musteri_adaylari_liste'))

        unvan = request.POST.get('unvan', '').strip()
        sektor = request.POST.get('sektor', 'Beyaz Eşya')
        ulke = request.POST.get('ulke', 'Almanya').strip()
        sehir = request.POST.get('sehir', '').strip()
        adres = request.POST.get('adres', '').strip()
        eposta = request.POST.get('eposta', '').strip()
        telefon = request.POST.get('telefon', '').strip()
        web_sitesi = request.POST.get('web_sitesi', '').strip()
        kanal = request.POST.get('kanal', 'Pazar Ziyareti')
        kaynak = request.POST.get('kaynak', '').strip()
        durum = request.POST.get('durum', 'YENI')
        oncelik = request.POST.get('oncelik', 'ILIK')
        ilgili_urun_gruplari = request.POST.get('ilgili_urun_gruplari', '').strip()
        etiketler = request.POST.get('etiketler', '').strip()
        atanan_sorumlu = request.POST.get('atanan_sorumlu', 'Buse Nur BALTACIOĞLU').strip()
        aciklama = request.POST.get('aciklama', '').strip()

        # Tahmini Potansiyel Ciro
        tahmini_potansiyel_ciro = None
        ciro_val = request.POST.get('tahmini_potansiyel_ciro', '').strip()
        if ciro_val:
            try:
                tahmini_potansiyel_ciro = float(ciro_val.replace(',', '.'))
            except ValueError:
                tahmini_potansiyel_ciro = None

        adayi = MusteriAdayi.objects.create(
            ad_soyad=ad_soyad,
            unvan=unvan,
            sirket_adi=sirket_adi,
            sektor=sektor,
            ulke=ulke,
            sehir=sehir,
            adres=adres,
            eposta=eposta,
            telefon=telefon,
            web_sitesi=web_sitesi,
            kanal=kanal,
            kaynak=kaynak,
            durum=durum,
            oncelik=oncelik,
            tahmini_potansiyel_ciro=tahmini_potansiyel_ciro,
            ilgili_urun_gruplari=ilgili_urun_gruplari,
            etiketler=etiketler,
            atanan_sorumlu=atanan_sorumlu,
            aciklama=aciklama
        )

        # İlk Kayıt Notu
        MusteriAdayiNotu.objects.create(
            adayi=adayi,
            not_tipi='NOT',
            baslik='Aday Kaydı Oluşturuldu',
            icerik=f"Aday sisteme kaydedildi. Kanal: {kanal}, Kaynak: {kaynak or 'Doğrudan Giriş'}.",
            ekleyen=atanan_sorumlu or 'Buse Nur BALTACIOĞLU'
        )

        messages.success(request, f"'{sirket_adi} - {ad_soyad}' müşteri adayı havuzuna başarıyla eklendi.")
        return redirect('musteri_adayi_detay', pk=adayi.pk)

    return redirect('musteri_adaylari_liste')


def musteri_adayi_detay(request, pk):
    """
    Müşteri Adayı 360° Detay, Aktivite / Zaman Tüneli ve Dönüştürme Merkezi
    """
    adayi = get_object_or_404(MusteriAdayi, pk=pk)
    notlar = adayi.notlar.all().order_by('-tarih', '-id')
    musteri_kartlari = MusteriKarti.objects.all().order_by('kisa_ad')

    # Otomatik Müşteri Kodu Önerisi
    son_kod_sayisi = MusteriKarti.objects.count() + 1
    onerilen_firma_kodu = f"FRM-{son_kod_sayisi:02d}"
    while MusteriKarti.objects.filter(kod=onerilen_firma_kodu).exists():
        son_kod_sayisi += 1
        onerilen_firma_kodu = f"FRM-{son_kod_sayisi:02d}"

    context = {
        'adayi': adayi,
        'notlar': notlar,
        'musteri_kartlari': musteri_kartlari,
        'onerilen_firma_kodu': onerilen_firma_kodu,
        'durum_choices': MusteriAdayi.DURUM_CHOICES,
        'kanal_choices': MusteriAdayi.KANAL_CHOICES,
        'oncelik_choices': MusteriAdayi.ONCELIK_CHOICES,
        'sektor_choices': MusteriAdayi.SEKTOR_CHOICES,
        'not_tipi_choices': MusteriAdayiNotu.NOT_TIPI_CHOICES,
        'tier_choices': MusteriKarti.TIER_CHOICES,
        'strategy_choices': MusteriKarti.STRATEGY_CHOICES,
    }
    return render(request, 'crm_takip/musteri_adayi_detay.html', context)


def musteri_adayi_donustur(request, pk):
    """
    Müşteri Adayını Resmi Müşteri Portföy Kartına (ve İsteğe Bağlı Sürece) Dönüştürme (Lead Conversion)
    """
    adayi = get_object_or_404(MusteriAdayi, pk=pk)
    if request.method == 'POST':
        tier = request.POST.get('tier', 'Tier 2 - Growth')
        strateji = request.POST.get('strateji', 'Start')
        firma_kodu = request.POST.get('firma_kodu', '').strip()
        surec_baslat = request.POST.get('surec_baslat', 'YOK')
        user_name = request.POST.get('user_name', 'Buse Nur BALTACIOĞLU').strip() or 'Buse Nur BALTACIOĞLU'

        # Dönüştürme metodunu çağır
        musteri = adayi.donustur_musteri_kartina(
            tier=tier, 
            strateji=strateji, 
            firma_kodu=firma_kodu or None, 
            user=user_name
        )

        # İsteğe Bağlı Süreç Başlatma
        if surec_baslat == 'URUN_TEKLIF':
            # Yeni Teklif Süreci Aç
            teklif_kodu = inckey_uret('TEK', timezone.now().year)
            teklif = UrunTeklifSureci.objects.create(
                kod=teklif_kodu,
                ad=f"{adayi.sirket_adi} - İlk Teklif Talebi (RFQ)",
                musteri_adi=adayi.sirket_adi,
                musteri_karti=musteri,
                urun_grubu=adayi.ilgili_urun_gruplari or 'Metal Parca & Sac',
                ilgili_fabrika='PRESHANE',
                sorumlu_satis_uzmani=user_name,
                sorumlu_satis_yoneticisi='YİĞİT EFE BİLİR',
                teklif_tutari=adayi.tahmini_potansiyel_ciro or 100000,
                aciklama=f"Müşteri Adayı ({adayi.ad_soyad}) dönüştürülerek otomatik RFQ Teklif Süreci başlatıldı."
            )
            # 1. Adımı aktif yap
            for adim_tanim in UrunTeklifAdimTanimi.objects.all().order_by('sira_no'):
                UrunTeklifAdimKaydi.objects.create(
                    surec=teklif,
                    adim=adim_tanim,
                    durum='DEVAM_EDIYOR' if adim_tanim.sira_no == 1 else 'BEKLIYOR'
                )
            messages.success(request, f"'{adayi.sirket_adi}' portföye aktarıldı ve '{teklif.kod}' Teklif Süreci başlatıldı!")
            return redirect('urun_teklif_detay', pk=teklif.pk)

        elif surec_baslat == 'PAZARLAMA':
            # Yeni Pazarlama Fırsatı Aç
            proje_kodu = inckey_uret('PRJ', timezone.now().year)
            proje = PazarlamaProjesi.objects.create(
                kod=proje_kodu,
                ad=f"{adayi.sirket_adi} - İş Geliştirme ve Pazarlama Fırsatı",
                musteri_adi=adayi.sirket_adi,
                musteri_karti=musteri,
                hedef_ulke=adayi.ulke,
                urun_grubu='Metal Parca & Sac',
                ilgili_fabrika='PRESHANE',
                sorumlu_pazarlama_uzmani=user_name,
                sorumlu_satis_muduru='YİĞİT EFE BİLİR',
                beklenen_ciro=adayi.tahmini_potansiyel_ciro or 500000,
                aciklama=f"Müşteri Adayı ({adayi.ad_soyad}) dönüştürülerek 15 Adımlık Pazarlama Süreci başlatıldı."
            )
            for adim_tanim in SurecAdimTanimi.objects.all().order_by('adim_no'):
                ProjeAdimKaydi.objects.create(
                    proje=proje,
                    adim=adim_tanim,
                    durum='DEVAM_EDIYOR' if adim_tanim.adim_no == 1 else 'BEKLIYOR'
                )
            messages.success(request, f"'{adayi.sirket_adi}' portföye aktarıldı ve '{proje.kod}' Pazarlama Süreci başlatıldı!")
            return redirect('proje_detay', pk=proje.pk)

        messages.success(request, f"'{adayi.sirket_adi}' başarıyla '{musteri.kod}' Müşteri Portföy Kartı olarak oluşturuldu.")
        return redirect('musteri_360_detay', pk=musteri.pk)

    return redirect('musteri_adayi_detay', pk=adayi.pk)


def musteri_adayi_durum_guncelle(request, pk):
    """
    Aday Durumu ve Önceliğini Hızlı Güncelleme
    """
    adayi = get_object_or_404(MusteriAdayi, pk=pk)
    if request.method == 'POST':
        eski_durum = adayi.get_durum_display()
        yeni_durum = request.POST.get('durum', adayi.durum)
        yeni_oncelik = request.POST.get('oncelik', adayi.oncelik)
        not_metni = request.POST.get('not_metni', '').strip()
        user_name = request.POST.get('ekleyen', 'Buse Nur BALTACIOĞLU')

        if yeni_durum in dict(MusteriAdayi.DURUM_CHOICES):
            adayi.durum = yeni_durum
        if yeni_oncelik in dict(MusteriAdayi.ONCELIK_CHOICES):
            adayi.oncelik = yeni_oncelik

        adayi.save()

        # Durum değişikliği aktivite notu
        MusteriAdayiNotu.objects.create(
            adayi=adayi,
            not_tipi='DURUM_DEGISIKLIGI',
            baslik=f"Durum '{adayi.get_durum_display()}' Olarak Güncellendi",
            icerik=f"Önceki Durum: {eski_durum} -> Yeni Durum: {adayi.get_durum_display()}" + (f"\nNot: {not_metni}" if not_metni else ""),
            ekleyen=user_name
        )

        messages.success(request, f"Aday durumu '{adayi.get_durum_display()}' olarak güncellendi.")

    return redirect('musteri_adayi_detay', pk=adayi.pk)


def musteri_adayi_not_ekle(request, pk):
    """
    Müşteri Adayına Etkileşim Notu / Aktivite Ekleme
    """
    adayi = get_object_or_404(MusteriAdayi, pk=pk)
    if request.method == 'POST':
        not_tipi = request.POST.get('not_tipi', 'NOT')
        baslik = request.POST.get('baslik', '').strip()
        icerik = request.POST.get('icerik', '').strip()
        ekleyen = request.POST.get('ekleyen', 'Buse Nur BALTACIOĞLU').strip() or 'Buse Nur BALTACIOĞLU'

        if not baslik:
            baslik = f"{dict(MusteriAdayiNotu.NOT_TIPI_CHOICES).get(not_tipi, 'Aktivite')} Kaydı"

        MusteriAdayiNotu.objects.create(
            adayi=adayi,
            not_tipi=not_tipi,
            baslik=baslik,
            icerik=icerik,
            ekleyen=ekleyen
        )
        messages.success(request, "Aktivite notu başarıyla kaydedildi.")

    return redirect('musteri_adayi_detay', pk=adayi.pk)


def musteri_adayi_sil(request, pk):
    """
    Müşteri Adayı Kaydını Silme
    """
    adayi = get_object_or_404(MusteriAdayi, pk=pk)
    if request.method == 'POST':
        sirket = adayi.sirket_adi
        ad_soyad = adayi.ad_soyad
        adayi.delete()
        messages.success(request, f"'{sirket} - {ad_soyad}' müşteri adayı başarıyla silindi.")
    return redirect('musteri_adaylari_liste')


def musteri_karti_olustur(request):
    """
    Doğrudan Portföye Yeni Kurumsal Müşteri Kartı Ekleme
    """
    if request.method == 'POST':
        ad = request.POST.get('ad', '').strip()
        kisa_ad = request.POST.get('kisa_ad', '').strip()
        ulke = request.POST.get('ulke', 'Almanya').strip()
        sehir = request.POST.get('sehir', '').strip()
        tier = request.POST.get('tier', 'Tier 2 - Growth')
        strateji = request.POST.get('strateji', 'Grow')
        kam_satis_lideri = request.POST.get('kam_satis_lideri', 'Buse Nur BALTACIOĞLU').strip() or 'Buse Nur BALTACIOĞLU'
        aktif_urunler = request.POST.get('aktif_urunler', 'Kondanser, Metal Parça').strip()
        yetkili_kisi = request.POST.get('yetkili_kisi', '').strip()
        yetkili_unvan = request.POST.get('yetkili_unvan', 'Satınalma Yöneticisi').strip()
        yetkili_email = request.POST.get('yetkili_email', '').strip()
        yetkili_telefon = request.POST.get('yetkili_telefon', '').strip()
        notlar = request.POST.get('notlar', '').strip()

        # Otomatik Firma Kodu
        kod = request.POST.get('kod', '').strip()
        if not kod:
            sayi = MusteriKarti.objects.count() + 1
            kod = f"FRM-{sayi:02d}"
            while MusteriKarti.objects.filter(kod=kod).exists():
                sayi += 1
                kod = f"FRM-{sayi:02d}"

        if not kisa_ad and ad:
            kisa_ad = ad.split()[0][:50]

        # Yıllık Ciro
        yillik_ciro = 0
        ciro_str = request.POST.get('yillik_ciro_eur', '').strip()
        if ciro_str:
            try:
                yillik_ciro = float(ciro_str.replace(',', '.'))
            except ValueError:
                yillik_ciro = 0

        musteri = MusteriKarti.objects.create(
            kod=kod,
            ad=ad,
            kisa_ad=kisa_ad,
            ulke=ulke,
            sehir=sehir,
            tier=tier,
            strateji=strateji,
            yillik_ciro_eur=yillik_ciro,
            cuzdan_payi_yuzde=25,
            aktif_proje_sayisi=1,
            kam_satis_lideri=kam_satis_lideri,
            aktif_urunler=aktif_urunler,
            sozlesme_durumu="Yeni Tanımlandı",
            churn_riski="0.05 (Düşük Risk)",
            notlar=notlar
        )

        # Müşteri Tesis / İletişim Kartı Oluştur
        MusteriTesisi.objects.create(
            musteri=musteri,
            sira=1,
            tesis_adi=f"{musteri.kisa_ad} Ana Fabrika",
            lokasyon=f"{sehir}, {ulke}".strip(', '),
            kod=f"{musteri.kisa_ad}-01",
            clv_m=f"{(float(musteri.yillik_ciro_eur or 0) * 3.76) / 1000000.0:.1f} M€",
            churn_skoru="0.05",
            churn_durumu="Düşük Risk",
            yillik_ciro_str=f"€ {float(musteri.yillik_ciro_eur or 0)/1000000.0:.2f}M",
            ciro_alt_bilgi="Aktif Portföy",
            cuzdan_payi_yuzde=25,
            cuzdan_alt_bilgi="Sac & Kablo Grubu",
            destek_sayisi=1,
            npi_proje_sayisi=1,
            teklif_sayisi=1,
            sevkiyat_sayisi=0,
            kam_satis_lideri=kam_satis_lideri,
            yetkili_adi=yetkili_kisi or f"{musteri.kisa_ad} Satınalma Sorumlusu",
            yetkili_unvan=yetkili_unvan,
            yetkili_email=yetkili_email or f"info@{musteri.kisa_ad.lower().replace(' ', '')}.com",
            yetkili_telefon=yetkili_telefon or "",
            son_etkilesim=f"{timezone.now().strftime('%d.%m.%Y')} - Portföy Kartı Oluşturuldu"
        )

        # Başlangıç Zaman Tüneli
        MusteriEtkilesimZamanTuneli.objects.create(
            musteri=musteri,
            kod="FRM-START",
            baslik=f"{musteri.kisa_ad} Müşteri Kartı Portföye Eklendi",
            aciklama=f"{musteri.ad} firması Teleset CRM müşteri portföyüne başarıyla kaydedildi.",
            sorumlu=kam_satis_lideri,
            tarih=timezone.now().date(),
            donem_ay_yil=f"{timezone.now().strftime('%B %Y').upper()} (YENİ MÜŞTERİ)",
            ikon="bi-buildings",
            ikon_bg="bg-primary text-white"
        )

        messages.success(request, f"'{musteri.ad}' ({musteri.kod}) müşteri portföyüne başarıyla eklendi.")
        return redirect('musteri_360_detay', pk=musteri.pk)

    return redirect('kartlar')












