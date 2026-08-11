# Publish this repo (you run these)

Local docs + agent prompt are ready. Creating a **public** GitHub repo is a write to public GitHub — run this yourself (or reply **publish AlexBodner/alexs-rig** and confirm).

```bash
cd ~/Projects/alexs-rig-proto

# optional rename locally
# cd .. && mv alexs-rig-proto alexs-rig && cd alexs-rig

gh repo create alexs-rig --public --source=. --remote=origin --description "Personal Claude Code harness: L0 memory, batch review loop, agent-iterable docs"
git push -u origin main
```

After publish, update `README.md` clone URL if needed.

## Give to a Grok bot

1. Clone the public repo (or open this folder).  
2. New agent chat → paste **entire** `prompts/AGENT_ITERATE.md` (below the horizontal rule).  
3. Let it iterate backlog item 1+; you review PRs/commits.
