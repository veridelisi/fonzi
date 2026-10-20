import math
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Borçla Büyüyen Portföyler | İnteraktif İnfografik", page_icon="📊", layout="wide")

START_PRICE = 100.0
HAIRCUT = 0.10
FUND_SHARES = 1_000_000
FUND_CASH = 5.0
LENDER_START_CASH = 500.0
GROUP_COLLATERAL_SHARES = 1_200_000

def amount(value):
    return f"{value:,.1f} mn TL"

def box(title, entries, color):
    lines = "".join(
        f'<div class="data-row"><span>{key}</span><b>{value}</b></div>'
        for key, value in entries
    )
    st.markdown(
        f'<div class="actor-card"><div class="actor-heading" style="border-left-color:{color}">{title}</div>{lines}</div>',
        unsafe_allow_html=True
    )

def bubble(label, value, color):
    # Global, fixed visual scale: bubbles grow as price increases.
    diameter = min(190, max(22, 22 + 168 * math.sqrt(max(0, value) / 500)))
    st.markdown(
        f'<div class="bubble-column"><div class="circle" style="width:{diameter:.1f}px;height:{diameter:.1f}px;background:{color}"></div>'
        f'<div class="bubble-name">{label}</div><div class="bubble-number">{amount(value)}</div></div>',
        unsafe_allow_html=True
    )

st.markdown("""
<style>
.block-container {max-width:1180px;padding-top:1.2rem}
.actor-card{border:1px solid #d6dce5;border-radius:13px;padding:14px;min-height:185px}
.actor-heading{border-left:6px solid;font-size:1.05rem;font-weight:800;padding-left:9px;margin-bottom:12px}
.data-row{display:flex;justify-content:space-between;gap:12px;border-bottom:1px solid #e5e7eb;padding:9px 0;font-size:.9rem}
.data-row:last-child{border:0}
.data-row b{white-space:nowrap;font-variant-numeric:tabular-nums}
.flow-card{text-align:center;border:1px solid #d6dce5;border-radius:12px;padding:13px;min-height:115px}
.flow-card strong{display:block;margin-bottom:8px}
.flow-card small{opacity:.8}
.bubble-column{display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:260px;gap:8px;text-align:center}
.circle{border-radius:50%;flex-shrink:0;box-shadow:inset -8px -12px 20px rgba(0,0,0,.09)}
.bubble-name{font-weight:650;font-size:.88rem}
.bubble-number{font-weight:800;font-variant-numeric:tabular-nums}
@media(max-width:700px){.actor-card{min-height:0}.bubble-column{height:235px}.bubble-name{font-size:.74rem}.bubble-number{font-size:.82rem}}
</style>
""", unsafe_allow_html=True)

st.title("📊 Borçla Büyüyen Portföyler")
st.write("**Kısa vadeli repo finansmanı, hisse fiyatı ve fonun gerçek nakdi arasındaki fark**")
st.caption("Varsayımsal interaktif infografik. Hiçbir gerçek kurumun danışıklı işlem yaptığı veya repo kaynaklarını hisse fiyatını yükseltmek için kullandığı bu modelle iddia edilmemektedir. Tutarlar milyon TL.")

st.subheader("1. Değerleri değiştir")
left, right = st.columns(2)
with left:
    multiple = st.slider("Hisse fiyat katsayısı (sağa çekerek artır)",1.0,5.0,1.0,0.1)
with right:
    desired_loan = st.slider("Grup şirketlerinin istediği repo borcu (mn TL)",0.0,300.0,100.0,5.0)

price = START_PRICE * multiple
collateral_market = GROUP_COLLATERAL_SHARES * price / 1_000_000
collateral_eligible = collateral_market * (1 - HAIRCUT)
loan = min(desired_loan, collateral_eligible, LENDER_START_CASH)
remaining_lender_cash = LENDER_START_CASH - loan
lender_claim = loan
group_bought = loan  # Bu senaryoda alınan repo nakdinin tamamı piyasada hisse alımına gider.
group_new_shares = loan * 1_000_000 / price
group_stock_value = collateral_market + group_bought
group_debt = loan
group_equity = group_stock_value - group_debt
fund_stock_before = FUND_SHARES * START_PRICE / 1_000_000
fund_stock_now = FUND_SHARES * price / 1_000_000
fund_nav = fund_stock_now + FUND_CASH
extra_capacity = max(0.0, collateral_eligible - loan)

if loan + 1e-9 < desired_loan:
    st.warning(f"Talep edilen reponun yalnızca {amount(loan)} tutarı teminat veya para fonu nakdi sınırı nedeniyle karşılanabilir.")

st.subheader("2. Üç aktör, üç ayrı bilanço")
a,b,c = st.columns(3)
with a:
    box("Para Piyasası Fonu",[
        ("Başlangıç nakdi",amount(LENDER_START_CASH)),
        ("Kalan nakit",amount(remaining_lender_cash)),
        ("Repo alacağı",amount(lender_claim))], "#16a34a")
with b:
    box("Borçlanan Grup Şirketi",[
        ("Repo borcu",amount(group_debt)),
        ("Teminattaki hisseler",amount(collateral_market)),
        ("Repo nakdiyle alınan hisseler",amount(group_bought))], "#dc2626")
