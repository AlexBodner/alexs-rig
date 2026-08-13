"use strict";

const path = require("path");
const vscode = require("vscode");
const store = require("./store");

const MODE_KEY = "alexsRig.review.mode";

function workspaceRoot() {
  const folder = vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders[0];
  const start = folder ? folder.uri.fsPath : process.cwd();
  return store.findProjectRoot(start);
}

class ReviewProvider {
  constructor(getMode) {
    this.getMode = getMode;
    this._onDidChangeTreeData = new vscode.EventEmitter();
    this.onDidChangeTreeData = this._onDidChangeTreeData.event;
  }

  refresh() {
    this._onDidChangeTreeData.fire();
  }

  getTreeItem(rel) {
    const root = workspaceRoot();
    const mode = this.getMode();
    const item = new vscode.TreeItem(rel, vscode.TreeItemCollapsibleState.None);
    const viewed = store.isViewed(root, rel);
    item.checkboxState = viewed
      ? vscode.TreeItemCheckboxState.Checked
      : vscode.TreeItemCheckboxState.Unchecked;
    item.tooltip = viewed
      ? "Viewed — unchecks if the file content changes"
      : "Not viewed";
    item.resourceUri = vscode.Uri.file(path.join(root, rel));
    item.command = {
      command: "alexsRig.review.openDiff",
      title: "Open Diff",
      arguments: [rel],
    };
    item.contextValue = viewed ? "viewedFile" : "pendingFile";
    const sha = store.compareSha(root, mode);
    item.id = `${mode}:${sha}:${rel}`;
    return item;
  }

  getChildren() {
    try {
      return store.dirtyNames(workspaceRoot(), this.getMode());
    } catch {
      return [];
    }
  }
}

async function openDiff(rel, getMode) {
  const root = workspaceRoot();
  const mode = getMode();
  const sha = store.compareSha(root, mode);
  const fileUri = vscode.Uri.file(path.join(root, rel));
  const gitExt = vscode.extensions.getExtension("vscode.git");
  let left = fileUri;
  if (gitExt && sha) {
    if (!gitExt.isActive) {
      await gitExt.activate();
    }
    const api = gitExt.exports.getAPI(1);
    left = api.toGitUri(fileUri, sha);
  }
  const label = mode === "pr" ? `${rel} (PR)` : `${rel} (session)`;
  try {
    await vscode.workspace.fs.stat(fileUri);
    await vscode.commands.executeCommand("vscode.diff", left, fileUri, label);
  } catch {
    await vscode.commands.executeCommand("vscode.open", left);
  }
}

function activate(context) {
  const getMode = () => {
    const root = workspaceRoot();
    const stored = context.workspaceState.get(MODE_KEY);
    const pr = store.currentPr(root);
    if (stored === "pr" && !pr) {
      return "session";
    }
    if (stored === "session" || stored === "pr") {
      return stored;
    }
    return pr ? "pr" : "session";
  };

  const provider = new ReviewProvider(getMode);
  const treeView = vscode.window.createTreeView("alexsRig.review", {
    treeDataProvider: provider,
    showCollapseAll: false,
    manageCheckboxStateManually: true,
  });

  const refreshBadge = () => {
    try {
      const root = workspaceRoot();
      const mode = getMode();
      const n = store.pendingNames(root, mode).length;
      const pr = mode === "pr" ? store.currentPr(root) : null;
      const src = pr ? `PR #${pr.number}` : "session";
      treeView.badge = n ? { value: n, tooltip: `${n} not viewed (${src})` } : undefined;
      treeView.description = n ? `${src} · ${n} pending` : `${src} · all viewed`;
    } catch {
      treeView.badge = undefined;
      treeView.description = "";
    }
  };

  let timer;
  const scheduleRefresh = () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      store.invalidatePrCache();
      provider.refresh();
      refreshBadge();
    }, 300);
  };

  treeView.onDidChangeCheckboxState((e) => {
    const root = workspaceRoot();
    const mark = [];
    const unmark = [];
    for (const [rel, state] of e.items) {
      if (state === vscode.TreeItemCheckboxState.Checked) {
        mark.push(rel);
      } else {
        unmark.push(rel);
      }
    }
    if (mark.length) {
      store.markFiles(root, mark);
    }
    if (unmark.length) {
      store.unmarkFiles(root, unmark);
    }
    scheduleRefresh();
  });

  const setMode = async (mode) => {
    if (mode === "pr" && !store.currentPr(workspaceRoot())) {
      vscode.window.showInformationMessage("No pull request for this branch. Checkout a PR branch, or stay on Session.");
      return;
    }
    await context.workspaceState.update(MODE_KEY, mode);
    scheduleRefresh();
  };

  const reviewedWatch = vscode.workspace.createFileSystemWatcher("**/.alexs-rig/reviewed.json");
  const baseWatch = vscode.workspace.createFileSystemWatcher("**/.alexs-rig/SESSION_BASE");
  reviewedWatch.onDidChange(scheduleRefresh);
  reviewedWatch.onDidCreate(scheduleRefresh);
  reviewedWatch.onDidDelete(scheduleRefresh);
  baseWatch.onDidChange(scheduleRefresh);
  baseWatch.onDidCreate(scheduleRefresh);
  baseWatch.onDidDelete(scheduleRefresh);

  context.subscriptions.push(
    treeView,
    reviewedWatch,
    baseWatch,
    vscode.workspace.onDidSaveTextDocument(scheduleRefresh),
    vscode.commands.registerCommand("alexsRig.review.refresh", scheduleRefresh),
    vscode.commands.registerCommand("alexsRig.review.useSession", () => setMode("session")),
    vscode.commands.registerCommand("alexsRig.review.usePr", () => setMode("pr")),
    vscode.commands.registerCommand("alexsRig.review.markAll", () => {
      store.markAllPending(workspaceRoot(), getMode());
      scheduleRefresh();
    }),
    vscode.commands.registerCommand("alexsRig.review.openDiff", (rel) => openDiff(rel, getMode))
  );

  const gitExt = vscode.extensions.getExtension("vscode.git");
  if (gitExt) {
    gitExt.activate().then((exp) => {
      const api = exp.getAPI(1);
      const subRepo = (repo) => context.subscriptions.push(repo.state.onDidChange(scheduleRefresh));
      api.repositories.forEach(subRepo);
      context.subscriptions.push(api.onDidOpenRepository(subRepo));
    });
  }

  refreshBadge();
}

function deactivate() {}

module.exports = { activate, deactivate };
