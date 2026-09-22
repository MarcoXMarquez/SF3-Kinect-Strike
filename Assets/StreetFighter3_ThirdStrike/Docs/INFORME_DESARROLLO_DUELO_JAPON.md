# Informe de desarrollo: escenario Japon y duelo Ken contra Ryu

Fecha: 2026-09-22

Rama: `feature/sp1-sebas-japan-stage`

Commit de implementacion: `a55f8e8ce` (`feat: add Ken vs Ryu local duel to Japan stage`).

## 1. Objetivo y alcance

Integrar un duelo local de dos jugadores en el escenario Japon modificado por
Sebas, con Ken frente a Ryu. Se implementaron movimiento, salto, agacharse,
bloqueo, cuatro ataques basicos, deteccion de impactos, vida y resultado de ronda.

Este informe describe esta ampliacion. No certifica por si solo la aprobacion
de las tareas anteriores del sprint ni una implementacion completa de las reglas
originales de Street Fighter III. Es un prototipo jugable de combate local.

## 2. Revision y conservacion del escenario

Antes de integrar el duelo se revisaron los cambios locales del usuario en
`Scenes/Sandbox_Sebas.unity`:

- Retiro de las capas Sky, Suzaku_Castle y Foreground_Roof de la instancia.
- Reescalado y desplazamiento de las montanas distantes.
- Ajustes de escala, posicion y orden de dibujo del piso.
- Incorporacion de `Battle_Ground (1)` con el sprite del templo.
- Referencias de parallax anuladas para las capas retiradas.

Estos cambios de composicion pertenecen a Sebas y se conservaron en el commit.
La integracion nueva agrega `JapanDuel` a Main Camera. El prefab fuente
`Prefabs/Stage_Japan.prefab` no se modifico.

La revision visual detecto que los pies quedaban por encima de las tablas.
Durante Play, `JapanDuel` desplaza el collider `Ground_Collider` para que su cara
superior quede en Y=-0.32. Los luchadores usan esa misma altura como referencia.
El ajuste solo ocurre en ejecucion y esta calibrado para esta composicion.

El componente de parallax existente se conserva. Durante el duelo se desactiva
`StageParallaxTester` para que las flechas controlen a Ryu y no a la camara.
No se agrego seguimiento automatico de camara: con la camara quieta no hay
desplazamiento de parallax visible.

## 3. Archivos entregados

Las rutas de esta tabla son relativas a `Assets/StreetFighter3_ThirdStrike/`.

| Archivo | Tipo de cambio | Responsabilidad |
| --- | --- | --- |
| `Scenes/Sandbox_Sebas.unity` | Modificado | Conserva la composicion de Sebas e incorpora el controlador del duelo |
| `Scripts/Combat/JapanDuel.cs` | Nuevo | Carga del catalogo, creacion de luchadores, ronda, marcador, KO y revancha |
| `Scripts/Combat/DuelFighter.cs` | Nuevo | Teclado, fisica, estados, sprites, cajas y recepcion de impactos |
| `Scripts/Combat/DuelRoster.cs` | Nuevo | ScriptableObject con secuencias de sprites para ambos personajes |
| `Resources/JapanDuelRoster.asset` | Nuevo | Catalogo serializado de 42 secuencias y 486 referencias de sprites |
| `Scripts/Editor/JapanDuelValidation.cs` | Nuevo | Validacion repetible desde el menu del editor |
| `Docs/DUELO_KEN_RYU.md` | Nuevo | Guia de uso, controles, implementacion y limitaciones |
| `Docs/INFORME_DESARROLLO_DUELO_JAPON.md` | Nuevo | Este informe de entrega tecnica |

Se incluyen los archivos `.meta` correspondientes y el `.meta` de Resources,
necesarios para conservar las referencias de Unity al compartir el proyecto.

