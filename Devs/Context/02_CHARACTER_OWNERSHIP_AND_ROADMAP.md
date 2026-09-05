# 👥 Contexto de Asignación de Personajes y Calendario de Sprints
## Street Fighter III: 3rd Strike (Unity + Azure Kinect + IA Adaptativa)

Este documento define la propiedad de cada personaje y el calendario de desarrollo para el equipo de 3 desarrolladores.

---

### 🥋 Propiedad Estricta por Personaje (100% End-to-End)

Cada desarrollador es dueño absoluto de su personaje:
1. **👑 MARCO (Lead / Ryu / ML-Agents):**
   - **Personaje:** **Ryu** (`02_Ryu`). Sprites, Animaciones, Hitboxes, Hurtboxes y Hadouken/Shoryuken.
   - **Módulos Core:** Máquina de Estados, Física y Entrenamiento de IA en GPU RTX 4060 (Unity ML-Agents / PyTorch).
2. **🔥 SEBAS (Dev 2 / Ken / VFX & Audio):**
   - **Personaje:** **Ken** (`01_Ken`). Sprites, Animaciones, Hitboxes, Hurtboxes y Shoryuken Ígneo.
   - **Módulos Core:** Escenarios Parallax (Japón / China), Prefabs de VFX (Hadouken, Chispas, Parry) y `SF3SoundManager`.
3. **⚡ KEVIN (Dev 3 / Chun-Li / Kinect & SQLite):**
   - **Personaje:** **Chun-Li** (`03_ChunLi`). Sprites, Animaciones, Hitboxes, Hurtboxes y Hyakuretsukyaku.
   - **Módulos Core:** Pipeline de Azure Kinect (gestos 3D), UI/HUD y Base de Datos local SQLite.

---

### 📅 Fechas Oficiales de Sprints y Martes de Laboratorio

* **Sprint 1:** Sep 7 – Sep 20 (Lab: Mar 8 y Mar 15 Sep)
* **Sprint 2:** Sep 21 – Oct 4 (Lab: Mar 22 y Mar 29 Sep)
* **Sprint 3:** Oct 5 – Oct 18 (Lab: Mar 6 y Mar 13 Oct)
* **Sprint 4:** Oct 19 – Nov 1 (Lab: Mar 20 y Mar 27 Oct)
* **Sprint 5:** Nov 2 – Nov 15 (Lab: Mar 3 y Mar 10 Nov)
* **Sprint 6:** Nov 16 – Nov 30 (Lab: Mar 17 y Mar 24 Nov)
* 🎯 **Entrega y Sustentación Oficial:** **Martes 1 de Diciembre de 2026**
