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

### 💻 Paso 4: Añadir el Script `FighterCombatColliders` al GameObject con el Animator (`Visuals`)

> [!IMPORTANT]
> **Regla de Unity para Animation Events:**
> Unity **únicamente** busca funciones públicas en los componentes que están en el **mismo GameObject que tiene el componente `Animator`** (es decir, en el hijo **`Visuals`**). Si colocas el script en el padre `Fighter_Ryu`, el menú desplegable de funciones aparecerá vacío.

1. En la ventana **Hierarchy**, selecciona el hijo **`Visuals`** de Ryu.
2. Haz clic en **Add Component** ➔ busca y añade **`FighterCombatColliders`**.
3. En el Inspector:
   * En el campo **Hitbox Object**, arrastra el hijo **`Hitbox_Root`**.
   * *(Opcional)* En el campo **Attack Voice Clip**, arrastra el audio de voz que desees (ej. `Audio/Voices/02_Ryu/SE_00062.wav`).

---

### 📍 Paso 5: Cómo Posicionar la Hitbox sobre el Puño (Viendo el Golpe en Vivo)

1. Con el hijo **`Visuals`** seleccionado en la Hierarchy, abre la ventana **Animation** (`Ctrl + 6`).
2. En el desplegable de animaciones (arriba a la izquierda de la ventana Animation), selecciona **`light_punch`**.
3. Mueve la barra vertical blanca de tiempo (la aguja de reproducción) hasta el **frame 2 o 3** (donde el puño está completamente extendido).
4. **¡Mira la ventana Scene!** Verás a Ryu congelado con el puño estirado.
5. En la Hierarchy, selecciona el hijo **`Hitbox_Root`**:
   * En el Inspector, haz clic en el botón **Edit Collider** del `Box Collider 2D`.
   * En la ventana Scene, **arrastra el recuadro para que envuelva exactamente el puño derecho de Ryu**.

---

### 📍 Paso 6: Crear los Animation Events (Encender y Apagar el Golpe)

1. En la ventana **Animation**, con la animación `light_punch` abierta:
2. **Evento para ENCENDER la Hitbox:**
   * Sitúa la aguja en el **frame 1 o 2** (justo cuando el puño sale).
   * Haz **clic derecho** sobre la línea gris de tiempo ➔ **`Add Animation Event`**.
   * Con la etiqueta blanca seleccionada, mira el **Inspector**: en el desplegable **Function**, ahora verás **`EnableHitbox()`** listado automáticamente. Selecciónalo.

3. **Evento para APAGAR la Hitbox:**
   * Mueve la aguja al **frame 4 o 5** (cuando el brazo empieza a replegarse).
   * Haz **clic derecho** ➔ **`Add Animation Event`**.
   * En el Inspector, en **Function**, selecciona **`DisableHitbox()`**.

4. **(Opcional) Evento de Voz:**
   * En el frame del impacto, crea otro Animation Event y selecciona **`PlayAttackVoice()`**.

El script ya viene incluido en `Assets/StreetFighter3_ThirdStrike/Scripts/Combat/FighterCombatColliders.cs`:

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
