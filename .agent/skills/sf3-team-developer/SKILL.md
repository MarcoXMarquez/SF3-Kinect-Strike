---
name: sf3-team-developer
description: Guía y tutor de desarrollo para el equipo de Street Fighter III (Marco, Sebas, Kevin). Aplica pedagogía paso a paso, convenciones de 100 PPU / 14 FPS / Mecanim desacoplado, reglas de Git, sincronización dinámica de contexto y propiedad de personajes.
---

# SF3 Team Developer Skill

Esta habilidad guía a los asistentes de Antigravity para trabajar de forma coordinada, pedagógica y sincronizada en el proyecto **Street Fighter III: 3rd Strike (Unity + Azure Kinect + IA Adaptativa)**.

---

## 1. Modo Tutor Pedagógico Obligatorio
Cuando un desarrollador te pida ayuda con una tarea de `Devs/`:
- **No generes código monolítico sin explicar.**
- Explica la lógica matemática y arquitectónica paso a paso.
- Proporciona fragmentos claros y guía al desarrollador para que implemente, pruebe y valide en Unity.
- Revisa el cumplimiento de los **Criterios de Aceptación** de la tarea.

---

## 2. Protocolo de Sincronización Dinámica de Contexto (`Devs/Context/`)
**Regla Estricta:** La carpeta `Devs/Context/` es la memoria compartida entre todos los desarrolladores y agentes de IA.

1. **Al iniciar cualquier sesión o tarea:**
   - Lee siempre [`Devs/Context/05_PROJECT_LIVE_STATUS.md`](file:///c:/Users/marco/2026%20B/Desarrollo%20de%20Juegos/StreetFighter3_ThirdStrike/Devs/Context/05_PROJECT_LIVE_STATUS.md) y [`Devs/Context/01_PROJECT_ARCHITECTURE_AND_CONVENTIONS.md`](file:///c:/Users/marco/2026%20B/Desarrollo%20de%20Juegos/StreetFighter3_ThirdStrike/Devs/Context/01_PROJECT_ARCHITECTURE_AND_CONVENTIONS.md) para conocer el estado actual y los scripts ya creados por otros compañeros.
2. **Al completar, modificar, refactorizar o eliminar código/assets:**
   - **DEBES actualizar automáticamente** el archivo `Devs/Context/05_PROJECT_LIVE_STATUS.md` registrando el nuevo script, cambio de arquitectura o elemento deprecado en la tabla correspondiente.
   - De esta forma, cuando otro compañero haga `git pull origin main`, su propio agente de IA sabrá exactamente qué hiciste y cómo conectarse a tu código.

---

## 3. Convenciones Técnicas de Unity y CPS-3
- **Sprites:** `Pixels Per Unit: 100`, `Filter Mode: Point (no filter)`, `Compression: None`.
- **Animaciones:** Tasa arcade exacta de **14 FPS** (`frameRate = 14`).
- **Pivote:** `BottomCenter` (`Vector2(0.5f, 0.0f)`). El suelo siempre está en $Y = 0$.
- **Mecanim:** Prohibido crear telarañas de transiciones con flechas. Usar siempre `animator.Play(clipName, 0, 0f)`.
- **Transiciones instantáneas:** Cero tiempo de transición (`Transition Duration = 0`, `Has Exit Time = False`) para respuesta en frame 1.

---

## 4. Propiedad de Personajes y Ramas
- **Marco:** Ryu (`02_Ryu`) + Core / Machine Learning (`feature/spX-marco-...`).
- **Sebas:** Ken (`01_Ken`) + Escenarios Parallax / VFX / Audio (`feature/spX-sebas-...`).
- **Kevin:** Chun-Li (`03_ChunLi`) + Azure Kinect / SQLite / UI (`feature/spX-kevin-...`).

---

## 5. Estructura de Scripts (`Assets/.../Scripts/`)
- `Core/`: Máquinas de estado, física, GameManager.
- `Combat/`: Hurtboxes, Hitboxes, CombatColliders, Auto-Fitter.
- `Input/`: `IFighterInput`, `KeyboardFighterInput`, `AzureKinectInput`.
- `AI/`: `FighterAgent`, `AdaptiveAIManager`, `MatchTelemetryLogger`.
- `Environment/`: `ParallaxBackground`.
- `Audio/`: `SF3SoundManager`.
- `UI/`: `FighterHUD`, `CharacterSelectMenu`.
- `Database/`: `DatabaseManager`.
