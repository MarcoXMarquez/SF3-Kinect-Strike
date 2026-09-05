# Guía Definitiva de Montaje y Preparación en Unity
## Street Fighter III: 3rd Strike - De Cero a Jugable

Esta guía explica paso a paso cómo dejar el proyecto **100% configurado, animado y organizado en Unity** usando las herramientas automáticas que hemos incluido en el paquete, para que **no tengas que hacer trabajo repetitivo manual** y te dediques **exclusivamente a programar la lógica de juego**.

---

## 🚀 Resumen del Flujo de Trabajo (En 3 Pasos)

1. **Importar la carpeta a Unity:** Copia `Assets/StreetFighter3_ThirdStrike` dentro de tu carpeta `Assets/` de Unity.
2. **Sprites automáticos:** El script `Scripts/Editor/SF3AutoSpriteImporter.cs` incluido configurará **automáticamente** todos los sprites con Pixel-Perfect (Point filter, sin compresión y con Pivot en los pies).
3. **Generar todas las animaciones en 1 clic:** Usa la herramienta de menú `SF3 Tools > Auto-Generate Animation Clips` para crear todas las animaciones de cualquier luchador en 2 segundos.

> [!TIP]
> **¿Eres un programador Junior o buscas un tutorial ultra-detallado paso a paso ("haz clic aquí")?**
> Hemos creado una carpeta completa con **11 manuales independientes para desarrolladores** en:
> **[`Docs/Manuales_Junior_Devs/00_INDICE_Y_ROADMAP_PROYECTO.md`](./Docs/Manuales_Junior_Devs/00_INDICE_Y_ROADMAP_PROYECTO.md)**
> Contiene guías paso a paso de clics de ratón, capturas mentales, configuración de Kinect, máquina de estados y checklists.

---

## 1. Configuración de Sprites (Totalmente Automatizada)

Hemos creado el script **`Scripts/Editor/SF3AutoSpriteImporter.cs`** dentro del paquete. 
Cuando Unity detecta los sprites dentro de esta carpeta, **aplica automáticamente los siguientes ajustes esenciales**:

* **Texture Type:** `Sprite (2D and UI)`
* **Sprite Mode:** `Single`
* **Pixels Per Unit (PPU):** `100`
* **Filter Mode:** `Point (no filter)` *(Crítico: evita que el pixel art se vuelva borroso)*
* **Compression:** `None (Uncompressed)` *(Mantiene intactos los colores de Capcom)*
* **Pivot:** `Bottom (Center)` *(Garantiza que al cambiar entre estar de pie, agacharse o dar un puñetazo, los pies siempre toquen el suelo sin desalinearse)*.

> [!NOTE]
> **Lienzo Unificado y Espacio Vacío (Canvas Baseline CPS-3):**
> Varios sprites presentan espacio transparente amplio arriba o abajo. Esto es 100% fiel a la placa arcade: en un salto o *Shoryuken*, el frame 0 está en el suelo (espacio arriba) y el ápice del salto está en el aire (espacio abajo). Con el pivote en `BottomCenter`, Unity reproduce las trayectorias y alturas reales de CPS-3 sin requerir ajustes manuales de offset.

---

## 2. Cómo Crear las Animaciones Rápido (En Segundos)

No tienes que arrastrar 32,000 archivos a mano. Cada personaje está estructurado en 7 categorías limpias (`01_Movement`, `02_Normals`, `03_Specials_Supers`, `04_Defense_Hit`, `05_Throws`, `06_Intros_Victories`, `07_Secondary_Extras`) con nombres completos y descriptivos.

### Método A: Generador Automático por Menú (¡Recomendado!)
Hemos incluido el editor script **`Scripts/Editor/SF3AnimationBatchCreator.cs`**:

1. En la ventana **Project** de Unity, haz clic sobre la carpeta de cualquier personaje (por ejemplo, `Assets/StreetFighter3_ThirdStrike/Characters/02_Ryu`) o sobre una categoría concreta (ej. `01_Movement`).
2. En la barra superior de Unity, ve al menú:
   `SF3 Tools` ➔ `Auto-Generate Animation Clips from Selected Folder`.
