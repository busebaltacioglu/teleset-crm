"""
Teleset Intranet SQL Server (172.16.8.49) Read-Only Entegrasyon Servisi
Kaynak Tablo: [Teleset_Intranet].[dbo].[Teleset_Akademi_Personel]
"""
import pyodbc
from django.core.cache import cache

SQL_SERVER_HOST = "172.16.8.49"
SQL_DATABASE = "Teleset_Intranet"
CACHE_TTL = 300  # 5 dakika önbellek süresi

_FALLBACK_ANA_DEPARTMANLAR = [
    "CERKEZKOY",
    "KABLOGR",
    "KALIPHANE",
    "KONDANSER",
    "MANISA ORTAK",
    "PRESHANE",
]

_FALLBACK_PROJE_LIDERLERI = [
    {"id": 9, "sicil_no": "09998450", "ad_soyad": "BUSE NUR BALTACIOĞLU", "pozisyon": "Yazılım Destek Personeli", "departman": "Genel Müdürlük", "sirket": "TELESET MANİSA", "ana_departman": "MANISA ORTAK", "mail": ""},
    {"id": 10, "sicil_no": "09998451", "ad_soyad": "YİĞİT EFE BİLİR", "pozisyon": "İş Çözümleri Mühendisi", "departman": "Genel Müdürlük", "sirket": "TELESET MANİSA", "ana_departman": "MANISA ORTAK", "mail": ""},
    {"id": 11, "sicil_no": "09998460", "ad_soyad": "MELİSA ARAS", "pozisyon": "Satış Mühendisi", "departman": "Satış & Pazarlama", "sirket": "TELESET MANİSA", "ana_departman": "MANISA ORTAK", "mail": ""},
    {"id": 12, "sicil_no": "09998461", "ad_soyad": "SENA TAŞA", "pozisyon": "Satış Analiz Mühendisi", "departman": "Satış & Pazarlama", "sirket": "TELESET MANİSA", "ana_departman": "MANISA ORTAK", "mail": ""},
    {"id": 13, "sicil_no": "09998462", "ad_soyad": "YANKI ÇAM", "pozisyon": "Satış Uzmanı", "departman": "Satış & Pazarlama", "sirket": "TELESET MANİSA", "ana_departman": "MANISA ORTAK", "mail": ""},
    {"id": 14, "sicil_no": "09998463", "ad_soyad": "EGEMEN ARSLANKIRAY", "pozisyon": "Proje ve Ürün Geliştirme Sorumlusu", "departman": "Proje", "sirket": "TELESET MANİSA", "ana_departman": "PRESHANE", "mail": ""},
    {"id": 15, "sicil_no": "09998464", "ad_soyad": "FİGEN ÇETİN", "pozisyon": "Proje ve Ürün Geliştirme Sorumlusu", "departman": "Kondanser", "sirket": "TELESET MANİSA", "ana_departman": "KONDANSER", "mail": ""},
    {"id": 16, "sicil_no": "09998465", "ad_soyad": "MİNE ŞAHİN", "pozisyon": "Proje ve Ürün Geliştirme Sorumlusu", "departman": "Preshane", "sirket": "TELESET MANİSA", "ana_departman": "PRESHANE", "mail": ""},
    {"id": 17, "sicil_no": "09998466", "ad_soyad": "ONAT ÖZYURT", "pozisyon": "Proje Mühendisi", "departman": "Kablo Grubu", "sirket": "TELESET MANİSA", "ana_departman": "KABLOGR", "mail": ""},
    {"id": 18, "sicil_no": "09998467", "ad_soyad": "SILA KARABULUT GÖKTÜ", "pozisyon": "Proje Mühendisi", "departman": "Kablo Grubu", "sirket": "TELESET MANİSA", "ana_departman": "KABLOGR", "mail": ""},
    {"id": 19, "sicil_no": "09998468", "ad_soyad": "MERT ALİ CAN", "pozisyon": "URGE - Endüstri Mühendisi", "departman": "Proje", "sirket": "TELESET MANİSA", "ana_departman": "PRESHANE", "mail": ""},
    {"id": 8, "sicil_no": "09998435", "ad_soyad": "MUHARREM FURKAN TARHAN", "pozisyon": "Yazılım Destek Sorumlusu", "departman": "Genel Müdürlük", "sirket": "TELESET MANİSA", "ana_departman": "MANISA ORTAK", "mail": ""},
    {"id": 6, "sicil_no": "09998410", "ad_soyad": "GİZEM ERBAYAT BOĞAN", "pozisyon": "Sistem Uzmanı", "departman": "Bilgi İşlem", "sirket": "TELESET MANİSA", "ana_departman": "MANISA ORTAK", "mail": ""},
]

