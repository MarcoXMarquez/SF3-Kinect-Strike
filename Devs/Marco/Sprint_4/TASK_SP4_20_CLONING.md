# 📌 Tarea #20 [SP4-MARCO-20]: Entrenamiento de Behavioral Cloning (BC / GAIL) en GPU
## Sprint 4 (Oct 19 – Nov 1) | Asignado a: @Marco

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp4-marco-behavioral-cloning
```

---

### 🎯 2. Explicación Técnica de la Tarea

Entrenar la política de imitación con el dataset humano de telemetría y exportar el modelo AI_Imitation.onnx para inferencia nativa.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de Deep Reinforcement Learning. Por favor lee este archivo y explícame cómo configurar el archivo yaml de entrenamiento con Behavioral Cloning (BC) y GAIL, ejecutar el entrenamiento en mi RTX 4060 y exportar el modelo ONNX a Unity."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Modelo entrenado con el dataset de partidas humanas del laboratorio.
- [ ] Archivo AI_Imitation.onnx exportado e integrado en Unity Sentis/Barracuda.
- [ ] El bot toma decisiones tácticas humanoides (spacing, bloqueo y castigo).

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: entrenamiento de behavioral cloning (bc / gail) en gpu (#20)"

# 2. Subir rama a GitHub
git push -u origin feature/sp4-marco-behavioral-cloning
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #20`.