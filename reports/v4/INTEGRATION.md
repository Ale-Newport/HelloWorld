# Integración y aceptación · World Studio 04

La iteración conserva el motor, las actividades y la base anterior. El mapa v4 se ensambla mediante `preview/world-map.js`, assets reutilizables y carreteras derivadas de curvas. La copia anterior completa está en `backups/world_before_map_and_editor_upgrade_20260927/`, incluido `AlejandroWorld_before_upgrade.blend`.

Este informe distingue pruebas automatizadas, observación de navegador y comprobación nativa. Las pruebas automatizadas se ejecutan sobre los módulos entregados; `tests/v4-world.mjs` construye el mapa real, sus colliders, el vehículo y los once controladores World2 colocados en él. No sustituye el mapa por un suelo de ensayo. El canvas de texto de Node es inerte; el navegador verifica materiales, jerarquía, miniaturas y composición.

## Matriz de los quince tests solicitados

| Test del encargo | Evidencia verificable | Estado |
|---|---|---|
| 1. Abrir árbol, editar child/material, guardar y añadir | `asset-studio-tests.json`: edición aislada y guardado de partes/material; navegador de integración | PASS · navegador: `browser-asset-roundtrip.json`, `asset-studio.png` |
| 2. Save As New conserva ambos assets | `asset-studio-tests.json`: variante independiente, source e instancia conservados | PASS · navegador: `browser-asset-roundtrip.json`, `asset-studio.png` |
| 3. Editar curva mueve líneas blancas | `roads-tests.json` y `road-curve-edited.png`: punto X −28→−35 y Undo; superficie y marcas sincronizadas | PASS |
| 4. Editar circuito mueve bordillos | `roads-tests.json` y `race-curve-edited.png`: punto X −23→−18 y Undo; bordillo acoplado por metros | PASS |
| 5. Curva extrema sin asfalto duplicado y aviso | `roads-tests.json`: comparación de área/unión con GEOS independiente y diagnósticos | PASS |
| 6. Playa → agua → tierra | `world-physics-tests.json`, ruta `beach-route.json` sobre la malla costera real | PASS |
| 7. Coche inmóvil sin input | `vehicle-tests.json`: plano y pendiente 0,57°; `world-physics-tests.json`: spawn real | PASS |
| 8. SPACE sencillo = freno | `vehicle-tests.json`: buffer, tap, hold y liberación | PASS |
| 9. SPACE SPACE coche → avión | Buffer automatizado y observación del teclado real en navegador | PASS |
| 10. Vuelo alrededor de isla | `world-physics-tests.json`: vuelo continuo por 8 puntos, 298 × 225 m alrededor de isla; `island-flight-route.json`; navegador verifica ambos modos | PASS |
| 11. Avión → coche cae y aterriza | `vehicle-tests.json`: caída real desde 29,5 m; navegador observa transición y aterrizaje | PASS |
| 12. Transformaciones repetidas sin duplicación | `vehicle-tests.json`: 24 cambios; `world-physics-tests.json`: cambios con todos los cuerpos del mapa | PASS |
| 13. Conducción en puentes | `world-physics-tests.json`: cruces del puente rojo y de madera con contactos reales | PASS |
| 14. Entrada al hielo sin puente | `world-physics-tests.json`: trayectoria desde suelo normal y detección de collider ice | PASS |
| 15. Vista aérea respeta blueprint | Posiciones de las 23 zonas en `world-map.js`; `world-top-browser.png`, `world-overview-browser.png` y `blueprint-comparison.png` | PASS · distribución comparada |

Los informes JSON registran cada comprobación individual y su evidencia. Un resultado anterior fallido no se interpreta como aceptación: se corrige y se repite la suite afectada antes del cierre.

## Arquitectura comprobada

- **Definición frente a instancia:** los cambios de source conservan posición, rotación y escala de copias colocadas. Save As New y Edit Instance permanecen independientes. Serialización y recarga conservan edición de jerarquía.
- **Actividades:** diez regresiones World2 verifican bolos, carrera, proyectos, cronología, letras, lugares/social, tierra nueva, hoyo físico y copias independientes. La edición de un asset funcional conserva la lógica y sincroniza cambios de cuerpo/collider y reset.
- **Carreteras:** unión geométrica antes de triangular; marcas y bordillos siguen una curva y distancia común. Conform to terrain comparte superficie visual y física. Los helpers de debug viven fuera de la raíz exportable.
- **Agua:** mar y física usan `SEA_LEVEL = -0.35`; el terreno principal usa `MAIN_HEIGHT = 0.15`. Las playas continúan bajo el agua. La frenada por agua deriva del motor World2 y la recuperación solo se aplica a profundidad sostenida.
- **Vehículos:** un chasis Rapier, un controlador activo, una cámara; el raycast controller no se actualiza en modo avión. El modelo Corsair tiene materiales incorporados y no necesita rutas externas.
- **Persistencia:** definiciones y mundo se guardan por separado mediante escritura atómica. La exportación GLB conserva recursos y datos; las interacciones requieren los módulos web de HelloWorld. El importador Blender v4 preserva las partes y sus padres, y genera proxies físicos independientes en una colección oculta.

