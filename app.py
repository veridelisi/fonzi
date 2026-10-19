import streamlit as st
import pandas as pd

st.set_page_config(page_title="Fonzi | Repo ve Teminat Krizi", page_icon="🎮", layout="wide")

# Eğitim amaçlı basitleştirilmiş model. Bütün tutarlar milyon TL'dir.
# Gerçek kurumlara ilişkin işlem veya manipülasyon iddiası içermez.
INITIAL = {
    "day": 1, "cash": 20.0, "free_shares": 50.0,
    "pledged_shares": 150.0, "price": 1.0, "debt": 100.0,
    "lender_cash": 900.0, "lender_receivable": 100.0,
    "history": [], "events": []
}

def reset():
    for key, value in INITIAL.items():
        st.session_state[key] = value.copy() if isinstance(value, list) else value
    log("Başlangıç", "Fon: 20 nakit + 50 serbest hisse + 150 teminatta hisse; 100 repo borcu. Karşı taraf: 900 nakit + 100 repo alacağı.")

def log(action, detail):
    st.session_state.events.append({"Gün": st.session_state.day, "İşlem": action, "Açıklama": detail})
    save_snapshot()

def save_snapshot():
    s = st.session_state
    s.history.append({
        "Gün": s.day, "İşlem no": len(s.events),
        "Hisse fiyatı": s.price, "Nakit": s.cash,
        "Hisseler": (s.free_shares + s.pledged_shares) * s.price,
        "Repo borcu": s.debt, "Özkaynak (NAV)": nav(),
        "Teminat değeri": s.pledged_shares * s.price,
        "Teminat açığı": shortfall()
    })

def nav():
    s = st.session_state
    return s.cash + (s.free_shares + s.pledged_shares) * s.price - s.debt

def collateral_limit():
    s = st.session_state
    return s.pledged_shares * s.price * haircut

def shortfall():
    return max(0.0, st.session_state.debt - collateral_limit())

if "events" not in st.session_state:
    # İlk sürümde başlangıç verileri modelin tüm kullanıcıları için örnektir.
    for key, value in INITIAL.items():
        st.session_state[key] = value.copy() if isinstance(value, list) else value

st.title("🎮 Fonzi: Repo Rollover ve Teminat Döngüsü")
st.caption("Tera fon krizi üzerine araştırma için hazırlanmış VARSAYIMSAL mekanizma simülasyonu. Tutarlar gerçek kurum verileri değildir.")
st.info("Amaç: fiyat artışı → teminat kapasitesi → borçlanma → hisse alımı döngüsünü ve tersine dönüşünü bilançolarla görmek. Fiyat düğmeleri piyasa olaylarını temsil eder; manipülasyonun kanıtı değildir.")

with st.sidebar:
    st.header("Model varsayımları")
    haircut = st.slider("Kabul edilen teminat oranı (%)", 20, 100, 70, 5) / 100
    annual_rate = st.slider("Yıllık repo faizi (%)", 0.0, 100.0, 43.0, 0.5) / 100
    st.caption("Basit günlük faiz: yıllık oran / 365. Teminat oranı tüm simülasyonda ortak varsayılır.")
    if st.button("🧹 Oyunu sıfırla", use_container_width=True):
        reset()
        st.rerun()

s = st.session_state
assets = s.cash + (s.free_shares + s.pledged_shares) * s.price
equity = nav()
capacity = max(0.0, collateral_limit() - s.debt)
gap = shortfall()

a, b, c, d, e = st.columns(5)
a.metric("Gün", s.day)
b.metric("Fon aktifleri", f"{assets:,.2f} mn TL")
c.metric("Repo borcu", f"{s.debt:,.2f} mn TL")
d.metric("Özkaynak / NAV", f"{equity:,.2f} mn TL")
e.metric("Teminat açığı", f"{gap:,.2f} mn TL")
st.caption(f"Hisse fiyatı: {s.price:.3f} TL (başlangıç 1 TL) | Kullanılabilir ek repo kapasitesi: {capacity:,.2f} mn TL | Varsayımsal yıllık faiz: %{annual_rate * 100:g}")

if gap > 0.000001:
    st.error(f"⚠️ Teminat açığı: {gap:,.2f} mn TL. Yeni borçlanma kapalı; ek teminat veya geri ödeme gerekiyor.")
if equity < 0:
    st.error("⚠️ Fonun model özkaynağı negatif: borçlar varlıkların değerini aşıyor.")

