# 🎯 Job Scrater

**Job Scrater**, LinkedIn üzerinden belirttiğiniz meslekler için otomatik iş ilanları çeken, aranan yetenekleri analiz eden ve **kendi CV'nizi** pazarın gerçek verileriyle kıyaslayan yapay zeka destekli bir Kariyer Asistanıdır.

## ✨ Yeni ve Öne Çıkan Özellikler
- **🤖 Akıllı Oto-Tarama (Daemon Worker):** Arka planda sessizce çalışan gelişmiş botumuz sayesinde sistem periyodik olarak belirlediğiniz profilleri tarar. Tüm ayarları (Çalışma Aralığı, İlan Limiti, İstek Gecikmesi) doğrudan **Analiz Merkezi**'nden saniyeler içinde değiştirebilirsiniz. Saat değil "dakika" bazlı ayarlanabilir!
- **📊 Etkileşimli İlan Yönetimi:** Çektiğiniz ham ilanları yeni "Data Editor" arayüzü sayesinde kolayca inceleyebilir, istemediğiniz ilanları kutucukları işaretleyerek (checkbox) tek tıkla silebilirsiniz.
- **⚡ Canlı ve Hızlı Güncellemeler:** Projeye entegre edilen `watchdog` ve `config.toml` sayesinde arka planda yapılan bir ayar değişikliği saniyesinde arayüze yansır, sayfayı sürekli yenilemenize gerek kalmaz.
- **🧠 Gelişmiş NLP ve Regex:** İlanlardan sadece yetenekleri değil, tam olarak "kaç yıl tecrübe" istendiğini yüksek isabet oranıyla çeken yeni Regex mimarisi. (Örn: "3+ years of experience")

## 🚀 Temel Özellikler
- **Piyasa Analizi:** LinkedIn verilerini kazıyarak "en çok hangi yetenek isteniyor", "ortalama kaç yıl tecrübe bekleniyor" gibi verileri istatistiksel grafiklerle (Radar, Pasta, Kelime Bulutu, Isı Haritası vb.) sunar.
- **Profil (Loadout) Sistemi:** Yaptığınız her aramayı (örn: *Frontend-Europe*) ayrı ayrı kaydeder. 
- **Yapay Zeka CV Analizi:** PDF formatındaki CV'nizi okur, "Pazarın istediği ama sizde eksik olan" yetenekleri işaretler ve tavsiyeler verir.
- **Kariyer Çaprazlaması:** CV'nizi diğer meslek profilleriyle eşleştirerek farklı rotalar çizer.

## 🛠️ Kurulum ve Çalıştırma (Kod Bilmeyenler İçin)

Docker veya komut satırı ile uğraşmanıza gerek yok! Bilgisayarınızda sadece **Python** yüklü olması yeterlidir. Eğer yüklü değilse [python.org](https://www.python.org/downloads/) adresinden indirip kurabilirsiniz (Kurarken "Add Python to PATH" seçeneğini işaretlemeyi unutmayın).

### Windows Kullanıcıları:
Klasörün içindeki `baslat.bat` dosyasına **çift tıklayın**. İlk açılışta gerekli kütüphaneleri indirecek (1-2 dakika sürebilir), ardından uygulamayı tarayıcınızda otomatik olarak açacaktır.

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

## 🛡️ Güvenli (Stealth) Bot Kullanım Tavsiyeleri
LinkedIn'den ban yememek için bot ayarlarınızı şu şekilde tutmanızı tavsiye ederiz:
- **Çalışma Aralığı:** Min 120 dakika (2 Saat)
- **Maksimum İlan:** 30 - 50 arası
- **Gecikme (Sn):** 4.0 - 5.0 saniye
Bu ayarlar botun insan davranışı sergilemesini sağlayarak güvenle çalışmasını garanti eder.
