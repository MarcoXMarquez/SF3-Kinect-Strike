# 📌 Tarea #14 [SP3-MARCO-14]: Grabador de Telemetría para Entrenamiento (MatchTelemetryLogger.cs)
## Sprint 3 (Oct 5 – Oct 18) | Asignado a: @Marco

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp3-marco-telemetry-logger
```

---

### 🎯 2. Explicación Técnica de la Tarea

Script que graba en cada frame [distancia, estado_propio, estado_rival, accion] para construir el dataset de aprendizaje por imitación.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de Machine Learning en Unity. Por favor lee este archivo y explícame cómo programar MatchTelemetryLogger.cs para registrar vectores de estado y acciones humanas en formato CSV/SQLite durante las partidas del laboratorio."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] MatchTelemetryLogger registra datos cada frame sin causar caídas de FPS.
- [ ] Guarda archivo de telemetría estructurado al finalizar la partida.
- [ ] Probado grabando partidas en el laboratorio los martes.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: grabador de telemetría para entrenamiento (matchtelemetrylogger.cs) (#14)"

# 2. Subir rama a GitHub
git push -u origin feature/sp3-marco-telemetry-logger
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #14`.