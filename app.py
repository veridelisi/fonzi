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


st.subheader("Tera Bağlantılı Fonların Hisse Sahiplik Ağı")
st.caption("Bir fonun veya hisse kodunun üzerine tıklayın: yalnızca seçilen aktör ve doğrudan ortaklık bağlantıları görünür. Oranlar şirketin TOPLAM sermayesi içindeki paylardır.")
import plotly.graph_objects as go
import textwrap

# Matriks Analist ekranlarından birebir okunmuş, yalnızca Tera bağlantılı ortaklar.
# Ekranlarda ortaklık kesit tarihi belirtilmemiştir.
holdings = [
    ("DSTKF", "Tera Portföy Birinci Serbest Fon", 8.06, "Fon"),
    ("DSTKF", "Tera Portföy Para Piyasası Fonu (TP2)", 7.21, "Fon"),
    ("DSTKF", "Tera Yatırım Menkul Değerler", 3.08, "Şirket"),
    ("KTLEV", "Tera Portföy Hisse Senedi (TL) Fonu", 3.12, "Fon"),
]
df_ownership = pd.DataFrame(holdings, columns=["Hisse", "Ortak / fon", "Sermaye payı (%)", "Tür"])
names = list(dict.fromkeys([row[1] for row in holdings] + [row[0] for row in holdings]))
if "ownership_focus" not in st.session_state:
    st.session_state.ownership_focus = None
if "ownership_graph_version" not in st.session_state:
    st.session_state.ownership_graph_version = 0

focus = st.session_state.ownership_focus
visible = [r for r in holdings if focus is None or focus in (r[0], r[1])]
visible_investors = list(dict.fromkeys(r[1] for r in visible))
visible_companies = list(dict.fromkeys(r[0] for r in visible))
N = max(len(visible_investors), len(visible_companies))
height = max(430, N * 105 + 110)
left_y = {name: (len(visible_investors)-1-i) for i,name in enumerate(visible_investors)}
right_y = {name: (len(visible_companies)-1-i) * max(len(visible_investors)-1,1)/max(len(visible_companies)-1,1)
           for i,name in enumerate(visible_companies)}
fig = go.Figure()

# Çizgi yüzdelerini sabit, büyük ve çizginin üzerinde göster.
for ticker, owner, pct, kind in visible:
    y0, y1 = left_y[owner], right_y[ticker]
    color = "#2563eb" if kind == "Fon" else "#0f766e"
    fig.add_trace(go.Scatter(
        x=[0.49,0.82], y=[y0,y1], mode="lines",
        line=dict(color=color,width=2.7),hoverinfo="skip",
        showlegend=False))
    xmid=0.68
    ymid=y0+(y1-y0)*(xmid-0.49)/(0.82-0.49)
    fig.add_trace(go.Scatter(
        x=[xmid],y=[ymid],mode="markers+text",
        marker=dict(size=25,color="rgba(255,255,255,0.92)",line=dict(width=0)),
        text=[f"<b>%{pct:.2f}</b>".replace(".",",")],
        textposition="middle center",textfont=dict(size=15,color=color),
        hovertemplate=f"{owner} → {ticker}: %{pct:.2f}<extra></extra>",
        showlegend=False))
# İsimler bu kez kesilmesin: grafik içi etiket, ortanın sağına kadar uzanmaz.
for owner in visible_investors:
    name_lines="<br>".join(textwrap.wrap(owner, 30,break_long_words=False))
    fig.add_trace(go.Scatter(
        x=[0.47], y=[left_y[owner]],mode="markers+text",
        marker=dict(color="#2563eb" if "Fon" in owner else "#0f766e",size=21),
        text=[name_lines],textposition="middle left",textfont=dict(size=12,color="#334155"),
        customdata=[owner],hovertemplate="Seç: "+owner+"<extra></extra>",
        selected=dict(marker=dict(size=25)),showlegend=False))
for ticker in visible_companies:
    fig.add_trace(go.Scatter(
        x=[0.84],y=[right_y[ticker]],mode="markers+text",
        marker=dict(color="#ea8a30",size=26),
        text=[ticker],textposition="middle right",textfont=dict(size=16,color="#334155"),
        customdata=[ticker],hovertemplate="Seç: "+ticker+"<extra></extra>",
        selected=dict(marker=dict(size=30)),showlegend=False))
fig.update_layout(
    height=height,margin=dict(l=15,r=12,t=35,b=35),
    xaxis=dict(visible=False,range=[0,1]),
    yaxis=dict(visible=False,range=[-0.45,max(len(visible_investors)-1,1)+0.45]),
    clickmode="event+select",dragmode=False,
    paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")

event = st.plotly_chart(
    fig,use_container_width=True,config={"displayModeBar":False},
    on_select="rerun",selection_mode="points",
    key=f"tera_sahiplik_{st.session_state.ownership_graph_version}")
points = event.selection.points if event is not None else []
clicked = next((p.get("customdata") for p in points if isinstance(p.get("customdata"),str) and p.get("customdata") in names),None)
if clicked is not None and clicked != focus:
    st.session_state.ownership_focus = clicked
    st.session_state.ownership_graph_version += 1
    st.rerun()
if focus:
    st.markdown(f"**Seçilen: {focus}** — yalnızca doğrudan ilişkiler gösteriliyor.")
    if st.button("↩ Tüm ağı göster",key="tera_reset"):
        st.session_state.ownership_focus = None
        st.session_state.ownership_graph_version += 1
        st.rerun()
else:
    st.caption("Mavi: Tera fonları · Yeşil: Tera şirketi · Turuncu: hisseler. Düğümün üzerine tıklayarak ağı süzebilirsiniz.")

shown = pd.DataFrame(visible,columns=["Hisse","Tera bağlantılı ortak","Pay (%)","Tür"])
shown["Pay (%)"] = shown["Pay (%)"].map(lambda x:f"%{x:.2f}".replace(".",","))
st.dataframe(shown[["Hisse","Tera bağlantılı ortak","Pay (%)"]],use_container_width=True,hide_index=True)
st.caption("Kaynak: Kullanıcının paylaştığı Matriks Analist DSTKF ve KTLEV ortaklık ekranları. Kesit tarihi belirsizdir. PASEU ve ODINE ekranlarında doğrudan Tera bağlantılı büyük ortak listelenmediği için bu grafikte yoktur. Fon yatırımcısı ile fonun portföy mülkiyeti aynı şey değildir.")
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
