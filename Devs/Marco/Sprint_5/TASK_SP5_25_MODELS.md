# 📌 Tarea #25 [SP5-MARCO-25]: Entrenamiento por Refuerzo (PPO) de 3 Dificultades (Easy, Med, Hard)
## Sprint 5 (Nov 2 – Nov 15) | Asignado a: @Marco

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp5-marco-rl-difficulty-models
```

---

### 🎯 2. Explicación Técnica de la Tarea

Entrenar políticas por refuerzo con recompensas por control de distancia, castigo y daño, exportando 3 modelos ONNX.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de Machine Learning. Por favor lee este archivo y explícame cómo diseñar las funciones de recompensa en C# y configurar PPO en PyTorch para entrenar 3 niveles de habilidad (Fácil, Medio, Difícil) en mi GPU RTX 4060."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] 3 modelos exportados: AI_Easy.onnx, AI_Medium.onnx, AI_Hard.onnx.
- [ ] AI_Easy comete errores y deja aperturas.
- [ ] AI_Hard castiga saltos con Shoryuken y aplica parry reactivo.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: entrenamiento por refuerzo (ppo) de 3 dificultades (easy, med, hard) (#25)"

# 2. Subir rama a GitHub
git push -u origin feature/sp5-marco-rl-difficulty-models
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #25`.