# 🛠️ Guía de Recomendación de Paquetes y Herramientas para Unity
## Desarrollo de Street Fighter III: 3rd Strike en Unity 6 / URP 2D

Esta guía recopila las **herramientas, paquetes oficiales, extensiones de la comunidad y patrones arquitectónicos más recomendados** para llevar el desarrollo de *Street Fighter III: 3rd Strike* en Unity al máximo nivel de fluidez, fidelidad arcade y comodidad técnica.

---

## 📋 Resumen Rápido: Qué Instalar Primero

| Herramienta / Paquete | Origen | Prioridad | Propósito Principal |
| :--- | :--- | :--- | :--- |
| **Cinemachine** | Unity Package Manager | ⭐⭐⭐⭐⭐ **Esencial** | Cámara dinámica 2D para mantener a ambos luchadores en pantalla y temblores de impacto. |
| **URP 2D Pixel Perfect Camera** | Incluido en URP (Ya instalado) | ⭐⭐⭐⭐⭐ **Esencial** | Renderizado nítido de sprites CPS-3 sin distorsión de píxeles en cualquier resolución. |
| **Input System** | Unity Package Manager (Ya instalado) | ⭐⭐⭐⭐⭐ **Esencial** | Soporte de Gamepads, Arcade Fightsticks, Teclado P1/P2 y mapeo de acciones. |
| **Frame Debugger & Frame Stepper** | Script C# personalizado | ⭐⭐⭐⭐⭐ **Esencial** | Avanzar fotograma a fotograma (`F`) para calibrar Parries e impactos al milisegundo. |
| **Animancer Lite / Pro** | Unity Asset Store | ⭐⭐⭐⭐ **Muy Recomendado** | Control de animaciones directo por código C# sin enredarse en telarañas de Animator. |
| **TextMeshPro** | Unity Package Manager | ⭐⭐⭐⭐ **Muy Recomendado** | UI de combate, números de combo ("3 HITS!"), barra de vida y textos arcade. |
| **Rewired** | Unity Asset Store | ⭐⭐⭐⭐ **Recomendado** | Motor de entrada profesional para torneos, cero recolección de basura y remapeo. |
| **MediaPipe Unity Plugin** | GitHub / OpenUPM | ⭐⭐⭐⭐ **Recomendado (Kinect)** | Seguimiento corporal con IA por cámara web estándar si no dispones del sensor físico. |
| **AudioMixer Ducking** | Integrado en Unity | ⭐⭐⭐⭐ **Recomendado** | Atenuación de música cuando el Speaker grita *"SUPER ART!"* o *"K.O.!"*. |

---

## 1. Cámara y Encuadre Dinámico de Lucha (Cinemachine)

En un juego de pelea 2D, la cámara nunca es fija: debe **encuadrar automáticamente a los dos luchadores**, acercarse cuando están pegados y alejarse cuando retroceden, respetando los límites de la pantalla (*Corners* / Esquinas del escenario).

### 📦 Paquete: `Cinemachine` (`com.unity.cinemachine`)
* **Instalación:** `Window` ➔ `Package Manager` ➔ `Unity Registry` ➔ Busca **Cinemachine** ➔ Clic en **Install**.

### ⚙️ Configuración Paso a Paso:
1. **Target Group 2D:**
   * Crea un GameObject vacío: `CinemachineTargetGroup`.
   * Añade el componente `CinemachineTargetGroup`.
   * Agrega a la lista tus dos GameObjects: `Fighter_P1` (Weight: 1, Radius: 1) y `Fighter_P2` (Weight: 1, Radius: 1).
2. **Virtual Camera 2D:**
   * En la Virtual Camera, asigna el `CinemachineTargetGroup` en el campo **Follow** y **LookAt**.
   * En **Body**, selecciona **Framing Transposer**:
     * **Camera Distance:** `10` (o tamaño ortográfico dinámico).
     * **Minimum Orthographic Size:** `3.5` (cuando ambos luchadores están cuerpo a cuerpo).
     * **Maximum Orthographic Size:** `4.8` (cuando están en esquinas opuestas).
3. **Límites de Escenario (Confiner 2D):**
   * Añade una extensión `CinemachineConfiner2D` a la cámara virtual.
   * Crea un `CompositeCollider2D` o `PolygonCollider2D` que encierre el escenario (el templo de Ryu, las calles de Chun-Li, etc.).
   * Esto garantiza que los luchadores nunca salgan del borde visible y la cámara no muestre zonas vacías fuera del fondo.
4. **Impact Shake (Cinemachine Impulse):**
   * Añade el componente `CinemachineImpulseSource` al personaje.
   * Cuando conecte un golpe fuerte (`heavy_punch`, `super_art_shinku_hadouken`), dispara `impulseSource.GenerateImpulse()`.
   * Dará el temblor de pantalla idéntico al arcade CPS-3.

