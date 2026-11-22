# The reference-first pipeline

How a machine goes from one painting to a rigged, animated, exported model that is built entirely by a script.
[`stilt/`](stilt/NOTES.md) is the worked example; every file named below exists there.

Part 1 (below) is for machines that move. [Part 2](#part-2-complicated-static-objects) is the same method for
complicated objects that do not: a lifeboat station, a helicopter, a kit of equipment.

This is written for two readers: a person who wants to know how the Stilt was made, and an agent that is asked to
build the next machine. The Stilt was built by an agent (Claude Fable 5.2 in Claude Code) working through these
steps, with a person choosing the design, approving each set of references and judging the result.

## The idea

A generator can give you a mesh of a machine, but not one whose joints work. A modeller can build working joints,
but needs to know what each one looks like up close. So the pipeline spends its effort on **references**: it turns
one concept image into the set of drawings a modeller would ask for, and only then writes geometry. Nothing is
modelled from a whole-body picture alone.

The model itself is code. One Python script builds every part, the materials, the UVs, the rig and the animations
when it is run in Blender. A change to the design is a change to the script, and the whole machine rebuilds.

## Steps

| # | Step | What is made | In `stilt/` |
|---|---|---|---|
| 1 | Concept | One painting of the machine in its world, with a person for scale | `refs/concept_sheet.png` |
| 2 | Turnaround | The same machine, clean, on grey: front, side, rear, top, three-quarter | `refs/stilt_turnaround.png`, `jobs_turnaround.json` |
| 3 | Single views | Each view on its own, large enough to measure | `refs/stilt_front / left / rear / top / 3q.png`, `jobs_views.json` |
| 4 | Close-up plates | One plate per mechanism, then three more angles of each | `refs/closeup_*.png`, `jobs_closeups.json`, `jobs_closeup_angles.json` |
| 5 | Parts breakdown | Scale, axes, dimensions, every part and bone, written before modelling | `PARTS.md` |
| 6 | Build script | Geometry, materials, UVs, bake, rig, actions, export | `build_stilt.py` |
| 7 | Check renders | The model framed like each reference, placed beside it | `render_stilt.py`, `renders/stilt_compare_*.jpg` |
| 8 | Motion reference | Short video-model clips made from renders of the model, read for timing | `refs/motion/`, `jobs_motion.json` |
| 9 | Animation | Actions written in the build script, checked for parts passing through each other | `render_stilt.py -- check` |
| 10 | Export and verify | GLB and FBX, re-imported into an empty scene and compared | `verify_glb.py` |

### 1 to 4: references

Each step feeds the one before it back in as an image reference, so the design does not drift:

- The **turnaround** is generated from the concept plus crops of it.
- The **single views** are generated from the turnaround plus the concept.
- Each **close-up plate** is generated from the side view, the front view, the turnaround and the concept. The
  prompt asks for a studio product render of one area "for a 3D modeller", with every part "readable and physically
  plausible as real heavy engineering", on flat grey, no labels.

Rules that made the references usable:

- **One plate per mechanism, not per body area.** Hip, knee, foot, hand, head, shoulder, elbow. Then front, rear and
  inner or top angles of each, because a joint cannot be modelled from one side.
- **Approve before going on.** A person looks at each set. A wrong turnaround makes every later image wrong.
- **Say the scale in the prompt** ("a joint housing is 1.5 to 2.5 m across"), or the plates come back with details
  sized for a toy.
- **Keep the prompts.** The `jobs_*.json` files are the record of how each image was asked for; `edit.ps1` runs them.

The images here were made with GPT Image 2.6 on fal. Any image model that accepts reference images will do.

### 5: parts breakdown

Written before any geometry, from measurements taken off the single views (pixels per metre, where the ground and
the top are, where each joint sits). It fixes:

- the axes and the origin;
- overall dimensions and the size of every joint housing;
- **how the machine carries its own weight.** For the Stilt this was the decision to build each leg as a guyed mast
  (a compression beam, tension cables on spreaders, an actuator across each joint). This is what makes thin legs
  believable, and it came from asking the question, not from the references;
- the part list with the bone each part rides on;
- where the views disagree and which one wins.

### 6: build script

One file, run headless. In order: a solver for the limb poses, part builders, instancing of the repeated limbs,
materials, UV layouts, a texture bake, the armature, skinning (every rigid part to exactly one bone), the actions,
export. Habits worth copying:

- **Every joint is a real mechanism**: fork and tongue on a pin, a drum with a bolted flange, a two-part hydraulic
  cylinder whose halves are on their own bones and aim at each other.
- **Let the script pick what a person would fudge.** The actuator anchor points are chosen by sampling every action
  and keeping the points where the rod stays inside its cylinder over the whole stroke with the largest lever arm.
  The build fails if a rod could leave its cylinder.
- **Assert the rules.** No mesh shares a name with a bone; the bake is refused if the topology changed.
- **Write the numbers out.** `stilt_info.json` holds every part, bone, rest axis and stroke for whoever imports it.

### 7: check renders

`render_stilt.py` renders the model from the camera of each reference, and the comparison images put reference and
model side by side. This is the step that keeps the build honest: differences are listed in the notes
("What differs from the references") instead of being left for someone to find.

### 8 and 9: motion

A 30 m machine has no motion capture. Renders of the finished model are given to an image-to-video model with a
prompt for the movement ("like a giraffe or a heron filmed in slow motion"). The clips are **read, not tracked**:
frame strips show the order of the feet, how long each is in the air, when the body dips. Those timings go into the
actions in the build script. The first walk moved one foot at a time; the clips showed overlapping steps, and the
walk was rewritten.

After every animation change, the clash check compares every part against every part on another bone through all
actions and reports any intersection that is not there in the rest pose.

### 10: export and verify

The GLB and FBX are re-imported into empty scenes and counted: bones, meshes, actions and their lengths. The GLB is
rendered on its own, so what a plain viewer shows is known.

## Building the next machine

1. Make a folder beside `stilt/` and copy `edit.ps1`, `video.ps1` and the `jobs_*.json` files as templates. Rewrite
   the prefix of each jobs file to describe the new machine.
2. Do steps 1 to 4, stopping for approval after the turnaround and after the first plates.
3. Write `PARTS.md`. Do not start the script until the load path and the joint types are decided.
4. Write the build script. Reuse the solver, the actuator anchor search, the bake and the export from
   `build_stilt.py`; the part builders are specific to each machine.
5. Render the comparisons, list the differences, fix or accept each one.
6. Motion reference, actions, clash check, export, verify.

## What it costs

This is not one prompt. The Stilt has 40 reference images, each generated from the ones before it and looked at by
a person, a build script of about 2,200 lines, and some 40 check and comparison renders. It was the fourth machine
built this way, and the steps above are what survived from the first three. What generalises is the order of work
and the checks, and the parts of the script named in step 4 above.

## Needs

- Blender 5.2 (5.0 runs the older experiments in this repo).
- `FAL_KEY` in the environment, only for regenerating references and motion clips. Building, rendering and
  verifying need no network.
- ffmpeg, for the videos.

# Part 2: complicated static objects

The steps above end in a machine that walks. Most of what a game level needs does not move, but has a great deal on
it: a lifeboat on its davit, a helicopter, a hydraulic power unit. This part is how those are built. It is the same
idea, references first and the model as code, with the rig and animation steps taken out and two added: a second
pass against the references, and a texture bake on a GPU render farm. [`hardsurface/`](hardsurface/NOTES.md) is the
worked example: a lifeboat station, a helicopter, twelve pieces of equipment, nineteen light fixtures and three
rifles, built by an agent (Claude Fable 5.2 in Claude Code) for one map of a browser FPS.

## The rule

**Anything with more than a few parts gets reference sheets first, then is modelled to them.** Image-to-3D
generators are not used for these. The first lifeboat on that map was a generated mesh; it had the right outline and
nothing underneath it, no hinges, no hooks, no winch you could follow a wire to, and it was rejected on sight. A
generated mesh is still fine as a skin to measure joints off (the laptop and quadruped in this repo) or for a
background prop nobody walks up to.

## Steps

| # | Step | What is made | In `hardsurface/rig2_blender/kit/` |
|---|---|---|---|
| 1 | Overall sheet | One object from six directions on grey, five of them orthographic | `sheets/<id>_turn.jpg`, `gen_sheets.mjs` |
| 2 | Close-up sheets | Six construction close-ups per sheet; more sheets for busier objects | `sheets/<id>_detail.jpg`, `_close1.jpg`, `aircraft/helicopter/sheets/` |
| 3 | Model, part by part | One script per object that builds every real part as its own mesh | `<family>/<id>/build.py` |
| 4 | Compare | The model from the sheet's own six directions, beside the sheet | `<family>/<id>/review.jpg` |
| 5 | Second pass | What the comparison showed missing, added; more close-ups generated where needed | `equipment/review_pass2.jpg` |
| 6 | Bake | Wear and fine detail baked to base colour, normal and ORM maps, on a GPU render farm | `--size`, `--spp` on each `build.py` |
| 7 | Export | `.blend`, `.glb`, the texture set and a stats file | `stats.json` |

### 1 and 2: sheets

The sheet replaces the brief. Proportions, part breakdown, fastener spacing, colour and wear are read off it; sizes
come from where the object has to fit.

- **The overall sheet** is asked for as "a technical reference sheet for 3D modelling, showing ONE object from six
  directions", photographic, with true orthographic elevations at one scale, no labels, and the real size in metres
  in the prompt. If the object appears in an approved concept image of the scene, that image goes in as the input so
  the object matches its surroundings.
- **Close-up sheets** take the overall sheet as their input image, so they show the same object. The first is
  generic (a corner, a joint, the foot, a working detail, a plain surface, the most worn spot). The rest name what
  they want, one mechanism per panel, usually square-on and then from the side: "one master gate valve seen
  square-on from the front", then "the same master valve from the side, showing how far the bonnet and handwheel
  stand off". The helicopter has eight such sheets.
- **How many.** Two sheets for a simple fixture. Three for a piece of equipment with a mechanism. Six for the
  lifeboat station, ten for the helicopter. If a part cannot be modelled from what the sheets show, that is a
  missing sheet, not a licence to guess.
- **Look at each sheet before using it.** One equipment sheet came back with its lifting sling drawn in the air
  above the box and was regenerated.

### 3: model, part by part

One Python script per object, run headless in Blender, on a small shared kit of part builders (`hs.py` and the
family helpers on top of it: boxes with skipped hidden faces, prisms, lathes, pipes with bends, flanges with bolt
circles, hinges, handwheels, gratings, welds).

- **Write the part list first, as the script's header comment**, then build the list in order. A part is something
  that would be a separate piece of metal: build it as a separate mesh and let it touch its neighbours where the
  real one would be bolted or welded.
- **Two kinds of geometry.** What changes the silhouette at playing distance is real geometry. Bolt heads, weld
  beads, rivets, panel joints and anything else under about 8 mm is built too, but flagged bake-only: it shapes the
  normal map and is not in the exported mesh. The equipment pieces are 2,000 to 6,000 triangles with 5,000 to
  35,000 triangles of bake-only detail behind them.
- **Budget and size are asserted.** The build prints triangles and the bounding-box error against the intended
  size, and the brief gives a limit for both.
- **Say where you left the sheet.** When the object has to be taller, shorter or closed where the sheet's is open,
  the header says what was changed and why.

### 4 and 5: compare, then a second pass

A build that ran without errors proves nothing about how it looks. Every object is rendered from the same six
directions as its overall sheet, same framing, flat light, and the two are put side by side. Big objects are also
rendered from the camera of each close-up panel. The agent looks at the pairs and writes down what differs.

The first pass is reliably plainer than the sheet: the right parts, too few of them, too regular. So there is a
second pass, and it is planned for, not a repair. It adds what the comparison showed missing, and for the busiest
objects it starts by generating one more close-up sheet of the parts that came out as plain boxes.

### 6: bake, on a GPU render farm

Each material is a wear shader over a tiling paint or metal texture: chipped edges, grime runs under anything that
sheds water, rust bleed at feet and bolts, stains and decals. That and the bake-only geometry are baked in Cycles to
one texture set per object (base colour, normal, occlusion / roughness / metal), or to one set shared by a whole
family when its members are small and instanced many times, like the light fixtures.

Baking is the slow part and it is independent per object, so it goes to a GPU render farm: one job per object or per
texture set, all running at once. What that asks of the scripts:

- a build must run unattended from one command and take `--size` and `--spp`;
- it must find everything by paths relative to itself, and need nothing from the network;
- the comparison render is a separate script or a flag, so the bake does not need the sheets;
- it must exit non-zero if no texture was written.

Locally only geometry checks (`--nobake`) and small preview bakes are run. The same split works for film: the
lifeboat's making-of film is rendered as independent frame ranges, one range per job.

### 7: export

`.blend` and `.glb`, with the stats. Then the things only the destination can tell you: collision boxes measured off
the model, what in the level is in the way, what has not been checked in the engine. The helicopter's folder has
its proposed collision boxes; its notes say it has not been loaded in the game.

## What it costs, and what it does not give you

The helicopter is ten sheets, about 950 lines of Python, three texture sets and some forty comparison stills. The
equipment kit is 31 sheets and twelve scripts of 80 to 250 lines.

The results are game props, not film assets, and beside their sheets they are still simpler and flatter: fewer
pipes, blockier castings, sparser rivets, even wear. The sheets are generated pictures whose views do not always
agree, so they fix the look and not the dimensions. And a person still decides: which design, whether a sheet is
right, whether the result is good enough. [`hardsurface/NOTES.md`](hardsurface/NOTES.md#where-it-falls-short) lists
the specific shortfalls.
