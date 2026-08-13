#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const REVIEWED_NAME = "reviewed.json";
const prCache = new Map();

function git(root, args, extraEnv) {
  const r = spawnSync("git", ["-C", root, ...args], {
    encoding: "utf8",
    env: extraEnv ? { ...process.env, ...extraEnv } : process.env,
    timeout: 30000,
  });
  return {
    code: r.status === null ? 1 : r.status,
    stdout: r.stdout || "",
    stderr: r.stderr || "",
  };
}

function findProjectRoot(start) {
  let cur = path.resolve(start);
  for (let i = 0; i < 8; i++) {
    if (fs.existsSync(path.join(cur, ".git")) || fs.existsSync(path.join(cur, "docs", "memory"))) {
      return cur;
    }
    const parent = path.dirname(cur);
    if (parent === cur) {
      break;
    }
    cur = parent;
  }
  return path.resolve(start);
}

function reviewedPath(root) {
  return path.join(root, ".alexs-rig", REVIEWED_NAME);
}

function loadReviewed(root) {
  const p = reviewedPath(root);
  if (!fs.existsSync(p)) {
    return {};
  }
  try {
    const data = JSON.parse(fs.readFileSync(p, "utf8"));
    if (!data || typeof data !== "object" || Array.isArray(data)) {
      return {};
    }
    const out = {};
    for (const [k, v] of Object.entries(data)) {
      out[String(k)] = String(v);
    }
    return out;
  } catch {
    return {};
  }
}

function saveReviewed(root, mapping) {
  const dest = path.join(root, ".alexs-rig");
  fs.mkdirSync(dest, { recursive: true });
  const keys = Object.keys(mapping).sort();
  const ordered = {};
  for (const k of keys) {
    ordered[k] = mapping[k];
  }
  fs.writeFileSync(reviewedPath(root), JSON.stringify(ordered, null, 2) + "\n", "utf8");
}

function sessionBase(root) {
  const p = path.join(root, ".alexs-rig", "SESSION_BASE");
  if (!fs.existsSync(p)) {
    return "";
  }
  return fs.readFileSync(p, "utf8").trim();
}

function head(root) {
  const r = git(root, ["rev-parse", "HEAD"]);
  return r.code === 0 ? r.stdout.trim() : "";
}

function mergeBase(root, baseRef) {
  if (!baseRef) {
    return "";
  }
  for (const ref of [`origin/${baseRef}`, baseRef]) {
    const r = git(root, ["merge-base", "HEAD", ref]);
    if (r.code === 0 && r.stdout.trim()) {
      return r.stdout.trim();
    }
  }
  return "";
}

function invalidatePrCache() {
  prCache.clear();
}

function currentPrUncached(root) {
  const r = spawnSync("gh", ["pr", "view", "--json", "number,url,baseRefName,title"], {
    cwd: root,
    encoding: "utf8",
    timeout: 15000,
  });
  if (r.status !== 0) {
    return null;
  }
  try {
    const j = JSON.parse(r.stdout || "{}");
    if (!j.number) {
      return null;
    }
    const base = mergeBase(root, j.baseRefName);
    if (!base) {
      return null;
    }
    return {
      number: j.number,
      url: j.url || "",
      title: j.title || "",
      baseRefName: j.baseRefName,
      mergeBase: base,
    };
  } catch {
    return null;
  }
}

function currentPr(root) {
  const hit = prCache.get(root);
  if (hit && Date.now() - hit.at < 8000) {
    return hit.value;
  }
  const value = currentPrUncached(root);
  prCache.set(root, { at: Date.now(), value });
  return value;
}

function compareSha(root, mode) {
  if (mode === "pr") {
    const pr = currentPr(root);
    if (pr && pr.mergeBase) {
      return pr.mergeBase;
    }
  }
  return sessionBase(root) || head(root);
}

function fileDigest(root, rel) {
  const file = path.join(root, rel);
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) {
    return "";
  }
  const r = git(root, ["hash-object", file]);
  return r.code === 0 ? r.stdout.trim() : "";
}

