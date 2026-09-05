# 📌 Tarea #2 [SP1-MARCO-02]: Pipeline de Animaciones de Ryu (02_Ryu)
## Sprint 1 (Sep 7 – Sep 20) | Asignado a: @Marco

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp1-marco-ryu-anim
```

---

### 🎯 2. Explicación Técnica de la Tarea

Sincronizar los 64 AnimationClips de Ryu en Ryu_Animator.controller y verificar retornos automáticos a reposo.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de animación en Unity. Por favor lee este archivo y explícame cómo verificar los 64 clips de Ryu, cómo funciona el auto-poblado en el Animator y cómo calibrar pivotes para evitar desplazamientos."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Ryu_Animator.controller contiene los 64 estados organizados.
- [ ] idle_stance es el estado por defecto.
- [ ] Ataques en modo Play vuelven a idle_stance.
- [ ] No hay desplazamientos visuales erróneos en el pie de apoyo.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: pipeline de animaciones de ryu (02_ryu) (#2)"

# 2. Subir rama a GitHub
git push -u origin feature/sp1-marco-ryu-anim
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #2`.