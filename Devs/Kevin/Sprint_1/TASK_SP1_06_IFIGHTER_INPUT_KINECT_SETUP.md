# 📌 Tarea #6 [SP1-KEVIN]: Arquitectura IFighterInput y Azure Kinect SDK
## Sprint 1 (Sep 7 – Sep 20) | Asignado a: @Kevin

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

```bash
git checkout main
git pull origin main
git checkout -b feature/sp1-kevin-input-kinect
```

---

### 🎯 2. Explicación Técnica de la Tarea

Debes crear la **capa desacoplada de entrada** (`IFighterInput.cs`) y preparar el entorno de Azure Kinect:
1. **Interfaz `IFighterInput.cs`:** Ubicada en `Assets/StreetFighter3_ThirdStrike/Scripts/Input/`.
   - Métodos necesarios:
     - `float GetHorizontalAxis()` (retorna -1 para atrás, 1 para adelante, 0 neutral).
     - `bool IsCrouching()` (retorna true si está agachado).
     - `bool IsJumping()` (retorna true si ejecuta salto).
     - `bool IsAttacking(out FighterAttackType attackType)` (retorna true si presiona puño/patada).
     - `bool IsBlocking()` (retorna true si está en guardia).
2. **Emulador de Teclado `KeyboardFighterInput.cs`:**
   - Implementa `IFighterInput` para que Marco, Sebas y tú puedan jugar y probar el juego de miércoles a lunes sin sensor físico.
3. **Importación del SDK de Azure Kinect Body Tracking:**
   - Crear una escena de prueba `Assets/StreetFighter3_ThirdStrike/Scenes/Test_AzureKinect_Body.unity` para probar la detección de 32 articulaciones los **martes en el laboratorio**.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de arquitectura de software en Unity C#. Por favor lee `Devs/Kevin/Sprint_1/TASK_SP1_06_IFIGHTER_INPUT_KINECT_SETUP.md` y explícame paso a paso cómo debo diseñar e implementar la interfaz `IFighterInput.cs` y su adaptador de teclado `KeyboardFighterInput.cs`. Explícame por qué el desacoplamiento mediante interfaces es fundamental para el proyecto y guíame para preparar la estructura del SDK de Azure Kinect sin hacer el código por mí a ciegas."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] La interfaz `IFighterInput.cs` está creada y compila sin errores.
- [ ] `KeyboardFighterInput.cs` permite mover y atacar al personaje con teclas (`WASD`, `J`, `K`, `L`, `U`).
- [ ] El script de Azure Kinect está listo para recibir el esqueleto 3D en el laboratorio el martes.
- [ ] La escena de prueba `Test_AzureKinect_Body.unity` compila correctamente.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

```bash
git add .
git commit -m "feat: implementar IFighterInput y KeyboardFighterInput (#6)"
git push -u origin feature/sp1-kevin-input-kinect
```
Abre el Pull Request en GitHub con la descripción: `Closes #6`.
