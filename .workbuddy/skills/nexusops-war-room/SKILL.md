---
name: nexusops-war-room
description: "Orkestrasi NexusOps Spatial War Room & Workplace Brain (SOP-ENG-082, SOP-OPS-014, insiden pembayaran/payment, database congestion, mitigasi otomatis, dan post-mortem report). Gunakan skill ini setiap kali pengguna meminta cek status operasional NexusOps, menjalankan simulasi insiden pembayaran/database, atau mengeksekusi mitigasi otomatis."
description_en: "Orchestrate NexusOps Spatial War Room & Workplace Brain (SOP retrieval, payment/DB incident simulation, PIC task dispatch, automated mitigation, and post-mortem audit). Always use this skill when the user mentions NexusOps, payment incident simulation, or automated mitigation."
disable: false
---

# NexusOps Spatial War Room & Workplace Brain Skill

File Knowledge Base SOP: `./sop_data.json`
Skrip Eksekutor CLI: `./workbuddy_cli.py`

## Instruksi Wajib Saat Pengguna Memberikan Perintah

1. **Saat pengguna meminta cek status operasional NexusOps & simulasi insiden pembayaran** (contoh: *"WorkBuddy, tolong cek status operasional NexusOps dan jalankan simulasi insiden pembayaran jika ada gangguan"*):
   - Jalankan perintah terminal berikut:
     ```bash
     python3 ./workbuddy_cli.py trigger-payment
     ```
2. **Saat pengguna meminta eksekusi mitigasi otomatis** (contoh: *"Eksekusi mitigasi otomatis sekarang"*):
   - Jalankan perintah terminal:
     ```bash
     python3 ./workbuddy_cli.py mitigate
     ```
3. **Saat pengguna meminta reset sistem ke normal**:
   - Jalankan perintah terminal:
     ```bash
     python3 ./workbuddy_cli.py reset
     ```
