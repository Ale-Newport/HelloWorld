# Rendimiento de Terrain en MAP

Se corrigió el trabajo que se acumulaba al crear y borrar tierra con pinceles, especialmente al superponer trazos con playa.

- Se conserva el resultado de las operaciones previas y sólo se aplica la nueva. Cambiar el historial, las alturas base o las transformaciones invalida la caché; una carga completa reconstruye el mismo terreno.
- La nueva tierra se subdivide para conectar exactamente su perímetro con el terreno existente. Las aristas de todos los triángulos anteriores ya no se prolongan por el interior del nuevo trazo.
- Los booleanos se limitan a los polígonos cercanos; las playas se unen una vez por operación. Se reutilizan muestras de altura y vértices de la base.
- La costa se reconstruye una sola vez al terminar, después de los recortes de las Experiences. Se actualizan los caminos y carreteras que dependen del terreno afectado.
- Undo/Redo comparte los datos inmutables de la base de terreno en lugar de duplicar sus arrays en cada captura. El JSON guardado sigue incluyendo la base completa.

## Medición local

Prueba con el mundo completo Archipiélago, pincel de radio 8 m, playa de 2 m y trazos superpuestos de unos 60 m. Incluye historial, geometría y actualizaciones dependientes; excluye la carga inicial del mundo.

| Operación | Antes | Después |
|---|---:|---:|
| Primer trazo de tierra | 1.61 s | 0.84 s |
| Primer borrado superpuesto | 4.48 s | 1.02 s |
| Tercer trazo | Error por expansión de argumentos | 1.00 s |

Se completaron 12 trazos consecutivos, con un máximo de 1.91 s y 159 125 triángulos. Son medidas locales de ese escenario; trazos de otras dimensiones pueden tardar más. La medición inicial utilizó el perfilador de CPU.

`npm run test:v8` verifica la reconstrucción incremental frente a una carga completa, Undo/Redo, persistencia, invalidación de caché, caminos afectados y el escenario de 12 trazos. Pasaron además las 38 comprobaciones existentes de pinceles, terreno, superficies y consultas de altura. En el navegador se probaron añadir, borrar y deshacer ambos trazos, sin guardar las pruebas ni alterar los mundos.

Evidencia: `reports/v8/validation.json`, `before.json`, `after.json` y `terrain-brush-browser.png`.
