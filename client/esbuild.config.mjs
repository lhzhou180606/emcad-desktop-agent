import esbuild from "esbuild";

await esbuild.build({
  entryPoints: ["src/cli.js"],
  bundle: true,
  platform: "node",
  target: "node18",
  format: "cjs",
  outfile: "dist/ipd-emcad-cli.cjs",
  minify: false,
  sourcemap: false,
});

console.log("Build complete: dist/ipd-emcad-cli.cjs");
