import chromadb
from chromadb.utils import embedding_functions

print("🔌 Veritabanına bağlanılıyor...")
# Ajanın aradığı klasörün aynısını hedefliyoruz
chroma_client = chromadb.PersistentClient(path="./kaantech_db")

# Ajanla AYNI Türkçe dil modelini kullanmak ZORUNDAYIZ
turkce_embed_modeli = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

# Koleksiyonu oluştur (varsa bağlanır)
collection = chroma_client.get_or_create_collection(
    name="urun_katalogu", 
    embedding_function=turkce_embed_modeli
)

print("📝 Şirket verileri hazırlanıyor...")
# İşte burası senin (olmayan) PDF'lerinin içindeki metinler!
dokumanlar = [
    "KaanTech X1 Edge Kamera: 4K çözünürlük, yapay zeka destekli hareket algılama, gece görüşü var. Birim Fiyatı: 200 Dolar.",
    "KaanTech Pro Server: 64GB RAM, 2TB NVMe SSD, Llama modellerini lokalde çalıştırmak için optimize edilmiştir. Birim Fiyatı: 1500 Dolar.",
    "KaanTech Akıllı Sensör Seti: Fabrika içi sıcaklık ve nem ölçümü yapar, WiFi uyumludur. Birim Fiyatı: 50 Dolar.",
    "Şirket Politikası: KaanTech olarak 10 adet ve üzeri toplu alımlarda standart %5 iskonto (indirim) uygulanır."
]

# Her dökümana benzersiz bir ID veriyoruz
idler = ["urun_1", "urun_2", "urun_3", "kural_1"]

print("🧠 Veriler Vektörlere (Matematiğe) dönüştürülüp veritabanına yazılıyor...")
# Eğer veriler daha önce eklendiyse hata vermemesi için upsert (update/insert) kullanıyoruz
collection.upsert(
    documents=dokumanlar,
    ids=idler
)

print("✅ Başarılı! KaanTech Hafızası yüklendi. Artık ajanınız bu ürünleri biliyor.")