_FALLBACK_PAZARLAMA_UZMANLARI = [
    {"id": 11, "sicil_no": "09998460", "ad_soyad": "MELİSA ARAS", "pozisyon": "Satış Mühendisi", "departman": "Satış & Pazarlama", "sirket": "TELESET MANİSA", "ana_departman": "MANISA ORTAK", "mail": ""},
    {"id": 12, "sicil_no": "09998461", "ad_soyad": "SENA TAŞA", "pozisyon": "Satış Analiz Mühendisi", "departman": "Satış & Pazarlama", "sirket": "TELESET MANİSA", "ana_departman": "MANISA ORTAK", "mail": ""},
    {"id": 13, "sicil_no": "09998462", "ad_soyad": "YANKI ÇAM", "pozisyon": "Satış Uzmanı", "departman": "Satış & Pazarlama", "sirket": "TELESET MANİSA", "ana_departman": "MANISA ORTAK", "mail": ""},
]

_FALLBACK_SATIS_MUDURLERI = [
    {"id": 101, "sicil_no": "09998101", "ad_soyad": "ALİ OKSAY CANLI", "pozisyon": "Ürün ve İş Geliştirme Müdürü", "departman": "Satış & İş Geliştirme", "sirket": "TELESET MANİSA", "ana_departman": "KABLOGR", "mail": ""},
    {"id": 102, "sicil_no": "09998102", "ad_soyad": "BEYHAN YORGANCI", "pozisyon": "Genel Müdür", "departman": "Genel Müdürlük", "sirket": "TELESET MANİSA", "ana_departman": "MANISA ORTAK", "mail": ""},
    {"id": 103, "sicil_no": "09998103", "ad_soyad": "SELEN ÇAM DENİZ", "pozisyon": "Genel Müdür Yardımcısı", "departman": "Genel Müdürlük", "sirket": "TELESET MANİSA", "ana_departman": "MANISA ORTAK", "mail": ""},
    {"id": 104, "sicil_no": "09998104", "ad_soyad": "CÜNEYT URGAN", "pozisyon": "Fabrika Müdürü", "departman": "Kondanser", "sirket": "TELESET MANİSA", "ana_departman": "KONDANSER", "mail": ""},
    {"id": 105, "sicil_no": "09998105", "ad_soyad": "MURAT KILIÇ", "pozisyon": "Fabrika Müdürü", "departman": "Kablo Grubu", "sirket": "TELESET MANİSA", "ana_departman": "KABLOGR", "mail": ""},
    {"id": 106, "sicil_no": "09998106", "ad_soyad": "SONER HANOĞLU", "pozisyon": "Fabrika Müdürü", "departman": "Kalıphane", "sirket": "TELESET MANİSA", "ana_departman": "KALIPHANE", "mail": ""},
    {"id": 107, "sicil_no": "09998107", "ad_soyad": "ÖMER BERKAY AYSAL", "pozisyon": "Fabrika Müdürü", "departman": "Preshane", "sirket": "TELESET MANİSA", "ana_departman": "PRESHANE", "mail": ""},
    {"id": 108, "sicil_no": "09998108", "ad_soyad": "TARKAN AKIN", "pozisyon": "Fabrika Müdürü", "departman": "Yönetim", "sirket": "TELESET MANİSA", "ana_departman": "MANISA ORTAK", "mail": ""},
    {"id": 7, "sicil_no": "09998420", "ad_soyad": "ONUR TUNCER", "pozisyon": "Bilgi Teknolojileri Müdürü", "departman": "Bilgi İşlem", "sirket": "TELESET MANİSA", "ana_departman": "MANISA ORTAK", "mail": ""},
    {"id": 109, "sicil_no": "09998109", "ad_soyad": "BERNA KANIT", "pozisyon": "İnsan Kaynakları Müdürü", "departman": "İnsan Kaynakları", "sirket": "TELESET MANİSA", "ana_departman": "MANISA ORTAK", "mail": ""},
    {"id": 110, "sicil_no": "09998110", "ad_soyad": "GÜLAYŞE ÖZIRK ÖZ", "pozisyon": "Tedarik Zinciri Müdürü", "departman": "Tedarik Zinciri", "sirket": "TELESET MANİSA", "ana_departman": "MANISA ORTAK", "mail": ""},
    {"id": 111, "sicil_no": "09998111", "ad_soyad": "EBRU KUZUCU", "pozisyon": "Bütçe Planlama ve Kontrol Yöneticisi", "departman": "Genel Müdürlük", "sirket": "TELESET MANİSA", "ana_departman": "MANISA ORTAK", "mail": ""},
]


