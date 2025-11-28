"""
Test whether statsmodels GEE formula interface accepts 'weights' parameter
"""

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import statsmodels.api as sm

# Create simple test data
np.random.seed(42)
data = pd.DataFrame({
    'participant_id': ['p1', 'p1', 'p2', 'p2', 'p3', 'p3'],
    'outcome': [0.2, 0.3, 0.5, 0.6, 0.1, 0.2],
    'group': ['A', 'A', 'B', 'B', 'A', 'B'],
    'total_transitions': [2, 5, 3, 7, 4, 6]
})

print("="*80)
print("TESTING: Does smf.gee accept 'weights' parameter?")
print("="*80)
print()

# Test 1: Try using weights= parameter
print("TEST 1: Using weights= parameter (like our current code)")
print("-"*80)
try:
    model = smf.gee(
        "outcome ~ group",
        groups="participant_id",
        data=data,
        family=sm.families.Gaussian(),
        weights=data['total_transitions']
    )
    result = model.fit()
    print("[OK] SUCCESS: weights= parameter was ACCEPTED")
    print(f"  Coefficient: {result.params.get('group[T.B]', 'N/A')}")
    print(f"  Model ran without error!")
except TypeError as e:
    print(f"[FAIL] FAILED: TypeError - {e}")
except Exception as e:
    print(f"[FAIL] FAILED: {type(e).__name__} - {e}")
print()

# Test 2: Try using freq_weights= parameter
print("TEST 2: Using freq_weights= parameter (as reviewer suggested)")
print("-"*80)
try:
    model = smf.gee(
        "outcome ~ group",
        groups="participant_id",
        data=data,
        family=sm.families.Gaussian(),
        freq_weights=data['total_transitions']
    )
    result = model.fit()
    print("[OK] SUCCESS: freq_weights= parameter was ACCEPTED")
    print(f"  Coefficient: {result.params.get('group[T.B]', 'N/A')}")
except TypeError as e:
    print(f"[FAIL] FAILED: TypeError - {e}")
except Exception as e:
    print(f"[FAIL] FAILED: {type(e).__name__} - {e}")
print()

# Test 3: Check if they produce different results
print("TEST 3: Do weights= and freq_weights= produce different results?")
print("-"*80)

results_weights = None
results_freq_weights = None

try:
    model1 = smf.gee("outcome ~ group", groups="participant_id", data=data,
                     family=sm.families.Gaussian(), weights=data['total_transitions'])
    results_weights = model1.fit()
except:
    pass

try:
    model2 = smf.gee("outcome ~ group", groups="participant_id", data=data,
                     family=sm.families.Gaussian(), freq_weights=data['total_transitions'])
    results_freq_weights = model2.fit()
except:
    pass

if results_weights and results_freq_weights:
    coef_weights = results_weights.params.get('group[T.B]', None)
    coef_freq = results_freq_weights.params.get('group[T.B]', None)
    print(f"weights= coefficient:      {coef_weights:.6f}")
    print(f"freq_weights= coefficient: {coef_freq:.6f}")

    if abs(coef_weights - coef_freq) < 0.0001:
        print("-> Results are IDENTICAL")
    else:
        print(f"-> Results DIFFER by {abs(coef_weights - coef_freq):.6f}")
elif results_weights:
    print("Only weights= worked")
elif results_freq_weights:
    print("Only freq_weights= worked")
else:
    print("Neither worked!")
print()

# Test 4: Test with actual GEE class (not formula interface)
print("TEST 4: Direct GEE class (not formula interface)")
print("-"*80)
from statsmodels.genmod.generalized_estimating_equations import GEE

# Create design matrix manually
data['intercept'] = 1
data['group_B'] = (data['group'] == 'B').astype(int)
X = data[['intercept', 'group_B']]
y = data['outcome']

try:
    model_direct = GEE(
        endog=y,
        exog=X,
        groups=data['participant_id'],
        family=sm.families.Gaussian(),
        weights=data['total_transitions']
    )
    result_direct = model_direct.fit()
    print("[OK] SUCCESS: Direct GEE class with weights= works")
    print(f"  Coefficient: {result_direct.params[1]}")
except Exception as e:
    print(f"[FAIL] FAILED: {type(e).__name__} - {e}")
print()

print("="*80)
print("CONCLUSION")
print("="*80)
if results_weights:
    print("[OK] Your current code (weights=) WORKS CORRECTLY")
    print("  The reviewer may be mistaken or using a different statsmodels version")
else:
    print("[FAIL] The reviewer is correct - you need to change to freq_weights=")
    print("  Your current code with weights= will fail or be ignored")
