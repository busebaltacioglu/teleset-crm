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
    FaaliyetKaydi
)
import calendar
import datetime
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
    1. Müşteri Kartları (Tier 1 KAM, Tier 2 Growth, Tier 3) + 360° Müşteri Profili
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
            Q(kod__icontains=q_musteri)
        )

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
        ilgili_fabrika = request.POST.get('ilgili_fabrika', 'Teleset 1 (Manisa)')
        sorumlu_pazarlama_uzmani = request.POST.get('sorumlu_pazarlama_uzmani', 'Pazarlama Uzmanı').strip()
        sorumlu_satis_muduru = request.POST.get('sorumlu_satis_muduru', 'Satış ve Pazarlama Müdürü').strip()
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
        ilgili_fabrika = request.POST.get('ilgili_fabrika', 'Teleset 1 (Manisa)')
        sorumlu_eys = request.POST.get('sorumlu_eys', 'Buse Nur Baltacıoğlu')
        sorumlu_surec_sahibi = request.POST.get('sorumlu_surec_sahibi', 'Süreç Sahibi / İyileştirme Ekibi')
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
    Ürün Teklif Süreci Listesi & İstatistik Paneli (15 Adım)
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
    }
    return render(request, 'crm_takip/urun_teklif_liste.html', context)


def urun_teklif_olustur(request):
    """
    Yeni Ürün Teklif Süreci Başlatma (15 Standart Adım)
    """
    if request.method == 'POST':
        kod = request.POST.get('kod', '').strip()
        ad = request.POST.get('ad', '').strip()
        musteri_adi = request.POST.get('musteri_adi', '').strip()
        donem = request.POST.get('donem', '2026 Yıllık').strip()
        ilgili_fabrika = request.POST.get('ilgili_fabrika', 'Teleset 1 (Manisa)')
        urun_grubu = request.POST.get('urun_grubu', 'Metal Parca & Sac')
        sorumlu_satis_analiz_uzmani = request.POST.get('sorumlu_satis_analiz_uzmani', 'Satış Analiz Uzmanı')
        sorumlu_satis_uzmani = request.POST.get('sorumlu_satis_uzmani', 'Buse Nur Baltacıoğlu')
        sorumlu_satis_yoneticisi = request.POST.get('sorumlu_satis_yoneticisi', 'Satış Yöneticisi')
        teklif_tutari_val = request.POST.get('teklif_tutari') or request.POST.get('beklenen_ciro')
        aciklama = request.POST.get('aciklama', '').strip()

        year = timezone.now().year

        # Otomatik ve çakışmasız kod üretimi
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

        # İlişkili Müşteri Kartı
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
                guncel_adim_no=1
            )
        except Exception as e:
            messages.error(request, f"Ürün teklif süreci oluşturulurken bir hata oluştu: {str(e)}")
            return redirect('urun_teklif_liste')

        # 15 Standart Adım Kaydının Oluşturulması
        master_adimlar = UrunTeklifAdimTanimi.objects.all().order_by('adim_no')
        for adim in master_adimlar:
            durum = 'DEVAM_EDIYOR' if adim.adim_no == 1 else 'BEKLIYOR'
            dokuman = adim.ilgili_dokumanlar.split(',')[0] if adim.ilgili_dokumanlar else ""
            UrunTeklifAdimKaydi.objects.create(
                surec=surec,
                adim=adim,
                durum=durum,
                dokuman_referansi=dokuman
            )

        # İlk Log Kaydı
        UrunTeklifGecmisLog.objects.create(
            surec=surec,
            islem="Ürün Teklif Süreci Başlatıldı",
            detay=f"15 adımlık standart ürün teklif süreci başlatıldı. Başlangıç Adımı: 1. Fiyat Stratejisinin Oluşturulması. (Dönem: {donem})",
            yapan=sorumlu_satis_uzmani
        )

        messages.success(request, f"'{surec.kod}' kodlu Ürün Teklif Süreci başarıyla başlatıldı.")
        return redirect('urun_teklif_detay', pk=surec.pk)

    return redirect('urun_teklif_liste')


