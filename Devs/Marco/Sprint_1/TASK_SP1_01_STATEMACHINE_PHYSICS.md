# 📌 Tarea #1 [SP1-MARCO]: Máquina de Estados Core y Física de Salto
## Sprint 1 (Sep 7 – Sep 20) | Asignado a: @Marco

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp1-marco-statemachine
```

---

### 🎯 2. Explicación Técnica de la Tarea

Debes implementar la **Máquina de Estados de Combate Desacoplada** (`FighterStateMachine.cs`) y el controlador de física (`FighterPhysics.cs`) en `Assets/StreetFighter3_ThirdStrike/Scripts/Core/`:
1. **No usar transiciones con flechas en Animator:** La máquina de estados controla la animación llamando a `animator.Play(clipName, 0, 0f)`.
2. **Estados Soportados en Sprint 1:**
   - `Neutral / Idle`: Reposo en el suelo.
   - `WalkForward / WalkBackward`: Movimiento horizontal continuo.
   - `Crouching`: Postura agachada.
   - `Jumping`: Salto parabólico con física real ($V_y$ inicial y gravedad) para `jump_neutral`, `jump_forward` y `jump_backward`.
   - `AttackOneShot`: Estado ocupado al tirar un puño/patada que regresa automáticamente a Idle.
3. **Escena de Prueba Sandbox:** `Assets/StreetFighter3_ThirdStrike/Scenes/Sandbox_Marco.unity` con `Fighter_Ryu.prefab`.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de programación senior en Unity C#. Por favor lee el archivo `Devs/Marco/Sprint_1/TASK_SP1_01_STATEMACHINE_PHYSICS.md` y explícame paso a paso cómo debo estructurar y programar yo mismo los scripts `FighterStateMachine.cs` y `FighterPhysics.cs`. Explícame la lógica matemática del salto parabólico y el cambio de estados, guíame con la estructura de clases y ayúdame a revisar mi código para asegurar que cumpla todos los criterios de aceptación."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] El código compila sin errores ni warnings en Unity.
- [ ] Ryu camina adelante/atrás con `D` y `A`.
- [ ] Ryu se agacha manteniendo `S` y vuelve a Idle al soltar.
- [ ] Ryu salta con `W` describiendo una parábola física real y aterriza suavemente.
- [ ] Ataques con `J`, `K`, `L`, `U` vuelven a Idle automáticamente tras terminar la animación.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: implementar FighterStateMachine y FighterPhysics (#1)"

# 2. Subir rama a GitHub
git push -u origin feature/sp1-marco-statemachine
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #1`.
