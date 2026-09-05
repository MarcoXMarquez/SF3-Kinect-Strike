# 🕺 Guía 09: Arquitectura de Entrada y Preparación para Kinect
## Diseño Desacoplado para Conectar el Sensor de Movimiento sin Romper el Juego

### ⚠️ El Error Típico de los Desarrolladores Principiantes
Muchos programadores cometen el error de escribir cosas como:
```csharp
if (Input.GetKeyDown(KeyCode.Space)) // <-- ¡ERROR DE ARQUITECTURA!
{
    LanzarHadouken();
}
```
Si escribes eso directamente dentro de tu personaje, cuando llegue el momento de conectar el Kinect tendrás que borrar, modificar y arriesgarte a romper todo el código del luchador.

---

### 🛡️ La Solución Profesional: La Interfaz `IFighterInput`
Diseñaremos una **capa de abstracción de entrada**. El personaje no sabe (ni le importa) si la orden viene de un teclado, un gamepad o de un sensor Kinect que lee el esqueleto del jugador en tiempo real.

---

### 📍 Paso 1: Crear la Interfaz `IFighterInput.cs`
Crea este archivo en `Assets/StreetFighter3_ThirdStrike/Scripts/Input/IFighterInput.cs`:

```csharp
using UnityEngine;

public interface IFighterInput
{
    // Movimiento horizontal (-1 = izquierda, 0 = quieto, 1 = derecha)
    float GetHorizontalMove();

    // ¿Está agachado?
    bool IsCrouching();

    // ¿Quiere saltar?
    bool IsJumping();

    // Comandos de ataque
    bool WasLightPunchPressed();
    bool WasHeavyPunchPressed();
    bool WasHadoukenGestureDetected();
    bool WasShoryukenGestureDetected();
    bool WasParryStanceDetected();
}
```

---

### 📍 Paso 2: El Adaptador de Teclado (Para Desarrollar y Probar en Laptop)
Mientras configuras el juego y antes de conectar el hardware de Kinect, necesitas poder probar todo cómodamente desde el teclado:

Crea `Assets/StreetFighter3_ThirdStrike/Scripts/Input/KeyboardFighterInput.cs`:

```csharp
using UnityEngine;

public class KeyboardFighterInput : MonoBehaviour, IFighterInput
{
    public float GetHorizontalMove()
    {
        return Input.GetAxisRaw("Horizontal"); // Flechas izq / der o teclas A / D
    }

    public bool IsCrouching()
    {
        return Input.GetKey(KeyCode.S) || Input.GetKey(KeyCode.DownArrow);
    }

    public bool IsJumping()
    {
        return Input.GetKeyDown(KeyCode.W) || Input.GetKeyDown(KeyCode.UpArrow);
    }

    public bool WasLightPunchPressed()
    {
        return Input.GetKeyDown(KeyCode.J);
    }

    public bool WasHeavyPunchPressed()
    {
        return Input.GetKeyDown(KeyCode.K);
    }

    public bool WasHadoukenGestureDetected()
    {
        // En teclado simulamos el Hadouken con la tecla U
        return Input.GetKeyDown(KeyCode.U);
    }

    public bool WasShoryukenGestureDetected()
    {
        // En teclado simulamos el Shoryuken con la tecla I
        return Input.GetKeyDown(KeyCode.I);
    }

    public bool WasParryStanceDetected()
    {
        // En teclado simulamos el Parry con la tecla Espacio
        return Input.GetKeyDown(KeyCode.Space);
    }
}
```

---

### 📍 Paso 3: El Controlador del Personaje usando la Interfaz
Crea `Assets/StreetFighter3_ThirdStrike/Scripts/Combat/FighterController.cs`:

```csharp
using UnityEngine;

public class FighterController : MonoBehaviour
{
    private IFighterInput input;
    private Animator animator;
    private Rigidbody2D rb;

    void Awake()
    {
        // Busca cualquier componente de entrada acoplado (Keyboard o Kinect)
        input = GetComponent<IFighterInput>();
        animator = GetComponentInChildren<Animator>();
        rb = GetComponent<Rigidbody2D>();
    }

    void Update()
    {
        if (input == null) return;

        // 1. Lectura de movimiento
        float moveX = input.GetHorizontalMove();
        animator.SetFloat("MoveSpeed", Mathf.Abs(moveX));

        // 2. Comandos de ataques y gestos
        if (input.WasHadoukenGestureDetected())
        {
            animator.SetTrigger("Special_Hadouken");
        }
        else if (input.WasShoryukenGestureDetected())
        {
            animator.SetTrigger("Special_Shoryuken");
        }
        else if (input.WasLightPunchPressed())
        {
            animator.SetTrigger("Attack_LP");
        }
        else if (input.WasParryStanceDetected())
        {
            animator.SetTrigger("Parry");
        }
    }
}
```

---

### 📍 Paso 4: Cómo se conectará el Kinect en la Siguiente Fase
Cuando conecten el SDK de Kinect (Kinect v2 o Azure Kinect):
1. Solo tendrán que crear un nuevo script: `KinectFighterInputAdapter.cs` que implemente la misma interfaz `IFighterInput`.
2. En ese script, leerán las posiciones de las articulaciones (*Joints*):
   * **Hadouken:** Cuando ambas muñecas se extiendan rápidamente hacia adelante respecto a los hombros.
   * **Shoryuken:** Cuando la mano derecha suba verticalmente por encima de la cabeza a alta velocidad.
   * **Parry:** Cuando ambos antebrazos se crucen frente al pecho.
3. Para cambiar de teclado a Kinect, **¡solo remueves el componente `KeyboardFighterInput` y añades `KinectFighterInputAdapter` en el inspector!**
4. Todo el sistema visual, los sprites, animaciones y sonidos seguirán funcionando al 100% sin cambiar una sola línea de código en el luchador.
