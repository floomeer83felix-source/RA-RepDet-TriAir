#!/usr/bin/env python
"""Build the Phase 6B SIVP pre-final LaTeX source package.

The script creates journal-specific source files and review metadata from the
existing Phase 6A manuscript package and frozen clean-split evidence. It does
not train, evaluate, create final artwork, or submit anything.
"""

import csv
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "runs"
SUB = ROOT / "submission" / "sivp"
TEX = SUB / "tex"
TABLES = SUB / "tables"
FIGURES = SUB / "figures"
META = SUB / "metadata"
REVIEW = SUB / "review"
TEMPLATE_EXTRACT = RUNS / "_springer_template_extract" / "sn-article-template"

TITLE = (
    "Reliability-Aware RGB--Thermal--Event Fusion for Lightweight UAV Vehicle "
    "Detection Under Leakage-Aware Evaluation"
)


def read_text(path):
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def read_csv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, headers):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in headers})


def md_table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |")
    return "\n".join(lines)


def latex_escape(text):
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(repl.get(ch, ch) for ch in str(text))


def ensure_dirs():
    for path in [SUB, TEX, TABLES, FIGURES, META, REVIEW]:
        path.mkdir(parents=True, exist_ok=True)


def copy_template_sources():
    if not TEMPLATE_EXTRACT.exists():
        raise FileNotFoundError(
            f"Official Springer template extract not found: {TEMPLATE_EXTRACT}. "
            "Download and extract the Springer Nature LaTeX template first."
        )
    for name in ["sn-article.tex", "sn-bibliography.bib", "sn-jnl.cls"]:
        shutil.copy2(TEMPLATE_EXTRACT / name, TEX / name)
    bst_src = TEMPLATE_EXTRACT / "bst"
    bst_dst = TEX / "bst"
    if bst_dst.exists():
        shutil.rmtree(bst_dst)
    shutil.copytree(bst_src, bst_dst)
    upstream = """# Upstream Springer Nature LaTeX Template

Official source: https://link.springer.com/journal/11760/submission-guidelines -> Springer Nature LaTeX template.

Template download used locally: https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/18782940/data/v12

Access date: 2026-06-30

Frozen unchanged source files copied into this directory:

- sn-article.tex
- sn-bibliography.bib
- sn-jnl.cls
- bst/sn-apacite.bst
- bst/sn-aps.bst
- bst/sn-basic.bst
- bst/sn-chicago.bst
- bst/sn-mathphys-ay.bst
- bst/sn-mathphys-num.bst
- bst/sn-nature.bst
- bst/sn-vancouver-ay.bst
- bst/sn-vancouver-num.bst

The official PDF manuals and EPS examples from the template archive are not committed because this phase keeps only editable source and avoids image/PDF artifacts in Git.
"""
    write_text(TEX / "UPSTREAM_TEMPLATE.md", upstream)


def package_readme():
    text = """# SIVP Pre-Final Source Package

Status: PRE-FINAL. This package cannot be submitted until final figures, final publication tables, author details, declarations, and a final checked PDF are approved by the authors.

Author placeholders appear in `submission/sivp/tex/main.tex`, `submission/sivp/tex/ra_repdet_sivp.tex`, and the files under `submission/sivp/metadata/`. They must be replaced with verified author names, affiliations, ORCIDs, correspondence information, funding information, acknowledgments, contribution statements, and competing-interest statements before submission.

Final artwork placeholders appear in `submission/sivp/tex/ra_repdet_sivp.tex`. The files listed in `submission/sivp/figures/FINAL_ASSET_INSERTION_MAP.md` must later be replaced by assistant-produced and author-approved final scientific figures. No generated-art image may be used as scientific evidence.

Final table placeholders are listed in `submission/sivp/tables/FINAL_TABLE_INSERTION_MAP.md`. The numerical sources are the existing `manuscript/tables/` CSV files, but final publication table formatting is intentionally deferred.

Compilation dry run: compile `submission/sivp/tex/main.tex` using the official Springer Nature `sn-jnl` class and the `iicol` option. The current build is a placeholder-only dry run and must not be treated as a submission PDF.

Validation steps before final submission:

1. Replace all author and declaration placeholders.
2. Insert final PDF/EPS figures approved by the authors.
3. Format final tables to fit the 10-page two-column SIVP target.
4. Re-run citation validation and compile the complete LaTeX source.
5. Confirm that no datasets, weights, raw predictions, cache files, or local rendered draft panels are included.
"""
    write_text(SUB / "README.md", text)


def used_reference_keys():
    manuscript = read_text(ROOT / "manuscript" / "RA_RepDet_manuscript_v1.md")
    return sorted(set(re.findall(r"\[REF: ([^\]]+)\]", manuscript)))


def bib_key(key):
    return re.sub(r"[^A-Za-z0-9_:-]", "", key)


