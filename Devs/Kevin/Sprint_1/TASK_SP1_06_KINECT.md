# 📌 Tarea #6 [SP1-KEVIN-06]: Arquitectura de Entrada IFighterInput.cs y Azure Kinect SDK
## Sprint 1 (Sep 7 – Sep 20) | Asignado a: @Kevin

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp1-kevin-input-kinect
```

---

### 🎯 2. Explicación Técnica de la Tarea

Crear la interfaz desacoplada de entrada IFighterInput, el emulador de teclado KeyboardFighterInput y preparar el SDK de Azure Kinect.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de arquitectura de software en Unity. Por favor lee este archivo y explícame cómo diseñar la interfaz IFighterInput.cs, cómo implementar KeyboardFighterInput.cs y cómo estructurar la lectura de 32 articulaciones del SDK de Azure Kinect."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [x] Interfaz IFighterInput.cs creada y compilando.
- [x] KeyboardFighterInput.cs permite mover y atacar con teclas.
- [x] Estructura lista para recibir datos de Kinect en Lab los martes.
- [x] Escena de prueba Test_AzureKinect_Body.unity creada.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: arquitectura de entrada ifighterinput.cs y azure kinect sdk (#6)"

# 2. Subir rama a GitHub
git push -u origin feature/sp1-kevin-input-kinect
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #6`.