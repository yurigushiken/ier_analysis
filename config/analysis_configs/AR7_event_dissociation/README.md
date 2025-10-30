# AR7 Event Dissociation - Configuration Directory

## Overview

This directory contains configuration assets for AR7 Event Dissociation Analysis, combining toy-looking (AR1) and social triplet (AR3) metrics to test whether SHOW events dissociate from GIVE and HUG.

## File Structure
- ar7_config.yaml - Base defaults shared across variants
- ar7_explanation.md - Scientific notes and interpretation guidance
- ar7_show_vs_give_hug.yaml - Standard SHOW vs GIVE vs HUG comparison
- README.md - This guide

## Configuration System
- Base config defines contrasts, metrics, and visualisation defaults.
- Variant configs specify target condition families and cohort filters.

## Running AR7
1. Activate the environment: conda activate ier_analysis
2. Set the variant: $env:IER_AR7_CONFIG='AR7_event_dissociation/ar7_show_vs_give_hug'
3. Run analysis: python -m src.analysis.ar7_dissociation
4. Clear override: Remove-Item Env:IER_AR7_CONFIG

Batch execution: python scripts/run_ar7_variants.py

## Outputs
- Reports saved under results/AR7_Event_Dissociation/<variant>/
- Per-metric CSV tables and pairwise comparisons
- Bar plots for each metric (toy looking, social triplets)
- HTML/PDF report summarising dissociation findings