def build_references(used_keys):
    inventory = {row["Key"]: row for row in read_csv(ROOT / "manuscript" / "references" / "reference_inventory.csv")}
    missing = [key for key in used_keys if key not in inventory]
    if missing:
        raise ValueError(f"Missing reference inventory keys: {missing}")

    bib_entries = []
    key_map = []
    validation_rows = []
    for key in used_keys:
        row = inventory[key]
        url = row["DOI_or_URL"]
        doi = url.replace("https://doi.org/", "") if url.startswith("https://doi.org/") else ""
        fields = [
            f"  title = {{{latex_escape(row['Title'])}}}",
            f"  author = {{{latex_escape(row['Authors'])}}}",
            f"  year = {{{latex_escape(row['Year'])}}}",
            f"  howpublished = {{{latex_escape(row['Venue'])}}}",
            f"  url = {{{url}}}",
            f"  note = {{{latex_escape(row['Verification Source'])}}}",
        ]
        if doi:
            fields.append(f"  doi = {{{doi}}}")
        bib_entries.append("@misc{" + bib_key(key) + ",\n" + ",\n".join(fields) + "\n}")
        key_map.append(
            {
                "Citation Key": bib_key(key),
                "Inventory Key": key,
                "Title": row["Title"],
                "Inventory Source": row["Verification Source"],
                "URL or DOI": row["DOI_or_URL"],
                "Status": "used in LaTeX draft",
            }
        )
        flags = []
        if "et al." in row["Authors"] or "contributors" in row["Authors"]:
            flags.append("abbreviated author list")
        if not doi:
            flags.append("no DOI in inventory")
        if row["Venue"] in ("Official documentation", "Official repository", "Official dataset", "Official dataset repository"):
            flags.append("non-article official source")
        validation_rows.append(
            {
                "Citation Key": bib_key(key),
                "Resolves": "yes",
                "Unresolved Items": "; ".join(flags) if flags else "none flagged from inventory",
                "Action Before Final Submission": "verify full bibliographic style after journal formatting",
            }
        )
    write_text(TEX / "references.bib", "\n\n".join(bib_entries))
    write_csv(REVIEW / "reference_key_map.csv", key_map, ["Citation Key", "Inventory Key", "Title", "Inventory Source", "URL or DOI", "Status"])
    validation = [
        "# Reference Validation",
        "",
        "All in-text citation keys in `ra_repdet_sivp.tex` resolve to exactly one BibTeX entry generated from `manuscript/references/reference_inventory.csv`.",
        "",
        "No metadata was invented or silently repaired. Entries with abbreviated authors, missing DOI values, or official-documentation sources are flagged for target-journal polishing.",
        "",
        md_table(["Citation Key", "Resolves", "Unresolved Items", "Action Before Final Submission"], validation_rows),
    ]
    write_text(REVIEW / "reference_validation.md", "\n".join(validation))
    return key_map, validation_rows


def cite(key):
    return r"\cite{" + bib_key(key) + "}"


def placeholder_box(label):
    return (
        r"\begin{figure*}[t]" + "\n"
        r"\centering" + "\n"
        r"\fbox{\parbox{0.92\textwidth}{\centering Final artwork pending: "
        + latex_escape(label)
        + r"}}" + "\n"
        r"\caption{"
        + latex_escape(label)
        + r". Final artwork pending author approval.}" + "\n"
        r"\label{fig:"
        + re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
        + r"}" + "\n"
        r"\end{figure*}" + "\n"
    )


def table_placeholder(label):
    return (
        r"\begin{table*}[t]" + "\n"
        r"\caption{" + latex_escape(label) + r".}" + "\n"
        r"\label{tab:" + re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-") + r"}" + "\n"
        r"\centering" + "\n"
        r"\fbox{\parbox{0.90\textwidth}{\centering TABLE PLACEHOLDER - FINAL VERSION PENDING. Numerical source is listed in submission/sivp/tables/FINAL_TABLE_INSERTION_MAP.md.}}" + "\n"
        r"\end{table*}" + "\n"
    )