3. **¡Listo!** El script escaneará recursivamente todas las carpetas con fotogramas (`idle_stance`, `walk_forward`, `light_punch`, `special_hadouken`, `parry_high`, etc.), ordenará los frames numéricamente (`0.png`, `1.png`...), generará los archivos `.anim` a **14 FPS** (tasa arcade nativa) y activará el bucle `Loop` automáticamente en las animaciones de reposo y caminata.

### Método B: Creación Rápida por Arrastre (Drag & Drop)
Para animaciones específicas o personalizadas:
1. Abre cualquier carpeta de acción (ej. `Characters/16_Chun_Li/03_Specials_Supers/special_kikoken/`).
2. Selecciona todos los frames (`0.png` al `N.png`).
3. Arrástralos a la ventana **Hierarchy** o **Scene**.
4. Unity te pedirá dónde guardar el `.anim` y creará automáticamente un GameObject con su `SpriteRenderer` y `Animator`.
5. En la ventana **Animation**, cambia el valor de **Samples** a `14` FPS.

---

## 3. Arquitectura del Personaje (GameObject Hierarchy)

Para un juego de peleas profesional en Unity, estructura tu GameObject de personaje de la siguiente manera:

```text
[GameObject] Fighter_Ryu (Tag: "Player", Layer: "Fighters")
   │
   ├── [Componentes en el Root]:
   │     ├── Rigidbody2D (Body Type: Kinematic o Dynamic con Constraints: Freeze Rotation Z)
   │     ├── BoxCollider2D (Is Trigger: False) -> Esta es la "Pushbox" (evita que se traspasen)
   │     ├── FighterController.cs (Tu script de control)
   │     └── SF3SoundManager.cs o AudioSource
   │
   ├── [Child 1] Visuals
   │     ├── SpriteRenderer (Sorting Layer: "Fighters", Order in Layer: 10)
   │     └── Animator (Asignar el Animator Controller del personaje)
   │
   ├── [Child 2] Hurtboxes (Layer: "Hurtbox")
   │     ├── BoxCollider2D (Is Trigger: True) -> Cubre cabeza, torso y piernas
   │     └── FighterHurtbox.cs (Incluido en Scripts/Combat/)
   │
   └── [Child 3] Hitboxes (Layer: "Hitbox")
         ├── BoxCollider2D (Is Trigger: True) -> Cubre el puño o pie en ataque
         └── FighterHitbox.cs (Incluido en Scripts/Combat/)
```

---

## 4. Configuración del Animator Controller y Máquina de Estados

Crea un **Animator Controller** (ej. `Ryu_Animator`) y configura la máquina de estados:

### Parámetros recomendados en el Animator:
* `Speed` (Float): Velocidad de movimiento horizontal.
* `isGrounded` (Bool): `true` si está en el suelo, `false` en el aire.
* `isCrouching` (Bool): `true` si mantiene presionado abajo.
* `AttackTrigger` (Trigger): Para disparar ataques normales.
* `SpecialHadouken` (Trigger): Para movimientos especiales.
* `Hit` (Trigger): Para animaciones de recibir daño.
* `isDead` (Bool): `true` al agotarse la vida.

### Conexión de Transiciones (Input Instantáneo Frame-Perfect):
1. Selecciona las flechas de transición entre estados (ej. de `Idle` a `Punch_Light`).
2. En el Inspector, **desmarca la casilla `Has Exit Time`**.
3. Pon **`Transition Duration (s)` en 0**.
4. *(Esto elimina cualquier retraso para que el personaje responda en el mismo frame que el jugador presiona el botón)*.

---

## 5. Eventos de Animación (Activar Golpes y Sonidos)

Para que los ataques hagan daño solo cuando el puño o pie está extendido:

1. Abre la ventana **Animation** en Unity y selecciona el clip del ataque (ej. `heavy_punch` - puñetazo fuerte).
2. Avanza la línea de tiempo hasta el fotograma donde el golpe impacta (ej. frame 4).
3. En la barra debajo de los números de fotograma, haz clic derecho y selecciona **Add Animation Event**.
4. En el Inspector, vincula la función `EnableHitbox()`.
5. En el frame donde el puño empieza a retroceder (ej. frame 7), agrega otro evento con `DisableHitbox()`.
6. En el frame del impacto también puedes agregar un evento para reproducir el sonido:
   `PlaySFX("Hit_Punch_Heavy")`.

