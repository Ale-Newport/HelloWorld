# Alejandro World · World Studio 04

Editor local de una isla conducible y sobrevolable. Esta versión continúa el mundo anterior y utiliza **ALEJANDRO WORLD MAP** como plano de distribución. Los modelos, texturas, Three.js, Rapier y el avión están dentro de HelloWorld. Portfolio es una referencia de solo lectura; no se necesita su carpeta para ejecutar el proyecto.

## Abrir y conservar el estado anterior

**Start Driving.command** abre `http://127.0.0.1:8844/preview/` en **EDIT WORLD**. También puedes ejecutar:

```sh
python3 scripts/serve.py --open
```

Se necesita Python 3 y un navegador con WebGL2. No hacen falta cuentas ni servicios externos.

El backup completo anterior a esta iteración está en `backups/world_before_map_and_editor_upgrade_20260927/`, con el archivo Blender anterior. Se conservan además `backups/pre-world2-library.zip` y `backups/v1-expanded/`. El mundo Blender v2 no se sobrescribe: **Open Alejandro World.command** abre esa base; **Open Edited World.command** abre la exportación actual del editor web.

## Correcciones sobre el mundo guardado

Esta iteración conserva tus ediciones del puerto, carreteras, actividades y terreno. El circuito World2 ocupa una ampliación al suroeste a escala 1:1, conectada con South Coast Road. La vista general, Top View, mapa y límites de vuelo se adaptan al terreno creado. El loop se completa con W por ambos extremos; Shift es opcional. La fuente central tiene dos vasos de piedra, cascadas, mosaico y luces nocturnas. El modelo de estudios/experiencia y sus líneas comparten el mismo marco al editarlos y entrar en Drive.

Copia exacta previa: `backups/user_world_before_four_fixes_20260927_103401/`. Pruebas de esta iteración: `npm run test:v5`. Evidencias: `reports/v5/`.

## El mapa elegido

La plaza de Alejandro Newport ocupa el centro. Castle e Ice Lake están al noroeste; Bowling, Cookies y Lighthouse al oeste; el circuito World2 a tamaño original en la ampliación suroeste y la playa al sur; Ferris Wheel y Hot Air Balloon al norte/noreste; Projects al este del centro y Loop al extremo este; Achievements y Contact al sureste; Career y Harbor al sur. Canales y puentes conectan las zonas. Las carreteras rodean las plazas.

**Top View** utiliza una cámara ortográfica orientada al norte y encuadra la isla completa. La distribución se define en `preview/world-map.js`, las carreteras en `preview/roads/` y los assets modulares en `preview/assets/`. El terreno principal está a **0,15 m** y el mar a **−0,35 m**: medio metro de diferencia, con costa y playa inclinadas hacia el agua.

## Asset Library y Asset Studio

Cada tarjeta ofrece **Add** y **Edit**. Puedes buscar por nombre, filtrar por categoría o arrastrar el asset al mundo. **Edit** abre una escena temporal aislada, con fondo neutro, iluminación, cuadrícula, órbita y gizmo. El mundo principal queda suspendido durante esta edición.

1. Selecciona una parte en **Asset Hierarchy** o en el visor.
2. Ajusta transformación, material y textura, física, colisión, visibilidad, luces, animación o metadatos.
3. **Save Asset** guarda la definición y actualiza su miniatura. Las instancias vinculadas reciben los cambios sin perder su posición, rotación o escala.
4. **Save As New** crea una definición independiente y conserva la original.
5. **Add To World** guarda y coloca una instancia. **Back To World** vuelve al mapa; los cambios sin guardar se descartan. **Reset** recupera la última definición guardada.

La jerarquía permite renombrar, ocultar, bloquear, duplicar, borrar, cambiar **Parent** y **Unparent**. Las partes nuevas o modificadas permanecen separadas y editables. En el mundo, **Edit Instance** modifica solamente esa copia; **Edit Source Asset** abre su definición compartida.

Las categorías incluyen Water, Bridges, Harbor, Beach, Landmarks, City / Street, Nature, Park, Fairground, Racing, Technology, Buildings, Roads y Vehicles. Los lagos exponen parámetros de tamaño, profundidad visual, orilla, agua, vegetación, rocas y hielo; **Rebuild shape** aplica los parámetros. Los puentes, faro, castillo, puerto y globo se componen de piezas identificables, reutilizables y editables.

Los presets de física incluyen Static Decoration, Heavy Static, Light Dynamic, Medium Dynamic, Vehicle Prop, Water Object y No Collision. Los presets de material incluyen Grass, Wood, Stone, Metal, Plastic, Glass, Asphalt, Sand, Ice y Water.

## Actividades de Portfolio World2

Las **179 entradas World2** siguen disponibles, incluidas 15 actividades completas: bolos, circuito original, proyectos, baño, achievements, behind the scenes, social, carrera/estudios, letras 3D, cookies, laboratorio, altar, máquina del tiempo, controles y hoguera.