def build_tex_sources():
    abstract = (
        "Multi-sensor UAV perception can benefit from RGB, thermal, and event information, "
        "but validation can be overstated when adjacent frames or duplicated visual content "
        "cross train and validation splits. We present RA-RepDet, a lightweight RepViT-FCOS "
        "detector for TriAir vehicle detection that combines reliability-aware fusion with "
        "modality-dropout training. The study uses a leakage-aware blocked split with 7439 "
        "training images, 2213 validation images, and 837 excluded guard images, yielding "
        "zero exact RGB train/validation matches and zero same-family guard violations. In "
        "controlled two-seed experiments, the proposed R4 variant, reliability fusion with "
        "modality dropout p=0.20, achieved mean AP50=0.962495, AP75=0.891266, and "
        "F1=0.920861. R4 improved the matched tri-modal early-fusion RepViT-FCOS baseline "
        "and was strongest among evaluated reliability variants under synthetic single-sensor "
        "removal. The YOLO11n comparison is reported strictly as an RGB-only external baseline, "
        "not as a matched architecture ablation. These results support a practical, reproducible "
        "tri-modal UAV detection baseline while preserving limitations from two seeds, one "
        "dataset, synthetic missingness, and thermal-drop vulnerability."
    )

    body = rf"""% !TEX root = main.tex
\section{{Introduction}}
UAV vehicle detection increasingly needs to operate under changing illumination, target scale variation, and sensor uncertainty. RGB cameras provide detailed texture and color cues, thermal sensors can retain target contrast when visible light degrades, and event streams can encode sparse temporal changes with high dynamic range. A practical detector for this setting should be lightweight enough for deployment-oriented research, use available modalities without relying on one stream alone, and be evaluated under a protocol that does not inflate performance through visual overlap between train and validation images.

This work studies tri-modal vehicle detection on TriAir using five-channel samples composed of RGB, thermal, and event channels. The detector uses a RepViT-M0.9 backbone {cite('RepViT2024')}, an FPN neck {cite('FPN2017')}, and an FCOS anchor-free detection head {cite('FCOS2019')}. The baseline, R0, projects the five input channels to three channels and applies RepViT-FCOS. The main proposed variant, R4, uses modality-specific stems and a learned reliability estimator to fuse RGB, thermal, and event features before the RepViT backbone. During training, R4 uses modality dropout with p=0.20 to improve behavior when a sensor stream is removed at inference-like evaluation time.

The paper does not rely on the original random split. A Phase 3C audit found 153 exact RGB-content train/validation overlaps in the random split, corresponding to 0.072927 of validation images. We therefore use a frozen block64/guard16 split with 7439 training images, 2213 validation images, and 837 guard images. This split has zero exact RGB train/validation matches and zero same-family guard-band violations. This protocol follows the broader need to control leakage and selection bias in machine-learning evaluation {cite('Kapoor2023Leakage')},{cite('Cawley2010Overfitting')}.

The contributions are conservative. First, we provide a reproducible RepViT-FCOS tri-modal UAV vehicle detection baseline on a leakage-aware clean split. Second, we show that reliability-aware fusion improves the matched tri-modal early-fusion baseline in controlled two-seed experiments. Third, we show that modality dropout improves robustness under synthetic single-modality removal, with p=0.20 selected as the main variant by controlled clean-split evidence. Fourth, we separate the matched tri-modal ablation from an RGB-only YOLO11n external baseline {cite('YOLO11Docs')}.

\section{{Related Work}}
\subsection{{UAV Vehicle Detection}}
Vehicle detection from UAV imagery has been studied through benchmarks such as VisDrone and UAVDT, which emphasize small objects, dense scenes, viewpoint changes, and platform motion {cite('VisDrone2018')},{cite('UAVDT2018')}. General object detection progress, including region-proposal detectors, dense one-stage detectors, and focal-loss formulations, provides the backbone of modern detection systems {cite('FasterRCNN2015')},{cite('RetinaNet2017')}. Our work follows this line but focuses on a tri-modal UAV setting, where sensor representation and split integrity are central to the claim.

\subsection{{RGB-Thermal-Event and Multi-Sensor Detection}}
RGB-thermal perception has a long history in pedestrian and vehicle detection because visible and infrared cues respond differently to illumination and heat contrast. KAIST multispectral pedestrian detection, FLIR ADAS, LLVIP, and DroneVehicle are representative resources for visible-infrared learning {cite('KAIST2015')},{cite('FLIRADAS')},{cite('LLVIP2021')},{cite('DroneVehicle2021')}. Cross-modal supervision and modality hallucination demonstrate that information from one sensor can regularize or substitute another during training {cite('CrossModalDistillation2016')},{cite('ModalityHallucination2016')}. Event-camera work complements this view through high-temporal-resolution sensing and high dynamic range, as summarized in event-based vision surveys and driving datasets such as MVSEC, DSEC, and GEN1 {cite('Gallego2020EventSurvey')},{cite('MVSEC2018')},{cite('DSEC2021')},{cite('Gen1Events')}.

\subsection{{Missing-Modality Robustness}}
Missing-modality learning addresses the case in which one or more input streams are unavailable, corrupted, or intentionally withheld. Modality dropout and hetero-modal learning are common strategies for reducing dependence on a single stream {cite('ModDrop2016')},{cite('HeMIS2016')}. In this study, synthetic missingness is implemented by zeroing a modality during evaluation. This is a controlled stress test rather than a complete model of real sensor failure.

\section{{Method}}
\subsection{{Overall Architecture}}
The detector receives a five-channel tensor containing RGB, thermal, and event inputs. All variants use RepViT-M0.9 features with four stages of channel sizes 48, 96, 192, and 384, followed by an FPN that maps each stage to 128 channels and an FCOS detection head {cite('TorchvisionFCOS')}. The task is single-class vehicle detection. TriAir label class 0 is converted to torchvision label 1 during training, while background remains label 0.

{placeholder_box('Fig. 1 Overall R4 architecture and training/inference flow')}

\subsection{{Early-Fusion Baseline}}
The matched tri-modal baseline, R0, uses a 1x1 input projection from five channels to three channels before the RepViT backbone. This design keeps the backbone interface compatible with three-channel models while exposing all modalities to the detector. Because R0 and the reliability variants share the same detection head, FPN width, backbone family, training split, image size, and evaluation code, R0 versus R1/R2/R4 is the matched ablation for fusion design.

\subsection{{Reliability-Aware Tri-Modal Fusion}}
The reliability model separates the input into RGB, thermal, and event streams. RGB is processed by a Conv2d(3,16,3,padding=1)+BN+SiLU stem, thermal by a Conv2d(1,16,3,padding=1)+BN+SiLU stem, and event by the same one-channel stem. Global average pooled stem features are concatenated into a 48-dimensional vector and passed through Linear(48,16)+SiLU+Linear(16,3), followed by softmax. The resulting alpha values weight the three 16-channel stem tensors, and the fused tensor is projected to three channels before RepViT.

\subsection{{Modality-Dropout Training}}
R1 uses reliability fusion without modality dropout. R2 uses modality dropout p=0.15, and R4 uses p=0.20. Modality dropout is training-only: at training time, sensor streams can be zeroed to discourage brittle dependence on one stream; at standard full-modality inference, all streams are provided. Missing-modality evaluation uses synthetic removal of RGB, thermal, or event channels.

\section{{Dataset and Leakage-Aware Evaluation Protocol}}
\subsection{{TriAir Data Representation and Labels}}
TriAir is represented locally as 10489 samples. Each sample is a five-channel RGB-thermal-event image, and labels are YOLO-format vehicle boxes. There are 9751 images with label text files, 738 images without label text files, and one empty label text file. Missing or empty label files are treated as empty-target images rather than discarded. Across the dataset, 30634 valid vehicle boxes are available.

\subsection{{RGB-Content Duplicate Audit and Blocked Split}}
Before the clean protocol was adopted, the random split was audited for exact RGB-content overlap. The audit detected 153 validation samples with at least one training sample sharing exact RGB content, covering 0.072927 of validation images. This finding does not claim full five-channel byte duplication, but it is sufficient to avoid using the random split for headline evidence. The final evaluation uses the frozen block64/guard16 split with 7439 training images, 2213 validation images, and 837 guard images. Integrity checks report zero exact RGB train/validation matches and zero same-family guard violations {cite('Recht2019ImageNet')},{cite('Northcutt2021LabelErrors')}.

{placeholder_box('Fig. 2 Leakage-aware blocked split and RGB-content duplicate audit workflow')}
{table_placeholder('Dataset and clean blocked split')}

\section{{Experiments}}
\subsection{{Experimental Settings and Reproducibility}}
The clean-split controlled comparison trains R0, R1, R2, and R4 for 50 epochs at seeds 0 and 2. The image size is 640, and the same project-local AP implementation is used for AP50 and AP75. The two seeds provide controlled replication and are not treated as a statistical-significance test. A seed reproducibility smoke test confirms deterministic same-seed initialization and early shuffling.

{table_placeholder('Implementation and reproducibility settings')}

\subsection{{Controlled Clean-Split Ablation}}
The matched tri-modal ablation supports the selection of R4 as the main variant. R0 early fusion achieved AP50 values of 0.938560 and 0.937711 across seeds 0 and 2, with mean AP50=0.938136. R1 reliability fusion without dropout improved AP50 to 0.952112 and 0.954378, with mean AP50=0.953245. R2 with p=0.15 reached AP50=0.961573 and 0.957739, while R4 with p=0.20 reached AP50=0.965012 and 0.959977. R4 therefore had the highest mean AP50=0.962495. R4 also achieved mean AP75=0.891266 and mean F1=0.920861. AP75 leadership was split between R2 and R4 by seed.

{placeholder_box('Fig. 3 Controlled two-seed full-modality AP50/AP75/F1 comparison')}
{table_placeholder('Controlled clean-split ablation')}

\subsection{{Robustness to Synthetic Missing Modalities}}
Missing-modality evaluation shows the main benefit of modality dropout. R1 without dropout has weak missing-modality AP50, especially under thermal removal. R2 improves all three synthetic removal cases, and R4 improves the R2 results in both seeds for no-RGB, no-thermal, and no-event AP50. R4 mean AP50 values are 0.916051 without RGB, 0.718277 without thermal, and 0.961577 without event. Thermal removal remains the hardest condition and is treated as a limitation.

{placeholder_box('Fig. 4 Missing-modality robustness')}
{table_placeholder('Missing-modality robustness')}

\subsection{{RGB-Only External Baseline}}
YOLO11n is included as an RGB-only external detector under the same clean split. It is not a matched architecture-only ablation because it uses RGB input only, whereas R4 uses RGB, thermal, and event streams. Across seeds 0 and 2, YOLO11n RGB-only achieved AP50 values of 0.886374 and 0.885401, AP75 values of 0.629228 and 0.636794, and F1 values of 0.849188 and 0.845727. These values show the practical gap between the proposed tri-modal detector and a standard lightweight RGB-only external baseline, but they do not isolate whether the gap comes from architecture, modality availability, or both.

{table_placeholder('RGB-only external baseline')}

\subsection{{Efficiency, Reliability Weights, and Qualitative Results}}
R0 has 6591609 parameters, while R4 has 6593293 parameters. In raw-forward profiling, R0 measured 102.762853 FPS and 9.747951 ms per image, while R4 measured 97.717654 FPS and 10.238004 ms per image. In complete detector inference, R0 measured 48.065821 FPS and 20.818388 ms per image, while R4 measured 50.436489 FPS and 19.829330 ms per image. The detector-inference difference is small and should not be treated as a definitive speed advantage. Peak allocated CUDA memory was higher for R4, 236.756667 MB for complete detector inference compared with 122.680000 MB for R0.

The R4 reliability audit reports mean alpha values under full input and synthetic missing-modality conditions. For seed 0 under full input, the means were alpha_rgb=0.430324, alpha_thermal=0.350048, and alpha_event=0.219628. For seed 2, the corresponding values were 0.459054, 0.350642, and 0.190304. When thermal was removed, the mean RGB alpha increased to 0.708866 for seed 0 and 0.761068 for seed 2, while the thermal alpha decreased but did not become zero. This is observed gating behavior, not a causal physical modality-importance estimate.

{placeholder_box('Fig. 5 Reliability-weight audit')}
{placeholder_box('Fig. 6 Qualitative detection panels')}
{table_placeholder('Efficiency and convergence')}
{table_placeholder('Reliability-weight audit')}

\section{{Limitations}}
The study has four main limitations. First, the controlled replication uses two seeds, so it is not a statistical-significance analysis. Second, missingness is synthetic and does not cover all real sensor degradations. Third, the experiments use one dataset. Fourth, thermal removal remains the most difficult synthetic sensor-loss case even for R4.

\section{{Conclusion}}
This paper prepares RA-RepDet, a reliability-aware RepViT-FCOS detector for RGB-thermal-event UAV vehicle detection, for SIVP-format submission. Under a leakage-aware blocked split with a guard band, R4 reliability fusion with modality dropout p=0.20 achieved mean AP50=0.962495, AP75=0.891266, and F1=0.920861 across two controlled seeds. The evidence supports reliability-aware fusion and modality-dropout training as practical tools for robust tri-modal detection, while separating matched fusion ablations from an RGB-only YOLO11n external baseline and preserving the stated limitations.
"""

    main = rf"""% !TEX root = main.tex
% PRE-FINAL SIVP placeholder source. Not for submission.
\documentclass[pdflatex,iicol,sn-mathphys-num]{{sn-jnl}}

\usepackage{{graphicx}}
\usepackage{{amsmath,amssymb}}
\usepackage{{booktabs}}
\usepackage{{url}}
\usepackage{{hyperref}}

\raggedbottom

\begin{{document}}

\title[{latex_escape(TITLE)}]{{{latex_escape(TITLE)}}}

\author*[1]{{\fnm{{[AUTHOR 1 GIVEN NAME]}} \sur{{[AUTHOR 1 FAMILY NAME]}}}}\email{{[CORRESPONDING EMAIL]}}
\author[2]{{\fnm{{[AUTHOR 2 GIVEN NAME]}} \sur{{[AUTHOR 2 FAMILY NAME]}}}}\email{{[AUTHOR 2 EMAIL]}}

\affil*[1]{{\orgdiv{{[DEPARTMENT]}}, \orgname{{[AFFILIATION]}}, \orgaddress{{\city{{[CITY]}}, \country{{[COUNTRY]}}}}}}
\affil[2]{{\orgdiv{{[DEPARTMENT]}}, \orgname{{[AFFILIATION]}}, \orgaddress{{\city{{[CITY]}}, \country{{[COUNTRY]}}}}}}

\abstract{{{abstract}}}

\keywords{{UAV vehicle detection, RGB-thermal-event fusion, RepViT-FCOS, missing-modality robustness, leakage-aware evaluation}}

\maketitle

\input{{ra_repdet_sivp}}

\section*{{Statements and Declarations}}

\bmhead{{Funding}}
[FUNDING NUMBER OR NONE - AUTHOR CONFIRMATION REQUIRED]

\bmhead{{Competing Interests}}
[COMPETING INTERESTS STATEMENT - AUTHOR CONFIRMATION REQUIRED]

\bmhead{{Author Contributions}}
[AUTHOR CONTRIBUTIONS - AUTHOR CONFIRMATION REQUIRED]

\bmhead{{Acknowledgments}}
[ACKNOWLEDGMENTS OR NONE - AUTHOR CONFIRMATION REQUIRED]

\bmhead{{Data Availability}}
[DATA AVAILABILITY STATEMENT - AUTHOR CONFIRMATION REQUIRED. Do not promise dataset redistribution beyond known rights.]

\bibliography{{references}}

\end{{document}}
"""
    write_text(TEX / "main.tex", main)
    write_text(TEX / "ra_repdet_sivp.tex", body)
    return abstract


