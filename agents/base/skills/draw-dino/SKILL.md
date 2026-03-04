---
name: draw-dino
description: Draw an ASCII art dinosaur. Use this skill when the user asks for a dinosaur, dino, asks you to draw a dino, wants ASCII art of a dinosaur, or says things like "rawr", "show me a dino", "draw a T-Rex", or references any dinosaur species.
argument-hint: "[species]"
---

## What This Skill Does

This skill draws ASCII art dinosaurs. It supports multiple species and styles.

## Instructions

When invoked, pick an appropriate dinosaur based on the user's request. If no specific species is mentioned, pick one yourself. Always output the ASCII art inside a code block so spacing is preserved.

## Customization

- If the user asks for a **cute** or **baby** dino, use the Baby Dino.
- If the user asks for a **flying** dinosaur, use the Pterodactyl.
- If the user asks for something **scary** or **fierce**, use the T-Rex or Velociraptor.
- If the user asks for something **big** or **gentle**, use the Brontosaurus.

## Workflow

1. Note the type of dinosaur and prompt customization, if one is given. Choose a classic if one is not.
2. Freestyle draw your own dinosaur.
3. After drawing, add a short fun dinosaur fact related to the species you drew.