def _get_db_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SQL_SERVER_HOST};"
        f"DATABASE={SQL_DATABASE};"
        f"Trusted_Connection=yes;"
        f"Timeout=3;"
    )
    return pyodbc.connect(conn_str)


def get_intranet_sirketler():
    """
    Teleset_Akademi_Personel tablosundaki aktif Ana Departman listesini döner.
    EV HİZMETLERİ, KARPEK AMBALAJ, KARPEK HUZUR, ZEKİ ve YÖNETİM KURULU hariç tutulur.
    """
    try:
        cached = cache.get('intranet_sirketler')
        if cached:
            return cached
    except Exception:
        pass

    try:
        conn = _get_db_connection()
        cur = conn.cursor()
        query = """
            SELECT DISTINCT Ana_Departman 
            FROM dbo.Teleset_Akademi_Personel 
            WHERE Durum = 1 
              AND Ana_Departman IS NOT NULL
              AND Sirket NOT IN ('EV HİZMETLERİ', 'EV HIZMETLERI', 'KARPEK AMBALAJ', 'KARPEK HUZUR', 'ZEKİ', 'ZEKI')
              AND Sirket NOT LIKE '%KARPEK%'
              AND Sirket NOT LIKE '%ZEK%'
              AND Sirket NOT LIKE '%EV H%'
              AND Ana_Departman NOT IN ('EV HİZMETLERİ', 'EV HIZMETLERI', 'KARPEK AMBALAJ', 'KARPEK HUZUR', 'ZEKİ', 'ZEKI', 'YÖNETİM KURULU', 'YONETIM KURULU')
              AND Ana_Departman NOT LIKE '%KARPEK%'
              AND Ana_Departman NOT LIKE '%ZEK%'
              AND Ana_Departman NOT LIKE '%EV H%'
              AND Ana_Departman NOT LIKE '%YÖNETİM%'
              AND Ana_Departman NOT LIKE '%YONETIM%'
            ORDER BY Ana_Departman
        """
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        ana_departmanlar = []
        for r in rows:
            ana_dep = (r[0] or "").strip()
            if ana_dep and ana_dep not in ana_departmanlar:
                if not any(ex in ana_dep.upper() for ex in ['EV H', 'KARPEK', 'ZEK', 'YÖNETİM', 'YONETIM']):
                    ana_departmanlar.append(ana_dep)

        if not ana_departmanlar:
            ana_departmanlar = _FALLBACK_ANA_DEPARTMANLAR

        try:
            cache.set('intranet_sirketler', ana_departmanlar, CACHE_TTL)
        except Exception:
            pass

        return ana_departmanlar
    except Exception:
        return _FALLBACK_ANA_DEPARTMANLAR


