import streamlit as st

st.set_page_config(page_title="Fonzi | Repo ve Hisse Döngüsü", page_icon="📈", layout="wide")
st.markdown("""
<style>
.block-container{padding-top:1.4rem;max-width:1250px}
.statebar{display:flex;gap:12px;align-items:center;margin-bottom:16px;flex-wrap:wrap}
.pill{padding:10px 23px;border-radius:28px;background:#eee;font-weight:700;color:#151515}
.pill.green{background:#d8f9d7;color:#007f50}
.pill.amber{background:#fff0c2;color:#8b6100}
.sheet{border:1.5px solid #d9d9d9;border-radius:20px;padding:20px;min-height:290px;background:white;color:#151515}
.sheet-head{display:flex;justify-content:space-between;gap:8px;font-size:1.16rem;font-weight:750;border-bottom:3px solid #3b82f6;padding-bottom:12px;margin-bottom:15px}
.sheet.pasif .sheet-head{border-color:#64748b}
.entry{display:flex;justify-content:space-between;gap:10px;padding:9px 0;font-size:1.05rem}
.entry span:first-child{color:#707070}
.entry b{font-weight:600;white-space:nowrap;font-variant-numeric:tabular-nums}
.entry.accent{background:#f4f4f4;border-radius:10px;padding:9px 10px}
.entry.blue b{color:#317dff}
.entry.red b{color:#d82727}
.entry.green b{color:#008e59}
.entry.total{border-top:1px dashed #ddd;margin-top:4px}
.info-panel{background:#f3f3f3;border-radius:20px;padding:20px;margin:18px 0;color:#111}
.mini-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:14px}
.mini{border-radius:14px;background:white;text-align:center;padding:12px 4px}
.mini small{display:block;color:#777}.mini strong{font-size:1.16rem}
div.stButton>button{border-radius:28px;min-height:53px;font-size:1.0rem}
@media(max-width:700px){.sheet{min-height:245px;padding:12px}.sheet-head{font-size:.92rem}.entry{font-size:.86rem}.mini-grid{gap:5px}.mini{padding:8px 2px}.mini strong{font-size:.87rem}}
.bubble-wrap{height:340px;display:flex;flex-direction:column;justify-content:end;align-items:center;gap:7px;text-align:center}
.bubble{border-radius:50%;border:2px solid rgba(0,0,0,.08);flex-shrink:0;box-shadow:inset -12px -14px 25px rgba(0,0,0,.09)}
.bubble-label{font-weight:700;font-size:.92rem}
.bubble-value{font-weight:800;font-size:1.16rem}
@media(max-width:640px){.bubble-wrap{height:295px}.bubble-label{font-size:.8rem}.bubble-value{font-size:.94rem}}
</style>
""",unsafe_allow_html=True)

INITIAL={"day":0,"cash":20.0,"free":80.0,"pledged":120.0,"price":1.0,"debt":100.0,"lender_cash":900.0,"lender_claim":100.0,"interest_total":0.0,"message":""}
if "fonzi_day" not in st.session_state:
    for k,v in INITIAL.items(): st.session_state["fonzi_"+k]=v

def v(k): return st.session_state["fonzi_"+k]
def setv(k,val): st.session_state["fonzi_"+k]=val
def fmt(x): return f"{x:,.2f} TL"
def nav(): return v("cash")+(v("free")+v("pledged"))*v("price")-v("debt")
HAIRCUT = 0.10
def available(): return max(0.0,v("pledged")*v("price")*(1-HAIRCUT)-v("debt"))
def sheet(title,side,entries,total):
    items="".join(f'<div class="entry {c}"><span>{label}</span><b>{fmt(value)}</b></div>' for label,value,c in entries)
    st.markdown(f'<div class="sheet {side}"><div class="sheet-head"><span>{title}</span><span>{fmt(total)}</span></div>{items}</div>',unsafe_allow_html=True)

status="Normal Operasyon" if v("cash")>=0 and nav()>=0 else "Nakit Sıkışıklığı"
st.markdown(f'<div class="statebar"><span class="pill">Gün: {v("day")}</span><span class="pill {"green" if status=="Normal Operasyon" else "amber"}">{status}</span></div>',unsafe_allow_html=True)
l,r=st.columns(2,gap="medium")
asset=v("cash")+(v("free")+v("pledged"))*v("price")
with l:
    sheet("VARLIKLAR (AKTİF)","aktif",[
        ("Nakit",v("cash"),""),
        ("Serbest Hisseler",v("free")*v("price"),""),
        ("Teminattaki Hisseler",v("pledged")*v("price"),"accent blue")],asset)
with r:
    sheet("YÜKÜMLÜLÜK & ÖZKAYNAK (PASİF)","pasif",[
        ("Gecelik Repo Borcu",v("debt"),"accent red"),
        ("Ödenen Birikmiş Faiz",v("interest_total"),"red"),
        ("Özkaynak (Net Varlık)",nav(),"total green")],asset)
