# Cellshading-Dominica

A DCTL for DaVinci Resolve that turns live-action footage into cel-shaded, Killer7-style
images: flat colour palettes, hard ink-black shadows, blown-out highlights and ink outlines.

## What it does

1. **Flattens** the image into painted-looking patches (smooth Kuwahara filter), removing skin and fabric texture while keeping edges sharp.
2. **Cuts hard shadows**: everything below a threshold becomes flat ink, in black or a chosen colour.
3. **Posterises** the lit areas into a few flat tones.
4. **Blows out** the highlights to near-white.
5. **Reduces the palette** by snapping hues and saturation to fixed steps, or uses a monochrome tint or a single accent colour.
6. **Draws ink outlines** from edge detection.
7. Optionally adds **halftone dots or hatching** along the shadow edge.

It also includes flicker reduction: light/shadow and colour decisions are made from a smoothed
version of the frame, so grain doesn't flip pixels between bands from frame to frame.

## Install

1. Copy `Cellshading-Dominica.dctl` to
   - Windows: `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\LUT\`
   - macOS: `/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/`
   - Linux: `/opt/resolve/LUT/`
2. Restart Resolve, or click **Update Lists** under Project Settings → Color Management.
3. On the Color page, add the **DCTL** effect (OpenFX) to a node and choose **Cellshading-Dominica**.

## Usage

The DCTL expects **Rec.709 Gamma 2.4** input. Put a Color Space Transform (or LUT) that
converts your camera log to Rec.709 on the node before it.

Suggested workflow:

1. Set **View** to *Shadow Matte* and adjust **Shadow Threshold**, **Exposure** and **Contrast** until the black shapes look right. This matters most.
2. Switch to *Tone Bands* and set **Tone Count** and the highlight controls.
3. Switch to *Outline Matte* and tune the outlines.
4. Go back to *Final* and pick colours.

### Main controls

| Control | Effect |
|---|---|
| Shadow Threshold | How much of the image becomes flat ink shadow |
| Shadow Color | Ink Black, Source Hue, Crimson, Navy, Violet or Custom RGB |
| Tone Count | Number of flat tones in the lit areas (1 gives the starkest two-tone look) |
| Exposure / Contrast | Shape brightness before the thresholds are applied |
| Color Mode | Snapped Palette, Monochrome Tint or Single Accent Color |
| Saturation | Colour intensity before palette snapping |
| Highlight Threshold / Blowout | Where and how strongly highlights clip to white |
| Flatten Radius | Strength of the painted-patch smoothing (the most expensive setting) |
| Flicker Reduction | Makes shadow and band shapes steadier on moving footage |
| Outlines / Outline Threshold / Outline Width | Ink lines on edges |
| Shadow Pattern | None, Halftone Dots, Hatching or Cross-Hatching |
| Effect Mix | Blend with the original image |
| View | Final image or debug mattes |

Everything else sits under the **ADVANCED** sections (Tone, Shadow, Highlight, Color,
Outline, Pattern, Flatten, Stability, Output). The checkboxes beside the section headers
do nothing; they are only there to show the headers.

### Presets

The **Preset** menu at the top picks a saved look. *Custom - Use Sliders* uses the sliders.
Any other preset replaces every slider except **Exposure**, **Effect Mix** and **View**, which
stay live so you can adjust each shot.

Built-in presets: Killer7 Classic, Stark Noir, Crimson Ink, Halftone Comic, Pen and Ink,
Sepia Woodcut, Navy Night, Pop Palette, Soft Painted.

To tweak a preset, set the sliders to its values and switch to *Custom*. A DCTL can't move
its own sliders.

#### Saving your own

There are six slots, *User 1* to *User 6*. An empty slot behaves like *Custom*. To fill one:

1. Copy `preset-template.txt`, then type in the values from your DCTL panel. Delete any lines
   you left at the default.
2. Run

   ```
   python save_preset.py 1 --name "Red Room" --values my-look.txt
   ```

   This writes slot 1 into the .dctl, renames it in the menu and installs it into Resolve's
   LUT folder (Windows).
3. In Resolve, re-select the DCTL on the node to load the new version.

To rename a slot, use `--name` on its own. To empty it, use `--clear`. Names may only contain
letters, digits, spaces, `:` and `-`, because other characters crash Resolve's DCTL parser.

To keep the whole node quickly without editing the file, right-click the viewer and choose
**Grab Still**. Apply it to other clips from the Gallery. This also works for any setup.

## Performance

**Flatten Radius** is the expensive control. On weaker GPUs, keep it at 0–2 while grading and
raise it only for the final render.

## Flicker

A DCTL can only see one frame at a time, so some flicker near the thresholds is unavoidable.
To reduce it:
- Raise **Flicker Reduction**.
- Put temporal noise reduction before this node.
- Add Resolve's **Deflicker** effect after it.

## License

MIT, see [LICENSE](LICENSE). Free to use, modify and share, including commercially.
