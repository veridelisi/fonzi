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


st.subheader("Şirketten Ortağa · Tersine Sahiplik Haritası")
st.caption("Başlangıç noktası şirketlerdir: DSTKF, KTLEV, PASEU ve ODINE. Her çizgi ilgili şirketin sermayesindeki bildirilen payı gösterir. Kaynak: kullanıcı tarafından sağlanan Matriks Analist ortaklık ekranları; ortaklık kesit tarihi görüntülerde bulunmadığından güncel veya 16 Eylül tarihli olduğu varsayılmamıştır.")
import plotly.graph_objects as go

# Şirketler (hedef) ve ortaklar (kaynak); yüzdeler ekran görüntülerinden okunmuştur.
holdings = [
    ("DSTKF","Destek Holding",73.81,"Diğer"),
    ("DSTKF","Tera Portföy Birinci Serbest Fon",8.06,"Tera fonu"),
    ("DSTKF","Diğer",7.84,"Diğer"),
    ("DSTKF","Tera Portföy Para Piyasası Fonu (TP2)",7.21,"Tera fonu"),
    ("DSTKF","Tera Yatırım Menkul Değerler",3.08,"Tera şirketi"),
    ("KTLEV","Pusula Finans Holding",29.50,"Pusula şirketi"),
    ("KTLEV","Diğer",22.55,"Diğer"),
    ("KTLEV","Pusula Portföy Üçüncü Hisse Senedi Fonu",15.90,"Pusula fonu"),
    ("KTLEV","Pusula Portföy Kuzey Hisse Senedi Fonu",15.34,"Pusula fonu"),
    ("KTLEV","Ömer Burkay",9.33,"Diğer"),
    ("KTLEV","Pusula Portföy Para Piyasası Fonu",4.26,"Pusula fonu"),
    ("KTLEV","Tera Portföy Hisse Senedi (TL) Fonu",3.12,"Tera fonu"),
    ("PASEU","Pusula Portföy Üçüncü Hisse Senedi Fonu",17.92,"Pusula fonu"),
    ("PASEU","Pasifik Holding",17.86,"Diğer"),
    ("PASEU","Pardus Portföy Yönetimi A.Ş.",17.86,"Diğer"),
    ("PASEU","Diğer",17.13,"Diğer"),
    ("PASEU","Pasifik Gayrimenkul Yatırım İnşaat",10.08,"Diğer"),
    ("PASEU","Pusula Portföy Beşinci Hisse Senedi Fonu",8.11,"Pusula fonu"),
    ("PASEU","Pusula Portföy Para Piyasası Fonu",5.24,"Pusula fonu"),
    ("PASEU","Mehmet Erdoğan",4.08,"Diğer"),
    ("ODINE","Alper Tunğa Sağ Burak",33.00,"Diğer"),
    ("ODINE","Diğer",19.49,"Diğer"),
    ("ODINE","Geylan Abdülaziz Zapsu",19.15,"Diğer"),
    ("ODINE","Pusula Portföy Üçüncü Hisse Senedi Fonu",9.93,"Pusula fonu"),
    ("ODINE","Cengiz Avcı",6.34,"Diğer"),
    ("ODINE","Fırat Kerim Ersoy",4.64,"Diğer"),
    ("ODINE","Hasan Kaytan",4.06,"Diğer"),
    ("ODINE","Feridun Geçgel",3.39,"Diğer"),
]
# Aynı isimli "Diğer" kalemleri ayrı şirketin anonim toplamını gösterir, ortak kişi değildir.
network_rows = [(ticker, (name if name!="Diğer" else "Diğer / "+ticker), pct, typ)
                for ticker,name,pct,typ in holdings]
df_ownership=pd.DataFrame(network_rows,columns=["Hisse","Ortak / fon","Sermaye payı (%)","Sınıf"])
company_y={"DSTKF":3.0,"KTLEV":2.0,"PASEU":1.0,"ODINE":0.0}
investors=list(dict.fromkeys(row[1] for row in network_rows))
# Fonların birden fazla şirketle bağlantısı ortada, kalan ortaklar kendi şirketinin yanında dizilir.
degree={n:sum(1 for _,v,_,_ in network_rows if v==n) for n in investors}
nodes=sorted(investors,key=lambda n:(-degree[n], -sum(company_y[t] for t,v,_,_ in network_rows if v==n)/degree[n],n))
investor_y={name:(len(nodes)-1-i)*3.0/max(len(nodes)-1,1) for i,name in enumerate(nodes)}
palette={"Tera fonu":"#2473bb","Tera şirketi":"#1d4ed8","Pusula fonu":"#0e906a",
         "Pusula şirketi":"#0c7560","Diğer":"#94a3b8"}
fig=go.Figure()
for ticker,owner,pct,typ in network_rows:
    y0=investor_y[owner];y1=company_y[ticker]
    fig.add_trace(go.Scatter(x=[0,1],y=[y0,y1],mode="lines",
        line=dict(color=palette[typ],width=max(1.3,min(pct/15,5))),
        customdata=[[ticker,owner,pct],[ticker,owner,pct]],
        hovertemplate="<b>%{customdata[1]}</b> → <b>%{customdata[0]}</b><br>Sermaye payı: %%{customdata[2]:.2f}<extra></extra>",
        showlegend=False))
for name in investors:
    typ=next(z for t,n,p,z in network_rows if n==name)
    fig.add_trace(go.Scatter(x=[0],y=[investor_y[name]],mode="markers+text",
        marker=dict(size=11,color=palette[typ]),text=[name],textposition="middle left",
        hovertemplate=name+"<extra></extra>",showlegend=False,textfont=dict(size=10)))
for ticker,y in company_y.items():
    fig.add_trace(go.Scatter(x=[1],y=[y],mode="markers+text",
       marker=dict(size=31,color="#e18a37",line=dict(color="white",width=1.5)),
       text=[ticker],textposition="middle right",hovertemplate=ticker+"<extra></extra>",
       showlegend=False,textfont=dict(size=14)))
fig.update_layout(height=820,margin=dict(l=295,r=110,t=30,b=20),
    xaxis=dict(visible=False,range=[-0.05,1.15]),yaxis=dict(visible=False,range=[-0.17,3.17]),
    paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
    hovermode="closest",dragmode=False)
st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
st.caption("Mavi: Tera bağlantılı doğrudan ortak/fon · Yeşil: Pusula fonu/şirketi · Gri: diğer yatırımcılar · Turuncu: hisseler. Çizgi kalınlığı pay oranını kabaca gösterir; ok yönü ortaktan hisseye doğrudur.")
st.markdown("**Ortaklıkları şirket bazında inceleyin:**")
for ticker in company_y:
    chunk=df_ownership[df_ownership["Hisse"]==ticker].copy()
    chunk["Sermaye payı (%)"]=chunk["Sermaye payı (%)"].map(lambda v:f"%{v:.2f}".replace(".",","))
    st.markdown(f"**{ticker}**")
    st.dataframe(chunk[["Ortak / fon","Sermaye payı (%)","Sınıf"]],hide_index=True,use_container_width=True)
st.warning("Bu oranlar pay sahipliğini gösterir; portföy yönetimi ile nihai ekonomik mülkiyet veya ortaklar arasında koordinasyon olduğu sonucu çıkarılamaz. 'Diğer' payları ayrı bir kişi/kurum değil, ilgili şirketin toplulaştırılmış kalan kısmıdır. Matriks verilerinin geçerlilik tarihi ayrıca teyit edilmelidir.")
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