Se reutiliza `FighterHurtbox` para recibir impactos. No se modifican los sistemas
anteriores `FighterHitbox` ni `FighterCombatColliders`; el nuevo duelo consulta
los solapamientos directamente para controlar que un ataque no reste vida
varias veces al tocar distintas zonas del mismo rival.

## 4. Creacion y estados de los personajes

Al iniciar Play, `JapanDuel` carga el catalogo desde Resources y crea
`Fighter_Ken` y `Fighter_Ryu` en la escena. En modo edicion estos objetos no
estan presentes. Cada uno obtiene un Rigidbody2D, una pushbox, un objeto
Visuals con SpriteRenderer, tres hurtboxes y una hitbox de ataque.

Ambos empiezan con 100 de vida, en X=-1.35 y X=1.35. La preparacion de ronda
dura dos segundos. Cuando no estan ejecutando un ataque se orientan hacia el
rival. Adelante y atras se interpretan respecto a esa orientacion.

Se implementaron los estados de reposo, caminar, salto, agacharse, bloqueo,
ataque, reaccion al impacto y final de ronda. No se utiliza un Animator nuevo:
el controlador selecciona las secuencias del catalogo y actualiza el sprite.

La fisica utiliza Unity Physics2D, gravedad de escala 3, rotacion bloqueada,
interpolacion y deteccion continua. El desplazamiento horizontal es de 1.7
unidades por segundo y el impulso vertical de salto es de 7.5. Se limita el
recorrido horizontal a X entre -3.7 y 3.7.

## 5. Animaciones y referencias

Se conectaron 21 secuencias por personaje: reposo, caminar adelante/atras,
salto, agacharse, cuatro ataques de pie, sus variantes agachadas y aereas,
bloqueo, reaccion al golpe, victoria y derrota por timeout.

El catalogo contiene 230 referencias de Ken y 256 de Ryu, ordenadas por el
numero del archivo de cada fotograma. No son 486 animaciones nuevas ni nuevos
dibujos: son referencias a sprites ya presentes en el proyecto.

Durante la integracion se corrigieron las referencias de subassets teniendo
en cuenta el modo de importacion del sprite. No se alteraron las imagenes,
sus pivotes, sus ajustes de importacion ni los clips anteriores.

Idle y caminar se repiten; las otras secuencias mantienen su ultimo fotograma
cuando corresponde. Los ataques recorren la secuencia completa en 0.55 segundos.
El salto selecciona fotogramas segun su velocidad vertical. La colocacion
visual compensa los bounds del sprite sin reescribir su pivot.

## 6. Hitboxes, hurtboxes y dano

Cada personaje tiene tres zonas vulnerables: cabeza, torso y piernas.
La altura del conjunto baja de 1 a 0.6 unidades al agacharse, y se aplica un
desplazamiento al atacar. La pushbox tambien reduce su altura.

La hitbox de ataque cambia entre puno y patada en tamano, altura y alcance,
se refleja con la orientacion y extiende su alcance durante el ataque.
Solo esta activa entre 0.13 y 0.28 segundos; permanece desactivada durante
preparacion y recuperacion, despues de un impacto o al terminar la ronda.

La consulta de solapamientos solo acepta hurtboxes del oponente. Un indicador
de impacto consumido limita el dano a una vez por ataque. Los golpes ligeros
restan 7 puntos y los fuertes 12; la vida nunca baja de cero.

El bloqueo requiere estar en suelo y orientado hacia el atacante. Un bloqueo
valido evita todo el dano y aplica una breve reaccion. No se implemento la
distincion entre bloqueo alto y bajo. El color del sprite cambia brevemente
para distinguir bloqueo e impacto.

Las cajas son dinamicas por postura y fase, no cajas dibujadas individualmente
para cada fotograma ni una reproduccion pixel-perfect del juego original.
Pueden inspeccionarse seleccionando al luchador con Gizmos activados: zonas
vulnerables verdes y hitbox activa roja.

## 7. Interfaz y resultado