---

## 2. Renderizado Pixel-Perfect en URP

Dado que tu proyecto ya tiene instalado **Universal Render Pipeline (URP 17.3)**, dispones del renderizador 2D nativo más moderno de Unity.

### 📐 Configuración del Pixel Perfect Camera:
1. Selecciona tu **Main Camera**.
2. Añade el componente **`Pixel Perfect Camera`**.
3. Configura los valores según la proporción CPS-3:
   * **Assets Pixels Per Unit (PPU):** `100` (coincidiendo con los sprites importados).
   * **Reference Resolution:** `384 x 224` (la resolución interna nativa de CPS-3) o `1920 x 1080` si usas escala HD de escenario.
   * **Upscale RT:** Activado (Checked).
   * **Pixel Snapping:** Activado. Evita que los sprites tiemblen o vibren al moverse a velocidades fraccionarias.

### 💡 Iluminación 2D para Efectos Especiales:
Aprovecha que URP 2D incluye iluminación en tiempo real sobre sprites:
* **Luz de Destello de Super Art:** Un `Light2D` (tipo *Point/Freeform*) de color blanco puro que se enciende durante 3 fotogramas al activar un Super.
* **Luz Azul de Parry:** Un `Light2D` cian centrado en el punto de contacto al ejecutar un Parry exitoso.

---

## 3. Manejo de Animaciones: ¿Animator o Animancer?

### El Dilema del Animator en Fighting Games:
El `Animator Controller` tradicional de Unity con nodos y flechas funciona bien para 5 o 10 animaciones. Sin embargo, cada luchador de *Street Fighter III* tiene **más de 65 acciones distintas** (golpes de pie, agachados, saltando, 3 tipos de parry, especiales débiles/medios/fuertes, caídas, etc.). Conectar flechas entre 65 estados genera una "telaraña de espagueti" propensa a errores y transiciones fantasma.

### 🚀 Solución A: Animancer (Asset Store - Recomendado para juegos de lucha)
* **Qué es:** Una librería que te permite reproducir cualquier `AnimationClip` directamente desde C#:
  ```csharp
  [SerializeField] private AnimationClip lightPunchClip;
  
  public void PlayLightPunch()
  {
      animancer.Play(lightPunchClip, 0f, FadeMode.FixedSpeed);
  }
  ```
* **Ventajas:**
  * Cero tiempo de transición inmediato.
  * No requiere crear ni mantener archivos `.controller` con cientos de flechas.
  * Permite consultar directamente el fotograma actual y tiempo normalizado con precisión absoluta.
  * Existe una versión **Animancer Lite** completamente gratuita en la Unity Asset Store.

### 🏛️ Solución B: StateMachineBehaviour (Si prefieres Animator nativo)
Si prefieres usar el Animator nativo de Unity:
* Agrupa las acciones en **Sub-State Machines** dentro del Animator Controller:
  * Sub-State: `Movement` (`idle_stance`, `walk_forward`, `jump_neutral`...).
  * Sub-State: `Normals` (`light_punch`, `heavy_kick`...).
  * Sub-State: `Specials` (`special_hadouken`, `special_shoryuken`...).
  * Sub-State: `Reactions` (`hurt_light_1`, `knockdown_face_down`...).
* Crea clases que hereden de `StateMachineBehaviour` para limpiar variables y resetear colisionadores automáticamente al salir de un estado (`OnStateExit`).

---

## 4. Arquitectura de Frame Data y Cajas de Colisión

En un juego de pelea competitivo, cada ataque se rige por su **Frame Data**:
$$\text{Duración Total} = \text{Startup} + \text{Active} + \text{Recovery}$$

* **Startup (Inicio):** Fotogramas antes de que el golpe pueda hacer daño (la mano preparándose).
* **Active (Activo):** Fotogramas donde la `Hitbox` está encendida e inflige daño.
* **Recovery (Recuperación):** Fotogramas de retroceso donde el personaje es vulnerable.

### 📄 ScriptableObject de Frame Data (`AttackFrameDataSO`):
Crea un asset de datos para cada ataque en lugar de escribir números fijos en el código:

```csharp
using UnityEngine;

[CreateAssetMenu(fileName = "NewAttackFrameData", menuName = "SF3/Attack Frame Data")]
public class AttackFrameDataSO : ScriptableObject
{
    [Header("Identificación")]
    public string attackName = "Light Punch";
    public AnimationClip clip;

    [Header("Cronometría de Fotogramas (a 14 FPS)")]
    public int startupFrames = 3;
    public int activeFrames = 2;
    public int recoveryFrames = 5;

    [Header("Propiedades de Combate")]
    public int damage = 40;
    public int hitstunFrames = 11;
    public int blockstunFrames = 9;
    public int hitstopFrames = 10; // Congelación de impacto

    [Header("Flags de Cancelación")]
    public bool canCancelIntoSpecial = true;
    public bool canCancelIntoSuper = true;
}
```

