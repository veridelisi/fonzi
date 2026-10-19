import streamlit as st
import pandas as pd

st.set_page_config(page_title="Fonzi | Repo ile büyüyen fon", page_icon="📈", layout="wide")
st.title("Fonzi | Repo ile büyüyen fon nasıl kırılgan olur?")
st.caption("Eğitim amaçlı varsayımsal model. Gerçek Tera, Pusula veya başka kurumların bu işlemleri yaptığına ilişkin bir tespit değildir. Tüm parasal tutarlar milyon TL.")

st.markdown("""
<style>
[data-testid="stMetricValue"] {font-size:1.65rem;}
.t-box{border:1px solid #a0a8b3;border-radius:9px;overflow:hidden;margin:8px 0 18px}
.t-title{text-align:center;font-weight:750;padding:10px;background:rgba(135,150,160,.12)}
.t-head,.t-body,.t-footer{display:grid;grid-template-columns:1fr 1fr}
.t-head{border-bottom:3px solid currentColor;font-weight:750;text-align:center}
.t-head>div{padding:8px 4px;font-size:.82rem}
.t-head>div:first-child,.t-side:first-child,.t-footer>div:first-child{border-right:2px solid #a0a8b3}
.t-side{min-height:110px;padding:9px}
.t-row,.t-footer>div{display:flex;justify-content:space-between;gap:8px;padding:7px 2px;font-size:.88rem}
.t-row b,.t-footer b{white-space:nowrap;font-variant-numeric:tabular-nums}
.t-footer{border-top:2px solid currentColor;background:rgba(135,150,160,.08);font-weight:750}
.t-footer>div{padding:10px}
@media(max-width:640px){.t-row,.t-footer>div{font-size:.72rem}.t-side{padding:5px}.t-footer>div{padding:6px}}
</style>
""", unsafe_allow_html=True)

def t_balance(title, assets, liabilities):
    def rows(items):
        return "".join(f'<div class="t-row"><span>{label}</span><b>{value:,.1f}</b></div>' for label,value in items)
    ta=sum(x for _,x in assets)
    tp=sum(x for _,x in liabilities)
    st.markdown(f"""
    <div class="t-box"><div class="t-title">{title}</div>
    <div class="t-head"><div>AKTİF</div><div>PASİF</div></div>
    <div class="t-body"><div class="t-side">{rows(assets)}</div><div class="t-side">{rows(liabilities)}</div></div>
    <div class="t-footer"><div><span>TOPLAM</span><b>{ta:,.1f}</b></div><div><span>TOPLAM</span><b>{tp:,.1f}</b></div></div></div>
    """,unsafe_allow_html=True)

st.subheader("🎛️ Değerleri değiştir, sonucu hemen gör")
u1,u2,u3=st.columns(3)
with u1:
    initial_cash=st.slider("Hisse fonunun başlangıç nakdi (mn TL)",50,500,100,10)
    first_buy=st.slider("İlk hisse alımı (mn TL)",0,initial_cash,60,5)
with u2:
    price_multiple=st.slider("İlk alımdan sonra fiyat kaç katına çıksın?",1.0,5.0,2.0,0.1)
    repo_requested=st.slider("Repo ile alınmak istenen borç (mn TL)",0,300,60,5)
with u3:
    fall_pct=st.slider("Ardından hisse fiyatı yüzde kaç düşsün?",0,90,50,5)
    min_collateral=st.slider("Gerekli teminat oranı (%)",100,200,105,5)/100

with st.expander("Diğer varsayımlar"):
    lender_initial=st.slider("Para piyasası fonunun başlangıç nakdi (mn TL)",100,1000,200,25)
    new_buy_pct=st.slider("Repo nakdinin yüzde kaçıyla yeniden hisse alınsın?",0,100,100,10)/100

# Teminat kabulünü tüm ilk alım hisseleri üzerinden ve repo günündeki fiyatla hesapla.
# Repo oranının limiti aşması halinde işlem yapılamaz; fiili borç hesaplanır.
initial_price=1.0
shares_first=first_buy/initial_price
elevated_price=initial_price*price_multiple
pledged_market_value=shares_first*elevated_price
repo_capacity=pledged_market_value/min_collateral if min_collateral else 0
actual_repo=min(float(repo_requested),repo_capacity,float(lender_initial))
spent=actual_repo*new_buy_pct
additional_shares=spent/elevated_price
cash_before_fall=initial_cash-first_buy+actual_repo-spent
shares_total=shares_first+additional_shares
final_price=elevated_price*(1-fall_pct/100)
stock_before=shares_total*elevated_price
stock_after=shares_total*final_price
nav_before=cash_before_fall+stock_before-actual_repo
nav_after=cash_before_fall+stock_after-actual_repo
collateral_after=shares_first*final_price
required_collateral=actual_repo*min_collateral
margin_gap=max(0.0,required_collateral-collateral_after)
cash_gap=max(0.0,actual_repo-cash_before_fall)
lender_cash=lender_initial-actual_repo
lender_receivable=actual_repo

