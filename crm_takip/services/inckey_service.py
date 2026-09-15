"""
Teleset CRM Standart IncKey (Otomatik Tekil Kod Üretim) Servisi
Format: [SUREC_KODU]-[YIL]-[000_SIRA_NO]  (Örn: PRJ-2026-001, TEK-2026-001, ECO-2026-001-A)
"""
from django.db import transaction
from django.utils import timezone


def inckey_uret(surec_tipi='PRJ', revizyon=None):
    """
    Race-condition korumalı, atomik IncKey üretici.
    """
    from crm_takip.models import SistemKodSayaci
    
    aktif_yil = timezone.now().year
    surec_tipi = surec_tipi.upper().strip()

    with transaction.atomic():
        sayac, created = SistemKodSayaci.objects.select_for_update().get_or_create(
            surec_tipi=surec_tipi,
            yil=aktif_yil,
            defaults={'son_sira_no': 100}
        )
        sayac.son_sira_no += 1
        sayac.save()

        sira_str = f"{sayac.son_sira_no:03d}"
        temel_kod = f"{surec_tipi}-{aktif_yil}-{sira_str}"

        if revizyon:
            return f"{temel_kod}-{revizyon}"
        return temel_kod


def siradaki_inckey_goruntule(surec_tipi='PRJ', revizyon=None):
    """
    Sayacı artırmadan sıradaki kodu önizleme amaçlı döner.
    """
    from crm_takip.models import SistemKodSayaci
    
    aktif_yil = timezone.now().year
    surec_tipi = surec_tipi.upper().strip()

    sayac = SistemKodSayaci.objects.filter(surec_tipi=surec_tipi, yil=aktif_yil).first()
    son_no = sayac.son_sira_no if sayac else 100
    siradaki_no = son_no + 1

    sira_str = f"{siradaki_no:03d}"
    temel_kod = f"{surec_tipi}-{aktif_yil}-{sira_str}"

    if revizyon:
        return f"{temel_kod}-{revizyon}"
    return temel_kod
