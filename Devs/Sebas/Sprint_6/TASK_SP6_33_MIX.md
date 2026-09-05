# 📌 Tarea #33 [SP6-SEBAS-33]: Pulido de Assets, Shaders de Destello y Balance de Mezcla de Audio
## Sprint 6 (Nov 16 – Nov 30) | Asignado a: @Sebas

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp6-sebas-polish-audio-mix
```

---

### 🎯 2. Explicación Técnica de la Tarea

Normalizar volúmenes de SFX vs BGM vs Voces, ajustar shaders de destello de impacto y corregir detalles visuales de Ken y escenarios.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de pulido audiovisual en Unity. Por favor lee este archivo y explícame cómo balancear los AudioMixers para que la música no tape las voces de los luchadores, y cómo revisar que ningún sprite tenga artefactos visuales."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] AudioMixer balanceado (Voces, SFX y Música tienen volumen armónico).
- [ ] Todos los fondos y sprites verificados sin bordes borrosos.
- [ ] Efectos visuales de impacto perfectamente alineados.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: pulido de assets, shaders de destello y balance de mezcla de audio (#33)"

# 2. Subir rama a GitHub
git push -u origin feature/sp6-sebas-polish-audio-mix
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #33`.