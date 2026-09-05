# 📌 Tarea #29 [SP5-KEVIN-29]: HUD Arcade Completo (Barras de Vida, Super Gauge y Timer de 99s)
## Sprint 5 (Nov 2 – Nov 15) | Asignado a: @Kevin

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp5-kevin-hud-arcade
```

---

### 🎯 2. Explicación Técnica de la Tarea

Diseñar e implementar el HUD oficial Pixel-Perfect: barras de vida verde/roja, temporizador de 99s y barra de Super Art.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de UI en Unity. Por favor lee este archivo y explícame cómo construir el HUD arcade de SF3 con Canvas Pixel-Perfect, barras de vida con efecto de daño residual amarillo, medidor de Super y reloj de 99 segundos."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Barras de vida reflejan el daño recibido con animación suave.
- [ ] Temporizador cuenta regresiva de 99 a 0 segundos y activa Time Over.
- [ ] Barra de Super Art se llena al golpear y recibir daño.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: hud arcade completo (barras de vida, super gauge y timer de 99s) (#29)"

# 2. Subir rama a GitHub
git push -u origin feature/sp5-kevin-hud-arcade
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #29`.