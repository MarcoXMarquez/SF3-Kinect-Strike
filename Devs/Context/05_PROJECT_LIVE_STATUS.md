# 📡 Estado Vivo y Changelog del Proyecto (Live Synchronization)
## KINET STRIKE (Unity + Azure Kinect + IA Adaptativa)

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
| `SF3JapanStageBuilder.cs` | `Scripts/Editor/` | Sebas | Generador del escenario Suzaku Castle (Japón) con Parallax y suelo físico Y=0. |
| `SF3ChinaStageBuilder.cs` | `Scripts/Editor/` | Sebas | Generador del escenario Crowded Street (China) con Parallax, límites de arena y props animados. |
| `AnimatedSpriteProp.cs` | `Scripts/Environment/` | Sebas | Controlador de props y espectadores vivos a 14 FPS para escenarios CPS-3. |
| `Stage_China.prefab` | `Prefabs/` | Sebas | Prefab oficial reutilizable del escenario de China con colisionadores y capas 2D. |
| `Sandbox_China.unity` | `Scenes/` | Sebas | Escena de combate independiente para duelos en el escenario de China con BGM oficial. |
| `IFighterInput.cs` | `Scripts/Input/` | Kevin | Interfaz desacoplada para desacoplar el origen de entrada (Teclado/Kinect/IA) del luchador. |
| `KeyboardFighterInput.cs` | `Scripts/Input/` | Kevin | Adaptador de teclado para locomoción, ataques normales y emulación de gestos. |
| `AzureKinectInput.cs` | `Scripts/Input/` | Kevin | Adaptador somatosensorial de Azure Kinect con cálculo cinemático de articulaciones 3D. |
| `AzureKinectBodyTracker.cs` | `Scripts/Input/` | Kevin | Conector del hardware Azure Kinect y Body Tracking SDK para Unity. |
| `KinectPoseMatcher.cs` | `Scripts/Input/` | Kevin | Comparador de poses calibradas en tiempo real desde JSON con cálculo de similitud (%). |
| `sf3_kinect_sagittal_visualizer.py` | `Tools/` | Kevin | Visualizador OpenCV con grabación dinámica de clips (35 frames), mini-video player en bucle, gestión de 10 sujetos y modo mockup (--mock). |
| `gesture_feature_extractor.py` | `Tools/` | Kevin | Extractor matemático de cinemática 3D: normalización local, ángulos relativos, velocidades instantáneas y 26 métricas agregadas por clip. |
| `train_gesture_classifier.py` | `Tools/` | Kevin | Entrenador de Random Forest con GroupKFold por sujeto, exportador ONNX a Unity Models y generador sintético. |
| `gesture_classifier.onnx` | `Assets/.../Models/` & `Tools/` | Kevin | Modelo tabular supervisado optimizado para inferencia en Unity Sentis / Python. |
| `clean_dataset_outliers.py` | `Tools/` | Kevin | Limpiador de outliers e interpolador de discontinuidades ToF con filtro 1€ adaptativo. |
| `test_live_gesture_classifier.py` | `Tools/` | Kevin | Testeador terminal interactivo de inferencia y auditor de sesgos/probabilidades por clase. |
| `test_live_kinect_classifier.py` | `Tools/` | Kevin | Detector somatosensorial en vivo con Azure Kinect físico y panel visual HUD de sesgos (7 clases). |
| `record_transition_graph.py` | `Tools/` | Kevin | Estudio de transiciones y combos con perspectiva DUAL (Frontal + Sagital), modo práctica libre, telemetría cinemática, creación ilimitada de nuevos sujetos en la UI y matriz 7x7 (42 aristas). |
| `DuelFighter.cs` | `Scripts/Combat/` | Sebas | Controlador de combate 2D con Rigidbody2D, orientación, animaciones, bloqueo frontal y hurtboxes (cabeza, torso, piernas). |
| `DuelRoster.cs` | `Scripts/Combat/` | Sebas | ScriptableObject que almacena 21 secuencias de sprites por personaje (230 Ken, 256 Ryu). |
| `JapanDuel.cs` | `Scripts/Combat/` | Sebas | Gestor del duelo local Ken vs. Ryu en Suzaku Castle (rondas, HUD de vida, KO y revancha). |
| `JapanDuelValidation.cs` | `Scripts/Editor/` | Sebas | Validador automatizado en Play Mode del duelo (`SF3 Tools > Validate Local Duel`). |
| `SF3JapanStageBuilder.cs` | `Scripts/Editor/` | Sebas | Constructor y ensamblador del escenario de Japón (Suzaku Castle) con parallax y colliders. |
| `StageParallaxTester.cs` | `Scripts/Testing/` | Sebas | Script de prueba de cámara para validar el desplazamiento de capas de parallax. |
| `SF3ChromaKeySprite.shader` | `Shaders/` | Sebas | Shader de ChromaKey para eliminación de fondos en sprites del escenario. |
| `ISteeringAgent.cs` | `Scripts/AI/Steering/` | Kevin | Contrato cinemático para entidades con aceleración de dirección (Reynolds). |
| `ISteeringBehavior.cs` | `Scripts/AI/Steering/` | Kevin | Contrato desacoplado para algoritmos de cálculo de fuerzas vectoriales de dirección. |
| `SeekBehavior.cs` | `Scripts/AI/Steering/` | Kevin | Algoritmo clásico de Persecución (Seeking) de Craig Reynolds con frenado suave de llegada. |
| `WanderBehavior.cs` | `Scripts/AI/Steering/` | Kevin | Algoritmo clásico de Merodeo (Wandering) de Craig Reynolds con círculo virtual y variación angular. |
| `SteeringUIEntity.cs` | `Scripts/AI/Steering/` | Kevin | MonoBehaviour cinemático para mover entidades en Canvas UI con rebote elástico perimetral. |
| `MainMenuController.cs` | `Scripts/UI/` | Kevin | Menú principal interactivo 100% navegable con teclado, submenú Versus (Bot / 2P) y SFX arcade. |
| `LoadingScreenController.cs` | `Scripts/UI/` | Kevin | Controlador de pantalla de carga asíncrona, barra de progreso y orquestador del minijuego. |
| `LoadingMinigameManager.cs` | `Scripts/UI/` | Kevin | Administrador del minijuego estilo DBZ Tenkaichi 3 que coordina orbes Wandering y buscador Seeking. |
| `MiniFighterController.cs` | `Scripts/UI/` | Kevin | Avatar 2D jugable en la pantalla de carga (movimiento horizontal, salto, golpe y animación de Ryu). |
| `FightHUD.cs` | `Scripts/UI/` | Marco / Sebas | HUD de combate arcade (barras de vida P1/P2 con daño retardado y contador central de 99s). |
| `TenkaichiDialogueManager.cs` | `Scripts/UI/` | Marco / Kevin | Sistema de cinemáticas y diálogos estilo DBZ Budokai Tenkaichi 3 con lore original de KINET STRIKE y selector de episodios. |
| `Stage_Tomb.prefab` | `Prefabs/` | Sebas / Marco | Prefab oficial del escenario Tumba Olímpica (Grecia) con columnas de mármol y BGM de Urien. |
| `Fighter_Urien.prefab` | `Prefabs/` | Marco | Prefab de Urien con Animator CPS-3 a 14 FPS, Aegis Reflector, Chariot Rush y Super Art. |
| `Sandbox_Tomb.unity` | `Scenes/` | Sebas / Marco | Escena de combate versus en la Tumba Olímpica de Urien con HUD y música oficial. |
| `StoryMode_Scene.unity` | `Scenes/` | Marco / Kevin | Escena del Modo Historia con cinemáticas y diálogos estilo DBZ Budokai Tenkaichi 3. |
| `SF3MainMenuBuilder.cs` | `Scripts/Editor/` | Kevin | Generador automatizado de la escena `MainMenu_Scene.unity` y sincronizador de `EditorBuildSettings`. |
| `SF3SoundManager.cs` | `Scripts/Audio/` | Marco / Sebas | Singleton para reproducir BGM, SFX y voces de luchadores. |
| `StealthCollectible.cs` | `Scripts/AI/` | Equipo | Orbes coleccionables con efectos luminosos para el minijuego de waypoints. |
| `StealthGoal.cs` | `Scripts/AI/` | Equipo | Portal Rinnegan dimensional de extracción con shader custom y detección de victoria. |
| `StealthMinigameManager.cs` | `Scripts/AI/` | Equipo | Gestor del minijuego de sigilo por waypoints, contador de orbes y HUD retro. |
| `StealthPlayerController.cs` | `Scripts/AI/` | Equipo | Controlador de Ryu con movimiento suave, colisiones sólidas y físicas 2D en minijuego de sigilo. |
| `WaypointCircuit.cs` | `Scripts/AI/` | Equipo | Circuito de waypoints para patrullaje con gizmos y bucles de nodos. |
| `WaypointPatrolNPC.cs` | `Scripts/AI/` | Equipo | Centinelas y patrulleros que recorren waypoints con detección perimétrica de Ryu. |
| `WaypointMinigameBuilder.cs` | `Scripts/Editor/` | Equipo | Generador y ensamblador de la escena minijuegowaypoint con pilares, orbes y portal. |
| `RinneganPortal2D.shader` | `Shaders/` | Equipo | Shader procedural de vórtice dimensional Rinnegan para el portal del minijuego. |
| `RockStone2D.shader` | `Shaders/` | Equipo | Shader procedural para pilares de roca del minijuego. |
| `minijuegowaypoint.unity` | `Scenes/` | Equipo | Escena jugable del minijuego de sigilo y waypoints. |

