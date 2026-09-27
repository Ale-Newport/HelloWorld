# Slabs de Portfolio /world2: auditoría y copia local

Fecha: 27 de septiembre de 2026. Portfolio se ha inspeccionado en modo de solo lectura. La apertura de Blender usó `--disable-autoexec` y `use_scripts=False`; el SHA-256 de `folio-2025.blend` es idéntico antes y después: `df5286df6141a6bece01abbd873d87a7f3d915cb685c6c989883cb7457474080`.

## Fuente exacta

El pavimento está en el material **`terrain`** de `Portfolio/folio-2025.blend`, dentro de su grafo de nodos. No existe un material de suelo llamado literalmente `Slabs` en el GLB de `/world2`. La colección Blender `slabs` contiene además piezas geométricas que usan `palette`; esas piezas no identifican el shader del pavimento.

`Portfolio/scripts/export-world2-blender.py:177` hornea la expresión original de Base Color a `public/world2/textures/terrain-color.png`, una imagen de 1024 × 1024 que cubre el terreno de 192 × 192 metros. `Portfolio/src/world2/World2Environment.ts:9` mantiene `WORLD2_SCALE = 1`; su carga conserva el material GLTF y establece DoubleSide. El filtro Nearest se aplica únicamente a las texturas `palette`, no a este terreno.

La rama original que produce Slabs es:

```
Geometry.Position
  → Vector Math MULTIPLY (0.20000000298023224 en X/Y/Z)
  → Image Texture.004 (slabs.png)
  → Mix.005 (factor = color gris de la textura)
  → Mix.004 (mezcla espacial con el resto del terreno)
  → Principled BSDF Base Color
```

La máscara de `Mix.004` decide dónde aparece el pavimento en el terreno original. Una plaza o un camino propio necesita toda la salida de `Mix.005`, de modo que no copia esa máscara de distribución del mapa original.

| Parámetro | Fuente y copia |
|---|---|
| Textura | `Portfolio/assets/world2-source/textures/slabs.png`, 256 × 256 RGBA, canales RGB grises idénticos |
| Espacio de color | sRGB |
| Proyección / extensión / interpolación | FLAT / REPEAT / Linear |
| Color A de Mix.005, RGB lineal | `[0.39157015085220337, 0.18447518348693848, 0.1221388429403305]` |
| Color B de Mix.005, RGB lineal | `[1, 0.6239606738090515, 0.25818297266960144]` |
| Escala | Una repetición completa cada `4.999999925494195` metros |
| UV en Three.js | `[worldX * 0.20000000298023224, -worldZ * 0.20000000298023224]` |
| Roughness / Metallic | `0.5` / `0` |
| Normal / bump / roughness map | No existen conexiones ni texturas para estos canales |

El signo negativo de Z corresponde a la conversión del plano XY de Blender al plano XZ de Three. Los UV se regeneran con coordenadas mundiales al editar o escalar la superficie; el tamaño de los slabs permanece constante.

## Recursos de HelloWorld

`assets/surfaces/world2/slabs.png` es una copia byte a byte. SHA-256 de fuente y copia: `ae96f33015f45b7f1414f3c338c006e13263ac9b43ccf6efe58ec46734558126`.

`assets/surfaces/world2/slabs-albedo.png` representa la salida exacta del nodo de mezcla: descodifica la máscara sRGB, interpola los dos colores lineales y codifica el resultado a sRGB RGBA8. SHA-256: `7667c54ca3dbb39be5884c19096c324e0c3eeedb2d032992005313916908e996`. Esta conversión mecánica permite usar un `MeshStandardMaterial` exportable a GLB, conservando el aspecto sin depender de un shader exclusivo del navegador. No se ha creado ni reinterpretado la textura mediante generación de imágenes.

`assets/surfaces/world2/slabs-source.json` conserva la procedencia y los parámetros. `preview/surface-materials.js` expone el material reutilizable `Ground_Slabs`, la paleta y `surfaceUV`. Todas las URL utilizadas en ejecución apuntan a recursos de HelloWorld. Portfolio solo es necesario para repetir la auditoría de procedencia, no para abrir el editor, conducir o exportar.

La resolución de la textura reutilizable corresponde al material autoral, antes del horneado de todo el terreno. Por ello conserva más detalle que el mapa de terreno de 1024 píxeles de `/world2`; mantiene sus colores y densidad de origen, sin trasladar al nuevo mapa el remuestreo de aquel horneado global.

## Superficies editables

`preview/map-surfaces.js` ofrece `createPath`, `createPlaza`, `getSurfaceDefinition`, `setSurfaceDefinition`, `rebuildSurface` y `rebuildSurfaces`. La definición serializable vive en `userData.surfaceDefinition`. Los caminos usan una curva Catmull–Rom; las plazas aceptan polígonos cóncavos y huecos. Se rechazan intersecciones propias y huecos fuera del contorno antes de alterar la geometría existente.

Cada superficie genera una malla triangular con normales superiores, colisión estática y un desplazamiento predeterminado de 2,5 cm sobre el terreno. No modifica la malla de la isla. Los solapamientos internos de un mismo camino se unen geométricamente. El muestreo del terreno abarca también el interior de la superficie, y los UV mantienen su densidad después de mover, girar o escalar y regenerar la malla.

Materiales de caminos y plazas: Slabs, Stone, Dirt, Wood, Sand y Concrete. Slabs es el predeterminado. Los otros materiales son alternativas locales, sin atribución al material original.

Al integrar: pasar `{heightAt}` a las funciones de construcción/regeneración; regenerar después de editar transforms o el terreno; esperar `surfaceMaterialsReady()` antes de exportar texturas. El mundo y las Experiences pueden usar el mismo material y las mismas funciones de construcción.

## Comprobaciones

Comando ejecutado:

```sh
node --loader ./tests/local-loader.mjs tests/v6-map-surfaces.mjs
```

**11/11 pruebas superadas.** Resultado detallado: `reports/v6/map-surfaces-tests.json`.

- Textura original y copia idénticas; parámetros de la auditoría coincidentes.
- Comprobación de los 65.536 texeles de la conversión de color.
- Materiales estándar reutilizables, settings de textura y canales físicos correctos.
- Anchura y edición de curva comprobadas mediante raycasts de Rapier dentro y fuera del camino.
- Plaza cóncava con hueco: área correcta y ausencia real de collider en el hueco.
- UV de densidad mundial tras traslación, rotación, escala y edición del contorno.
- Adaptación de caminos y plazas a un terreno no plano.
- Regeneración idéntica de posiciones y UV después de guardar/cargar por ObjectLoader.
- Ediciones inválidas rechazadas conservando la geometría anterior.
- Cruce del propio camino sin áreas triangulares duplicadas.
- Conducción del PhysicsVehicle original sobre un camino elevado, con cuatro ruedas apoyadas y sin caída.

Auditoría de nodos completa: `reports/v6/slabs-node-audit.json`. Scripts locales reproducibles: `scripts/v6/audit_slabs.py` y `scripts/v6/copy_slabs.py`. Ninguno escribe dentro de Portfolio.
