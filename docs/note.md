Rencana Penelitian: Pengembangan Sistem Agentic RAG Teologi Katolik
1. Judul Penelitian

Optimasi Information Retrieval pada Domain Teologi Katolik Menggunakan Agentic RAG dengan Arsitektur Hybrid LLM Orchestration.
2. Kebaruan Penelitian (Novelty)

    Spesialisasi Domain: Pengembangan basis pengetahuan (knowledge base) teologi Katolik terlengkap dalam bahasa Indonesia yang mengintegrasikan Alkitab, Kitab Hukum Kanonik (KHK), dan Katekismus Gereja Katolik (KKGK) ke dalam satu sistem terpadu.

    Arsitektur Hybrid: Implementasi model bahasa Llama 3 sebagai local agent router untuk klasifikasi intensi dan keamanan data, yang dikombinasikan dengan Gemini API sebagai generator sintesis jawaban.

    Agentic Routing: Penggunaan logika agen otomatis yang mampu membedakan kategori pertanyaan (doktrinal, biblika, atau legal) untuk memastikan akurasi sitasi dari sumber otoritatif gereja.

3. Rumusan Masalah

    Bagaimana mengintegrasikan dataset teologi Katolik yang bersifat heterogen (JSONL, PDF, XLSX) menjadi sebuah unified knowledge base yang terstruktur dan terstandarisasi?

    Bagaimana efektivitas arsitektur Hybrid LLM dalam meminimalisir halusinasi informasi pada domain sensitif yang memerlukan tingkat akurasi tinggi?

    Sejauh mana implementasi Agentic RAG dapat meningkatkan relevansi jawaban dibandingkan dengan sistem pencarian informasi konvensional pada lingkungan Gereja St. Yohanes Girisekar?

4. Abstrak

    Abstrak

    Penyajian informasi teologi Katolik yang akurat sering kali terkendala oleh fragmentasi sumber data dan risiko halusinasi pada model bahasa besar (Large Language Models). Penelitian ini bertujuan untuk membangun sistem Agentic Retrieval-Augmented Generation (RAG) yang mampu melakukan pencarian informasi secara presisi pada domain spesifik teologi Katolik. Metodologi yang digunakan mencakup akuisisi data heterogen dari berbagai sumber otoritatif menjadi format .jsonl yang terstandarisasi. Kebaruan riset ini terletak pada penerapan arsitektur Hybrid LLM Orchestration, di mana Llama 3 berfungsi sebagai pengatur rute intensi lokal dan Gemini API sebagai penyintesis output akhir. Hasil penelitian diharapkan dapat meminimalisir kesalahan interpretasi doktrin serta menyediakan dataset sekunder yang berkualitas bagi pengembang dan peneliti AI di masa mendatang.

5. Hasil Konsultasi Akademik

    Orientasi Produk: Penelitian ini dinilai unggul karena memiliki luaran konkret berupa produk yang dapat diintegrasikan dengan infrastruktur web gereja.

    Kontribusi Data Sekunder: Fokus penelitian diarahkan pada penyediaan data sekunder yang bersih dan terstruktur untuk mendukung ekosistem pengembangan perangkat lunak bagi peneliti lain.

    Ekspansi Dataset: Pentingnya penambahan volume data dari sumber-sumber tambahan seperti dokumen pastoral KWI guna memperkuat basis pengetahuan sistem.