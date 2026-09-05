# 📌 Tarea #24 [SP4-KEVIN-24]: Mapeo de Gestos de Patada y Hadouken en Azure Kinect (Lab)
## Sprint 4 (Oct 19 – Nov 1) | Asignado a: @Kevin

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp4-kevin-kinect-kicks-hadouken
```

---

### 🎯 2. Explicación Técnica de la Tarea

Detectar elevación de pierna para patada física y unión/empuje de dos manos para disparar Hadouken en Azure Kinect.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de visión y sensores. Por favor lee este archivo y explícame cómo calcular los umbrales de posición de tobillos/rodillas para detectar patadas y la distancia euclidiana entre ambas muñecas para el gesto de Hadouken."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Elevación de pierna activa patada en el personaje en pantalla.
- [ ] Juntar y proyectar ambas manos dispara el Hadouken.
- [ ] Validado en hardware físico en los martes de laboratorio.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: mapeo de gestos de patada y hadouken en azure kinect (lab) (#24)"

# 2. Subir rama a GitHub
git push -u origin feature/sp4-kevin-kinect-kicks-hadouken
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #24`.