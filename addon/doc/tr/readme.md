# Windows Konsolları için Görüntüleyici Eklenti Kılavuzu
## Giriş

Bu eklenti, etkileşimli bir iletişim kutusu aracılığıyla Windows konsollarının içeriğini görüntülemeyi kolaylaştırır. Kolay gezinme ve entegre arama seçeneklerine olanak tanıyan, herhangi bir Windows konsol penceresi için geçerli bir araçtır.  

## İlk kurulum
### Tuş Ataması

Bu eklentiyi kullanabilmek için, konsol görüntüleyici iletişim kutusunu açacak bir tuş bileşimi atamanız gerekir. Bunu aşağıdaki şekilde yapabilirsiniz:

```
NVDA > Tercihler > Girdi Hareketleri > Konsol Görüntüleyici > Konsol Görüntüleyiciyi Göster
```

### kısıtlamalar

* Aynı anda yalnızca bir iletişim kutusunun açılmasına izin verilir.
* İletişim kutusu yalnızca bir Windows konsol penceresi odakta olduğunda çağrılabilir.

## Diyalog Özellikleri

### Gezinme:

* İçerikte gezinmek için imleç tuşlarını kullanın.
* İmlecin geçerli satırını ve konumunu almak için 'F1' tuşuna basın.

### Arama:

* `Ctrl + F`: Bir arama iletişim kutusu açar.
* `F3`: Arama yapmak için bir iletişim kutusu görüntüler. Daha önce bir arama yapılmışsa, bir sonraki sonucu arar.
* `Shift + F3`: Aramada önceki sonucu gider.
* Aramalar büyük/küçük harfe duyarlı değildir ve tam kelimeler veya kelime parçaları üzerinde gerçekleştirilebilir.
* Her başarılı arama, imlecin artık bir sonraki bulunan kelimenin üzerinde olduğunu belirten bir "bip" sesi çıkaracaktır.

### Hızlı Menü

Aşağıdaki seçenekleri bulacağınız menüye 'Alt + K' ile hızlı erişim:

* Ara
* Farklı Kaydet.
* Çık

### İletişim Kutusundan Çıkma:

* `Alt + F4` veya `Escape`: İletişim kutusunu kapatır.

## İçeriğin Güncellenmesi:

Bir iletişim kutusu açarsanız ve ardından konsol güncellenirse, güncellemeleri görmek için iletişim kutusunu kapatmanız ve yeniden çağırmanız gerekir.

## Kullanılabilir Windows Ortak Konsolları

Windows'ta komutları ve komut dosyalarını çalıştırmak için kullanabileceğiniz çeşitli konsollar veya terminaller vardır. İşte en yaygın konsolların listesi:

1. **CMD** (Komut İstemi): Bu, komutları ve toplu komut dosyalarını çalıştırmak için kullanılan metin tabanlı bir konsoldur.
   
2. **PowerShell**: Komut dosyaları aracılığıyla görevlerin otomasyonuna olanak tanıyan gelişmiş bir konsoldur. Geleneksel CMD'den daha fazla özellik sunar.
   
3. **Windows Terminal**: PowerShell, CMD ve Linux konsolu (Windows Alt Sistemi aracılığıyla) gibi birden fazla konsola erişime izin veren modern bir uygulamadır.para Linux).
   
4. **Bash** (Linux için Windows Alt Sistemi Üzerinden): Windows içerisinde bir Linux ortamı çalıştırmanıza, Linux komutlarının ve uygulamalarının kullanılmasına olanak sağlar.

> **Not**: Bu konsollara Windows başlat menüsünden ya da kullanmak istediğiniz konsolun adını yazarak Windows arama yoluyla ulaşabilirsiniz.

## Sürüm Geçmişi:
### Sürüm 1.4:

**Yenilikler:**:

Girdi hareketlerinde ilgili kategorideki tuşları atayın.

1. **Konsollara sağ tıklayın**:
   - Artık pano içeriğini konsolda otomatik olarak yapıştırmak için klasik veya modern konsollara sağ tıklayabilirsiniz.
   - Bu işlev, ek kombinasyonlara ihtiyaç duymadan metni konsol ortamına hızlı bir şekilde aktarmak için yararlıdır.

2. **Konsol başlatıcısı**:
   - Sistemde herhangi bir dizinden kurulan farklı konsolları açmanıza olanak tanıyan yeni bir işlev eklendi.
   - Mevcut konsolları otomatik olarak algılar: CMD, PowerShell, Windows Terminali, Git-Bash ve Visual Studio konsolları.
   - Normal modda veya yönetici ayrıcalıklarıyla konsolları açma seçenekleri içerir.
   - Ok tuşlarıyla istenen konsolu kolayca seçmeye ve ** `Başlatıcı` ** ile açmaya izin verir.

### Sürüm 1.3:

* Windows Terminali ile tam uyumluluk.

Bu özellik test aşamasındadır.

Şu anda yapılan testlerde metni doğru bir şekilde ayıklıyor ve bir diyalogda rahatça görselleştirilebilmesi ve onunla çalışabilmesi için görüntülüyor.

Bu yeni işlev, eklentiye eklediğimiz aynı tuş kombinasyonu kullanılarak cmd, powershell ve bash konsol görüntüleyicisine eklenir.

Bu kombinasyona bastığınızda ne tür bir konsola odaklandığınızı algılayacak ve buna göre hareket edecektir.

### Sürüm 1.2:

* Windows 10'da izin reddi ile ilgili kritik hata düzeltildi (kod 5).

* Türkçe dil desteği ve belgeleri eklendi (Umut KORKMAZ).

* Metinsiz konsol algılama özelliği eklendi.

### Sürüm 1.1.

* Çevrilebilir dizelerdeki hata düzeltmeleri.

* Otomatik çeviri ile İngilizce dili eklendi.

### Sürüm 1.0.

* İlk sürüm.