with c:
    box("Hisseleri Elinde Tutan Fon",[
        ("Hisse adedi",f"{FUND_SHARES:,.0f}"),
        ("Hisse portföyü",amount(fund_stock_now)),
        ("Banka nakdi",amount(FUND_CASH))], "#2563eb")

st.subheader("3. Nakit akışı ve fiyat mekanizması")
f1,f2,f3 = st.columns(3)
with f1:
    st.markdown(f'<div class="flow-card"><strong>1 · Para fonu</strong>{amount(loan)} repo finansmanı verir.<br><small>Nakit azalır, repo alacağı artar.</small></div>',unsafe_allow_html=True)
with f2:
    st.markdown(f'<div class="flow-card"><strong>2 · Grup şirketi</strong>{amount(group_bought)} tutarında hisse alır.<br><small>Repo borcu grup şirketinin pasifindedir.</small></div>',unsafe_allow_html=True)
with f3:
    st.markdown(f'<div class="flow-card"><strong>3 · Hisse taşıyan fon</strong>Hisse fiyatı {price:,.0f} TL olur.<br><small>Hisse adedi ve banka nakdi değişmez.</small></div>',unsafe_allow_html=True)
st.caption("Fiyat değişimi sürgüyle varsayılıyor; model, alım tutarından otomatik fiyat etkisi hesaplamıyor. Repo teminatı grup şirketine ait hisselerdir, diğer fonun hisseleri değildir.")

st.subheader("4. Fiyat arttığında teminat kapasitesi")
m1,m2,m3,m4 = st.columns(4)
m1.metric("Teminatın piyasa değeri", amount(collateral_market))
m2.metric("%10 haircut sonrası", amount(collateral_eligible))
m3.metric("Repo borcu", amount(loan))
m4.metric("Ek teminat kapasitesi", amount(extra_capacity))
st.caption("Basitleştirilmiş örnek: Kabul edilen teminat = hisse piyasa değeri × %90. Kullanılabilecek yeni borç ayrıca karşı tarafın nakdine, limitlere ve sözleşmeye bağlıdır.")

st.subheader("5. Fonun görünen değeri büyür, nakdi aynı kalır")
compare=pd.DataFrame({
    "Gösterge":["Hisse adedi","Hisse fiyatı","Hisse portföyü","Bankadaki nakit","Fonun net varlık değeri"],
    "Başlangıç":[f"{FUND_SHARES:,.0f}",f"{START_PRICE:,.0f} TL",amount(fund_stock_before),amount(FUND_CASH),amount(fund_stock_before+FUND_CASH)],
    "Seçilen fiyat":[f"{FUND_SHARES:,.0f}",f"{price:,.0f} TL",amount(fund_stock_now),amount(FUND_CASH),amount(fund_nav)]
})
st.dataframe(compare,hide_index=True,use_container_width=True)

st.subheader("6. Piyasa değeri başka, nakit başka")
d1,d2,d3=st.columns(3)
with d1: bubble("Hisse taşıyan fonun portföyü",fund_stock_now,"#93c5fd")
with d2: bubble("Hisse taşıyan fonun nakdi",FUND_CASH,"#86efac")
with d3: bubble("Para fonunun kalan nakdi",remaining_lender_cash,"#fdba74")
st.info(f"Fonun elinde yine {FUND_SHARES:,.0f} hisse bulunuyor. Hisselerin piyasa değeri {amount(fund_stock_now)}; "
        f"ama fonun banka nakdi yalnızca {amount(FUND_CASH)}. "
        "Değerleme artışı tek başına nakit girişi değildir.")

st.subheader("7. Ekonomik sonuç")
st.write("**Repo finansmanı grup şirketinin borcunu ve para fonunun alacağını artırır.** Borçlanan şirketin hisse talebi, piyasa koşullarına bağlı olarak fiyatı etkileyebilir. Fiyatı yükselen hisseleri elinde tutan başka bir fon, hiç hisse satmadan daha yüksek NAV gösterebilir. Bu durum, fonun aynı tutarda likit nakde sahip olduğu anlamına gelmez.")
with st.expander("Varsayımlar, sınırlar ve muhasebe notları"):
    st.markdown(f"""
- Fiyat artışı sürgüyle belirlenen **varsayımdır**; gerçekleşmiş fiyat manipülasyonunu veya nedenselliği kanıtlamaz.
- Tek para fonu, tek grup şirketi ve hisseleri satmadan tutan ayrı bir fon bulunur.
- Grup şirketi başlangıçta {GROUP_COLLATERAL_SHARES:,.0f} adet teminatlık hisseye sahiptir; repo ile aldığı tutarın tamamını hisse alımına yönlendirir. Teminatlık hisseler ile yeni alınan hisseler birbirinden ayrıdır.
- Repo borcu grup şirketinin pasifinde, repo alacağı para fonunun aktifindedir. Hisse tutan fonun repo borcu varsayılmamıştır.
- Teminata sabit **%10 haircut** uygulanır. Faiz, temerrüt, değerleme farklarının realize edilmesi, işlem hacmi kaynaklı fiyat oluşumu ve kurumlar arası diğer işlemler modellenmez.
- Balon çapı tüm senaryolarda **sabit referans ölçeği** kullanır ve 190 pikselde sınırlandırılır; bu sınırın üzerindeki tutarlar için balon büyümeye devam etmez.
""")
