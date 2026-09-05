# 🌿 Contexto de Flujo Git y Reglas de Pull Requests
## Street Fighter III: 3rd Strike (Unity + Azure Kinect + IA Adaptativa)

Reglas estrictas de control de versiones para evitar conflictos de fusión (*Merge Conflicts*) en Unity.

---

### 1. Reglas de Ramas
* **Nadie comitea directo en `main`.**
* Cada tarea se desarrolla en una rama nombrada: `feature/sp<SPRINT>-<DEV>-<NOMBRE_CORTO>`.
* Antes de crear una rama: `git checkout main && git pull origin main`.

---

### 2. Reglas de Unity y Git
* **Prefabs Separados:** Marco trabaja en `Fighter_Ryu.prefab`, Sebas en `Fighter_Ken.prefab` y Kevin en `Fighter_ChunLi.prefab`.
* **Escenas Sandbox Personales:** Cada desarrollador prueba en su escena personal (`Scenes/Sandbox_Marco.unity`, `Sandbox_Sebas.unity`, `Sandbox_Kevin.unity`).
* **La Escena Principal:** `Scenes/Main_Fight_Stage.unity` solo se actualiza los martes en el laboratorio.

---

### 3. Cierre de Issues Automático
* En la descripción de cada Pull Request, escribir:  
  `Closes #<NUMERO_ISSUE>`
* Esto cierra la Issue en GitHub y mueve la tarjeta en el tablero Kanban automáticamente a **`Done`**.