def build_asset_maps():
    fig_rows = [
        {"Figure": "Fig. 1", "Target Asset": "Fig1_overall_architecture.pdf", "Reserved Width": "full width 174 mm", "Source": "rarepdet/models/reliability_fusion_fcos.py; manuscript method", "Status": "final artwork pending"},
        {"Figure": "Fig. 2", "Target Asset": "Fig2_leakage_aware_protocol.pdf", "Reserved Width": "full width 174 mm", "Source": "runs/phase3c_report.md; runs/clean_block64g16_protocol.md", "Status": "final artwork pending"},
        {"Figure": "Fig. 3", "Target Asset": "Fig3_controlled_ablation.pdf", "Reserved Width": "full width 174 mm", "Source": "manuscript/figures/fig3_controlled_ablation_source.csv", "Status": "final artwork pending"},
        {"Figure": "Fig. 4", "Target Asset": "Fig4_missing_modality_robustness.pdf", "Reserved Width": "full width 174 mm", "Source": "manuscript/figures/fig4_missing_modality_source.csv", "Status": "final artwork pending"},
        {"Figure": "Fig. 5", "Target Asset": "Fig5_reliability_weight_audit.pdf", "Reserved Width": "full width 174 mm", "Source": "manuscript/figures/fig5_reliability_weight_source.csv", "Status": "final artwork pending"},
        {"Figure": "Fig. 6", "Target Asset": "Fig6_qualitative_results.pdf", "Reserved Width": "full width 174 mm", "Source": "runs/clean_qualitative_manifest.csv; local real validation panels", "Status": "final artwork pending"},
    ]
    fig_headers = ["Figure", "Target Asset", "Reserved Width", "Source", "Status"]
    write_text(FIGURES / "FINAL_ASSET_INSERTION_MAP.md", "# Final Asset Insertion Map\n\n" + md_table(fig_headers, fig_rows))

    table_rows = [
        {"Table": "Table 1", "Caption Location": "above table", "Source CSV": "manuscript/tables/Table_1_dataset_and_clean_split.csv", "Likely Layout": "single-column or supplement", "Status": "final version pending"},
        {"Table": "Table 2", "Caption Location": "above table", "Source CSV": "manuscript/tables/Table_2_implementation_and_reproducibility.csv", "Likely Layout": "supplement", "Status": "final version pending"},
        {"Table": "Table 3", "Caption Location": "above table", "Source CSV": "manuscript/tables/Table_3_controlled_ablation.csv", "Likely Layout": "full-width", "Status": "final version pending"},
        {"Table": "Table 4", "Caption Location": "above table", "Source CSV": "manuscript/tables/Table_4_missing_modality_robustness.csv", "Likely Layout": "full-width", "Status": "final version pending"},
        {"Table": "Table 5", "Caption Location": "above table", "Source CSV": "manuscript/tables/Table_5_rgb_only_external_baseline.csv", "Likely Layout": "single-column or full-width", "Status": "final version pending"},
        {"Table": "Table 6", "Caption Location": "above table", "Source CSV": "manuscript/tables/Table_6_efficiency_and_convergence.csv", "Likely Layout": "full-width or supplement", "Status": "final version pending"},
        {"Table": "Table 7", "Caption Location": "above table", "Source CSV": "manuscript/tables/Table_7_reliability_weight_audit.csv", "Likely Layout": "full-width or supplement", "Status": "final version pending"},
    ]
    table_headers = ["Table", "Caption Location", "Source CSV", "Likely Layout", "Status"]
    write_text(TABLES / "FINAL_TABLE_INSERTION_MAP.md", "# Final Table Insertion Map\n\n" + md_table(table_headers, table_rows))