---

### ⚠️ Elementos Obsoletos / Deprecados (NO USAR)

* ❌ **Flechas con `Has Exit Time` en Mecanim:** Prohibido usar transiciones con flechas para ataques. Usar siempre `animator.Play(clipName, 0, 0f)`.
* ❌ **Recortar PNGs a mano (*Tight Crop*):** Prohibido alterar las dimensiones originales de los lienzos arcade.
* ❌ **Pivotes en el centro (*Center*):** Todos los sprites deben usar `BottomCenter` ($X=0.5, Y=0$) o Custom Pivot documentado.

---

### 🔄 Historial de Cambios Recientes (Changelog)

* **2026-10-20 (Integración de Minijuegos y Modo Historia Ryu vs Ken):**
  - **Fusión de `minijuego-waypoint`:** Integrado el minijuego de sigilo por waypoints con Ryu, centinelas patrulleros, orbes de energía y portal Rinnegan.
  - **Fusión de `minijuego/lanzamiento-de-proyectil`:** Integrado el minijuego Neon Siege arcade con balística parabólica de proyectiles.
  - **Menú Principal Unificado:** Añadido submenú de Minijuegos en `MainMenuController.cs` para acceder y jugar directamente a ambos minijuegos.
  - **Modo Historia Ryu vs Ken:** Cinemática introductoria con pantalla negra, texto de máquina de escribir y lore del conflicto Ryu vs Ken previo al combate en Suzaku Castle.

