from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    # Ana Sayfa (Executive Workspace & Takvim / Planner / Kanban)
    path('', views.ana_sayfa_view, name='ana_sayfa'),
    path('ana-proje/yeni/', views.ana_proje_ekle_view, name='ana_proje_ekle'),
    path('ana-proje/<int:pk>/senkronize/', views.ana_proje_senkronize_view, name='ana_proje_senkronize'),
    path('ana-proje/<int:pk>/iterasyon-ekle/', views.ana_proje_iterasyon_ekle_view, name='ana_proje_iterasyon_ekle'),
    path('faaliyet/yeni/', views.faaliyet_olustur_view, name='faaliyet_olustur'),
    path('faaliyet/<int:pk>/durum/', views.faaliyet_durum_guncelle_view, name='faaliyet_durum_guncelle'),
    path('faaliyet/<int:pk>/sil/', views.faaliyet_sil_view, name='faaliyet_sil'),

    # Pazarlama Süreci
    path('pazarlama-sureci/', views.dashboard, name='dashboard'),
    path('kartlar/', views.kartlar_view, name='kartlar'),
    path('musteri/<int:pk>/360/', views.musteri_360_view, name='musteri_360_detay'),
    path('kanvaslar/', views.kanvas_listesi, name='kanvas_listesi'),
    path('proje/yeni/', views.proje_olustur, name='proje_olustur'),
    path('proje/<int:pk>/', views.proje_detay, name='proje_detay'),
    path('proje/<int:pk>/adim/<int:adim_no>/aksiyon/', views.adim_aksiyon, name='adim_aksiyon'),
    path('proje/<int:pk>/sil/', views.proje_sil, name='proje_sil'),
    
    # Müşteri İlişkileri Süreci (EYS-EK-028)
    path('musteri-iliskileri/', views.musteri_iliskileri_liste, name='musteri_iliskileri_liste'),
    path('musteri-iliskileri/yeni/', views.musteri_iliskileri_olustur, name='musteri_iliskileri_olustur'),
    path('musteri-iliskileri/<int:pk>/', views.musteri_iliskileri_detay, name='musteri_iliskileri_detay'),
    path('musteri-iliskileri/<int:pk>/adim/<int:adim_id>/aksiyon/', views.musteri_iliskileri_adim_aksiyon, name='musteri_iliskileri_adim_aksiyon'),
    path('musteri-iliskileri/<int:pk>/sil/', views.musteri_iliskileri_sil, name='musteri_iliskileri_sil'),
    
    # Ürün Teklif Süreci (15 Adım)
    path('urun-teklif-sureci/', views.urun_teklif_liste, name='urun_teklif_liste'),
    path('urun-teklif-sureci/yeni/', views.urun_teklif_olustur, name='urun_teklif_olustur'),
    path('urun-teklif-sureci/<int:pk>/', views.urun_teklif_detay, name='urun_teklif_detay'),
    path('urun-teklif-sureci/<int:pk>/adim/<int:adim_id>/aksiyon/', views.urun_teklif_adim_aksiyon, name='urun_teklif_adim_aksiyon'),
    path('urun-teklif-sureci/<int:pk>/sil/', views.urun_teklif_sil, name='urun_teklif_sil'),
    
    # Sözleşmenin Değerlendirilmesi Süreci (15 Adım)
    path('sozlesme-sureci/', views.sozlesme_sureci_liste, name='sozlesme_sureci_liste'),
    path('sozlesme-sureci/yeni/', views.sozlesme_sureci_olustur, name='sozlesme_sureci_olustur'),
    path('sozlesme-sureci/<int:pk>/', views.sozlesme_sureci_detay, name='sozlesme_sureci_detay'),
    path('sozlesme-sureci/<int:pk>/adim/<int:adim_id>/aksiyon/', views.sozlesme_sureci_adim_aksiyon, name='sozlesme_sureci_adim_aksiyon'),
    path('sozlesme-sureci/<int:pk>/sil/', views.sozlesme_sureci_sil, name='sozlesme_sureci_sil'),
    
    # Yeni Ürün Devreye Alma Süreci (45 Adım - APQP / NPI)
    path('yeni-urun-devreye-alma/', views.yeni_urun_liste, name='yeni_urun_liste'),
    path('yeni-urun-devreye-alma/yeni/', views.yeni_urun_olustur, name='yeni_urun_olustur'),
    path('yeni-urun-devreye-alma/<int:pk>/', views.yeni_urun_detay, name='yeni_urun_detay'),
    path('yeni-urun-devreye-alma/<int:pk>/adim/<int:adim_id>/aksiyon/', views.yeni_urun_adim_aksiyon, name='yeni_urun_adim_aksiyon'),
    path('yeni-urun-devreye-alma/<int:pk>/sil/', views.yeni_urun_sil, name='yeni_urun_sil'),

    # Mühendislik Değişikliği Süreci (34 Adım - ECO / ECM)
    path('muhendislik-degisikligi/', views.muhendislik_degisikligi_liste, name='muhendislik_degisikligi_liste'),
    path('muhendislik-degisikligi/yeni/', views.muhendislik_degisikligi_olustur, name='muhendislik_degisikligi_olustur'),
    path('muhendislik-degisikligi/<int:pk>/', views.muhendislik_degisikligi_detay, name='muhendislik_degisikligi_detay'),
    path('muhendislik-degisikligi/<int:pk>/adim/<int:adim_id>/aksiyon/', views.muhendislik_degisikligi_adim_aksiyon, name='muhendislik_degisikligi_adim_aksiyon'),
    path('muhendislik-degisikligi/<int:pk>/sil/', views.muhendislik_degisikligi_sil, name='muhendislik_degisikligi_sil'),
    
    # Prototip Süreci (23 Adım - Prototype Management)
    path('prototip-sureci/', views.prototip_liste, name='prototip_liste'),
    path('prototip-sureci/yeni/', views.prototip_olustur, name='prototip_olustur'),
    path('prototip-sureci/<int:pk>/', views.prototip_detay, name='prototip_detay'),
    path('prototip-sureci/<int:pk>/adim/<int:adim_id>/aksiyon/', views.prototip_adim_aksiyon, name='prototip_adim_aksiyon'),
    path('prototip-sureci/<int:pk>/sil/', views.prototip_sil, name='prototip_sil'),

    # Ürün Seri Üretim Sonlandırma Süreci / EOP (6 Adım - End of Production)
    path('eop-sureci/', views.eop_listesi_view, name='eop_listesi'),
    path('eop-sureci/yeni/', views.eop_yeni_view, name='eop_yeni'),
    path('eop-sureci/<int:pk>/', views.eop_detay_view, name='eop_detay'),
    path('eop-sureci/<int:pk>/adim/<int:adim_no>/tamamla/', views.eop_adim_tamamla_view, name='eop_adim_tamamla'),
    path('eop-sureci/<int:pk>/sil/', views.eop_sil, name='eop_sil'),

    # Anketler & Formlar (Google Forms & Sheets Entegrasyonu)
    path('anketler/musteri-memnuniyeti/', views.anket_musteri_memnuniyeti_view, name='anket_musteri_memnuniyeti'),
    path('anketler/rapor/', views.anket_raporu_view, name='anket_raporu'),
    path('anketler/', RedirectView.as_view(pattern_name='anket_musteri_memnuniyeti', permanent=False)),

    # Eski URL Yönlendirmesi
    path('satis-sureci/', RedirectView.as_view(pattern_name='urun_teklif_liste', permanent=False)),
]