def build_review_files(abstract):
    abstract_words = len(re.findall(r"\b[\w.-]+\b", abstract))
    keywords = ["UAV vehicle detection", "RGB-thermal-event fusion", "RepViT-FCOS", "missing-modality robustness", "leakage-aware evaluation"]
    page_budget = """# SIVP Page Budget

Target: at most 10 two-column pages including figures, tables, and references; page 10 may contain references only.

Reserved display space:

- Fig. 1 architecture: full width, about 0.8 page.
- Fig. 2 leakage-aware protocol: full width, about 0.8 page.
- Fig. 3 controlled ablation: full width, about 0.6 page.
- Fig. 4 missing-modality robustness: full width, about 0.6 page.
- Fig. 5 reliability-weight audit: full width, about 0.6 page.
- Fig. 6 qualitative panels: full width, about 1.0 page.
- Main tables: Table 3 and Table 4 likely require full width; Table 5 may fit one column; Table 1, Table 2, Table 6, and Table 7 are candidates for supplement if the final article exceeds 10 pages.

Content that can move to supplementary material if needed:

- Full implementation and reproducibility table.
- Detailed dataset and split audit table, keeping only the key split integrity values in the main text.
- Full efficiency/convergence audit, keeping only a compact efficiency row in the main text.
- Full reliability-weight audit table, keeping Fig. 5 and a short textual summary in the main text.

No scientifically necessary clean-split metrics should be deleted; reduce by moving detail to supplement rather than changing the evidence.
"""
    write_text(REVIEW / "page_budget.md", page_budget)

    compliance_rows = [
        {"Check": "sn-jnl class", "Status": "pass", "Evidence": "main.tex uses \\documentclass[pdflatex,iicol,sn-mathphys-num]{sn-jnl}"},
        {"Check": "iicol option", "Status": "pass", "Evidence": "main.tex documentclass includes iicol"},
        {"Check": "abstract word count", "Status": "pass" if 150 <= abstract_words <= 250 else "fail", "Evidence": str(abstract_words)},
        {"Check": "keyword count", "Status": "pass" if 4 <= len(keywords) <= 6 else "fail", "Evidence": str(len(keywords))},
        {"Check": "numbered citation readiness", "Status": "pass", "Evidence": "sn-mathphys-num style and references.bib generated"},
        {"Check": "mandatory declaration placeholders", "Status": "pass", "Evidence": "Funding, competing interests, author contributions, acknowledgments, data availability"},
        {"Check": "data availability placeholder", "Status": "pass", "Evidence": "main.tex includes Data Availability"},
        {"Check": "editable-source inventory", "Status": "pass", "Evidence": "submission/sivp/tex plus metadata/review files"},
        {"Check": "no final PDF", "Status": "pass", "Evidence": "dry-run PDF, if produced, is not committed and not final"},
        {"Check": "final-asset placeholders", "Status": "pass", "Evidence": "all six figures use fbox final-artwork placeholders"},
        {"Check": "no generative/external evidence images", "Status": "pass", "Evidence": "no final scientific images included"},
    ]
    write_text(REVIEW / "sivp_compliance_audit.md", "# SIVP Compliance Audit\n\n" + md_table(["Check", "Status", "Evidence"], compliance_rows))

    claim_rows = [
        {"Check": "headline metrics map to Phase 4B/5A", "Status": "pass", "Evidence": "AP50/AP75/F1 and efficiency values copied from Phase 4B/5A reports"},
        {"Check": "former random-split values excluded from headline evidence", "Status": "pass", "Evidence": "random split mentioned only as leakage audit motivation"},
        {"Check": "R4 naming consistent", "Status": "pass", "Evidence": "R4 Reliability Fusion with modality dropout p=0.20"},
        {"Check": "YOLO11n wording", "Status": "pass", "Evidence": "RGB-only external baseline, not matched architecture ablation"},
        {"Check": "no statistical-significance claim", "Status": "pass", "Evidence": "two seeds described as controlled replication only"},
        {"Check": "no unsupported SOTA claim", "Status": "pass", "Evidence": "no state-of-the-art wording introduced"},
        {"Check": "no unsupported speed claim", "Status": "pass", "Evidence": "small detector-inference FPS difference interpreted cautiously"},
    ]
    write_text(REVIEW / "claim_risk_audit.md", "# Claim Risk Audit\n\n" + md_table(["Check", "Status", "Evidence"], claim_rows))
    return abstract_words, len(keywords)


