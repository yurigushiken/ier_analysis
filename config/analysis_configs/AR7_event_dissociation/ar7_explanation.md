# AR7 Event Dissociation - Scientific Notes

## Purpose

AR7 combines two complementary metrics to test the dissociation hypothesis:

1. Proportion of primary AOIs (toy and faces) - derived from AR1 gaze proportions.
2. Social triplet rate - derived from AR3 (face-toy-face) sequences.

SHOW events are expected to match GIVE in toy attention but diverge in social triplet frequency, demonstrating that visual salience alone does not drive event understanding.

## Data Preparation

- Off-screen fixations are removed before calculating proportions or triplets.
- Toy anticipation (toy_location) is treated as a primary AOI so WITHOUT variants can be analysed.
- Raw condition names (e.g., GIVE_WITH, SHOW_WITHOUT, upside-down variants) are mapped to GIVE/HUG/SHOW families.

## Interpretation Checklist

- Positive dissociation evidence: SHOW matches GIVE on toy attention but falls below in social triplet rate.
- Null dissociation: SHOW aligns with GIVE/HUG on both metrics - note potential power limitations.
- Review pairwise comparison tables and effect sizes for each metric.
- Cross-check exported CSVs to validate aggregation before reporting.

## Reporting Guidance

- Highlight both metrics side-by-side in the overview section.
- Use cohort-specific results (infant vs adult) to discuss developmental contrasts when applicable.
- Reference Gordon (2003) when explaining the theoretical motivation for dissociation.
