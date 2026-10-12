Delivery checks use only pinned public assets and the installed SDK:

```sh
node tools/build.mjs --canon /path/to/frozen/arxo-cnaf
npm install
npm test
npm run test:types
```

For an installed-tarball check, import `@arxo/canon-fr-benefits` and its `/apl`
entry in place of the relative source imports; use the identical cases and
assertions. TypeScript uses `ESNext.Disposable` because the engine's declarations
expose the optional disposal symbol. No live corpus is generated or checked.
