from django.core.management.base import BaseCommand
from crm_takip.models import UrunTeklifAdimTanimi

class Command(BaseCommand):
    help = "16 Adımlık Teleset Ürün Teklif Süreci ve Alt Dallanma Master Verilerini Yükler"

    def handle(self, *args, **options):
        adilar = [
            # FAZ 1: RFQ Alımı & Ön Fizibilite (Adım 1 - 4C)
            {
                "sira_no": 1,
                "adim_kodu": "1",
                "adim_no": 1,
                "baslik": "RFQ/Teklif Talebinin Alınması ve Ön Kontrolü",
                "faaliyet_tanimi": "Pazarlama Sürecinden aktarılan veya müşteri tarafından doğrudan iletilen RFQ/teklif talebi, ilgili Ürün Grubu Satış Sorumlusu tarafından alınır. Talebin; müşteri ve varsa RFQ referansı, ilgili ürün grubu, talep tarihi, teklif teslim tarihi, tahmini sipariş miktarı/forecast bilgileri, proje süresi, teknik resim ve şartname revizyonları, kalite ve numune gereklilikleri ile ticari ve lojistik koşullar açısından ön kontrolü yapılır. Eksik veya açıklığa kavuşturulması gereken bilgiler belirlenerek müşteriden tamamlanması talep edilir. Teklif çalışmasının başlatılması için gerekli asgari bilgiler tamamlandığında 2. adıma geçilir.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – Pazarlama Uzmanı — Pazarlama Sürecinden aktarılan taleplerde\nC – İlgili Ürün Grubu Proje Sorumlusu — teknik dokümanların ön kontrolünün gerekli olduğu durumlarda\nI – Genel Müdür Yardımcısı — yalnızca stratejik veya kritik taleplerde",
                "ilgili_dokumanlar": "Müşteri RFQ/Teklif Talebi, Teknik Resim, Teknik Şartname ve varsa BOM, Müşteri Sözleşmesi veya Çerçeve Anlaşma, EBA – Teklif & Ürün Devreye Alma Kaydı",
                "dijital_platformlar": "Müşteri portalı, Outlook, EBA-CRM, EBA – Teklif & Ürün Devreye Alma",
                "karar_adimi_mi": False,
                "ana_adim_mi": True,
                "faz": "FAZ1"
            },
            {
                "sira_no": 2,
                "adim_kodu": "2",
                "adim_no": 2,
                "baslik": "Teklif Kaydının Tamamlanması",
                "faaliyet_tanimi": "1. adımda açılan EBA – Teklif & Ürün Devreye Alma kaydı; müşteri ve varsa RFQ referansı, talep kaynağı, ilgili ürün grubu, talep ve hedef teklif tarihleri, tahmini sipariş miktarı/forecast bilgileri, proje süresi ve mevcut dokümanlarla tamamlanır. Kayıt tamamlandıktan sonra teklif türünün belirlenmesi için 3. adıma geçilir.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – Pazarlama Uzmanı — Pazarlama Sürecinden aktarılan taleplerde\nC – İlgili Ürün Grubu Proje Sorumlusu — teknik değerlendirme gerektiren taleplerde\nI – İlgili Fabrika Müdürü — ön fizibilite gerektirecek taleplerde\nI – Genel Müdür Yardımcısı — yalnızca stratejik veya kritik taleplerde",
                "ilgili_dokumanlar": "Müşteri RFQ/Teklif Talebi, Teknik Resim, Teknik Şartname ve varsa BOM, Müşteri Sözleşmesi veya Çerçeve Anlaşma, EBA – Teklif & Ürün Devreye Alma Kaydı, EBA-CRM RFQ, Netsis Mevcut Ürün ve Fiyat Kayıtları, Teleset Fiyatlama Süreç Talimatı",
                "dijital_platformlar": "EBA – Teklif & Ürün Devreye Alma, EBA-CRM, Netsis, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": True,
                "faz": "FAZ1"
            },
            {
                "sira_no": 3,
                "adim_kodu": "3",
                "adim_no": 3,
                "baslik": "Teklif Talebinin Türü Nedir?",
                "faaliyet_tanimi": "Teklif talebi; müşterinin ve ürünün mevcut durumu ile talebin teknik değişiklik içerip içermediği dikkate alınarak sınıflandırılır. Yeni müşteriden gelen talepler, ürün mevcut veya benzer olsa dahi yeni müşteri/proje kapsamında değerlendirilir. Belirlenen teklif türü EBA-CRM ve EBA – Teklif & Ürün Devreye Alma üzerinde kayıt altına alınarak ilgili süreç adımına yönlendirilir:\n1- Mevcut müşteri – mevcut ürün fiyat revizyonu -> 3A\n2- Mevcut müşteri – yeni/revize ürün veya proje -> 3B\n3- Yeni müşteri – ürün veya proje teklifi -> 3C",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Ürün Grubu Proje Sorumlusu — teknik teyit gerektiren durumlarda\nC – Pazarlama Uzmanı — yeni müşteri taleplerinde\nI – İlgili Fabrika Müdürü — 3B ve 3C kapsamındaki taleplerde\nI – Genel Müdür Yardımcısı — yalnızca stratejik veya kritik taleplerde",
                "ilgili_dokumanlar": "Müşteri RFQ/Teklif Talebi, Teknik Resim, Teknik Şartname ve varsa BOM, Müşteri Sözleşmesi veya Çerçeve Anlaşma, EBA – Teklif & Ürün Devreye Alma Kaydı, EBA-CRM RFQ, Netsis Mevcut Ürün ve Fiyat Kayıtları, Teleset Fiyatlama Süreç Talimatı",
                "dijital_platformlar": "EBA-CRM, EBA – Teklif & Ürün Devreye Alma, Netsis, DocHuman",
                "karar_adimi_mi": True,
                "ana_adim_mi": True,
                "faz": "FAZ1"
            },
            {
                "sira_no": 4,
                "adim_kodu": "3A",
                "adim_no": 3,
                "baslik": "Mevcut Ürün Fiyat Revizyonu Kapsamının Belirlenmesi",
                "faaliyet_tanimi": "Mevcut ürün fiyat revizyonunun gerekçesi; müşteri talebi, sözleşme hükümleri, hammadde veya endeks değişimleri, döviz kuru, işçilik, enerji, lojistik, genel gider, verimlilik taahhüdü ya da diğer ticari koşullar dikkate alınarak belirlenir. Revizyondan etkilenen ürün kodları, mevcut fiyatlar, referans parametreler, uygulanacak fiyatlandırma yöntemi ve talep edilen geçerlilik tarihi kontrol edilerek EBA üzerinde kayıt altına alınır. Talebin teknik değişiklik içerdiğinin tespiti hâlinde 3B adımına, teknik değişiklik bulunmaması hâlinde ise 5. adıma geçilir.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – Bütçe Kontrol ve Dijital Dönüşüm\nC – İlgili Fabrika Müdürü — üretim maliyeti değişikliklerinde\nC – İlgili Ürün Grubu Proje Sorumlusu — teknik değişiklik teyidinde",
                "ilgili_dokumanlar": "Müşteri Fiyat Revizyon Talebi, Mevcut Onaylı Fiyat Listesi / Son Teklif, Müşteri Sözleşmesi, Endeks ve Döviz Kuru Kayıtları, Netsis Mevcut Ürün ve Fiyat Kayıtları, EBA – Teklif & Ürün Devreye Alma Kaydı",
                "dijital_platformlar": "EBA – Teklif & Ürün Devreye Alma, EBA-CRM, Netsis, Excel, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ1"
            },
            {
                "sira_no": 5,
                "adim_kodu": "3B",
                "adim_no": 3,
                "baslik": "Mevcut Müşteri – Yeni/Revize Ürün veya Proje Ön Fizibilitesinin Yapılması",
                "faaliyet_tanimi": "Mevcut müşteriden gelen yeni veya revize ürün/proje talebi, Ürün Grubu Proje Sorumlusu koordinasyonunda ilgili birimlerin katılımıyla değerlendirilir. Ürünün teknik uygulanabilirliği; teknik resim ve BOM, malzeme, proses, makine ve ekipman, kalıp/aparat, kapasite, yatırım, kalite ve test gereklilikleri, numune koşulları, ambalajlama ve termin açısından incelenir. Tespit edilen ihtiyaçlar, riskler, eksik bilgiler ve ilgili birim görüşleri EBA Ön Fizibilite Kaydı üzerinde dokümante edilerek 4. adıma geçilir.",
                "sorumlular_raci": "A – İlgili Fabrika Müdürü\nR – İlgili Ürün Grubu Proje Sorumlusu\nC – İlgili Ürün Grubu Satış Sorumlusu\nC – Üretim, Kalite, Planlama, Satın Alma ve teknik birimler\nI – Satış ve Pazarlama Müdürü\nI – Genel Müdür Yardımcısı — stratejik veya kritik projelerde",
                "ilgili_dokumanlar": "Müşteri RFQ/Teklif Talebi, Teknik Resim, Teknik Şartname ve BOM, PMG-EK-002 Ürün Üretebilirlik Analizi, EBA Ön Fizibilite Kaydı, Yeni Ürün Devreye Alma Talimatı, Netsis Ürün/BOM Kayıtları",
                "dijital_platformlar": "EBA – Teklif & Ürün Devreye Alma, EBA-CRM, Netsis, Excel, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ1"
            },
            {
                "sira_no": 6,
                "adim_kodu": "3C",
                "adim_no": 3,
                "baslik": "Yeni Müşteri – Ürün/Proje Ön Değerlendirmesi ve Teknik Ön Fizibilitesinin Yapılması",
                "faaliyet_tanimi": "Yeni müşteriye ilişkin müşteri ve fırsat bilgileri; Pazarlama Sürecinden aktarılan kayıtlar veya doğrudan alınan RFQ talebi üzerinden değerlendirilir. Faaliyet alanı, pazar bilgileri, talep potansiyeli, proje süresi, ticari koşullar ve Teleset stratejisine uygunluğu EBA-CRM'e kaydedilir. Uygun bulunan talepler için teknik ön fizibilite gerçekleştirilir. Uygun bulunmayan talepler gerekçesiyle 16. adıma (Kapatma), uygun bulunanlar ise 4. adıma aktarılır.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nR – İlgili Ürün Grubu Proje Sorumlusu — teknik fizibilitede\nC – Pazarlama Uzmanı\nC – İlgili Fabrika Müdürü\nC – Üretim, Kalite, Planlama, Satın Alma ve teknik birimler\nI – Genel Müdür Yardımcısı",
                "ilgili_dokumanlar": "Müşteri RFQ Talebi, Teknik Resim, BOM, EBA Ön Fizibilite Kaydı, EBA-CRM Müşteri/Fırsat Kaydı, PMG-EK-002 Ürün Üretebilirlik Analizi",
                "dijital_platformlar": "EBA-CRM, EBA – Teklif & Ürün Devreye Alma, Netsis, Excel, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ1"
            },
            {
                "sira_no": 7,
                "adim_kodu": "4",
                "adim_no": 4,
                "baslik": "Ön Fizibilite Sonucu Nedir?",
                "faaliyet_tanimi": "Hazırlanan EBA Ön Fizibilite Kaydı, ilgili Fabrika Müdürü tarafından teknik uygulanabilirlik, kapasite, yatırım, kalite, numune, termin ve riskler açısından değerlendirilir. Değerlendirme sonucu EBA üzerinde kayıt altına alınır. Stratejik projelerde Genel Müdür Yardımcısının görüşü alınır. Sonuca göre 4A (Onay), 4B (Uygun Değil) veya 4C (İlave Çalışma) adımına geçilir.",
                "sorumlular_raci": "A – İlgili Fabrika Müdürü\nR – İlgili Ürün Grubu Proje Sorumlusu\nC – İlgili Ürün Grubu Satış Sorumlusu\nC – Teknik birimler\nC – Genel Müdür Yardımcısı — stratejik projelerde\nI – Satış ve Pazarlama Müdürü",
                "ilgili_dokumanlar": "EBA Ön Fizibilite Kaydı, PMG-EK-002 Ürün Üretebilirlik Analizi, Müşteri RFQ/Teklif Talebi, Teknik Resim ve BOM, Birim Görüş Kayıtları",
                "dijital_platformlar": "EBA – Teklif & Ürün Devreye Alma, EBA-CRM, DocHuman",
                "karar_adimi_mi": True,
                "ana_adim_mi": True,
                "faz": "FAZ1"
            },
            {
                "sira_no": 8,
                "adim_kodu": "4A",
                "adim_no": 4,
                "baslik": "Ön Fizibilitenin Onaylanması ve Maliyet Çalışmasına Aktarılması",
                "faaliyet_tanimi": "Ön fizibilitenin uygun bulunması durumunda EBA Ön Fizibilite Kaydı Fabrika Müdürü tarafından onaylanır. Onaylanan teknik kapsam, kapasite/yatırım varsayımları ile kalite ve termin koşulları kayıt altına alınır. Teklif dosyası 5. Maliyet ve Fiyatlandırma Verilerinin Hazırlanması adımına aktarılır.",
                "sorumlular_raci": "A – İlgili Fabrika Müdürü\nR – İlgili Ürün Grubu Proje Sorumlusu\nC – İlgili Ürün Grubu Satış Sorumlusu\nI – Satış ve Pazarlama Müdürü",
                "ilgili_dokumanlar": "EBA Ön Fizibilite Kaydı",
                "dijital_platformlar": "EBA – Teklif & Ürün Devreye Alma, EBA-CRM",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ1"
            },
            {
                "sira_no": 9,
                "adim_kodu": "4B",
                "adim_no": 4,
                "baslik": "Uygun Olmayan Ön Fizibilitenin Sonuçlandırılması",
                "faaliyet_tanimi": "Ön fizibilitenin teknik, kapasite, yatırım veya kalite koşulları nedeniyle uygun bulunmaması hâlinde ret gerekçeleri EBA Ön Fizibilite Kaydına işlenir. Alternatif çözüm varsa 4C'ye, kesin ret kararı durumunda müşteri bilgilendirilerek süreç 16. adıma (Kapatma) aktarılır.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Fabrika Müdürü\nC – İlgili Ürün Grubu Proje Sorumlusu\nI – Genel Müdür Yardımcısı — kritik projelerde",
                "ilgili_dokumanlar": "Uygun Bulunmayan EBA Ön Fizibilite Kaydı, PMG-EK-002 Ürün Üretebilirlik Analizi, Teknik Ret Gerekçeleri, EBA-CRM RFQ Kaydı",
                "dijital_platformlar": "EBA – Teklif & Ürün Devreye Alma, EBA-CRM, Outlook, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ1"
            },
            {
                "sira_no": 10,
                "adim_kodu": "4C",
                "adim_no": 4,
                "baslik": "İlave Çalışma veya Bilginin Tamamlanması",
                "faaliyet_tanimi": "Ön fizibilite sonucunun netleşmesi için gerekli ilave teknik çalışma, doğrulama, müşteri bilgisi veya kapasite teyidi sorumlu birimler ve hedef tarihlerle EBA'ya kaydedilir. Aksiyonlar tamamlandığında EBA Ön Fizibilite Kaydı güncellenerek yeniden 4. adıma sunulur. Kapsam büyük ölçüde değiştiyse 3B/3C'ye dönülür.",
                "sorumlular_raci": "A – İlgili Fabrika Müdürü\nR – İlgili Ürün Grubu Proje Sorumlusu\nC – İlgili Ürün Grubu Satış Sorumlusu\nC – Teknik birimler\nI – Satış ve Pazarlama Müdürü",
                "ilgili_dokumanlar": "EBA Ön Fizibilite Kaydı, EBA Aksiyon Kayıtları, PMG-EK-002 Ürün Üretebilirlik Analizi, İlave Teknik Çalışma Kayıtları",
                "dijital_platformlar": "EBA – Teklif & Ürün Devreye Alma, EBA-CRM, Outlook, Excel, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ1"
            },

            # FAZ 2: Maliyet & Fiyatlandırma (Adım 5 - 9C)
            {
                "sira_no": 11,
                "adim_kodu": "5",
                "adim_no": 5,
                "baslik": "Maliyet ve Fiyatlandırma Verilerinin Hazırlanması",
                "faaliyet_tanimi": "Fiyatlandırmada kullanılacak malzeme, işçilik, makine, enerji, genel gider, fire, dış kaynak, ambalaj, lojistik, finansman ve yatırım/amortisman verileri temin edilir. Yeni/revize ürünlerde Proje Sorumlusu verileri iletir; fiyat revizyonlarında 3A kapsamı esas alınır. Veriler tamamlandıktan sonra 6. adıma geçilir.",
                "sorumlular_raci": "A – İlgili Fabrika Müdürü\nR – İlgili Ürün Grubu Proje Sorumlusu — yeni/revize ürünlerde\nR – İlgili Ürün Grubu Satış Sorumlusu — fiyat revizyonlarında ve ticari verilerde\nC – Bütçe Kontrol ve Dijital Dönüşüm\nC – Teknik ve idari birimler\nI – Satış ve Pazarlama Müdürü",
                "ilgili_dokumanlar": "Fiyatlandırma Veri ve Hesaplama Excel Şablonu, Onaylı EBA Ön Fizibilite Kaydı, Onaylı Teknik Resim/BOM, Tedarikçi Teklifleri, Netsis Kayıtları",
                "dijital_platformlar": "Netsis, Excel, EBA – Teklif & Ürün Devreye Alma, EBA-CRM, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": True,
                "faz": "FAZ2"
            },
            {
                "sira_no": 12,
                "adim_kodu": "6",
                "adim_no": 6,
                "baslik": "Toplam Birim Maliyetin Hesaplanması",
                "faaliyet_tanimi": "5. adım verileri kullanılarak ürünün toplam birim maliyeti, Fiyatlandırma Veri ve Hesaplama Excel Şablonu üzerinde hesaplanır (hammadde, işçilik, makine, enerji, GÜG, fire, dış kaynak, ambalaj, lojistik, finansman, amortisman). Bu adımda kâr marjı ve satış fiyatı belirlenmez. Hesaplama tamamlandıktan sonra 7. adıma geçilir.",
                "sorumlular_raci": "A – İlgili Fabrika Müdürü\nR – İlgili Ürün Grubu Proje Sorumlusu — yeni/revize ürünlerde\nR – İlgili Ürün Grubu Satış Sorumlusu — fiyat revizyonlarında\nC – Bütçe Kontrol ve Dijital Dönüşüm\nC – Üretim, Planlama, Satın Alma\nI – Satış ve Pazarlama Müdürü",
                "ilgili_dokumanlar": "Fiyatlandırma Veri ve Hesaplama Excel Şablonu, Maliyet Analiz Dosyaları, Onaylı BOM/Proses Bilgileri, Netsis Kayıtları",
                "dijital_platformlar": "Excel, Netsis, EBA – Teklif & Ürün Devreye Alma, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": True,
                "faz": "FAZ2"
            },
            {
                "sira_no": 13,
                "adim_kodu": "7",
                "adim_no": 7,
                "baslik": "Maliyet Hesaplaması Doğrulandı mı?",
                "faaliyet_tanimi": "Hazırlanan maliyet hesabı; BOM revizyonu, malzeme fiyatları, süreler, giderler, fire, ambalaj, lojistik, formüller, döviz kurları ve varsayımlar açısından kontrol edilir ve doğrulanır. Doğrulama sonucuna göre 7A (Doğrulandı) veya 7B (Düzeltme) adımına geçilir.",
                "sorumlular_raci": "A – İlgili Fabrika Müdürü\nR – Bütçe Kontrol ve Dijital Dönüşüm\nC – İlgili Ürün Grubu Proje Sorumlusu\nC – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili teknik birimler\nI – Satış ve Pazarlama Müdürü",
                "ilgili_dokumanlar": "Fiyatlandırma Veri ve Hesaplama Excel Şablonu, Maliyet Analiz Dosyaları, Maliyet Doğrulama/Onay Kaydı, EBA Ön Fizibilite Kaydı",
                "dijital_platformlar": "Excel, EBA – Teklif & Ürün Devreye Alma, Netsis, DocHuman",
                "karar_adimi_mi": True,
                "ana_adim_mi": True,
                "faz": "FAZ2"
            },
            {
                "sira_no": 14,
                "adim_kodu": "7A",
                "adim_no": 7,
                "baslik": "Doğrulanmış Maliyetin Fiyatlandırmaya Aktarılması",
                "faaliyet_tanimi": "Maliyet hesaplamasının doğru ve eksiksiz olduğu teyit edilerek onaylı maliyet verisi 8. Pazar/Proje Profilinin, Kârlılık Çarpanının ve Teklif Fiyatının Belirlenmesi adımına aktarılır.",
                "sorumlular_raci": "A – İlgili Fabrika Müdürü\nR – İlgili Ürün Grubu Proje Sorumlusu / Satış Sorumlusu\nC – Bütçe Kontrol ve Dijital Dönüşüm\nI – Satış ve Pazarlama Müdürü",
                "ilgili_dokumanlar": "Fiyatlandırma Veri ve Hesaplama Excel Şablonu, Maliyet Analiz Dosyaları, Onaylı BOM ve Operasyon Bilgileri",
                "dijital_platformlar": "Excel, Netsis, EBA – Teklif & Ürün Devreye Alma, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ2"
            },
            {
                "sira_no": 15,
                "adim_kodu": "7B",
                "adim_no": 7,
                "baslik": "Maliyet Hesaplamasının Düzeltilmesi",
                "faaliyet_tanimi": "Eksik veya hatalı olduğu belirlenen veriler ve hesaplamalar ilgili birimlerle birlikte düzeltilir. Güncellenen revize maliyet çalışması yeniden 7. adımda doğrulamaya sunulur.",
                "sorumlular_raci": "A – İlgili Fabrika Müdürü\nR – İlgili Ürün Grubu Proje Sorumlusu / Satış Sorumlusu\nC – Bütçe Kontrol ve Dijital Dönüşüm\nI – Satış ve Pazarlama Müdürü",
                "ilgili_dokumanlar": "Fiyatlandırma Veri ve Hesaplama Excel Şablonu, Maliyet Analiz Dosyaları, Netsis Kayıtları",
                "dijital_platformlar": "Excel, Netsis, EBA – Teklif & Ürün Devreye Alma, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ2"
            },
            {
                "sira_no": 16,
                "adim_kodu": "8",
                "adim_no": 8,
                "baslik": "Pazar/Proje Profilinin, Kârlılık Çarpanının ve Teklif Fiyatının Belirlenmesi",
                "faaliyet_tanimi": "Doğrulanan birim maliyet üzerinden Teleset Fiyatlama Süreç Talimatı Madde 6.3'e göre ana pazar/proje profili seçilir ve kârlılık çarpanı uygulanarak teklif fiyatı ile müzakere sınırları belirlenir. İskonto, prim, dönemsel indirimler hesaba katılarak net efektif satış fiyatı ve net efektif çarpan hesaplanır, brüt kâr marjı gösterilir. 9. adıma geçilir.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Fabrika Müdürü\nC – İlgili Ürün Grubu Proje Sorumlusu\nC – Bütçe Kontrol ve Dijital Dönüşüm\nC – Pazarlama Uzmanı\nI – Genel Müdür Yardımcısı — stratejik projelerde",
                "ilgili_dokumanlar": "Fiyatlandırma Veri ve Hesaplama Excel Şablonu, Maliyet Analiz Dosyaları, Teleset Fiyatlama Süreç Talimatı, Müşteri RFQ/Sözleşme Kayıtları",
                "dijital_platformlar": "Excel, EBA – Teklif & Ürün Devreye Alma, EBA-CRM, Netsis, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": True,
                "faz": "FAZ2"
            },
            {
                "sira_no": 17,
                "adim_kodu": "9",
                "adim_no": 9,
                "baslik": "Teklifin Net Efektif Çarpan Durumu Nedir?",
                "faaliyet_tanimi": "Hesaplanan net efektif çarpan, pazar/proje profilinin hedef ve asgari çarpanları ile Teklif Yetki Matrisine göre değerlendirilir. Sonuç EBA'ya işlenerek 9A (Hedef Çarpana Uygun), 9B (Yetki Matrisi İlave Onay) veya 9C (Revizyon) adımına yönlendirilir.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Fabrika Müdürü\nC – İlgili Ürün Grubu Proje Sorumlusu\nC – Bütçe Kontrol ve Dijital Dönüşüm\nI – Genel Müdür Yardımcısı",
                "ilgili_dokumanlar": "Fiyatlandırma Veri ve Hesaplama Excel Şablonu, Teleset Fiyatlama Süreç Talimatı, Maliyet Analiz Dosyaları, EBA-CRM RFQ Kaydı",
                "dijital_platformlar": "Excel, EBA – Teklif & Ürün Devreye Alma, EBA-CRM, DocHuman",
                "karar_adimi_mi": True,
                "ana_adim_mi": True,
                "faz": "FAZ2"
            },
            {
                "sira_no": 18,
                "adim_kodu": "9A",
                "adim_no": 9,
                "baslik": "Hedef Çarpana Uygun Teklif",
                "faaliyet_tanimi": "Net efektif çarpanın hedef çarpana eşit veya üzerinde olduğu ve standart ticari koşulların uygulandığı teyit edilir. Teklif dosyası 10. adıma aktarılır.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Fabrika Müdürü\nC – İlgili Ürün Grubu Proje Sorumlusu\nC – Bütçe Kontrol ve Dijital Dönüşüm",
                "ilgili_dokumanlar": "Fiyatlandırma Veri ve Hesaplama Excel Şablonu, Teleset Fiyatlama Süreç Talimatı, EBA-CRM RFQ Kaydı",
                "dijital_platformlar": "Excel, EBA – Teklif & Ürün Devreye Alma, EBA-CRM, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ2"
            },
            {
                "sira_no": 19,
                "adim_kodu": "9B",
                "adim_no": 9,
                "baslik": "Yetki Matrisi Kapsamında İlave Onay Gerektiren Teklif",
                "faaliyet_tanimi": "Net efektif çarpanın hedef çarpanın altında kalması veya kritik ticari koşul içermesi durumunda onay sınıfı (kontrollü sapma, istisnai teklif, kritik istisna) Yetki Matrisine göre belirlenir. Gerekçe ve riskler EBA'ya işlenerek dosya 10. adıma aktarılır.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Fabrika Müdürü\nC – İlgili Ürün Grubu Proje Sorumlusu\nC – Bütçe Kontrol ve Dijital Dönüşüm\nI – Yetki Matrisindeki İlgili Onay Makamı",
                "ilgili_dokumanlar": "Fiyatlandırma Veri ve Hesaplama Excel Şablonu, Teleset Fiyatlama Süreç Talimatı, Maliyet Analiz Dosyaları",
                "dijital_platformlar": "Excel, EBA – Teklif & Ürün Devreye Alma, EBA-CRM, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ2"
            },
            {
                "sira_no": 20,
                "adim_kodu": "9C",
                "adim_no": 9,
                "baslik": "Revizyon Gerektiren Teklif",
                "faaliyet_tanimi": "Hedef seviyeyi karşılamayan ve onaya sunulması uygun bulunmayan tekliflerde revizyon kapsamı belirlenir. Yalnızca fiyat/çarpan/ticari koşul için 8. adıma; maliyet hesabı için 5/6. adıma; teknik kapsam için 3B/3C adımına dönülür.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Fabrika Müdürü\nC – İlgili Ürün Grubu Proje Sorumlusu\nC – Bütçe Kontrol ve Dijital Dönüşüm",
                "ilgili_dokumanlar": "Fiyatlandırma Veri ve Hesaplama Excel Şablonu, Teleset Fiyatlama Süreç Talimatı, EBA-CRM RFQ Kaydı",
                "dijital_platformlar": "Excel, EBA – Teklif & Ürün Devreye Alma, EBA-CRM, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ2"
            },

            # FAZ 3: Yönetim Onayı & Müşteri Müzakeresi (Adım 10 - 15C)
            {
                "sira_no": 21,
                "adim_kodu": "10",
                "adim_no": 10,
                "baslik": "Teklif Dosyasının Yetki Matrisine Göre Onaya Sunulması",
                "faaliyet_tanimi": "Müşteri ve RFQ bilgileri, doğrulanmış maliyet, teklif fiyatı, net efektif çarpan, brüt kâr, iş hacmi, kapasite/yatırım, ticari koşullar ve riskleri içeren teklif dosyası hazırlanır. 9A teklifleri Satış ve Pazarlama Müdürü onayına; 9B teklifleri Yetki Matrisindeki GMY/GM/YK onayına EBA üzerinden sunulur. 11. adıma geçilir.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Fabrika Müdürü\nC – İlgili Ürün Grubu Proje Sorumlusu\nC – Bütçe Kontrol ve Dijital Dönüşüm\nI – Yetki Matrisindeki İlgili Onay Makamı",
                "ilgili_dokumanlar": "Fiyatlandırma Veri ve Hesaplama Excel Şablonu, Maliyet Analiz Dosyaları, Teleset Fiyatlama Süreç Talimatı (Yetki Matrisi), EBA Görüş ve Onay Kaydı",
                "dijital_platformlar": "EBA – Teklif & Ürün Devreye Alma, EBA-CRM, Excel, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": True,
                "faz": "FAZ3"
            },
            {
                "sira_no": 22,
                "adim_kodu": "11",
                "adim_no": 11,
                "baslik": "Teklif Onay Sonucu Nedir?",
                "faaliyet_tanimi": "Teklif dosyası onay makamı tarafından değerlendirilir. Onay sonucu ve varsa koşullar EBA Görüş ve Onay Kaydı üzerine işlenir. Sonuca göre 11A (Onaylandı), 11B (Koşullu Onay / Revizyon) veya 11C (Onaylanmadı) adımına yönlendirilir.",
                "sorumlular_raci": "A – Teklif Yetki Matrisinde Belirlenen Onay Makamı\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – Satış ve Pazarlama Müdürü\nC – İlgili Fabrika Müdürü\nC – İlgili Ürün Grubu Proje Sorumlusu\nC – Bütçe Kontrol ve Dijital Dönüşüm",
                "ilgili_dokumanlar": "Fiyatlandırma Veri ve Hesaplama Excel Şablonu, Teleset Fiyatlama Süreç Talimatı, EBA Görüş ve Onay Kaydı, EBA Ön Fizibilite Kaydı",
                "dijital_platformlar": "EBA – Teklif & Ürün Devreye Alma, EBA-CRM, Excel, DocHuman",
                "karar_adimi_mi": True,
                "ana_adim_mi": True,
                "faz": "FAZ3"
            },
            {
                "sira_no": 23,
                "adim_kodu": "11A",
                "adim_no": 11,
                "baslik": "Teklif Onaylandı",
                "faaliyet_tanimi": "Onaylanan teklifin fiyatı, ticari koşulları, geçerlilik süresi ve versiyonu kesinleştirilerek dosya 12. Müşteri Teklifinin Hazırlanması ve Gönderilmesi adımına aktarılır.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nI – İlgili Onay Makamı\nI – İlgili Fabrika Müdürü\nI – Bütçe Kontrol ve Dijital Dönüşüm\nI – İlgili Ürün Grubu Proje Sorumlusu",
                "ilgili_dokumanlar": "Onaylı Fiyatlandırma Veri ve Hesaplama Excel Şablonu, EBA Görüş ve Onay Kaydı, Müşteri RFQ/Teklif Talebi",
                "dijital_platformlar": "EBA – Teklif & Ürün Devreye Alma, EBA-CRM, Excel, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ3"
            },
            {
                "sira_no": 24,
                "adim_kodu": "11B",
                "adim_no": 11,
                "baslik": "Koşullu Onay veya Revizyon Talebi",
                "faaliyet_tanimi": "Onay makamının koşul ve revizyonları kayıt altına alınır: Teknik/kapasite için 3B/3C; Maliyet için 5/6; Fiyat/çarpan/ticari koşul için 8; Doküman/açıklama için 10. adıma dönülür. Revize teklif yeniden 10. adımda onaya sunulur.",
                "sorumlular_raci": "A – İlgili Onay Makamı\nR – Satış ve Pazarlama Müdürü\nC – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Fabrika Müdürü\nC – İlgili Ürün Grubu Proje Sorumlusu\nC – Bütçe Kontrol ve Dijital Dönüşüm",
                "ilgili_dokumanlar": "Fiyatlandırma Veri ve Hesaplama Excel Şablonu, EBA Görüş ve Onay Kaydı, Teleset Fiyatlama Süreç Talimatı",
                "dijital_platformlar": "EBA – Teklif & Ürün Devreye Alma, EBA-CRM, Excel, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ3"
            },
            {
                "sira_no": 25,
                "adim_kodu": "11C",
                "adim_no": 11,
                "baslik": "Teklif Onaylanmadı",
                "faaliyet_tanimi": "Teklifin reddedilmesi hâlinde ret gerekçesi ve karar tarihi EBA'ya işlenir. Alternatif çalışma istenirse 11B'ye; nihai ret durumunda müşteri bilgilendirilerek dosya 16C adımına (Kapatma) aktarılır.",
                "sorumlular_raci": "A – İlgili Onay Makamı\nR – Satış ve Pazarlama Müdürü\nC – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Fabrika Müdürü\nC – İlgili Ürün Grubu Proje Sorumlusu\nC – Bütçe Kontrol ve Dijital Dönüşüm",
                "ilgili_dokumanlar": "Fiyatlandırma Veri ve Hesaplama Excel Şablonu, Teleset Fiyatlama Süreç Talimatı, EBA Görüş ve Onay Kaydı",
                "dijital_platformlar": "EBA – Teklif & Ürün Devreye Alma, EBA-CRM, Excel, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ3"
            },
            {
                "sira_no": 26,
                "adim_kodu": "12",
                "adim_no": 12,
                "baslik": "Müşteri Teklifinin Hazırlanması ve Gönderilmesi",
                "faaliyet_tanimi": "Onaylanan fiyat ve ticari koşullar esas alınarak müşteriye sunulacak resmi teklif hazırlanır (ürün kodu, fiyat, döviz, teslim/ödeme, MOQ, termin, geçerlilik süresi, kalıp bedeli). İç maliyet/marj teklife dahil edilmez. Müşteri portalı, e-ihale veya e-posta ile iletilerek gönderim tarihi ve kanalı EBA-CRM'e kaydedilir. 13. adıma geçilir.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Ürün Grubu Proje Sorumlusu — teknik içerikte\nC – İlgili Fabrika Müdürü — üretim/termin koşullarında\nI – İlgili birimler",
                "ilgili_dokumanlar": "SAT-EK-005 / SAT-EK-006 İlgili Teklif Formu, Onaylı Fiyatlandırma Excel Şablonu, EBA Görüş ve Onay Kaydı, Müşteri RFQ/Teklif Talebi, EBA-CRM Gönderim Kaydı",
                "dijital_platformlar": "EBA-CRM, EBA – Teklif & Ürün Devreye Alma, Office/Excel, Outlook, Müşteri portalı / e-ihale, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": True,
                "faz": "FAZ3"
            },
            {
                "sira_no": 27,
                "adim_kodu": "13",
                "adim_no": 13,
                "baslik": "Teklifin Takibi ve Müzakerenin Yürütülmesi",
                "faaliyet_tanimi": "Gönderilen teklifin durumu belirlenen takip planı doğrultusunda izlenir. Sorular ve karşı talepler onaylı müzakere sınırları dahilinde yanıtlanır. Görüşmeler, geri bildirimler ve takip tarihleri EBA-CRM'e işlenir. Müşteri geri bildirimi netleştiğinde 14. adıma geçilir.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Ürün Grubu Proje Sorumlusu — teknik taleplerde\nC – İlgili Fabrika Müdürü — kapasite/termin konularında\nC – Bütçe Kontrol ve Dijital Dönüşüm — maliyet/marj etkilerinde\nI – Genel Müdür Yardımcısı — stratejik müzakerelerde",
                "ilgili_dokumanlar": "Müşteriye Gönderilen Onaylı Teklif, Müşteri Geri Bildirimi/Karşı Teklifi, EBA-CRM Görüşme ve Müzakere Kayıtları",
                "dijital_platformlar": "EBA-CRM, Outlook, Müşteri portalı, Microsoft Teams, EBA – Teklif & Ürün Devreye Alma, Office/Excel",
                "karar_adimi_mi": False,
                "ana_adim_mi": True,
                "faz": "FAZ3"
            },
            {
                "sira_no": 28,
                "adim_kodu": "14",
                "adim_no": 14,
                "baslik": "Müşteri Geri Bildirimine Göre Teklifin Durumu Nedir?",
                "faaliyet_tanimi": "Müşterinin geri bildirimi EBA-CRM'e kaydedilir. Durum; kabul (14A), revizyon/karşı teklif (14B), ret/iptal (14C) veya müşteri kararı bekleniyor (14D) olarak sınıflandırılır. Yazılı teyit aranır.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Ürün Grubu Proje Sorumlusu\nC – İlgili Fabrika Müdürü\nC – Bütçe Kontrol ve Dijital Dönüşüm\nI – Genel Müdür Yardımcısı — stratejik projelerde",
                "ilgili_dokumanlar": "Müşteriye Gönderilen Onaylı Teklif, Müşteri Kabul/Ret Bildirimi, Müşteri Revizyon Talebi / Karşı Teklifi, EBA-CRM Teklif Durum Kaydı",
                "dijital_platformlar": "EBA-CRM, EBA – Teklif & Ürün Devreye Alma, Outlook, Müşteri portalı, DocHuman",
                "karar_adimi_mi": True,
                "ana_adim_mi": True,
                "faz": "FAZ3"
            },
            {
                "sira_no": 29,
                "adim_kodu": "14A",
                "adim_no": 14,
                "baslik": "Teklif Kabul Edildi",
                "faaliyet_tanimi": "Yazılı kabulün gönderilen teklif versiyonuyla uyumu doğrulanır. Sipariş, nomination veya sözleşme kayda eklenir. Teklif sonucu EBA-CRM'de 'Kabul Edildi' olarak işaretlenerek 16. adıma geçilir. Koşullu kabul ise 14B'ye aktarılır.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Ürün Grubu Proje Sorumlusu\nC – İlgili Fabrika Müdürü\nI – İlgili birimler\nI – Genel Müdür Yardımcısı",
                "ilgili_dokumanlar": "Müşterinin Yazılı Kabul Bildirimi, Sipariş/Nomination/Sözleşme Kaydı, Onaylı Teklif, EBA-CRM Teklif Sonuç Kaydı",
                "dijital_platformlar": "EBA-CRM, EBA – Teklif & Ürün Devreye Alma, Outlook, Müşteri portalı, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ3"
            },
            {
                "sira_no": 30,
                "adim_kodu": "14B",
                "adim_no": 14,
                "baslik": "Teklif Revizyon Talebi veya Karşı Teklif Alındı",
                "faaliyet_tanimi": "Müşterinin fiyat, teknik kapsam, miktar, termin veya ticari koşullardaki değişiklik talebi ya da karşı teklifi EBA-CRM'e kaydedilir. Değerlendirilmek üzere 15. adıma aktarılır.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Ürün Grubu Proje Sorumlusu\nC – İlgili Fabrika Müdürü\nC – Bütçe Kontrol ve Dijital Dönüşüm\nI – Genel Müdür Yardımcısı",
                "ilgili_dokumanlar": "Müşteri Revizyon Talebi / Karşı Teklifi / Koşullu Kabul Bildirimi, Son Onaylı Teklif, EBA-CRM Müzakere Kaydı",
                "dijital_platformlar": "EBA-CRM, EBA – Teklif & Ürün Devreye Alma, Outlook, Müşteri portalı, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ3"
            },
            {
                "sira_no": 31,
                "adim_kodu": "14C",
                "adim_no": 14,
                "baslik": "Teklif Reddedildi veya Proje İptal Edildi",
                "faaliyet_tanimi": "Yazılı ret veya proje iptali bildiriminin gerekçesi EBA-CRM'e işlenir. Sonuç ve kayıp nedenlerinin sınıflandırılması için süreç 16. adıma (Kapatma) aktarılır.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Fabrika Müdürü\nC – İlgili Ürün Grubu Proje Sorumlusu\nC – Pazarlama Uzmanı\nI – Genel Müdür Yardımcısı",
                "ilgili_dokumanlar": "Müşteri Ret / Proje İptal Bildirimi, Müşteriye Gönderilen Son Teklif, EBA-CRM Teklif Sonuç Kaydı",
                "dijital_platformlar": "EBA-CRM, EBA – Teklif & Ürün Devreye Alma, Outlook, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ3"
            },
            {
                "sira_no": 32,
                "adim_kodu": "14D",
                "adim_no": 14,
                "baslik": "Müşteri Kararı Bekleniyor",
                "faaliyet_tanimi": "Teklif 'Müşteri Kararı Bekleniyor' durumunda takip edilir. Süreç 13. adım kapsamında sürdürülür. Geçerlilik süresi dolduysa 5. adıma dönülür. Geri bildirim alınamazsa Satış ve Pazarlama Müdürü kararıyla 16. adıma (Kapatma) geçilir.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nI – Genel Müdür Yardımcısı",
                "ilgili_dokumanlar": "Müşteriye Gönderilen Son Teklif, Müşteri Yazışmaları, EBA-CRM Takip Kaydı",
                "dijital_platformlar": "EBA-CRM, EBA – Teklif & Ürün Devreye Alma, Outlook, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ3"
            },
            {
                "sira_no": 33,
                "adim_kodu": "15",
                "adim_no": 15,
                "baslik": "Teklif Revizyon Talebi Nasıl Yönetilecek?",
                "faaliyet_tanimi": "14B adımında alınan revizyon talebinin onaylı müzakere sınırları içinde olup olmadığı, yeniden maliyet/fizibilite ve yönetim onayı gerektirip gerektirmediği değerlendirilir. Sonuca göre 15A, 15B veya 15C adımına geçilir.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Ürün Grubu Proje Sorumlusu\nC – İlgili Fabrika Müdürü\nC – Bütçe Kontrol ve Dijital Dönüşüm\nI – Genel Müdür Yardımcısı",
                "ilgili_dokumanlar": "Müşteri Revizyon Talebi / Karşı Teklifi, Son Onaylı Teklif, Fiyatlandırma Excel Şablonu, EBA-CRM Müzakere Kaydı",
                "dijital_platformlar": "EBA-CRM, EBA – Teklif & Ürün Devreye Alma, Excel, Outlook, DocHuman",
                "karar_adimi_mi": True,
                "ana_adim_mi": True,
                "faz": "FAZ3"
            },
            {
                "sira_no": 34,
                "adim_kodu": "15A",
                "adim_no": 15,
                "baslik": "Onaylı Müzakere Sınırları İçindeki Revizyon",
                "faaliyet_tanimi": "Revizyon talebinin önceden onaylanmış müzakere sınırları içinde kaldığı ve maliyet/fizibilite değişikliği yaratmadığı teyit edilir. Teklif güncellenerek ilave yönetim onayı aranmaksızın yeniden müşteriye gönderilmek üzere 12. adıma aktarılır.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Ürün Grubu Proje Sorumlusu\nC – İlgili Fabrika Müdürü\nI – İlgili Onay Makamı",
                "ilgili_dokumanlar": "Müşteri Revizyon Talebi, Son Onaylı Teklif, Müzakere Sınırlarını İçeren EBA Onay Kaydı, Revize Müşteri Teklifi",
                "dijital_platformlar": "EBA-CRM, EBA – Teklif & Ürün Devreye Alma, Excel, Outlook, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ3"
            },
            {
                "sira_no": 35,
                "adim_kodu": "15B",
                "adim_no": 15,
                "baslik": "Yeniden Değerlendirme veya Onay Gerektiren Revizyon",
                "faaliyet_tanimi": "Müzakere sınırlarını aşan veya teknik/maliyet/fiyat/ticari koşul değişikliği oluşturan talepler ilgili adıma yönlendirilir: Teknik için 3B/3C; Maliyet için 5/6; Fiyat/marj için 8; Doküman için 12. İlgili onaylar tamamlandıktan sonra 12. adımda müşteriye gönderilir.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Ürün Grubu Proje Sorumlusu\nC – İlgili Fabrika Müdürü\nC – Bütçe Kontrol ve Dijital Dönüşüm\nI – Genel Müdür Yardımcısı",
                "ilgili_dokumanlar": "Müşteri Revizyon Talebi, Son Onaylı Teklif, Fiyatlandırma Excel Şablonu, EBA Görüş ve Onay Kaydı",
                "dijital_platformlar": "EBA-CRM, EBA – Teklif & Ürün Devreye Alma, Excel, Outlook, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ3"
            },
            {
                "sira_no": 36,
                "adim_kodu": "15C",
                "adim_no": 15,
                "baslik": "Talep Edilen Revizyon Uygulanabilir Değil",
                "faaliyet_tanimi": "Revizyon talebinin teknik/mali nedenlerle karşılanamaması durumunda gerekçeler müşteriye bildirilir. Alternatif çözüm sunulacaksa 15B'ye; alternatif yoksa mevcut teklif takibi için 13. adıma dönülür. Müşteri ret bildirirse 14C'ye geçilir.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Ürün Grubu Proje Sorumlusu\nC – İlgili Fabrika Müdürü\nC – Bütçe Kontrol ve Dijital Dönüşüm\nI – Genel Müdür Yardımcısı",
                "ilgili_dokumanlar": "Müşteri Revizyon Talebi, Revizyon Değerlendirme ve Gerekçe Kaydı, Müşteri Bilgilendirme Yazışması",
                "dijital_platformlar": "EBA-CRM, EBA – Teklif & Ürün Devreye Alma, Outlook, DocHuman",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ3"
            },

            # FAZ 4: Teklif Sonucu, Devreye Alma & Kapanış (Adım 16 - 16C)
            {
                "sira_no": 37,
                "adim_kodu": "16",
                "adim_no": 16,
                "baslik": "Teklif Sonucunun Kaydedilmesi ve İlgili Sürece Aktarılması",
                "faaliyet_tanimi": "Teklifin nihai sonucu; teklif versiyonu, karar tarihi ve müşteri bildirimiyle EBA-CRM'e kaydedilir. Sonuç; mevcut ürün fiyat revizyonu kabulü (16A), yeni/revize ürün kabulü (16B) veya olumsuz/kapanış (16C) olarak sınıflandırılır.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Ürün Grubu Proje Sorumlusu\nC – İlgili Fabrika Müdürü\nC – Bütçe Kontrol ve Dijital Dönüşüm\nI – Genel Müdür Yardımcısı\nI – İlgili birimler",
                "ilgili_dokumanlar": "Müşterinin Kabul/Ret/İptal Bildirimi, Son Onaylı Teklif, Sipariş/Nomination/Sözleşme, EBA Görüş ve Onay Kaydı, EBA-CRM Teklif Sonuç Kaydı",
                "dijital_platformlar": "EBA-CRM, EBA – Teklif & Ürün Devreye Alma, Netsis, DocHuman",
                "karar_adimi_mi": True,
                "ana_adim_mi": True,
                "faz": "FAZ4"
            },
            {
                "sira_no": 38,
                "adim_kodu": "16A",
                "adim_no": 16,
                "baslik": "Mevcut Ürün Fiyat Revizyonunun Sisteme Aktarılması ve Kapatılması",
                "faaliyet_tanimi": "Kabul edilen yeni fiyat para birimi ve geçerlilik tarihleriyle Netsis üzerinde tanımlanır. Eski/yeni fiyat geçişi, açık siparişler ve stoklar kontrol edilerek ilgili birimler bilgilendirilir. Teklif dosyası arşivlenerek Ürün Teklif Süreci tamamlanır.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Fabrika Müdürü\nC – Planlama ve ilgili birimler\nC – Bütçe Kontrol ve Dijital Dönüşüm\nI – İlgili birimler",
                "ilgili_dokumanlar": "Müşterinin Yazılı Fiyat Kabulü, Onaylı Müşteri Teklifi, Fiyatlandırma Excel Şablonu, EBA-CRM Teklif Sonuç Kaydı, Netsis Fiyat Tanımlama Dokümanı",
                "dijital_platformlar": "EBA-CRM, EBA – Teklif & Ürün Devreye Alma, Netsis, Excel, DocHuman, Ortak paylaşım alanı",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ4"
            },
            {
                "sira_no": 39,
                "adim_kodu": "16B",
                "adim_no": 16,
                "baslik": "Kabul Edilen Yeni/Revize Ürün veya Projenin Devreye Alma Sürecine Aktarılması ve Teklif Sürecinin Kapatılması",
                "faaliyet_tanimi": "Yazılı kabul, sipariş/nomination/sözleşme alınarak sonuç EBA-CRM'de güncellenir. Proje EBA üzerinden Yeni Ürün Devreye Alma Sürecine (APQP / PPAP) aktarılır. Onaylı teknik dokümanlar, fizibilite, maliyet ve ticari şartlar paylaşılır. Teklif dosyası arşivlenerek Ürün Teklif Süreci tamamlanır.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu — ticari devir\nR – İlgili Ürün Grubu Proje Sorumlusu — teknik/proje devri\nC – İlgili Fabrika Müdürü\nC – Planlama, Satın Alma, Kalite ve teknik birimler\nC – Bütçe Kontrol ve Dijital Dönüşüm\nI – Genel Müdür Yardımcısı\nI – İlgili birimler",
                "ilgili_dokumanlar": "Müşterinin Yazılı Kabulü, Sipariş/Nomination/Sözleşme, Onaylı Teklif, Teknik Resim/BOM, Onaylı Ön Fizibilite Kaydı, Yeni Ürün Devreye Alma Talimatı, EBA-CRM Teklif Sonuç Kaydı",
                "dijital_platformlar": "EBA-CRM, EBA – Teklif & Ürün Devreye Alma, Netsis, Excel, DocHuman, Ortak paylaşım alanı",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ4"
            },
            {
                "sira_no": 40,
                "adim_kodu": "16C",
                "adim_no": 16,
                "baslik": "Teklif Verilmeyen veya Olumsuz Sonuçlanan Teklif Kaydının Kapatılması",
                "faaliyet_tanimi": "Teklif verilmeme, iç onayda ret, müşteri reddi, proje iptali veya geri bildirim alınamaması durumlarında teklif kapatılır. Sonuç (fiyat, termin, teknik yeterlilik, kapasite, yatırım vb.) EBA-CRM'e kaydedilir. Bulgular sonraki çalışmalar için arşivlenerek süreç kapatılır.",
                "sorumlular_raci": "A – Satış ve Pazarlama Müdürü\nR – İlgili Ürün Grubu Satış Sorumlusu\nC – İlgili Fabrika Müdürü — kapasite/termin/üretim nedenlerinde\nC – İlgili Ürün Grubu Proje Sorumlusu — teknik nedenlerde\nC – Pazarlama Uzmanı — pazar/rakip nedenlerinde\nI – Genel Müdür Yardımcısı",
                "ilgili_dokumanlar": "Müşteri Ret / İptal Bildirimi, Müşteriye Gönderilen Son Teklif, EBA-CRM Teklif Sonuç ve Kayıp Nedeni Kaydı, EBA Görüş ve Onay Kaydı",
                "dijital_platformlar": "EBA-CRM, EBA – Teklif & Ürün Devreye Alma, Outlook, DocHuman, Ortak paylaşım alanı",
                "karar_adimi_mi": False,
                "ana_adim_mi": False,
                "faz": "FAZ4"
            },
        ]

        count_created = 0
        count_updated = 0

        for item in adilar:
            adim_kodu = item["adim_kodu"]
            defaults = {
                "sira_no": item["sira_no"],
                "adim_no": item["adim_no"],
                "baslik": item["baslik"],
                "faaliyet_tanimi": item["faaliyet_tanimi"],
                "sorumlular_raci": item["sorumlular_raci"],
                "sorumlular": item["sorumlular_raci"],
                "ilgili_dokumanlar": item["ilgili_dokumanlar"],
                "dijital_platformlar": item["dijital_platformlar"],
                "karar_adimi_mi": item["karar_adimi_mi"],
                "ana_adim_mi": item["ana_adim_mi"],
                "faz": item["faz"],
            }
            obj, created = UrunTeklifAdimTanimi.objects.update_or_create(
                adim_kodu=adim_kodu,
                defaults=defaults
            )
            if created:
                count_created += 1
            else:
                count_updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"UrunTeklifAdimTanimi basariyla yuklendi: {count_created} yeni eklendi, {count_updated} guncellendi (Toplam {len(adilar)} adim)."
            )
        )
