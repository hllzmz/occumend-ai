# OccumendAI: Sıfırdan AI Destekli Kariyer Öneri Motoru Geliştirmek

*Psikoloji, makine öğrenmesi ve yapay zeka teknolojilerini birleştirerek insanların ideal kariyerlerini keşfetmelerine yardımcı olan modern bir web uygulaması geliştirme sürecinin tam hikayesi*

![Uygulama Ekran Görüntüsü](https://github.com/user-attachments/assets/ab1dae53-4b1c-4b53-880e-889abb6c4a0e)

## Giriş: Problem ve Vizyon

Günümüzün sürekli gelişen iş pazarında, doğru kariyer yolunu seçmek her zamankinden daha karmaşık hale geldi. Binlerce meslek seçeneği mevcut ve sürekli yeni roller ortaya çıkıyor, bu durumda bireyler kendi ilgileri, yetenekleri ve kişilik özelliklerine uygun kariyerleri belirlemekte zorlanıyor.

**OccumendAI** bu zorluktan doğdu — bilimsel olarak kanıtlanmış metodolojilere dayanan ve modern AI yetenekleriyle desteklenen kişiselleştirilmiş kariyer önerileri sunan akıllı bir sistem yaratmak amacıyla.

## Proje Genel Bakış

OccumendAI, aşağıdaki teknolojileri birleştiren Flask tabanlı bir web uygulamasıdır:
- **Psikoloji**: RIASEC (Holland Kodu) kariyer ilgi değerlendirmesi
- **Veri Bilimi**: ABD Çalışma Bakanlığı'nın O*NET veritabanı işlenmesi
- **Makine Öğrenmesi**: K-means kümeleme ve kosinüs benzerlik eşleştirmesi
- **AI**: RAG (Retrieval-Augmented Generation) sohbet arayüzü
- **Görselleştirme**: İnteraktif grafikler ve kullanıcı dostu arayüz

**Canlı Demo**: [OccumendAI](https://occumendai-d0f6abgrcwagagbp.germanywestcentral-01.azurewebsites.net)
**Kaynak Kod**: [GitHub Deposu](https://github.com/hllzmz/occumend-ai)

## Mimari Genel Bakış

Uygulama, sorumlulukların net bir şekilde ayrıldığı modüler bir mimari izler:

```
OccumendAI/
├── app/                    # Ana Flask uygulaması
│   ├── __init__.py        # Uygulama fabrikası
│   ├── config.py          # Konfigürasyon yönetimi
│   ├── routes.py          # API endpoint'leri
│   ├── data_processing.py # Veri yükleme ve ML pipeline
│   ├── services.py        # AI sohbet servisi
│   ├── visualizations.py # Grafik oluşturma
│   ├── static/            # Frontend assets
│   └── templates/         # HTML şablonları
├── data/                  # O*NET veritabanı (işlenmiş)
├── scripts/               # Veri işleme scriptleri
├── models/                # Sentence transformer modelleri
└── tests/                 # Unit testler
```

## Faz 1: Veri Temeli - O*NET Veritabanı Entegrasyonu

### O*NET Veritabanını Anlama

O*NET (Occupational Information Network) veritabanı, iş arayanlar, işgücü geliştirme ve İK profesyonelleri, öğrenciler, geliştiriciler, araştırmacılar ve daha fazlası tarafından kullanılmak üzere çalışma dünyasının ayrıntılı açıklamalarını içeren ülkenin birincil mesleki bilgi kaynağıdır.

OccumendAI için özellikle şunları kullandık:
- **Meslekler**: İş unvanları ve açıklamaları
- **İlgiler**: Her meslek için RIASEC skorları
- **Beceriler**: Her iş için gerekli beceriler
- **Yetenekler**: İhtiyaç duyulan bilişsel ve fiziksel yetenekler
- **Bilgi**: Gerekli bilgi alanları

### Veri İşleme Süreci

#### Adım 1: Veri Dönüşümü ve Optimizasyonu

```python
# scripts/convert_data.py
def convert_excel_to_parquet():
    """O*NET Excel dosyalarını verimli Parquet formatına dönüştür"""
    files_to_convert = [
        "abilities.xlsx", "interests.xlsx", "knowledge.xlsx", 
        "occupations.xlsx", "skills.xlsx"
    ]
    
    for file in files_to_convert:
        df = pd.read_excel(DATA_DIR / file)
        df.to_parquet(DATA_DIR / file.replace('.xlsx', '.parquet'))
```

**Neden Parquet?** 
- Excel'e kıyasla %60-80 daha küçük dosya boyutları
- Çok daha hızlı okuma/yazma işlemleri
- Daha iyi sıkıştırma ve sütun odaklı depolama
- Pandas ve veri bilimi araçlarında native destek

#### Adım 2: Bilgi Bankası Oluşturma

```python
# scripts/onet_knowledge_base.py
def build_knowledge_base():
    """O*NET verilerinden aranabilir bilgi bankası oluştur"""
    knowledge_base = []
    
    for _, occupation in occupations.iterrows():
        # Birden fazla veri kaynağını birleştir
        combined_text = f"""
        Başlık: {occupation['Title']}
        Görevler: {get_tasks(occupation['O*NET-SOC Code'])}
        Beceriler: {get_skills(occupation['O*NET-SOC Code'])}
        Yetenekler: {get_abilities(occupation['O*NET-SOC Code'])}
        Bilgi: {get_knowledge(occupation['O*NET-SOC Code'])}
        İş Bağlamı: {get_work_context(occupation['O*NET-SOC Code'])}
        """
        
        # Daha iyi geri alma için örtüşen parçalar oluştur
        chunks = chunk_text(combined_text, max_words=200, overlap=50)
        
        for idx, chunk in enumerate(chunks, 1):
            knowledge_base.append({
                "doc_id": f"{occupation['O*NET-SOC Code']}#{idx}",
                "title": f"{occupation['Title']} (Parça {idx})",
                "content": chunk
            })
```

#### Adım 3: Vektör Veritabanı Kurulumu

```python
# scripts/vectorize_knowledge_base.py
def create_vector_database():
    """RAG sistemi için LanceDB vektör veritabanı oluştur"""
    
    # Sentence transformer modelini yükle
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Bilgi bankası için embeddingler oluştur
    with open('data/onet_knowledge_base.json') as f:
        knowledge_base = json.load(f)
    
    documents = []
    for doc in knowledge_base:
        # Embedding vektörü oluştur
        vector = model.encode(doc['content'])
        documents.append({
            'doc_id': doc['doc_id'],
            'title': doc['title'],
            'content': doc['content'],
            'vector': vector
        })
    
    # LanceDB'de sakla
    db = lancedb.connect('data/lancedb_store')
    table = db.create_table('onet_data', documents)
```

## Faz 2: Makine Öğrenmesi Pipeline'ı

### RIASEC Değerlendirme Uygulaması

OccumendAI'nin kalbi, kariyer ilgilerini altı türde kategorize eden RIASEC (Holland Kodu) değerlendirmesidir:

- **R**ealistic (Gerçekçi): Pratik, uygulamalı çalışma
- **I**nvestigative (Araştırmacı): Araştırma, analiz, sorgulama
- **A**rtistic (Sanatsal): Yaratıcı, ifadeci faaliyetler
- **S**ocial (Sosyal): Yardım etme, öğretme, başkalarına hizmet
- **E**nterprising (Girişimci): Liderlik, ikna, yönetim
- **C**onventional (Geleneksel): Organize etme, büro işleri, detay çalışması

```python
# Frontend JavaScript - Dinamik anket oluşturma
const questions = [
    { cat: 'R', text: 'Sevkiyat öncesi parça kalitesini test etmek' },
    { cat: 'I', text: 'İnsan vücudunun yapısını incelemek' },
    { cat: 'A', text: 'Müzik korosu yönetmek' },
    { cat: 'S', text: 'İnsanlara kariyer rehberliği vermek' },
    { cat: 'E', text: 'Restoran franchise'larını satmak' },
    { cat: 'C', text: 'Aylık bordro çeklerini oluşturmak' }
    // ... toplam 48 soru, kategori başına 8
];

function renderStep(stepIndex) {
    const category = steps[stepIndex];
    const stepQuestions = questions.filter(q => q.cat === category);
    
    stepQuestions.forEach(q => {
        // Her soru için 5 puanlı Likert ölçeği oluştur
        // "Sevmiyorum"dan "Seviyorum"a kadar
    });
}
```

### Kümeleme ve Benzerlik Eşleştirmesi

#### Adım 1: Veri İşleme ve Kümeleme

```python
# app/data_processing.py
def load_and_prepare_data(config):
    """O*NET verilerini yükle ve kümeleme gerçekleştir"""
    
    # Meslekleri ve RIASEC profillerini yükle
    df_jobs = pd.read_parquet(config["OCCUPATIONS_FILE_PATH"])
    df_interests = pd.read_parquet(config["INTERESTS_FILE_PATH"])
    
    # Mesleki İlgiler (OI) ölçeği için filtrele
    df_interests = df_interests[df_interests["Scale ID"] == "OI"]
    
    # Her meslek için RIASEC skorlarını almak için pivot yap
    df_riasec_profiles = df_interests.pivot_table(
        index="O*NET-SOC Code", 
        columns="Element ID", 
        values="Data Value"
    )
    
    # Element ID'leri okunabilir isimlere dönüştür
    riasec_mapping = {
        "1.B.1.a": "R_score", "1.B.1.b": "I_score",
        "1.B.1.c": "A_score", "1.B.1.d": "S_score", 
        "1.B.1.e": "E_score", "1.B.1.f": "C_score"
    }
    df_riasec_profiles.rename(columns=riasec_mapping, inplace=True)
    
    # Meslekleri RIASEC profilleriyle birleştir
    df_job_profiles = df_jobs.join(df_riasec_profiles, how="inner")
    
    # İş ilgi gruplarını bulmak için K-means kümeleme
    features = ["R_score", "I_score", "A_score", "S_score", "E_score", "C_score"]
    job_scores = df_job_profiles[features].fillna(0)
    
    kmeans = KMeans(n_clusters=8, random_state=42, n_init="auto")
    df_job_profiles["cluster"] = kmeans.fit_predict(job_scores)
    
    # Anlamlı küme isimleri oluştur
    cluster_centers = pd.DataFrame(kmeans.cluster_centers_, columns=features)
    
    def get_cluster_name(center):
        # Her küme için en yüksek 3 ilgiyi al
        top_three = center.nlargest(3).index
        return f"{top_three[0][0]}-{top_three[1][0]}-{top_three[2][0]}"
    
    cluster_centers["cluster_name"] = cluster_centers.apply(get_cluster_name, axis=1)
    df_job_profiles["cluster_name"] = df_job_profiles["cluster"].map(
        cluster_centers["cluster_name"].to_dict()
    )
    
    return df_job_profiles
```

#### Adım 2: Kullanıcı Eşleştirme Algoritması

```python
# app/routes.py
@bp.route("/recommend", methods=["POST"])
def recommend():
    """Kullanıcı yanıtlarına göre kariyer önerileri oluştur"""
    
    user_answers = request.json
    
    # Kullanıcının RIASEC profilini hesapla
    user_profile = {
        "R_score": np.mean(user_answers.get("R", [0])),
        "I_score": np.mean(user_answers.get("I", [0])),
        "A_score": np.mean(user_answers.get("A", [0])),
        "S_score": np.mean(user_answers.get("S", [0])),
        "E_score": np.mean(user_answers.get("E", [0])),
        "C_score": np.mean(user_answers.get("C", [0]))
    }
    
    # Tüm mesleklerle kosinüs benzerliğini hesapla
    features = ["R_score", "I_score", "A_score", "S_score", "E_score", "C_score"]
    job_scores = df_clustered_jobs[features].fillna(0)
    user_vector = pd.DataFrame([user_profile])[features].values
    
    similarity_scores = cosine_similarity(user_vector, job_scores.values)
    df_clustered_jobs["similarity"] = similarity_scores[0]
    
    # En iyi 20 eşleşmeyi al
    top_jobs = df_clustered_jobs.sort_values(by="similarity", ascending=False).head(20)
    
    # Ek meta verilerle önerileri hazırla
    recommendations = []
    for index, row in top_jobs.iterrows():
        recommendations.append({
            "Title": row["Title"],
            "cluster_name": row["cluster_name"],
            "similarity": row["similarity"],
            "knowledge": current_app.knowledge_map.get(index, []),
            "skills": current_app.skills_map.get(index, []),
            "abilities": current_app.abilities_map.get(index, [])
        })
    
    return jsonify({"recommendations": recommendations})
```

### Neden Kosinüs Benzerliği?

Kosinüs benzerliği iki vektör arasındaki açının kosinüsünü ölçer ve RIASEC profilleri için mükemmeldir çünkü:

1. **Ölçek Bağımsız**: Mutlak skorlardan ziyade ilgi desenine odaklanır
2. **Normalleştirilmiş**: -1 ve 1 arası değerler, yorumlaması kolay
3. **Yönlü**: Farklı ilgilerin göreceli gücünü yakalar
4. **Verimli**: Gerçek zamanlı öneriler için hızlı hesaplama

## Faz 3: Görselleştirme ve Kullanıcı Deneyimi

### Matplotlib ile İnteraktif Grafikler

```python
# app/visualizations.py
def create_radar_chart_image(user_profile_values):
    """RIASEC radar grafiği görselleştirmesi oluştur"""
    labels = ["Gerçekçi", "Araştırmacı", "Sanatsal", 
              "Sosyal", "Girişimci", "Geleneksel"]
    
    # Dairesel grafik oluştur
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
    stats = np.concatenate((user_profile_values, [user_profile_values[0]]))
    angles = np.concatenate((angles, [angles[0]]))
    
    # Matplotlib stillendirme
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.plot(angles, stats, color="#007bff", linewidth=3)
    ax.fill(angles, stats, color="#007bff", alpha=0.25)
    
    # Görünümü özelleştir
    ax.set_thetagrids(angles[:-1] * 180 / np.pi, labels, 
                      fontsize=13, weight="bold", color="#333")
    ax.set_ylim(0, 5)
    
    # Web görüntüsü için base64 string olarak döndür
    return _fig_to_base64(fig)

def create_bar_chart_image(recommendations):
    """En iyi önerilerin yatay çubuk grafiğini oluştur"""
    top_recommendations = recommendations[:10]
    
    data = {
        "Meslek": [rec["Title"] for rec in top_recommendations],
        "Benzerlik": [(rec["similarity"] * 100) for rec in top_recommendations]
    }
    df = pd.DataFrame(data).sort_values("Benzerlik", ascending=False)
    
    # Yatay çubuk grafiği oluştur
    fig, ax = plt.subplots(figsize=(8, 8))
    bars = sns.barplot(x="Benzerlik", y=df.index, data=df, 
                       orient="h", ax=ax, color="#007bff")
    
    # Çubuklarda etiketler ekle
    for index, (bar, row) in enumerate(zip(bars.patches, df.itertuples())):
        width = bar.get_width()
        
        # Uzun meslek başlıklarını sar
        wrapped_label = textwrap.fill(row.Meslek, width=40)
        
        ax.text(ax.get_xlim()[0] + 0.5, bar.get_y() + bar.get_height() / 2,
                wrapped_label, ha="left", va="center", 
                fontsize=12, color="white", weight="bold")
        
        # Benzerlik yüzdesini göster
        ax.text(width + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{width:.1f}%", va="center", ha="left", 
                color="#444", fontsize=12)
    
    return _fig_to_base64(fig)
```

### Frontend Uygulaması

#### Aşamalı Anket Arayüzü

```javascript
// app/static/js/script.js
function renderStep(stepIndex) {
    const category = steps[stepIndex];
    const stepQuestions = questions.filter(q => q.cat === category);
    
    surveyBody.innerHTML = '';
    stepQuestions.forEach(q => {
        const qIndex = questions.indexOf(q);
        const card = document.createElement('div');
        card.className = `survey-question-card cat-${q.cat.toLowerCase()}`;
        card.id = `q-card-${qIndex}`;
        
        // 5 puanlı Likert ölçeği oluştur
        let optionsHTML = '';
        for (let i = 1; i <= 5; i++) {
            const isChecked = userAnswers[qIndex] === i.toString();
            const isSelected = isChecked ? 'selected' : '';
            optionsHTML += `
                <label class="survey-option ${isSelected}">
                    <input type="radio" name="q${qIndex}" value="${i}" 
                           data-q-index="${qIndex}" ${isChecked ? 'checked' : ''}>
                    <span class="option-label">${optionLabels[i - 1]}</span>
                </label>
            `;
        }
        
        card.innerHTML = `
            <p class="question-text">${q.text}</p>
            <div class="survey-options">${optionsHTML}</div>
        `;
        
        surveyBody.appendChild(card);
    });
}

function submitSurvey() {
    // Cevapları RIASEC kategorisine göre organize et
    const answersForBackend = { R: [], I: [], A: [], S: [], E: [], C: [] };
    
    questions.forEach((q, index) => {
        if (userAnswers[index]) {
            answersForBackend[q.cat].push(parseInt(userAnswers[index]));
        }
    });
    
    // Backend'e gönder
    fetch('/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(answersForBackend)
    })
    .then(response => response.json())
    .then(data => renderResults(data, answersForBackend));
}
```

## Faz 4: AI Destekli Sohbet Arayüzü

### RAG (Retrieval-Augmented Generation) Uygulaması

Sohbet özelliği, bağlamsal kariyer tavsiyeleri sağlamak için gelişmiş bir RAG pipeline kullanır:

```python
# app/services.py
def get_ai_response(llm_client, onet_collection, user_question, 
                   profile_summary, model, embedding_model):
    """RAG pipeline kullanarak AI yanıtı oluştur"""
    
    # Adım 1: Sorgu embeddingini oluştur
    query_embedding = embedding_model.encode(user_question)
    
    # Adım 2: İlgili belgeler için vektör veritabanını ara
    search_results = onet_collection.search(query_embedding).limit(5).to_df()
    
    # Adım 3: Alınan belgelerden bağlam hazırla
    context_docs = []
    for _, result in search_results.iterrows():
        context_docs.append(f"Belge: {result['title']}\n{result['content']}")
    
    context = "\n\n".join(context_docs)
    
    # Adım 4: Bağlam ve kullanıcı profiliyle prompt oluştur
    system_prompt = f"""
    Kapsamlı mesleki verilere erişimi olan profesyonel kariyer danışmanısınız.
    
    Yönergeler:
    1. Kişilik & Ton: Profesyonel, cesaretlendirici ve anlayışlı olun. Kullanıcının 
       güvenini artıran pozitif bir ton kullanın.
    2. Bağlamı akıllıca kullanın: Sağlanan kullanıcı profilini ve iş belgelerini 
       yardımcı bağlam olarak kullanın. Desteklenmeyen ayrıntıları ileri sürmeyin.
    3. Sentez yapın, Sadece Listelemeyin: Kullanıcının ilgileri/becerilerini iş 
       görevleri veya ortamlarıyla ilişkilendirerek neden uygun olduğunu açıklayın.
    4. Yapı ve Biçimlendirme: Basit HTML etiketleri kullanın: bölümler için <h3>, 
       vurgu için <strong>, listeler için <ul>/<li>.
    
    Kullanıcı Profili: {profile_summary}
    
    O*NET Veritabanından Bağlam:
    {context}
    """
    
    # Adım 5: LLM kullanarak yanıt oluştur
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ]
    
    response = llm_client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=800,
        temperature=0.7
    )
    
    return response.choices[0].message.content
```

### Sohbet Arayüzü Entegrasyonu

```javascript
// Frontend sohbet uygulaması
function sendMessage() {
    const question = chatInput.value.trim();
    if (!question) return;
    
    // Kullanıcı mesajını sohbete ekle
    addChatMessage(question, 'user');
    chatInput.value = '';
    
    // Yazma göstergesini göster
    showTypingIndicator();
    
    // Backend'e gönder
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            question: question,
            profile_summary: userProfileSummary
        })
    })
    .then(response => response.json())
    .then(data => {
        hideTypingIndicator();
        if (data.answer) {
            addChatMessage(data.answer, 'assistant');
        }
    })
    .catch(error => {
        hideTypingIndicator();
        addChatMessage('Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.', 'assistant');
    });
}

function addChatMessage(content, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;
    
    if (sender === 'assistant') {
        // AI yanıtından HTML içeriği parse et
        messageDiv.innerHTML = `<div class="message-content">${content}</div>`;
    } else {
        messageDiv.innerHTML = `<div class="message-content">${escapeHtml(content)}</div>`;
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
```

## Faz 5: Konfigürasyon ve Deployment

### Ortam Konfigürasyonu

```python
# app/config.py
class Config:
    """Uygulama konfigürasyonu"""
    # API Anahtarları
    OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")
    
    # Model Ayarları
    LLM_CHAT_MODEL = "openai/gpt-oss-20b:free"  # Demo için ücretsiz model
    EMBEDDING_MODEL_NAME = "models/all-MiniLM-L6-v2"
    
    # Veritabanı yolları
    DATA_PATH = BASE_DIR / "data"
    VECTOR_DB_PATH = DATA_PATH / "lancedb_store"
    ONET_COLLECTION_NAME = "onet_data"
    
    # İşlenmiş veri dosya yolları
    ABILITIES_FILE_PATH = DATA_PATH / "abilities.parquet"
    INTERESTS_FILE_PATH = DATA_PATH / "interests.parquet"
    KNOWLEDGE_FILE_PATH = DATA_PATH / "knowledge.parquet"
    OCCUPATIONS_FILE_PATH = DATA_PATH / "occupations.parquet"
    SKILLS_FILE_PATH = DATA_PATH / "skills.parquet"
```

### Uygulama Fabrika Deseni

```python
# app/__init__.py
def create_app(config_class=Config):
    """Uygulama Fabrikası: Flask uygulamasını oluşturur ve yapılandırır"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    with app.app_context():
        # O*NET verilerini yükle ve işle
        (app.df_clustered_jobs, app.knowledge_map, 
         app.skills_map, app.abilities_map) = load_and_prepare_data(app.config)
        
        # LLM istemcisini başlat
        if app.config["OPEN_ROUTER_API_KEY"]:
            app.llm_client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=app.config["OPEN_ROUTER_API_KEY"]
            )
        
        # RAG bileşenlerini başlat
        app.lancedb_client = lancedb.connect(str(app.config["VECTOR_DB_PATH"]))
        app.embedding_model = SentenceTransformer(app.config["EMBEDDING_MODEL_NAME"])
        app.onet_collection = app.lancedb_client.open_table(app.config["ONET_COLLECTION_NAME"])
    
    # Route'ları kaydet
    from . import routes
    app.register_blueprint(routes.bp)
    
    return app
```

### Prodüksiyon Deployment

```bash
# requirements.txt - Ana bağımlılıklar
Flask==3.1.2
gunicorn==23.0.0
lancedb==0.25.1
matplotlib==3.10.6
numpy==2.3.3
openai==1.109.0
pandas==2.3.2
scikit-learn==1.7.2
sentence-transformers==5.1.1

# Deployment scripti
gunicorn --bind 0.0.0.0:$PORT run:app
```

## Teknik Zorluklar ve Çözümler

### Zorluk 1: Büyük Veri Seti İşleme

**Problem**: O*NET veritabanı birden fazla Excel dosyasında milyonlarca veri noktası içeriyor.

**Çözüm**: 
- Excel dosyalarını Parquet formatına dönüştürdük (%60-80 boyut azalması)
- Lazy loading ve önbellekleme stratejileri uyguladık
- Verimli veri manipülasyonu için pandas kullandık

### Zorluk 2: Gerçek Zamanlı Benzerlik Hesaplamaları

**Problem**: 1000+ meslek için gerçek zamanlı kosinüs benzerliği hesaplama.

**Çözüm**:
- Önceden hesaplanmış iş kümesi merkezleri
- Optimize edilmiş numpy vektorleştirmesi
- Önbelleğe alınmış benzerlik hesaplamaları

### Zorluk 3: Vektör Arama Performansı

**Problem**: RAG sistemi büyük bilgi bankasında hızlı semantik arama gerektiriyordu.

**Çözüm**:
- Verimli vektör depolama ve geri alma için LanceDB kullandık
- Daha iyi bağlam için örtüşmeli belge parçalama uyguladık
- Embedding oluşturma pipeline'ını optimize ettik

### Zorluk 4: Bellek Yönetimi

**Problem**: Modelleri ve verileri yüklemek önemli miktarda bellek tüketiyordu.

**Çözüm**:
- Sentence transformer modellerinin lazy loading'i
- Verimli veri yapıları (Parquet + pandas)
- Garbage collection optimizasyonu

## Performans Metrikleri ve Sonuçlar

### Sistem Performansı
- **Veri Yükleme**: Tam O*NET veritabanı için 2-3 saniye
- **Öneri Oluşturma**: Benzerlik hesaplamaları için <500ms
- **Grafik Oluşturma**: Görselleştirme oluşturma için <200ms
- **RAG Yanıtı**: LLM çıkarımı dahil 2-5 saniye

### Kullanıcı Deneyimi Metrikleri
- **Anket Tamamlama**: Gerçek zamanlı doğrulama ile aşamalı arayüz
- **Mobil Uyumlu**: Tüm cihaz boyutlarında çalışıyor
- **Erişilebilirlik**: Semantik HTML ve klavye navigasyonu
- **Yükleme Süresi**: İlk sayfa yüklemesi için <3 saniye

## Öğrenilenler ve En İyi Uygulamalar

### Veri İşleme
1. **Format Önemlidir**: Parquet dosyaları yükleme performansını önemli ölçüde iyileştirdi
2. **Ön İşleme Anahtardır**: Kümeleri ve embeddingleri önceden hesaplamak çalışma zamanından tasarruf sağlar
3. **Veri Doğrulama**: O*NET verilerini her zaman eksik değerler ve aykırı değerler için doğrulayın

### Makine Öğrenmesi
1. **Özellik Seçimi**: RIASEC skorları kariyer eşleştirmesi için son derece etkili oldu
2. **Kümeleme Doğrulama**: k=8 ile K-means optimal iş gruplandırmaları sağladı
3. **Benzerlik Metrikleri**: Kosinüs benzerliği ilgi eşleştirmesi için Euclidean mesafeden daha iyi performans gösterdi

### AI Entegrasyonu
1. **RAG Mimarisi**: Geri alma ile oluşturmanın birleştirilmesi doğru, bağlamsal yanıtlar sağlıyor
2. **Prompt Engineering**: Net yönergeli yapılandırılmış promptlar yanıt kalitesini artırıyor
3. **Model Seçimi**: Ücretsiz modeller (gpt-oss-20b) demolar için iyi sonuçlar verebilir

### Kullanıcı Deneyimi
1. **Aşamalı Açıklama**: Çok adımlı anket bilişsel yükü azaltıyor
2. **Görsel Geri Bildirim**: Grafikler kullanıcıların ilgi profillerini anlamalarına yardımcı oluyor
3. **Sohbet Arayüzü**: Sohbet özelliği etkileşimi artırıyor ve kişiselleştirilmiş rehberlik sağlıyor

## Gelecek Geliştirmeler

### Teknik İyileştirmeler
1. **Gerçek Zamanlı Öğrenme**: Önerileri iyileştirmek için kullanıcı geri bildirimini uygula
2. **Gelişmiş ML**: Neural collaborative filtering ile deneyim yap
3. **Çok Modlu Girdi**: Özgeçmiş/CV analiz yetenekleri ekle
4. **A/B Testi**: Farklı öneri algoritmalarını uygula

### Özellik Eklentileri
1. **Kariyer Yolları**: Meslekler arası ilerleme rotalarını göster
2. **Maaş Entegrasyonu**: Önerilere ücret verilerini dahil et
3. **Beceri Açığı Analizi**: İstenilen kariyerler için eğitim ihtiyaçlarını belirle
4. **Sektör Trendleri**: İş piyasası tahminlerini dahil et

### Ölçeklenebilirlik
1. **Mikroservis Mimarisi**: ML pipeline'ı web arayüzünden ayır
2. **Önbellek Katmanı**: Sık erişilen veriler için Redis uygula
3. **Yük Dengeleme**: Birden çok eş zamanlı kullanıcıyı işle
4. **API Geliştirme**: Üçüncü taraf entegrasyonları için genel API oluştur

## Sonuç

OccumendAI'yi geliştirmek, modern web teknolojilerinin yerleşik psikoloji teorileri ve son teknoloji AI ile nasıl birleştirilerek gerçek dünya problemlerini çözebileceğini gösteren inanılmaz bir yolculuk oldu. Proje şunları sergiliyor:

- **Veri Mühendisliği**: Büyük veri setlerini prodüksiyon kullanımı için işleme ve optimize etme
- **Makine Öğrenmesi**: Kişiselleştirilmiş öneriler için kümeleme ve benzerlik algoritmaları uygulama  
- **AI Entegrasyonu**: Akıllı sohbet arayüzleri için RAG sistemleri oluşturma
- **Full-Stack Geliştirme**: Duyarlı, kullanıcı dostu web uygulamaları oluşturma
- **Prodüksiyon Deployment**: Uygulamaları gerçek dünya kullanımı için ölçeklendirme

En tatmin edici yönü, teknolojinin kariyer rehberliğini daha erişilebilir ve kişiselleştirilmiş hale nasıl getirebildiğini görmek oldu. Holland Kodu değerlendirmesini modern AI ile birleştirerek, hem bilimsel temelli öneriler hem de kişiselleştirilmiş sohbet rehberliği sağlayan bir araç yarattık.

ML uygulamalarıyla ilgilenen bir geliştirici, teknoloji araçlarını keşfeden bir kariyer danışmanı veya sadece psikoloji ve AI kesişimini merak eden biri olun, OccumendAI'nin geliştirilmesine dair bu derinlemesine incelemenin kendi projeleriniz için değerli içgörüler ve ilham sağlamasını umuyorum.

## Kaynaklar ve Referanslar

### Teknik Dokümantasyon
- [Flask Dokümantasyonu](https://flask.palletsprojects.com/)
- [Scikit-learn Kullanıcı Rehberi](https://scikit-learn.org/stable/user_guide.html)
- [LanceDB Dokümantasyonu](https://lancedb.github.io/lancedb/)
- [Sentence Transformers](https://www.sbert.net/)

### Veri Kaynakları
- [O*NET Veritabanı](https://www.onetcenter.org/database.html)
- [O*NET İlgi Profili](https://www.mynextmove.org/explore/ip)
- [Holland Kodu Teorisi](https://en.wikipedia.org/wiki/Holland_Codes)

### Proje Deposu
- **Kaynak Kod**: [GitHub - OccumendAI](https://github.com/hllzmz/occumend-ai)
- **Canlı Demo**: [OccumendAI Uygulaması](https://occumendai-d0f6abgrcwagagbp.germanywestcentral-01.azurewebsites.net)

---

*Okuduğunuz için teşekkür ederim! Bu makaleyi faydalı bulduysanız, lütfen alkışlayın ve AI ve web geliştirme projelerine dair daha fazla derinlemesine inceleme için takip edin. Sorularınız veya gelecek makaleler için önerileriniz varsa lütfen iletişime geçmekten çekinmeyin.*

**Etiketler**: #AI #MakineÖğrenmesi #WebGeliştirme #Flask #Python #KariyerRehberliği #VeriBlimi #RAG #VektörArama #Psikoloji