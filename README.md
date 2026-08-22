# Asset generator

The geometry and textures are generated, not hand-drawn. Geometry and UV
packing are authored together, so the texture sheet can never drift out of
alignment with the model.

```bash
cd tools
python3 build_models.py      # .geo.json + texture sheets -> tools/out/
python3 build_mod_assets.py  # rehome into ../src/main/resources, write lang,
                             # tags, recipes, item models
python3 build_sprites.py     # 16x16 sprites for plates, goggles, materials
cd .. && python3 verify_mod.py
```

Two conventions matter, both measured from Fracture Point's own models rather
than assumed:

- **1 texel per model unit** (standard 16 px per block). `TEXELS_PER_UNIT` in
  `build_models.py` pins it.
- **Cube rotation everywhere.** 87% of FP's cubes carry a rotation, which is
  what gives them smooth silhouettes. `geom.py` builds faceted domes out of
  octagonal rings and 45-degree chamfers.

`rotconv.py` re-derives the Euler convention by rendering a reference model
under four candidates and keeping the only coherent one (XYZ, no sign flips,
about the cube's own pivot). It needs a Fracture Point jar extracted to
`/tmp/fp` and is not needed for normal builds.

`render_preview.py` and `render_helmets.py` rasterise the models to PNG so
geometry can be checked without launching Minecraft.
