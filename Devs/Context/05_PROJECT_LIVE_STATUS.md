# 📡 Estado Vivo y Changelog del Proyecto (Live Synchronization)
## Street Fighter III: 3rd Strike (Unity + Azure Kinect + IA Adaptativa)

Este documento es la **fuente única de verdad en tiempo real** del proyecto. Cada vez que un desarrollador (Marco, Sebas o Kevin) y su asistente de IA completen una tarea, creen un nuevo script, refactoricen o eliminen algo, **DEBEN actualizar este archivo**.

Al hacer `git pull origin main`, todos los asistentes de IA leerán este documento para sincronizarse automáticamente con los avances del equipo.

---

### 📊 Resumen de Estado Actual del Proyecto (Sprint 1 Activo)

* **Sprint Activo:** Sprint 1 (Sep 7 – Sep 20, 2026)
* **Rama Principal:** `main`
* **Luchadores en Desarrollo:**
  - 👑 **Ryu (`02_Ryu` - Marco):** 64 AnimationClips sincronizados en `Ryu_Animator.controller`, probador interactivo de teclado `FighterAnimationTester.cs` listo.
  - 🔥 **Ken (`01_Ken` - Sebas):** Listo para organizar en 7 categorías y generar clips a 14 FPS.
  - ⚡ **Chun-Li (`03_ChunLi` - Kevin):** Listo para organizar en 7 categorías y generar clips a 14 FPS.

---

### 📝 Registro de Componentes y Scripts Creados

| Script / Asset | Ruta | Creado / Modificado Por | Propósito |
| :--- | :--- | :---: | :--- |
| `SF3AnimationBatchCreator.cs` | `Scripts/Editor/` | Marco | Generación de clips a 14 FPS y Auto-Populate del Animator en 1 clic. |
| `SF3AutoSpriteImporter.cs` | `Scripts/Editor/` | Marco | Importador automático con Point Filter, Uncompressed y BottomCenter. |
| `FighterAnimationTester.cs` | `Scripts/Testing/` | Marco | Probador de estados, ataques con retorno automático a idle y locomoción. |
| `FighterHurtbox.cs` | `Scripts/Combat/` | Marco | Componente de recepción de daño (cabeza, torso, piernas). |
| `FighterHitbox.cs` | `Scripts/Combat/` | Marco | Componente de ataque activo. |
| `FighterCombatColliders.cs` | `Scripts/Combat/` | Marco | Coordinador de activación/desactivación de hitboxes y voces. |
| `ParallaxBackground.cs` | `Scripts/Environment/` | Sebas / Marco | Scroll con efecto de profundidad 2.5D para escenarios. |
| `SF3SoundManager.cs` | `Scripts/Audio/` | Marco / Sebas | Singleton para reproducir BGM, SFX y voces de luchadores. |
| `SpriteFrameAnimator.cs` | `Scripts/Loading/` | Marco | Reproductor ligero de secuencias de frames a 14 FPS CPS-3 sin GC. |
| `LoadingPlayerRyu.cs` | `Scripts/Loading/` | Marco | Controlador de Ryu en pantalla de carga (WASD/flechas, turbo, esquinas, colisión). |
| `LoadingChaserKen.cs` | `Scripts/Loading/` | Marco | IA de Ken para perseguir a Ryu desde la esquina opuesta superior. |
| `LoadingCollectible.cs` | `Scripts/Loading/` | Marco | Orbe Hadouken coleccionable estilo Budokai Tenkaichi que otorga turbo y puntos. |
| `LoadingItemSpawner.cs` | `Scripts/Loading/` | Marco | Generador de orbes coleccionables con object pooling seguro. |
| `LoadingMinigameRunner.cs` | `Scripts/Loading/` | Marco | Gestor de ciclo de juego, cronómetro de supervivencia, puntuación y reinicio. |
| `LoadingScreenController.cs` | `Scripts/Loading/` | Marco | Coordinador de carga asíncrona de escenas, barra de progreso y HUD arcade. |
| `SF3LoadingMinigameBuilder.cs` | `Scripts/Editor/` | Marco | Generador en 1 clic de Prefab y Escena con sprites, cámara, límites y UI. |
| `LoadingScreenMinigame.prefab` | `Prefabs/Loading/` | Marco | Prefab autónomo y reutilizable de la pantalla de carga con minijuego. |
| `LoadingScreen_Minigame.unity` | `Scenes/` | Marco | Escena interactiva lista para probar el minijuego de Ryu vs Ken. |

---

### ⚠️ Elementos Obsoletos / Deprecados (NO USAR)

* ❌ **Flechas con `Has Exit Time` en Mecanim:** Prohibido usar transiciones con flechas para ataques. Usar siempre `animator.Play(clipName, 0, 0f)`.
* ❌ **Recortar PNGs a mano (*Tight Crop*):** Prohibido alterar las dimensiones originales de los lienzos arcade.
* ❌ **Pivotes en el centro (*Center*):** Todos los sprites deben usar `BottomCenter` ($X=0.5, Y=0$) o Custom Pivot documentado.

---

### 🔄 Historial de Cambios Recientes (Changelog)

* **2026-09-20 (Minijuego Interactivo de Pantalla de Carga - Ryu vs Ken):**
  - Creada la rama `feature/loading-screen`.
  - Diseñado e implementado el minijuego estilo Dragon Ball Budokai Tenkaichi 3 para pantallas de carga.
  - Ryu empieza en la esquina inferior izquierda y escapa de Ken usando Flechas o WASD (`LoadingPlayerRyu.cs`).
  - Ken empieza en la esquina opuesta superior y persigue incansablemente a Ryu (`LoadingChaserKen.cs`).
  - Sistema de orbes Hadouken coleccionables con turbo de velocidad y puntos (`LoadingCollectible.cs`, `LoadingItemSpawner.cs`).
  - Motor de animación ligero a 14 FPS arcade CPS-3 sin consumo de Garbage Collector (`SpriteFrameAnimator.cs`).
  - Coordinador de carga asíncrona de escenas con barra de progreso, textos arcade retro y ciclo continuo (`LoadingScreenController.cs`, `LoadingMinigameRunner.cs`).
  - Generador automatizado de Editor para reconstruir Prefab y Escena con 1 clic (`SF3LoadingMinigameBuilder.cs`).
  - Generados los assets nativos de Unity: `LoadingScreenMinigame.prefab` y escena `LoadingScreen_Minigame.unity`.
* **2026-09-05:**
  - Creadas las 36 tareas atómicas de los Sprints 1 a 6 en `Devs/`.
  - Creado el sistema de sincronización y contexto para IAs en `Devs/Context/`.
  - Creada la Skill `.agent/skills/sf3-team-developer/SKILL.md`.
  - Creado el script de auto-configuración `Tools/setup_team_workspace.py`.
  - Sincronizados los 64 AnimationClips de Ryu en `Ryu_Animator.controller`.
