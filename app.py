import streamlit as st
import pandas as pd

st.set_page_config(page_title="Fonzi | Fon Krizinin Mekanizması", page_icon="🎮", layout="wide")

# Eğitim amaçlı varsayımsal senaryo: Gerçek kurumların manipülasyon yaptığına
# veya belirtilen nakit akışlarının fiilen gerçekleştiğine ilişkin kanıt değildir.
# Tutarlar milyon TL. Bir adet temsilî hisse ve basitleştirilmiş repo muhasebesi.
SCENES = [
    ("Başlangıç", "Hisse fonunun nakdi var; repo borcu yok.", "Fon nakdiyle hisse alabilecek durumda. Para fonunun bankada nakdi var."),
    ("Hisse alımı", "Hisse fonu piyasadan 60 milyon TL'lik hisse alır.", "Fonun nakdi 100'den 40'a iner; hisselerinin değeri 60 olur. İkincil piyasa satışında para hisseyi satanlara gider."),
    ("Fiyat yükselişi", "Yoğun ve varsayımsal danışıklı işlemler senaryosunda hisse fiyatı iki katına çıkar.", "Fondaki 60 milyon TL'lik hisse pozisyonu 120 milyon TL görünür. Artış nakit girişi değildir."),
    ("Repo teminatı ve borçlanma", "Fon, uygun hisseleri teminat göstererek para fonundan 60 milyon TL borç alır.", "Para fonunun nakdi azalır, repo alacağı artar. Hisse fonunda nakit ve repo borcu birlikte artar."),
    ("Yeni alım ve büyüme", "Hisse fonu aldığı 60 milyon TL ile yeniden hisse satın alır.", "Fonun nakdi azalır; hisse pozisyonu büyür. Borç yerinde durur. Fiyatların tekrar yükselmesi otomatik değildir."),
    ("Kırılma", "Hisse fiyatı %50 düşer; repo vadesi gelir ve para fonu yenilemek istemez.", "Teminat değeri düşer. Fonun repo borcu devam eder; nakdi bulunmadığı için ödeme sıkışıklığı oluşur.")
]

# Sayısal durum: hisse adedi milyon, fiyat TL.
def snapshot(stage):
    fund_cash, fund_shares, price, fund_debt = 100.0, 0.0, 1.0, 0.0
    money_cash, money_claim = 200.0, 0.0
    if stage >= 1:
        fund_cash -= 60
        fund_shares += 60
    if stage >= 2:
        price = 2.0
    if stage >= 3:
        fund_cash += 60
        fund_debt += 60
        money_cash -= 60
        money_claim += 60
    if stage >= 4:
        fund_cash -= 60
        fund_shares += 30  # O anki fiyat 2 TL
    if stage >= 5:
        price = 1.0
    return dict(cash=fund_cash, shares=fund_shares, price=price, debt=fund_debt,
                money_cash=money_cash, money_claim=money_claim)

def money(x):
    return f"{x:,.1f} mn TL"

def balance(title, asset_rows, liability_rows):
    a = pd.DataFrame(asset_rows, columns=["AKTİF", "Milyon TL"])
    p = pd.DataFrame(liability_rows, columns=["PASİF", "Milyon TL"])
    total_a = sum(v for _, v in asset_rows)
    total_p = sum(v for _, v in liability_rows)
    left, right = st.columns(2)
    st.markdown(f"**{title}**")
    with left:
        st.dataframe(pd.concat([a, pd.DataFrame([["TOPLAM AKTİF", total_a]], columns=a.columns)]),
                     hide_index=True, use_container_width=True)
    with right:
        st.dataframe(pd.concat([p, pd.DataFrame([["TOPLAM PASİF", total_p]], columns=p.columns)]),
                     hide_index=True, use_container_width=True)

if "stage" not in st.session_state:
    st.session_state.stage = 0

st.title("🎮 Fonzi: Bir Fon Krizi Nasıl Büyür?")
st.write("**Hisse fiyatı → teminat değeri → repo finansmanı → yeni hisse alımı → kırılganlık**")
st.caption("Tera krizi araştırmasından esinlenen, varsayımsal ve sadeleştirilmiş bilanço oyunu. Bu adımların tamamının Tera'da gerçekleştiği ileri sürülmüyor.")

