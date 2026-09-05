# 📌 Tarea #35 [SP6-KEVIN-35]: Filtro de Suavizado de Ruido de Articulaciones en Azure Kinect (Lab)
## Sprint 6 (Nov 16 – Nov 30) | Asignado a: @Kevin

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp6-kevin-kinect-noise-filter
```

---

### 🎯 2. Explicación Técnica de la Tarea

Aplicar filtros de suavizado (Moving Average / Exponential Smoothing) a las 32 articulaciones para eliminar falsos disparos en el sensor.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de procesamiento de señales en Unity. Por favor lee este archivo y explícame cómo programar un filtro de suavizado temporal para las coordenadas (X, Y, Z) de Azure Kinect que elimine el jitter sin añadir latencia perceptible."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Filtro de suavizado elimina temblores en las manos y pies.
- [ ] Latencia de respuesta se mantiene por debajo de 50ms.
- [ ] Probado y calibrado en el laboratorio con el sensor físico.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: filtro de suavizado de ruido de articulaciones en azure kinect (lab) (#35)"

# 2. Subir rama a GitHub
git push -u origin feature/sp6-kevin-kinect-noise-filter
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #35`.