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
| `sf3_kinect_sagittal_visualizer.py` | `Tools/` | Kevin | Visualizador OpenCV con grabación dinámica de clips (35 frames), mini-video player en bucle, gestión de 10 sujetos y modo mockup (--mock). |
| `gesture_feature_extractor.py` | `Tools/` | Kevin | Extractor matemático de cinemática 3D: normalización local, ángulos relativos, velocidades instantáneas y 26 métricas agregadas por clip. |
| `train_gesture_classifier.py` | `Tools/` | Kevin | Entrenador de Random Forest con GroupKFold por sujeto, exportador ONNX a Unity Models y generador sintético. |
| `gesture_classifier.onnx` | `Assets/.../Models/` & `Tools/` | Kevin | Modelo tabular supervisado optimizado para inferencia en Unity Sentis / Python. |
| `clean_dataset_outliers.py` | `Tools/` | Kevin | Limpiador de outliers e interpolador de discontinuidades ToF con filtro 1€ adaptativo. |
| `test_live_gesture_classifier.py` | `Tools/` | Kevin | Testeador terminal interactivo de inferencia y auditor de sesgos/probabilidades por clase. |
| `test_live_kinect_classifier.py` | `Tools/` | Kevin | Detector somatosensorial en vivo con Azure Kinect físico y panel visual HUD de sesgos (7 clases). |

---

### ⚠️ Elementos Obsoletos / Deprecados (NO USAR)

* ❌ **Flechas con `Has Exit Time` en Mecanim:** Prohibido usar transiciones con flechas para ataques. Usar siempre `animator.Play(clipName, 0, 0f)`.
* ❌ **Recortar PNGs a mano (*Tight Crop*):** Prohibido alterar las dimensiones originales de los lienzos arcade.
* ❌ **Pivotes en el centro (*Center*):** Todos los sprites deben usar `BottomCenter` ($X=0.5, Y=0$) o Custom Pivot documentado.

---

### 🔄 Historial de Cambios Recientes (Changelog)

* **2026-09-17 (Set 2 Bloqueo Dinámico, Limpieza Biomecánica, Retorno Inmediato a Idle < 200ms y Re-entrenamiento ML 98 Clips):**
  - **Captura e Integración de Set 2 (Sujetos 11 a 14):** 28 nuevos clips CSV incorporando la nueva dinámica de combate: Bloqueo dinámico (`block`: brazos suben desde guardia a bloquear el pecho/cara y vuelven a bajar) y Guardia estática (`idle` estable con velocidad < 0.1 m/s). Total dataset: **98 clips**.
  - **Limpieza de Outliers (`Tools/clean_dataset_outliers.py`):** Procesados los 98 clips en `Tools/dataset_cleaned/`. Se eliminaron 313 saltos espurios (> 30 cm), logrando 0 discontinuidades y reduciendo el salto máximo promedio de 0.348m a 0.074m.
  - **Re-entrenamiento Random Forest Supervisado (`Tools/train_gesture_classifier.py`):** Entrenado sobre los 98 clips limpios (14 sujetos). Validación cruzada `GroupKFold` subió de 91.43% a **95.24% ± 3.01%** sobre sujetos no vistos. La característica `max_elev_wrist_l` ascendió al Top 2 de importancia (7.00%) para captar la elevación bilateral de brazos del bloqueo.
  - **Exportación ONNX y Joblib Sincronizada:** Actualizados `Tools/gesture_classifier.joblib`, `Tools/gesture_classifier.onnx` y `Assets/StreetFighter3_ThirdStrike/Models/gesture_classifier.onnx`.
  - **Retorno Inmediato a Guardia / Idle (< 200 ms):** Solucionada la latencia de 2 segundos de retorno a guardia causada por la persistencia de picos de velocidad en la ventana rodante de 35 frames. Implementado detector de desaceleración y reposo instantáneo (últimos 6 frames / ~200 ms, $v < 0.42\text{ m/s}$) tanto en `Tools/test_live_kinect_classifier.py` como en `Tools/sf3_kinect_sagittal_visualizer.py`. Si las extremidades se detienen tras un golpe, el sistema transiciona instantáneamente a `idle` (o `crouch`/`block` sostenido si corresponde).
  - **Mejora del Detector en Vivo (`Tools/test_live_kinect_classifier.py`):** Integrada persistencia visual de impacto (2.5s), telemetría de guardia activa en reposo y registro de eventos y sesgos por consola en tiempo real.

* **2026-09-15 (Pipeline ML Cinemático Temporal - 10 Sujetos, UX Studio & 44 Features):**
  - **Filtro Adaptativo One-Euro ($1€$):** Implementado en `Tools/gesture_feature_extractor.py` sobre el eje temporal 3D, mitigando el jitter de profundidad ToF en reposo sin añadir latencia a golpes explosivos.
  - **Normalización Antropométrica y Extensión Biomecánica:** Incorporada longitud de torso ($L_{\text{torso}}$) y ratios de extensión articular ($\text{Ext}_{\text{brazo}}, \text{Ext}_{\text{pierna}}$) invariantes a la estatura (44 features cinemáticas totales).
  - **Cuenta Regresiva de 3 Segundos (Visual + Audio):** Integrada cuenta 3.. 2.. 1.. con tonos audibles (`winsound.Beep`) y overlay en `Tools/sf3_kinect_sagittal_visualizer.py` para sincronizar al voluntario y centrar los golpes en el clip.
  - **Auditoría Heurística de Calidad (Quality Gatekeeper):** Evaluación instantánea de velocidad pico, centrado temporal de impacto y distancia operativa ($Z$), asistiendo al operador en la revisión manual.
  - **Sistema Cuádruple de Verificación y Auditoría Anti-Olvido ("Memoria de Pollo"):**
    1. **Badges Permanentes por Pose:** Píldoras visuales en cada una de las 8 acciones (`[OK] 20/20 OK`, `[SAVE] X/20`, `[-] VACIO 0/20`).
    2. **Resaltado de Guardado Reciente:** Borde verde brillante y tag `>> RECIEN GUARDADO (Xs)` en el botón de la acción recién guardada.
    3. **Matriz Rápida de los 10 Sujetos:** Vista de pájaro con 10 botones interactivos (`S01` a `S10`) con conteo de clips en tiempo real y salto inmediato con un clic.
    4. **Comprobante Físico Permanente en Disco:** Tarjeta fija con timestamp, nombre de archivo CSV y tamaño en KB verificado en disco tanto en el centro inferior como en el panel derecho de video.
  - **Calibración Biomecánica A-Pose (Tecla `[C]`):** Captura de 2 segundos para medir y registrar longitudes de brazos, piernas, torso y envergadura en `Tools/dataset_raw/subject_profiles.json`.
  - **Re-entrenamiento ML & ONNX:** Modelo Random Forest re-entrenado con 44 features y GroupKFold (99.98% de exactitud), exportado a `Tools/gesture_classifier.onnx` y `Assets/StreetFighter3_ThirdStrike/Models/gesture_classifier.onnx`.
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
