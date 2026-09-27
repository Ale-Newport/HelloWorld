# Discovery y decisiones de base

Se inspeccionaron los dos proyectos antes de generar el mundo. Se registraron SHA-256, tamaño, fecha de modificación y permisos de 477 archivos de contenido de Portfolio. No se ejecutó npm, Next, exportadores ni comandos de escritura dentro de Portfolio.

## HelloWorld original

- `folio-2025.blend`: 16,074,344 bytes; SHA-256 `df5286df6141a6bece01abbd873d87a7f3d915cb685c6c989883cb7457474080`.
- 1,507 objetos; 120 colecciones; 35 materiales. Terreno de 192 × 192 m antes de la ampliación.
- Inventario completo, matrices, pivots, bounding boxes, padres, colecciones, materiales, imágenes y modificadores: `reports/original-blender-audit.json`.
- Curvas, constraints, textos, acciones y rigid bodies: `reports/original-extras.json`. No había animaciones ni cuerpos rígidos nativos; las físicas se representaban con empties y convenciones de nombres para el runtime web.
- El archivo es idéntico al de Portfolio y al hash de la dependencia original registrada allí. A pesar de la expectativa inicial, su texto archivado y las letras originales todavía eran BRUNO SIMON. La identidad Alejandro Newport estaba implementada en `src/world2/interactions/Title.ts`, no guardada en el blend. El nuevo mundo la incorpora explícitamente en geometría/texto editable, conservando el original intacto.
- Varias texturas y la fuente antigua no estaban presentes en las rutas relativas originales. La recuperación usa los recursos locales de Portfolio; Geist Bold sustituye la fuente ausente con su licencia OFL incluida.
- El archivo fuente fue guardado en Blender 5.0; el Blender disponible es 4.5.13 LTS. Se inspeccionó sin guardar sobre él. El núcleo nuevo usa la geometría ya evaluada y los shaders adaptados de los GLB de Portfolio, evitando reescribir los Geometry Nodes del original con una versión inferior. La fuente completa se conserva en el backup.

## Referencia visual de Portfolio

La ruta actual relevante es `/world2`. Carga `public/world2/models/world.glb` y `vegetation.glb`, `world-manifest.json`, `interactions.json` y texturas. El world GLB contiene 960 nodos, 322 meshes y 23 materiales; vegetation tiene 799 nodos, 9 meshes reutilizados y 5 materiales.

Se copiaron ambos GLB completos, el mapa y manifests; las 24 dependencias originales recuperadas (EXR de terreno/vegetación/agua, slabs, atlas/paleta, imágenes de carteles), la textura de terreno ya horneada y licencias. La vegetación usa las instancias en las posiciones originales, y en las expansiones se reutilizan árboles completos de esos mismos GLB.

El vehículo del portfolio se construye desde código. Se reutilizó su controlador Rapier, su sistema de eventos y matemáticas mediante una transpilación local. El nuevo vehículo visible sigue las dimensiones y el lenguaje de su carrocería crema con franja roja y placa AN. Se añadió frenada dependiente del hielo y se ajustó el parachoques para empujar objetos bajos con grupos de colisión.

## Noria disponible

`ferris-wheel.zip` ya estaba en HelloWorld. Contiene `source/Wheel model.fbx` y una textura AO. Se extrajo dentro de HelloWorld. El FBX tiene 368 objetos y 93,191 vértices fuente. El inventario está en `reports/ferris-audit.json`.

Se agrupan las piezas en soporte estático, rotor y doce cabinas reales, se corrigen los ejes importados y se reconstruyen los radios que excedían el aro. La jerarquía animada usa rotación y contrarrotación, no un giro de toda la estructura. Sus materiales se unifican con la paleta del mundo.

## Expansión

Cinco superficies de terreno nuevas alojan el circuito occidental, jardín del norte, lago helado, plaza de la noria y taller/loop del sur. Las carreteras originales pasan a servir la circulación por el núcleo. El mobiliario de competición original se lleva al nuevo circuito. Las conexiones incluyen superficies físicas y detalles de puente.

El diseño del circuito toma como referencia libre el [plano oficial del Circuit](https://www.circuitcat.com/wp-content/uploads/2026/02/2026-Manual-del-Oficial-de-Carrera-febrero.pdf). Se priorizan escala del diorama y conducción. Para comprobar la configuración contemporánea se consultó también la [guía oficial de F1](https://www.formula1.com/en/latest/article/circuit-guide-everything-you-need-to-know-about-the-circuit-de-barcelona-catalunya.7i1UoRE8Za0Jk4LI0r68qk).

La API física se contrastó con la [documentación de RigidBodyObject de Blender](https://docs.blender.org/api/current/bpy.types.RigidBodyObject.html) y con la implementación instalada. Los campos que Bullet no expone individualmente se identifican como metadatos de runtime.
