# 📌 Tarea #4 [SP1-SEBAS-04]: Montaje del Escenario Japón (Suzaku Castle) con Parallax
## Sprint 1 (Sep 7 – Sep 20) | Asignado a: @Sebas

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp1-sebas-japan-stage
```

---

### 🎯 2. Explicación Técnica de la Tarea

Configurar Sorting Layers y montar el escenario de Suzaku Castle con el script ParallaxBackground.cs y suelo con colisión.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de diseño de niveles 2D. Por favor lee este archivo y explícame paso a paso cómo configurar las Sorting Layers, cómo colocar los sprites y cómo ajustar ParallaxBackground.cs para lograr profundidad 2.5D."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Sorting Layers configuradas sin tapar a los luchadores.
- [ ] Efecto Parallax activo al mover la cámara horizontalmente.
- [ ] Suelo con BoxCollider2D a Y=0.
- [ ] Guardado como Prefab reutilizable (Stage_Japan.prefab).

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: montaje del escenario japón (suzaku castle) con parallax (#4)"

# 2. Subir rama a GitHub
git push -u origin feature/sp1-sebas-japan-stage
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #4`.