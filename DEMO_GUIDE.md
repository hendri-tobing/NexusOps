# PANDUAN DEMO & INTEGRASI TENCENT CLOUD WORKBUDDY

**Kompetisi:** Tencent Cloud AI CAN DO IT Hackathon Indonesia 2026  
**Track:** Challenge A (The Workplace Brain) & Challenge B (The Office Agent)  
**Komponen Utama:** Tencent Cloud WorkBuddy Desktop AI App + NexusOps Spatial War Room  

---

## 1. MENGAPA TENCENT CLOUD WORKBUDDY DIGUNAKAN?
Dalam arsitektur submission ini, **Tencent Cloud WorkBuddy Desktop App** bertindak sebagai *Workplace Brain* (Challenge A) sekaligus *Office Agent* utama (Challenge B) yang memimpin orkestrasi penanganan insiden lintas fungsi:
- **Workspace Library Integration (Challenge A):** WorkBuddy mengindeks dokumen SOP perusahaan ([`sop_data.json`](sop_data.json)) secara langsung dari *local workspace* tanpa migrasi manual untuk melakukan *semantic matching* saat insiden terjadi.
- **Natural Language Desktop Execution (Challenge B):** Operator cukup memberikan perintah bahasa natural di aplikasi **Tencent Cloud WorkBuddy Desktop**, dan WorkBuddy mengeksekusi orkestrasi war-room melalui bridge CLI/API lokal ([`workbuddy_cli.py`](workbuddy_cli.py)).
- **Live Spatial Radar Synchronization:** Setiap tindakan yang dieksekusi oleh **WorkBuddy Desktop App** langsung tersinkronisasi secara *real-time* (melalui `/api/state`) ke layar visualisasi **NexusOps Spatial War Room** di browser (`http://127.0.0.1:8765`).

---

## 2. LANGKAH PERSIAPAN DEMO LOKAL
1. **Jalankan Backend & Server Simulasi NexusOps:**
   ```bash
   ./run_demo.sh
   ```
2. **Buka Tencent Cloud WorkBuddy Desktop App (`WorkBuddy AI.app` — Wajib):**
   - Buka aplikasi `WorkBuddy AI.app` di komputer Anda.
   - **Cara Menghubungkan Workspace:**
     1. Di bagian bawah kolom chat `WorkBuddy AI.app` (atau saat membuat *New Task*), klik ikon **Folder / Workspace** lalu pilih folder proyek `WorkBuddy` ini.
     2. Begitu folder dipilih, WorkBuddy otomatis membaca skill bawaan di [`.workbuddy/skills/nexusops-war-room/SKILL.md`](.workbuddy/skills/nexusops-war-room/SKILL.md), mengenali [`sop_data.json`](sop_data.json), serta memetakan perintah ke [`workbuddy_cli.py`](workbuddy_cli.py).
     3. *(Opsional — Global Skill)* Agar perintah NexusOps dapat dipanggil dari sesi WorkBuddy mana saja, salin skill ke direktori user WorkBuddy:
        ```bash
        mkdir -p ~/.workbuddy-ai/skills/nexusops-war-room
        cp .workbuddy/skills/nexusops-war-room/SKILL.md ~/.workbuddy-ai/skills/nexusops-war-room/SKILL.md
        ```
     4. *(Opsional)* Anda juga dapat mengetik `@sop_data.json` atau `@DEMO_GUIDE.md` langsung di kolom chat WorkBuddy untuk me-*refer* file secara eksplisit.
3. **Buka Dashboard Visual Spatial War Room (Side-by-Side):**
   - Buka browser di `http://127.0.0.1:8765` dan letakkan berdampingan dengan jendela **WorkBuddy AI.app**.
   - Pastikan indikator di atas dashboard mendeteksi proses asli aplikasi dan menampilkan **`WorkBuddy Desktop: LIVE (PID xxxx)`**.

---

## 3. SKENARIO DEMO DI DEPAN DEWAN JURI (MENGGUNAKAN WORKBUDDY DESKTOP APP)