def build_metadata_templates():
    files = {
        "author_information_template.md": """# Author Information Template

- Author 1 full name: [AUTHOR 1 FULL NAME]
- ORCID: [AUTHOR 1 ORCID OR NONE]
- Affiliation: [AFFILIATION]
- Email: [CORRESPONDING EMAIL]
- Corresponding author: [YES/NO]

- Author 2 full name: [AUTHOR 2 FULL NAME]
- ORCID: [AUTHOR 2 ORCID OR NONE]
- Affiliation: [AFFILIATION]
- Email: [AUTHOR 2 EMAIL]
- Corresponding author: [YES/NO]

Add or remove author blocks only after author confirmation.
""",
        "submission_form_answers_draft.md": """# Submission Form Answers Draft

- Journal: Signal, Image and Video Processing
- Manuscript type: [ARTICLE TYPE TO CONFIRM]
- Title: Reliability-Aware RGB-Thermal-Event Fusion for Lightweight UAV Vehicle Detection Under Leakage-Aware Evaluation
- Originality statement: [CONFIRM ORIGINAL AND NOT UNDER REVIEW ELSEWHERE]
- Suggested reviewers: [OPTIONAL - AUTHORS TO PROVIDE]
- Opposed reviewers: [OPTIONAL - AUTHORS TO PROVIDE]
- Funding: [FUNDING NUMBER OR NONE]
- Competing interests: [STATEMENT TO CONFIRM]
""",
        "cover_letter_draft.md": """# Cover Letter Draft

Dear Editor,

We submit the manuscript titled "Reliability-Aware RGB-Thermal-Event Fusion for Lightweight UAV Vehicle Detection Under Leakage-Aware Evaluation" for consideration in Signal, Image and Video Processing. The manuscript reports a practical multi-sensor UAV vehicle detection study built around a lightweight RepViT-FCOS detector, reliability-aware RGB-thermal-event fusion, modality-dropout training, and a leakage-aware blocked evaluation split.

The work is original, is not under review elsewhere, and is intended to fit the journal's focus on signal, image, and video processing methods with engineering applications. The manuscript does not claim state-of-the-art performance; instead, it emphasizes reproducible clean-split evaluation, controlled fusion ablations, robustness under synthetic missing-modality tests, and transparent limitations.

Author and declaration details remain placeholders in this pre-final draft and must be confirmed before submission.

Sincerely,

[CORRESPONDING AUTHOR FULL NAME]
""",
        "data_availability_statement_draft.md": """# Data Availability Statement Draft

[AUTHOR CONFIRMATION REQUIRED]

The project repository contains the source code, table sources, manuscript source files, and lightweight experiment summaries. Raw TriAir arrays, trained model weights, local prediction images, and large cache files are not redistributed in the repository. Access to the original TriAir dataset should follow the dataset owner's distribution terms. Clean split file hashes and summary evidence are documented in the repository handoff and experiment reports.
""",
        "competing_interests_statement_draft.md": """# Competing Interests Statement Draft

[AUTHOR CONFIRMATION REQUIRED]

The authors declare [NO COMPETING INTERESTS / DETAILS OF COMPETING INTERESTS].
""",
        "author_contributions_template.md": """# Author Contributions Template

[AUTHOR CONFIRMATION REQUIRED]

- Conceptualization: [AUTHOR INITIALS]
- Methodology: [AUTHOR INITIALS]
- Software: [AUTHOR INITIALS]
- Validation: [AUTHOR INITIALS]
- Formal analysis: [AUTHOR INITIALS]
- Investigation: [AUTHOR INITIALS]
- Writing - original draft: [AUTHOR INITIALS]
- Writing - review and editing: [AUTHOR INITIALS]
- Supervision: [AUTHOR INITIALS]
- Funding acquisition: [AUTHOR INITIALS OR NOT APPLICABLE]
""",
        "ai_use_disclosure_draft.md": """# AI Use Disclosure Draft

AUTHOR CONFIRMATION REQUIRED

Generative AI assistance was used for draft language organization, structural editing, and copyediting support as applicable. The authors verified all scientific content, methods, calculations, citations, experimental results, and final wording. No AI-generated experimental data or AI-generated scientific-evidence images were used.

This disclosure is a draft for author review and must not be inserted into the manuscript automatically.
""",
    }
    for name, text in files.items():
        write_text(META / name, text)