stage = st.session_state.stage
d = snapshot(stage)
title, action, meaning = SCENES[stage]
st.progress(stage / (len(SCENES)-1))
st.subheader(f"{stage + 1}. Aşama — {title}")
st.markdown(f"**{action}**")
st.info(meaning)

nav = d["cash"] + d["shares"] * d["price"] - d["debt"]
asset = d["cash"] + d["shares"] * d["price"]
# Teminat örneğinde hisselerin tamamı reponun dayanağı olarak kabul edilmiştir.
# Teminata kabul oranı %70, repo alacağı 60 mn TL; bu gösterge nakit değildir.
collateral = d["shares"] * d["price"] * 0.70
gap = max(0, d["debt"] - collateral)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Hisse fiyatı", f"{d['price']:.2f} TL")
k2.metric("Hisse fonunun NAV'ı", money(nav))
k3.metric("Repo borcu", money(d["debt"]))
k4.metric("Nakit", money(d["cash"]))

st.markdown("### Para ve borç nerede? — T-Balance")
balance("Hisse Fonu",
        [("Banka nakdi", d["cash"]), ("Hisse senetleri", d["shares"] * d["price"])],
        [("Repo borcu", d["debt"]), ("Katılımcı özkaynağı / NAV", nav)])
balance("Repo finansörü — Para Piyasası Fonu",
        [("Banka nakdi", d["money_cash"]), ("Repo alacağı", d["money_claim"])],
        [("Fon katılımcı özkaynağı", d["money_cash"] + d["money_claim"])])

if d["debt"] > 0:
    st.caption(f"Örnek kabul edilen teminat değeri (%70): {money(collateral)} | "
               f"Teminat açığı: {money(gap)}")
if stage == 5:
    st.error("Repo borcu 60 milyon TL, fondaki nakit ise 0 TL. Repo yenilenmezse fonun varlık satması veya başka kaynak bulması gerekir. Bu, ödeme sıkışıklığıdır; otomatik olarak hukuki temerrüt veya iflas anlamına gelmez.")

b1, b2, b3 = st.columns([1, 2, 1])
if b1.button("⬅️ Önceki", disabled=stage == 0, use_container_width=True):
    st.session_state.stage -= 1
    st.rerun()
if b2.button("▶️ Sonraki aşama", disabled=stage == len(SCENES)-1, use_container_width=True, type="primary"):
    st.session_state.stage += 1
    st.rerun()
if b3.button("🔄 Baştan", use_container_width=True):
    st.session_state.stage = 0
    st.rerun()

with st.expander("Gerçek kurumların konumu — araştırma haritası"):
    st.markdown("""
    - **TLY ve Tera bağlantılı hisse fonları:** Her fonun pay portföyü, bankadaki nakdi ve repo işlemleri ayrı ayrı doğrulanmalı.
    - **Tera Yatırım:** KAP'ta bildirilen bazı repo işlemlerinde nakit borçlanan karşı taraftır; doğrudan fon bilançosuyla birleştirilmemeli.
    - **Tera para piyasası fonları ve Pusula fonları:** Repo ile nakit sağlayan tarafta oldukları işlemler ayrı ayrı gösterilmeli.
    - **Holdingler:** Holding hissesinin fiyatının artması, holdingin banka hesabına nakit girdiği anlamına gelmez.
    - **Takasbank, TEFAS ve MKK:** Repo/takas yükümlülükleri, fon satış emirleri ve pay blokajları birbirinden ayrılmalı.

    Oyunun bu sürümü yalnızca temel finansal mekanizmayı örneklendirir.
    Belgelenmiş işlem ve tutarları sonraki sürümlere kaynak bazında ekleyeceğiz.
    """)

st.caption("Model notu: Örnek teminat ve repo işlemi tek fon–tek finansör üzerinden basitleştirilmiştir. "
           "Gerçek işlem sözleşmeleri, değerleme ve nakit takası daha karmaşıktır.")
