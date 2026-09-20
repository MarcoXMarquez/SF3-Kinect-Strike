# Entrega tecnica - Tarea #3: Pipeline de animaciones de Ken

## Resumen

Se completo el pipeline de sprites y animaciones de Ken Masters utilizando los recursos existentes en `Assets/StreetFighter3_ThirdStrike/Characters/11_Ken/`. La carpeta se mantiene con el numero real que usa el repositorio (`11_Ken`), aunque la consigna original la menciona como `01_Ken`.

El resultado incluye 74 clips de animacion a 14 FPS, un Animator Controller con los 74 estados, un prefab reutilizable del luchador y una escena Sandbox para revisar visualmente todas las animaciones.

## Archivos creados

- `Assets/StreetFighter3_ThirdStrike/Characters/11_Ken/**/*.anim`: 74 clips distribuidos en las 7 categorias del personaje.
- `Assets/StreetFighter3_ThirdStrike/Characters/11_Ken/Ken_Animator.controller`: controlador con un estado por clip y `idle_stance` como estado inicial.
- `Assets/StreetFighter3_ThirdStrike/Prefabs/Fighter_Ken.prefab`: prefab principal de Ken.
- `Assets/StreetFighter3_ThirdStrike/Prefabs/Ground_Test.prefab`: suelo estatico para probar el prefab sin que caiga por gravedad.
- `Assets/StreetFighter3_ThirdStrike/Scenes/Sandbox_Sebas.unity`: escena aislada de verificacion.
- Los archivos `.meta` asociados, necesarios para conservar GUID y referencias de Unity.

## Archivos modificados

- `Assets/StreetFighter3_ThirdStrike/Characters/11_Ken/01_Movement/jump_forward/*.png.meta`: pivotes horizontales ajustados para conservar la trayectoria visual del salto.
- `Assets/StreetFighter3_ThirdStrike/Characters/11_Ken/01_Movement/jump_backward/*.png.meta`: pivotes horizontales ajustados para conservar la trayectoria visual del salto.
- `Assets/StreetFighter3_ThirdStrike/Scripts/Testing/FighterAnimationTester.cs`: se agrego un modo de revision secuencial para recorrer los 74 estados con teclado.
- `ProjectSettings/TagManager.asset`: se agregaron las capas fisicas `Fighter`, `Hurtbox` y `Hitbox` requeridas por la jerarquia del prefab.

## Implementacion tecnica

Los 74 clips usan `m_SampleRate: 14`, de acuerdo con el ritmo solicitado para los sprites de Street Fighter III. Los ciclos continuos (`idle_stance`, `crouch_idle`, `walk_forward`, `walk_backward` y `stance_lbx`) tienen repeticion habilitada; los ataques, impactos, saltos, intros y victorias se mantienen como acciones de una sola ejecucion.

`Ken_Animator.controller` referencia todos los clips y permite reproducirlos por nombre. El objeto raiz `Fighter_Ken` contiene `Rigidbody2D` y los componentes de combate. Su jerarquia separa `Visuals`, `Pushbox`, `Hurtbox_Root` y `Hitbox_Root`, evitando mezclar presentacion, colision corporal, recepcion de golpes y zonas de ataque.

El componente `FighterAnimationTester` permite activar el modo de revision con `R`, avanzar con `N`, retroceder con `B`, repetir con `Enter` y volver a reposo con `Espacio`. Esto permite comprobar los 74 estados sin crear transiciones temporales en el Animator.

## Criterios de aceptacion comprobados

- [x] Las animaciones estan distribuidas en 7 categorias con nombres descriptivos.
- [x] Se generaron 74 AnimationClips a 14 FPS.
- [x] Idle, caminatas y postura ciclica tienen Loop Time habilitado.
- [x] `Ken_Animator.controller` contiene los 74 estados y abre en `idle_stance`.
- [x] `Fighter_Ken.prefab` posee la jerarquia y componentes requeridos.
- [x] El prefab se reproduce y puede revisarse en `Sandbox_Sebas.unity`.
- [x] El proyecto compila sin errores ni advertencias en los ensamblados C#.

## Conclusion

La tarea #3 esta terminada porque los sprites de Ken ya forman un pipeline utilizable: los clips tienen la velocidad correcta, el Animator los centraliza, el prefab integra la estructura de combate y la escena Sandbox permite verificar cada animacion de manera repetible.

Pull Request: incluir `Closes #3` en la descripcion.
