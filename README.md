# 🎯 Job Scrater

**Job Scrater**, LinkedIn üzerinden belirttiğiniz meslekler için otomatik iş ilanları çeken, aranan yetenekleri analiz eden ve **kendi CV'nizi** pazarın gerçek verileriyle kıyaslayan yapay zeka destekli bir Kariyer Asistanıdır.

## ✨ Özellikler
- **Piyasa Analizi:** LinkedIn verilerini kazıyarak "en çok hangi yetenek isteniyor", "ortalama kaç yıl tecrübe bekleniyor" gibi verileri istatistiksel olarak çizer.
- **Profil (Loadout) Sistemi:** Yaptığınız her aramayı (örn: *Frontend-Europe*) ayrı ayrı kaydeder. İleride o profile geçtiğinizde tüm ayarlarınız geri yüklenir.
- **Yapay Zeka CV Analizi:** PDF formatındaki CV'nizi okur, "Pazarın istediği ama sizde eksik olan" yetenekleri kırmızıyla işaretler ve kişiselleştirilmiş akıllı tavsiyeler verir.
- **Kariyer Çaprazlaması:** CV'nizi diğer meslek profilleriyle eşleştirip "Bu yeteneklerinle Veri Bilimi pazarına da %60 uyumlusun!" gibi farklı rotalar çizer.
- **Ban Korumalı Bot:** İstekler arası bekleme süresi ve otomatik tarama döngüsü ile arka planda güvenle çalışır.

## 🚀 Kurulum ve Çalıştırma (Kod Bilmeyenler İçin)

Docker veya komut satırı ile uğraşmanıza gerek yok! Bilgisayarınızda sadece **Python** yüklü olması yeterlidir. Eğer yüklü değilse [python.org](https://www.python.org/downloads/) adresinden indirip kurabilirsiniz (Kurarken "Add Python to PATH" seçeneğini işaretlemeyi unutmayın).

### Windows Kullanıcıları:
Klasörün içindeki `baslat.bat` dosyasına **çift tıklayın**. İlk açılışta gerekli kütüphaneleri ve yapay zeka modellerini indirecek (1-2 dakika sürebilir), ardından uygulamayı tarayıcınızda otomatik olarak açacaktır.

### Mac / Linux Kullanıcıları:
Klasörün içindeki `baslat.command` dosyasına çift tıklayın. (Eğer tıklamayla açılmazsa terminali bu klasörde açıp `bash baslat.command` yazmanız yeterlidir).

## 🐳 Docker İle Çalıştırma (Alternatif Yöntem)
Eğer bilgisayarınızda Docker yüklüyse (Python kurmanıza gerek kalmadan) sistemi tamamen izole çalıştırabilirsiniz. "Ben kod yazmayı bilmiyorum, sadece kopyala-yapıştır yapacağım" diyorsanız:

1. Windows'ta başlat menüsüne **CMD** (veya *Komut İstemi* / *PowerShell*) yazıp açın. Mac kullanıyorsanız **Terminal**'i açın.
2. Siyah ekran açıldığında, aşağıdaki iki satırı sırayla kopyalayıp sağ tıklayarak yapıştırın ve klavyenizden "Enter" tuşuna basın:

```bash
docker build -t job-scrater .
docker run -p 8501:8501 job-scrater
```

İşlem bitip yazılar durduğunda, internet tarayıcınızı açın ve adres çubuğuna şunu yazıp girin: **`http://localhost:8501`**