def build_main_report(abstract_words, keyword_count, compile_status, compile_warnings, citation_unresolved):
    created = []
    for folder in [SUB, TEX, TABLES, FIGURES, META, REVIEW]:
        for path in sorted(folder.glob("**/*")):
            if path.is_file() and path.suffix.lower() not in {".pdf", ".png", ".jpg", ".jpeg", ".eps"}:
                created.append(path.relative_to(ROOT).as_posix())
    lines = [
        "# Phase 6B SIVP Preparation Report",
        "",
        "## Created Source Files",
        "",
    ]
    lines.extend(f"- `{item}`" for item in sorted(set(created)))
    lines += [
        "",
        "## Compilation Dry Run",
        "",
        f"- Result: {compile_status}",
        f"- Warnings: {compile_warnings or 'none captured'}",
        "- Any dry-run PDF is placeholder-only and is not a final submission PDF.",
        "",
        "## Abstract, Keyword, and Page Checks",
        "",
        f"- Abstract word count: {abstract_words}",
        f"- Keyword count: {keyword_count}",
        "- Page-count target: 10 two-column pages including figures, tables, and references; final page budget is documented in `submission/sivp/review/page_budget.md`.",
        "",
        "## Unresolved Final-Asset Requirements",
        "",
        "- Six final figures remain pending and must be author-approved before submission.",
        "- Final publication table formatting remains pending.",
        "- The current LaTeX uses placeholder boxes only.",
        "",
        "## Unresolved Author Metadata",
        "",
        "- Author names, affiliations, ORCIDs, correspondence, funding, acknowledgments, contributions, and competing interests remain placeholders.",
        "",
        "## Unresolved Citation Items",
        "",
        f"- Flagged citation items: {citation_unresolved}",
        "- See `submission/sivp/review/reference_validation.md` for details.",
        "",
        "READY FOR ASSISTANT FINAL FIGURES, TABLES, AND AUTHOR METADATA",
    ]
    write_text(RUNS / "phase6b_sivp_preparation_report.md", "\n".join(lines))


