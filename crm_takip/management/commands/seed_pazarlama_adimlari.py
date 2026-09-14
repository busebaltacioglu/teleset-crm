from django.core.management.base import BaseCommand
from crm_takip.models import SurecAdimTanimi

class Command(BaseCommand):
    help = "15 Adımlık Teleset Pazarlama Süreci Standart Tanımlarını Yükler"

    def handle(self, *args, **options):
        adilar = [
            {
                "adim_no": 1,
                "baslik": "Pazarlama süreci girdilerinin toplanması ve doğrulanması",
                "faaliyet_tanimi": "Pazarlama planlama çalışmalarına esas teşkil etmek üzere; ürün grubu ve fabrika bazındaki geçmiş satış, ciro ve kârlılık verileri, mevcut müşteri portföyü, devam eden projeler, potansiyel müşteri ve fırsatlar, fiyatlandırma verileri, pazar ve rakip gelişmeleri, kapasite kullanımı, stok durumu, tedarik ve termin kısıtları ile bütçe verileri, tanımlı raporlama dönemi ve onaylı veri kaynakları esas alınarak toplanır. Verilerin güncelliği, bütünlüğü ve tutarlılığı ilgili sorumlular tarafından kontrol edilir; tespit edilen eksiklik ve uyumsuzluklar giderilerek pazarlama analizlerine esas oluşturacak doğrulanmış veri seti hazırlanır.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – Pazarlama Uzmanı\nR – Ürün Grubu Satış Sorumluları\nC – İlgili Fabrika Müdürleri\nC – Planlama ve Üretim birimleri\nI – Genel Müdür Yardımcısı",
                "ilgili_dokumanlar": "Kapasite Kullanım Raporu, Bütçe ve Kârlılık Raporları, Satış Raporu, Devam Eden Projeler Listesi, Pazar, Rakip ve Müşteri Verileri",
                "dijital_platformlar": "NETSİS, Office/Excel, EBA, DocHuman, EBA – CRM, Power BI",
                "karar_adimi_mi": False,
                "faz": "FAZ1"
            },
            {
                "adim_no": 2,
                "baslik": "Hedef ülke ve pazarların analiz edilmesi, puanlanması ve önceliklendirilmesi",
                "faaliyet_tanimi": "Birinci adımda oluşturulan doğrulanmış veri seti; ülke seçim ve hedef pazar metodolojileri doğrultusunda pazar büyüklüğü, müşteri potansiyeli, ürün grubu uyumu, ciro, büyüme ve kârlılık potansiyeli, rekabet koşulları, ticari ve finansal riskler ile pazara erişim kriterleri esas alınarak analiz edilir ve puanlanır. Değerlendirme sonuçlarına göre potansiyel ülke ve pazarlar; Birincil Pazarlar, İkincil Pazarlar, Stratejik Aday Pazarlar ve İzleme Pazarları olarak sınıflandırılır. Belirlenen öncelikler ilgili kayıtlara işlenerek üçüncü adımda gerçekleştirilecek detaylı ülke ve müşteri analizlerine girdi oluşturur.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – Pazarlama Uzmanı\nC – Ürün Grubu Satış Sorumluları\nC – İlgili Fabrika Müdürleri\nI – Genel Müdür Yardımcısı\nI – Genel Müdür",
                "ilgili_dokumanlar": "Teleset Ülke Seçim Metodolojisi, Hedef Pazar Metodolojisi ve Puanlama Tablosu, Teleset Ülke Stratejileri, Potansiyel Ülkeler Analizi",
                "dijital_platformlar": "NETSİS, Office/Excel, Office/Word ve PowerPoint, EBA, DocHuman, EBA – CRM",
                "karar_adimi_mi": False,
                "faz": "FAZ1"
            },
            {
                "adim_no": 3,
                "baslik": "Önceliklendirilen ülke ve pazarlara yönelik detaylı analizlerin yapılması",
                "faaliyet_tanimi": "İkinci adımda önceliklendirilen ülke ve pazarlara ilişkin SWOT analizleri ve ülke kartları hazırlanır veya güncellenir. Pazar yapısı, ürün grubu fırsatları, rekabet koşulları, ticari riskler ve pazara giriş koşulları detaylı olarak değerlendirilir. Mevcut ve potansiyel müşteriler; ürün grubu uyumu, mevcut ve potansiyel ciro, gelişim fırsatı, ticari öncelik ve stratejik önem kriterleri doğrultusunda analiz edilir. Değerlendirme sonuçlarına göre hedef müşteriler ve fırsatlar önceliklendirilerek ilgili kayıtlara işlenir ve pazarlama faaliyet ve bütçe planı taslağına girdi oluşturur.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – Pazarlama Uzmanı\nR – Ürün Grubu Satış Sorumluları\nC – İlgili Fabrika Müdürleri\nI – Genel Müdür Yardımcısı\nI – Genel Müdür",
                "ilgili_dokumanlar": "Ülke SWOT Analizleri, Ülke Kartları, Potansiyel Müşteriler Analizi, Müşteri Bazlı Ciro Dağılımı, Müşteri Hesap Planları (Account Plan), Teleset Ülke Stratejileri",
                "dijital_platformlar": "NETSİS, Office/Excel, Power BI, Office/Word ve PowerPoint, EBA, EBA-CRM, DocHuman",
                "karar_adimi_mi": False,
                "faz": "FAZ1"
            },
            {
                "adim_no": 4,
                "baslik": "Pazarlama faaliyet ve bütçe planı taslağının hazırlanması",
                "faaliyet_tanimi": "Önceliklendirilen ülke, pazar ve hedef müşteriler doğrultusunda gerçekleştirilecek pazarlama faaliyetleri ile fuar, etkinlik, müşteri ziyareti ve diğer tanıtım çalışmaları planlanır. Her faaliyet için hedef ülke ve müşteri, ilgili ürün grubu, uygulama dönemi, katılım şekli, tahmini bütçe ve beklenen kazanım belirlenir. Pazarlama Uzmanı tarafından hazırlanan faaliyet ve bütçe planı taslağı, değerlendirilmek üzere Satış ve Pazarlama Müdürüne sunulur.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – Pazarlama Uzmanı\nC – Ürün Grubu Satış Sorumluları\nC – İlgili Fabrika Müdürleri",
                "ilgili_dokumanlar": "Fuar ve Etkinlik Planı/Takvimi, Satış ve Pazarlama Tahmini Bütçe ve Faaliyet Planı",
                "dijital_platformlar": "NETSİS, Office/Excel, EBA, EBA-CRM, DocHuman",
                "karar_adimi_mi": False,
                "faz": "FAZ1"
            },
            {
                "adim_no": 5,
                "baslik": "Pazarlama faaliyet ve bütçe planı taslağının değerlendirilmesi ve onaya hazırlanması",
                "faaliyet_tanimi": "Pazarlama Uzmanı tarafından hazırlanan pazarlama faaliyet ve bütçe planı taslağı; hedef ülke, pazar ve müşteri öncelikleri, faaliyet kapsamı, zamanlama, beklenen kazanım ve bütçe uygunluğu açısından Satış ve Pazarlama Müdürü tarafından değerlendirilir. Gerekli görülen değişiklikler Pazarlama Uzmanı tarafından gerçekleştirilir. Uygun bulunan plan, üst yönetim onayına sunulmak üzere hazırlanır.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – Pazarlama Uzmanı\nC – Ürün Grubu Satış Sorumluları\nC – İlgili Fabrika Müdürleri",
                "ilgili_dokumanlar": "Fuar ve Etkinlik Planı/Takvimi, Satış ve Pazarlama Tahmini Bütçe ve Faaliyet Planı, EBA Görüş ve Onay Kaydı",
                "dijital_platformlar": "NETSİS, Office/Excel, EBA, EBA-CRM, DocHuman",
                "karar_adimi_mi": False,
                "faz": "FAZ1"
            },
            {
                "adim_no": 6,
                "baslik": "Pazarlama faaliyet ve bütçe planı uygun mu?",
                "faaliyet_tanimi": "Beşinci adımda gözden geçirilerek üst yönetim onayına hazır hâle getirilen pazarlama faaliyet ve bütçe planı; hedef ülke, pazar ve müşteri öncelikleri, faaliyet kapsamı, zamanlama, beklenen kazanım ve bütçe uygunluğu açısından değerlendirilir. Uygun bulunan plan, ilgili üst yönetim onayıyla yürürlüğe alınarak yedinci adıma aktarılır. Uygun bulunmayan plan, revizyon gerekçeleri kaydedilerek yeniden hazırlanmak üzere dördüncü adıma yönlendirilir.",
                "sorumlular_raci": "A – Yetki seviyesine göre Genel Müdür Yardımcısı veya Genel Müdür\nR – Satış ve Pazarlama Müdürü\nC – Pazarlama Uzmanı\nC – İlgili Fabrika Müdürleri\nI – Ürün Grubu Satış Sorumluları",
                "ilgili_dokumanlar": "Fuar ve Etkinlik Planı/Takvimi, Satış ve Pazarlama Tahmini Bütçe ve Faaliyet Planı, EBA Görüş ve Onay Kaydı",
                "dijital_platformlar": "Office/Excel, EBA, DocHuman",
                "karar_adimi_mi": True,
                "faz": "FAZ1"
            },
            {
                "adim_no": 7,
                "baslik": "Hedef müşteriyle ilk temasın kurulması ve kurumsal tanıtımın gerçekleştirilmesi",
                "faaliyet_tanimi": "Onaylanan pazarlama faaliyet planında yer alan hedef ülkelerdeki potansiyel müşterilerle e-posta, telefon, dijital kanallar, fuarlar veya müşteri ziyaretleri aracılığıyla ilk temas kurulur. Teleset’in kurumsal yapısı ile ilgili ürün grubunun kabiliyetleri, onaylı ve güncel tanıtım materyalleri kullanılarak müşteriye aktarılır. Görüşme tarihi, iletişim kanalı, müşteri ilgisi, ilgili ürün grubu, görüşme sonucu ve planlanan sonraki aksiyon EBA-CRM’e kaydedilerek takip edilir.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – Pazarlama Uzmanı\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Fabrika Müdürü — teknik destek gerektiğinde\nC – Marka Yöneticisi — kurumsal tanıtım materyalleri açısından\nI – Genel Müdür Yardımcısı — yalnızca stratejik veya kritik müşteri temaslarında",
                "ilgili_dokumanlar": "Potansiyel Müşteriler Analizi/Listesi, Fuar ve Etkinlik Planı/Takvimi, Şirket ve Ürün Grubu Sunumları, Broşür, Katalog ve Tanıtım Filmleri, E-posta/Görüşme Kaydı",
                "dijital_platformlar": "Office/Outlook, EBA-CRM, DocHuman, Kurumsal web sitesi, Onaylı dijital iletişim kanalları",
                "karar_adimi_mi": False,
                "faz": "FAZ2"
            },
            {
                "adim_no": 8,
                "baslik": "Potansiyel müşteri talep ve beklentilerinin alınması ve ön değerlendirilmesi",
                "faaliyet_tanimi": "Potansiyel müşterinin ürün ve hizmet beklentileri ile teknik, kalite, teslimat ve ticari talepleri, Müşteri İletişim Talimatı’na uygun olarak alınır. Talep; müşteri, iletişim kişisi, tarih, iletişim kanalı, talep türü, öncelik ve açıklama bilgileriyle EBA-CRM’e kaydedilerek ilgili ürün grubu satış sorumlusuna ve değerlendirmeyi yapacak birimlere yönlendirilir. İlgili birimler tarafından ürün kabiliyeti, kapasite, kalite, teslimat, lojistik ve ticari koşullar açısından ön değerlendirme yapılır. Değerlendirme sonuçları ve gerekli aksiyonlar EBA-CRM üzerinden kayıt altına alınarak takip edilir.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – Pazarlama Uzmanı\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Fabrika Müdürü\nC – İlgili birim yöneticileri — Proje, Kalite, Planlama ve Lojistik\nI – Genel Müdür Yardımcısı — yalnızca stratejik veya kritik taleplerde",
                "ilgili_dokumanlar": "Müşteri İletişim Talimatı, Müşteri tarafından iletilen e-posta, portal kaydı ve ilgili belgeler, Ürün Üretilebilirlik Analizi – PMG-EK-002",
                "dijital_platformlar": "Office/Outlook, Office/Excel, EBA-CRM, DocHuman, Müşteri portalları ve yetkilendirilmiş dijital iletişim kanalları",
                "karar_adimi_mi": False,
                "faz": "FAZ2"
            },
            {
                "adim_no": 9,
                "baslik": "Müşteriyle talep ve beklentileri karşılanabilir mi?",
                "faaliyet_tanimi": "Ön değerlendirme sonuçları esas alınarak müşteri talep ve beklentilerinin ürün kabiliyeti, kapasite, kalite, teslimat, lojistik ve ticari koşullar çerçevesinde karşılanabilirliği değerlendirilerek karara bağlanır. Değerlendirme sonucu; olumlu, koşullu veya olumsuz olarak, gerekçesi ve varsa karşılanması gereken koşullarla birlikte EBA-CRM’e kaydedilir. İlave bilgi veya yeniden değerlendirme gereken talepler 8. adıma geri yönlendirilir. Değerlendirmesi tamamlanan talepler ise sonuç olumlu, koşullu veya olumsuz olmasına bakılmaksızın müşteriye bildirilmek üzere 10. adıma aktarılır.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – Pazarlama Uzmanı\nC – İlgili Fabrika Müdürü\nC – Değerlendirmeyi yapan ilgili birim yöneticileri — Proje, Kalite, Planlama ve Lojistik\nI – Genel Müdür Yardımcısı — stratejik veya yüksek riskli taleplerde",
                "ilgili_dokumanlar": "Müşteri İletişim Talimatı, Ürün Üretilebilirlik Analizi – PMG-EK-002, Müşteri tarafından iletilen teknik ve ticari belgeler",
                "dijital_platformlar": "Office/Excel, Office/Outlook, EBA-CRM, DocHuman",
                "karar_adimi_mi": True,
                "faz": "FAZ2"
            },
            {
                "adim_no": 10,
                "baslik": "Değerlendirme sonucunun müşteriye bildirilmesi ve geri bildirimin alınması",
                "faaliyet_tanimi": "Dokuzuncu adımda alınan değerlendirme sonucu; karşılanabilecek kapsam, varsa uygulanması gereken koşullar, ihtiyaç duyulan ilave bilgi ve belgeler ile planlanan sonraki adımlar belirtilerek müşteriye yazılı olarak bildirilir. Müşteriden alınan geri bildirim, talep edilen değişiklikler ve taraflarca mutabık kalınan hususlar EBA-CRM’e kaydedilir. Müşterinin talep ettiği değişikliklerin yeniden teknik veya ticari değerlendirme gerektirmesi durumunda 8. adıma geri dönülür. İlave değerlendirme gerektirmeyen geri bildirimler ise karşılıklı ön mutabakatın değerlendirilmesi amacıyla 11. adıma aktarılır.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – Pazarlama Uzmanı\nC – İlgili Fabrika Müdürü\nC – Değerlendirmeye katılan ilgili birim yöneticileri — Proje, Kalite, Planlama ve Lojistik\nI – Genel Müdür Yardımcısı — stratejik veya yüksek riskli taleplerde",
                "ilgili_dokumanlar": "Müşteri İletişim Talimatı, E-posta veya Toplantı Notu, Müşteri Portalı Kaydı, Müşteri tarafından iletilen bilgi ve belgeler",
                "dijital_platformlar": "Office/Outlook, Office/Excel, EBA-CRM, Müşteri portalı ve yetkilendirilmiş iletişim kanalları, DocHuman",
                "karar_adimi_mi": True,
                "faz": "FAZ2"
            },
            {
                "adim_no": 11,
                "baslik": "Müşteri ile karşılıklı ön mutabakat sağlandı mı?",
                "faaliyet_tanimi": "Onuncu adımda müşteriye bildirilen değerlendirme sonucu ve müşteriden alınan geri bildirim esas alınarak; tarafların sunulabilecek ürün veya hizmet kapsamı, temel teknik ve ticari koşullar ile sonraki aşamaya geçilmesi konusunda ön mutabakat sağlayıp sağlamadığı değerlendirilir. Alınan karar, gerekçesi, varsa mutabık kalınan koşullar ve fırsatın güncel durumu EBA-CRM’e kaydedilir. İlave bilgi veya yeniden teknik ya da ticari değerlendirme gerekmesi durumunda 8. adıma geri dönülür. Ön mutabakat sağlanamaması durumunda 15. adıma geçilerek süreç kapatılır. Ön mutabakat sağlanması durumunda ise RFQ öncesi müşteri tedarikçi değerlendirmesi gerekliliğinin belirlenmesi amacıyla 12. adıma geçilir.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – Pazarlama Uzmanı\nC – İlgili Fabrika Müdürü\nC – Değerlendirmeye katılan ilgili birim yöneticileri — Proje, Kalite, Planlama ve Lojistik\nI – Genel Müdür Yardımcısı — stratejik veya kritik müşteri fırsatlarında",
                "ilgili_dokumanlar": "Müşteri İletişim Talimatı, E-posta veya Toplantı Notu, Müşteri Portalı ve Geri Bildirim Kayıtları, Ürün Üretilebilirlik Analizi – PMG-EK-002",
                "dijital_platformlar": "Office/Outlook, Office/Excel, EBA-CRM, Müşteri portalı ve yetkilendirilmiş iletişim kanalları, DocHuman",
                "karar_adimi_mi": True,
                "faz": "FAZ3"
            },
            {
                "adim_no": 12,
                "baslik": "RFQ öncesinde müşterinin tedarikçi değerlendirmesi gerekli mi?",
                "faaliyet_tanimi": "On birinci adımda ön mutabakat sağlanan müşteri için Teleset’in mevcut tedarikçi onay durumu ve onayın geçerliliği kontrol edilir. Müşteri tarafından RFQ öncesinde tedarikçi değerlendirmesi, belge paylaşımı, denetim, tesis ziyareti veya başka bir kabul süreci talep edilip edilmediği belirlenir. Tedarikçi değerlendirmesi gerekli ise karar ve müşteri gereklilikleri EBA-CRM’e kaydedilerek 13. adıma geçilir. Geçerli tedarikçi onayının bulunması veya müşteri tarafından RFQ öncesinde değerlendirme talep edilmemesi durumunda doğrudan Ürün Teklif Sürecine geçilir.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – Pazarlama Uzmanı\nC – İlgili Fabrika Müdürü\nC – Kalite/EYS Birimi\nI – Genel Müdür Yardımcısı — yalnızca stratejik veya kritik müşterilerde",
                "ilgili_dokumanlar": "Müşteri Tedarikçi Değerlendirme/Kabul Koşulları, Müşteri Portalı veya E-posta Kayıtları, Mevcut Denetim ve Onay Kayıtları, Müşteri Denetim Soru Listesi",
                "dijital_platformlar": "Office/Outlook, Office/Excel, Müşteri portalı, EBA, EBA-CRM, DocHuman",
                "karar_adimi_mi": True,
                "faz": "FAZ3"
            },
            {
                "adim_no": 13,
                "baslik": "Müşterinin tedarikçi değerlendirme ve onay sürecinin yürütülmesi",
                "faaliyet_tanimi": "On ikinci adımda gerekli olduğu belirlenen tedarikçi değerlendirme süreci kapsamında müşterinin talep ettiği firma bilgileri, formlar, sertifikalar, politikalar ile teknik ve ticari belgeler ilgili birimlerden temin edilir. Belgelerin güncelliği, doğruluğu, gizlilik seviyesi ve paylaşım yetkisi kontrol edildikten sonra müşteriye iletilir. Müşteri tarafından talep edilen denetim, tesis ziyareti veya değerlendirme toplantıları ilgili birimlerin katılımıyla koordine edilir. Tespit edilen bulgu ve uygunsuzluklar kayıt altına alınarak gerekli aksiyonlar belirlenir ve sonuçlanıncaya kadar takip edilir. Tedarikçi değerlendirmesi tamamlandığında, müşteri kararının değerlendirilmesi amacıyla 14. adıma geçilir.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nR – Kalite/EYS Birimi\nC – Pazarlama Uzmanı\nC – İlgili Fabrika Müdürü\nC – Talep edilen belge veya aksiyonun sahibi ilgili birimler\nI – Genel Müdür Yardımcısı — stratejik müşteri veya kritik denetimlerde",
                "ilgili_dokumanlar": "SAG-EK-006 Firma Tanıtım Bilgi Formu, Müşteri İletişim Talimatı, Müşteri Tedarikçi Değerlendirme Formu/Anketi, Geçerli Sertifika, Politika ve Kontrollü Şirket Dokümanları, Denetim veya Ziyaret Kayıtları, Müşteri Portalı ve Geri Bildirim Kayıtları",
                "dijital_platformlar": "Office/Outlook, Office/Word ve Excel, EBA, EBA-CRM, DocHuman, Müşteri portalı",
                "karar_adimi_mi": False,
                "faz": "FAZ4"
            },
            {
                "adim_no": 14,
                "baslik": "Müşterinin tedarikçi değerlendirme süreci olumlu sonuçlandı mı?",
                "faaliyet_tanimi": "Müşteriye iletilen bilgi ve belgeler, gerçekleştirilen denetim veya ziyaretler ile varsa bulgulara ilişkin aksiyonların sonuçları esas alınarak müşterinin tedarikçi değerlendirme kararı takip edilir. Müşteriden alınan onay, koşullu onay veya olumsuz değerlendirme sonucu; karar tarihi, gerekçesi ve varsa yerine getirilmesi gereken koşullarla birlikte EBA-CRM’e kaydedilir. Değerlendirmenin olumlu sonuçlanması veya koşullu onayın teklif aşamasına geçilmesine izin vermesi durumunda Ürün Teklif Sürecine geçilir. Koşullu onaya ilişkin aksiyonların teklif aşamasından önce tamamlanmasının gerekmesi durumunda 13. adıma geri dönülür. Değerlendirmenin olumsuz sonuçlanması durumunda ise 15. adıma geçilerek süreç kapatılır.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nR – Kalite/EYS Birimi\nC – Pazarlama Uzmanı\nC – İlgili Fabrika Müdürü\nC – Bulguyla ilgili diğer birimler\nI – Genel Müdür Yardımcısı — stratejik veya kritik müşterilerde",
                "ilgili_dokumanlar": "Müşteri Tedarikçi Değerlendirme/Onay Bildirimi, Denetim veya Ziyaret Raporu, Bulgu ve Aksiyon Kapanış Kayıtları, Müşteri Portalı veya E-posta Kaydı",
                "dijital_platformlar": "Office/Outlook, Office/Excel, EBA, EBA-Uygunsuzluk Modülü, EBA-CRM, DocHuman, Müşteri portalı",
                "karar_adimi_mi": True,
                "faz": "FAZ4"
            },
            {
                "adim_no": 15,
                "baslik": "Sürecin kapatılması ve sonuçların raporlanması",
                "faaliyet_tanimi": "On birinci adımda müşteriyle ön mutabakat sağlanamaması veya on dördüncü adımda müşterinin tedarikçi değerlendirmesinin olumsuz sonuçlanması durumunda; fırsatın kapanış nedeni, kapanış tarihi, müşteri geri bildirimi ve sürecin güncel durumu EBA-CRM’e kaydedilerek pazarlama süreci kapatılır. Olumsuz sonuca yol açan nedenler ve varsa süreç içerisinde tespit edilen bulgu ve uygunsuzluklar ilgili birimlerle değerlendirilir. Gerekli aksiyonlar EBA üzerinden sonuçlanıncaya kadar takip edilir; elde edilen öğrenilmiş dersler kayıt altına alınır. Elde edilen sonuçlar raporlanır ve sonraki pazarlama planlama dönemine girdi oluşturur.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – Pazarlama Uzmanı\nC – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Fabrika Müdürü\nC – Kalite/EYS Birimi\nC – Bulguyla ilgili diğer birimler\nI – Genel Müdür Yardımcısı — stratejik veya kritik müşterilerde",
                "ilgili_dokumanlar": "EBA-CRM Fırsat Kaydı ve Kapanış Bilgileri, EBA Uygunsuzluk/Aksiyon Kaydı, EBA Öğrenilmiş Ders Kaydı",
                "dijital_platformlar": "EBA-CRM, EBA-Uygunsuzluk Modülü, EBA-Öğrenilmiş Ders Modülü, Office/Excel, DocHuman",
                "karar_adimi_mi": False,
                "faz": "FAZ4"
            }
        ]

        for veri in adilar:
            adim_obj, created = SurecAdimTanimi.objects.update_or_create(
                adim_no=veri["adim_no"],
                defaults=veri
            )
            action = "Oluşturuldu" if created else "Güncellendi"
            self.stdout.write(self.style.SUCCESS(f"Adım {adim_obj.adim_no}: {adim_obj.baslik} -> {action}"))

        self.stdout.write(self.style.SUCCESS("\n15 Adımlık Pazarlama Süreci Master Verileri Başarıyla Yüklendi!"))
