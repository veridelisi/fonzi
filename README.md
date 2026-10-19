# Fonzi — Repo Rollover ve Teminat Krizi Simülatörü

Streamlit üzerinden çalışan, bilanço tutarlılığı gözeten **varsayımsal** repo–teminat döngüsü oyunu.

## Çalıştırma
```bash
pip install -r requirements.txt
streamlit run app.py
```

Streamlit Community Cloud üzerinde **veridelisi/fonzi** deposunu, `main` dalını ve `app.py` giriş dosyasını seçin.

## Kapsam
- Hisse fonu ve repo finansmanı sağlayan karşı tarafın eşzamanlı T hesapları
- Fiyat değişiklikleri ve teminat kapasitesi
- Hisse alımı, teminata ayırma, ek repo, geri ödeme, günlük faiz ve rollover
- Teminat açığı, yetersiz nakit ve işlem günlüğü

**Önemli:** Tutarlar, teminat oranları ve model mekanizmaları öğretici varsayımlardır; Tera, Pusula veya başka bir gerçek kuruluşun belirli işlemlerine ilişkin tespit ya da manipülasyon kanıtı değildir. Repo sözleşmelerinin hukuki/muhasebesel ayrıntıları bu ilk sürümde sadeleştirilmiştir.