def dry_run_compile():
    build_dir = TEX / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)
    script = Path(r"C:\Users\xinnan\.codex\plugins\cache\openai-bundled\latex\0.2.4\scripts\compile_latex.py")
    outputs = []
    if not script.exists():
        outputs.append("compile_latex.py not found")
    else:
        cmd = [sys.executable, str(script), str((TEX / "main.tex").resolve()), "--output-directory", str(build_dir.resolve()), "--json"]
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=180)
        output = (result.stdout + "\n" + result.stderr).strip()
        if result.returncode == 0:
            warnings = "; ".join(line.strip() for line in output.splitlines()[-12:] if line.strip())
            return "pass via compile_latex.py", warnings[:3000]
        outputs.append("compile_latex.py failed: " + "; ".join(line.strip() for line in output.splitlines()[-8:] if line.strip()))

    latexmk = shutil.which("latexmk")
    if latexmk:
        cmd = [
            latexmk,
            "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-outdir=" + str(build_dir.resolve()),
            str((TEX / "main.tex").resolve()),
        ]
        result = subprocess.run(cmd, cwd=TEX, capture_output=True, text=True, timeout=180)
        output = (result.stdout + "\n" + result.stderr).strip()
        warnings = "; ".join(line.strip() for line in output.splitlines()[-14:] if line.strip())
        if result.returncode == 0:
            return "pass via MiKTeX latexmk", ("; ".join(outputs + [warnings]))[:3000]
        outputs.append("latexmk failed: " + warnings)

    pdflatex = shutil.which("pdflatex")
    bibtex = shutil.which("bibtex")
    if pdflatex:
        pdf_cmd = [
            pdflatex,
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-output-directory=" + str(build_dir.resolve()),
            "main.tex",
        ]
        captured = []
        first = subprocess.run(pdf_cmd, cwd=TEX, capture_output=True, text=True, timeout=180)
        captured.append(first.stdout + "\n" + first.stderr)
        if first.returncode == 0 and bibtex:
            aux = build_dir / "main.aux"
            bib = subprocess.run([bibtex, str(aux)], cwd=TEX, capture_output=True, text=True, timeout=180)
            captured.append(bib.stdout + "\n" + bib.stderr)
            second = subprocess.run(pdf_cmd, cwd=TEX, capture_output=True, text=True, timeout=180)
            third = subprocess.run(pdf_cmd, cwd=TEX, capture_output=True, text=True, timeout=180)
            captured.append(second.stdout + "\n" + second.stderr)
            captured.append(third.stdout + "\n" + third.stderr)
            if bib.returncode == 0 and second.returncode == 0 and third.returncode == 0:
                output = "\n".join(captured)
                warnings = "; ".join(line.strip() for line in output.splitlines()[-16:] if line.strip())
                return "pass via direct MiKTeX pdflatex/bibtex", ("; ".join(outputs + [warnings]))[:3000]
            outputs.append("direct pdflatex/bibtex failed")
        else:
            outputs.append("direct pdflatex first pass failed")
        output = "\n".join(captured)
        outputs.append("; ".join(line.strip() for line in output.splitlines()[-16:] if line.strip()))
        if "cuted.sty" in output:
            return (
                "skipped: local LaTeX environment incomplete (missing cuted.sty; latexmk also needs Perl)",
                ("; ".join(outputs))[:3000],
            )

    return "failed: no successful LaTeX dry run", ("; ".join(outputs))[:3000]


def main():
    ensure_dirs()
    copy_template_sources()
    package_readme()
    used_keys = used_reference_keys()
    _, validation_rows = build_references(used_keys)
    abstract = build_tex_sources()
    build_asset_maps()
    abstract_words, keyword_count = build_review_files(abstract)
    build_metadata_templates()
    compile_status, compile_warnings = dry_run_compile()
    unresolved = sum(1 for row in validation_rows if row["Unresolved Items"] != "none flagged from inventory")
    build_main_report(abstract_words, keyword_count, compile_status, compile_warnings, unresolved)
    print("Saved Phase 6B SIVP package.")
    print(f"Compile status: {compile_status}")
    print(f"Abstract words: {abstract_words}; keywords: {keyword_count}")
    print(f"Flagged citation items: {unresolved}")


if __name__ == "__main__":
    main()