def get_proje_liderleri():
    """
    Teleset_Akademi_Personel tablosundaki aktif Beyaz/Gri yaka personelleri döner.
    """
    try:
        cached = cache.get('intranet_proje_liderleri')
        if cached:
            return cached
    except Exception:
        pass

    try:
        conn = _get_db_connection()
        cur = conn.cursor()
        query = """
            SELECT Personel_Id, Sicil_No, Ad_Soyad, Sirket, Ana_Departman, Departman, Unvan, Pozisyon, Mail, Yonetici_Ad_Soyad
            FROM dbo.Teleset_Akademi_Personel
            WHERE Durum = 1 AND Kategori IN ('BEYAZ', 'GRI')
              AND Sirket NOT IN ('EV HİZMETLERİ', 'EV HIZMETLERI', 'KARPEK AMBALAJ', 'KARPEK HUZUR', 'ZEKİ', 'ZEKI')
              AND Sirket NOT LIKE '%KARPEK%'
              AND Sirket NOT LIKE '%ZEK%'
              AND Sirket NOT LIKE '%EV H%'
              AND Ana_Departman NOT IN ('EV HİZMETLERİ', 'EV HIZMETLERI', 'KARPEK AMBALAJ', 'KARPEK HUZUR', 'ZEKİ', 'ZEKI', 'YÖNETİM KURULU', 'YONETIM KURULU')
              AND Ana_Departman NOT LIKE '%KARPEK%'
              AND Ana_Departman NOT LIKE '%ZEK%'
              AND Ana_Departman NOT LIKE '%EV H%'
              AND Ana_Departman NOT LIKE '%YÖNETİM KURULU%'
              AND Ana_Departman NOT LIKE '%YONETIM KURULU%'
              AND Departman NOT LIKE '%YÖNETİM KURULU%'
              AND Departman NOT LIKE '%YONETIM KURULU%'
              AND Unvan NOT LIKE '%YÖNETİM KURULU%'
              AND Unvan NOT LIKE '%YONETIM KURULU%'
            ORDER BY Ad_Soyad
        """
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        personeller = []
        gorulen_isimler = set()
        for r in rows:
            ad_soyad = (r[2] or "").strip()
            if not ad_soyad or ad_soyad in gorulen_isimler:
                continue

            sirket = (r[3] or "").strip()
            ana_dep = (r[4] or "").strip()
            departman = (r[5] or "").strip()
            unvan = (r[6] or "").strip()
            pozisyon = (r[7] or "").strip()

            combined = f"{sirket} {ana_dep} {departman} {unvan} {pozisyon}".upper()
            if any(ex in combined for ex in ['EV H', 'KARPEK', 'ZEK', 'YÖNETİM KURULU', 'YONETIM KURULU']):
                continue

            gorulen_isimler.add(ad_soyad)
            personeller.append({
                "id": r[0],
                "sicil_no": (r[1] or "").strip(),
                "ad_soyad": ad_soyad,
                "sirket": sirket,
                "ana_departman": ana_dep,
                "departman": departman,
                "unvan": unvan,
                "pozisyon": pozisyon,
                "mail": (r[8] or "").strip(),
                "yonetici": (r[9] or "").strip(),
            })

        if not personeller:
            personeller = _FALLBACK_PROJE_LIDERLERI

        try:
            cache.set('intranet_proje_liderleri', personeller, CACHE_TTL)
        except Exception:
            pass

        return personeller
    except Exception:
        return _FALLBACK_PROJE_LIDERLERI


def get_pazarlama_uzmanlari():
    """
    Sorumlu Pazarlama Uzmanı:
    Teleset_Akademi_Personel tablosunda Pozisyon alanında '%SATIS%', '%SATIŞ%', '%PAZARLAMA%' geçen
    ve Müdür/Yönetici olmayan satış/pazarlama uzmanlarını döner.
    """
    try:
        cached = cache.get('intranet_pazarlama_uzmanlari')
        if cached:
            return cached
    except Exception:
        pass

    try:
        conn = _get_db_connection()
        cur = conn.cursor()
        query = """
            SELECT Personel_Id, Sicil_No, Ad_Soyad, Sirket, Ana_Departman, Departman, Unvan, Pozisyon, Mail, Yonetici_Ad_Soyad
            FROM dbo.Teleset_Akademi_Personel
            WHERE Durum = 1 AND Kategori IN ('BEYAZ', 'GRI')
              AND (Pozisyon LIKE '%SATIS%' OR Pozisyon LIKE '%SATIŞ%' OR Pozisyon LIKE '%satıs%' OR Pozisyon LIKE '%pazarlama%' OR Pozisyon LIKE '%PAZARLAMA%')
              AND (Pozisyon NOT LIKE '%MUDUR%' AND Pozisyon NOT LIKE '%MÜDÜR%' AND Pozisyon NOT LIKE '%mudur%')
              AND Sirket NOT IN ('EV HİZMETLERİ', 'EV HIZMETLERI', 'KARPEK AMBALAJ', 'KARPEK HUZUR', 'ZEKİ', 'ZEKI')
              AND Sirket NOT LIKE '%KARPEK%' AND Sirket NOT LIKE '%ZEK%' AND Sirket NOT LIKE '%EV H%'
              AND Ana_Departman NOT IN ('EV HİZMETLERİ', 'EV HIZMETLERI', 'KARPEK AMBALAJ', 'KARPEK HUZUR', 'ZEKİ', 'ZEKI', 'YÖNETİM KURULU', 'YONETIM KURULU')
              AND Ana_Departman NOT LIKE '%KARPEK%' AND Ana_Departman NOT LIKE '%ZEK%' AND Ana_Departman NOT LIKE '%EV H%'
              AND Ana_Departman NOT LIKE '%YÖNETİM KURULU%' AND Ana_Departman NOT LIKE '%YONETIM KURULU%'
            ORDER BY Ad_Soyad
        """
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        uzmanlar = []
        gorulen_isimler = set()
        for r in rows:
            ad_soyad = (r[2] or "").strip()
            if not ad_soyad or ad_soyad in gorulen_isimler:
                continue

            gorulen_isimler.add(ad_soyad)
            uzmanlar.append({
                "id": r[0],
                "sicil_no": (r[1] or "").strip(),
                "ad_soyad": ad_soyad,
                "sirket": (r[3] or "").strip(),
                "ana_departman": (r[4] or "").strip(),
                "departman": (r[5] or "").strip(),
                "unvan": (r[6] or "").strip(),
                "pozisyon": (r[7] or "").strip(),
                "mail": (r[8] or "").strip(),
                "yonetici": (r[9] or "").strip(),
            })

        if not uzmanlar:
            uzmanlar = _FALLBACK_PAZARLAMA_UZMANLARI

        try:
            cache.set('intranet_pazarlama_uzmanlari', uzmanlar, CACHE_TTL)
        except Exception:
            pass

        return uzmanlar
    except Exception:
        return _FALLBACK_PAZARLAMA_UZMANLARI