## Diagnóstico del movimiento sin input

El coche original no se desplazó en suelo matemáticamente plano. En una pendiente de 0,57° recorrió 0,328 m en 25 segundos, con throttle exactamente cero. El origen era el pequeño componente tangencial de la suspensión por rayos integrada a 1/60 frente a gravedad a 1/30. El estado de parking exige cuatro contactos estáticos, normales casi horizontales, movimiento bajo, coche erguido, suspensión normal y ausencia de acelerador. Una fricción estática limitada neutraliza ese residuo. No se aplica sobre hielo o pendientes fuertes; se libera inmediatamente con intención o impacto. Véase `VEHICLES.md`.

La prueba con orientaciones de reposo no alineadas a los ejes detectó también una oscilación de yaw de la fricción lateral del raycast: pequeños errores numéricos crecían en impulsos alternos de ±1,1 rad/s. El mismo estado de parking aplica ahora un momento limitado de fricción estática, sin fijar rotación ni desactivar suspensión. Cinco orientaciones permanecen inmóviles; ruido acumulado de orientación <0,00004 rad. En el spawn real, yaw = 0 y el asentamiento vertical restante es 0,144 mm.

## Conflictos de input revisados

SPACE se elimina únicamente de la definición de salto que recibe el editor v4, sin modificar el código fuente portado. `VehicleInput` posee el buffer de 300 ms y evita repeat. En vuelo, las acciones de conducción y minijuegos se filtran; E pasa a cabeceo y no abre a la vez un proyecto. Los controles de cámara se mantienen. Al volver a coche se restauran las categorías de conducción/cámara. El teclado y los listeners se destruyen al salir de Drive.

Los tests de paridad v3 siguen mostrando los bindings originales de la fuente, incluido Space=salto. Es evidencia de la física de referencia, no de la interfaz actual. La guía v4 y el HUD indican Space=freno y doble Space=transformación. B es la alternativa de frenado anunciada; no se anuncia Ctrl, porque el Keyboard de la fuente protege los atajos del navegador con Ctrl.

## Evidencia visual de vehículos

En `tests/vehicle-review.html` se observaron con teclado real ambas transformaciones, el Corsair y su cámara de seguimiento, la caída/aterrizaje y un único vehículo. El color pasó de naranja a azul mediante el control de pintura. Una regresión de caída desde 25 m fuera de la costa verificó recuperación y cámara restaurada. No aparecieron errores de consola. Esta página no escribe el mundo del usuario.

## Resultados del mapa físico

Las diez pruebas de `v4-world.mjs` pasan con los once controladores World2 y 650 cuerpos del mapa integrado. Playa: entrada hasta agua somera y regreso sin recuperación. Hielo: transición terreno→ice a altura 0,122 m. Ambos puentes: cuatro ruedas apoyadas durante el cruce. Pit lane: recorrido completo, error máximo de 0,338 m respecto al eje y cuatro contactos. Vuelo: ocho puntos rodean la isla en una envolvente de 298 × 225 m y regresan sobre tierra. Catorce transformaciones conservan el mismo cuerpo y la caída real empieza a 29,7 m. Las rutas se guardan en JSON.

`physics-profile.json` registra 1.200 pasos: 0,68 ms de media / 0,89 ms p95 de física, 81 cuerpos dinámicos y tres despiertos al reposar. Se mantiene el sleep del motor original. En la interfaz principal se observaron las dos transformaciones con doble SPACE, sin errores de consola; la sesión Drive estabilizada alcanzó 120 FPS en el equipo de revisión. El rendimiento depende del equipo y encuadre.

## Agua, horizonte y animación

Las cuatro pruebas de `v4-water.mjs` pasan. El océano tiene 98.560 triángulos orientados hacia arriba, colores derivados del fondo real y un horizonte continuo de 2.640 m. Las alturas de lagos transformados coinciden con la consulta física, el hielo conserva su collider y las superficies ocultas no aportan agua. Las 33 animaciones generadas tienen 45 tracks, todos enlazados a nodos reales de su instancia.

## GLB portátil

La exportación v4 entregada supera las tres pruebas de `v4-export.mjs`: 48.169.688 bytes, 7.968 nodos, 604 recursos de malla, 131 materiales y 26 imágenes incorporadas. Sus 33 animaciones usan 45 canales con referencias válidas. No contiene recursos externos ni rutas absolutas del equipo. El archivo conserva once curvas viales y metadatos editables.

