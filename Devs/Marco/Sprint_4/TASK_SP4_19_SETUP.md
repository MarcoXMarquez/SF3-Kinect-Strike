# 📌 Tarea #19 [SP4-MARCO-19]: Configuración de Unity ML-Agents y PyTorch CUDA en GPU
## Sprint 4 (Oct 19 – Nov 1) | Asignado a: @Marco

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp4-marco-mlagents-setup
```

---

### 🎯 2. Explicación Técnica de la Tarea

Instalar el package de Unity ML-Agents, configurar FighterAgent : Agent en C# y validar la comunicación con PyTorch en tu GPU RTX 4060.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de Inteligencia Artificial en Unity. Por favor lee este archivo y explícame cómo estructurar la clase FighterAgent heredando de Agent de ML-Agents, definir el espacio de observaciones continuas y acciones discretas, y verificar la conexión con Python y PyTorch."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] FighterAgent implementa CollectObservations, OnActionReceived y Heuristic.
- [ ] Espacio de observación incluye distancias relativas, vida y estados.
- [ ] Comunicación con mlagents-learn validada en la GPU RTX 4060.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: configuración de unity ml-agents y pytorch cuda en gpu (#19)"

# 2. Subir rama a GitHub
git push -u origin feature/sp4-marco-mlagents-setup
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #19`.