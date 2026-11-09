#!/usr/bin/env node
// Launcher for `npx -y @gribanoveu/mcp-testops`.
//
// It runs the standalone binary of the matching platform from the GitHub release: no
// Python, no build, one command. Nothing is ever written to stdout - stdout belongs to
// the MCP protocol, so every message of this launcher goes to stderr.

"use strict";

const { spawn } = require("node:child_process");
const { chmodSync, createWriteStream, existsSync, mkdirSync } = require("node:fs");
const { get } = require("node:https");
const { homedir } = require("node:os");
const { join } = require("node:path");

const pkg = require("./package.json");

function fail(message) {
  process.stderr.write(`mcp-testops: ${message}\n`);
  process.exit(1);
}

function platformName() {
  const arch = process.arch === "arm64" ? "arm64" : "x64";
  if (process.platform === "darwin") return `darwin-${arch}`;
  if (process.platform === "linux") return `linux-${arch}`;
  if (process.platform === "win32") return "win32-x64";
  fail(`unsupported platform ${process.platform}/${process.arch}`);
}

const platform = platformName();
if (platform === "darwin-x64") {
  fail(
    "no Intel macOS binary is published; use `uvx mcp-testops` or the wheel from the release " +
      "(https://github.com/gribanoveu/mcp-testops/releases)",
  );
}
const exe = process.platform === "win32" ? ".exe" : "";
const asset = `mcp-testops-${platform}${exe}`;
const cacheDir = join(homedir(), ".cache", "mcp-testops", pkg.version);
const binary = join(cacheDir, asset);
const url = `https://github.com/gribanoveu/mcp-testops/releases/download/v${pkg.version}/${asset}`;

function run() {
  if (process.platform !== "win32") chmodSync(binary, 0o755);
  const child = spawn(binary, process.argv.slice(2), { stdio: "inherit" });
  child.on("error", (error) => fail(`cannot start ${binary}: ${error.message}`));
  child.on("exit", (code, signal) => process.exit(signal ? 1 : code === null ? 0 : code));
}

function download(source, target, redirects) {
  if (redirects > 5) return fail(`too many redirects for ${source}`);
  const request = get(source, { headers: { "user-agent": `mcp-testops/${pkg.version}` } }, (response) => {
    const status = response.statusCode || 0;
    if (status >= 300 && status < 400 && response.headers.location) {
      response.resume();
      // GitHub redirects release assets to objects.githubusercontent.com.
      return download(response.headers.location, target, redirects + 1);
    }
    if (status !== 200) {
      response.resume();
      return fail(`HTTP ${status} on ${source}`);
    }
    const file = createWriteStream(target);
    response.pipe(file);
    file.on("finish", () => file.close(run));
    file.on("error", (error) => fail(`cannot write ${target}: ${error.message}`));
  });
  request.on("error", (error) => fail(`cannot download ${source}: ${error.message}`));
}

if (existsSync(binary)) {
  run();
} else {
  mkdirSync(cacheDir, { recursive: true });
  process.stderr.write(`mcp-testops: downloading ${asset} (v${pkg.version})\n`);
  download(url, binary, 0);
}