## Cierre de integración en navegador

- **303 assets** disponibles. Asset Studio: se abrió Pine, se editó el hijo Needle tier 1 (Y 3,1→4,2), se aplicó material Ice, se guardó la definición y una variante independiente Pine Coastal QA, se añadió al mundo y se verificaron los JSON y las miniaturas. Los cambios de QA se descartaron tras recoger evidencia; el mundo entregado conserva su diseño limpio.
- **Carreteras:** controles numéricos y selección de puntos verificados para carretera y pista. Undo restaura sus coordenadas. Se creó tierra sobre el mar con radio 7 m y se descartó la isla de ensayo tras la captura.
- **Carrera compacta:** seleccionar Catalunya y pulsar Drive sitúa el coche en su salida. E activa cuenta atrás, cronómetro y doce checkpoints. `race-functional.png` registra el estado de carrera y 0 km/h al reposar.
- **Guardar y recargar:** SAVE WORLD confirmó la escritura de `exports/editor-world.json`; la recarga confirmó «Cambios guardados restaurados». Validate World sobre el guardado: **0 errores, 0 advertencias, 7.922 objetos**. Consola del navegador sin errores.
- **Exportación:** la interfaz confirmó `exports/EditedWorld.glb`, 48.169.688 bytes. Tres pruebas verifican 7.968 nodos exportados, 604 recursos mesh, 131 materiales, 26 imágenes integradas, 33 animaciones y 45 canales enlazados. Ninguna dependencia externa. Los recuentos difieren porque la validación excluye auxiliares y glTF incorpora nodos estructurales y luces.
- **Portfolio:** comparación completa de los 3.218 archivos del snapshot inicial: mismos SHA-256, mtime y permisos, sin altas ni bajas (`portfolio-unchanged.json`). El verificador antiguo utilizaba una captura anterior y señalaba cuatro diferencias preexistentes; ahora el test selecciona explícitamente la captura v4 tomada antes de esta iteración, conservando las anteriores como evidencia histórica.
- **Mapa:** comparación ortográfica con norte arriba y vista oblicua del mundo real. Se conserva el centro circular, castillo e hielo al NO/N, noria y globo al NE, loop al E, circuito al SO, puerto y playa al S y avión al SE. Es una interpretación 3D editable de la distribución; no reproduce al píxel la ilustración ni todos sus detalles pintados.
- **Salida de Drive:** una prueba recorre los once tipos de actividad y comprueba que sus 307 meshes, visibilidad y recursos permanecen idénticos tras simular, agrupar para rendimiento y restaurar. El sol recupera el encuadre de edición para conservar las sombras.

La ejecución completa inicial de `npm run test:v4` registra 88 comprobaciones aprobadas en `final-tests.log`. La última optimización añade cuatro comprobaciones de luces: **92 comprobaciones v4 aprobadas en total**, agregadas por suite en `final-summary.json`. Las regresiones de física, actividades y paridad originales también pasan. La prueba de portabilidad actualizada pasa en `asset-portability-final.log`.

La exportación GLB conserva datos visuales y de autoría. Las interacciones y el modo de vuelo se ejecutan mediante los módulos locales del editor web. El enlace CV conserva la ruta original: el PDF no existía en la referencia, y debe añadirse en `assets/alejandro-newport-cv.pdf` para disponer de esa descarga.


## Documento nativo y render

`world/EditedWorld_v4.blend` se creó y verificó desde el GLB final. Conserva los padres de sus 8.151 objetos visuales; 490 proxies físicos están separados y ocultos. Las 33 acciones de animación se evaluaron en los fotogramas 1, 91 y 181, y las 26 imágenes están empaquetadas. La creación de cuerpos se realiza en un único lote para evitar recalcular toda la escena por cada collider. `native-roundtrip.json` y `blender-tests.json` contienen la evidencia. El archivo comprimido (32.683.194 bytes) se volvió a abrir correctamente. La imagen `world-aerial.png` es un render Eevee de 1.600 × 1.200 del archivo entregado, inspeccionado junto a las capturas del navegador.

## Iluminación y rendimiento final

La noche utiliza ocho PointLights y un SpotLight cercanos, seleccionados cada 500 ms; actualiza sus posiciones e intensidades en cada frame. El conjunto permanece fuera del documento y el render restaura inmediatamente las capas de las luces originales, por lo que no altera guardado, Asset Studio ni exportación. Se verificaron cuatro casos con 257 luces authored, ocultaciones y errores de render. La vista general nocturna pasó de unos 8 a 36 FPS, y Drive nocturno estabilizado mostró 120 FPS y 1.232 llamadas en el equipo de revisión. Las capturas `world-night-browser.png` y `drive-night-browser.png` registran ambos modos. El rendimiento depende del equipo.
