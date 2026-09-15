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
| `IFighterInput.cs` | `Scripts/Input/` | Kevin | Interfaz desacoplada para desacoplar el origen de entrada (Teclado/Kinect/IA) del luchador. |
| `KeyboardFighterInput.cs` | `Scripts/Input/` | Kevin | Adaptador de teclado para locomoción, ataques normales y emulación de gestos. |
| `AzureKinectInput.cs` | `Scripts/Input/` | Kevin | Adaptador somatosensorial de Azure Kinect con cálculo cinemático de articulaciones 3D. |
| `AzureKinectBodyTracker.cs` | `Scripts/Input/` | Kevin | Conector del hardware Azure Kinect y Body Tracking SDK para Unity. |
| `KinectPoseMatcher.cs` | `Scripts/Input/` | Kevin | Comparador de poses calibradas en tiempo real desde JSON con cálculo de similitud (%). |
| `Test_AzureKinect_Body.unity` | `Scenes/` | Kevin | Escena de pruebas para visualizar y calibrar el esqueleto 3D en el laboratorio. |
| `sf3_kinect_sagittal_visualizer.py` | `Tools/` | Kevin | Visualizador OpenCV de esqueleto 3D (frontal y perfil sagital) con telemetría. |

---

### ⚠️ Elementos Obsoletos / Deprecados (NO USAR)

* ❌ **Flechas con `Has Exit Time` en Mecanim:** Prohibido usar transiciones con flechas para ataques. Usar siempre `animator.Play(clipName, 0, 0f)`.
* ❌ **Recortar PNGs a mano (*Tight Crop*):** Prohibido alterar las dimensiones originales de los lienzos arcade.
* ❌ **Pivotes en el centro (*Center*):** Todos los sprites deben usar `BottomCenter` ($X=0.5, Y=0$) o Custom Pivot documentado.

---

### 🔄 Historial de Cambios Recientes (Changelog)

* **2026-09-08 (Martes de Laboratorio - Sprint 1):**
  - Implementada la arquitectura desacoplada de entrada: `IFighterInput.cs`.
  - Creado el adaptador de teclado `KeyboardFighterInput.cs` con controles de movimiento, ataques y emulación de gestos.
  - Creado el adaptador somatosensorial `AzureKinectInput.cs` con cálculo cinemático de articulaciones 3D.
  - Creado el hardware bridge `AzureKinectBodyTracker.cs` con resolución automática de DLLs nativas y ONNX weights.
  - Creado el estudio de calibración interactivo `Tools/sf3_kinect_sagittal_visualizer.py` con esqueleto simplificado (13 articulaciones clave), diferenciación cromática anatómica (**Rojo = Lado Derecho, Azul = Lado Izquierdo, Cian = Tronco**), selector de posturas base (Perfil Izq/Der/Frontal), telemetría de patadas en profundidad (Z), catálogo completo de **51 animaciones de combate de Ryu** en 6 categorías, generación automática de snapshots de auditoría en `Tools/captured_pose_reviews/` y panel lateral flotante de review para inspeccionar la pose capturada en tiempo real.
  - Creado `KinectPoseMatcher.cs` con parser de poses línea a línea, evaluador de similitud biométrica (%) en tiempo real y vinculación directa al Animator de Ryu (`FighterAnimationTester` / `Ryu_Animator.controller`), reconociendo automáticamente por hash los 51 estados de animación.
  - Creada la escena de diagnóstico `Assets/StreetFighter3_ThirdStrike/Scenes/Test_AzureKinect_Body.unity`.
  - Rama activa: `feature/sp1-kevin-input-kinect` (#6).

* **2026-09-05:**
  - Creadas las 36 tareas atómicas de los Sprints 1 a 6 en `Devs/`.
  - Creado el sistema de sincronización y contexto para IAs en `Devs/Context/`.
  - Creada la Skill `.agent/skills/sf3-team-developer/SKILL.md`.
  - Creado el script de auto-configuración `Tools/setup_team_workspace.py`.
  - Sincronizados los 64 AnimationClips de Ryu en `Ryu_Animator.controller`.
