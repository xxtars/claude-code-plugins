# SLURM Shell Script Conventions

Rules for writing shell scripts that run on SLURM clusters.

## Shell options
- **Never use `set -euo pipefail`** or any `set -e`/`set -u`/`set -o pipefail` in SLURM scripts. Reason: SLURM job steps, health checks, and cleanup traps interact badly with `set -e` — a non-zero exit from an expected failure (e.g., `curl` during health check, `kill` on an already-dead process) will terminate the entire job.

## Containers (Apptainer/Singularity)
- Use Apptainer/Singularity containers, not conda/virtualenv on shared clusters
- sbatch scripts launch the container; run scripts execute inside it:
  ```bash
  srun apptainer exec --nv --bind="/scratch/" --home /users/$USER $SIF bash run_script.sh
  ```
- **Build SIF images on compute nodes**, not login nodes (login nodes are resource-constrained):
  ```bash
  sbatch build_sif.sh docker://<image>:<tag> <name>.sif
  ```
- Use `/dev/shm` (RAM-backed) as `TMPDIR` for builds — default `/tmp` often runs out of space

## Git on cluster
- Sync flow: `local commit → git push → ssh to cluster → git pull → sbatch`
- Respect `.gitignore` — never use `git add -f` to force-add ignored files
- When unsure if a file should be committed, ask first

## SLURM script structure (recommended)
Three-layer separation for maintainability:
1. **`submit_*.sh`** — Loop/batch submission logic (optional)
2. **`sbatch_*.sh`** — SLURM resource directives (`#SBATCH`) + `apptainer exec`
3. **`run/*.sh`** — Actual execution logic inside the container

This keeps resource config separate from business logic, making both easier to modify.
