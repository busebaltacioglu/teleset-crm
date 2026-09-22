from django.core.management.base import BaseCommand
from crm_takip.models import SozlesmeAdimTanimi, SozlesmeSureci, SozlesmeAdimKaydi

class Command(BaseCommand):
    help = "9 Adımlık Teleset Sözleşmenin Değerlendirilmesi Süreci Master Verilerini Yükler"

    def handle(self, *args, **options):
        adilar = [
            # FAZ 1: Talep Kaydı & İnceleme (Adım 1 - 3)
            {
                "adim_no": 1,
                "baslik": "Talebin Kaydı ve İnceleme Planının Oluşturulması",
                "faaliyet_tanimi": "Müşteriden gelen sözleşme taslağı ve ekleri alınarak Dochuman Müşteri Sözleşme Takip Formu açılır. Sözleşme türü, müşteri, ürün grubu/fabrika, taraf bilgileri, tarih, versiyon ve eklerin tamlığı kontrol edilir. Sözleşmenin kapsamına göre inceleme yapacak ilgili birimler ile şirket hukuk danışmanı belirlenir. Eksik dokümanlar tamamlanmadan değerlendirme başlatılmaz.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Fabrika Müdürü\nI – Atanan iç birimler ve Şirket Hukuk Danışmanı",
                "sorumlular": "A – Satış ve Pazarlama Müdürü; R – İlgili Ürün Grubu Satış Sorumlusu; C – İlgili Fabrika Müdürü; I – Atanan iç birimler ve Şirket Hukuk Danışmanı",
                "ilgili_dokumanlar": "Müşteri Sözleşme Taslağı ve Ekleri, RFQ / Onaylı Teklif, Müşteri Talebi ve İlgili Yazışmalar",
                "dijital_platformlar": "Dochuman, EBA-CRM",
                "karar_adimi_mi": False,
                "faz": "FAZ1"
            },
            {
                "adim_no": 2,
                "baslik": "Atanan Birimlerin İncelemesi",
                "faaliyet_tanimi": "Atanan birimler, sözleşme maddelerini kendi sorumluluk alanları açısından inceler. Her madde; madde numarası, kontrol konusu, sorumlu birim, referans doküman, uygunluk durumu ve açıklama bilgileriyle Dochuman üzerinde değerlendirilir. Uygun bulunmayan maddeler için gerekçe, risk ve önerilen revizyon veya kabul koşulu belirtilir.",
                "sorumlular_raci": "A – İlgili Birim Yöneticisi\nR – Atanan Birim Sorumluları\nC – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Fabrika Müdürü\nI – Satış ve Pazarlama Müdürü",
                "sorumlular": "A – İlgili Birim Yöneticisi; R – Atanan Birim Sorumluları; C – İlgili Ürün Grubu Satış Sorumlusu; C – İlgili Fabrika Müdürü; I – Satış ve Pazarlama Müdürü",
                "ilgili_dokumanlar": "Müşteri Sözleşme Taslağı ve Ekleri, RFQ / Onaylı Teklif, Müşteri Talebi ve İlgili Yazışmalar, İlgili Teknik, Kalite, Ticari ve Finansal Dokümanlar",
                "dijital_platformlar": "Dochuman",
                "karar_adimi_mi": False,
                "faz": "FAZ1"
            },
            {
                "adim_no": 3,
                "baslik": "Şirket Hukuk Danışmanı İncelemesi",
                "faaliyet_tanimi": "Sözleşme taslağı ve ekleri; sorumluluk ve tazminat, cezai şart, gizlilik ve kişisel veriler, fikri mülkiyet, süre ve fesih, uygulanacak hukuk, uyuşmazlık çözümü ve diğer hukuki riskler açısından şirket hukuk danışmanı tarafından incelenir. Hukuk danışmanının e-posta ile ilettiği yazılı görüş ve varsa revizyonlu sözleşme metni, İlgili Ürün Grubu Satış Sorumlusu tarafından Dochuman kaydına eklenir.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – Şirket Hukuk Danışmanı\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Birim Yöneticileri\nI – İlgili Fabrika Müdürü",
                "sorumlular": "A – Satış ve Pazarlama Müdürü; R – Şirket Hukuk Danışmanı; R – İlgili Ürün Grubu Satış Sorumlusu; C – İlgili Birim Yöneticileri; I – İlgili Fabrika Müdürü",
                "ilgili_dokumanlar": "Müşteri Sözleşme Taslağı ve Ekleri, Varsa İlgili Birim Görüşleri, Yazılı Hukuk Görüşü, Hukuk Danışmanı Tarafından Revize Edilen Sözleşme Metni",
                "dijital_platformlar": "E-posta, Dochuman",
                "karar_adimi_mi": False,
                "faz": "FAZ1"
            },

            # FAZ 2: Değerlendirme & Yetkili Makam Kararı (Adım 4 - 5)
            {
                "adim_no": 4,
                "baslik": "Görüşlerin Birleştirilmesi ve Risk Değerlendirmesi",
                "faaliyet_tanimi": "İlgili birimlerin Dochuman üzerindeki değerlendirmeleri ile şirket hukuk danışmanının yazılı görüşü, İlgili Ürün Grubu Satış Sorumlusu tarafından birlikte değerlendirilir. Eksik değerlendirmeler tamamlatılır; uygun bulunmayan maddeler, önerilen revizyonlar ve bunların hukuki, ticari, finansal, teknik ve operasyonel etkileri Dochuman ana kaydı üzerinde birleştirilir. Yetkili makam onayı gerektiren kritik sapmalar belirlenir ve değerlendirmeye esas güncel sözleşme versiyonu işaretlenir.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – Şirket Hukuk Danışmanı\nC – İlgili Fabrika Müdürü\nC – İlgili Birim Yöneticileri",
                "sorumlular": "A – Satış ve Pazarlama Müdürü; R – İlgili Ürün Grubu Satış Sorumlusu; C – Şirket Hukuk Danışmanı; C – İlgili Fabrika Müdürü; C – İlgili Birim Yöneticileri",
                "ilgili_dokumanlar": "Müşteri Sözleşme Taslağı ve Ekleri, İlgili Birimlerin Dochuman Değerlendirme Kayıtları, Yazılı Hukuk Görüşü, Hukuk Danışmanı Tarafından Revize Edilen Sözleşme Metni, RFQ / Onaylı Teklif",
                "dijital_platformlar": "Dochuman",
                "karar_adimi_mi": False,
                "faz": "FAZ2"
            },
            {
                "adim_no": 5,
                "baslik": "Kritik Sapma ve Yetkili Makam Kararı",
                "faaliyet_tanimi": "4. adımda belirlenen kritik sapmalar; ilgili birim görüşleri, yazılı hukuk görüşü ve olası ticari, finansal, teknik ve operasyonel etkileriyle birlikte yetkili makamın değerlendirmesine sunulur. Verilen karar gerekçesi ve varsa kabul koşullarıyla birlikte Dochuman üzerinde kayıt altına alınır. Kritik sapma bulunmaması veya sapmanın onaylanması durumunda Teleset müzakere pozisyonunun oluşturulmasına geçilir. Revizyon veya ek değerlendirme talebinde 4. adıma dönülür; sözleşmeye devam edilmeme kararında kayıt gerekçesiyle kapatılır.",
                "sorumlular_raci": "A – Yetkili Onay Makamı (Genel Müdür Yardımcısı / Genel Müdür / Yönetim Kurulu)\nR – Satış ve Pazarlama Müdürü\nC – Şirket Hukuk Danışmanı\nC – İlgili Fabrika Müdürü\nC – İlgili Birim Yöneticileri\nI – İlgili Ürün Grubu Satış Sorumlusu",
                "sorumlular": "A – Yetkili Onay Makamı; R – Satış ve Pazarlama Müdürü; C – Şirket Hukuk Danışmanı; C – İlgili Fabrika Müdürü; C – İlgili Birim Yöneticileri; I – İlgili Ürün Grubu Satış Sorumlusu",
                "ilgili_dokumanlar": "Müşteri Sözleşme Taslağı ve Ekleri, İlgili Birimlerin Dochuman Değerlendirme Kayıtları, Yazılı Hukuk Görüşü, RFQ / Onaylı Teklif, Yetkili Makam Kararı / Onay Kaydı",
                "dijital_platformlar": "Dochuman",
                "karar_adimi_mi": True,
                "faz": "FAZ2"
            },

            # FAZ 3: Müşteri Müzakeresi & Mutabakat Kontrolü (Adım 6 - 7)
            {
                "adim_no": 6,
                "baslik": "Teleset Müzakere Pozisyonunun Oluşturulması ve Müşteri Görüşmeleri",
                "faaliyet_tanimi": "İlgili birim görüşleri, yazılı hukuk görüşü, onaylanan sapmalar ve belirlenen kabul koşulları esas alınarak Teleset’in müzakere pozisyonu ve revizyonlu sözleşme metni oluşturulur. Sözleşme müşteriyle onaylanan sınırlar içerisinde müzakere edilir. Gönderilen ve alınan sözleşme versiyonları, müşteri geri bildirimleri, açık maddeler ve ilgili yazışmalar Dochuman üzerinde kayıt altına alınır. Onay sınırlarını aşan talepler için müşteriye bağlayıcı taahhütte bulunulmaz.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – Şirket Hukuk Danışmanı\nC – İlgili Fabrika Müdürü\nC – İlgili Birim Yöneticileri\nI – Yetkili Onay Makamı",
                "sorumlular": "A – Satış ve Pazarlama Müdürü; R – İlgili Ürün Grubu Satış Sorumlusu; C – Şirket Hukuk Danışmanı; C – İlgili Fabrika Müdürü; C – İlgili Birim Yöneticileri; I – Yetkili Onay Makamı",
                "ilgili_dokumanlar": "Müşteri Sözleşme Taslağı ve Ekleri, Yazılı Hukuk Görüşü, Yetkili Makam Kararı / Onay Kaydı, Revizyonlu Sözleşme Metni, RFQ / Onaylı Teklif, Müşteri Görüşme ve Yazışma Kayıtları",
                "dijital_platformlar": "Dochuman, EBA-CRM",
                "karar_adimi_mi": False,
                "faz": "FAZ3"
            },
            {
                "adim_no": 7,
                "baslik": "Nihai Mutabakat ve Sözleşme Metni Kontrolü",
                "faaliyet_tanimi": "Müşteriyle varılan mutabakat sonrasında nihai sözleşme metni kontrol edilir: Yabancı hukuk, sınırsız sorumluluk, önemli cezai şart, fikri mülkiyet devri, veri güvenliği, yetki belirsizliği veya önemli finansal/operasyonel riskler incelenir. Kritik sapma yoksa veya onaylı sınırlar içindeyse 8. adıma geçilir. Yeni kritik sapma veya revizyon ihtiyacı varsa 5. adıma yetkili makam onayına dönülür; müşteriyle mutabakat sağlanamazsa kayıt gerekçesiyle olumsuz kapatılır.",
                "sorumlular_raci": "A – Şirket iç onay düzeninde belirlenen yetkili makam\nR – Satış ve Pazarlama Müdürü\nC – Şirket Hukuk Danışmanı\nC – Genel Müdür Yardımcısı / Genel Müdür / Yönetim Kurulu\nI – İlgili Ürün Grubu Satış Sorumlusu",
                "sorumlular": "A – Şirket iç onay düzeninde belirlenen makam; R – Satış ve Pazarlama Müdürü; C – Şirket Hukuk Danışmanı, GMY, GM, Yönetim Kurulu; I – Ürün Grubu Satış Sorumlusu",
                "ilgili_dokumanlar": "Nihai Sözleşme Taslağı ve Ekleri, Yazılı Hukuk Görüşü, Yetkili Makam Kararı / Onay Kaydı, RFQ / Onaylı Teklif, Müşteri Görüşme ve Yazışma Kayıtları, Dochuman Değerlendirme ve Versiyon Kayıtları",
                "dijital_platformlar": "Dochuman, EBA-CRM",
                "karar_adimi_mi": True,
                "faz": "FAZ3"
            },

            # FAZ 4: Yetkili İmza & Yürürlük Takibi (Adım 8 - 9)
            {
                "adim_no": 8,
                "baslik": "Yetkili İmza, Arşivleme ve Dağıtım",
                "faaliyet_tanimi": "7. adımda imzaya esas nihai versiyon olarak belirlenen sözleşme, yürürlükteki imza sirkülerine uygun yetkili kişiler tarafından imzalanır. Karşılıklı imza tamamlandıktan sonra taraf, tarih, imza, sayfa ve eklerin tamlığı kontrol edilir. Tam ve imzalı sözleşme Dochuman’a yüklenerek taslak versiyonlardan ayrılır. Sözleşmeye erişmesi veya sözleşme yükümlülüklerini uygulaması gereken ilgili birimlere bildirim yapılır.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – Yetkili İmza Sahibi\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Fabrika Müdürü\nI – Sözleşme Yükümlülüklerinden Etkilenen Birimler",
                "sorumlular": "A – Satış ve Pazarlama Müdürü; R – Yetkili İmza Sahibi; R – İlgili Ürün Grubu Satış Sorumlusu; C – İlgili Fabrika Müdürü; I – Sözleşme Yükümlülüklerinden Etkilenen Birimler",
                "ilgili_dokumanlar": "İmzaya Esas Nihai Sözleşme ve Ekleri, Yetkili Makam Kararı / Onay Kaydı, İmza Sirküleri, Karşılıklı İmzalı Sözleşme ve Ekleri",
                "dijital_platformlar": "Dochuman, EBA-CRM",
                "karar_adimi_mi": False,
                "faz": "FAZ4"
            },
            {
                "adim_no": 9,
                "baslik": "Sözleşme Yükümlülüklerinin ve Sürelerinin Takibi",
                "faaliyet_tanimi": "Karşılıklı imzalanan sözleşmedeki ticari, finansal, teknik, kalite, lojistik ve hukuki yükümlülükler ile sorumlu birimler, önemli tarihler, geçerlilik süresi, yenileme ve fesih bildirim süreleri Dochuman üzerinde kayıt altına alınır ve ilgili birimlere bildirilir. İlgili birimler kendi sorumluluk alanlarındaki yükümlülükleri yerine getirir; İlgili Ürün Grubu Satış Sorumlusu sözleşme süresini ve müşteriyle ilgili ticari yükümlülükleri koordine eder. Yenileme, değişiklik veya fesih ihtiyacı, sözleşmedeki bildirim süreleri dikkate alınarak zamanında değerlendirmeye alınır.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nR – İlgili Sözleşme Yükümlülüğünün Süreç Sahibi\nC – İlgili Fabrika Müdürü\nC – İlgili Birim Yöneticileri\nC – Şirket Hukuk Danışmanı\nI – Sözleşme Yükümlülüklerinden Etkilenen Birimler",
                "sorumlular": "A – Satış ve Pazarlama Müdürü; R – İlgili Ürün Grubu Satış Sorumlusu; R – İlgili Sözleşme Yükümlülüğünün Süreç Sahibi; C – İlgili Fabrika Müdürü; C – İlgili Birim Yöneticileri; C – Şirket Hukuk Danışmanı; I – Sözleşme Yükümlülüklerinden Etkilenen Birimler",
                "ilgili_dokumanlar": "İmzaya Esas Nihai Sözleşme ve Ekleri, Yetkili Makam Kararı / Onay Kaydı, İmza Sirküleri, Karşılıklı İmzalı Sözleşme ve Ekleri",
                "dijital_platformlar": "Dochuman, EBA-CRM",
                "karar_adimi_mi": False,
                "faz": "FAZ4"
            }
        ]

        # 1. Eski 15 adımlıktan kalan ve 9'dan büyük olan adım tanımlarını temizleyelim
        # Önce mevcut süreçlerin bu adımlara olan referanslarını korumak / düzenlemek için kontrol
        SozlesmeAdimKaydi.objects.filter(adim__adim_no__gt=9).delete()
        SozlesmeAdimTanimi.objects.filter(adim_no__gt=9).delete()

        created_count = 0
        updated_count = 0

        for item in adilar:
            adim_tanimi, created = SozlesmeAdimTanimi.objects.update_or_create(
                adim_no=item["adim_no"],
                defaults=item
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        # Mevcut süreçlerin adım kayıtlarını senkronize et
        for surec in SozlesmeSureci.objects.all():
            for tanim in SozlesmeAdimTanimi.objects.all().order_by('adim_no'):
                SozlesmeAdimKaydi.objects.get_or_create(
                    surec=surec,
                    adim=tanim,
                    defaults={
                        'durum': 'DEVAM_EDIYOR' if tanim.adim_no == 1 else 'BEKLIYOR',
                        'dokuman_referansi': tanim.ilgili_dokumanlar.split(',')[0] if tanim.ilgili_dokumanlar else ""
                    }
                )

        self.stdout.write(self.style.SUCCESS(
            f"Sözleşme Değerlendirme Süreci 9 Adım Master Verisi Başarıyla Güncellendi! "
            f"({created_count} yeni oluşturuldu, {updated_count} güncellendi)"
        ))
