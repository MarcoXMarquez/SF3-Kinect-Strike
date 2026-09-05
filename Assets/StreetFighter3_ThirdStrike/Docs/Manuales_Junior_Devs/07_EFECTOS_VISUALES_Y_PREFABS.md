# ✨ Guía 07: Efectos Visuales y Prefabs
## Destello de Parry, Chispas de Impacto y Proyectiles Hadouken

En `Assets/StreetFighter3_ThirdStrike/Effects/` tienes todas las animaciones de efectos visuales del juego organizadas en carpetas. Para poder instanciarlas dinámicamente mediante código cuando ocurra un golpe o un bloqueo, debemos convertirlas en **Prefabs** reutilizables.

---

### 📍 ¿Qué es un Prefab?
Un Prefab en Unity es una "plantilla" o molde guardado en tu proyecto. En lugar de tener 50 chispas colocadas en la escena todo el tiempo, tienes un Prefab en tu carpeta y tu código crea una copia exacta en el punto de impacto solo cuando hay un golpe, y luego la destruye.

---

### 📍 Paso 1: Crear el Prefab del Destello de Parry (Iconic Blue Flash)
El destello azul de Parry (`05_Parry_Blue_Flash_Iconic`) es el efecto más legendario de Street Fighter III.

1. En la ventana **Hierarchy**, haz clic derecho ➔ **Create Empty**.
2. Nómbralo: **`FX_Parry_BlueFlash`**.
3. Añade los siguientes componentes:
   * **Sprite Renderer:**
     * Sorting Layer: **`Hit_Effects`**.
     * Order in Layer: **`20`** (para que se dibuje por encima de los luchadores).
   * **Animator:**
     * Asigna un Animator Controller con los 31 frames de la animación de destello de Parry.
4. Añade el script de autodestrucción:
   * Crea un script llamado `AutoDestroyOnAnimationEnd.cs` (código abajo) y agrégalo al GameObject.
5. **Convertirlo en Prefab:**
   * En la ventana **Project**, crea una carpeta llamada `Assets/StreetFighter3_ThirdStrike/Prefabs`.
   * Arrastra el GameObject `FX_Parry_BlueFlash` desde la Hierarchy hacia la carpeta `Prefabs` en Project.
   * El nombre en la Hierarchy se volverá de color **azul**. ¡Eso indica que ya es un Prefab!
6. Ahora puedes borrar el objeto de la Hierarchy (ya está guardado a salvo en Project).

---

### 📍 Paso 2: Crear el Prefab del Proyectil (Hadouken)
1. En la Hierarchy, haz clic derecho ➔ **Create Empty**.
2. Nómbralo: **`Projectile_Hadouken`**.
3. Añade los componentes:
   * **Sprite Renderer:**
     * Sorting Layer: **`Hit_Effects`**, Order in Layer: **`15`**.
     * Asigna el primer sprite de `Effects/Projectiles_Ryu_Hadouken/`.
   * **Animator:** Con la animación de vuelo continuo del Hadouken.
   * **Rigidbody 2D:**
     * Body Type: `Kinematic`.
   * **Circle Collider 2D:**
     * Marca la casilla **`Is Trigger` [X]** (True).
     * Ajusta el radio para cubrir la bola de energía.
4. Arrastra `Projectile_Hadouken` a tu carpeta `Prefabs`.
5. Bórralo de la Hierarchy.

---

### 💻 Script C# para Auto-Destruir Efectos Visuales
Crea este script en `Assets/StreetFighter3_ThirdStrike/Scripts/Combat/AutoDestroyOnAnimationEnd.cs`:

```csharp
using UnityEngine;

public class AutoDestroyOnAnimationEnd : MonoBehaviour
{
    // Llamado por un Animation Event en el último fotograma del efecto
    public void DestroyEffect()
    {
        Destroy(gameObject);
    }

    // Opcional: temporizador de seguridad por si no tiene eventos
    public float fallbackLifetime = 0.5f;

    void Start()
    {
        Destroy(gameObject, fallbackLifetime);
    }
}
```

---

### 💻 Cómo Instanciar Efectos por Código
En tu script de combate (o cuando el Kinect detecte el movimiento de Hadouken):

```csharp
public class FighterCombat : MonoBehaviour
{
    public GameObject hadoukenPrefab; // Asignar el Prefab en el Inspector
    public Transform spawnPoint;      // Punto frente a las manos del personaje

    public void SpawnHadouken()
    {
        GameObject projectile = Instantiate(hadoukenPrefab, spawnPoint.position, spawnPoint.rotation);
        
        // Darle velocidad hacia adelante según hacia dónde mira el personaje
        Rigidbody2D rb = projectile.GetComponent<Rigidbody2D>();
        float direction = transform.localScale.x; // 1 si mira a la derecha, -1 a la izquierda
        rb.linearVelocity = new Vector2(direction * 8f, 0);
    }
}
```