Arrastra una actividad, muévela, gírala sobre Y y escálala uniformemente. Selecciónala antes de pulsar **Drive** para aparecer en su punto de llegada. Cada copia conserva sus cuerpos, referencias y reinicios. Acércate a un marcador y pulsa **E / Enter**. En Proyectos, A/D o flechas cambian de proyecto; Esc cierra el panel.

Bolos conserva bola, diez pinos, bumpers, strike y reset. El circuito original conserva checkpoints, cuenta atrás y marcas. Las letras y la cabina mantienen su física. Las líneas cronológicas suben al acercarte. Social mantiene los contactos y ventilador. El hoyo abre también el suelo físico y lo restaura al moverlo o borrarlo. El circuito World2 original tiene su escala original y necesita más espacio que el circuito compacto del mapa. En tu mundo guardado, selecciona Carreras · circuito World2 antes de pulsar Drive para aparecer en la llegada original y activar la carrera con E.

Las modificaciones de las partes de un asset funcional se aplican a su representación de Drive conservando las referencias de sus controladores. La geometría y los metadatos se exportan; el comportamiento JavaScript se ejecuta dentro de HelloWorld.

El enlace CV original apunta a `assets/alejandro-newport-cv.pdf`; ese PDF no estaba en Portfolio. Para habilitar la descarga, coloca allí el archivo correspondiente.

## Editar mundo, curvas y terreno

Arrastra para orbitar, rueda para zoom y botón derecho para desplazar. Clic selecciona; Shift + clic amplía la selección.

| Acción | Atajo |
|---|---|
| Mover, rotar, escalar | G, R, S |
| Enfocar | F |
| Duplicar | ⌘/Ctrl D |
| Deshacer / rehacer | ⌘/Ctrl Z / ⌘/Ctrl Shift Z |
| Borrar | Suprimir |

El inspector ofrece transformaciones numéricas, ground snap, alineación a superficie, cuadrícula, giro por pasos, materiales y física. **Simulate** ejecuta física y animación sin activar el vehículo.

Una carretera tiene una sola curva maestra. Asfalto, marcas, bordillos, barreras y colisión se regeneran juntos cuando mueves sus puntos, cambias anchura o transformas la carretera. Las franjas rojo/blanco y las UV siguen la distancia recorrida. El sistema une o recorta las superficies antes de triangularlas, evitando capas de asfalto superpuestas en curvas cerradas y cruces.

Selecciona una carretera para editar puntos, añadir o borrar puntos, extenderla, cambiar anchura o barreras. **Conform to terrain** adapta su altura al suelo. **Auto Smooth** suaviza los puntos; los giros peligrosos siguen señalados hasta corregirse. La biblioteca incluye T Junction, Crossroad, Roundabout, Merge y Split. El loop vertical conserva su geometría y asistencia específicas.

**Road Debug** muestra eje, límites, separación, puntos, colisión y problemas. **Validate World** comprueba recursos, referencias, geometría vial, invasiones de edificios/atracciones, objetos flotantes o enterrados, agua, playa, física y spawn. Son diagnósticos para revisar los cambios del usuario; un aviso conserva información sobre el objeto afectado.

**⛰ → Create land** pinta tierra directamente sobre el mar. Ajusta radio y altura; **Erase land** baja la tierra creada. Raise, Lower, Smooth, Flatten y Paint permiten esculpir o pintar. Esc termina el pincel. Selecciona tierra creada y pulsa Drive para aparecer sobre ella. **Water Debug** diferencia nivel del mar, zonas someras, profundas y pendientes accesibles.

## Coche, agua y avión

**Drive** inicia la simulación; **Esc** cierra primero una actividad abierta y después vuelve a Edit World. Al salir se restauran las posiciones de autoría.

| Control | Coche |
|---|---|
| W / S, flechas arriba / abajo | Acelerar / frenar y marcha atrás |
| A / D, flechas izquierda / derecha | Dirección |
| SPACE una vez / mantener | Freno de mano |
| SPACE SPACE, dentro de 300 ms | Transformarse en avión |
| B | Freno |
| Shift | Boost de World2 |
| R | Recuperar posición segura |
| C | Restablecer cámara |
| E / Enter | Interactuar |
| H · 1–4 | Claxon · hidráulicos |
| M / Tab · K | Mapa · logros |

**SPACE ya no es salto en la versión 4.** La primera pulsación espera brevemente para distinguir el freno de la transformación; el doble toque no aplica antes un frenazo. **Vehicle Color** cambia la pintura del coche. Las ruedas, masa, centro de masa y fuerzas proceden de World2. El nuevo estado de aparcamiento elimina la pequeña deriva sobre suelo casi plano y se libera con input; pendientes fuertes e hielo mantienen su comportamiento.

