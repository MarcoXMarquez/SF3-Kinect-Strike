# 📌 Tarea #16 [SP3-SEBAS-16]: Montaje del Escenario China (Crowded Street) con Parallax
## Sprint 3 (Oct 5 – Oct 18) | Asignado a: @Sebas

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp3-sebas-china-stage
```

---

### 🎯 2. Explicación Técnica de la Tarea

Montar el segundo escenario oficial: Crowded Street (China) con múltiples capas de profundidad y Sorting Layers.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de diseño de niveles 2D. Por favor lee este archivo y explícame cómo montar el escenario de China en Stage_China.prefab, configurando las capas de ParallaxBackground.cs y los colisionadores de bordes y suelo."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Escenario de China montado con múltiples capas independientes.
- [ ] Efecto Parallax configurado y suave al moverse los luchadores.
- [ ] Colisionadores de esquinas (paredes invisibles) y suelo configurados.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: montaje del escenario china (crowded street) con parallax (#16)"

# 2. Subir rama a GitHub
git push -u origin feature/sp3-sebas-china-stage
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #16`.