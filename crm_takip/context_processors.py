from .services.intranet_service import (
    get_intranet_sirketler,
    get_proje_liderleri,
    get_pazarlama_uzmanlari,
    get_satis_mudurleri
)

def intranet_context(request):
    return {
        'intranet_sirketler': get_intranet_sirketler(),
        'proje_liderleri': get_proje_liderleri(),
        'pazarlama_uzmanlari': get_pazarlama_uzmanlari(),
        'satis_mudurleri': get_satis_mudurleri(),
    }