def urun_teklif_detay(request, pk):
    """
    15 Adımlık İnteraktif Ürün Teklif Süreci Takip ve Karar Ekranı
    """
    surec = get_object_or_404(UrunTeklifSureci, pk=pk)
    adim_kayitlari = surec.adim_kayitlari.select_related('adim').order_by('adim__adim_no')

    # Faz grupları (15 Adımlık Akışa Uygun 4 Faz)
    fazlar = [
        {
            'faz_kodu': 'FAZ1',
            'baslik': 'FAZ 1: Fiyat Stratejisi & Yönetim Onayı (Adım 1-3)',
            'adimlar': [k for k in adim_kayitlari if k.adim.faz == 'FAZ1']
        },
        {
            'faz_kodu': 'FAZ2',
            'baslik': 'FAZ 2: RFQ Alımı, Maliyet Analizi & Teklif Değerlendirme (Adım 4-8)',
            'adimlar': [k for k in adim_kayitlari if k.adim.faz == 'FAZ2']
        },
        {
            'faz_kodu': 'FAZ3',
            'baslik': 'FAZ 3: Teklif İletimi, Müşteri Geri Bildirimi & Revizyon (Adım 9-12)',
            'adimlar': [k for k in adim_kayitlari if k.adim.faz == 'FAZ3']
        },
        {
            'faz_kodu': 'FAZ4',
            'baslik': 'FAZ 4: Fiyat Stratejisi Kontrolü, Kapanış & Sürekli İyileştirme (Adım 13-15)',
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
    return render(request, 'crm_takip/urun_teklif_detay.html', context)


def urun_teklif_adim_aksiyon(request, pk, adim_id):
    """
    Ürün Teklif Süreci Adım İlerletme, Karar Kapıları ve İlgili Adıma Geri Dönüş Yönetimi
    """
    surec = get_object_or_404(UrunTeklifSureci, pk=pk)
    adim_kaydi = UrunTeklifAdimKaydi.objects.filter(pk=adim_id, surec=surec).first()
    if not adim_kaydi:
        adim_kaydi = get_object_or_404(UrunTeklifAdimKaydi, adim__adim_no=adim_id, surec=surec)
    
    adim_no = adim_kaydi.adim.adim_no

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
                islem=f"Adım {adim_no}: Notlar Kaydedildi",
                detay=f"Adım açıklama ve değerlendirme notları güncellendi. Not: {notlar or 'Girilmedi.'}",
                yapan=tamamlayan
            )
            messages.success(request, f"Adım {adim_no} not ve değerlendirme bilgileri başarıyla kaydedildi.")
            return redirect(f"{redirect('urun_teklif_detay', pk=surec.pk).url}#adim-{adim_no}")

        now = timezone.now()
        adim_kaydi.tamamlanma_tarihi = now

        # 1. STANDART İLERLEME ADIMLARI (Adım 1, 2, 4, 6, 7, 9, 10, 12, 13, 14)
        if adim_no in [1, 2, 4, 6, 7, 9, 10, 12, 13, 14]:
            adim_kaydi.durum = 'TAMAMLANDI'
            adim_kaydi.karar_sonucu = 'Tamamlandı'
            adim_kaydi.save()

            sonraki_adim_no = adim_no + 1
            surec.guncel_adim_no = sonraki_adim_no
            
            # Özel durum güncellemeleri
            if adim_no == 9:
                surec.durum = 'MUSTERIYE_ILETILDI'
            elif adim_no == 12:
                surec.durum = 'MUSTERIYE_ILETILDI'
            
            surec.save()

            sonraki_adim_kaydi = UrunTeklifAdimKaydi.objects.filter(surec=surec, adim__adim_no=sonraki_adim_no).first()
            if sonraki_adim_kaydi:
                sonraki_adim_kaydi.durum = 'DEVAM_EDIYOR'
                sonraki_adim_kaydi.save()

            UrunTeklifGecmisLog.objects.create(
                surec=surec,
                islem=f"Adım {adim_no} Tamamlandı",
                detay=f"{adim_kaydi.adim.baslik} tamamlandı. {sonraki_adim_no}. Adıma geçildi.",
                yapan=tamamlayan
            )
            messages.success(request, f"Adım {adim_no} başarıyla tamamlandı. Süreç Adım {sonraki_adim_no}'e geçti.")

        # 2. ADIM 3: KARAR KAPISI (Fiyat Stratejisi Üst Yönetim Onayı)
        elif adim_no == 3:
            if aksiyon in ['OK', 'EVET', 'EVET_ONAYLA', 'ONAYLA']:
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'OK (Fiyat Stratejisi Onaylandı -> Adım 4)'
                adim_kaydi.save()

                surec.guncel_adim_no = 4
                surec.save()
                UrunTeklifAdimKaydi.objects.filter(surec=surec, adim__adim_no=4).update(durum='DEVAM_EDIYOR')

                UrunTeklifGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 3: Fiyat Stratejisi Üst Yönetimce Onaylandı (OK)",
                    detay=f"Fiyat stratejisi onaylandı. 4. Adıma (RFQ Alımı) geçildi. Not: {notlar}",
                    yapan=tamamlayan
                )
                messages.success(request, "Fiyat stratejisi üst yönetim tarafından onaylandı! 4. Adıma geçildi.")

            elif aksiyon in ['NOK', 'HAYIR', 'HAYIR_REVIZYON', 'REVIZYON']:
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'NOK (Onaylanmadı -> Adım 2 Bölüm Yöneticileri Paylaşımı)'
                adim_kaydi.save()

                surec.guncel_adim_no = 2
                surec.durum = 'REVIZYONDA'
                surec.save()
                UrunTeklifAdimKaydi.objects.filter(surec=surec, adim__adim_no=2).update(durum='DEVAM_EDIYOR')
                UrunTeklifAdimKaydi.objects.filter(surec=surec, adim__adim_no=3).update(durum='BEKLIYOR', karar_sonucu=None)

                UrunTeklifGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 3: Fiyat Stratejisi Revizyona Gönderildi (NOK -> Adım 2)",
                    detay=f"Fiyat stratejisi üst yönetim tarafından revizyon amacıyla 2. Adıma geri yönlendirildi. Gerekçe: {notlar or 'Yönetim değerlendirmesi doğrultusunda revizyon.'}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Fiyat stratejisi revizyon için 2. Adıma geri yönlendirildi.")

        # 3. ADIM 5: KARAR KAPISI (Satış Koşulları & Parametrelerin Teklif Talebine Uygunluğu)
        elif adim_no == 5:
            if aksiyon in ['OK', 'EVET', 'EVET_UYGUN', 'UYGUN']:
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'OK (Parametreler Uygun -> Adım 6 Detaylı Maliyet Analizi)'
                adim_kaydi.save()

                surec.guncel_adim_no = 6
                surec.save()
                UrunTeklifAdimKaydi.objects.filter(surec=surec, adim__adim_no=6).update(durum='DEVAM_EDIYOR')

                UrunTeklifGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 5: Teklif Parametreleri Uygun Bulundu (OK)",
                    detay="Fiyat ve satış parametreleri RFQ talebine uygun bulundu. 6. Adım (Detaylı Maliyet Analizi) başlatıldı.",
                    yapan=tamamlayan
                )
                messages.success(request, "Teklif parametreleri uygun! 6. Adım Detaylı Maliyet Analizine geçildi.")

            elif aksiyon in ['NOK', 'HAYIR', 'HAYIR_UYGUNSUZ', 'UYGUNSUZ']:
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'NOK (Uygun Değil -> Adım 1 Fiyat Stratejisi)'
                adim_kaydi.save()

                surec.guncel_adim_no = 1
                surec.durum = 'REVIZYONDA'
                surec.save()
                UrunTeklifAdimKaydi.objects.filter(surec=surec, adim__adim_no=1).update(durum='DEVAM_EDIYOR')
                UrunTeklifAdimKaydi.objects.filter(surec=surec, adim__adim_no__in=[2, 3, 4, 5]).update(durum='BEKLIYOR', karar_sonucu=None)

                UrunTeklifGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 5: Parametreler Uygun Bulunmadı (NOK -> Adım 1)",
                    detay=f"Satış koşulları ve parametreler RFQ ile uyuşmadığı için süreç 1. Adıma (Fiyat Stratejisi) geri yönlendirildi. Not: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Parametre uyumsuzluğu sebebiyle süreç 1. Adıma geri yönlendirildi.")

        # 4. ADIM 8: KARAR KAPISI (Teklif Özet Tablosu ve Yönetim Değerlendirmesi)
        elif adim_no == 8:
            if aksiyon in ['OK', 'EVET', 'EVET_ONAYLA', 'ONAYLA']:
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'OK (Maliyet ve Teklif Onaylandı -> Adım 9)'
                adim_kaydi.save()

                surec.guncel_adim_no = 9
                surec.save()
                UrunTeklifAdimKaydi.objects.filter(surec=surec, adim__adim_no=9).update(durum='DEVAM_EDIYOR')

                UrunTeklifGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 8: Teklif Özet Tablosu Yönetimce Onaylandı (OK)",
                    detay="Maliyet kırılımları, karlılık ve ciro hedefleri onaylandı. 9. Adım (Müşteriye İletim) aşamasına geçildi.",
                    yapan=tamamlayan
                )
                messages.success(request, "Maliyet ve teklif tablosu yönetim tarafından onaylandı! 9. Adıma geçildi.")

            elif aksiyon in ['NOK', 'HAYIR', 'HAYIR_REVIZYON', 'REVIZYON']:
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'NOK (Maliyet Revizyonu Gerekli -> Adım 6)'
                adim_kaydi.save()

                surec.guncel_adim_no = 6
                surec.durum = 'REVIZYONDA'
                surec.save()
                UrunTeklifAdimKaydi.objects.filter(surec=surec, adim__adim_no=6).update(durum='DEVAM_EDIYOR')
                UrunTeklifAdimKaydi.objects.filter(surec=surec, adim__adim_no__in=[7, 8]).update(durum='BEKLIYOR', karar_sonucu=None)

                UrunTeklifGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 8: Teklif Maliyet Revizyonuna Gönderildi (NOK -> Adım 6)",
                    detay=f"Maliyet veya karlılık hesaplamaları revizyon için 6. Adıma geri gönderildi. Gerekçe: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Maliyet revizyonu için 6. Adıma geri yönlendirildi.")

        # 5. ADIM 11: KARAR KAPISI (Teklifte Güncelleme Yapılacak mı?)
        elif adim_no == 11:
            if aksiyon in ['EVET', 'EVET_GUNCELLE', 'GUNCELLE']:
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'EVET (Teklifte Güncelleme Yapılacak -> Adım 12)'
                adim_kaydi.save()

                surec.guncel_adim_no = 12
                surec.durum = 'REVIZYONDA'
                surec.save()
                UrunTeklifAdimKaydi.objects.filter(surec=surec, adim__adim_no=12).update(durum='DEVAM_EDIYOR')

                UrunTeklifGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 11: Teklif Güncelleme Kararı Alındı (EVET)",
                    detay=f"Müşteri geri bildirimleri doğrultusunda teklif revizyonu kararlaştırıldı. 12. Adıma (Revize Teklif İletimi) geçildi. Not: {notlar}",
                    yapan=tamamlayan
                )
                messages.info(request, "Teklif güncelleme kararı alındı. Revize teklif için 12. Adıma geçildi.")

            elif aksiyon in ['HAYIR', 'HAYIR_GUNCELLEME_YOK', 'GUNCELLEME_YOK']:
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'HAYIR (Güncelleme Yok -> Doğrudan Adım 13)'
                adim_kaydi.save()

                # 12. Adım pas geçilir, doğrudan 13. Adıma atlanır
                UrunTeklifAdimKaydi.objects.filter(surec=surec, adim__adim_no=12).update(durum='PAS_GECILDI')
                surec.guncel_adim_no = 13
                surec.save()
                UrunTeklifAdimKaydi.objects.filter(surec=surec, adim__adim_no=13).update(durum='DEVAM_EDIYOR')

                UrunTeklifGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 11: Teklif Güncellemesi Yapılmayacak (HAYIR -> Adım 13)",
                    detay="Mevcut teklif korunarak 12. Adım pas geçildi ve 13. Adıma geçildi.",
                    yapan=tamamlayan
                )
                messages.success(request, "Teklif güncellemesi yapılmadan doğrudan 13. Adıma ilerlendi.")

        # 6. ADIM 15: Süreç Kapanışı ve Öğrenilmiş Dersler (Nihai İstasyon)
        elif adim_no == 15:
            adim_kaydi.durum = 'TAMAMLANDI'
            adim_kaydi.karar_sonucu = 'Süreç Başarıyla Tamamlandı & Öğrenilmiş Dersler Paylaşıldı'
            adim_kaydi.save()

            surec.durum = 'BASARIYLA_TAMAMLANDI'
            surec.guncel_adim_no = 15
            surec.save()

            UrunTeklifGecmisLog.objects.create(
                surec=surec,
                islem="Ürün Teklif Süreci Başarıyla Tamamlandı",
                detay=f"15 adımlık ürün teklif süreci başarıyla tamamlandı. Öğrenilmiş dersler modülüne aktarıldı. Kapanış Notu: {notlar}",
                yapan=tamamlayan
            )
            messages.success(request, "Ürün Teklif Süreci başarıyla tamamlandı ve arşivlendi.")

    return redirect(f"{redirect('urun_teklif_detay', pk=surec.pk).url}#adim-{surec.guncel_adim_no}")


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
    }
    return render(request, 'crm_takip/sozlesme_sureci_liste.html', context)


