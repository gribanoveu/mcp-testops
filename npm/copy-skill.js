#!/usr/bin/env node
// Runs at `npm pack` / `npm publish`: the skill lives at the repository root, and npm can only
// ship what is inside the package folder, so it is copied in before the tarball is built.
// The copy is git-ignored and rebuilt every time, so the two can never drift apart.

"use strict";

const { cpSync, existsSync, rmSync } = require("node:fs");
const { join } = require("node:path");

const from = join(__dirname, "..", "skills", "testops-mcp");
const to = join(__dirname, "skills", "testops-mcp");

if (!existsSync(join(from, "SKILL.md"))) {
  process.stderr.write(`copy-skill: no skill at ${from}\n`);
  process.exit(1);
}

rmSync(to, { recursive: true, force: true });
cpSync(from, to, { recursive: true });
process.stderr.write(`copy-skill: ${from} -> ${to}\n`);
