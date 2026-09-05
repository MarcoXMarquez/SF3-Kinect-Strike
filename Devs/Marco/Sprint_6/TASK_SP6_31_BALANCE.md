# 📌 Tarea #31 [SP6-MARCO-31]: Calibración de Latencia y Balance de Frame Data del Bot
## Sprint 6 (Nov 16 – Nov 30) | Asignado a: @Marco

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp6-marco-bot-latency-balance
```

---

### 🎯 2. Explicación Técnica de la Tarea

Ajustar tiempos de reacción e interpolación de decisiones del bot para que el combate contra humanos en Kinect se sienta natural y justo.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de Game Feel y balance. Por favor lee este archivo y explícame cómo añadir pequeñas ventanas de reacción humana (100-200ms) a las decisiones del bot de IA para que no sea injustamente instantáneo frente a los movimientos físicos."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] El bot tiene tiempos de reacción calibrados y realistas.
- [ ] Combate se siente emocionante y justo para el usuario frente a Kinect.
- [ ] Probado en partidas continuas en el laboratorio.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: calibración de latencia y balance de frame data del bot (#31)"

# 2. Subir rama a GitHub
git push -u origin feature/sp6-marco-bot-latency-balance
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #31`.