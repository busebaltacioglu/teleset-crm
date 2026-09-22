from .models import SurecAdimTanimi, MusteriAdayi
from .services.intranet_service import (
    get_intranet_sirketler,
    get_proje_liderleri,
    get_pazarlama_uzmanlari,
    get_satis_mudurleri
)

def intranet_context(request):
    try:
        aktif_aday_sayisi = MusteriAdayi.objects.exclude(durum__in=['DONUSTURULDU', 'KAYBEDILDI']).count()
    except Exception:
        aktif_aday_sayisi = 0

    return {
        'intranet_sirketler': get_intranet_sirketler(),
        'proje_liderleri': get_proje_liderleri(),
        'pazarlama_uzmanlari': get_pazarlama_uzmanlari(),
        'satis_mudurleri': get_satis_mudurleri(),
        'pazarlama_master_adimlari': SurecAdimTanimi.objects.all().order_by('adim_no'),
        'sidebar_aktif_aday_sayisi': aktif_aday_sayisi,
    }
