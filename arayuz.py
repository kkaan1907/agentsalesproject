import streamlit as st
import requests
import json

# FastAPI Sunucusunun Adresi
API_URL = "http://127.0.0.1:8000"

# Sayfa Ayarları
st.set_page_config(page_title="KaanTech B2B Yönetim Paneli", page_icon="🤖", layout="wide")

st.title("🏭 KaanTech Otonom Satış Asistanı (v3)")
st.markdown("---")

# Session State: Ekranda verilerin kaybolmaması için Streamlit'in hafızası
if "ajan_taslagi" not in st.session_state:
    st.session_state.ajan_taslagi = ""
if "musteri_adi" not in st.session_state:
    st.session_state.musteri_adi = ""
if "islem_durumu" not in st.session_state:
    st.session_state.islem_durumu = "beklemede" # beklemede -> onay_bekliyor -> tamamlandi

# ==========================================
# 1. BÖLÜM: YENİ TALEP GİRİŞİ
# ==========================================
with st.container():
    st.subheader("📝 1. Yeni Müşteri Talebi")
    col1, col2 = st.columns([1, 3])
    
    with col1:
        musteri_input = st.text_input("Müşteri/Firma Adı:", placeholder="Örn: Kıvanç Tekstil")
    with col2:
        talep_input = st.text_area("Müşteri Talebi:", placeholder="Örn: Bize 50 tane akıllı sensör lazım, fiyat nedir?", height=100)
    
    if st.button("🤖 Ajanı Tetikle (Taslak Hazırla)", type="primary"):
        if musteri_input and talep_input:
            with st.spinner("Ajan RAG veritabanını tarıyor ve taslak hazırlıyor..."):
                try:
                    # Backend 1. Adımı (Taslak Hazırla) çağırıyoruz
                    payload = {"musteri_adi": musteri_input, "talep_metni": talep_input}
                    cevap = requests.post(f"{API_URL}/1-taslak-hazirla", json=payload).json()
                    
                    # Gelen cevabı Streamlit hafızasına kaydediyoruz
                    st.session_state.ajan_taslagi = cevap.get("ajan_taslagi", "Taslak oluşturulamadı.")
                    st.session_state.musteri_adi = musteri_input
                    st.session_state.islem_durumu = "onay_bekliyor"
                    st.rerun() # Sayfayı yenile
                except Exception as e:
                    st.error(f"Sunucuya bağlanılamadı. FastAPI'nin çalıştığından emin olun. Hata: {e}")
        else:
            st.warning("Lütfen Müşteri Adı ve Talebi boş bırakmayın.")

st.markdown("---")

# ==========================================
# 2. BÖLÜM: YÖNETİCİ ONAYI (İNSAN MÜDAHALESİ)
# ==========================================
if st.session_state.islem_durumu == "onay_bekliyor":
    st.subheader("🕵️‍♂️ 2. Yönetici Onayı Paneli")
    st.info(f"Ajan **{st.session_state.musteri_adi}** için verileri hazırladı ve uyku modunda.")
    
    raw_taslak = st.session_state.ajan_taslagi
    onaylanacak_metin = ""

    try:
        # LLM'den gelen metni JSON objesine çevirmeyi deniyoruz
        taslak_json = json.loads(raw_taslak)
        
        # JSON başarılıysa ekrana ŞIK METRİK KARTLARI çiziyoruz
        st.success("✅ Yapılandırılmış Veri (JSON) Başarıyla Çözümlendi!")
        
        # 3 sütunlu gösterge paneli
        col1, col2, col3 = st.columns(3)
        col1.metric("📦 Ürün", taslak_json.get("urun_adi", "Bilinmiyor"))
        col2.metric("💰 Fiyat", f"{taslak_json.get('birim_fiyat', 0)} {taslak_json.get('para_birimi', '')}")
        col3.metric("🏷️ İndirim", f"%{taslak_json.get('indirim_orani', 0)}")
        
        st.markdown("### 💌 Müşteriye Gidecek İkna Metni")
        # Yöneticinin sadece ikna metnini düzenlemesine izin veriyoruz
        duzenlenmis_metin = st.text_area("Mesajı Düzenle:", value=taslak_json.get("ikna_metni", ""), height=150)
        
        # Gönder tuşuna basıldığında JSON'ı tekrar paketliyoruz
        taslak_json["ikna_metni"] = duzenlenmis_metin
        onaylanacak_metin = json.dumps(taslak_json, ensure_ascii=False)

    except json.JSONDecodeError:
        # Eğer Router soruyu "Sohbet" sanıp düz metin döndüyse sistemin çökmesini engelliyoruz
        st.warning("Ajan standart metin döndürdü (Sohbet veya Hata Modu).")
        onaylanacak_metin = st.text_area("Ajanın Mesajı:", value=raw_taslak, height=150)

    # ONAY BUTONU
    if st.button("✅ Onayla ve Müşteriye Gönder", type="secondary"):
        with st.spinner("Sistem uyanıyor ve işlem tamamlanıyor..."):
            try:
                payload = {"musteri_adi": st.session_state.musteri_adi, "onaylanan_metin": onaylanacak_metin}
                final_cevap = requests.post(f"{API_URL}/2-onayla-ve-gonder", json=payload).json()
                
                st.success("İşlem Başarılı! Ajan uyandı ve süreci tamamladı.")
                st.write("**Müşteriye Giden Final Veri:**")
                st.code(final_cevap.get("musteriye_giden_final_metin", ""), language="json")
                
                if st.button("Yeni Talep Gir"):
                     st.session_state.islem_durumu = "beklemede"
                     st.session_state.ajan_taslagi = ""
                     st.rerun()

            except Exception as e:
                st.error(f"Onaylama sırasında bir hata oluştu: {e}")