import streamlit as st
import pandas as pd

st.set_page_config(page_title="Fonzi | Şişen hisse, azalan nakit", page_icon="🎈", layout="wide")

st.title("🎈 Fonzi: Hisse Şişiyor, Nakit Nerede?")
st.write("**Hisse alımı → fiyat yükselişi → daha yüksek teminat → ilişkili para fonundan repo → yeniden hisse alımı.**")
st.caption("Varsayımsal finansal döngü simülasyonu. Gerçek Tera veya Pusula işlemlerinin ya da danışıklı işlem iddiasının kanıtı değildir. Tutarlar milyon TL.")

st.subheader("🎛️ Senaryoyu değiştir")
c1,c2,c3=st.columns(3)
with c1:
    fund_initial=st.slider("Hisse fonunun başlangıç nakdi",100,1000,200,50)
    initial_buy_pct=st.slider("Başlangıç nakdinin yüzde kaçı hisseye gitsin?",10,100,75,5)
with c2:
    rounds=st.slider("Repo ve yeni alım döngüsü sayısı",1,8,4)
    price_gain=st.slider("Her turda hisse fiyatı yüzde kaç artsın?",0,100,30,5)
with c3:
    loan_ratio=st.slider("Teminatın kaçta kaçı kadar borç verilsin? (%)",20,90,70,5)
    lender_initial=st.slider("İlişkili para fonunun başlangıç nakdi",100,2000,700,50)

with st.expander("Gelişmiş varsayım"):
    buy_with_repo=st.slider("Yeni repo nakdinin yüzde kaçıyla hisse alınsın?",0,100,100,10)

# Sahip olunan hisse, mevcut piyasa fiyatı ile yeniden değerlenir.
# Borçlanma üst sınırı: teminata ayrılabilen toplam hisselerin güncel değeri * kabul oranı.
# Repo borcu her yeni turda artar; mevcut borç kapasiteden mahsup edilir.
# Finansörün toplam nakdi de doğal bir üst sınırdır.
cash=float(fund_initial)
price=1.0
shares=float(fund_initial)*initial_buy_pct/100
cash-=shares
debt=0.0
lender_cash=float(lender_initial)
lender_claim=0.0
rows=[]
def record(label, new_loan=0.0, spent=0.0):
    stock=shares*price
    rows.append({
        "Tur":label, "Hisse fiyatı":price, "Hisse portföyü":stock,
        "Fondaki nakit":cash, "Repo borcu":debt,
        "Fonun net değeri (NAV)":cash+stock-debt,
        "Para fonu nakdi":lender_cash, "Para fonu repo alacağı":lender_claim,
        "Bu tur yeni repo":new_loan,"Bu tur hisse alımı":spent
    })
record("İlk alım")
for i in range(1,rounds+1):
    price*=1+price_gain/100
    capacity=shares*price*loan_ratio/100
    new_loan=max(0.0,min(capacity-debt,lender_cash))
    cash+=new_loan
    debt+=new_loan
    lender_cash-=new_loan
    lender_claim+=new_loan
    spent=new_loan*buy_with_repo/100
    cash-=spent
    if price>0:
        shares+=spent/price
    record(f"{i}. repo turu",new_loan,spent)

df=pd.DataFrame(rows)
end=rows[-1]
stock=end["Hisse portföyü"]
nav=end["Fonun net değeri (NAV)"]
st.divider()
m1,m2,m3,m4=st.columns(4)
m1.metric("📈 Hisse portföyünün piyasa değeri",f"{stock:,.1f} mn TL")
m2.metric("💵 Hisse fonunda kalan nakit",f"{cash:,.1f} mn TL")
m3.metric("🏦 Repo borcu",f"{debt:,.1f} mn TL")
m4.metric("📊 Fonun net değeri (NAV)",f"{nav:,.1f} mn TL")

st.info(
    f"Hisse fonunun portföyündeki hisselerin ekranda görünen piyasa değeri **{stock:,.1f} milyon TL**. "
    f"Ama bankadaki kullanılabilir nakdi yalnızca **{cash:,.1f} milyon TL**. "
    f"İlişkili para fonundan alınmış toplam repo borcu ise **{debt:,.1f} milyon TL**. "
    "Hisselerin değerlenmesi, fonun kasasına kendiliğinden para girdiği anlamına gelmez."
)

st.subheader("Büyüme döngüsü — bütün turlar aynı ekranda")
show=df[["Tur","Hisse fiyatı","Hisse portföyü","Fondaki nakit","Bu tur yeni repo","Repo borcu","Fonun net değeri (NAV)"]].copy()
for column in show.columns[1:]:
    show[column]=show[column].round(1)
st.dataframe(show,hide_index=True,use_container_width=True)

st.subheader("Şişen portföy ve biriken borç")
chart=df.set_index("Tur")[["Hisse portföyü","Fondaki nakit","Repo borcu"]]
st.line_chart(chart)

def t_balance(title, asset_rows, liability_rows):
    a,b=st.columns(2)
    ta=sum(v for _,v in asset_rows)
    tp=sum(v for _,v in liability_rows)
    st.markdown(f"**{title}**")
    with a:
        st.markdown("**AKTİF (Varlıklar)**")
        st.dataframe(pd.DataFrame(asset_rows+[("TOPLAM",ta)],columns=["Kalem","Milyon TL"]),hide_index=True,use_container_width=True)
    with b:
        st.markdown("**PASİF (Borçlar + Özkaynak)**")
        st.dataframe(pd.DataFrame(liability_rows+[("TOPLAM",tp)],columns=["Kalem","Milyon TL"]),hide_index=True,use_container_width=True)

st.subheader("T-Balance: Para nerede, borç kimde?")
x,y=st.columns(2)
with x:
    st.markdown("### Hisse fonu")
    st.write("**Aktif:**",f"Nakit {cash:,.1f} + hisseler {stock:,.1f} = {cash+stock:,.1f} mn TL")
    st.write("**Pasif:**",f"Repo borcu {debt:,.1f} + NAV {nav:,.1f} = {debt+nav:,.1f} mn TL")
with y:
    st.markdown("### İlişkili para piyasası fonu")
    st.write("**Aktif:**",f"Nakit {lender_cash:,.1f} + repo alacağı {lender_claim:,.1f} = {lender_initial:,.1f} mn TL")
    st.write("**Pasif:**",f"Fon katılımcılarının özkaynağı {lender_initial:,.1f} mn TL")
st.caption("Repo alacağı nakit değildir. Para fonunun repo finansmanı sağlaması kendi yatırımcılarına karşı yükümlülüklerini ortadan kaldırmaz.")

with st.expander("Modelin sınırları ve gerçek Tera bağlantısı"):
    st.markdown("""
- Fiyat artışı her turda dışarıdan verilen bir **senaryo varsayımıdır**. Oyunda hisse alımından fiyat artışına geçiş, gerçek emir defteri verisiyle kurulmuş bir nedensellik kanıtı değildir.
- Bütün hisselerin ek teminata uygun olduğu ve tüm reponun tek finansör tarafından verildiği varsayılır. Faiz, teminat değerleme indirimi dışında diğer koşullar, vadeler ve olası temerrüt hesaba katılmamıştır.
- Gerçek KAP işlemlerinde Tera Yatırım'ın TLY/TP2 ve Pusula fonlarından borçlandığı örnekler vardır. Buradaki **hisse fonunun doğrudan borçlanması** şeması, bu işlemlerle birebir aynı değildir.
- Fiyat artışı NAV'ı büyütebilir; repo borcuyla alınan nakit ise kendi başına NAV'ı büyütmez. Fiyat yükselişi nakit yaratmaz.
""")