* **2026-10-13 (Red de Transiciones Dirigidas 7x7 y Estudio de Grabación Cinemática):**
  - **Estudio de Transiciones (`Tools/record_transition_graph.py`):** Creada herramienta especializada con interfaz gráfica OpenCV y renderizado sagital/frontal retro CPS-3 para capturar secuencias continuas entre movimientos sin retorno intermedio a reposo.
  - **Matriz de Continuidad 7x7 (42 Aristas Dirigidas):** Modeladas todas las posibles transiciones entre las 7 acciones maestras (`idle`, `punch_right`, `punch_left`, `kick_right`, `kick_left`, `crouch`, `block`), con selector interactivo y contador de repeticiones en tiempo real.
  - **Simulador Cinemático Procedural (`--mock`):** Generador de esqueleto continuo a 30 FPS que emula la curva bimodal de intercambio de energía cinética ($A_{\text{pico}} \rightarrow T_{A \rightarrow B} \rightarrow B_{\text{pico}}$) para pruebas inmediatas sin hardware físico.
  - **Generador de Dataset Sintético (`--generate-synthetic`):** Función de generación en batch automatizada con almacenamiento estructurado en `Tools/dataset_transitions/` para alimentar los modelos predictivos de combos.
  - **Artefacto de Arquitectura:** Generado plan exhaustivo con los 7 grafos Mermaid individuales y formalización matemática en `PLAN_ENTRENADOR_TRANSICIONES_KINECT.md`.

* **2026-09-22 (Menú de Inicio Retro y Pantalla de Carga con Minijuego Cinemático DBZ Tenkaichi 3):**
  - **Menú Principal Arcade (`MainMenuController.cs`):** Navegación completa por teclado (`W`/`S`, `Flechas`, `Enter`/`Espacio`, `ESC`/`Backspace`), indicador animado con cursor retro (`>>`), escalado palpitante de opciones activas y efectos de sonido arcade (`Menu_Cursor_Select.wav`, `Menu_Confirm_Start.wav`).
  - **Ventana Modal "Próximamente" para Modo Historia:** Al seleccionar Modo Historia, se abre una ventana modal explicativa que indica que el modo requerirá el sensor Azure Kinect DK e IA somatosensorial en el Sprint 2, descartable con Enter/Espacio/Esc sin iniciar combate accidental.
  - **Estructura de Menú y Submenús:** Opciones principales `Modo Historia`, `Versus` (con submenú interactivo `Versus Bot (1P vs CPU)` y `Versus 2 Players (Local)` conectado al duelo Suzaku Castle) y botón `Salir`.
  - **Pantalla de Carga Ampliada y Minijuego DBZ Tenkaichi 3 (`LoadingScreenController.cs`, `LoadingMinigameManager.cs`):** Área de minijuego expandida a 1460x580 px con límites horizontales de 670 px, barra de progreso CPS-3 animada (0% a 100%), avatar 2D jugable (`MiniFighterController.cs`) con físicas de salto aumentadas (jumpForce = 620), desplazamiento ágil y puñetazos con sprites arcade de Ryu.
  - **Música de Pelea y Menú de Pausa en Duelo (`JapanDuel.cs`):** Incorporada música de fondo BGM para el combate de Suzaku Castle (`08_Kobu_Ryu_Stage.mp3` en `Resources/Audio/BGM_Japan.mp3`) con bucle activo. Sistema de pausa interactivo con tecla `ESC` o `P` que congela la física, reproduce SFX y permite elegir con teclado o ratón entre `Reanudar`, `Reiniciar Ronda` o `Volver al Menú Principal` (`MainMenu_Scene`).

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
