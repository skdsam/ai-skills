---
name: anymachine
description: Build reference-driven mechanical models, articulated rigs and detailed hard-surface props in Blender Python using the AnyMachine pipeline. Use for machines with working joints, hydraulics, checked animation and verified GLB export.
---

# AnyMachine

This local wrapper adapts the upstream AnyMachine pipeline, which has no SKILL.md. Read [PIPELINE.md](PIPELINE.md) for the workflow. Example paths in that guide refer to the upstream repository, not files bundled here; retrieve examples at the revision recorded in PROVENANCE.json when needed.

Start with approved reference views and mechanism close-ups, then define scale, axes, load paths, parts and joints before modelling. Build real parts in Blender Python; render comparisons, check joint sweeps and intersections, and re-import exports to verify them. Use part 2 for static hard-surface props.

The worked examples require Blender 5.2; older experiments use 5.0. Verify other versions at runtime before claiming compatibility. Reference-image and motion generation are optional external steps requiring available tools and user authorization. This skill does not install Blender, API keys or remote services. Preserve the user's excluded-engine preferences.
