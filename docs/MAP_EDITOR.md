# MAP · 3D EDIT · DRIVE

Los tres modos usan los mismos objetos y el mismo guardado. MAP dispone de una cámara ortográfica propia; al volver a 3D EDIT se recupera la cámara 3D. Drive construye sus cuerpos físicos a partir del mundo editado y restaura las posiciones de autoría al salir.

## Componer el mapa

- **MAP** abre el plano orientado al norte. Rueda para zoom; botón central, Space + arrastrar o **Pan** para desplazar.
- **Experience / Object** decide qué selecciona un clic. Shift + clic suma o quita objetos; arrastrar sobre vacío selecciona por marco.
- Arrastra la selección para moverla. El círculo sobre su contorno permite girarla. **Frame / F** encuadra la selección; **World** encuadra toda la tierra.
- East es X y North es −Z, en metros. **Rotate 90°** y el ajuste angular permiten ordenar zonas con precisión.
- La cuadrícula comienza apagada. Pasos disponibles: 0,25 / 0,5 / 1 / 2 / 5 m; giros: 5 / 15 / 45 / 90°. Snap a objetos, carreteras y terreno se controla por separado.
- **Layers** permite ocultar y bloquear Terrain, Water, Roads, Race Track, Paths, Experiences, Buildings, Nature, Props, Vehicles y Debug. Su visibilidad es una ayuda de MAP; no elimina suelo ni colisiones de Drive.

## Experiences

Las 16 zonas existentes son grupos reales, con IDs y posiciones mundiales conservados: Central Plaza, About Me, Projects, Achievements, Career, Contact, Bowling, Cookies, F1 Circuit, Ice Rink, Ferris Wheel, Loop Area, Harbor / Port, Beach, Lighthouse y Castle.

Mover o girar una Experience conserva las distancias entre sus piezas. Doble clic o **Edit inside** entra en ella: el resto se atenúa, y sus miembros pueden seleccionarse desde el inspector. **Back to world** regresa al conjunto.

**Create Group**, **Ungroup**, **Duplicate**, **Lock group** y **Save Template** permiten reutilizar composiciones. La biblioteca contiene once plantillas completas; clic o arrastrar muestra una previsualización transparente. El contorno verde indica espacio libre; el rojo avisa de solapamiento con experiencias, carretera o agua. El aviso permite colocar si es intencional.

El circuito World2 conserva su escala original y forma: se mueve y gira sin convertirlo en una carretera procedural. Su entrada, checkpoints y actividad siguen dentro del grupo. Las carreteras creadas con curvas conservan su editor de puntos independiente.

Los assets pueden buscarse y filtrarse por categoría, favoritos o recientes. Las plantillas guardan referencias versionadas a definiciones; las instancias sin modificaciones comparten sus recursos. Las ediciones particulares conservan una copia independiente cuando es necesaria.

## Tierra, agua y costa

**Terrain** añade polígonos o rectángulos al mar a la altura base de **0,15 m**. Son operaciones geométricas de unión, sin superficies duplicadas en la zona compartida con la isla existente.

**Erase polygon / rectangle / brush** resta tierra de cualquier parte, incluida la isla principal. **Water** ofrece las mismas operaciones para abrir canales y lagos. Un corte puede separar varias islas. El mar está a −0,35 m; costa y playa se regeneran alrededor de los nuevos límites y huecos.

En un polígono, clic añade vértices, Backspace quita el último, Enter termina y Esc cancela. Rectángulos y pincel se aplican al soltar. **Beach width** controla la franja de playa. **Paint material** aplica Grass, Sand, Dirt, Rock, Snow o Slabs conservando las alturas fuera de la operación. **Terrain Debug** muestra límites, orillas, huecos y alturas.

Los pinceles de relieve de 3D EDIT siguen disponibles. Sus cambios se incorporan al mismo terreno y al historial compartido.

## Carreteras, caminos y plazas

En **Roads → Draw Road**, coloca puntos y pulsa Enter. Hay Road, Race Track, Service Road y Pedestrian. El suelo, marcas, bordillos y colisiones proceden de la misma curva. Selecciona la carretera para mover sus puntos, añadirlos, borrarlos o cambiar anchura.

Si la curva o sus bordes cruzan agua aparece **Add Bridge / Ignore / Cancel**. Add Bridge coloca tramos compatibles con el cruce y el ancho de la carretera. Cancel deja el mundo sin esa carretera. Los puentes no se añaden silenciosamente.

**Paths → Draw Path** crea caminos de 1–5 m. **Draw Plaza** crea un polígono con vértices editables. Ambos ofrecen Slabs, Stone, Dirt, Wood, Sand y Concrete. Los UV usan coordenadas del mundo: mover, girar, escalar o editar la forma no estira la textura.

Slabs reproduce el material autoral de Portfolio/world2, con una repetición cada 5 m. Está copiado localmente y auditado en `reports/v6/slabs-audit.md`. También se aplica en los suelos de Central Plaza, Projects, Achievements, Career, Ferris, Harbor y Castle Courtyard. Portfolio permanece como referencia de solo lectura.

## Guardar y comprobar

| Acción | Atajo |
|---|---|
| Deshacer / rehacer | ⌘/Ctrl Z · ⌘/Ctrl Shift Z |
| Duplicar | ⌘/Ctrl D |
| Copiar / pegar | ⌘/Ctrl C · ⌘/Ctrl V |
| Agrupar | ⌘/Ctrl G |
| Guardar | ⌘/Ctrl S |
| Borrar selección | Delete |

El historial comparte hasta 35 operaciones entre modos. **SAVE WORLD** escribe `exports/editor-world.json` y las definiciones personalizadas en `exports/asset-definitions.json`: incluye grupos, miembros, instancias, plantillas, terreno, curvas y ajustes de MAP. **EXPORT GLB** genera `exports/EditedWorld.glb` con sus texturas incrustadas para Blender. Las interacciones y conducción se ejecutan en HelloWorld.

El backup exacto anterior a MAP está en `backups/world_before_map_editor_20260927/`. Las comprobaciones se ejecutan con `npm run test:v6`; `docs/MAP_ACCEPTANCE.md` relaciona los 15 casos obligatorios con sus evidencias.

Los puntos de entrada se guardan como metadatos para futuras conexiones. Mover una Experience no rediseña automáticamente las carreteras o caminos que la rodean.
