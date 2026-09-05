---
name: unity-csharp-specialist
description: Reglas y restricciones de buenas prácticas en Unity C# (ciclo de vida, instanciación, asignación de memoria, eventos y rendimiento).
---

# Unity C# Specialist Skill

Esta habilidad proporciona reglas estrictas de desarrollo para proyectos Unity con C#. El incumplimiento de estas directrices genera problemas de rendimiento (caídas de FPS, picos de GC) o errores en tiempo de ejecución.

---

## 1. Reglas de Instanciación de Objetos Unity

### ❌ PROHIBIDO: Usar `new` en `MonoBehaviour` o `ScriptableObject`
Los componentes de Unity están administrados por el runtime nativo de C++. Instanciarlos con `new` rompe el ciclo de vida, la serialización y deja al componente huérfano de GameObject.

- **Para MonoBehaviour**:
  ```csharp
  // ❌ INCORRECTO:
  var myComponent = new PlayerController();

  // ✅ CORRECTO:
  var myComponent = gameObject.AddComponent<PlayerController>();
  // O instanciar prefab preconfigurado:
  var instance = Object.Instantiate(playerPrefab, position, rotation);
  ```

- **Para ScriptableObject**:
  ```csharp
  // ❌ INCORRECTO:
  var data = new ItemData();

  // ✅ CORRECTO:
  var data = ScriptableObject.CreateInstance<ItemData>();
  ```

---

## 2. Reglas del Game Loop (`Update`, `FixedUpdate`, `LateUpdate`)

### ❌ PROHIBIDO: Búsquedas dinámicas y reflexivas en bucles de frame
Nunca invoques métodos de búsqueda pesados dentro de `Update()`, `FixedUpdate()`, `LateUpdate()` o corrutinas recurrentes:
- `GetComponent<T>()` / `TryGetComponent<T>()`
- `GameObject.Find()` / `GameObject.FindWithTag()`
- `Object.FindObjectOfType<T>()` / `Object.FindObjectsByType<T>()`
- `Camera.main` (en versiones de Unity anteriores a 2020.2 o sin caché)

#### ✅ Solución: Caching o Inyección en Inspector
Almacena referencias en variables miembro durante la inicialización:
```csharp
public class PlayerMovement : MonoBehaviour
{
    [SerializeField] private Rigidbody rb; // Asignación preferente en Inspector
    [SerializeField] private CharacterController controller;

    private void Awake()
    {
        // Caché defensivo si no fue asignado en el Inspector
        if (rb == null) TryGetComponent(out rb);
    }

    private void FixedUpdate()
    {
        // Usar la referencia previamente cacheada
        rb.MovePosition(rb.position + movementVector * Time.fixedDeltaTime);
    }
}
```

---

## 3. Preservación de Memoria y Control del Garbage Collector (GC)

- **Evitar LINQ en Hot Paths**: Métodos como `.Where()`, `.Select()`, `.ToList()`, o `foreach` en colecciones no genéricas asignan memoria en el heap generando picos de GC.
- **Evitar Concatenación de Strings en Update**: Cada `"Vida: " + health` genera un objeto `string` nuevo en el heap. Usar `StringBuilder`, formateo con buffers o actualizar texto solo ante eventos de cambio.
- **Uso de Physics sin Garbage**: Preferir `Physics.RaycastNonAlloc()` o `Physics.OverlapSphereNonAlloc()` sobre `RaycastAll` / `OverlapSphere`.

---

## 4. Arquitectura Desacoplada por Eventos

Favorece el desacoplamiento de sistemas mediante eventos para que un sistema no conozca directamente a los demás:
- **C# Events nativos (`Action<T>`, `Func<T>`)**: Ultra rápidos, sin sobrecarga de serialización, ideales para sistemas puramente lógicos.
- **ScriptableObject Architecture (Game Events)**: Ideales para comunicar sistemas independientes (ej. UI con Player) sin referencias directas en escena.
- **UnityEvent**: Útiles cuando se requiere conectar eventos visualmente desde el Inspector de Unity.

---

## 5. Cuidado con Operadores de Coalescencia Nula (`?.` y `??`)

`UnityEngine.Object` sobrecarga el operador `==` para comprobar si el objeto subyacente en C++ ha sido destruido. Los operadores `?.` y `??` de C# puentean la sobrecarga de Unity:
```csharp
// ⚠️ PELIGROSO con objetos de UnityEngine.Object:
target?.TakeDamage(); 

// ✅ SEGURO:
if (target != null)
{
    target.TakeDamage();
}
```
