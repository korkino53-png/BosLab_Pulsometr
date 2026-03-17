# Repository guidelines

- Keep code modular by subsystem (`settings`, `BLE`, `game`, `physics`, `persistence`, `runtime helpers`).
- Prefer small, typed Python modules.
- Use `pygame-ce` APIs (imported as `pygame`).
- Store persistent JSON files next to executable using runtime helper utilities.
- Keep backward compatibility for missing keys in JSON files.