def sozlesme_sureci_olustur(request):
    """
    Yeni Sözleşme Değerlendirme Süreci Başlatma (15 Standart Adım)
    """
    if request.method == 'POST':
        kod = request.POST.get('kod', '').strip()
        ad = request.POST.get('ad', '').strip()
        musteri_adi = request.POST.get('musteri_adi', '').strip()
        sozlesme_tipi = request.POST.get('sozlesme_tipi', 'SATIS')
        donem = request.POST.get('donem', '2026 Yıllık').strip()
        ilgili_fabrika = request.POST.get('ilgili_fabrika', 'Teleset 1 (Manisa)')
        
        baslangic_tarihi = request.POST.get('baslangic_tarihi') or None
        bitis_tarihi = request.POST.get('bitis_tarihi') or None

        sorumlu_satis_uzmani = request.POST.get('sorumlu_satis_uzmani', 'Buse Nur Baltacıoğlu')
        sorumlu_satis_yoneticisi = request.POST.get('sorumlu_satis_yoneticisi', 'Satış Yöneticisi')
        sorumlu_fabrika_muduru = request.POST.get('sorumlu_fabrika_muduru', 'Fabrika Müdürü')
        sorumlu_hukuk = request.POST.get('sorumlu_hukuk', 'Şirket Hukuk Müşaviri')
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

        # 15 Standart Adım Kaydı Oluşturulması
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
            detay=f"15 adımlık standart sözleşme değerlendirme iş akışı başlatıldı. Sözleşme Tipi: {surec.get_sozlesme_tipi_display()}, Fabrika: {ilgili_fabrika}.",
            yapan=sorumlu_satis_uzmani
        )

        messages.success(request, f"'{surec.kod}' kodlu Sözleşme Değerlendirme Süreci başarıyla başlatıldı.")
        return redirect('sozlesme_sureci_detay', pk=surec.pk)

    return redirect('sozlesme_sureci_liste')