Se agregaron barras de vida, nombres y valores numericos para ambos jugadores,
con fondos oscuros para mantener legibilidad sobre el escenario. La interfaz
ajusta su escala usando una referencia de 960x540.

Al llegar un luchador a cero de vida, se desactivan los ataques y hurtboxes de
ambos. El vencedor reproduce `victory_pose_1`; el perdedor, `defeat_timeout`.
Se muestra el ganador y un boton Revancha. Enter tambien reinicia la ronda,
restaura vida y posiciones y vuelve a la preparacion inicial.

## 8. Controles

| Accion | Ken | Ryu |
| --- | --- | --- |
| Moverse izquierda / derecha | A / D | Flechas izquierda / derecha |
| Saltar | W | Flecha arriba |
| Agacharse | S | Flecha abajo |
| Bloquear manteniendo la tecla | G | Shift derecho |
| Puno izquierdo / derecho | F / H | Numpad 1 / 2 o fila superior 7 / 8 |
| Patada izquierda / derecha | V / B | Numpad 4 / 5 o fila superior 9 / 0 |
| Reiniciar ronda | Enter | Enter |

Los nombres izquierdo/derecho son asignaciones de control sobre las secuencias
existentes light/heavy; no garantizan una extremidad anatomica distinta en
cada sprite. No se agregaron especiales, proyectiles, supers ni agarres.

## 9. Verificacion realizada

- Compilacion de `Assembly-CSharp.csproj` y `Assembly-CSharp-Editor.csproj`
  completada sin errores ni advertencias de compilacion.
- Ejecucion real en Unity para comprobar que aparecen Ken y Ryu, su orientacion,
  las barras y la alineacion de los pies con el suelo.
- Ejecucion de `SF3 Tools > Validate Local Duel`, con resultado
  `DUEL VALIDATION PASS` despues de los ajustes finales.
- La validacion comprueba las 486 referencias, ataques fuera de alcance,
  dano de los cuatro golpes, un unico impacto por ataque, ausencia de
  autogolpes, bloqueo frontal, ataque de Ryu orientado a la izquierda,
  hitboxes inactivas en preparacion/recuperacion, reduccion de la pushbox
  al agacharse, KO, seleccion de victoria y restauracion de vida.

La validacion llama a la logica de combate en la escena en Play y restaura
la ronda al terminar. No es una prueba exhaustiva de todas las combinaciones
de teclado ni de todos los fotogramas y contactos posibles. Se debe seguir
probando con dos personas, especialmente combinaciones simultaneas: el
ghosting depende del teclado. Durante la automatizacion Unity tambien mostro
un mensaje de Raw Input sobre un controlador no valido; no se contabilizo como
error de compilacion ni se verifico su origen.

## 10. Limites y trabajo no incluido

- No hay IA, red, Kinect ni control por mando en este duelo.
- No se modifico ni completo la maquina de estados de otras ramas del equipo.
- No se crearon nuevos clips `.anim` ni se rehicieron las 74 animaciones previas.
- No hay balance competitivo, cancelaciones, combos, knockback ni frame data
  individual por ataque. Los cuatro golpes comparten la duracion y ventana activa.
- La altura de suelo y los limites horizontales estan calibrados para este sandbox.
- La validacion de victoria comprueba el estado elegido, no todas las poses visuales.

## 11. Entrega Git

La implementacion y la guia de uso se subieron a
`origin/feature/sp1-sebas-japan-stage` mediante el commit `a55f8e8ce`.
Este informe y su `.meta` se entregan en un segundo commit de documentacion.
No se hizo merge a main ni se uso force push.

Se dejaron fuera los cambios locales anteriores y ajenos a esta ampliacion:
`Assets/Scenes/SampleScene.unity`, configuraciones locales del proyecto,
`.vsconfig` y el `.meta` pendiente del manual de Git. Permanecen en la copia
local; no se eliminaron ni se revirtieron.
