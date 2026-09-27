# World Studio 03 — entrega World2

179 entradas de biblioteca, 15 actividades completas. Se reutilizan los modelos, colliders, 44 módulos originales y datos de Portfolio. Las instancias se trasladan y giran en un adaptador que conserva las coordenadas de los controladores. Portfolio se ha utilizado solo para lectura.

## Verificación

- 10 pruebas de actividades y terreno: bolos, circuito (incluido registro de vuelta), proyectos, carrera profesional, letras, lugares/contactos, nueva tierra, hoyo y dos pistas independientes.
- Paridad del vehículo: dos mundos Rapier independientes y 345 pasos de acciones; error máximo de posición 0 m.
- 10 pruebas de regresión de conducción: circuito compacto, bulevar, hielo, impactos, loop y vuelta completa por las zonas.
- Navegador: creación y guardado/recarga de tierra en el mar; colocación y guardado/recarga de Proyectos; Drive sobre tierra nueva; nueva sesión de Drive tras Simulate. Sin errores nuevos de consola en la sesión final.
- Restaurado el JSON del usuario anterior a las pruebas. La biblioteca queda disponible sin añadir objetos de prueba al mapa guardado.

La prueba de circuito atraviesa sus puertas con posiciones controladas para verificar el estado y las marcas; los recorridos físicos automatizados son los del mapa compacto de HelloWorld. La comparación de conducción cubre las acciones indicadas, no promete igualdad numérica en toda situación imaginable.

## Procedencia y límites

Los 44 archivos portados coinciden con sus hashes de origen. La auditoría histórica de 477 archivos de Portfolio registra cuatro diferencias fuera de esos módulos: Journey.tsx, GlobalCanvas.tsx, .DS_Store y tsconfig.tsbuildinfo. No se han modificado ni revertido estos archivos; se conserva el resultado fallido de esa auditoría en validation.json. Los otros 12 controles de assets pasan.

El perfil de Portfolio enlaza un PDF de CV que no existe allí. El enlace se conserva y quedará disponible al añadir assets/alejandro-newport-cv.pdf en HelloWorld. No se ha inventado ese documento.

Las actividades funcionan en World Studio / Drive. GLB conserva geometría y materiales para Blender, no el motor de interacciones JavaScript. Escala 1 mantiene las dimensiones originales; los conjuntos se pueden mover, girar en Y y escalar uniformemente.

## Uso

Abre http://127.0.0.1:8844/preview/. Elige World2 · actividades, arrastra un conjunto, selecciónalo y pulsa Drive. E/Enter interactúa, Espacio salta y B frena (controles originales). Para ampliar la isla: ⛰ → Create land; pinta sobre el mar y guarda. Selecciona la tierra nueva antes de Drive para aparecer en ella.
