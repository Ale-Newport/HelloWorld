# MAP v6 · aceptación

Fecha: 27 de septiembre de 2026. Se parte del mundo guardado por el usuario, respaldado en `backups/world_before_map_editor_20260927/`. La conversión conserva los **8.407 IDs anteriores**, la posición mundial de sus objetos, los cambios del puerto, las eliminaciones del usuario y las definiciones personalizadas. La comparación de matrices con el backup tiene un error máximo de `1,42 × 10⁻¹⁴`.

## Los 15 casos obligatorios

| Caso | Resultado y evidencia |
|---|---|
| 1. MAP, pan y zoom | Comprobado en el navegador; pan ortográfico medido a tres niveles de zoom en `map-model-tests.json`. Sin errores de consola. |
| 2. Mover Ice Rink y pasar a 3D | X −31 → −26 aparece inmediatamente en el inspector 3D; movimiento deshecho después. `experience-tests.json` verifica todas las matrices hijas. |
| 3. Editar un pingüino dentro | Plastic Penguin 44: X −43 → −42, Back to world y Undo. Solo cambia esa pieza; `map-edit-inside-ice.png` y prueba de offsets. |
| 4. Mover Harbor completo | Arrastrado desde MAP y deshecho. Muelles, barcos y props mantienen sus offsets; `map-harbor-moved.png` y `experience-tests.json`. |
| 5. Mover diez árboles juntos | Diez árboles del guardado real: trasladados y girados, IDs y transformaciones internas exactos. `map-model-tests.json`. |
| 6. Tierra conectada sin costura | Unión geométrica, altura 0,15 m y una sola superficie por muestra; `map-land-added.png`, `map-terrain-tests.json`, `editor-history-tests.json`. |
| 7. Recortar MAIN ISLAND | Corte rectangular visible en navegador, con agua y sin triángulos/collider residuales. `map-main-terrain-cut.png` y pruebas de terreno. |
| 8. Canal y terreno válido | Diferencia poligonal genera dos componentes válidos, costa cerrada y colisiones separadas. `map-terrain-tests.json`. |
| 9. Deshacer canal | Historial real restaura exactamente las geometrías originales incluso sin metadatos MAP previos; Redo reconstruye el canal. `editor-history-tests.json`. |
| 10. Carretera desde 2D | Dibujada sobre la isla real, terreno muestreado y curva generada; `map-road-edited.png`, `map-model-tests.json`. |
| 11. Editar punto y marcas | Arrastrado un punto en MAP, marcas/bordillos regenerados, dos Undo recuperan la escena. `editor-history-tests.json`, `road-dependencies-tests.json`. |
| 12. Camino Slabs | Creado en navegador; textura, 65.536 texeles y densidad original auditados. `map-slabs-path.png`, `slabs-audit.md`, `map-surfaces-tests.json`. |
| 13. Plaza Slabs redimensionada | Plaza dibujada y vértice movido; UV mundiales constantes incluso con escala y giro. `map-slabs-plaza-resized.png`, `map-surfaces-tests.json`. |
| 14. Mover F1 preservando forma | Experience trasladada/girada en prueba; buffers y escala original conservados. Campo Scale bloqueado también dentro del grupo y en 3D. `map-f1-original-scale.png`, `experience-tests.json`, `map-controls-tests.json`. |
| 15. Drive sincronizado | MAP → 3D → Drive sobre la misma escena. Coche World2 circula por una curva editada/agrupada con cuatro ruedas apoyadas. `map-to-drive.png`, `map-model-tests.json`; regresiones de loop y circuito pasan. |

Las carreteras, caminos, plazas y modificaciones temporales hechas para QA se deshicieron antes del guardado final. Se conserva la distribución del usuario.

## Comprobaciones adicionales

`npm run test:v6` ejecuta las suites secuencialmente para limitar la memoria. **79 comprobaciones**: surfaces 11, terrain-query 4, road-dependencies 2, map-terrain 15, world-instances 6, experiences 15, map-model 11, editor-history 6, state-coverage 1, map-controls 8. Informes JSON en `reports/v6/`.

El roundtrip completo usa `WorldEditor.document()` → JSON → reconstrucción del mundo, con 16 Experiences, 11 plantillas y la definición personalizada Pier v3. Los IDs y matrices del documento recargado coinciden exactamente; `missing-state-audit.json` comprueba por separado los 8.407 IDs del backup.

Las **27 regresiones World2** cubren fuente 4, Career 4, loop 12 y circuito 7 (`world2-regression-status.json`). El circuito conserva ocho gates a escala 1; todos apoyan cuatro ruedas. La conducción por el acceso dura 1.134 pasos, con cuatro contactos y error máximo 0,758 m; cuenta atrás, récord y salida siguen funcionando. Las 12 pruebas de carreteras v4 también pasan.

El aviso de cruce sobre agua se comprobó en navegador (`map-water-bridge-prompt.png`); los puentes compatibles se verifican con raycasts físicos. Las capas ocultas no eliminan terreno físico, y los bloqueos impiden editar selecciones ya activas. Las plantillas versionadas y referencias de instancias conservan recursos compartidos cuando no existe una edición particular.

## Portfolio y recursos

No se escribe en Portfolio. Sus **3.207 archivos de contenido** coinciden con el snapshot previo en SHA-256, fecha de modificación y permisos; no hay nuevos archivos de contenido. Tres archivos de caché de Finder `.DS_Store` difieren respecto al snapshot histórico y se registran explícitamente en `portfolio-integrity.json`. La prueba de assets distingue esas cachés del código, modelos y texturas; no las restaura ni modifica.

Slabs se copia byte a byte y su mezcla de color reproduce el grafo autoral. No hay dependencias de ejecución hacia Portfolio. El GLB exportado contiene 16 grupos Experience, los siete suelos Slabs y todas sus imágenes incrustadas. `delivery-manifest.json` conserva los checksums y tamaños finales; `native-roundtrip.json` documenta la importación Blender v6.

## Rendimiento y alcance

La búsqueda de altura usa un índice de triángulos reutilizable. Las dependencias entre carreteras se calculan por sus segmentos, evitando regenerar un boulevard entero cuando se dibuja en su centro vacío; la prueba de esa actualización tarda aproximadamente 5 ms. La regeneración de cruces reales sigue dependiendo de su complejidad.

El historial conserva hasta 35 operaciones. Las entradas de Experiences se guardan, pero las carreteras vecinas no se reconectan automáticamente al moverlas. Las actividades conservan su comportamiento JavaScript dentro de HelloWorld; Blender recibe geometría, materiales, jerarquía y metadatos.
