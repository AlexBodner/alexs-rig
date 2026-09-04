---
name: alex-experiments
description: Hygiene for machine-learning training runs and comparisons — what to save while a run is in flight, how to keep runs from overwriting each other, and what makes two arms actually comparable. Use when launching training, setting up an evaluation, or comparing model variants.
---

# Alex experiments (run hygiene)

For training runs and model comparisons. `research-conduct` carries the KV-cache thesis's
own guardrails and `experiment-report` interprets a finished run; this is the general
hygiene that applies to any run. The cross-cutting obligations stay in L0 — `P-run` for the
paid-compute lifecycle, `P-fair` for equal effort per arm.

## Save the best model, not only the periodic ones

Checkpoint on a schedule **and** keep the best-by-validation checkpoint separately. A run
that only writes every N steps loses its best model the moment validation dips afterwards,
and no amount of later analysis recovers it.

> "no se si deberíamos agarrar checkpoint 1000 o el mejor de la loss de validación,
> **¿estamos guardando el mejor modelo?**"

> "en realidad deberíamos haber guardado los mejores modelos, porque veo que cerca de
> 800/820 teníamos un mejor modelo"

> "¿estamos guardando los mejores checkpoints?" — answer at the time: **"No, no guardamos
> el mejor."**

Asked three times across two runs, answered no each time. Decide the checkpoint policy
**before** launching, and state it in the run's config: it is the one loss that cannot be
repaired after the fact.

## One run, one log — never a shared path

Every run writes to a path keyed by its own identity (arm, seed, timestamp). Two runs
sharing a log or an output directory silently overwrite each other, and the damage is only
visible once you go looking for a number that is no longer there.

> "las corridas se tienen que loguear bien, **cuidado con las cosas que se pisan**,
> idealmente distingámoslas"

Check for collisions before launching, not after: if the path does not contain something
unique to this run, it is a collision waiting to happen.

## Compare like with like

A comparison across arms is only meaningful when the nuisance variables match. Seed first:
compare same-seed against same-seed, and if the claim needs to be stronger, repeat across
several seeds rather than mixing them.

> "o sea lo justo sería comparar los de semilla 42 entre sí, ¿o no? Tal vez para mayor
> prueba podríamos comparar en distintas semillas a igual semilla"

State which nuisance variables were held fixed and which were not; an unmatched one is a
confound a reviewer will find (`P-fair`).

## Every queued evaluation must earn its slot

Before a batch of evaluations runs, say what question each one answers. An evaluation that
cannot name its question is compute spent on a table nobody will read.

> "¿las evaluaciones que tenés pensado correr son todas las aprobadas? **¿valen todas la
> pena?**"

## Before closing the laptop

When a run continues unattended, confirm and report: the process survives disconnection,
the checkpoint policy is what you intend, the logs are separated, and the evaluations
queued after training are the approved set. `P-run` then covers pulling the results off the
machine before anything is stopped.