# Faiz ödemeleri fonun nakdinden çıktığı için ayrı bir pasif değildir.
# Yukarıda ödenen faiz yalnızca bilgi amaçlıdır; toplam pasife dahil edilmez.
ratio=v("pledged")*v("price")*(1-HAIRCUT)/v("debt")*100 if v("debt") else 0
lev=asset/nav() if nav()>0 else 0
st.markdown(f"""
<div class="info-panel">
  <div style="display:flex;justify-content:space-between;gap:12px"><span>İskontolu Teminatın Borcu Karşılama Oranı (%10 haircut)</span><b>{ratio:.1f}%</b></div>
  <div style="height:12px;border-radius:9px;background:#e0e0e0;margin-top:9px;overflow:hidden">
    <div style="width:{min(100,ratio):.1f}%;height:100%;background:#00905a"></div>
  </div>
  <div class="mini-grid">
    <div class="mini"><small>Hisse Birim Fiyatı</small><strong>{fmt(v("price"))}</strong></div>
    <div class="mini"><small>Ekstra Borç Limiti</small><strong>{fmt(available())}</strong></div>
    <div class="mini"><small>Kaldıraç Oranı</small><strong>{lev:.2f}x</strong></div>
  </div>
</div>
""",unsafe_allow_html=True)

a,b,c=st.columns(3)
with a:
    if st.button("1 Gün İlerlet (Roll-Over)",use_container_width=True):
        interest=v("debt")*.43/365
        if v("cash")>=interest:
            setv("cash",v("cash")-interest)
            setv("lender_cash",v("lender_cash")+interest)
            setv("interest_total",v("interest_total")+interest)
            setv("day",v("day")+1)
            setv("message",f"Repo yenilendi; {fmt(interest)} günlük faiz nakitten ödendi.")
        else: setv("message","Repo faizinin ödenmesi için yeterli nakit yok.")
        st.rerun()
with b:
    if st.button("Hisse Fiyatı +%20",use_container_width=True):
        setv("price",v("price")*1.20)
        setv("message",f"Hisse fiyatı %20 yükseldi. %10 iskontodan sonra ek repo kapasitesi {fmt(available())} oldu. Fonun banka nakdi değişmedi.")
        st.rerun()
with c:
    if st.button("Ekstra Borçlan & Hisse Al",use_container_width=True,disabled=available()<0.01 or v("lender_cash")<0.01):
        loan=min(available(),v("lender_cash"))
        setv("debt",v("debt")+loan)
        setv("lender_cash",v("lender_cash")-loan)
        setv("lender_claim",v("lender_claim")+loan)
        setv("free",v("free")+loan/v("price"))
        setv("message",f"İlişkili para fonundan {fmt(loan)} repo borcu alınıp tamamıyla hisse alındı. Nakitte kalıcı artış yok.")
        st.rerun()

if v("message"): st.info(v("message"))

st.markdown("### 🎈 Şişen hisse değeri, değişmeyen nakit")
stock_value=(v("free")+v("pledged"))*v("price")
cash_value=v("cash")
base=max(stock_value,cash_value,1.0)
def balloon(label,value,fill):
    diameter=max(66,min(250,250*(max(value,0)/base)**0.5))
    st.markdown(f"""<div class="bubble-wrap">
        <div class="bubble" style="width:{diameter:.0f}px;height:{diameter:.0f}px;background:{fill}"></div>
        <div class="bubble-label">{label}</div>
        <div class="bubble-value">{fmt(value)}</div>
    </div>""",unsafe_allow_html=True)

bubbleleft,bubbleright=st.columns(2)
with bubbleleft: balloon("Hisse portföyünün piyasa değeri",stock_value,"#87b7fb")
with bubbleright: balloon("Fonun bankadaki nakdi",cash_value,"#80dcb3")
st.caption("Balonların büyüklüğü tutarı temsil eder. Hisse fiyatındaki artış bankadaki nakdi kendiliğinden artırmaz.")
with st.expander("Parayı veren ilişkili para fonu"):
    st.write(f"**Nakit:** {fmt(v('lender_cash'))}  ·  **Repo alacağı:** {fmt(v('lender_claim'))}  ·  **Toplam varlık:** {fmt(v('lender_cash')+v('lender_claim'))}")
    st.caption("Para fonunun nakdi, alacağa dönüşür. Repo alacağının tahsilatı garanti değildir.")
with st.expander("Varsayımlar ve sıfırlama"):
    st.caption("Tüm tutarlar varsayımsal birimlerdir; gerçek Tera işlemleri değildir. Başlangıçta 20 nakit, 80 serbest hisse ve 120 teminatlı hisse karşılığında 100 repo borcu vardır. Teminata sabit %10 haircut uygulanır: 120 TL hisse değeri 108 TL kabul edilen teminattır. Yıllık repo faizi %43'tür; her tur bir günlük faiz nakitten ödenir. Fiyat yükselişi dışsal senaryodur.")
    if st.button("Oyunu Sıfırla"):
        for k,value in INITIAL.items():setv(k,value)
        st.rerun()
st.caption("Repo teminatına sabit %10 haircut uygulanır. Ek repo, başlangıçta nakdi artırsa da aynı işlemde hisseye yatırılır. Hisse piyasa değerindeki artış nakit değildir. Gerçek kurumların danışıklı işlem yaptığı bu modelden çıkarılamaz.")
