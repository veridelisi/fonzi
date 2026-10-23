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


st.subheader("Tera ve Tera Bağlantılı Fonların Hisse Sahiplik Ağı")
st.caption("Önceki görünüm: solda ortaklar, sağda hisseler. Bağlantı üzerindeki oran, şirketin toplam sermayesinde ilgili ortağın payını gösterir. Tıklama ile filtreleme yoktur.")
import plotly.graph_objects as go
import textwrap

# Kaynak: kullanıcı tarafından gönderilen Matriks Analist DSTKF ve KTLEV ortaklık ekranları.
# Ekranların sahiplik kesit tarihi bilinmiyor.
holdings = [
    ("DSTKF", "Tera Portföy Birinci Serbest Fon", 8.06, "Tera fonu"),
    ("DSTKF", "Tera Portföy Para Piyasası Fonu (TP2)", 7.21, "Tera fonu"),
    ("DSTKF", "Tera Yatırım Menkul Değerler", 3.08, "Tera şirketi"),
    ("KTLEV", "Tera Portföy Hisse Senedi (TL) Fonu", 3.12, "Tera fonu"),
]
df_ownership = pd.DataFrame(holdings, columns=["Hisse", "Ortak / fon", "Pay (%)", "Tür"])
investors = list(dict.fromkeys(r[1] for r in holdings))
companies = list(dict.fromkeys(r[0] for r in holdings))
investor_y = {name: 3-i for i,name in enumerate(investors)}
company_y = {"DSTKF": 2.0, "KTLEV": 0.0}
colors = {"Tera fonu":"#2369c9", "Tera şirketi":"#0e8274"}

fig=go.Figure()
for ticker,owner,pct,typ in holdings:
    y0,y1=investor_y[owner],company_y[ticker]
    color=colors[typ]
    fig.add_trace(go.Scatter(
        x=[0.52,0.84],y=[y0,y1],mode="lines",
        line=dict(color=color,width=3.1),
        hovertemplate=f"{owner} → {ticker}: %{pct:.2f}<extra></extra>",
        showlegend=False))
    # Kalın yüzdelik etiket, tam çizginin üzerinde ve beyaz zeminde.
    x_pct = 0.73
    y_pct = y0+(y1-y0)*(x_pct-0.52)/(0.84-0.52)
    fig.add_annotation(x=x_pct,y=y_pct,
        text=f"<b>%{pct:.2f}</b>".replace(".",","),
        showarrow=False,bgcolor="#ffffff",bordercolor=color,
        borderwidth=1.8,borderpad=6,
        font=dict(size=17,color="#152338"),xanchor="center",yanchor="middle")
for owner in investors:
    typ=next(t for _,n,_,t in holdings if n==owner)
    fig.add_trace(go.Scatter(x=[0.52],y=[investor_y[owner]],mode="markers",
        marker=dict(size=18,color=colors[typ]),hovertemplate=owner+"<extra></extra>",showlegend=False))
    label="<br>".join(textwrap.wrap(owner,width=33,break_long_words=False))
    fig.add_annotation(x=0.48,y=investor_y[owner],text=label,showarrow=False,
        xanchor="right",yanchor="middle",align="right",font=dict(size=13,color="#24344b"))
for ticker,y in company_y.items():
    fig.add_trace(go.Scatter(x=[0.84],y=[y],mode="markers",
        marker=dict(size=29,color="#e58b36",line=dict(width=2,color="white")),
        hovertemplate=ticker+"<extra></extra>",showlegend=False))
    fig.add_annotation(x=0.88,y=y,text=f"<b>{ticker}</b>",showarrow=False,
        xanchor="left",font=dict(size=17,color="#24344b"))
fig.update_layout(height=590,margin=dict(l=12,r=12,t=25,b=25),
    xaxis=dict(visible=False,range=[0,1]),yaxis=dict(visible=False,range=[-0.6,3.6]),
    paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
    dragmode=False)
st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
st.caption("Mavi: Tera fonları · Yeşil: Tera şirketi · Turuncu: hisseler. Kalın çerçeveli yüzdeler daima görünür.")
shown=df_ownership.copy()
shown["Pay (%)"]=shown["Pay (%)"].map(lambda x:f"%{x:.2f}".replace(".",","))
st.dataframe(shown[["Hisse","Ortak / fon","Pay (%)"]],hide_index=True,use_container_width=True)
st.caption("Kaynak: Gönderilen Matriks Analist DSTKF ve KTLEV ortaklık ekranları. Ekranlarda kesit tarihi yer almıyor; rakamlar belirli bir günün güncel sahiplikleri olarak yorumlanmamalı. PASEU ve ODINE ekranlarında Tera bağlantılı büyük ortak belirtilmediği için gösterilmedi.")
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
