# AR6 Trial-Order Effects - Scientific Notes

## Aim

AR6 tests whether gaze metrics change across repeated presentations of the same event type, capturing learning (positive slopes) or habituation (negative slopes).

## Metrics

- Proportion of primary AOIs per trial (faces and toy location)
- Social triplet frequency per trial (optional future metric)

## Modelling

- Linear mixed models with participant random intercepts and slopes for trial order
- Participant-level slope summaries and optional learner/adapter/stable classification

## Interpretation Tips

- Inspect slope direction and significance for each condition
- Compare infant and adult cohorts, if both are enabled
- Use exported CSVs to validate trial sequences when anomalies appear