### 🎨 Visualizador de Gizmos para Hitboxes en Escena:
Para ver las cajas coloreadas en la ventana **Scene** como en los torneos profesionales (Evo / Super Arcade):

```csharp
using UnityEngine;

public class FighterHitboxGizmo : MonoBehaviour
{
    public enum BoxType { Pushbox, Hurtbox, Hitbox, ParryTrigger }
    public BoxType boxType;

    private void OnDrawGizmos()
    {
        BoxCollider2D col = GetComponent<BoxCollider2D>();
        if (col == null || !enabled) return;

        Color fillColor = boxType switch
        {
            BoxType.Pushbox => new Color(0f, 1f, 0f, 0.25f),     // Verde
            BoxType.Hurtbox => new Color(0f, 0.5f, 1f, 0.35f),   // Azul cian
            BoxType.Hitbox => new Color(1f, 0f, 0f, 0.5f),       // Rojo
            BoxType.ParryTrigger => new Color(1f, 1f, 0f, 0.4f), // Amarillo
            _ => Color.white
        };

        Gizmos.color = fillColor;
        Vector3 center = transform.position + (Vector3)col.offset;
        Gizmos.DrawCube(center, col.size);
        Gizmos.color = new Color(fillColor.r, fillColor.g, fillColor.b, 1f);
        Gizmos.DrawWireCube(center, col.size);
    }
}
```

---

## 5. El Sistema de Entrada (Input Buffer y Movimientos Especiales)

En Street Fighter no basta con detectar si un botón fue presionado; el juego debe registrar secuencias direccionales complejas:
* **Hadouken:** Cuarto de círculo adelante ($\downarrow \searrow \rightarrow + \text{Punch}$ / Notación numérica: `236P`).
* **Shoryuken:** Golpe de dragón ($\rightarrow \downarrow \searrow + \text{Punch}$ / Notación numérica: `623P`).
* **Tatsumaki:** Cuarto de círculo atrás ($\downarrow \swarrow \leftarrow + \text{Kick}$ / `214K`).

### 🕹️ Input Buffer (Cola de Entradas con Tolerancia):
Para que los movimientos salgan suaves sin requerir una precisión imposible de robot:
1. Mantén una lista circular de entradas con marca de tiempo:
   ```csharp
   public struct TimestampedInput
   {
       public Vector2 direction;
       public bool punchPressed;
       public bool kickPressed;
       public float timestamp;
   }
   ```
2. Conserva los últimos **15 fotogramas** de historial.
3. Cuando el jugador presione el botón de puño, revisa el historial hacia atrás:
   * Si en los últimos 12 frames se detectó: `Abajo` ➔ `Abajo-Adelante` ➔ `Adelante` $\Rightarrow$ Disparar **`special_hadouken`**.
   * Si en los últimos 12 frames se detectó: `Adelante` ➔ `Abajo` ➔ `Abajo-Adelante` $\Rightarrow$ Disparar **`special_shoryuken`**.
   * De lo contrario $\Rightarrow$ Disparar el golpe normal (`light_punch` o `heavy_punch`).

---

## 6. Shaders y Efectos de Impacto en Shader Graph 2D

### ⚡ 1. Hit Flash Shader (Destello Blanco al Recibir Impacto):
Cuando un personaje recibe un golpe, su sprite parpadea en color blanco sólido durante 2-3 frames para dar retroalimentación visual de impacto:
* En **Shader Graph (URP 2D Lit o Unlit)**:
  * Agrega una propiedad `Color` llamada `FlashColor` (blanco).
  * Agrega un `Float` llamado `FlashAmount` (de 0 a 1).
  * Usa un nodo `Lerp`: entre la textura base del sprite y `FlashColor` según `FlashAmount`.
  * En C#:
    ```csharp
    public System.Collections.IEnumerator TriggerHitFlash(float duration = 0.08f)
    {
        spriteRenderer.material.SetFloat("_FlashAmount", 1f);
        yield return new WaitForSeconds(duration);
        spriteRenderer.material.SetFloat("_FlashAmount", 0f);
    }
    ```

### 🥋 2. Palette Swap Shader (Cambio de Trajes Oficiales CPS-3):
Ya tienes todas las paletas oficiales de Capcom (`palette000.pal`, `palette001.pal`, etc.) en el paquete.
* En lugar de duplicar los 32,000 sprites para tener a Ryu con gi azul o gi negro:
  * Diseña un shader de reemplazo de paleta (*LUT Palette Swap*):
  * El shader toma la paleta original como índice de color y mapea cada píxel a la fila de la nueva paleta en una pequeña textura de 16 colores.
  * ¡Con una sola textura de 16x8 píxeles puedes cambiar el traje de cualquier personaje en tiempo real!

