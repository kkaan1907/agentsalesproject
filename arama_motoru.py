from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # 1. Bunu ekle
from pydantic import BaseModel
import chromadb
from chromadb.utils import embedding_functions
import ollama

# 1. FastAPI Uygulamasını Başlatıyoruz
app = FastAPI(
    title="KaanTech B2B Teklif Asistanı API",
    description="Müşteri ihale taleplerini (RFP) okuyup, RAG üzerinden uygun ürünü bularak Llama 3.1 ile teknik satış teklifi üreten akıllı ajan.",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Güvenlik için gerçek projede ["http://localhost:9999"] yazılır
    allow_credentials=True,
    allow_methods=["*"], # POST, GET, OPTIONS hepsine izin ver
    allow_headers=["*"],
)
# 2. Veri Doğrulama Şeması (Pydantic)
# Dış dünyadan (örneğin bir React uygulamasından) gelecek verinin yapısını belirliyoruz.
class IhaleTalebi(BaseModel):
    musteri_adi: str
    talep_metni: str

# 3. Akıllı Ajan Fonksiyonu (Eski kodumuzun fonksiyona sarılmış hali)
def ajan_teklif_uret(musteri_adi: str, talep_metni: str):
    try:
        # Vektör DB'ye Bağlan (Türkçe Model ile)
        chroma_client = chromadb.PersistentClient(path="./kaantech_db")
        turkce_embed_modeli = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="paraphrase-multilingual-MiniLM-L12-v2")
        collection = chroma_client.get_collection(name="urun_katalogu", embedding_function=turkce_embed_modeli)

        # RAG Arama (Retrieval)
        sonuclar = collection.query(query_texts=[talep_metni], n_results=1)

        # Eğer veritabanı boşsa veya eşleşme bulamazsa
        if not sonuclar['documents'][0]:
            raise ValueError("Katalogda uygun ürün bulunamadı.")

        bulunan_urun_metni = sonuclar['documents'][0][0]
        
        # System Prompt ve Üretim (Generation) - KISALTILMIŞ VERSİYON
        prompt = f"""Sen KaanTech'in Kıdemli Çözüm Mimarı ve Satış Mühendisisin. 
Görevin, müşterinin teknik problemini 'Nokta Atışı' çözmek ve teklif mektubu yazmak.

KURALLAR:
1. ÜSLUP: Çok profesyonel, kısa ve net. Gereksiz "anlıyorum, biliyorum" gibi dolaylı cümlelerden kaçın. 
2. YAPI: 
   - Giriş: "Değerli {musteri_adi} Ekibi,"
   - Sorun-Çözüm Eşleşmesi: Müşterinin derdini ve buna karşılık gelen ÜRÜN ADINI doğrudan söyle.
   - 2-3 adet kısa madde (Bullet points) ile teknik avantajı belirt.
   - Kapanış: "Detaylı teknik demo için toplantı planlamayı öneriyoruz."
3. KISITLAMA: Maksimum 60 kelime. Meta-açıklama yapma.

MÜŞTERİ TALEBİ:
"{talep_metni}"

ÜRÜN DETAYI (RAG'DEN GELEN):
"{bulunan_urun_metni}"

Sadece teklif metnini oluştur (açıklama yapma):"""

        response = ollama.generate(model='llama3.1', prompt=prompt)
        return response['response']

    except Exception as e:
        # Kodun içinde bir hata çıkarsa FastAPI bunu yakalar
        raise HTTPException(status_code=500, detail=str(e))

# 4. API Endpoint'ini Tanımlıyoruz (POST Request)
# Dış dünya buraya '/teklif-olustur' adresi üzerinden veri gönderecek.
@app.post("/teklif-olustur")
def teklif_olustur_endpoint(talep: IhaleTalebi):
    # Fonksiyonu çalıştır ve sonucu JSON formatında dış dünyaya geri döndür
    teklif_metni = ajan_teklif_uret(talep.musteri_adi, talep.talep_metni)
    
    return {
        "status": "success",
        "musteri": talep.musteri_adi,
        "ajan_cevabi": teklif_metni
    }

# Terminalden doğrudan çalıştırmak için (Geliştirme Modu)
if __name__ == "__main__":
    import uvicorn
    # Uygulamayı localhost'ta 8000 portundan ayağa kaldırıyoruz.
    print("🚀 KaanTech Sunucusu Başlatılıyor... http://127.0.0.0:8000 adresinden dinleniyor.")
    uvicorn.run(app, host="0.0.0.0", port=8000)