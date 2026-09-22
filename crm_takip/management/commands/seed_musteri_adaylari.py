from django.core.management.base import BaseCommand
from django.utils import timezone
from crm_takip.models import MusteriAdayi, MusteriAdayiNotu

class Command(BaseCommand):
    help = 'Müşteri Adayları (Leads / Prospects) Demo ve Başlangıç Verilerini Yükler'

    def handle(self, *args, **options):
        adaylar_data = [
            {
                'ad_soyad': 'Markus Weber',
                'unvan': 'Satınalma Müdürü / Procurement Lead',
                'sirket_adi': 'Miele Die Werkzeugfabrik',
                'sektor': 'Beyaz Eşya',
                'ulke': 'Almanya',
                'sehir': 'Gütersloh',
                'adres': 'Carl-Miele-Straße 29, 33332 Gütersloh',
                'eposta': 'markus.weber@miele.de',
                'telefon': '+49 5241 89-1240',
                'web_sitesi': 'www.miele.de',
                'kanal': 'Pazar Ziyareti',
                'kaynak': 'Almanya 2026 Q1 Stratejik Ziyaret',
                'durum': 'ILETISIMDE',
                'oncelik': 'SICAK',
                'tahmini_potansiyel_ciro': 1250000.00,
                'ilgili_urun_gruplari': 'Pres Sac Parça, Kondanser',
                'etiketler': 'Almanya, 400T Pres, Yıkama Grubu',
                'atanan_sorumlu': 'Buse Nur BALTACIOĞLU',
                'aciklama': 'Pazar ziyareti kapsamında görüşüldü. Yeni çamaşır makinesi şasi parçaları için 400T pres kalıp kabiliyetimiz tanıtıldı.',
                'notlar': [
                    ('TOPLANTI', 'Pazar Ziyareti & Yüz Yüze Tanıtım', 'Gütersloh tesislerinde ilk temas gerçekleştirildi. Teleset üretim tesisleri ve kalite sertifikaları sunuldu.'),
                    ('EPOSTA', 'Şirket Kataloğu & Sertifikalar Gönderildi', 'IATF 16949 ve ISO 9001 sertifikaları ile makine parkı listesi e-posta ile paylaşıldı.'),
                ]
            },
            {
                'ad_soyad': 'Piotr Kowalski',
                'unvan': 'Tedarik Zinciri Direktörü',
                'sirket_adi': 'Amica S.A. Poland',
                'sektor': 'Beyaz Eşya',
                'ulke': 'Polonya',
                'sehir': 'Wronki',
                'adres': 'ul. Mickiewicza 52, 64-510 Wronki',
                'eposta': 'p.kowalski@amica.com.pl',
                'telefon': '+48 67 25 46 100',
                'web_sitesi': 'www.amica.pl',
                'kanal': 'Fuar & Etkinlik',
                'kaynak': 'IFA Berlin 2026',
                'durum': 'NITELIKLI',
                'oncelik': 'SICAK',
                'tahmini_potansiyel_ciro': 850000.00,
                'ilgili_urun_gruplari': 'Kablo Grubu & Demetleri, Metal Parça',
                'etiketler': 'Polonya, Kablo Grubu, IFA 2026',
                'atanan_sorumlu': 'Buse Nur BALTACIOĞLU',
                'aciklama': 'Fuar standımızda fırın kablo demetleri ve sac yan panel tedariki için teknik şartname talep edildi.',
                'notlar': [
                    ('TOPLANTI', 'IFA Berlin Stand Görüşmesi', 'Fuar standımızda 45 dakikalık detaylı teknik ve ticari toplantı yapıldı.'),
                    ('TELEFON', 'Teknik Çizimler Hakkında Görüşüldü', 'Fırın kablo grupları için numune ve teknik resimlerin haftaya iletileceği teyit edildi.'),
                ]
            },
            {
                'ad_soyad': 'Matteo Bianchi',
                'unvan': 'Global Sourcing Manager',
                'sirket_adi': 'DeLonghi Appliances S.r.l.',
                'sektor': 'İklimlendirme & Soğutma',
                'ulke': 'İtalya',
                'sehir': 'Treviso',
                'adres': 'Via Lodovico Seitz 47, 31100 Treviso',
                'eposta': 'matteo.bianchi@delonghigroup.com',
                'telefon': '+39 0422 4131',
                'web_sitesi': 'www.delonghi.com',
                'kanal': 'Müşteri Referansı',
                'kaynak': 'Mevcut İtalyan Müşteri Tavsiyesi',
                'durum': 'TEKLIF_ASAMASINDA',
                'oncelik': 'SICAK',
                'tahmini_potansiyel_ciro': 2100000.00,
                'ilgili_urun_gruplari': 'Kondanser & Soğutma, Bakır Boru',
                'etiketler': 'İtalya, Kondanser, RFQ Bekleniyor',
                'atanan_sorumlu': 'Buse Nur BALTACIOĞLU',
                'aciklama': 'Kondanser ve soğutma boru komponentleri için yıllık 250.000 adetlik seri üretim şartnamesi inceleniyor.',
                'notlar': [
                    ('NOT', 'Referans İletişimi Kuruldu', 'İtalya pazarındaki partnerimiz üzerinden doğrudan sıcak temas sağlandı.'),
                    ('TOPLANTI', 'Teknik Fizibilite Online Toplantısı', 'Kalıphane ve Proje ekibimizle teknik fizibilite detayları görüşüldü.'),
                ]
            },
            {
                'ad_soyad': 'Alain Laurent',
                'unvan': 'Kategori Satınalma Uzmanı',
                'sirket_adi': 'Groupe SEB France',
                'sektor': 'Beyaz Eşya',
                'ulke': 'Fransa',
                'sehir': 'Lyon',
                'adres': '112 Chemin du Moulin Carron, 69130 Écully',
                'eposta': 'alaurent@groupeseb.com',
                'telefon': '+33 4 72 18 18 18',
                'web_sitesi': 'www.groupeseb.com',
                'kanal': 'LinkedIn / Sosyal Medya',
                'kaynak': 'LinkedIn B2B Outreach 2026',
                'durum': 'YENI',
                'oncelik': 'ILIK',
                'tahmini_potansiyel_ciro': 420000.00,
                'ilgili_urun_gruplari': 'Kalıp, Fikstür & Aparat',
                'etiketler': 'Fransa, Kalıphane, Küçük Ev Aletleri',
                'atanan_sorumlu': 'Buse Nur BALTACIOĞLU',
                'aciklama': 'LinkedIn üzerinden bağlantı kuruldu. Yeni pres kalıpları için tedarikçi havuzuna dahil olma başvurusu yapıldı.',
                'notlar': [
                    ('NOT', 'İlk LinkedIn Bağlantısı', 'Şirket profili ve kalıphane kabiliyetlerimiz iletildi.'),
                ]
            },
            {
                'ad_soyad': 'Stefan Radu',
                'unvan': 'Operasyon & Satınalma Müdürü',
                'sirket_adi': 'Arctic S.A. Găești',
                'sektor': 'Beyaz Eşya',
                'ulke': 'Romanya',
                'sehir': 'Dâmbovița',
                'adres': 'Str. 13 Decembrie nr. 210, Găești',
                'eposta': 'stefan.radu@arctic.ro',
                'telefon': '+40 245 710 100',
                'web_sitesi': 'www.arctic.ro',
                'kanal': 'Pazar Ziyareti',
                'kaynak': 'Romanya Ülke Analizi 2026',
                'durum': 'ILETISIMDE',
                'oncelik': 'ILIK',
                'tahmini_potansiyel_ciro': 680000.00,
                'ilgili_urun_gruplari': 'Metal Parça & Sac Şekillendirme',
                'etiketler': 'Romanya, Buzdolabı, Pres Parça',
                'atanan_sorumlu': 'Buse Nur BALTACIOĞLU',
                'aciklama': 'Romanya fabrikası için yıllık 180.000 adetlik sac büküm parçaları değerlendiriliyor.',
                'notlar': [
                    ('ZIYARET', 'Găești Fabrika Ziyareti', 'Buzdolabı üretim hatları yerinde incelendi ve mevcut tedarik zinciri darboğazları öğrenildi.'),
                ]
            }
        ]

        sayac = 0
        for data in adaylar_data:
            notlar = data.pop('notlar', [])
            adayi, created = MusteriAdayi.objects.get_or_create(
                sirket_adi=data['sirket_adi'],
                ad_soyad=data['ad_soyad'],
                defaults=data
            )
            if created:
                sayac += 1
                for not_tipi, baslik, icerik in notlar:
                    MusteriAdayiNotu.objects.create(
                        adayi=adayi,
                        not_tipi=not_tipi,
                        baslik=baslik,
                        icerik=icerik,
                        ekleyen='Buse Nur BALTACIOĞLU',
                        tarih=timezone.now()
                    )

        self.stdout.write(self.style.SUCCESS(f"{sayac} yeni Müşteri Adayı başarıyla yüklendi!"))
