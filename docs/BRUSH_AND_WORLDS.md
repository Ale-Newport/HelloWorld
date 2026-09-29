# Pinceles · Archipiélago

Archipiélago es el único mundo. Abre `http://127.0.0.1:8844/preview/`. MAP, 3D EDIT y DRIVE comparten la escena y el guardado.

## Pintar en MAP

**Terrain → ＋ Land brush / − Land brush** añade tierra en el mar o recorta tierra existente. Ajusta **Brush radius**, mantén pulsado y dibuja libremente; suelta para aplicar. Un clic pinta un círculo. **Material brush** cambia el acabado. Polygon y Rectangle siguen disponibles.

**Paths → ＋ Path brush / − Path brush** pinta caminos a mano alzada o borra sólo la parte bajo el pincel, también en caminos y plazas existentes. Ajusta **Path width** para pintar y **Eraser radius** para borrar. Los trazos que se cruzan, con el mismo material, se unen. Slabs mantiene su textura a escala constante.

El círculo muestra el tamaño real del pincel. Cada trazo completo es un paso de **Undo/Redo** (⌘/Ctrl Z y ⌘/Ctrl Shift Z). Las capas ocultas o bloqueadas no se modifican. **Esc** sale de la herramienta.

## Guardado

SAVE WORLD actualiza `exports/worlds/archipelago/editor-world.json.gz` (versionado) y su JSON de trabajo (ignorado). Las definiciones se guardan en la misma carpeta. EXPORT GLB escribe allí `EditedWorld.glb`, también ignorado. La versión anterior se conserva en `backups/worlds/archipelago/`.

Las variantes Laguna, Costa y el guardado original se retiraron el 29 de septiembre. Sus copias locales permanecen en `backups/retired-worlds-20260929/`, fuera de Git y del selector.
