import streamlit as st
import pandas as pd

st.set_page_config(page_title="Fon Krizi | Belgeli Finansman Ağı", page_icon="📊", layout="wide")
st.markdown("""
<style>
.block-container{max-width:1220px;padding-top:1.4rem}
.intro{color:#64748b;font-size:.95rem}
.node{border:1px solid #cbd5e1;border-radius:14px;padding:17px;min-height:150px;background:#f8fafc}
.node b{font-size:1.1rem}
.node p{font-size:.89rem;line-height:1.5}
.green{border-top:5px solid #178766}.blue{border-top:5px solid #3869a7}
.red{border-top:5px solid #b55b56}
.connector{text-align:center;font-size:1.5rem;color:#6b7280;padding:8px}
.notice{border-left:4px solid #497da7;padding:12px 16px;background:#f0f5fa;border-radius:8px}
@media(max-width:700px){.node{min-height:auto}}
</style>
""",unsafe_allow_html=True)

st.title("Fon Krizi: Bilançolar ve Finansman Bağlantıları")
st.markdown('<p class="intro">2024 sonundan Eylül 2026’ya uzanan, yalnızca yayımlanmış tarihsel kayıtlarla oluşturulmuş inceleme. Simülasyon, varsayımsal rakam, oyun veya fiyat kaydırıcısı içermez.</p>',unsafe_allow_html=True)
st.info("Önemli ayrım: Repo işleminde nakit veren fonun aktifinde **repo alacağı**, nakit kullanan kurumun pasifinde **repo borcu** doğar. Teminat hissesi, nakit borçlusu şirketle aynı şey değildir.")


st.subheader("Tera Bağlantılı Sahiplikler · Genişletilmiş Ağ")
st.caption("Solda hissedar, sağda şirket. Mavi: tekil Tera fonu; yeşil: Tera şirketi; mor: Tera Portföy tarafından yönetilen fonların TOPLAM payı. Her bağlantının oranı ve tarihi sabit gösterilir.")
import plotly.graph_objects as go
import textwrap

# Tekil sahiplikler: kullanıcının Matriks Analist ekranları (ortaklık kesit tarihi görünmüyor).
# Toplu sahiplikler: daha önce araştırmada bulunan tarihli KAP pay alım-satım açıklamaları.
# Toplam fon payı, tekil fon paylarına EKLENEREK hesaplanamaz.
links = [
    ("DSTKF","Tera Portföy Birinci Serbest Fon",8.06,"Tekil fon","Tarih belirtilmemiş"),
    ("DSTKF","Tera Portföy Para Piyasası Fonu (TP2)",7.21,"Tekil fon","Tarih belirtilmemiş"),
    ("DSTKF","Tera Yatırım Menkul Değerler",3.08,"Tera şirketi","Tarih belirtilmemiş"),
    ("KTLEV","Tera Portföy Hisse Senedi (TL) Fonu",3.12,"Tekil fon","Tarih belirtilmemiş"),
    ("TRHOL","Tera Portföy fonları (toplam)",33.07,"Fonların toplamı","27.08.2026"),
    ("MANAS","Tera Portföy fonları (toplam)",20.96,"Fonların toplamı","01.09.2026"),
    ("OZATD","Tera Portföy fonları (toplam)",17.93,"Fonların toplamı","31.08.2026"),
    ("PEKGY","Tera Portföy fonları (toplam)",15.05,"Fonların toplamı","05.05.2026"),
    ("TEHOL","Tera Portföy fonları (toplam)",14.13,"Fonların toplamı","19.01.2026"),
    ("DSTKF","Tera Portföy fonları (toplam)",10.20,"Fonların toplamı","01.09.2026"),
]
company_order=["DSTKF","KTLEV","TRHOL","MANAS","OZATD","PEKGY","TEHOL"]
actors=list(dict.fromkeys(x[1] for x in links))
colors={"Tekil fon":"#2369c9","Tera şirketi":"#0e8274","Fonların toplamı":"#7c3aed"}
# Aynı hissedeki çizgiler birbiri üzerine binmesin: her ilişkiye ayrı satır.
rows=[]
for ticker in company_order:
    for entry in links:
        if entry[0]==ticker:
            rows.append(entry)
row_count=len(rows)
fig=go.Figure()
for i,(ticker,owner,pct,kind,date) in enumerate(rows):
    yy=row_count-1-i
    color=colors[kind]
    fig.add_trace(go.Scatter(x=[0.53,0.86],y=[yy,yy],mode="lines",
        line=dict(color=color,width=3),
        hovertemplate=f"{owner} → {ticker}<br>%{pct:.2f} · {date}<extra></extra>",
        showlegend=False))
    fig.add_trace(go.Scatter(x=[0.53,0.86],y=[yy,yy],mode="markers",
        marker=dict(size=[14,16],color=[color,"#e58b36"]),
        hoverinfo="skip",showlegend=False))
    owner_label="<br>".join(textwrap.wrap(owner,32,break_long_words=False))
    fig.add_annotation(x=0.50,y=yy,text=owner_label,showarrow=False,
        xanchor="right",align="right",font=dict(size=12,color="#24344b"))
    fig.add_annotation(x=0.68,y=yy,text=f"<b>%{pct:.2f}</b>".replace(".",","),
        showarrow=False,bgcolor="white",bordercolor=color,borderwidth=2,
        borderpad=5,font=dict(size=16,color="#17233b"))
    fig.add_annotation(x=0.89,y=yy,text=f"<b>{ticker}</b><br><span style='font-size:10px'>{date}</span>",
        showarrow=False,xanchor="left",align="left",font=dict(size=14,color="#24344b"))
