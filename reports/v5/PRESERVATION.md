# Conservación del guardado — verificación final

Comparado `backups/user_world_before_four_fixes_20260927_103401/exports/editor-world.json` con el guardado/export final de `2026-09-27T10:01:02.748Z`.

**8/8 comprobaciones de conservación pasan.** SHA-256 del documento final verificado: `2ebbd04ce02f9eb0fa58b2416440e862ec53104f820daea6015c86b7fcb0f04b`.

| Elemento | Resultado |
|---|---|
| Objetos existentes | 8.347 IDs y 41.733 campos de nombre, posición, orientación, escala y visibilidad conservados, con las excepciones exactas solicitadas |
| Ajustes | 11 definiciones de carretera y 11.210 propiedades físicas/autoría conservadas |
| Tierras pintadas por el usuario | Las cuatro mantienen posiciones y colores bit a bit; su nueva metadata describe la misma malla original |
| Circuito | Sólo cambia la posición a `[-194, 0.15, 173]` y la escala a `[1,1,1]`; orientación, nombre, visibilidad y descendientes permanecen |
| Fuente | Raíz idéntica; las 16 piezas anteriores se sustituyen por las 57 piezas nuevas |
| Terreno principal | Pose idéntica; 1.020 vértices elevados únicamente en la ampliación SO según la fórmula autorizada; 20.489 vértices originales y 4.164 intersecciones de orilla conservados |
| Assets añadidos | Jerarquías, materiales, geometría y bytes de las imágenes conservados; cada referencia de malla/textura sigue apuntando al mismo contenido |
| Dock y Pier personalizados | Ambas definiciones versión 3 y el archivo completo de definiciones son byte a byte idénticos al backup |
| Estados retirados | Sólo 303 estados huérfanos de instancias añadidas que ya no existían en el guardado original |

No se ignoran cambios de apariencia o geometría. Se normalizan únicamente los UUID aleatorios de `THREE.Source` y `BufferGeometry`, comprobando su contenido completo y la asociación de cada referencia.

## Corrección adicional descubierta por la comparación

Los estados de geometría guardaban también los vértices temporales de los recortes de orilla, sin su procedencia. Al recargar, 21.509 vértices originales se convertían erróneamente en 25.673 «originales» y se añadían de nuevo los recortes.

`preview/geometry-state.js` y el uso desde `WorldEditor.capture/apply` guardan ahora sólo la malla original junto con sus índices y reconstruyen los recortes. Para guardados anteriores, la geometría base del mismo objeto recupera la procedencia sin perder las alturas o colores pintados.

**Dos ciclos de geometría fresca / aplicar / guardar pasan:** 21.509 vértices guardados, 25.673 renderizados, hashes idénticos de XYZ, colores e índices y crecimiento cero. La regresión anterior de recortes pasa también **5/5**.

## Comandos comprobados

```sh
node --loader ./tests/local-loader.mjs tests/v5-preservation.mjs
node --loader ./tests/local-loader.mjs tests/v5-terrain-persistence.mjs
node --loader ./tests/local-loader.mjs tests/v4-terrain-cuts.mjs
```

Resultados detallados: `preservation-tests.json`, `terrain-persistence-tests.json`. El fallo previo que permitió detectar la serialización defectuosa se conserva en `preservation-before-terrain-fix.json`.