La playa tiene una transición continua a agua somera: se puede entrar, notar mayor resistencia y volver a tierra. El agua profunda requiere una inmersión sostenida antes de recuperar una posición segura. La estela da feedback de inmersión. El hielo está integrado al nivel de la isla y reduce agarre/frenado.

| Control | Avión |
|---|---|
| W / S | Aumentar / reducir velocidad |
| A / D | Girar |
| Q / E o flechas abajo / arriba | Subir / bajar el morro |
| Arrastrar dentro del visor | Asistencia opcional de giro y cabeceo |
| SPACE SPACE | Volver a coche en esa posición |

El Corsair incluido en la raíz se utiliza como avión local. Tiene despegue asistido, velocidad mínima, nivelación automática, cabeceo limitado, cámara de seguimiento y techo gradual a 85 m. Al volver a coche, aparece en la posición del avión y **cae de verdad**, conservando movimiento horizontal. Se limita la velocidad vertical extrema; una caída al mar sigue las reglas del agua. Se comparte un único cuerpo físico, un controlador activo y una cámara.

## Guardar y exportar

**Save Asset** conserva definiciones en `exports/asset-definitions.json`. **Save World** guarda instancias, transformaciones, terreno y overrides en `exports/editor-world.json`. Se escriben de forma atómica y mantienen copia anterior en `backups/`. El siguiente arranque restaura ambos documentos. Las definiciones están separadas de las transformaciones de sus instancias. El historial Undo/Redo pertenece a la sesión.

**Export GLB** guarda `exports/EditedWorld.glb` con jerarquía, materiales, transformaciones, animación disponible y metadatos. Los helpers del editor y overlays de depuración quedan fuera. **Open Edited World.command** abre el mapa guardado y crea `world/EditedWorld_v5.blend`, conservando la jerarquía visual, los materiales y las animaciones. Los colliders nativos son proxies ocultos independientes, por lo que no se fusionan ni destruyen las partes editables. El documento base `world/AlejandroWorld.blend` permanece como la versión anterior conservada. Los juegos y el cambio coche/avión requieren además los módulos web: para mover el producto completo, conserva toda la carpeta HelloWorld.

El importador web admite GLB y GLTF con recursos incorporados. FBX, OBJ o GLTF con archivos externos pueden importarse mediante el editor Blender.

## Comprobar la iteración

Las pruebas usan Three.js y Rapier reales. Los tests de texto en Node sustituyen únicamente la pintura de canvas; el aspecto visual se comprueba aparte en el navegador.

```sh
node --loader ./tests/local-loader.mjs tests/v4-assets.mjs
node --loader ./tests/local-loader.mjs tests/v4-factories.mjs
node --loader ./tests/local-loader.mjs tests/v4-roads.mjs
node --loader ./tests/local-loader.mjs tests/v4-routes.mjs
node --loader ./tests/local-loader.mjs tests/v4-validation.mjs
node --loader ./tests/local-loader.mjs tests/v4-vehicle.mjs
node --loader ./tests/local-loader.mjs tests/v4-world.mjs
node --loader ./tests/local-loader.mjs tests/v4-water.mjs
node --loader ./tests/local-loader.mjs tests/v4-track.mjs
node --loader ./tests/local-loader.mjs tests/v4-terrain-cuts.mjs
node --loader ./tests/local-loader.mjs tests/v4-lifecycle.mjs
node --loader ./tests/local-loader.mjs tests/v4-lights.mjs
node --loader ./tests/local-loader.mjs tests/v4-export.mjs
node --loader ./tests/local-loader.mjs tests/v3-world2.mjs
node --loader ./tests/local-loader.mjs tests/v3-handling.mjs
```

`npm run test:v4` ejecuta las suites v4. La suite de exportación requiere haber pulsado **Export GLB** en el mapa actual. **Run World Tests.command** añade regresiones de las versiones anteriores y la importación nativa con Blender, guardando el documento v4 independiente.

El test v4 del mundo construye el mapa entregado y sus colliders, incluidos los controladores World2; recorre playa, hielo y puentes, vuela alrededor de la isla y comprueba spawn y transformaciones. Los resultados de aceptación y las comprobaciones visuales están en [reports/v4/INTEGRATION.md](reports/v4/INTEGRATION.md). [reports/v4/VEHICLES.md](reports/v4/VEHICLES.md) documenta el diagnóstico de deriva y las pruebas de conducción/vuelo. Los informes v2/v3 conservan evidencia histórica de las versiones previas, no sustituyen las pruebas del mapa v4.

La prueba v3 de paridad conserva los bindings de referencia originales (incluido Space=salto) para comparar la física base. La interfaz v4 utiliza los controles de esta guía. Procedencia y licencias: [ASSET_SOURCES.md](ASSET_SOURCES.md).
