# Archipiélago · Alejandro World

Editor local de la isla de Alejandro Newport y motor de conducción del portfolio.
**Archipiélago es el único mundo y el predeterminado.** MAP, 3D EDIT y DRIVE trabajan sobre el mismo documento.

## Ejecutar

Requisitos: Python 3.10+; Node.js 20+ para pruebas y publicación. El navegador carga Three.js y Rapier incluidos en `preview/vendor`, sin CDN.

```sh
npm run preview
```

Abre `http://127.0.0.1:8844/preview/`. SAVE WORLD guarda la isla y sus assets. El servidor solo escucha en localhost y mantiene la versión anterior en `backups/`.

## Estructura

- `preview/`: editor, renderizado, experiencias y física. `runtime/` contiene el coche, avión y loop; `portfolio/` conserva los controladores portados de World2.
- `exports/worlds/archipelago/`: guardado canónico `editor-world.json.gz` y definiciones de assets. La compresión es sin pérdida; el JSON de trabajo y los GLB exportados quedan fuera de Git.
- `exports/AlejandroWorld.glb` y `navigation.json`: recursos base que reconstruye el cargador antes de aplicar el guardado. No son mundos alternativos seleccionables.
- `assets/`: modelos, texturas, fuentes y procedencia. Consulta `ASSET_SOURCES.md` y `docs/source/` para licencias.
- `scripts/release/`: restaurar, comprimir y publicar el mundo. Las carpetas numeradas contienen herramientas de migración históricas.
- `tests/`: pruebas del editor, las experiencias y la conducción. Los informes generados van a `reports/`, ignorado.
- `editor/`, `world/` y `scripts/worldgen/`: herramientas y fuentes de Blender. Los mundos retirados y exportaciones antiguas se conservan solo en `backups/`, ignorado.
- `docs/`: documentación del editor, assets, pinceles, costa y rendimiento.

## Publicar en Portfolio

```sh
npm run publish:player -- ../Portfolio/public/archipelago
```

El paquete contiene el **mismo código de física y experiencias** del editor, el guardado actual y todos los recursos necesarios. `/world` lo presenta mediante un iframe del mismo origen. No depende del servidor local ni de una API de escritura. `release.json` incluye hashes SHA-256 para verificar que el motor y el guardado coinciden.

Después de editar, guarda en el editor, vuelve a generar el paquete y versiona los cambios de ambos repositorios. No edites a mano `Portfolio/public/archipelago`.

```sh
npm run world:restore   # JSON de trabajo en un clon nuevo (no sobrescribe uno existente)
npm run world:pack      # tras modificar el JSON con una herramienta externa
npm run test:brush
npm run test:v8
npm run test:v9:projects
npm run test:release
```

Las pruebas históricas v4–v7 documentan etapas anteriores y algunas requieren sus snapshots locales; no representan la distribución actual de Archipiélago. Las comprobaciones de preservación v9 utilizan los backups previos a la intervención.

## Controles

WASD / flechas: conducir · Shift: boost · SPACE: frenar · doble SPACE: coche / avión · R: respawn · E / Enter: interactuar · M / Tab: mapa · K: logros · C: cámara. En avión, Q/E controla el cabeceo. Escape cierra la actividad; en el editor vuelve a edición.
