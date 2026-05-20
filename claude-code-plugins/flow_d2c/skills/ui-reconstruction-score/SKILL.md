---
name: ui-reconstruction-score
description: Compare design screenshots with code implementation screenshots to evaluate UI reconstruction fidelity and identify the top actionable visual/layout problems. Use when Codex is asked to score similarity, judge restoration quality, compare paired UI screenshots or folders of screenshots, produce a reconstruction report, or describe the most obvious differences between an original design/reference image and an implementation/candidate image for mobile or web app UI.
---

# UI Reconstruction Score

## Purpose

Use this skill to compare a design/reference UI screenshot with a code implementation/candidate screenshot. Support two user intents with the same analysis pipeline:

- **Score**: return a stable reconstruction/similarity score.
- **Issues**: return at most two most obvious, actionable UI problems that help locate code changes.

Never score or report the phone status information area at the top, such as time, signal, Wi-Fi, carrier, battery, or system indicators. Use it only to infer screenshot alignment/safe-area handling.

## Workflow

1. Identify whether the input is one pair of images or two directories of paired screenshots. For directories, pair images by filename stem before the extension.
2. Inspect the images directly first. Before looking at numeric scores, decide the page type, major regions, and whether the implementation is globally scaled, globally shifted, or genuinely broken.
3. Run `scripts/ui_score.py` to generate deterministic evidence:

```bash
python3 /path/to/ui-reconstruction-score/scripts/ui_score.py reference.png candidate.png --out report
python3 /path/to/ui-reconstruction-score/scripts/ui_score.py pic0 pic --out report --profile mobile-app
```

4. Open the generated `report/index.html`, contact sheets, normalized images, and heatmaps when available. Use script results only as supporting evidence. Do not let low SSIM, heatmap intensity, or script hints override model-visible UI similarity.
5. Divide the UI into semantic regions before judging. This is mandatory; do not evaluate only as a whole image:
   - ignored status/system area
   - app header/navigation
   - fixed tabs/search/actions
   - primary content flow
   - list/grid/card/media regions
   - overlays, scrims, dialogs, sheets
   - bottom navigation or bottom-anchored panels
6. For each semantic region, compare after allowing a small uniform scale tolerance. If the candidate is consistently 3-8% larger or smaller but preserves anchors, hierarchy, spacing relationships, and readability, treat it as high similarity and do not report it as a problem. Report scale only when it breaks layout, clips text, changes visible item count materially, or violates an anchor.
7. Determine the page state and comparability. A different modal state, route, scroll position, or data state can lower comparability, but do not mistake a layout constraint failure for low comparability. For example, a bottom panel that appears too high is an anchor problem, not merely a scroll-state difference.
8. Select output mode based on the user's request:
   - If the user asks for score/similarity/restoration quality, return score mode.
   - If the user asks what is different, where to fix, or problems, return issues mode.
   - If the user asks for a full evaluation, return score plus at most two issues.

## Output Modes

### Score Mode

Return a compact score with component scores. Use a 0-100 scale where 100 means screenshot-level reconstruction after ignoring top status information.

```json
{
  "overall": 84.2,
  "comparability": 0.93,
  "scores": {
    "state_match": 95,
    "region_alignment": 86,
    "fixed_component_layout": 82,
    "text_integrity": 88,
    "visual_style": 80,
    "media_fit": 76,
    "anchor_integrity": 90,
    "overlap_integrity": 96
  }
}
```

### Issues Mode

Return zero, one, or two issues. Prefer one strong issue over two weak ones, and return an empty list when there is no clearly actionable problem. Do not include status bar/time/battery differences. Phrase each issue as a code-locatable UI problem, not as a vague visual mismatch.

Use this shape:

```json
{
  "issues": [
    {
      "area": "bottom join panel",
      "problem": "The information panel is not bottom-anchored and sits in the middle of the screen, leaving background content visible below it.",
      "likely_code_area": "Check the bottom sheet container's bottom positioning, parent viewport height, safe-area handling, and layer order.",
      "severity": "high"
    }
  ]
}
```