def sozlesme_sureci_detay(request, pk):
    """
    15 Adımlık İnteraktif Sözleşme Değerlendirme Süreci Detay ve Karar Ekranı
    """
    surec = get_object_or_404(SozlesmeSureci, pk=pk)
    adim_kayitlari = surec.adim_kayitlari.select_related('adim').order_by('adim__adim_no')

    # Fazlara göre gruplama
    faz_tanimlari = [
        ('FAZ1', 'Faz 1: Sözleşme Kabulü, Hukuki İnceleme & Uygunluk (Adım 1-4)'),
        ('FAZ2', 'Faz 2: Şartlar, Risk Değerlendirmesi & Yönetim Onayı (Adım 5-8)'),
        ('FAZ3', 'Faz 3: Müşteri Bilgilendirmesi, Müzakere & Karşılıklı İmza (Adım 9-12)'),
        ('FAZ4', 'Faz 4: EYS Entegrasyonu, Kapanış & Öğrenilmiş Dersler (Adım 13-15)'),
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

    tarihce = surec.tarihce_kayitlari.all().order_by('-tarih')

    context = {
        'surec': surec,
        'adim_kayitlari': adim_kayitlari,
        'fazlar': fazlar,
        'tarihce': tarihce,
    }
    return render(request, 'crm_takip/sozlesme_sureci_detay.html', context)


def sozlesme_sureci_adim_aksiyon(request, pk, adim_id):
    """
    15 Adımlık Sözleşme Süreci Adım Tamamlama ve Karar Kapısı Aksiyon Motoru
    """
    surec = get_object_or_404(SozlesmeSureci, pk=pk)
    adim_kaydi = get_object_or_404(SozlesmeAdimKaydi, pk=adim_id, surec=surec)
    adim_no = adim_kaydi.adim.adim_no

    if request.method == 'POST':
        aksiyon = request.POST.get('aksiyon', 'TAMAMLA')
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
            messages.success(request, f"Adım {adim_no} not ve değerlendirme bilgileri başarıyla kaydedildi.")
            return redirect(f"{redirect('sozlesme_sureci_detay', pk=surec.pk).url}#adim-{adim_no}")

        now = timezone.now()
        adim_kaydi.tamamlanma_tarihi = now

        # 1. STANDART İLERLEME ADIMLARI (Adım 1, 2, 3, 5, 6, 9, 11, 12, 13, 14)
        if adim_no in [1, 2, 3, 5, 6, 9, 11, 12, 13, 14]:
            adim_kaydi.durum = 'TAMAMLANDI'
            adim_kaydi.karar_sonucu = 'Tamamlandı'
            adim_kaydi.save()

            sonraki_adim_no = adim_no + 1
            surec.guncel_adim_no = sonraki_adim_no

            if adim_no == 3:
                surec.durum = 'HUKUKI_INCELEMEDE'
            elif adim_no == 9:
                surec.durum = 'MUSTERI_MUZAKERESINDE'
            elif adim_no == 11:
                surec.durum = 'DEVAM_EDIYOR'

            surec.save()

            sonraki_adim_kaydi = SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no=sonraki_adim_no).first()
            if sonraki_adim_kaydi:
                sonraki_adim_kaydi.durum = 'DEVAM_EDIYOR'
                sonraki_adim_kaydi.save()

            SozlesmeGecmisLog.objects.create(
                surec=surec,
                islem=f"Adım {adim_no} Tamamlandı",
                detay=f"{adim_kaydi.adim.baslik} tamamlandı. {sonraki_adim_no}. Adıma geçildi.",
                yapan=tamamlayan
            )
            messages.success(request, f"Adım {adim_no} başarıyla tamamlandı. Süreç Adım {sonraki_adim_no}'e geçti.")

        # 2. ADIM 4: KARAR KAPISI (Hukuki Görüş ve Sözleşme Uygunluğu)
        elif adim_no == 4:
            if aksiyon in ['OK', 'EVET', 'UYGUN', 'ONAYLA']:
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'OK (Sözleşme Hukuki Olarak Uygun -> Adım 5)'
                adim_kaydi.save()

                surec.guncel_adim_no = 5
                surec.save()
                SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no=5).update(durum='DEVAM_EDIYOR')

                SozlesmeGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 4: Sözleşme Hukuki Olarak Uygun Bulundu (OK)",
                    detay=f"Sözleşme mevzuat ve şartlar açısından uygun bulundu. 5. Adıma geçildi. Not: {notlar}",
                    yapan=tamamlayan
                )
                messages.success(request, "Sözleşme hukuki olarak uygun bulundu! 5. Adıma geçildi.")

            elif aksiyon in ['NOK', 'HAYIR', 'UYGUNSUZ', 'MUZAKERE']:
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'NOK (Uygunsuzluk / Riskli Maddeler -> Doğrudan Adım 9 Müşteri Bilgilendirmesi)'
                adim_kaydi.save()

                # 5, 6, 7, 8 adımlar pas geçilip doğrudan 9. adıma yönlendirilir
                SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no__in=[5, 6, 7, 8]).update(durum='PAS_GECILDI')
                surec.guncel_adim_no = 9
                surec.durum = 'MUSTERI_MUZAKERESINDE'
                surec.save()
                SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no=9).update(durum='DEVAM_EDIYOR')

                SozlesmeGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 4: Hukuki Uygunsuzluk Sebebiyle Müşteri Müzakeresine Yönlendirildi (NOK -> Adım 9)",
                    detay=f"Sözleşme maddelerinde hukuki çekince veya uygunsuzluk tespit edildi. Müzakere için doğrudan 9. Adıma aktarıldı. Gerekçe: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Hukuki çekinceler nedeniyle süreç doğrudan 9. Adıma (Müşteri Bilgilendirme) aktarıldı.")

        # 3. ADIM 7: KARAR KAPISI (Risk Değerlendirmesi Sonucu Görüş & Öneriler)
        elif adim_no == 7:
            if aksiyon in ['OK', 'EVET', 'UYGUN', 'ONAYLA']:
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'OK (Risk Değerlendirmesi Uygun -> Adım 8 Üst Yönetim Onayı)'
                adim_kaydi.save()

                surec.guncel_adim_no = 8
                surec.durum = 'YONETIM_ONAYINDA'
                surec.save()
                SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no=8).update(durum='DEVAM_EDIYOR')

                SozlesmeGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 7: Risk Değerlendirmesi Mutabakatı Sağlandı (OK)",
                    detay="Risk puanları kabul edilebilir seviyede bulundu. 8. Adım (Üst Yönetim Onayı) aşamasına geçildi.",
                    yapan=tamamlayan
                )
                messages.success(request, "Risk değerlendirmesi onaylandı! 8. Adım Üst Yönetim Onayına geçildi.")

            elif aksiyon in ['NOK', 'HAYIR', 'RISKLI', 'MUZAKERE']:
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'NOK (Yüksek Riskli Maddeler -> Doğrudan Adım 9 Müşteri Bilgilendirmesi)'
                adim_kaydi.save()

                SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no=8).update(durum='PAS_GECILDI')
                surec.guncel_adim_no = 9
                surec.durum = 'MUSTERI_MUZAKERESINDE'
                surec.save()
                SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no=9).update(durum='DEVAM_EDIYOR')

                SozlesmeGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 7: Yüksek Risk Nedeniyle Müşteri Bilgilendirmesine Yönlendirildi (NOK -> Adım 9)",
                    detay=f"Bölüm değerlendirmelerinde kritik riskli maddeler belirlendi. 9. Adıma aktarıldı. Not: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Kritik riskli maddeler nedeniyle süreç 9. Adıma (Müşteri Bilgilendirme) aktarıldı.")

        # 4. ADIM 8: KARAR KAPISI (Üst Yönetim Onayı)
        elif adim_no == 8:
            if aksiyon in ['OK', 'EVET', 'ONAYLA', 'DOGRUDAN_ONAY']:
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'OK (Yönetimce Doğrudan Onaylandı -> Adım 11 İmzalanma)'
                adim_kaydi.save()

                # Adım 9 ve 10 pas geçilerek doğrudan Adım 11'e atlanır
                SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no__in=[9, 10]).update(durum='PAS_GECILDI')
                surec.guncel_adim_no = 11
                surec.save()
                SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no=11).update(durum='DEVAM_EDIYOR')

                SozlesmeGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 8: Sözleşme Üst Yönetimce Onaylandı (OK -> Adım 11)",
                    detay="Üst yönetim sözleşmeyi doğrudan onayladı. 9 ve 10. adımlar pas geçilerek 11. Adıma (İmzalanma) geçildi.",
                    yapan=tamamlayan
                )
                messages.success(request, "Sözleşme üst yönetim tarafından onaylandı! Doğrudan 11. Adım İmzalanma aşamasına geçildi.")

            elif aksiyon in ['NOK', 'HAYIR', 'MUZAKERE_ISTENDI', 'MUZAKERE']:
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'NOK (Yönetim Revizyon / Müzakere İstedi -> Adım 9)'
                adim_kaydi.save()

                surec.guncel_adim_no = 9
                surec.durum = 'MUSTERI_MUZAKERESINDE'
                surec.save()
                SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no=9).update(durum='DEVAM_EDIYOR')

                SozlesmeGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 8: Yönetim Müzakere Talep Etti (NOK -> Adım 9)",
                    detay=f"Yönetim bazı sözleşme koşullarının müşteriyle müzakere edilmesini istedi. Gerekçe: {notlar}",
                    yapan=tamamlayan
                )
                messages.warning(request, "Yönetim değerlendirmesi doğrultusunda müşteri müzakeresi için 9. Adıma geçildi.")

        # 5. ADIM 10: KARAR KAPISI (Müşteri İle Müzakere Mutabakatı)
        elif adim_no == 10:
            if aksiyon in ['OK', 'EVET', 'MUTABAKAT_SAGLANDI', 'MUTABIK']:
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'OK (Müşteriyle Mutabakat Sağlandı -> Adım 11 İmzalanma)'
                adim_kaydi.save()

                surec.guncel_adim_no = 11
                surec.durum = 'DEVAM_EDIYOR'
                surec.save()
                SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no=11).update(durum='DEVAM_EDIYOR')

                SozlesmeGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 10: Müşteri İle Müzakere Mutabakatı Sağlandı (OK)",
                    detay=f"Müşteri ile revize maddeler üzerinde tam mutabakata varıldı. 11. Adıma (İmzalanma) geçildi. Not: {notlar}",
                    yapan=tamamlayan
                )
                messages.success(request, "Müşteri ile mutabakat sağlandı! 11. Adım İmzalanma aşamasına geçildi.")

            elif aksiyon in ['NOK', 'HAYIR', 'MUTABAKAT_YOK', 'IPTAL']:
                adim_kaydi.durum = 'TAMAMLANDI'
                adim_kaydi.karar_sonucu = 'NOK (Mutabakat Sağlanamadı -> Adım 14 Kapanış)'
                adim_kaydi.save()

                # Adım 11, 12, 13 pas geçilip doğrudan Adım 14'e gidilir
                SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no__in=[11, 12, 13]).update(durum='PAS_GECILDI')
                surec.guncel_adim_no = 14
                surec.durum = 'OLUMSUZ_KAPATILDI'
                surec.save()
                SozlesmeAdimKaydi.objects.filter(surec=surec, adim__adim_no=14).update(durum='DEVAM_EDIYOR')

                SozlesmeGecmisLog.objects.create(
                    surec=surec,
                    islem="Adım 10: Müzakere Sonucu Mutabakat Sağlanamadı (NOK -> Adım 14)",
                    detay=f"Müşteri ile kritik maddelerde uzlaşılamadı. Süreç olumsuz olarak 14. Adıma (Kapanış) aktarıldı. Gerekçe: {notlar}",
                    yapan=tamamlayan
                )
                messages.error(request, "Mutabakat sağlanamadığı için süreç olumsuz kapanış amacıyla 14. Adıma aktarıldı.")

        # 6. ADIM 15: Süreç Kapanışı ve Öğrenilmiş Dersler (Nihai İstasyon)
        elif adim_no == 15:
            adim_kaydi.durum = 'TAMAMLANDI'
            adim_kaydi.karar_sonucu = 'Sözleşme Süreci Başarıyla Tamamlandı & Öğrenilmiş Dersler Kaydedildi'
            adim_kaydi.save()

            if surec.durum != 'OLUMSUZ_KAPATILDI':
                surec.durum = 'BASARIYLA_TAMAMLANDI'
            surec.guncel_adim_no = 15
            surec.save()

            SozlesmeGecmisLog.objects.create(
                surec=surec,
                islem="Sözleşme Değerlendirme Süreci Başarıyla Tamamlandı",
                detay=f"15 adımlık sözleşme değerlendirme süreci tamamlandı. Öğrenilmiş dersler modülüne aktarıldı. Kapanış Notu: {notlar}",
                yapan=tamamlayan
            )
            messages.success(request, "Sözleşme Değerlendirme Süreci başarıyla tamamlandı ve arşivlendi.")

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
        ilgili_fabrika = request.POST.get('ilgili_fabrika', 'Teleset 1 (Manisa)')
        parca_kodu = request.POST.get('parca_kodu', '').strip()
        hedef_seri_uretim_tarihi = request.POST.get('hedef_seri_uretim_tarihi') or None
        yillik_hedef_adet = request.POST.get('yillik_hedef_adet') or None
        
        sorumlu_proje_lideri = request.POST.get('sorumlu_proje_lideri', 'Proje Sorumlusu')
        sorumlu_fabrika_muduru = request.POST.get('sorumlu_fabrika_muduru', 'Fabrika Müdürü')
        sorumlu_satis_analiz = request.POST.get('sorumlu_satis_analiz', 'Satış-Analiz Sorumlusu')
        sorumlu_kalite = request.POST.get('sorumlu_kalite', 'Kalite Sorumlusu')
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
        ilgili_fabrika = request.POST.get('ilgili_fabrika', 'Teleset 1 (Manisa)')
        hedef_tamamlanma_tarihi = request.POST.get('hedef_tamamlanma_tarihi') or None

        sorumlu_proje_sorumlusu = request.POST.get('sorumlu_proje_sorumlusu', 'Buse Nur Baltacıoğlu').strip()
        sorumlu_fabrika_muduru = request.POST.get('sorumlu_fabrika_muduru', 'Serdar Acar').strip()
        sorumlu_satis_analiz = request.POST.get('sorumlu_satis_analiz', 'Hakan Yılmaz').strip()
        sorumlu_kalite = request.POST.get('sorumlu_kalite', 'Ahmet Yurt').strip()

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
        ilgili_fabrika = request.POST.get('ilgili_fabrika', 'Teleset 1 (Manisa)')
        hedef_tamamlanma_tarihi = request.POST.get('hedef_tamamlanma_tarihi') or None

        sorumlu_proje_sorumlusu = request.POST.get('sorumlu_proje_sorumlusu', 'Buse Nur Baltacıoğlu').strip()
        sorumlu_fabrika_muduru = request.POST.get('sorumlu_fabrika_muduru', 'Serdar Acar').strip()
        sorumlu_satis_analiz = request.POST.get('sorumlu_satis_analiz', 'Hakan Yılmaz').strip()
        sorumlu_kalite = request.POST.get('sorumlu_kalite', 'Ahmet Yurt').strip()

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
        fabrika = request.POST.get('ilgili_fabrika', 'Teleset 1 (Manisa)')
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
            yapan="Buse Nur Baltacıoğlu"
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
        'ad': 'Buse Nur Baltacıoğlu',
        'unvan': 'Pazarlama & İş Geliştirme Yöneticisi',
        'rol_kodu': 'PAZARLAMA',
        'renk': '#22609d',
        'avatar_text': 'BN',
    },
    {
        'id': 'ahmet',
        'ad': 'Ahmet Yılmaz',
        'unvan': 'Satış & Teklif Yöneticisi',
        'rol_kodu': 'SATIS',
        'renk': '#0ea5e9',
        'avatar_text': 'AY',
    },
    {
        'id': 'canan',
        'ad': 'Canan Kaya',
        'unvan': 'Yeni Ürün & Ar-Ge Mühendisi',
        'rol_kodu': 'ARGE',
        'renk': '#8b5cf6',
        'avatar_text': 'CK',
    },
    {
        'id': 'mehmet',
        'ad': 'Mehmet Demir',
        'unvan': 'Mühendislik & Kalite Yöneticisi',
        'rol_kodu': 'KALITE',
        'renk': '#10b981',
        'avatar_text': 'MD',
    },
]


