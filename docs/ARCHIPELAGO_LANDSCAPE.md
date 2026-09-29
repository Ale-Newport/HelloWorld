# Archipiélago: jardines y costa conducible

La iteración parte del guardado del usuario de `2026-09-28T17:58:40.147Z`, conservado íntegro en `backups/archipelago_before_landscape_20260928/`. No se regeneraron los mundos v7.

- Se mantienen las transformaciones, jerarquía, visibilidad y eliminaciones de los 12.950 objetos originales.
- Se añadieron 25 árboles, 16 parterres y un banco en huecos libres. Se reservan los caminos existentes y corredores abiertos. Para el circuito se comprueba su huella triangular, no el rectángulo que engloba sus zonas interiores.
- El grupo vacío Projects District recibe una instancia funcional de `world2:projects`; conserva la posición y rotación del grupo del usuario. La instancia nueva está adaptada al espacio disponible y conserva las referencias de interacción del catálogo.
- El terreno se reconstruye desde los siete trazos del usuario sobre una cuadrícula de un metro. La tierra pasa a arena en la orilla y sigue bajo el agua: transición seca de 4 m, plataforma somera de 12 m y descenso posterior. Los recortes del hielo y del hoyo siguen perteneciendo a sus respectivos assets. El terreno resultante continúa siendo editable con los pinceles existentes.
- 12.648 briznas, distribuidas en 38 mallas sin colisión, usan los colores de raíz/punta y las frecuencias de viento de `Portfolio/src/world2/World2Grass.ts`. El color queda horneado para exportación; el viento se reinstala al cargar o deshacer. Una textura de grano fino aporta detalle al suelo y la arena.
- El color del agua se calcula a partir del fondo físico tras las ediciones. Los controles y la física del coche no se modifican.

## Comprobación

`node --loader ./tests/local-loader.mjs tests/v9-landscape.mjs exports/worlds/archipelago/editor-world.json`

La prueba verifica preservación del guardado, carga del panel, césped, apoyo de los nuevos elementos, separación entre ellos y respecto a 351 objetos existentes. Se realizan seis trayectos con PhysicsVehicle sobre la malla costera real: entrada y salida por oeste, este y norte, manteniendo contacto con el suelo y sin recuperaciones. Estas pruebas de pendiente aíslan el terreno; la escena completa se comprobó también visualmente en MAP, 3D y Drive.

También pasa `tests/v8-terrain-cache.mjs`: seis trazos, equivalencia con reconstrucción completa, Undo/Redo y persistencia.

Resultados: `reports/v9/validation.json`. Capturas: `reports/v9/archipelago-map.png` y `reports/v9/drive-grass-projects.png`.

`scripts/v9/landscape.mjs` genera un candidato a partir de la copia original. Su opción `--install` rechaza reemplazar un archivo que haya cambiado desde esa copia; no debe utilizarse para sustituir ediciones posteriores del usuario.

## Projects District: reparación del conjunto

Se recuperaron también `world2:lab` (segunda pantalla, con Next experiment) y una plaza de losas con la textura original de World2. El pavimento excluye las tres superficies de caminos existentes para evitar solapamientos; su máscara guarda los contornos originales, no miles de triángulos. Se retiraron 188 briznas bajo la nueva plaza. Las posiciones y estados de los objetos existentes permanecen intactos. Copia previa: `backups/projects_before_completion_20260928/`.

`npm run test:v9:projects` comprueba ambas pantallas, navegación, interacción del laboratorio, salida a conducción y material del suelo después de cargar. Evidencia: `reports/projects/completion.json` y `reports/v9/projects-validation.json`.
