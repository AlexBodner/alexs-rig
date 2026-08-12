# Principle candidates (DO NOT auto-apply)

Accept with:
```
./bin/principle-upsert --id P-… --text "…"
```

## P-mine-1 (other, evidence≈72)
- proposed: Capture standing preferences as id-addressable principles after human review.
- evidence sample: untimeError Traceback (most recent call last) Cell In[23], line 50 48 for col, idx in enumerate(high_risk_indices): 49 ndvi_t, tab_t, _ = test_dataset[idx] ---> 50 cam = compute_gradcam(hybrid_model, 

## P-mine-2 (review_batch, evidence≈20)
- proposed: Prefer batch review (Desktop +N -M / IDE SCM) over stop-on-every-edit; use Edit automatically after Plan.
- evidence sample: I want you to first understand what we want and are trying to do and then to review each pr and all the code that we have to find if we are properly doing what we claim for (eg, if we say we are using

## P-mine-3 (commit_git, evidence≈15)
- proposed: Agent may commit when asked; no silent auto-PR; review uncommitted changes before ship.
- evidence sample: i want to recheck what we change in the readme in this draft PR. Lets not name YOLO if its not named in the main branch. Also i dont want the focus mode that is speed + distance of player to be referr

## P-mine-4 (memory_l0, evidence≈8)
- proposed: Keep L0 a small generated snapshot of current principles/progress/pending; upsert by id; never mix SUPERSEDED into L0.
- evidence sample: Place fixes where the code was introduced Implement the plan as specified, it is attached for your reference. Do NOT edit the plan file itself. To-do's from the plan have already been created. Do not 

## P-mine-5 (ux_simple, evidence≈5)
- proposed: Daily UX first — tomorrow-morning test; plain files for standing state; invisible complexity under CLIs.
- evidence sample: i see that the images generated seemed to rollback to like simple lines like we had before instead of nicer ones
