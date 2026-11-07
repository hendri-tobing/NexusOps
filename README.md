# NexusOps — Autonomous Spatial War Room & Workplace Brain
**Target Competition:** Tencent Cloud AI CAN DO IT Hackathon Indonesia 2026  
**Tracks:** Challenge A (The Workplace Brain) & Challenge B (The Office Agent)  
**Core Agent Platform:** Tencent Cloud WorkBuddy Desktop App  

---

## 1. The Core Problem: The Silent Execution Gap
During enterprise outages or operational bottlenecks:
- Incidents are detected in telemetry, but human coordination takes 20–45 minutes of panic across disparate chat channels.
- Corporate knowledge (SOPs, runbooks, historical post-mortems) sits passively inside Notion, Confluence, or PDFs without being connected to live operational execution.

## 2. The Solution: NexusOps + Tencent Cloud WorkBuddy Desktop
NexusOps unifies **The Workplace Brain** and **The Office Agent** by pairing **Tencent Cloud WorkBuddy Desktop App** with a live **Spatial War Room**:
1. **WorkBuddy Workspace Library (Challenge A):** Indexes corporate SOPs ([`sop_data.json`](sop_data.json)) directly inside the Tencent Cloud WorkBuddy Desktop workspace to match incident symptoms to validated mitigation runbooks (`SOP-ENG-082`, `SOP-OPS-014`).
2. **Natural Language Office Agent (Challenge B):** Operators command **Tencent Cloud WorkBuddy Desktop** in natural language to trigger diagnostics, dispatch tasks to PICs (Budi Pratama, Rizky Sanjaya, Sarah Amalia), and execute automated failovers via [`workbuddy_cli.py`](workbuddy_cli.py).
3. **Live Spatial Topology Radar:** An interactive 60 FPS radar (`http://127.0.0.1:8765`) synchronized in real time with WorkBuddy Desktop actions.
4. **C-Level Executive Post-Mortem:** Automatically generates an audit-ready post-mortem report upon mitigation completion.

---

## 3. Quickstart & Live Demo Setup
1. Start the NexusOps server:
   ```bash
   ./run_demo.sh
   ```
2. Open the Spatial War Room Dashboard in your browser:
   `http://127.0.0.1:8765`
3. Connect **Tencent Cloud WorkBuddy Desktop App (`WorkBuddy AI.app`)** to this workspace:
   - **Via Workspace Folder Picker:** Open `WorkBuddy AI.app`, click the **Folder / Workspace** icon at the bottom of the chat input bar (or when starting a *New Task*), and select this repository folder (`WorkBuddy`).
   - **Automatic Project Skill Discovery:** Once this folder is selected as the workspace, WorkBuddy automatically loads the bundled skill at [`.workbuddy/skills/nexusops-war-room/SKILL.md`](.workbuddy/skills/nexusops-war-room/SKILL.md), indexing [`sop_data.json`](sop_data.json) and binding [`workbuddy_cli.py`](workbuddy_cli.py).
   - **Optional Global Skill Install:** To allow WorkBuddy Desktop to run NexusOps commands from any session, copy the skill to your user skill directory:
     ```bash
     mkdir -p ~/.workbuddy-ai/skills/nexusops-war-room
     cp .workbuddy/skills/nexusops-war-room/SKILL.md ~/.workbuddy-ai/skills/nexusops-war-room/SKILL.md
     ```
4. Follow the step-by-step judge scenario in **[DEMO_GUIDE.md](DEMO_GUIDE.md)**.
