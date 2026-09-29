# Pinceles y tres mundos · World Studio 07

Abre [la comparativa local](http://127.0.0.1:8844/preview/worlds.html). El botón con el nombre del mundo en la barra superior vuelve a esta página; guarda los cambios pendientes antes de salir.

- **Laguna**: isla con laguna central y circuito en una península occidental.
- **Archipiélago**: zonas urbanas, de ocio y deportivas separadas por mar y conectadas por puentes.
- **Costa panorámica**: recorrido de norte a sur con el circuito en el extremo meridional.

Cada alternativa contiene las 16 Experiences del mundo guardado, las 11 plantillas y las actividades World2 adicionales. Mantiene las piezas y transformaciones internas de cada grupo; el circuito sigue a escala 1:1. MAP, 3D EDIT y DRIVE comparten la misma escena.

## Pintar en MAP

**Terrain → ＋ Land brush / − Land brush** añade tierra en el mar o recorta tierra existente. Ajusta **Brush radius**, mantén pulsado y dibuja libremente; suelta para aplicar. Un clic pinta un círculo. **Material brush** cambia el acabado. Polygon y Rectangle siguen disponibles.

**Paths → ＋ Path brush / − Path brush** pinta caminos a mano alzada o borra sólo la parte bajo el pincel, también en caminos y plazas existentes. Ajusta **Path width** para pintar y **Eraser radius** para borrar. Los trazos que se cruzan, con el mismo material, se unen. Slabs mantiene su textura a escala constante.

El círculo muestra el tamaño real del pincel. Cada trazo completo es un paso de **Undo/Redo** (⌘/Ctrl Z y ⌘/Ctrl Shift Z). Las capas ocultas o bloqueadas no se modifican. **Esc** sale de la herramienta.

## Guardado independiente

Tu mundo original continúa en `exports/editor-world.json`. Sus assets continúan en `exports/asset-definitions.json`.

Las alternativas se guardan en `exports/worlds/lagoon/`, `exports/worlds/archipelago/` y `exports/worlds/coast/`, cada una con su propio `editor-world.json` y `asset-definitions.json`. **SAVE WORLD** y **EXPORT GLB** usan únicamente la carpeta del mundo abierto. Cambiar una alternativa no cambia las demás.

La copia de seguridad anterior a esta iteración está en `backups/world_before_brush_worlds_20260927/`. El servidor conserva además el guardado anterior de cada alternativa en `backups/worlds/<id>/`.

## Verificación

`npm run test:v7` comprueba los pinceles, recorte parcial, capas bloqueadas, unión sin solapamiento, Undo/Redo, reconstrucción y guardado; después reconstruye los tres mundos y verifica sus grupos, IDs, transformaciones, actividades World2, carreteras, suelo y cuatro contactos de ruedas en el punto de salida. La pista de hielo conserva su recorte de terreno y su propio suelo de hielo.

Resultados y capturas: `reports/v7/`. El generador de alternativas es una herramienta de desarrollo: volver a ejecutarlo reemplaza los guardados de las tres alternativas. No es necesario para abrirlas o editarlas.