function workingTreeDiff(root, sha, extraArgs) {
  if (!sha) {
    return { code: 1, stdout: "" };
  }
  const dest = path.join(root, ".alexs-rig");
  fs.mkdirSync(dest, { recursive: true });
  const env = { GIT_INDEX_FILE: path.join(dest, "review-pending.index") };
  git(root, ["add", "-A", "--", ".", ":!.alexs-rig"], env);
  return git(root, ["diff", "--cached", ...extraArgs, sha, "--"], env);
}

function dirtyAt(root, sha) {
  if (!sha) {
    return [];
  }
  const r = workingTreeDiff(root, sha, ["--name-only"]);
  if (r.code !== 0) {
    return [];
  }
  return r.stdout
    .split("\n")
    .map((n) => n.trim())
    .filter((n) => n && !n.startsWith(".alexs-rig/"));
}

function dirtyNames(root, mode) {
  return dirtyAt(root, compareSha(root, mode || "session"));
}

function isViewed(root, rel, mapping) {
  const map = mapping || loadReviewed(root);
  return map[rel] === fileDigest(root, rel);
}

function pendingNames(root, mode) {
  const mapping = loadReviewed(root);
  return dirtyNames(root, mode).filter((rel) => !isViewed(root, rel, mapping));
}

function clearStopReminded(root) {
  const p = path.join(root, ".alexs-rig", "STOP_REMINDED");
  if (fs.existsSync(p)) {
    fs.unlinkSync(p);
  }
}

function markFiles(root, rels) {
  const mapping = loadReviewed(root);
  for (let rel of rels) {
    rel = rel.replace(/\\/g, "/").replace(/^\.\//, "");
    mapping[rel] = fileDigest(root, rel);
  }
  saveReviewed(root, mapping);
  clearStopReminded(root);
  return rels;
}

function unmarkFiles(root, rels) {
  const mapping = loadReviewed(root);
  for (let rel of rels) {
    rel = rel.replace(/\\/g, "/").replace(/^\.\//, "");
    delete mapping[rel];
  }
  saveReviewed(root, mapping);
  return rels;
}

function markAllPending(root, mode) {
  return markFiles(root, pendingNames(root, mode));
}

function defaultMode(root) {
  return currentPr(root) ? "pr" : "session";
}

module.exports = {
  compareSha,
  currentPr,
  defaultMode,
  dirtyAt,
  dirtyNames,
  fileDigest,
  findProjectRoot,
  invalidatePrCache,
  isViewed,
  loadReviewed,
  markAllPending,
  markFiles,
  mergeBase,
  pendingNames,
  sessionBase,
  unmarkFiles,
};

if (require.main === module) {
  const cmd = process.argv[2] || "pending";
  const root = findProjectRoot(process.argv[3] || process.cwd());
  const rest = process.argv.slice(4);
  if (cmd === "dirty") {
    const names = dirtyNames(root, rest[0] || "session");
    process.stdout.write(names.join("\n") + (names.length ? "\n" : ""));
  } else if (cmd === "dirty-at") {
    const names = dirtyAt(root, rest[0] || "");
    process.stdout.write(names.join("\n") + (names.length ? "\n" : ""));
  } else if (cmd === "pending") {
    const names = pendingNames(root, rest[0] || "session");
    process.stdout.write(names.join("\n") + (names.length ? "\n" : ""));
  } else if (cmd === "mark") {
    markFiles(root, rest);
  } else if (cmd === "unmark") {
    unmarkFiles(root, rest);
  } else if (cmd === "mark-all") {
    markAllPending(root, rest[0] || "session");
  } else if (cmd === "merge-base") {
    process.stdout.write(mergeBase(root, rest[0] || "main") + "\n");
  } else if (cmd === "pr") {
    const pr = currentPr(root);
    process.stdout.write(pr ? JSON.stringify(pr) + "\n" : "");
  } else {
    process.stderr.write(
      "usage: node store.js dirty|pending|mark|unmark|mark-all|dirty-at|merge-base|pr [root] [args…]\n"
    );
    process.exit(2);
  }
}
