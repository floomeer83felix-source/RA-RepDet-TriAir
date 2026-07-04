# Environment Record Template

This template separates repository-documented experimental settings from machine-specific facts that still require author or research-owner confirmation.

## Machine-Specific Facts To Confirm

| field | confirmed value | confirmer/date | notes |
| --- | --- | --- | --- |
| GPU model |  |  |  |
| GPU count |  |  |  |
| GPU memory |  |  |  |
| CPU model |  |  |  |
| RAM |  |  |  |
| Operating system |  |  |  |
| Python version |  |  |  |
| PyTorch version |  |  |  |
| Torchvision version |  |  |  |
| CUDA version |  |  |  |
| cuDNN version |  |  |  |
| Key package versions |  |  | Include only author-confirmed package versions. |
| Person confirming record |  |  |  |
| Confirmation date |  |  |  |

## Repository-Documented Experimental Settings

| field | repository-documented value | evidence | confirmation status |
| --- | --- | --- | --- |
| Training image size | 640 | `manuscript/tables/Table_2_implementation_and_reproducibility.csv`; clean run `config.txt` files | repository documented; final environment confirmation still required |
| Training batch size | 4 | `docs/REPRODUCIBILITY.md`; clean R4 `config.txt` files | repository documented; final environment confirmation still required |
| Controlled seed list | 0, 2 | `runs/seed_reproducibility_smoke.md`; `docs/REPRODUCIBILITY.md` | repository documented; final environment confirmation still required |
| Epoch count | 50 where supported by clean-split evidence | `runs/clean_block64g16_convergence.csv`; clean run `config.txt` files | repository documented; final environment confirmation still required |
| Profiling batch size | 1 | `runs/clean_efficiency_profile.md`; `docs/REPRODUCIBILITY.md` | repository documented; final environment confirmation still required |
| Profiling warmup | 100 iterations | `runs/clean_efficiency_profile.md`; `runs/phase5a_report.md` | repository documented; final environment confirmation still required |
| Profiling timed iterations | 300 | `runs/clean_efficiency_profile.md`; `runs/phase5a_report.md` | repository documented; final environment confirmation still required |
| Profiling repeats | 3 | `runs/clean_efficiency_profile.md`; `runs/phase5a_report.md` | repository documented; final environment confirmation still required |

Do not fill machine-specific values from the current workstation unless the authors explicitly approve those values as the final training/evaluation environment record.