* **Fase 1: Perintah Natural Language ke WorkBuddy Desktop**
  - Di dalam panel chat **Tencent Cloud WorkBuddy Desktop App**, ketik atau berikan perintah suara:
    > *"WorkBuddy, tolong cek status operasional NexusOps dan jalankan simulasi insiden pembayaran jika ada gangguan."*
  - **Aksi Agen WorkBuddy Desktop:** Mengeksekusi `./workbuddy_cli.py trigger-payment` (atau `POST http://127.0.0.1:8765/api/incident/trigger?type=payment`).
  - **Hasil Visual:** Radar spasial di browser (`http://127.0.0.1:8765`) seketika berubah menjadi **MERAH** (*CRITICAL ANOMALY DETECTED* pada node *Payment Core*).

* **Fase 2: Deteksi Insiden & RAG SOP Retrieval (Challenge A - Workplace Brain)**
  - **WorkBuddy Desktop** mendeteksi *timeout 504* pada *Payment Core*, lalu mencocokkan gejala tersebut dengan Knowledge Library ([`sop_data.json`](sop_data.json)) dan menampilkan **SOP-ENG-082 (Payment Webhook Timeout & Gateway Failover)** baik di chat WorkBuddy Desktop maupun di panel *Workplace Brain* pada layar War Room.

* **Fase 3: Delegasi Tugas Lintas Fungsi (Challenge B - Office Agent Action)**
  - Berdasarkan **SOP-ENG-082**, **WorkBuddy Desktop** secara otomatis mendispatch *action items* ke PIC terkait beserta ETA:
    1. **Budi Pratama (Payment Lead)** — *Trigger Redundant Ingress Failover* (ETA: 2m)
    2. **Rizky Sanjaya (SRE Lead)** — *Engage Redis Idempotency Queue* (ETA: 1m)
    3. **Sarah Amalia (CS Lead)** — *Dispatch Merchant Status Notice* (ETA: 3m)

* **Fase 4: Eksekusi Mitigasi & Post-Mortem Audit**
  - Berikan konfirmasi di **Tencent Cloud WorkBuddy Desktop App**:
    > *"Eksekusi mitigasi otomatis sekarang."*
  - **Aksi Agen WorkBuddy Desktop:** Mengeksekusi `./workbuddy_cli.py mitigate` (atau `POST http://127.0.0.1:8765/api/incident/mitigate`).
  - **Hasil Visual:** WorkBuddy mengeksekusi *failover*, status seluruh tugas berubah menjadi **RESOLVED**, radar spasial kembali **HIJAU** (*ALL SYSTEMS RECOVERED*), dan laporan audit **Executive Post-Mortem** langsung tercetak di WorkBuddy Desktop, ditampilkan di dashboard War Room, serta disimpan sebagai file fisik [`POST_MORTEM_LATEST.md`](POST_MORTEM_LATEST.md) di dalam *workspace*.

---

## 4. REFERENSI PERINTAH UNTUK AGENT WORKBUDDY DESKTOP
> Catatan untuk AI Agent di dalam **Tencent Cloud WorkBuddy Desktop**: Gunakan skrip atau endpoint berikut saat pengguna memberikan instruksi di atas:

| Instruksi Pengguna di WorkBuddy Desktop | Perintah CLI yang Dieksekusi WorkBuddy | Endpoint HTTP Alternatif |
| :--- | :--- | :--- |
| Cek status / kesehatan sistem | `./workbuddy_cli.py status` | `GET http://127.0.0.1:8765/api/state` |
| Simulasi insiden pembayaran (*Payment*) | `./workbuddy_cli.py trigger-payment` | `POST http://127.0.0.1:8765/api/incident/trigger?type=payment` |
| Simulasi insiden database (*DB Pool*) | `./workbuddy_cli.py trigger-db` | `POST http://127.0.0.1:8765/api/incident/trigger?type=db` |
| Eksekusi mitigasi otomatis sekarang | `./workbuddy_cli.py mitigate` | `POST http://127.0.0.1:8765/api/incident/mitigate` |
| Reset status war room ke normal | `./workbuddy_cli.py reset` | `POST http://127.0.0.1:8765/api/incident/reset` |
