# 📌 Tarea #26 [SP5-MARCO-26]: Gestor de Dificultad Dinámica Adaptativa (AdaptiveAIManager.cs)
## Sprint 5 (Nov 2 – Nov 15) | Asignado a: @Marco

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp5-marco-adaptive-ai-manager
```

---

### 🎯 2. Explicación Técnica de la Tarea

Script que analiza la telemetría del jugador en vivo y cambia dinámicamente el modelo o pesos del bot para mantener el reto equilibrado.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de sistemas adaptativos. Por favor lee este archivo y explícame cómo programar AdaptiveAIManager.cs para evaluar métricas del jugador en vivo (frecuencia de aciertos, daño por segundo) y alternar entre los modelos ONNX en tiempo real."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] AdaptiveAIManager evalúa rendimiento del jugador entre rounds.
- [ ] Alterna suavemente entre modelos ONNX sin congelar la pantalla.
- [ ] Registra los cambios de dificultad en la base de datos SQLite.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: gestor de dificultad dinámica adaptativa (adaptiveaimanager.cs) (#26)"

# 2. Subir rama a GitHub
git push -u origin feature/sp5-marco-adaptive-ai-manager
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #26`.