st.subheader("T-Balance | Karşılıklı Bilançolar")

def t_balance(title, assets_rows, liabilities_rows):
    """Aktif ve pasifi aynı yatay çizginin altında gösteren T bilanço."""
    def side(rows):
        return "".join(
            f'<div class="t-row"><span>{name}</span><strong>{value:,.2f}</strong></div>'
            for name, value in rows
        )
    left_total = sum(value for _, value in assets_rows)
    right_total = sum(value for _, value in liabilities_rows)
    st.markdown(f"""
    <div class="t-sheet">
      <div class="t-title">{title}</div>
      <div class="t-head"><div>AKTİF (VARLIKLAR)</div><div>PASİF (BORÇ + ÖZKAYNAK)</div></div>
      <div class="t-body">
        <div class="t-side">{side(assets_rows)}</div>
        <div class="t-side">{side(liabilities_rows)}</div>
      </div>
      <div class="t-foot">
        <div><span>TOPLAM AKTİF</span><strong>{left_total:,.2f}</strong></div>
        <div><span>TOPLAM PASİF</span><strong>{right_total:,.2f}</strong></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<style>
.t-sheet { border:1px solid #99a4b3; border-radius:11px; margin:9px 0 18px; overflow:hidden; }
.t-title { padding:12px 14px; font-weight:750; font-size:1.07rem; text-align:center; background:rgba(120,140,160,.10); }
.t-head,.t-body,.t-foot { display:grid; grid-template-columns:1fr 1fr; }
.t-head { border-bottom:3px solid currentColor; font-size:.83rem; font-weight:750; text-align:center; }
.t-head > div { padding:9px 5px; }
.t-head > div:first-child,.t-body > div:first-child,.t-foot > div:first-child { border-right:2px solid #99a4b3; }
.t-side { padding:8px 11px; min-height:136px; }
.t-row,.t-foot > div { display:flex; justify-content:space-between; gap:9px; padding:7px 1px; font-size:.88rem; }
.t-row strong,.t-foot strong { white-space:nowrap; font-variant-numeric:tabular-nums; }
.t-foot { border-top:2px solid currentColor; background:rgba(120,140,160,.08); font-weight:750; }
.t-foot > div { padding:10px 12px; }
@media(max-width:640px) {
  .t-side { padding:6px; } .t-row,.t-foot > div { font-size:.73rem; gap:4px; }
  .t-head { font-size:.7rem; } .t-foot > div { padding:7px 5px; }
}
</style>
""", unsafe_allow_html=True)

st.caption("Tutarlar milyon TL. Teminata ayrılan hisseler basitleştirilmiş modelde fonun aktifinde tutulur.")
t_balance(
    "Hisse Fonu",
    [("Banka nakdi", s.cash),
     ("Serbest hisseler", s.free_shares * s.price),
     ("Teminattaki hisseler", s.pledged_shares * s.price)],
    [("Repo borcu", s.debt), ("Özkaynak (NAV)", equity)]
)
t_balance(
    "Repo Finansörü (Karşı Taraf)",
    [("Nakit", s.lender_cash), ("Repo alacağı", s.lender_receivable)],
    [("Özkaynak", s.lender_cash + s.lender_receivable)]
)
with st.expander("Teminat takibi (bilanço dışı bilgi)"):
    st.dataframe(pd.DataFrame([
        ("Bloke hisse adedi (milyon)", s.pledged_shares),
        ("Hisselerin piyasa değeri", s.pledged_shares * s.price),
        ("Kabul edilen teminat değeri", collateral_limit()),
        ("Repo borcu", s.debt),
        ("Teminat açığı", gap)
    ], columns=["Kalem", "Değer"]), hide_index=True, use_container_width=True)
    st.caption("Teminat karşı tarafa ikinci kez aktif yazılmaz. Gerçek repo işlemlerinde hukuki mülkiyet ve muhasebe işlem türüne göre değişebilir.")

st.divider()
st.subheader("1 · Hisse işlemleri ve fiyat hareketi")
p1, p2, p3 = st.columns(3)
with p1:
    buy = st.number_input("Nakitle hisse alımı (mn TL)", min_value=1.0, value=10.0, step=5.0)
    if st.button("🛒 Hisse satın al", use_container_width=True):
        if buy > s.cash + 1e-8:
            st.warning("Yetersiz nakit. Borçlanma, hisse alımıyla aynı işlem değildir.")
        else:
            s.cash -= buy
            s.free_shares += buy / s.price
            log("Hisse alımı", f"{buy:.2f} mn TL nakit azaldı, {buy / s.price:.2f} milyon serbest hisse eklendi.")
            st.rerun()
