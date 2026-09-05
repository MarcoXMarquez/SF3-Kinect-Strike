---
name: architecture-planner
description: Evalúa dependencias cruzadas, modela el grafo de dependencias y define interfaces/contratos antes de escribir lógica o implementar código.
---

# Architecture Planner Skill

Esta habilidad guía el diseño arquitectónico de software antes de cualquier implementación de código. Su objetivo principal es prevenir el acoplamiento excesivo, evitar dependencias circulares y asegurar el cumplimiento de principios SOLID (especialmente DIP - Dependency Inversion Principle).

---

## Principios Fundamentales

1. **Contratos Primero (Interface-First Design)**:
   - Toda interacción entre módulos, sistemas o capas debe mediarse a través de interfaces (`interface`) o abstracciones bien definidas.
   - Ningún sistema de alto nivel debe depender directamente de detalles de bajo nivel. Ambos deben depender de abstracciones.

2. **Evaluación de Dependencias Cruzadas**:
   - Antes de crear o modificar una clase, trazar el flujo de datos y dependencias:
     `Modulo A -> IContrato -> Modulo B`
   - Si el Módulo B necesita notificar o interactuar de vuelta con el Módulo A, **prohibido acoplar directamente**. Usar eventos, callbacks o un mediador/mensajería.

3. **Prevención de Acoplamiento Cíclico**:
   - Analizar el grafo acíclico dirigido (DAG). Si existe una ruta `A -> B -> C -> A`, la arquitectura es defectuosa. Debe romperse invirtiendo el control mediante interfaces o un bus de eventos.

---

## Flujo de Trabajo Obligatorio

Antes de escribir código de lógica de negocio o implementar métodos:

### Paso 1: Mapeo de Entidades y Dependencias
- Identificar qué módulos existen y qué módulos se crearán o modificarán.
- Enumerar dependencias entrantes (quién usa este módulo) y salientes (a quién usa este módulo).

### Paso 2: Especificación de Interfaces y Contratos
- Escribir las firmas de las interfaces completas:
  ```csharp
  public interface IInventoryService
  {
      bool TryAddItem(ItemId id, int quantity);
      bool HasItem(ItemId id, int quantity);
      IReadOnlyList<ItemStack> GetItems();
      event Action<ItemId, int> OnItemAdded;
  }
  ```
- Validar que las interfaces contengan solo lo que el consumidor necesita (Interface Segregation Principle).

### Paso 3: Definición del Flujo de Eventos / Notificaciones
- Diseñar la comunicación asíncrona o reactiva.
- Evitar que los servicios llamen métodos imperativos cruzados cuando un evento es más semántico y desacoplado.

### Paso 4: Revisión del Plan de Implementación
- Confirmar que las interfaces están validadas antes de implementar las clases concretas (`InventoryService : IInventoryService`).

---

## Checklist de Validación Arquitectónica

- [ ] ¿Existe alguna referencia directa entre dos sistemas hermanos que deba ser abstracta?
- [ ] ¿Se pueden probar unitariamente los sistemas aislando sus dependencias con mocks/stubs?
- [ ] ¿Hay métodos con más de una responsabilidad (SRP)?
- [ ] ¿El nuevo módulo puede ser reemplazado por otra implementación sin alterar el resto de la aplicación?