def ana_sayfa_view(request):
    """
    Kullanıcı Kişisel Çalışma Alanı & Ajandası
    (Herkes yalnızca kendi seyahat, toplantı, fuar ve destek taleplerini görür;
     Ajanda & Takvim ve Liste görünümleri)
    """
    if request.user.is_authenticated and (request.user.first_name or request.user.last_name):
        aktif_kullanici = f"{request.user.first_name} {request.user.last_name}".strip()
    else:
        aktif_kullanici = "Buse Nur Baltacıoğlu"

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

    # Kullanıcının yalnızca kendi faaliyetleri
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

    # Kategori Sayaçları (Kullanıcının kendi faaliyetleri üzerinden)
    kullanici_tum = FaaliyetKaydi.objects.filter(sorumlu_kisi=aktif_kullanici)
    kategori_sayilari = {
        'toplam': kullanici_tum.count(),
        'seyahat': kullanici_tum.filter(tur='SEYAHAT').count(),
        'toplanti': kullanici_tum.filter(tur='TOPLANTI').count(),
        'fuar': kullanici_tum.filter(tur='FUAR').count(),
        'destek': kullanici_tum.filter(tur='DESTEK').count(),
    }

    # Takvim Verisi Üretimi (Ayın Günleri ve Faaliyetler)
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

    # Gün Seçimi
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

    # Seçili günün faaliyetleri
    gun_faaliyetleri = faaliyetler.filter(
        baslangic_tarihi__lte=secili_gun_tarih,
        bitis_tarihi__gte=secili_gun_tarih
    ).order_by('saat_araligi', 'durum')

    # Seçili ayın tüm faaliyetleri
    aylik_faaliyetler = faaliyetler.filter(
        baslangic_tarihi__year=secili_yil,
        baslangic_tarihi__month=secili_ay
    ).order_by('baslangic_tarihi', 'saat_araligi')

    # Takvim Izgarası
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

    musteriler = MusteriKarti.objects.all().order_by('kisa_ad')

    context = {
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
        'baslik': 'Kişisel Çalışma Alanı & Ajandam',
    }
    return render(request, 'crm_takip/ana_sayfa.html', context)


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











