# AI Autonomous Sales Assistant 🤖🚀

Bu proje, kurumsal şirketlerin satış süreçlerini otomatize etmek için geliştirilmiş bir **RAG (Retrieval-Augmented Generation)** çözümüdür.

## 🌟 Neleri Çözüyor?
- **Hızlı Analiz:** Sayfalarca süren müşteri taleplerini saniyeler içinde tarar.
- **Doğru Eşleşme:** ChromaDB vektör veritabanı ile müşteri ihtiyacına en uygun ürünü bulur.
- **Profesyonel Çıktı:** Llama 3.1 kullanarak jilet gibi keskin B2B teklif taslakları üretir.

## 🛠 Kullanılan Teknolojiler
- **Backend:** FastAPI, Python
- **AI/LLM:** Llama 3.1 (via Ollama), LangChain
- **Database:** ChromaDB (Vector DB)
- **Frontend:** Modern HTML5, CSS3, JavaScript

## 🚀 Kurulum
1. Gerekli kütüphaneleri yükleyin: `pip install -r requirements.txt`
2. Vektör veritabanını oluşturun: `python veritabani_kur.py`
3. Backend'i çalıştırın: `python arama_motoru.py`
4. `index.html` dosyasını tarayıcıda açın.
