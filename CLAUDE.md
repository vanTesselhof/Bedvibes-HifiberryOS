# Beocreate Development Guidelines

## Build Commands
- Start server: `node beo-system/beo-server.js`
- Debug mode (level 1-3): `node beo-system/beo-server.js v` or `vv` or `vvv`
- Developer mode: `node beo-system/beo-server.js dev`
- No customization: `node beo-system/beo-server.js no-custom`

## Code Style Guidelines
- **Naming**: Use camelCase for variables and functions
- **Indentation**: 4 spaces (mixed usage found in codebase)
- **Variables**: Use `var` declarations (not const/let)
- **Architecture**: Event-driven using EventEmitter via beo.bus
- **Modules**: Use CommonJS pattern (require/module.exports)
- **Error Handling**: Use try/catch for file operations, console.error for errors
- **Deep Cloning**: Use JSON.parse(JSON.stringify(obj))
- **Object Merging**: Use Object.assign() for extending objects
- **Settings**: Use beo.getSettings() and beo.saveSettings()
- **Event Communication**: Use beo.bus.emit() and beo.bus.on()
- **UI Communication**: Use beo.sendToUI()

## Extension Development
Extensions should follow the existing pattern with index.js defining the extension,
menu.html for UI, and standard file structure for images and assets.

## Web Interface Architecture
- Paths in HTML are URL paths (not file paths) mapped by Express routes
- Server maps `/views/`, `/extensions/`, `/common/` to actual directories
- Extensions are loaded dynamically at runtime via `loadAppearance()` function
- The `manifest.json` configures how extensions are loaded:
  - `extensionMarkupFileName`: HTML file for each extension (default: "menu.html")
  - `extensionScriptFileName`: JS pattern (€ replaced with extension name)
  - `extensionStylesheetFileName`: CSS pattern
- Dynamic content placeholders:
  - `<beo-dynamic-ui>`: Extension markup
  - `<beo-styles>`: Stylesheets 
  - `<beo-scripts>`: JavaScript
- Custom interfaces can be created in `beo-views/` and accessed with `/view/custom-name`