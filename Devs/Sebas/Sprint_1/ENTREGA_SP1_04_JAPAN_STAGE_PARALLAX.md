# Entrega tecnica - Tarea #4: Escenario Japon con Parallax

## Resumen

Se completo el montaje reutilizable de Suzaku Castle como escenario 2D multicapa. El escenario separa cielo, montanas, castillo, suelo de combate y techo frontal mediante Sorting Layers, aplica desplazamientos de parallax diferentes y proporciona un suelo fisico cuya superficie se encuentra exactamente en `Y=0`.

Tambien se preparo una escena `Sandbox_Sebas` independiente para abrir y comprobar el escenario sin depender del prefab de Ken ni de los archivos de la tarea #3.

## Archivos creados

- `Assets/StreetFighter3_ThirdStrike/Prefabs/Stage_Japan.prefab`: prefab reutilizable del escenario completo.
- `Assets/StreetFighter3_ThirdStrike/Scenes/Sandbox_Sebas.unity`: escena de verificacion con camara ortografica y una instancia de `Stage_Japan`.
- `Assets/StreetFighter3_ThirdStrike/Scripts/Editor/SF3JapanStageBuilder.cs`: herramienta de editor para reconstruir la configuracion del escenario.
- `Assets/StreetFighter3_ThirdStrike/Scripts/Testing/StageParallaxTester.cs`: control de camara exclusivo del Sandbox para comprobar el efecto con las flechas izquierda y derecha.
- `Assets/StreetFighter3_ThirdStrike/Shaders/SF3ChromaKeySprite.shader`: shader para retirar el fondo magenta de las imagenes originales.
- `Assets/StreetFighter3_ThirdStrike/Materials/Stage_ChromaKey.mat`: material compartido por las cinco capas visuales.
- Los archivos `.meta` y metadatos de carpeta asociados, necesarios para conservar GUID y referencias de Unity.

## Archivos modificados

- `ProjectSettings/TagManager.asset`: se agregaron y ordenaron las Sorting Layers `Background_Sky`, `Background_Distant`, `Midground_Temple`, `Floor_Ground`, `Fighters` y `Foreground_Props`.

Los sprites fuente de `Assets/StreetFighter3_ThirdStrike/Stages/Japan_Ryu/` ya estaban configurados en el repositorio con `Pixels Per Unit: 100`, `Filter Mode: Point` y compresion desactivada para la plataforma predeterminada, por lo que no fue necesario duplicar cambios en esos metadatos.

## Implementacion tecnica

El prefab contiene las siguientes capas:

| Objeto | Sorting Layer | Parallax X | Parallax Y |
| --- | --- | ---: | ---: |
| `Sky` | `Background_Sky` | 0.10 | 0.02 |
| `Distant_Mountains` | `Background_Distant` | 0.25 | 0.04 |
| `Suzaku_Castle` | `Midground_Temple` | 0.40 | 0.06 |
| `Battle_Ground` | `Floor_Ground` | 1.00 | 0.00 |
| `Foreground_Roof` | `Foreground_Props` | 0.80 | 0.08 |

`ParallaxBackground` obtiene automaticamente `Camera.main` al comenzar si el campo `Target Camera` no esta asignado. En cada `LateUpdate` calcula el desplazamiento de la camara y mueve cada capa segun sus factores. De esta forma, los elementos lejanos avanzan menos que los cercanos y producen profundidad 2.5D.

En `Sandbox_Sebas`, `StageParallaxTester` mueve la camara horizontalmente con las flechas izquierda y derecha dentro de un rango controlado. Este componente solo pertenece a la escena de prueba y no modifica el comportamiento del prefab reutilizable.

`Ground_Collider` utiliza un `BoxCollider2D` de `12 x 0.2` ubicado en `Y=-0.1`; su borde superior queda en `Y=0`, que es la altura de apoyo requerida para los luchadores.

El shader `SF3/ChromaKeySprite` descarta los pixeles cercanos al magenta con un umbral de `0.22`. Esto permite usar las imagenes originales del escenario sin mostrar sus fondos de color solido.

## Criterios de aceptacion comprobados

- [x] Las seis Sorting Layers estan configuradas en el orden solicitado.
- [x] Ninguna capa de fondo se dibuja por encima de `Fighters`.
- [x] Las cinco capas usan factores de parallax diferentes.
- [x] El suelo tiene un BoxCollider2D cuya superficie esta en `Y=0`.
- [x] El escenario esta guardado como `Stage_Japan.prefab` reutilizable.
- [x] La composicion visual fue ajustada y verificada en `Sandbox_Sebas.unity`.
- [x] El proyecto compila sin errores ni advertencias en los ensamblados C#.

## Conclusion

La tarea #4 esta terminada porque el escenario ya tiene orden visual estable, profundidad por parallax, colision de suelo correcta, tratamiento del fondo magenta y una estructura encapsulada que puede insertarse en otras escenas mediante un solo prefab.

Pull Request: incluir `Closes #4` en la descripcion.
