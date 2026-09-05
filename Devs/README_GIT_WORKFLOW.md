# 🥋 Guía Maestra de Git y Flujo de Trabajo para Desarrolladores
## Street Fighter III: 3rd Strike (Unity + Azure Kinect + IA Adaptativa)

¡Bienvenidos al equipo! Esta carpeta `Devs/` contiene las carpetas personales para **Marco, Sebas y Kevin** con las guías de cada tarea de Sprint.

---

### 🌳 Convención Estricta de Nombres de Ramas

Cada rama de Git debe seguir este formato exacto:
`feature/sp<NUMERO_SPRINT>-<DEV>-<NOMBRE_CORTO>`

* **Marco (Sprint 1):**
  * `feature/sp1-marco-statemachine` (Tarea #1)
  * `feature/sp1-marco-ryu-anim` (Tarea #2)
* **Sebas (Sprint 1):**
  * `feature/sp1-sebas-ken-anim` (Tarea #3)
  * `feature/sp1-sebas-japan-stage` (Tarea #4)
* **Kevin (Sprint 1):**
  * `feature/sp1-kevin-chunli-anim` (Tarea #5)
  * `feature/sp1-kevin-input-kinect` (Tarea #6)

---

### 🔄 Los 5 Comandos Obligatorios de Git

```
1. Actualizar main:          git checkout main && git pull origin main
2. Crear tu rama:            git checkout -b feature/tu-rama
3. Guardar cambios:          git add . && git commit -m "feat: descripcion (#ID)"
4. Subir a GitHub:           git push -u origin feature/tu-rama
5. Abrir Pull Request:       En GitHub.com > Compare & pull request > "Closes #ID"
```

---

### 📂 Estructura de Carpetas Personales
```
Devs/
├── README_GIT_WORKFLOW.md
├── Marco/
│   └── Sprint_1/
│       ├── TASK_SP1_01_STATEMACHINE_PHYSICS.md
│       └── TASK_SP1_02_RYU_ANIMATION_PIPELINE.md
├── Sebas/
│   └── Sprint_1/
│       ├── TASK_SP1_03_KEN_ANIMATION_PIPELINE.md
│       └── TASK_SP1_04_JAPAN_STAGE_PARALLAX.md
└── Kevin/
    └── Sprint_1/
        ├── TASK_SP1_05_CHUNLI_ANIMATION_PIPELINE.md
        └── TASK_SP1_06_IFIGHTER_INPUT_KINECT_SETUP.md
```

Cada archivo `.md` contiene los comandos de terminal exactos, la descripción del código y un **Prompt listo para que Antigravity les programe la tarea**.