if actual_repo + 1e-8 < repo_requested:
    st.warning(f"Talep edilen {repo_requested:,.1f} mn TL repo borcunun yalnızca {actual_repo:,.1f} mn TL'si teminat/finansör nakdi sınırları içinde gerçekleşebilir. Hesaplar gerçekleşebilir tutarı kullanıyor.")

k1,k2,k3,k4,k5=st.columns(5)
k1.metric("Hisse fiyatı (son)",f"{final_price:.2f} TL",f"%{-fall_pct} (zirveden)")
k2.metric("Fon NAV (son)",f"{nav_after:,.1f} mn TL",f"{nav_after-nav_before:+,.1f} mn TL")
k3.metric("Repo borcu",f"{actual_repo:,.1f} mn TL")
k4.metric("Hisse portföyü",f"{stock_after:,.1f} mn TL")
k5.metric("Vade günü nakit açığı",f"{cash_gap:,.1f} mn TL")

st.caption(f"İlk hisse alımı: {first_buy:,.1f} mn TL • Yükseliş sonrası ilk hisselerin değeri: {pledged_market_value:,.1f} mn TL • "
           f"Yeni hisse alımı: {spent:,.1f} mn TL • Zirvede NAV: {nav_before:,.1f} mn TL")

if cash_gap>0:
    st.warning(f"Repo yenilenmezse {actual_repo:,.1f} milyon TL anapara ödenecek; elde {cash_before_fall:,.1f} milyon TL nakit var. "
               f"{cash_gap:,.1f} milyon TL başka kaynaktan bulunmalı. Bu otomatik iflas anlamına gelmez.")

st.subheader("T-Balance | Kriz sonrasındaki pozisyonlar")
left,right=st.columns(2)
with left:
    t_balance("Hisse Fonu",
              [("Banka nakdi",cash_before_fall),("İlk alınan hisseler",shares_first*final_price),("Borçla alınan hisseler",additional_shares*final_price)],
              [("Repo borcu",actual_repo),("Fon özkaynağı (NAV)",nav_after)])
with right:
    t_balance("Para Piyasası Fonu — Repo Finansörü",
              [("Banka nakdi",lender_cash),("Repo alacağı",lender_receivable)],
              [("Fon katılımcı özkaynağı",lender_initial)])

st.caption("Teminattaki ilk hisseler ikinci kez varlık yazılmamıştır. Repo alacağı teminat veya karşı taraf zararından etkilenebilir; tahsilat garanti değildir.")
st.subheader("Fiyat ve kaldıraç etkisi")
fig=pd.DataFrame({
    "Önce":[initial_cash,0,0],
    "Fiyat yükseldiğinde":[initial_cash-first_buy,first_buy*price_multiple,0],
    "Repo ve yeni alım sonrası":[cash_before_fall,stock_before,actual_repo],
    "Düşüş sonrası":[cash_before_fall,stock_after,actual_repo]
},index=["Nakit","Hisseler","Repo borcu"]).T
st.bar_chart(fig)
st.caption("Grafikte nakit ve hisse varlıkları ile repo borcu birlikte gösterilir. Repo borcu varlık değil, yükümlülüktür.")

with st.expander("Teknik ayrıntı: Teminat yeterliliği"):
    st.write(f"Teminatın son değeri: **{collateral_after:,.1f} milyon TL** | Gereken değer: **{required_collateral:,.1f} milyon TL**")
    if margin_gap > 0:
        st.warning(f"Teminat açığı: {margin_gap:,.1f} milyon TL. Ek teminat veya borç azaltımı gerekebilir.")
    elif actual_repo > 0:
        st.success("Teminat bu varsayımlarda yeterli.")
    else:
        st.info("Repo borcu bulunmuyor.")

with st.expander("İşlem sırası ve hesaplama notları"):
    st.markdown(f"""
1. Fonun bankada **{initial_cash:,.1f} milyon TL** nakdi var.
2. **{first_buy:,.1f} milyon TL** hisse alıyor; satıcıya nakit gidiyor.
3. Hisse fiyatı **{price_multiple:.1f} katına** yükseliyor (varsayımsal piyasa senaryosu).
4. İlk alınan hisseler repo teminatı olarak ayrılıyor; en fazla kabul edilen teminat / gerekli teminat oranı kadar ve finansörün nakdiyle sınırlı borçlanılıyor.
5. Repo nakdinden **{spent:,.1f} milyon TL** yeniden hisse alımına gidiyor.
6. Hisse fiyatı zirveden **%{fall_pct}** düşüyor. Borç anaparası sabit kalırken fon varlıklarının değeri azalıyor.

**İki ayrı açık:** Teminat açığı = max(0, repo borcu × gerekli teminat oranı − ilk hisselerin son piyasa değeri). 
Nakit açığı = max(0, repo borcu − bankadaki nakit). Faiz, komisyon, vergiler, fiyat etkisinin gerçek emir akışı, teminat iskonto kuralları ve yatırımcı iadeleri bu sürümde yoktur.

**Gerçek Tera ağı ile fark:** KAP'taki bazı işlemlerde Tera Yatırım nakit borçlanan, TLY/TP2/Pusula fonları nakit veren taraftadır. 
Buradaki doğrudan *hisse fonu → para fonu* repo işlemi gerçek işlemlerin birebir bilanço aktarımı değildir.
""")
