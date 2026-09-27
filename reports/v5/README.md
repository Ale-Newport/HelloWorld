# Correcciones del mundo guardado

Se parte de la copia exacta `backups/user_world_before_four_fixes_20260927_103401/`, también registrada en el commit `410fdbd`.

- Circuito World2: escala 1:1, posición Three.js (-194, 0.15, 173), giro del usuario conservado. Huella aproximada 167 × 152 m. Terreno SO ampliado y editable; acceso conectado con South Coast sin invasión del asfalto original.
- Loop: entradas en ambos sentidos y asistencia activada con aceleración normal. Se conserva el cuerpo físico; sin teletransportes. Frenar o encontrar un obstáculo real libera la asistencia.
- Fuente: dos vasos huecos de piedra, detalles de bronce, mosaico, ocho cascadas animadas, ondas y cuatro luces nocturnas. La posición y escala originales se conservan.
- Estudios y experiencia: el modelo fuente y la geometría generada comparten marco, incluido el cálculo de proximidad en Drive. Mover, girar, escalar o renombrar el modelo no separa las líneas.

El mapa y las cámaras abarcan la tierra añadida. El minimapa reutiliza una imagen estática y dibuja contornos de costa en vez de decenas de miles de triángulos por fotograma. La exportación omite animaciones de objetos borrados para no producir referencias GLTF inexistentes.

## Evidencia

- `circuit-fit-tests.json`: acceso con vehículo real, ocho checkpoints, cuenta atrás, vuelta y registro; cero solapes.
- `saved-loop-tests.json` y `LOOP.md`: ambos sentidos, cuatro niveles de aceleración, contacto de ruedas, salida y obstáculo sólido.
- `fountain-tests.json`: restauración, animación, colisiones y aislamiento de la migración.
- `../v4/career-frame-tests.json`: transformaciones, definiciones, serialización, Drive y Stop.
- `minimap-tests.json`: costa, huecos, encuadre y reducción de complejidad.
- `terrain-persistence-tests.json`: dos ciclos de guardado y recarga sin duplicar vértices de recortes.
- `preservation-tests.json`: comparación del guardado final con las modificaciones del usuario.
- `native-roundtrip.json`: jerarquía Blender, texturas incorporadas y encuadre de toda la isla.

Vista real del resultado: `world-aerial.png`. Fuente ampliada: `fountain-studio.png`. Arranque del coche en el circuito: `circuit-drive.png`.

No se modificó Portfolio. La comprobación de sus 3.218 archivos confirma la identidad con el inventario previo. Los juegos y controles se ejecutan en el navegador; el archivo Blender conserva geometría, materiales, animaciones y proxies físicos editables.
