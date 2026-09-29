# Publicación de Archipiélago

`npm run publish:player -- ../Portfolio/public/archipelago` empaqueta el guardado actual con los módulos exactos del editor. La entrada utiliza `data-player="true"`: arranca DRIVE, bloquea guardar/editar y mantiene todas las experiencias y sus controladores. No necesita la API de Python.

Portfolio `/world` aloja `/archipelago/preview/index.html` en un iframe del mismo origen. Three y Rapier permanecen aislados de React y del bundle de la página principal. Los proyectos y redes se abren con sus controladores originales.

`release.json` identifica el commit fuente, el SHA-256 del guardado comprimido y los hashes de cada archivo. Ejecuta `node tests/release.mjs ../Portfolio/public/archipelago` para comprobar identidad del motor y del mundo. Genera el paquete después de crear el commit fuente.

## Verificaciones

- `npm run test:brush`: pincel libre, borrado, Undo/Redo, UV y único mundo.
- `npm run test:v8`: caché incremental y 12 trazos sobre Archipiélago.
- `npm run test:v9:projects`: pantalla de proyectos, laboratorio, textura de plaza e interacción.
- `python3 tests/release-server.py`: guardado real de más de 100 MB en un repositorio temporal, espejo comprimido y rechazo de mundos retirados.
- `npm run publish:player && npm run test:release`: integridad sin pérdida e identidad de todos los módulos publicados.
- Compilación de producción de Portfolio y prueba visual de `/world`, mapa, controles y logros.

Los informes y capturas son locales y están ignorados. Las versiones retiradas no se incluyen en el paquete. `exports/AlejandroWorld.glb` sigue siendo una dependencia técnica del cargador; el documento canónico de Archipiélago determina la escena final.
