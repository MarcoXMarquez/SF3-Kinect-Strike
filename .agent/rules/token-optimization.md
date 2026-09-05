# DIRECTRIZ MAESTRA: OPTIMIZACIÓN Y AHORRO DE TOKENS

Esta regla es de cumplimiento estricto para todas las operaciones del agente en el entorno de desarrollo. Su objetivo es minimizar el consumo innecesario de tokens, reducir la latencia de respuesta y preservar la claridad del contexto.

---

## 1. Consulta Previa a Grafos e Índices

- **Prohibido realizar lecturas recursivas masivas o volcados ciegos** de carpetas completas buscando comprender la estructura del proyecto.
- **Protocolo de Exploración**:
  1. Utilizar herramientas de mapeo de relaciones como `graphify` para consultar el grafo o dependencias de la base de código.
  2. Usar `grep_search` o `find_by_name` con patrones precisos (`Pattern`, `Extensions`, `Includes`) para ubicar únicamente las clases, métodos o símbolos relevantes.
  3. No volcar directorios de metadatos o generados automáticamente (`Library/`, `Temp/`, `obj/`, `bin/`, `Logs/`, `node_modules/`, `.git/`).

---

## 2. Compresión de Salidas CLI con RTK (Rust Token Killer)

- Cuando se ejecuten comandos de consola que generen salidas potencialmente extensas, detalladas o ruidosas (como salidas de tests, logs de compilación, estados de control de versiones o búsquedas), **prefijar el comando con `rtk`**:
  - `rtk git status`
  - `rtk git diff`
  - `rtk dotnet test`
  - `rtk dotnet format --verify-no-changes`
  - `rtk npm test`
- `rtk` filtra y comprime automáticamente el ruido, duplicaciones y advertencias repetidas, reduciendo entre un 60% y un 90% el volumen de tokens consumidos en el contexto.

---

## 3. Delimitación Estricta de Lectura de Archivos

- **Prohibido leer archivos enteros (>100 líneas) si solo se necesita inspeccionar o editar una sección**:
  - Utilizar siempre parámetros de rango (`StartLine` y `EndLine`) tras haber localizado la línea exacta mediante `grep_search` o inspección previa.
  - Al editar código, limitar las modificaciones al bloque contiguo indispensable (`replace_file_content` o diff puntual) en lugar de reescribir todo el archivo.

---

## 4. Respuestas Sintéticas y Directas

- Omitir explicaciones redundantes o prefacios extensos.
- Presentar diffs, fragmentos y conclusiones técnicas de forma directa y procesable.
