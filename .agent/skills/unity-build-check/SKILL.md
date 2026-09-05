---
name: unity-build-check
description: Verificación de compilación en Unity C# (concordancia nombre clase vs archivo, diagnóstico de errores de compilador CS*, asmdef y directivas del editor).
---

# Unity Build Check Skill

Esta habilidad se encarga del análisis estático, diagnóstico de compilación y verificación estructural de scripts C# en proyectos Unity.

---

## 1. Regla de Oro: Nombre de Clase vs Nombre de Archivo

En Unity, para que un script pueda ser reconocido y adjuntado como componente en un GameObject:
- **El nombre del archivo `.cs` debe ser exactamente idéntico al nombre de la clase pública que hereda de `MonoBehaviour` (sensible a mayúsculas/minúsculas)**.

### Verificación:
- Archivo: `PlayerHealthController.cs`
  ```csharp
  // ✅ CORRECTO:
  public class PlayerHealthController : MonoBehaviour { }
  ```
- Si el archivo se llama `PlayerHealthController.cs` pero la clase se define como:
  ```csharp
  // ❌ ERROR CRÍTICO: Unity emitirá una advertencia y deshabilitará el componente
  public class HealthController : MonoBehaviour { }
  ```

---

## 2. Diagnóstico Sistemático de Errores de Compilación C# (`CS*`)

Cuando se ejecutan compilaciones o se leen logs de error, clasificar y resolver según el código de diagnóstico:

| Código | Significado | Causa Común & Solución |
| :--- | :--- | :--- |
| **`CS0246`** | El nombre del tipo o namespace no se encuentra | Falta directiva `using` (ej. `using UnityEngine.UI;`) o falta referencia en el `.asmdef`. |
| **`CS1061`** | El tipo no contiene una definición para el miembro | Propiedad/método mal escrito, no público, o método de extensión no importado. |
| **`CS0103`** | El nombre no existe en el contexto actual | Variable local no declarada, fuera de alcance, o parámetro mal nombrado. |
| **`CS0234`** | El tipo o namespace no existe en el namespace padre | Assembly Definition no referenciada o versión de paquete incompatible. |
| **`CS0117`** | El tipo no contiene una definición para el identificador estático | Método estático deprecado o renombrado en la versión de Unity en uso. |
| **`CS0161`** | No todas las rutas de código devuelven un valor | Falta `return` en algún camino condicional (`if/else` o `switch`). |

---

## 3. Manejo de Assembly Definitions (`.asmdef`)

Si el proyecto utiliza Assembly Definitions modulares:
- Verificar que el script pertenezca al ensamblado correcto.
- Si un script en `Gameplay.asmdef` necesita un tipo de `Core.asmdef`, `Gameplay.asmdef` debe incluir explícitamente a `Core` en su lista de `references`.
- Los scripts dentro de subcarpetas heredan el `.asmdef` padre más cercano a menos que se defina otro `.asmdef`.

---

## 4. Aislamiento de Código de Editor (`UnityEditor`)

El namespace `UnityEditor` solo está disponible dentro del Editor de Unity y **provocará que la compilación de Build (Player) falle**:
- Todo script que use `UnityEditor` debe:
  1. Estar ubicado dentro de una carpeta llamada `Editor` (ej. `Assets/Scripts/Editor/`).
  2. O estar encapsulado con directivas de preprocesador:
     ```csharp
     #if UNITY_EDITOR
     using UnityEditor;
     #endif

     public class ToolUtility
     {
     #if UNITY_EDITOR
         [MenuItem("Tools/Generar Assets")]
         public static void Generate() { }
     #endif
     }
     ```

---

## 5. Procedimiento de Inspección Rápida

1. Comprobar que no haya errores de sintaxis o llaves desbalanceadas.
2. Validar que el nombre de la clase coincida con el archivo.
3. Revisar que los `using` contengan los namespaces requeridos sin warnings no resueltos.
4. Ejecutar formateo y análisis de código:
   ```bash
   dotnet format whitespace
   dotnet format style
   ```
