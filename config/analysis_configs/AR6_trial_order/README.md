# AR6 Trial-Order Effects - Configuration Directory

## Overview

This directory contains configuration assets for AR6 Trial-Order Effects Analysis, examining learning versus habituation across repeated event presentations.

## File Structure
- ar6_config.yaml - Shared defaults (trial variable, statistics, plotting)
- ar6_explanation.md - Scientific notes
- ar6_gw_vs_hw.yaml - Standard GIVE_WITH vs HUG_WITH variant
- README.md - This guide

## Running AR6
1. Activate the environment: conda activate ier_analysis
2. Set the variant: $env:IER_AR6_CONFIG='AR6_trial_order/ar6_gw_vs_hw'
3. Run analysis: python -m src.analysis.ar6_learning
4. Clear override: Remove-Item Env:IER_AR6_CONFIG

Batch execution: python scripts/run_ar6_variants.py

## Outputs
- Results saved under results/AR6_Trial_Order/<variant>/
- Trial-level CSV exports and regression summaries
- Participant slope and classification tables
- HTML/PDF report describing learning or habituation patterns
