# Neon Siege: la última señal

## Entrega

Minijuego 2D para Unity 6000.3.23f1 y Windows, desarrollado en la rama
`minijuego/lanzamiento-de-proyectil`.

- Escena: `Assets/StreetFighter3_ThirdStrike/Minigames/NeonSiege/NeonSiege.unity`.
- Ejecutable de esta revisión: `Builds/NeonSiege_Arcade/NeonSiege.exe`.
- El ejecutable necesita su carpeta de datos y los DLL incluidos en la entrega.
- Constructor: `SF3 Tools > Neon Siege > Build Scene and Assets`.
- Compilación: `SF3 Tools > Neon Siege > Build Windows Player`.

## Misión e historia

En Hong Kong, Urien controla los repetidores de comunicación. Yun y Yang evacuan
a los vecinos mientras Ryu despeja las azoteas. Remy protege los accesos desde
ascensores de carga; Urien defiende el transmisor final. La campaña tiene cinco
asaltos con una introducción narrativa y un objetivo concreto en cada uno.

| Asalto | Desafío | Energía | Tiempo |
| --- | --- | --- | --- |
| La última señal | Tres enemigos a diferentes alturas | 6 | 55 s |
| Cazadores de neón | Dos enemigos móviles, dos impactos cada uno | 7 | 65 s |
| Línea de ruptura | Cobertura de acero y enemigos de dos y tres impactos | 9 | 80 s |
| El pulso de Aegis | Escudos periódicos y contraataques | 10 | 80 s |
| Amanecer sobre Hong Kong | Dos enlaces, Urien y contraataques más frecuentes | 15 | 95 s |

Cada asalto empieza con cuatro puntos de integridad. Se pierde por tiempo,
energía agotada sin proyectiles pendientes o integridad cero. Reintentar restaura
la puntuación anterior al asalto: no permite acumular puntos repitiendo un sector.

## Controles y apuntado

| Acción | Control |
| --- | --- |
| Señalar un punto de llegada | Ratón |
| Disparar | Clic izquierdo o Espacio |
| Potencia | Rueda, W/S o deslizador |
| Ángulo manual | A/D |
| Arco bajo/alto | Tab o selector inferior |
| Foco | F o botón Foco |
| Pausa | Escape, P o botón II |

El ratón calcula un arco balístico hacia el punto señalado, compensando la gravedad.
Para un enemigo móvil sigue siendo necesario anticipar su posición. La potencia
se limita a 9–18 m/s; cada asalto comienza en 13.8 m/s. Si el punto está fuera de
alcance, la interfaz avisa. Los arcos altos pueden salir de cámara y regresar.

Se sustituyó la lectura suavizada de los ejes del ratón por sus coordenadas reales.
La mira se actualiza cada fotograma. El suavizado angular es visual: al hacer clic,
`FireAimedShot` usa inmediatamente el ángulo solicitado, evitando disparar con el
ángulo anterior después de un movimiento rápido.

El Foco calcula una intercepción futura y tiene dos usos en los primeros asaltos
y uno en los restantes. No guía el proyectil después del lanzamiento.

## Corrección del nivel 3

La validación original completaba la campaña, pero no aislaba cada blanco en
diferentes fases ni comprobaba el apuntado manual. La revisión encontró:

1. Un tiro inicial que no sugería la potencia necesaria para el blanco lejano.
2. Una mira que cambiaba el ángulo sin compensar la gravedad hacia el cursor.
3. Un límite superior de cámara que eliminaba proyectiles todavía en vuelo,
   haciendo fallar algunos arcos altos.

Se ajustaron la cobertura y las posiciones de los blancos, se corrigió la mira
y se permitió continuar el vuelo sobre la cámara. La predicción y la simulación
comparten ahora el límite superior de seguridad de 18 unidades y un horizonte
de predicción de 3.8 segundos. La vida máxima del proyectil sigue siendo 4.5 s.

La prueba específica elimina temporalmente al otro enemigo y busca rutas mediante
el mismo cálculo de arco que usa el ratón. Comprueba ambos blancos en ocho fases
cada uno. Las 16 muestras pasaron con potencia 13.8 m/s; algunas posiciones del
blanco cercano requieren el arco alto, de aproximadamente 75–76 grados.

Estos son muestreos de alcanzabilidad, no una demostración de todas las fases
continuas posibles. La campaña también se reproduce con proyectiles físicos.

## Física predictiva

Unity Physics2D simula los proyectiles con gravedad -9.81 m/s², paso fijo 0.02 s
y amortiguación cero. La predicción reproduce Euler semiimplícito:

```text
v[n+1] = v[n] + g * dt
p[n+1] = p[n] + v[n+1] * dt
```

Los enemigos siguen movimientos sinusoidales conocidos. Para cada segmento de
vuelo se comprueba el contacto relativo con la posición futura del enemigo.
El escudo se consulta en el momento previsto de impacto. Las barreras detienen
el recorrido y las esferas hostiles existentes se proyectan con su velocidad
rectilínea. No se anticipan esferas que todavía no han sido disparadas.

El cálculo de arco busca tiempos de vuelo cuya velocidad inicial coincida con
la potencia elegida, compensando el paso discreto de gravedad. El selector permite
usar la solución baja o alta. El Foco añade la predicción del movimiento enemigo.

## Dificultad y puntuación

Se redujeron los recursos de las primeras versiones, se aceleraron los enemigos
del segundo asalto y el blanco lejano del tercero necesita tres impactos. Desde
el cuarto asalto hay contraataques con una animación de aviso previa de 0.7 s.
El intervalo es de 10 s en el cuarto y 6.2 s en el final.