def get_satis_mudurleri():
    """
    Satış & Pazarlama Müdürü / Fabrika Müdürleri / Yöneticiler:
    Teleset_Akademi_Personel tablosunda Pozisyon alanında '%MUDUR%' veya '%MÜDÜR%' geçen yöneticileri döner.
    """
    try:
        cached = cache.get('intranet_satis_mudurleri')
        if cached:
            return cached
    except Exception:
        pass

    try:
        conn = _get_db_connection()
        cur = conn.cursor()
        query = """
            SELECT Personel_Id, Sicil_No, Ad_Soyad, Sirket, Ana_Departman, Departman, Unvan, Pozisyon, Mail, Yonetici_Ad_Soyad
            FROM dbo.Teleset_Akademi_Personel
            WHERE Durum = 1 AND Kategori IN ('BEYAZ', 'GRI')
              AND (Pozisyon LIKE '%MUDUR%' OR Pozisyon LIKE '%MÜDÜR%' OR Pozisyon LIKE '%mudur%')
              AND Sirket NOT IN ('EV HİZMETLERİ', 'EV HIZMETLERI', 'KARPEK AMBALAJ', 'KARPEK HUZUR', 'ZEKİ', 'ZEKI')
              AND Sirket NOT LIKE '%KARPEK%' AND Sirket NOT LIKE '%ZEK%' AND Sirket NOT LIKE '%EV H%'
              AND Ana_Departman NOT IN ('EV HİZMETLERİ', 'EV HIZMETLERI', 'KARPEK AMBALAJ', 'KARPEK HUZUR', 'ZEKİ', 'ZEKI', 'YÖNETİM KURULU', 'YONETIM KURULU')
              AND Ana_Departman NOT LIKE '%KARPEK%' AND Ana_Departman NOT LIKE '%ZEK%' AND Ana_Departman NOT LIKE '%EV H%'
              AND Ana_Departman NOT LIKE '%YÖNETİM KURULU%' AND Ana_Departman NOT LIKE '%YONETIM KURULU%'
            ORDER BY Ad_Soyad
        """
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        mudurler = []
        gorulen_isimler = set()
        for r in rows:
            ad_soyad = (r[2] or "").strip()
            if not ad_soyad or ad_soyad in gorulen_isimler:
                continue

            gorulen_isimler.add(ad_soyad)
            mudurler.append({
                "id": r[0],
                "sicil_no": (r[1] or "").strip(),
                "ad_soyad": ad_soyad,
                "sirket": (r[3] or "").strip(),
                "ana_departman": (r[4] or "").strip(),
                "departman": (r[5] or "").strip(),
                "unvan": (r[6] or "").strip(),
                "pozisyon": (r[7] or "").strip(),
                "mail": (r[8] or "").strip(),
                "yonetici": (r[9] or "").strip(),
            })

        if not mudurler:
            mudurler = _FALLBACK_SATIS_MUDURLERI

        try:
            cache.set('intranet_satis_mudurleri', mudurler, CACHE_TTL)
        except Exception:
            pass

        return mudurler
    except Exception:
        return _FALLBACK_SATIS_MUDURLERI


