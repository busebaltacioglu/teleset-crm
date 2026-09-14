import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "teleset_crm_core.settings")
django.setup()

from crm_takip.models import PazarlamaProjesi, SurecAdimTanimi, ProjeAdimKaydi, ProjeGecmisLog

# Örnek Proje 1: BMW EV Batarya Muhafazası (7. Adımda Aktif)
p1, created = PazarlamaProjesi.objects.get_or_create(
    kod="PRJ-2026-001",
    defaults={
        "ad": "Almanya EV Batarya Muhafazası Projesi",
        "musteri_adi": "BMW AG",
        "hedef_ulke": "Almanya",
        "urun_grubu": "Batarya & EV Bilesenleri",
        "ilgili_fabrika": "Teleset 1 (Manisa)",
        "sorumlu_pazarlama_uzmani": "Pazarlama Uzmanı",
        "sorumlu_satis_muduru": "Satış ve Pazarlama Müdürü",
        "durum": "DEVAM_EDIYOR",
        "guncel_adim_no": 7,
        "tahmini_butce": 35000,
        "beklenen_ciro": 2400000,
        "aciklama": "BMW Leipzig tesisi için batarya taşıyıcı şasi sac parçaları pazarlama girişimi."
    }
)

if created:
    for adim in SurecAdimTanimi.objects.all():
        if adim.adim_no < 7:
            durum = "TAMAMLANDI"
            karar = "Onaylandı / Tamamlandı"
        elif adim.adim_no == 7:
            durum = "DEVAM_EDIYOR"
            karar = None
        else:
            durum = "BEKLIYOR"
            karar = None
        
        ProjeAdimKaydi.objects.create(
            proje=p1,
            adim=adim,
            durum=durum,
            karar_sonucu=karar,
            tamamlayan="Pazarlama Uzmanı" if adim.adim_no < 7 else None
        )
    
    ProjeGecmisLog.objects.create(proje=p1, islem="Pazarlama Süreci Başlatıldı", detay="Proje açıldı.", yapan="Sistem")
    ProjeGecmisLog.objects.create(proje=p1, islem="Adım 6: Bütçe Onaylandı", detay="Genel Müdür bütçe planını onayladı. 7. Adıma geçildi.", yapan="Genel Müdür")

# Örnek Proje 2: Stellantis Gövde Sac Parçaları (Doğrudan Teklif Sürecine Aktarılmış)
p2, created2 = PazarlamaProjesi.objects.get_or_create(
    kod="PRJ-2026-002",
    defaults={
        "ad": "Fransa Yeni Platform Gövde Parçaları",
        "musteri_adi": "Stellantis Group",
        "hedef_ulke": "Fransa",
        "urun_grubu": "Sac Sekillendirme",
        "ilgili_fabrika": "Teleset Otomotiv",
        "sorumlu_pazarlama_uzmani": "Pazarlama Uzmanı",
        "sorumlu_satis_muduru": "Satış ve Pazarlama Müdürü",
        "durum": "TEKLIF_SURECINDE",
        "guncel_adim_no": 12,
        "tahmini_butce": 15000,
        "beklenen_ciro": 4500000,
        "aciklama": "Geçerli tedarikçi onayı bulunduğu için 12. adımda doğrudan Ürün Teklif Sürecine aktarıldı."
    }
)

if created2:
    for adim in SurecAdimTanimi.objects.all():
        if adim.adim_no <= 12:
            durum = "TAMAMLANDI"
            karar = "Geçerli Onay Var -> Teklif Süreci" if adim.adim_no == 12 else "Tamamlandı"
        else:
            durum = "PAS_GECILDI"
            karar = "Pas Geçildi"
        
        ProjeAdimKaydi.objects.create(
            proje=p2,
            adim=adim,
            durum=durum,
            karar_sonucu=karar,
            tamamlayan="Satış ve Pazarlama Müdürü"
        )
    ProjeGecmisLog.objects.create(proje=p2, islem=" Ürün Teklif Sürecine Aktarıldı", detay="Geçerli denetim onayı ile RFQ sürecine geçildi.", yapan="Satış ve Pazarlama Müdürü")

print("Örnek demo veriler başarıyla oluşturuldu!")
