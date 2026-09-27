# Asset Studio

Cada tarjeta de la biblioteca tiene **Add** y **Edit**. Edit abre una escena temporal con suelo neutro, iluminación, órbita, grid y gizmo. El mundo queda suspendido mientras se edita; al volver se liberan el renderer, los controles, las geometrías privadas y los listeners temporales.

Selecciona una parte del árbol de jerarquía o del viewport. Puedes cambiar su nombre, transformarla, ocultarla, bloquearla, duplicarla, eliminarla y cambiar su padre sin perder su posición mundial. Los apartados Lights, Colliders, Helpers y Animations permiten localizar los componentes especiales.

Las propiedades incluyen materiales y slots, color, roughness, metallic, opacity, importación de textura, presets, masa, fricción, restitución, colisión, luces, animación y metadata. Los assets paramétricos, como los lagos, incluyen **Asset parameters → Rebuild shape**. El contorno y el shoreline se reconstruyen juntos desde la definición.

- **Save Asset** actualiza la definición, regenera la miniatura y propaga el contenido a las instancias vinculadas. Conserva la posición, rotación y escala de cada instancia.
- **Save As New** crea una definición independiente con un nuevo ID. Ambas siguen disponibles en la biblioteca.
- **Add To World** guarda y coloca la definición en el mundo.
- **Reset** recupera la versión guardada. Undo y Redo funcionan dentro del Studio.
- **Back To World** cierra el contexto temporal; los cambios sin Save se descartan.
- **Edit Instance**, desde Properties del mundo, edita solamente esa copia. **Save Instance** guarda su jerarquía completa como override y la separa de las posteriores propagaciones de la fuente.
- **Edit Source Asset** abre la definición compartida.

Los atajos del Studio son G mover, R rotar, S escalar, F enfocar, ⌘/Ctrl D duplicar, Suprimir eliminar, ⌘/Ctrl Z deshacer y ⌘/Ctrl S guardar.

Las definiciones editadas viven en `exports/asset-definitions.json`. El servidor local guarda de forma atómica y conserva `backups/asset-definitions.previous.json`. Las definiciones originales se generan de forma determinista desde los assets locales; se persisten únicamente las definiciones modificadas y las variantes. El mundo sigue guardándose en `exports/editor-world.json`, incluyendo los overrides de instancia. Los cambios de base de mapa no aplican accidentalmente IDs numéricos de una versión anterior.

El código distingue `assetDefinitionId`, `assetDefinitionVersion`, `assetPartId` y la transformación de instancia. Las copias normales comparten geometría y materiales. El Studio clona sus recursos antes de editar. Los cambios en piezas de World2 se trasladan también a las mallas y cuerpos físicos que sus controladores generan al iniciar Drive, incluyendo las letras y sus posiciones de reset.

Prueba automatizada: `node --loader ./tests/local-loader.mjs tests/v4-assets.mjs`. La evidencia queda en `reports/v4/asset-studio-tests.json`. El fixture de revisión visual es `tests/asset-review.html`, servido desde el mismo servidor local.