In prose responses, keep the same fields but localize the wording to the user's language.

## Issue Selection Rules

Only emit an issue when it passes all gates:

- The issue is visible at normal screenshot-viewing size.
- The issue affects layout, readability, hierarchy, anchoring, layer behavior, media fit, or a meaningful visual state.
- The issue is likely actionable in code.
- The issue is not explained only by a globally consistent scale/resolution difference.

If no issue passes these gates, return `{"issues": []}`. Do not fill the list just because two screenshots are not pixel-identical.

Choose the most obvious remaining problems in this priority order:

1. Wrong page state or missing/extra fixed UI that changes the screen's meaning.
2. Bottom/top/center anchor failures, including bottom sheets or panels not sticking to their expected edge.
3. Overlay/layer failures, including scrims not covering the intended region, clipped content, or content appearing above a layer that should cover it.
4. Large region flow shifts, such as a list/grid/card area moving up or down as a block.
5. Text integrity issues, including truncation, unintended line wrap, wrong alignment, wrong font size, or label width causing layout breakage.
6. Media fit issues, including image not centered, wrong crop, wrong aspect ratio, or grid images stretched taller/wider.
7. Visual style issues, including brightness, color, opacity, blur, or gradient differences.

When two differences have similar visibility, prefer the one that is more likely to map directly to code: anchoring, parent height, padding/margin, flex alignment, z-index/layer, text wrapping, image `object-fit`, aspect ratio, or opacity.

Suppress small issues when the overall screen reads as visually equivalent. Examples of suppressed issues include tiny icon position drift, minor color compression from JPEG, slight global scale differences, and one-off text antialiasing differences that do not affect layout or readability.

## Problem Wording

Write problems so an engineer can locate the relevant code.

Good:

- "The bottom sheet is not anchored to the bottom; its bottom edge sits far above the viewport bottom."
- "The grid content starts too low, so the first row is not covered by the top overlay as in the design."
- "The search input is too narrow or has excessive internal padding, causing the query text to be clipped."
- "The primary media image is shifted right inside its container; check image centering or `object-fit`."

Avoid:

- "This area is different."
- "The implementation does not match the design."
- "The colors are off" without naming region and likely cause.
- Any issue about time, battery, signal, or other phone status information.

## Scoring Guidance

Use model-visible region reasoning as the primary source of truth. Use the script's `final_baseline_score`, `scale_tolerant_baseline_score`, heatmaps, and band metrics as supporting evidence. `deterministic_baseline_score` is raw evidence only. When raw pixel metrics are low but the screen is the same UI with only global scale/resolution differences, ignore that difference in the final score unless it causes a concrete layout failure such as clipping, overlap, wrong anchoring, or materially different visible item count.

For mobile app screenshots, a useful default weighting is:

```text
overall =
  state_match * 0.10 +
  region_alignment * 0.18 +
  fixed_component_layout * 0.20 +
  text_integrity * 0.12 +
  visual_style * 0.12 +
  media_fit * 0.08 +
  anchor_integrity * 0.12 +
  overlap_integrity * 0.08
```

Apply penalties after the weighted score:

- Critical fixed element missing or extra: -8 to -18
- Wrong modal/page state: -10 to -25, and lower `comparability`
- Bottom/top anchor failure: -6 to -15
- Text clipped, overlapped, or unreadable: -5 to -12
- Major region shifted as a block: -4 to -12
- Media crop/aspect ratio visibly wrong: -3 to -8
- Pure color/opacity difference: -2 to -7 unless it hides content

## References

- Read `references/analysis_workflow.md` for detailed model/script coordination and region reasoning.
- Read `references/scoring_schema.md` when emitting machine-readable scores or issue JSON.
- Read `references/vlm_prompt.md` when asking a vision model to produce structured UI regions/elements/masks.
