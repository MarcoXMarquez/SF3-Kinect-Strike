# 📌 Tarea #12 [SP2-KEVIN-12]: Clasificador Somatosensorial Azure Kinect (Puñetazo y Bloqueo en Lab)
## Sprint 2 (Sep 21 – Oct 4) | Asignado a: @Kevin

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp2-kevin-kinect-gestures
```

---

### 🎯 2. Explicación Técnica de la Tarea

Algoritmo de detección de puño por velocidad de muñeca y bloqueo por brazos cruzados en Azure Kinect, validado en los martes de Lab.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de visión y sensores. Por favor lee este archivo y explícame cómo programar el algoritmo cinemático que calcula la velocidad del vector muñeca-codo para detectar puñetazos directos y la proximidad de muñecas para bloqueo en Azure Kinect."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Algoritmo de velocidad detecta extensión rápida de brazo como puñetazo.
- [ ] Posición de guardia detectada cuando las muñecas se cruzan frente al torso.
- [ ] Probado en hardware físico de Azure Kinect en el laboratorio.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: clasificador somatosensorial azure kinect (puñetazo y bloqueo en lab) (#12)"

# 2. Subir rama a GitHub
git push -u origin feature/sp2-kevin-kinect-gestures
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #12`.