# 📌 Tarea #30 [SP5-KEVIN-30]: Guía Visual de Silueta Azure Kinect en Pantalla (Lab)
## Sprint 5 (Nov 2 – Nov 15) | Asignado a: @Kevin

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp5-kevin-kinect-silhouette
```

---

### 🎯 2. Explicación Técnica de la Tarea

Widget en esquina de la pantalla que muestra la silueta del usuario para saber si está en el rango óptimo del sensor (1.5m a 4m).

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de interfaces interactivas. Por favor lee este archivo y explícame cómo crear un widget de silueta que cambie de color (verde = buena posición, rojo = fuera de rango) según la coordenada Z del usuario en Azure Kinect."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Widget visualiza si el jugador está bien posicionado frente a la cámara.
- [ ] Alerta si está demasiado cerca (<1.5m) o lejos (>4m).
- [ ] Validado en el laboratorio los martes.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: guía visual de silueta azure kinect en pantalla (lab) (#30)"

# 2. Subir rama a GitHub
git push -u origin feature/sp5-kevin-kinect-silhouette
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #30`.