### ❄️ 3. Hitstop / Freeze Frame (El secreto de la sensación "Game Juice"):
El impacto no se siente pesado por el sonido, sino por la **micro-congelación del tiempo** en el golpe:
* Al impactar un puño medio: congelar animaciones por **6 fotogramas** (~0.1 segundos).
* Al impactar un golpe fuerte o Super Art: congelar por **12 a 16 fotogramas**.
* Al ejecutar un **Parry exitoso**: congelar por **14 fotogramas** a ambos luchadores, emitir el destello azul de `05_Parry_Blue_Flash_Iconic` y reproducir `Parry_Success_Iconic_SF3.wav`.
* **¡Importante!** No uses `Time.timeScale = 0` globalmente porque pausará la música y los efectos de partículas. En su lugar, pausa el `animator.speed = 0` y la velocidad del `Rigidbody2D` durante los fotogramas de Hitstop.

---

## 7. Preparación para Control Corporal e IA (Kinect / WebCam)

Si el objetivo del proyecto es controlar al luchador con el cuerpo humano:

### Opción A: Kinect v2 (Hardware Oficial de Microsoft)
* **SDK:** *Kinect for Windows SDK v2.0* instalado en el sistema operativo Windows.
* **Paquete Unity:** *Kinect v2 Examples with MS-SDK* (o Azure Kinect Sensor SDK si usas la versión moderna).
* **Mapeo:**
  * Altura de la muñeca respecto al hombro $\Rightarrow$ Detección de puñetazo alto/medio.
  * Posición de los tobillos $\Rightarrow$ Detección de patada.
  * Rodillas flexionadas $\Rightarrow$ Detección de agacharse (`crouch_down`).

### Opción B: MediaPipe Unity Plugin (Cámara Web Estándar / Laptop)
Si algún miembro del equipo no tiene el sensor físico Kinect en su casa:
* **MediaPipe Unity Plugin** (de Homuler en GitHub):
  * Ejecuta la red neuronal de seguimiento de esqueleto de Google a 60 FPS en tiempo real usando **cualquier cámara web USB integrada**.
  * Te entrega las mismas coordenadas 3D de los huesos que un Kinect.
* **Filtro de Suavizado (Low-Pass Filter):**
  * Para evitar que el personaje lance golpes falsos por el temblor natural de la cámara:
    ```csharp
    smoothedHandPos = Vector3.Lerp(smoothedHandPos, rawHandPos, Time.deltaTime * smoothingFactor);
    ```

---

## 8. Herramientas de Depuración en Tiempo de Ejecución

Para afinar el juego a nivel milimétrico como un arcade real, incluye este script de prueba rápida:

### ⏱️ Frame-by-Frame Stepper Script (`SF3FrameStepper.cs`):
```csharp
using UnityEngine;

public class SF3FrameStepper : MonoBehaviour
{
    private bool isPaused = false;

    void Update()
    {
        // Presiona 'P' para pausar el combate
        if (Input.GetKeyDown(KeyCode.P))
        {
            isPaused = !isPaused;
            Time.timeScale = isPaused ? 0f : 1f;
        }

        // Presiona 'F' mientras está pausado para avanzar exactamente 1 fotograma (a 60 FPS)
        if (isPaused && Input.GetKeyDown(KeyCode.F))
        {
            StartCoroutine(StepOneFrame());
        }
    }

    private System.Collections.IEnumerator StepOneFrame()
    {
        Time.timeScale = 1f;
        yield return new WaitForFixedUpdate();
        Time.timeScale = 0f;
    }
}
```

---

## 9. Lista de Verificación para el Equipo

Antes de comenzar a programar personajes complejos:
- [ ] Instalar **Cinemachine** desde el Unity Package Manager.
- [ ] Configurar la **Main Camera** con el componente **Pixel Perfect Camera** (Assets PPU: 100, Ref Resolution: 384x224 o 1920x1080).
- [ ] Configurar las **Sorting Layers** (`Stage_Sky`, `Stage_Distant`, `Stage_Mid`, `Stage_Floor`, `Fighters`, `Hit_Effects`, `UI`).
- [ ] Crear el GameObject **SoundManager** con el script `SF3SoundManager.cs` en la escena de prueba.
- [ ] Probar la herramienta `SF3 Tools > Auto-Generate Animation Clips from Selected Folder` en la carpeta `Characters/02_Ryu` para validar que todas las 7 categorías generen sus animaciones `.anim` a 14 FPS.
- [ ] Probar el script de avance fotograma a fotograma (`P` para pausar, `F` para avanzar 1 frame) para calibrar las ventanas de Parry e impactos.
