#!/usr/bin/env node
// Runs at `npm pack` / `npm publish`: the skills live at the repository root, and npm can only
// ship what is inside the package folder, so they are copied in before the tarball is built.
// The copy is git-ignored and rebuilt every time, so the two can never drift apart.

"use strict";

const { cpSync, existsSync, readdirSync, rmSync } = require("node:fs");
const { join } = require("node:path");

const from = join(__dirname, "..", "skills");
const to = join(__dirname, "skills");

if (!existsSync(from)) {
  process.stderr.write(`copy-skill: no skills at ${from}\n`);
  process.exit(1);
}

rmSync(to, { recursive: true, force: true });
for (const name of readdirSync(from)) {
  if (!existsSync(join(from, name, "SKILL.md"))) continue;
  cpSync(join(from, name), join(to, name), { recursive: true });
  process.stderr.write(`copy-skill: ${name}\n`);
}
