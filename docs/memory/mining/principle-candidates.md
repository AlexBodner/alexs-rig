# Principle candidates

Named clusters auto-upsert into L0 unless `--no-apply`. `other` is skipped unless `--apply-other`.
Duplicates of existing principles are skipped. Forget with `principle-forget --id P-mine-<cluster>`.

## P-mine-other (other, evidence≈72)
- proposed: Capture standing preferences as id-addressable principles (review noisy `other` evidence before keeping).
- evidence sample: untimeError Traceback (most recent call last) Cell In[23], line 50 48 for col, idx in enumerate(high_risk_indices): 49 ndvi_t, tab_t, _ = test_dataset[idx] ---> 50 cam = compute_gradcam(hybrid_model, 
- status: skipped (other/low-evidence)

## P-mine-review_batch (review_batch, evidence≈20)
- proposed: Prefer batch review (Desktop +N -M / IDE SCM) over stop-on-every-edit; use Edit automatically after Plan.
- evidence sample: I want you to first understand what we want and are trying to do and then to review each pr and all the code that we have to find if we are properly doing what we claim for (eg, if we say we are using
- status: skipped (already in L0)

## P-mine-commit_git (commit_git, evidence≈15)
- proposed: Agent may commit when asked; no silent auto-PR; review uncommitted changes before ship.
- evidence sample: i want to recheck what we change in the readme in this draft PR. Lets not name YOLO if its not named in the main branch. Also i dont want the focus mode that is speed + distance of player to be referr
- status: skipped (already in L0)

## P-mine-memory_l0 (memory_l0, evidence≈8)
- proposed: Keep L0 a small generated snapshot of current principles/progress/pending; upsert by id; never mix SUPERSEDED into L0.
- evidence sample: Place fixes where the code was introduced Implement the plan as specified, it is attached for your reference. Do NOT edit the plan file itself. To-do's from the plan have already been created. Do not 
- status: **applied**

## P-mine-ux_simple (ux_simple, evidence≈5)
- proposed: Daily UX first — tomorrow-morning test; plain files for standing state; invisible complexity under CLIs.
- evidence sample: i see that the images generated seemed to rollback to like simple lines like we had before instead of nicer ones
- status: **applied**
