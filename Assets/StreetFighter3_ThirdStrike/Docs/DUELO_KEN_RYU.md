# Duelo local: Ken contra Ryu

## Uso

Abrir `Assets/StreetFighter3_ThirdStrike/Scenes/Sandbox_Sebas.unity`, pulsar Play
y hacer clic en Game. Los luchadores se crean al iniciar la escena; no aparecen
en modo edicion. Es un duelo para dos personas en el mismo teclado, sin IA.

| Accion | Ken | Ryu |
| --- | --- | --- |
| Izquierda / derecha | A / D | Flechas izquierda / derecha |
| Saltar | W | Flecha arriba |
| Agacharse | S | Flecha abajo |
| Bloquear (mantener) | G | Shift derecho |
| Puno izquierdo | F | Numpad 1 o 7 superior |
| Puno derecho | H | Numpad 2 o 8 superior |
| Patada izquierda | V | Numpad 4 o 9 superior |
| Patada derecha | B | Numpad 5 o 0 superior |
| Reiniciar ronda | Enter | Enter |

Idle es automatico. Adelante/atras cambia segun el lado del rival. Al llegar a
cero de vida se bloquean los ataques y el ganador reproduce `victory_pose_1`.
El boton Revancha inicia otra ronda. No hay especiales, proyectiles ni supers.

Los nombres izquierdo/derecho son asignaciones de control: se reutilizan los
sprites existentes light/heavy punch y light/heavy kick; no se han dibujado
animaciones nuevas que garanticen una extremidad anatomica concreta.

## Implementacion

- `Scripts/Combat/JapanDuel.cs`: crea ambos luchadores, ronda, vida en pantalla,
  resultado y revancha. Ajusta el collider del suelo a Y=-0.32 solo en ejecucion
  para alinearlo con las tablas de la composicion actual. Desactiva el tester
  de camara con flechas para evitar conflictos con los controles de Ryu.
- `Scripts/Combat/DuelFighter.cs`: movimiento con Rigidbody2D, orientacion,
  animacion por sprites, bloqueo frontal y estados de golpe/recuperacion.
  Los golpes recorren su secuencia completa durante 0.55 segundos.
- Tres hurtboxes por luchador: cabeza, torso y piernas. Cambian de altura al
  agacharse y se desplazan al atacar. Una hitbox de ataque cambia de alcance,
  altura y direccion, activa solo entre 0.13 y 0.28 segundos del golpe.
- Physics2D consulta los solapamientos; solo acepta al oponente, con un impacto
  por ataque aunque toque varias hurtboxes. Dano: 7 ligero y 12 fuerte.
  Bloqueo frontal en suelo: cero dano. No hay distincion alto/bajo de guardia.
- Las cajas son aproximaciones por postura y fase, no trazados pixel a pixel
  ni cajas editadas individualmente para cada fotograma del juego original.
- `Scripts/Combat/DuelRoster.cs` y `Resources/JapanDuelRoster.asset`: 21 secuencias
  por personaje, 230 referencias de sprites de Ken y 256 de Ryu. Incluyen las
  variantes agachadas/aereas de los cuatro golpes y reacciones/victoria.
- `Sandbox_Sebas.unity`: se agrega JapanDuel a Main Camera. Se conservan los
  cambios del usuario en montanas, templo y piso. No se modifican las imagenes,
  sus pivotes, los clips existentes ni el prefab Stage_Japan.

## Comprobacion

En Play: `SF3 Tools > Validate Local Duel`. Reinicia la ronda al terminar.
Verifica referencias de sprites, alcance, cuatro ataques, un impacto por golpe,
ausencia de autogolpes, bloqueo frontal, ataque invertido de Ryu, ventanas
inactivas, dimensiones al agacharse, KO, victoria y restauracion de vida.
El resultado aparece en Console como `DUEL VALIDATION PASS` o una excepcion.

La prueba no sustituye la revision manual de todas las poses y combinaciones
de teclas simultaneas. Algunos teclados limitan teclas simultaneas (ghosting).
