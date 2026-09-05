# 📌 Tarea #3 [SP1-SEBAS-03]: Pipeline de Sprites y Animaciones de Ken (01_Ken)
## Sprint 1 (Sep 7 – Sep 20) | Asignado a: @Sebas

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp1-sebas-ken-anim
```

---

### 🎯 2. Explicación Técnica de la Tarea

Organizar las 7 categorías de Ken, generar AnimationClips a 14 FPS y crear Ken_Animator.controller.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de Unity. Por favor lee este archivo y explícame paso a paso cómo organizar las 7 categorías de Ken (01_Ken), cómo usar SF3 Tools para generar clips a 14 FPS y cómo armar el prefab Fighter_Ken.prefab."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Carpetas de 01_Ken organizadas con nombres descriptivos.
- [ ] AnimationClips a 14 FPS con Loop Time en Idle/Walk.
- [ ] Ken_Animator.controller contiene los estados sin errores.
- [ ] Fighter_Ken.prefab se reproduce en Sandbox_Sebas.unity.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: pipeline de sprites y animaciones de ken (01_ken) (#3)"

# 2. Subir rama a GitHub
git push -u origin feature/sp1-sebas-ken-anim
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #3`.