# 🥋 Street Fighter III: 3rd Strike - Kinect & Adaptive AI Experience
## Videojuego de Combate 2D Basado en Sprites con Control Somatosensorial 3D e Inteligencia Artificial Adaptativa
**Proyecto Universitario de Desarrollo de Videojuegos e Inteligencia Artificial**  
**Motor:** Unity 2022.3 LTS / Unity 6 (URP 2D) | **Hardware:** Sensor Microsoft Azure Kinect DK | **IA:** Unity ML-Agents + PyTorch CUDA (RTX 4060)

---

### 👥 Equipo de Desarrollo y Propiedad de Personajes

| Desarrollador | GitHub | Personaje Asignado (100%) | Responsabilidades Core |
| :--- | :--- | :--- | :--- |
| **👑 MARCO** | [`@MarcoXMarquez`](https://github.com/MarcoXMarquez) | **Ryu** (`02_Ryu`) | Arquitectura Core, Máquina de Estados, Física y Entrenamiento de IA en GPU (ML-Agents / PyTorch). |
| **🔥 SEBAS** | [`@Sebastianzzzin`](https://github.com/Sebastianzzzin) | **Ken** (`01_Ken`) | Animaciones/Hitboxes de Ken, Escenarios Parallax (Japón / China), VFX de Impacto y Audio SoundManager. |
| **⚡ KEVIN** | [`@KevinCallo`](https://github.com/KevinCallo) | **Chun-Li** (`03_ChunLi`) | Animaciones/Hitboxes de Chun-Li, Pipeline Azure Kinect (32 articulaciones), HUD Arcade y SQLite. |

---

### 🚀 Inicio Rápido para Desarrolladores del Equipo

Al clonar este repositorio por primera vez, ejecuta el script de auto-configuración en tu terminal:
```bash
python Tools/setup_team_workspace.py
```
El script verificará tu configuración de Git, comprobará las carpetas de Unity y te mostrará tu tarea activa del Sprint 1 con el comando para crear tu rama de Git.

---

### 📅 Plan Maestro de Sprints y Laboratorios Martes (Kinect)

* **Sprint 1 (Sep 7 – Sep 20):** Motor 2D Base, Animaciones a 14 FPS y Emulador de Teclado.
* **Sprint 2 (Sep 21 – Oct 4):** Hitboxes/Hurtboxes de 3 piezas, Hadouken, Parry y Puñetazo en Kinect.
* **Sprint 3 (Oct 5 – Oct 18):** Ken y Chun-Li Integrados, Base de Datos SQLite y Grabador de Telemetría.
* **Sprint 4 (Oct 19 – Nov 1):** IA Fase 1 (Imitación / Behavioral Cloning en GPU) y Gestos Pro en Kinect.
* **Sprint 5 (Nov 2 – Nov 15):** IA Fase 2 (Refuerzo PPO + Dificultad Dinámica DDA) y HUD Arcade.
* **Sprint 6 (Nov 16 – Nov 30):** Calibración de Latencia, Optimización y Build Standalone `.exe` a 60 FPS.
* 🎯 **ENTREGA FINAL:** **Martes 1 de Diciembre de 2026**.

*Nota: Todos los **martes** se realiza la sesión presencial de pruebas con el sensor Azure Kinect físico en el laboratorio de la universidad.*

---

### 📂 Estructura del Proyecto

```text
StreetFighter3_ThirdStrike/
├── Assets/StreetFighter3_ThirdStrike/
│   ├── Characters/                  # 20 Luchadores Arcade CPS-3
│   │   ├── 01_Ken/                  # Ken Masters (Sebas)
│   │   ├── 02_Ryu/                  # Ryu (Marco)
│   │   └── 03_ChunLi/               # Chun-Li (Kevin)
│   ├── Stages/                      # Escenarios 2.5D Multicapa
│   ├── Scripts/                     # Arquitectura modular de C# (Core, Combat, Input, AI...)
│   └── Docs/Manuales_Junior_Devs/   # 15 Manuales técnicos paso a paso
│
├── Devs/                            # Guías de tareas por desarrollador
│   ├── README_GIT_WORKFLOW.md       # Reglas de ramas, commits y Pull Requests
│   ├── Context/                     # Memoria compartida y changelog vivo para IAs
│   ├── Marco/                       # Tareas de Marco (Sprint 1 al 6)
│   ├── Sebas/                       # Tareas de Sebas (Sprint 1 al 6)
│   └── Kevin/                       # Tareas de Kevin (Sprint 1 al 6)
│
├── .agent/skills/                   # Habilidades y reglas para agentes Antigravity
│   └── sf3-team-developer/          # Modo tutor pedagógico y convenciones de equipo
│
└── Tools/                           # Scripts de automatización y generadores
    ├── setup_team_workspace.py      # Configuración de entorno local
    └── generate_all_sprint_tasks.py # Generador de tareas de Sprints
```

---

### 📚 Índice de Documentación y Manuales

Dentro de [`Assets/StreetFighter3_ThirdStrike/Docs/Manuales_Junior_Devs/`](Assets/StreetFighter3_ThirdStrike/Docs/Manuales_Junior_Devs/00_INDICE_Y_ROADMAP_PROYECTO.md):
1. `01`: Configuración de Sprites Pixel-Perfect a 100 PPU.
2. `02`: Creación de Animaciones Paso a Paso a 14 FPS.
3. `03`: Jerarquía y Arquitectura del Luchador (`Root`, `Visuals`, `Pushbox`, `Hurtbox`, `Hitbox`).
4. `04`: Animator Controller y Máquina de Estados Frame-Perfect.
5. `05`: Hitboxes, Hurtboxes y Animation Events.
6. `06`: Escenarios Parallax y Cámara 2.5D.
7. `07`: Efectos Visuales y Prefabs.
8. `08`: Audio, Voces y Sound Manager Singleton.
9. `09`: Arquitectura de Entrada y Preparación para Azure Kinect (`IFighterInput`).
10. `10`: Checklist de Verificación Final.
11. `11`: Estructura y Arquitectura de Scripts (`Core`, `Combat`, `Input`...).
12. `12`: Plan Maestro de Sprints y Asignaciones para 3 Desarrolladores.
13. `13`: Guía de GitHub Projects, Tablero Kanban y Flujos Automáticos.
14. `14`: Detalle de los 6 Milestones y 36 Tareas Atómicas.
15. `15`: Guía de Git Flow, Ramas y Sincronización del Equipo.

---

### 🛠️ Herramientas de Editor Automatizadas (En Unity)

En la barra superior de Unity (`SF3 Tools`):
* **Auto-Generate Animation Clips:** Genera clips a 14 FPS automáticamente para cualquier carpeta seleccionada.
* **Auto-Populate Animator Controller:** Sincroniza todos los clips `.anim` de un personaje en su `AnimatorController` en 1 clic.
* **Auto Sprite Importer:** Aplica `Point Filter`, `Uncompressed` y `BottomCenter` a sprites nuevos.
