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
### Sürüm 1.2.

* Türkçe dil desteği eklendi. (Umut KORKMAZ)

### Sürüm 1.1.

* Çevrilebilir dizelerdeki hata düzeltmeleri.

* Otomatik çeviri ile İngilizce dili eklendi.

### Sürüm 1.0.

* İlk sürüm.