with p2:
    change = st.slider("Piyasa fiyatı değişimi (%)", -80, 200, 20, 5)
    if st.button("📊 Piyasa fiyatını değiştir", use_container_width=True):
        s.price *= 1 + change / 100
        log("Fiyat şoku", f"Hisse fiyatı %{change:+d} değişti; nakit değişmedi, hisseler yeniden değerlendi.")
        st.rerun()
with p3:
    pledge = st.number_input("Teminata ayrılacak hisse (milyon adet)", min_value=1.0, value=10.0, step=5.0)
    if st.button("🔐 Serbest hisseleri teminata ayır", use_container_width=True):
        if pledge > s.free_shares + 1e-8:
            st.warning("Yeterli serbest hisse yok.")
        else:
            s.free_shares -= pledge
            s.pledged_shares += pledge
            log("Teminat tahsisi", f"{pledge:.2f} milyon hisse serbestten blokeliye geçti. Toplam varlıklar değişmedi.")
            st.rerun()

st.subheader("2 · Repo finansmanı ve günlük çevrim")
r1, r2, r3 = st.columns(3)
with r1:
    borrow = st.number_input("Yeni repo anaparası (mn TL)", min_value=1.0, value=10.0, step=5.0)
    if st.button("💰 Ek repo borcu al", use_container_width=True):
        if borrow > capacity + 1e-8:
            st.warning("Teminat kapasitesi yetersiz.")
        elif borrow > s.lender_cash + 1e-8:
            st.warning("Finansman sağlayan karşı tarafın nakdi yetersiz.")
        else:
            s.cash += borrow
            s.debt += borrow
            s.lender_cash -= borrow
            s.lender_receivable += borrow
            log("Repo borçlanması", f"Fon +{borrow:.2f} nakit / +{borrow:.2f} borç; karşı taraf -nakit / +repo alacağı.")
            st.rerun()
with r2:
    repayment = st.number_input("Repo anaparası geri ödeme (mn TL)", min_value=1.0, value=10.0, step=5.0)
    if st.button("↩️ Repo anaparası öde", use_container_width=True):
        if repayment > min(s.cash, s.debt) + 1e-8:
            st.warning("Nakit veya mevcut borç miktarı yetersiz.")
        else:
            s.cash -= repayment
            s.debt -= repayment
            s.lender_cash += repayment
            s.lender_receivable -= repayment
            log("Repo geri ödemesi", f"{repayment:.2f} mn TL anapara geri ödendi.")
            st.rerun()
with r3:
    interest = s.debt * annual_rate / 365
    st.write(f"**Günlük faiz: {interest:.4f} mn TL**")
    if st.button("🔄 1 gün ilerle / repo yenile", use_container_width=True):
        if gap > 1e-8:
            st.error("Teminat açığı nedeniyle otomatik yenileme yapılamadı. Bu, sadeleştirilmiş stres senaryosudur.")
        elif interest > s.cash + 1e-8:
            st.error("Faiz ödemesi için nakit yetersiz. Repo yenileme gerçekleşmedi.")
        else:
            s.cash -= interest
            s.lender_cash += interest
            s.day += 1
            log("Repo yenileme", f"Anapara {s.debt:.2f} mn TL olarak yenilendi, {interest:.4f} mn TL faiz ödendi.")
            st.rerun()
    st.caption("Yenileme karşı tarafın kabul ettiği varsayımıyla gerçekleşir; gerçek piyasada otomatik garanti değildir.")

st.divider()
st.subheader("İşlem günlüğü ve gelişim")
if s.events:
    st.dataframe(pd.DataFrame(s.events).iloc[::-1], hide_index=True, use_container_width=True)
else:
    st.caption("Henüz işlem yapılmadı.")
if s.history:
    chart = pd.DataFrame(s.history).set_index("İşlem no")
    st.line_chart(chart[["Özkaynak (NAV)", "Repo borcu", "Nakit", "Teminat açığı"]])

st.caption("Model kapsamı: Tek hisse fonu + tek repo finansörü. TEFAS/MKK, yatırımcı iadeleri, çoklu fonlar, hisse satışının piyasayı etkilemesi, temerrüt tasfiyesi ve gerçek KAP verileri sonraki sürümlerde eklenecek.")
