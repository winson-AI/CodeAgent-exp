# Analysis Workflow

## Standardization

Normalize screenshots before comparing:

1. Load with EXIF orientation applied.
2. Convert to RGB.
3. Resize both images to the same logical width without stretching.
4. Ignore the top status/system information area. Default to 44 logical pixels after normalization unless a project config provides another value.
5. Compare common visible height for full-screen pages.
6. Align bottom-anchored regions from the bottom when evaluating bottom navigation, dialogs, sheets, and fixed bottom panels.
7. Evaluate a small uniform scale tolerance before calling a region wrong. A candidate that is consistently larger or smaller because of resolution/device scaling can still be highly similar.

Do not let device status differences become final issues. They are environment differences.

## Model And Script Roles

Use scripts for reproducible evidence only:

- dimensions
- normalized images
- heatmaps
- region band metrics
- global visual similarity
- edge similarity
- color distance
- simple candidate issue hints
- `final_baseline_score`, which ignores explainable global scale/resolution differences at script level
- raw baseline metrics, retained only as evidence

Use the model for semantic UI reasoning:

- page type
- region boundaries
- region-by-region comparison
- expected anchor
- fixed UI vs dynamic content
- global scale/resolution interpretation
- text alignment/wrapping intent
- overlay and layer relationships
- whether there are zero, one, or two issues worth reporting

The script must not drive the final judgment by itself. Low SSIM often reflects resolution, JPEG compression, dynamic media, or small global scale differences. Use `final_baseline_score` as the script-level score because it already applies scale tolerance. Treat raw SSIM and `deterministic_baseline_score` as diagnostic evidence only.

## Scale And Resolution Tolerance

Design screenshots and implementation screenshots often have different physical resolutions, device pixel ratios, crop heights, or preview scaling. Do not report a problem only because the candidate is uniformly larger/smaller.

Treat a global scale difference as acceptable when:

- most regions preserve their anchors
- text remains readable and not clipped
- spacing relationships are consistent
- visible item count is materially the same for the page type
- the screen still reads as the same UI state at normal viewing size

Report scale-related problems only when there is a concrete UI failure:

- text or chips wrap/clips because controls are too small
- media tiles become visibly too tall/wide
- a bottom/top panel no longer sticks to its anchor
- a list/grid shows materially different rows because item height changed
- global zoom breaks containment or causes overlap

When judging scale, compare semantic regions independently. A whole-screen scale change can be acceptable, while a single region scaling differently from surrounding regions may be a layout bug.

## Page Types

Identify the page type first because weights change by type:

- **full_screen_app**: header, tabs, content, bottom nav. Emphasize fixed UI and content flow.
- **list_or_grid**: repeated items. Emphasize item density, row/column placement, and text wrapping. Lower dynamic image content weight.
- **media_immersive**: image/video/background-heavy. Emphasize media crop, overlays, bottom actions, brightness/opacity.
- **bottom_sheet_or_dialog**: scrim + panel. Emphasize panel anchor, top radius, internal spacing, button placement, and scrim color/opacity.
- **empty_error_skeleton**: empty/error/loading page. Emphasize center positioning, skeleton geometry, and text/button alignment.

## Semantic Checks

Check these properties for each region:

- **anchor**: top, bottom, center, or content-flow. Anchor failures outrank ordinary pixel drift.
- **alignment**: left, center, right, baseline, and grid alignment.
- **flow**: whether a whole section shifted as a block and whether internal relative layout stayed intact.
- **layering**: whether overlays cover the intended region and whether content appears above/below the right layer.
- **text integrity**: clipping, unintended wrap, font size, label width, line height, and alignment.
- **media fit**: crop, centering, aspect ratio, object-fit, and whether image tiles appear stretched.
- **style**: color, brightness, opacity, blur, gradient, and shadow.

Always perform these checks at region level. Do not rely on full-image heatmaps to decide issues. Heatmaps are useful for finding candidate areas to inspect, not for choosing final issues.

## Comparability

Use `comparability` to express whether the two screenshots are the same UI state:

- `0.90-1.00`: same screen/state; normal reconstruction scoring.
- `0.70-0.89`: comparable with dynamic content, minor scroll, or non-critical data differences.
- `0.40-0.69`: partially comparable; page state or scroll differs enough to limit scoring.
- `<0.40`: different route/state; score should be treated as low-confidence.

Do not reduce comparability for a clear implementation layout bug. A bottom panel not sticking to the bottom, a list region starting too low, or a modal scrim not covering the right area should remain comparable and be reported as a layout issue.

## Top Issue Selection

After identifying visible differences, filter them first. Keep only differences that are clear, code-locatable, and impactful enough to mention. It is valid to return zero issues for a near-match.

Then keep at most two. Sort by:

1. User-visible severity.
2. Whether the issue affects fixed UI or core content.
3. Whether it maps to a likely code constraint.
4. Whether it explains multiple visible symptoms.

Prefer root-cause descriptions over surface comparisons. For example, "the bottom panel is not anchored" is better than "the bottom panel is higher than the design."

Do not add a second issue just to reach two. If the strongest remaining issue is minor, omit it.