fig.update_layout(height=max(830,row_count*92),margin=dict(l=15,r=15,t=20,b=20),
    xaxis=dict(visible=False,range=[0,1]),
    yaxis=dict(visible=False,range=[-0.7,row_count-0.3]),
    paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",dragmode=False)
st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
st.caption("ÖNEMLİ: Mor çizgiler aynı grubun yönetimindeki fonların bildirilen toplamını gösterir; tek başına bir fonun veya Tera Yatırım şirketinin doğrudan mülkiyeti değildir. DSTKF için farklı kaynak ve tarihlerdeki oranlar birbirine eklenmemelidir.")
table=pd.DataFrame(rows,columns=["Hisse","Tera bağlantılı sahip","Pay (%)","Sahiplik türü","Kesit tarihi"])
table["Pay (%)"]=table["Pay (%)"].map(lambda x:f"%{x:.2f}".replace(".",","))
st.dataframe(table,hide_index=True,use_container_width=True)
st.warning("Veri kontrolü: DSTKF ve KTLEV'nin tekil fon payları paylaştığın Matriks ekranından okunmuştur. Diğer oranlar önceki KAP incelememizdeki tarihli bildirim değerleridir; bunların bildirim kimlikleri ve sonraki devirleri bağımsız olarak yeniden teyit edilmelidir. Dolayısıyla bu grafik 16 Eylül 2026'nın tek günlük kesin ortaklık tablosu değildir.")
st.divider()

st.subheader("1 · Tarihsel bilanço göstergeleri")
st.caption("Tabloda dönemler birbirine karıştırılmamıştır. 2026 Eylül sonu için tam bilanço mevcut değilse veri türetilmemiştir.")
records=[
    ("31.12.2024","TLY","Fon toplam değeri / NAV",0.817627,"2024 fon raporu"),
    ("31.12.2025","TLY","Net varlık değeri / NAV",35.30,"2025 finansal rapor"),
    ("31.12.2025","TP2","Toplam varlıklar",61.202,"2025 finansal rapor"),
    ("31.12.2025","TP2","Net varlık değeri / NAV",61.05,"2025 finansal rapor"),
    ("31.12.2025","TP2","Ters repo alacakları",40.275,"2025 finansal rapor"),
    ("31.12.2025","TP2","Nakit ve nakit benzerleri",0.000787,"2025 finansal rapor"),
]
df=pd.DataFrame(records,columns=["Tarih","Kurum/fon","Bilanço kalemi","Milyar TL","Belge"])
st.dataframe(df,hide_index=True,use_container_width=True,column_config={"Milyar TL":st.column_config.NumberColumn(format="%.6f")})
st.caption("TP2'nin ters repo alacakları, para fonunun bankadaki kullanılabilir nakdi olarak okunamaz. TLY'nin 2024–2025 NAV büyümesi de tek başına fiyat artışını göstermez; fon giriş/çıkışları ayrıştırılmalıdır.")

c1,c2,c3=st.columns(3)
c1.metric("TLY 2024 sonu NAV","0,818 milyar TL")
c2.metric("TLY 2025 sonu NAV","35,30 milyar TL")
c3.metric("TP2 2025 sonu ters repo alacağı","40,275 milyar TL")
st.markdown("**Kaynaklar:** [TLY 2024 fon raporu](https://www.kap.org.tr/tr/api/file/download/4028328c949953a00194b1159d9976cb) · [TP2 2025 finansal raporu](https://www.kap.org.tr/tr/Bildirim/1581001) · [TLY 2025 raporu](https://www.kap.org.tr/tr/Bildirim/1581004)")

st.subheader("2 · Belgelenmiş finansman ağı")
l,mid,r=st.columns([4,1,4])
with l:
    st.markdown('<div class="node green"><b>TP2 — Para Piyasası Fonu</b><p>2026 tarihli açıklamalarda borsa dışı ters repo yapan, nakit sağlayan taraf.</p><p><b>Aktif: Repo alacağı</b></p></div>',unsafe_allow_html=True)
with mid:
    st.markdown('<div class="connector">→</div><div style="text-align:center;font-size:.8rem">Repo nakdi</div>',unsafe_allow_html=True)
with r:
    st.markdown('<div class="node red"><b>Tera Yatırım Menkul Değerler</b><p>TP2 ile bildirilen işlemlerde repo finansmanı kullanan karşı taraf.</p><p><b>Pasif: Repo borcu</b></p></div>',unsafe_allow_html=True)
st.caption("Kaynak: KAP tarihli borsa dışı ters repo bildirimleri; işlemlerin anapara büyüklükleri bu açıklamalardan çıkartılamaz.")

st.subheader("3 · Eylül 2026 öncesi doğrulanan repo işlemleri")
transactions=[
    ("13–14.07.2026","TP2","Tera Yatırım Menkul Değerler",43,"https://www.kap.org.tr/tr/Bildirim/1632916"),
    ("29–30.07.2026","TP2","Tera Yatırım Menkul Değerler",43,"https://www.kap.org.tr/tr/Bildirim/1638563"),
    ("05–06.08.2026","TLY","Tera Yatırım Menkul Değerler",43,"https://www.kap.org.tr/tr/Bildirim/1643656"),
    ("10–11.08.2026","TLY","Tera Yatırım Menkul Değerler",43,"https://www.kap.org.tr/tr/Bildirim/1646721"),
    ("21–24.08.2026","TLY","Tera Yatırım Menkul Değerler",43,"https://www.kap.org.tr/tr/Bildirim/1654172"),
    ("24–25.08.2026","TP2","Tera Yatırım Menkul Değerler",43,"https://www.kap.org.tr/tr/Bildirim/1654508"),
    ("01–02.09.2026","TP2","Tera Yatırım Menkul Değerler",43,"https://www.kap.org.tr/tr/Bildirim/1656969"),
    ("07–08.09.2026","TP2","Tera Yatırım Menkul Değerler",43,"https://www.kap.org.tr/tr/Bildirim/1659629"),
    ("08–09.09.2026","TP2","Tera Yatırım Menkul Değerler",43,"https://www.kap.org.tr/tr/Bildirim/1660238"),
    ("09–10.09.2026","TP2","Tera Yatırım Menkul Değerler",43,"https://www.kap.org.tr/tr/Bildirim/1661096"),
    ("11–14.09.2026","TP2","Tera Yatırım Menkul Değerler",43,"https://www.kap.org.tr/tr/Bildirim/1662026")
]
t=pd.DataFrame(transactions,columns=["İşlem dönemi","Nakit sağlayan","Borçlanan karşı taraf","Yıllık faiz (%)","KAP bildirimi"])
st.dataframe(t,hide_index=True,use_container_width=True,column_config={"KAP bildirimi":st.column_config.LinkColumn("Resmî kaynak",display_text="KAP bildirimi"),"Yıllık faiz (%)":st.column_config.NumberColumn(format="%d%%")})
st.caption("Bunlar seçilmiş, doğrudan bağlantısı doğrulanmış işlemlerdir; tüm repo işlemleri değildir. Aynı nakdin her gün çevrildiği, toplam repo borcu veya hisse alımında kullanıldığı bu tablodan hesaplanamaz.")

st.subheader("4 · Hisse taşıyan fon ile finansman tarafı ayrı")
a,b=st.columns(2)
with a:
    st.markdown('<div class="node blue"><b>TLY: Hisse taşıyan fon</b><p>Fiyat değişimleri fonun portföy değerini etkiler. Aynı fonun bazı tarihlerde Tera Yatırım’a ters repo ile finansman sağladığı da belgelenmiştir.</p></div>',unsafe_allow_html=True)
with b:
    st.markdown('<div class="node red"><b>Tera Yatırım: Repo borçlanan</b><p>Repo finansmanı kullanıldığı belgelidir. Alınan nakdin hangi hisse emirlerinde kullanıldığını kanıtlayan işlem bazlı veri ise bu kayıtlarda bulunmamaktadır.</p></div>',unsafe_allow_html=True)
st.markdown('<div class="notice"><b>Belgeli ilişki ≠ kanıtlanmış fiyat şişirme zinciri.</b> Repo işlemi, hisse portföyü ve piyasa fiyatları birlikte incelenebilir; ancak repo nakdinin belli hisselerin fiyatını yükseltmek için kullanıldığını kanıtlamak için nakit akışları, emir ve karşı taraf kayıtları gerekir.</div>',unsafe_allow_html=True)

st.subheader("5 · Araştırmada eksik kalan tarihsel köprüler")
st.markdown("""
- **2025 ilk yarı ve 2026 ilk yarı:** TP2 ve TLY fonlarının tam aktif/pasif hareketleri ve katılma payı giriş-çıkışları aynı tanımlarla karşılaştırılmalı.
- **2026 Ağustos–Eylül:** Fonların hisse adedi, gerçek nakit, repo alacağı ve karşı taraf detayları resmî portföy dökümleriyle eşleştirilmeli.
- **Grup şirketleri:** Tera Yatırım Bankası, Destek Faktoring ve Tera Varlık Kiralama için finansman araçları ayrı ayrı sınıflandırılmalı; kira sertifikası, repo ve doğrudan kredi birbirine karıştırılmamalı.
- **Eylül krizi:** Satış emirleri, pay blokajları ve tasfiye sırasında gerçekleşen nakit dağıtımları ayrıca belgelenmeli.
""")
st.caption("Veri ilkesi: Kaynağı bulunmayan hücrelere tahmin yazılmaz. Bu sayfadaki tarihler ve repo yönleri KAP bildirimleriyle desteklenmektedir.")
