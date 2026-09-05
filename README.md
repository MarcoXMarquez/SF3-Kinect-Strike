# 🥋 Street Fighter III: 3rd Strike - Kinect Arcade Experience
## Proyecto en Unity 6 / URP 2D con Detección de Movimiento Corporal

Bienvenido al repositorio de **Street Fighter III: 3rd Strike** adaptado para **Unity**, diseñado para ser jugado con el cuerpo humano a través de sensores de movimiento (**Kinect v2** o **MediaPipe** por cámara web).

---

## 🎮 Características Principales

* **20 Luchadores Completos (Arcade CPS-3):**
  * Todos los personajes originales ripeados y verificados frame a frame: *Ryu, Ken, Chun-Li, Akuma/Gouki, Alex, Dudley, Yun, Yang, Ibuki, Elena, Oro, Necro, Hugo, Sean, Urien, Gill, Makoto, Q, Twelve y Remy*.
  * **Paletas Oficiales de Capcom:** El 100% de los sprites cuentan con la paleta original **LP (Light Punch / Jab)** extraída de las tablas de color `.pal` oficiales de CPS-3.
* **Jerarquía Modular de 7 Categorías con Nombres Descriptivos:**
  * Todas las acciones organizadas en carpetas estandarizadas:
    1. `01_Movement`: `idle_stance`, `walk_forward`, `walk_backward`, `dash_forward`, `jump_neutral`, `crouch_down`...
    2. `02_Normals`: `light_punch`, `heavy_kick`, `crouch_medium_kick`, `jump_forward_heavy_punch`...
    3. `03_Specials_Supers`: `special_hadouken`, `special_shoryuken`, `super_art_shinku_hadouken`...
    4. `04_Defense_Hit`: `parry_high`, `parry_low`, `hurt_light_1`, `knockdown_face_down`...
    5. `05_Throws`: `throw_forward`, `throw_backward`, `throw_air`...
    6. `06_Intros_Victories`: `intro_default`, `victory_pose_1`, `victory_pose_2`...
    7. `07_Secondary_Extras`: Poses y efectos complementarios.
* **Lienzo Unificado y Línea de Suelo Fija (Floor Baseline):**
  * Configurado con pivote `BottomCenter` (`Vector2(0.5f, 0.0f)`), garantizando que las parábolas de salto, alturas de Shoryuken y posturas se alineen al píxel sin necesidad de offsets manuales.
* **Efectos Visuales Completos (VFX):**
  * Proyectiles (*Hadouken, Denjin Hadouken, GouHadou, Aegis Reflector*).
  * Destello azul icónico de Parry (`05_Parry_Blue_Flash_Iconic`).
  * Chispas de impacto ligeras, medianas, fuertes y críticas (`Hit Sparks`).
  * Auras de energía, polvo de suelo y fondos de activación de Super Art.
* **Escenarios 2.5D Multicapa:**
  * Fondos con capas independientes (*Sky, Distant, Mid, Floor, Props*) listos para Parallax 2.5D.
* **Audio y Voces Originales:**
  * Pistas de música completas (BGM) en MP3.
  * Efectos de sonido (SFX) clasificados descriptivamente en WAV.
  * Voces arcade verificadas de cada personaje y del Announcer oficial.

---

## 📚 Documentación y Manuales del Proyecto

Dentro de la carpeta `Assets/StreetFighter3_ThirdStrike/` encontrarás la documentación completa para el desarrollo:

1. **[Guía de Configuración e Integración Inicial](Assets/StreetFighter3_ThirdStrike/README_UNITY_SETUP.md)**: Estructura del paquete, Pixel-Perfect y lienzo arcade.
2. **[Guía Definitiva de Montaje en Unity](Assets/StreetFighter3_ThirdStrike/GUIA_DEFINITIVA_UNITY_SF3.md)**: Tutorial general para dejar el proyecto funcionando de cero a jugable.
3. **[Recomendación de Paquetes y Herramientas](Assets/StreetFighter3_ThirdStrike/Docs/RECOMENDACION_PACKAGES_Y_HERRAMIENTAS_UNITY.md)**: Cinemachine, URP 2D, Animancer, Frame Data ScriptableObjects, Input Buffering y Shaders 2D.
4. **[Manuales Paso a Paso para Desarrolladores Junior](Assets/StreetFighter3_ThirdStrike/Docs/Manuales_Junior_Devs/00_INDICE_Y_ROADMAP_PROYECTO.md)**:
   * `01`: Configuración de Sprites Pixel-Perfect.
   * `02`: Creación de Animaciones Paso a Paso a 14 FPS.
   * `03`: Jerarquía y Arquitectura del Luchador (`Root`, `Visuals`, `Pushbox`, `Hurtbox`, `Hitbox`).
   * `04`: Animator Controller y Máquina de Estados Frame-Perfect.
   * `05`: Hitboxes, Hurtboxes y Animation Events.
   * `06`: Escenarios Parallax y Cámara 2.5D.
   * `07`: Efectos Visuales y Prefabs.
   * `08`: Audio, Voces y Sound Manager Singleton.
   * `09`: Arquitectura de Entrada y Preparación para Kinect (`IFighterInput`).
   * `10`: Checklist de Verificación Final.

---

## 🛠️ Herramientas de Editor Automatizadas

El proyecto incluye herramientas integradas en la barra superior de Unity (`SF3 Tools`):
* **Auto-Generate Animation Clips (`SF3AnimationBatchCreator.cs`):**
  Selecciona cualquier personaje o subcarpeta en la ventana Project y presiona `SF3 Tools > Auto-Generate Animation Clips from Selected Folder`. Generará automáticamente todos los `.anim` ordenados a **14 FPS** con `Loop Time` configurado.
* **Auto Sprite Importer (`SF3AutoSpriteImporter.cs`):**
  Configura automáticamente cualquier sprite nuevo importado con `Point Filter`, `Uncompressed` y `Pivot = BottomCenter`.

---

## ⚙️ Requisitos Técnicos

* **Motor:** Unity 2022.3 LTS / Unity 6 o superior.
* **Render Pipeline:** Universal Render Pipeline (URP 2D).
* **Control:** Teclado, Gamepad / Arcade Fightstick (Input System) o Sensor de Movimiento corporal (Kinect v2 / MediaPipe).
