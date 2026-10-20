# Neon Siege: la última señal

Versión Arcade. Ryu contra los enlaces de Urien en Hong Kong: cinco asaltos,
enemigos móviles, barreras, escudos temporales y contraataques.

## Abrir

Ejecuta `NeonSiege.exe` dentro de la carpeta completa de esta entrega.
En Unity 6000.3.23f1, abre `NeonSiege.unity` y pulsa Play.

## Controles

- Ratón: señalar un punto de llegada. Clic izquierdo o Espacio: disparar.
- Rueda, W/S o deslizador: ajustar la potencia.
- A/D: ajustar manualmente el ángulo.
- Tab o selector BAJO/ALTO: cambiar de arco.
- F o botón Foco: calcular una intercepción. Dos usos al principio; uno desde el asalto 3.
- P, Escape o botón II: pausa.

La mira compensa la gravedad hacia el punto señalado. Para un enemigo móvil,
apunta por delante de su recorrido. Si aparece “Aumenta la potencia”, el punto
queda fuera del alcance de ese tiro.

## Nivel 3

Empieza con potencia 13.8 m/s. El enemigo lejano puede alcanzarse con un arco
bajo; el cercano, en ciertas posiciones, exige un arco alto para superar la
barrera. El selector ALTO o Tab permite esa trayectoria. Un proyectil que sale
por arriba de la cámara continúa volando y puede regresar al campo.

Los personajes están en plataformas metálicas. Un panel azul delante del enemigo
significa que Aegis está activo: espera a que desaparezca para golpear. Desde
el cuarto asalto los enemigos responden al fuego; intercepta sus esferas para
proteger la evacuación.

Reintentar restaura los puntos previos al asalto. El rango S exige acertar todos
los tiros sin usar Foco. El récord se guarda al terminar la campaña.

Al superar el quinto asalto termina el juego: se muestra el desenlace, el rango
y la puntuación final. No se reinicia la campaña. Pulsa SALIR DEL JUEGO para
cerrar el ejecutable (en Unity, detiene Play).

## Documentación

- `INFORME_TECNICO.md`: implementación, cambios de esta revisión y límites.
- `VALIDACION.json`: pruebas de campaña y 16 casos de alcanzabilidad del nivel 3.
- `Evidence/`: capturas obtenidas del ejecutable.
- `Licencias/`: licencias de las fuentes abiertas incorporadas.

El código y la escena están en
`Assets/StreetFighter3_ThirdStrike/Minigames/NeonSiege/`.
