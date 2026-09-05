# 💥 Guía 05: Hitboxes, Hurtboxes y Eventos de Animación
## El Sistema de Daño y Sincronización de Impactos

En los juegos de pelea no se usan colisiones normales. Se utiliza el sistema universal de **Pushbox, Hurtbox y Hitbox**:
* **Pushbox:** Es verde y sólida. Impide que los personajes se atraviesen.
* **Hurtbox (Caja de Daño):** Es azul/amarilla y representa el cuerpo vulnerable del personaje. Si una Hitbox rival la toca, recibes daño.
* **Hitbox (Caja de Golpe):** Es roja. Solo existe durante los fotogramas en que el puño o pie está completamente estirado. Si toca la Hurtbox rival, le inflige daño y activa las chispas.

En esta guía aprenderás cómo configurar este sistema y cómo usar **Animation Events** para encender y apagar los golpes en el fotograma exacto.

---

### 📍 Paso 1: Configurar las Capas (Layers) en Unity
Para que una Hitbox nunca choque con otra Hitbox, sino únicamente con la Hurtbox rival:
1. En la barra superior de Unity, ve a: **Edit** ➔ **Project Settings**.
2. En la lista de la izquierda, haz clic en **Tags and Layers**.
3. Despliega la sección **Layers**.
4. En las capas de usuario vacías (User Layer 8 en adelante), escribe:
   * Layer 8: **`Fighter`**
   * Layer 9: **`Hurtbox`**
   * Layer 10: **`Hitbox`**

---

### 📍 Paso 2: Configurar la Matriz de Físicas 2D
1. Dentro de la misma ventana **Project Settings**, haz clic en **Physics 2D** en la lista izquierda.
2. Desplázate hacia abajo hasta encontrar una cuadrícula de casillas llamada:
   **Layer Collision Matrix**.
3. Desmarca todas las casillas innecesarias para que:
   * `Hitbox` **SOLO tenga palomita con `Hurtbox`**.
   * `Hitbox` **NO** choque con `Hitbox`.
   * `Hurtbox` **NO** choque con `Hurtbox`.
4. Cierra la ventana de Project Settings.

---

### 📍 Paso 3: Asignar las Capas a los GameObjects
1. En la ventana **Hierarchy**, selecciona el hijo **`Hurtbox_Root`** de tu personaje.
   * En la parte superior derecha del Inspector, haz clic en el desplegable **Layer** y selecciona: **`Hurtbox`**.
   * Si Unity te pregunta *"Do you want to set layer to children too?"*, haz clic en **Yes, change children**.
2. Selecciona el hijo **`Hitbox_Root`**.
   * Cambia su **Layer** a: **`Hitbox`**.

---

### 📍 Paso 4: Qué son los Animation Events y Cómo Usarlos
Un golpe no debe hacer daño todo el tiempo; únicamente en los fotogramas en que la mano o pie impacta. Para lograr esto sin escribir líneas interminables de temporizadores en C#, usamos **Animation Events**:

1. En la ventana **Hierarchy**, selecciona tu personaje `Fighter_Ryu`.
2. Abre la ventana **Animation** (`Window > Animation > Animation` o `Ctrl + 6`).
3. En el menú desplegable de animaciones (arriba a la izquierda de la ventana Animation), selecciona la animación de ataque: por ejemplo `Ryu_Heavy_Punch`.
4. Mueve la barra vertical blanca de tiempo (la aguja de reproducción) cuadro por cuadro hasta encontrar el frame donde el puño está completamente extendido (por ejemplo, el **frame 3**).

#### Crear el Evento de "Activar Golpe":
1. Justo debajo de la regla con los números de fotogramas, haz **clic derecho** sobre la línea gris y selecciona:
   **`Add Animation Event`**.
2. Verás que aparece un pequeño marcador con forma de lápiz o etiqueta blanca.
3. Con ese marcador seleccionado, mira el panel **Inspector** a la derecha:
   * En el campo **Function**, escribe el nombre exacto de la función en tu script:
     **`EnableHitbox`** (o `ActivarGolpe`).

#### Crear el Evento de "Desactivar Golpe":
1. Ahora avanza la aguja de tiempo un par de cuadros hacia adelante, donde el puño comienza a replegarse (por ejemplo, el **frame 6**).
2. Haz **clic derecho** ➔ **`Add Animation Event`**.
3. En el Inspector, en el campo **Function**, escribe:
   **`DisableHitbox`** (o `DesactivarGolpe`).

#### Crear el Evento de "Sonido de Golpe":
1. En el mismo **frame 3** (donde impacta el golpe), haz clic derecho ➔ **`Add Animation Event`**.
2. En **Function**, escribe: **`PlayAttackVoice`**.

---

### 💻 Ejemplo de Script C# para Colisionadores (Listo para Usar)
Hemos incluido en el paquete el script `Assets/StreetFighter3_ThirdStrike/Scripts/Combat/FighterCombatColliders.cs`.
Este script contiene las funciones listas para ser llamadas por tus Animation Events:

```csharp
using UnityEngine;

public class FighterCombatColliders : MonoBehaviour
{
    [Header("Referencias a Colisionadores")]
    public GameObject hitboxObject; // Asignar el hijo Hitbox_Root
    public AudioClip attackVoiceClip;

    // Llamado por el Animation Event en el frame de impacto
    public void EnableHitbox()
    {
        if (hitboxObject != null)
            hitboxObject.SetActive(true);
    }

    // Llamado por el Animation Event cuando el golpe termina
    public void DisableHitbox()
    {
        if (hitboxObject != null)
            hitboxObject.SetActive(false);
    }

    // Reproduce la voz del personaje en el momento del impacto
    public void PlayAttackVoice()
    {
        if (attackVoiceClip != null)
            SF3SoundManager.Instance.PlayVoice(attackVoiceClip);
    }
}
```