---

## 6. Montaje de Escenarios y Parallax 2.5D

Las carpetas en `Stages/` (como `Japan_Ryu/` o `China_ChunLi/`) vienen divididas en capas para crear profundidad.

### A. Configurar Sorting Layers en Unity:
Ve a **Tags & Layers** ➔ **Sorting Layers** y crea el siguiente orden:
1. `Stage_Sky` (Cielo y nubes lejanas)
2. `Stage_Distant` (Montañas, edificios lejanos)
3. `Stage_Mid` (Templo, barandas, farolas)
4. `Stage_Floor` (Suelo donde pisan los luchadores)
5. `Fighters` (Luchadores en combate)
6. `Hit_Effects` (Chispas de golpe y proyectiles)
7. `Foreground_Props` (Elementos en primerísimo plano)

### B. Aplicar el Script de Parallax:
Hemos incluido **`Scripts/Environment/ParallaxBackground.cs`**:
1. Crea un GameObject vacío en la escena llamado `Stage_Parallax`.
2. Arrástrale el script `ParallaxBackground.cs`.
3. Arrastra las capas de sprites a la lista de capas:
   * **Capa 1 (Cielo):** `Parallax Factor X = 0.1` (se mueve muy poco).
   * **Capa 2 (Fondo lejano):** `Parallax Factor X = 0.4`.
   * **Capa 3 (Templo / Plano medio):** `Parallax Factor X = 0.7`.
   * **Capa 4 (Suelo):** `Parallax Factor X = 1.0` (se mueve a la par de la cámara).
4. Al mover la cámara con los luchadores, el escenario mostrará la profundidad 2.5D idéntica a Street Fighter III.

---

## 7. Efectos Visuales (Hit Sparks, Parry y Proyectiles)

Todos los efectos visuales están organizados en `Effects/`:

* **Destello azul de Parry (`05_Parry_Blue_Flash_Iconic`):**
  Crea un Prefab con un `SpriteRenderer` y `Animator`. Al bloquear un golpe con Parry exitoso, instáncialo en el punto de contacto entre los dos jugadores.
* **Chispas de golpe (`06_Hit_Spark_Electric_Yellow` y `20_Critical_Hit_Sparks_Red`):**
  Instancia el Prefab en la posición de la colisión entre la Hitbox y la Hurtbox.
* **Proyectiles (`Projectiles_Ryu_Hadouken`, etc.):**
  Crea un Prefab con `Rigidbody2D` Kinematic, un `CircleCollider2D` Trigger y dale velocidad hacia adelante (`velocity = transform.right * speed`).

---

## 8. Audio y Voces (SFX, BGM y Diálogos)

Hemos incluido el script **`Scripts/Audio/SF3SoundManager.cs`**:

1. Crea un GameObject en la escena llamado `SoundManager` y añade el componente `SF3SoundManager.cs`.
2. Asigna en el Inspector los clips que desees tener a mano:
   * `parrySound` ➔ Asignar `Audio/SFX/02_Defense_and_Parry/Parry_Success_Iconic_SF3.wav`.
   * `superFlashSound` ➔ Asignar `Audio/SFX/03_Super_Arts_and_EX/Super_Art_Activation_Flash.wav`.
3. Para la música de fondo, adjunta un `AudioSource` al GameObject, asigna cualquier pista de `Audio/BGM/` (ej. `08_Kobu_Ryu_Stage.mp3`) y activa **Loop = True**.
4. En cualquier script de combate puedes reproducir efectos con una sola línea de código:
   ```csharp
   SF3SoundManager.Instance.PlayParry();
   SF3SoundManager.Instance.PlaySFX(heavyHitClip);
   SF3SoundManager.Instance.PlayVoice(hadoukenVoiceClip);
   ```

---

¡Con esta configuración, todos tus sprites, animaciones, escenarios y sonidos estarán listos y funcionando en Unity en cuestión de minutos, permitiéndote concentrarte al 100% en la jugabilidad y la programación!
