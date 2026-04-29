import chromadb
from chromadb.utils import embedding_functions
from PyPDF2 import PdfReader

def pdf_metin_ayikla(dosya_yolu):
    reader = PdfReader(dosya_yolu)
    tam_metin = ""
    for page in reader.pages:
        if page.extract_text():
            tam_metin += page.extract_text() + "\n"
    return tam_metin

def veritabani_insasi_pdf_ile():
    print("1. KaanTech Vektör Veritabanı (PDF Tabanlı) başlatılıyor...")
    chroma_client = chromadb.PersistentClient(path="./kaantech_db")

    
    turkce_embed_modeli = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )

    collection = chroma_client.get_or_create_collection(
        name="urun_katalogu",
        embedding_function=turkce_embed_modeli
    )

    print("2. PDF Kataloğu okunuyor ve işleniyor...")
    
    pdf_yolu = "kaantech-kurumsal-katalog-v1.pdf" 
    katalog_metni = pdf_metin_ayikla(pdf_yolu)

   
    paragraflar = [p.strip() for p in katalog_metni.split("\n\n") if len(p.strip()) > 20]
    
    
    id_ler = [f"doc_pdf_{i}" for i in range(len(paragraflar))]

    print(f"3. Toplam {len(paragraflar)} farklı bilgi parçası (chunk) vektörleştiriliyor...")
    
   
    if collection.count() > 0:
        eski_idler = collection.get()['ids']
        if eski_idler:
            collection.delete(ids=eski_idler)
            
    collection.add(
        documents=paragraflar,
        ids=id_ler
    )

    print("✅ Mimar, PDF tabanlı kurumsal hafıza başarıyla kuruldu!")

if __name__ == "__main__":
    veritabani_insasi_pdf_ile()
