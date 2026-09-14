from django.contrib import admin
from .models import SurecAdimTanimi, PazarlamaProjesi, ProjeAdimKaydi, ProjeGecmisLog

@admin.register(SurecAdimTanimi)
class SurecAdimTanimiAdmin(admin.ModelAdmin):
    list_display = ('adim_no', 'baslik', 'faz', 'karar_adimi_mi')
    list_filter = ('faz', 'karar_adimi_mi')
    search_fields = ('baslik', 'faaliyet_tanimi', 'sorumlular_raci')
    ordering = ('adim_no',)

class ProjeAdimKaydiInline(admin.TabularInline):
    model = ProjeAdimKaydi
    extra = 0
    fields = ('adim', 'durum', 'karar_sonucu', 'tamamlayan', 'tamamlanma_tarihi')
    readonly_fields = ('adim',)
    can_delete = False

@admin.register(PazarlamaProjesi)
class PazarlamaProjesiAdmin(admin.ModelAdmin):
    list_display = ('kod', 'musteri_adi', 'ad', 'hedef_ulke', 'urun_grubu', 'ilgili_fabrika', 'guncel_adim_no', 'durum', 'olusturma_tarihi')
    list_filter = ('durum', 'urun_grubu', 'ilgili_fabrika', 'guncel_adim_no')
    search_fields = ('kod', 'musteri_adi', 'ad', 'hedef_ulke')
    inlines = [ProjeAdimKaydiInline]

@admin.register(ProjeGecmisLog)
class ProjeGecmisLogAdmin(admin.ModelAdmin):
    list_display = ('proje', 'islem', 'yapan', 'tarih')
    list_filter = ('tarih', 'yapan')
    search_fields = ('proje__kod', 'proje__musteri_adi', 'islem', 'detay')