Los escudos se representan como paneles eléctricos azules únicamente cuando están
cerrados. Cuando desaparecen, el enemigo es vulnerable. Los personajes están sobre
plataformas metálicas con guías y marcas de seguridad; no están dentro de burbujas.

- Impacto: 150 puntos más 40 por nivel de racha, hasta cinco niveles.
- Eliminar un enemigo: 150 puntos adicionales.
- Intercepción de una esfera: 200 puntos.
- Bonificación de asalto: energía x 60, segundos x 8 e integridad x 100.
- Un fallo o bloqueo rompe la racha.
- Foco descuenta hasta 75 puntos ganados en ese asalto.
- Rango S: todos los tiros acertados sin Foco; A: precisión mínima de 65%; B: victoria.
- El récord se guarda al completar la campaña; el volumen también se conserva.

## Dirección visual y recursos

Se mantiene el escenario Hong Kong y los sprites, música, voces e impactos del
repositorio. Los enemigos utilizan animaciones de Remy y Urien, incluidas reacciones
al impacto y preparación del contraataque. Los proyectiles usan las secuencias de
energía azul y violeta comprobadas visualmente, no las carpetas mal nombradas que
contenían poses de personajes.

La interfaz arcade se separó en `SiegeArcadeHUD.cs`: barras de vida, titulares
inclinados con contorno, botones angulares y paleta amarilla, roja y azul. Los
contadores muestran valores sin ceros de relleno. Se corrigieron tildes, ñ,
puntuación y redacción narrativa.

Se incorporaron Bangers, Barlow Condensed Black Italic y Rajdhani SemiBold desde
el repositorio oficial de Google Fonts. Sus licencias OFL están en `Fonts/` y
se incluyen en el paquete de Windows. La prueba comprueba los glifos ñ y á.

Fuentes:
- https://github.com/google/fonts/tree/main/ofl/bangers
- https://github.com/google/fonts/tree/main/ofl/barlowcondensed
- https://github.com/google/fonts/tree/main/ofl/rajdhani

La interfaz usa una referencia 1280x720, con bandas para conservar 16:9 en otras
ventanas. El constructor genera recortes de sprites como subassets propios sin
reescribir las imágenes, pivotes ni importadores originales. Se omiten fotogramas
vacíos y se usa el material de chroma key existente.

## Archivos principales

| Archivo | Responsabilidad |
| --- | --- |
| `NeonSiegeGame.cs` | Campaña, entrada, estados, puntuación, predicción y Foco |
| `SiegeArcadeHUD.cs` | Presentación arcade y textos |
| `SiegeBallistics.cs` | Integración, soluciones de arco y contacto relativo |
| `SiegeTarget.cs` | Movimiento, vida, escudos, plataformas y animación enemiga |
| `SiegeProjectile.cs` | Cuerpo físico, contactos, intercepciones y recuperación |
| `SiegeActor.cs` | Reproducción de secuencias |
| `NeonSiegeAssets.cs/.asset` | Catálogo de sprites, audio, material y fuentes |
| `Editor/NeonSiegeBuilder.cs` | Generación de escena, catálogo y Windows |
| `Editor/NeonSiegeAudit.cs` | Pruebas de física, apuntado, nivel 3 y campaña |
| `SiegeEvidenceCapture.cs` | Capturas de demostración con argumento explícito |
| `VALIDACION.json` | Resultado de la auditoría reproducible |

## Verificación y límites

### Ajustes finales de entrega

- El quinto asalto cierra la campaña con desenlace, rango y puntuación final.
  Se eliminó el reinicio desde la victoria y se añadió SALIR DEL JUEGO: cierra
  Windows o detiene Play en el editor. El estado final bloquea reintento,
  disparos y daño; los proyectiles restantes se retiran al completar un asalto.
- Remy y Urien miran hacia Ryu mediante la escala horizontal del objeto visual.
  El shader chroma key compartido no implementa `SpriteRenderer.flipX`; la escala
  garantiza el reflejo real sin modificar ese shader, imágenes ni importadores.
- Nombres y barras enemigas se anclan al límite superior del SpriteRenderer
  más un margen de 0.28 unidades. Siguen las animaciones sin tapar las cabezas.
- La auditoría añade comprobaciones de orientación, separación de etiquetas y
  estabilidad del final. La captura `06_campaign_complete.png` documenta el cierre.

La auditoría se ejecuta desde `SF3 Tools > Neon Siege > Validate Campaign in Play`.
Comprueba pausa, derrota, reintento, bloqueo de tiros simultáneos, referencias de
sprites, fuentes españolas y apuntado al cursor. Compara 85 pasos de predicción
con un Rigidbody2D en una escena física aislada: error medido 0 unidades en esa
ejecución. Después completa las cinco misiones con enemigos móviles y disparos
reales. El detalle y las 16 rutas del nivel 3 están en `VALIDACION.json`.

El controlador de prueba conoce el movimiento enemigo. Su resultado demuestra
alcanzabilidad, no una medición de dificultad humana. Los movimientos impredecibles,
viento, rebotes y nuevas esferas futuras no forman parte del predictor.

La ejecución final completó los cinco asaltos con 26 impactos en 27 disparos y
tres puntos de integridad restantes. La comprobación de ratón en el ejecutable
acertó dos blancos estáticos consecutivos mediante clic directo, con puntuaciones
de 340 y 720. Tab cambió el arco calculado de 25.5° a 73.6° en esa prueba. Se
revisó la interfaz a 1280x720 y en una ventana de aproximadamente 1024x576.

Las capturas del ejecutable se regeneran con `--neon-siege-evidence` en una ventana
renderizada. Ese modo recorre escenas y se cierra solo. Sin el argumento, la partida
es normal. La compilación existente puede emitir advertencias de APIs obsoletas
en KinectPoseMatcher, que no pertenece al minijuego.
