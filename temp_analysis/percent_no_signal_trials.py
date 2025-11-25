import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import numpy as np

def analyze_no_signal_percentage():
    # specific path as requested
    path = "data/csvs_human_verified_vv/child/*.csv"
    files = glob.glob(path)
    
    print(f"Found {len(files)} participant files.")
    
    results = []
    
    for f in files:
        try:
            # Read the whole file to get all frame data
            # 'What' and 'Where' columns are needed to determine signal status
            # 'trial_number_global' and 'event_verified' to group by unique trial
            df = pd.read_csv(f, usecols=['trial_number_global', 'event_verified', 'What', 'Where'])
            participant_id = os.path.basename(f).replace('.csv', '')
            
            if df.empty:
                continue
                
            # Group by unique trial (combination of event and trial number)
            # This handles cases where trial numbers reset or repeat for different events
            grouped = df.groupby(['event_verified', 'trial_number_global'])
            
            total_trials = 0
            no_signal_trials = 0
            
            for name, group in grouped:
                total_trials += 1
                
                # Check if ALL rows in this trial are no/signal
                # Assuming 'no' in What and 'signal' in Where
                # We'll be strict: What=='no' AND Where=='signal'
                
                is_no_signal = ((group['What'] == 'no') & (group['Where'] == 'signal')).all()
                
                if is_no_signal:
                    no_signal_trials += 1
            
            percentage = (no_signal_trials / total_trials * 100) if total_trials > 0 else 0
            
            results.append({
                'Participant': participant_id,
                'Total_Trials': total_trials,
                'No_Signal_Trials': no_signal_trials,
                'Percent_No_Signal': percentage
            })
            
        except Exception as e:
            print(f"Error processing {f}: {e}")

    if not results:
        print("No results to plot.")
        return

    # Create DataFrame
    results_df = pd.DataFrame(results)
    
    # Sort by percentage descending
    results_df = results_df.sort_values('Percent_No_Signal', ascending=False)
    
    print("\n--- Analysis Results: Percentage of completely 'No Signal' trials ---")
    print(results_df.to_string(index=False))
    
    # Plotting
    plt.figure(figsize=(14, 7))
    
    # Create bars
    bars = plt.bar(results_df['Participant'], results_df['Percent_No_Signal'], color='crimson', edgecolor='black')
    
    # Add labels and title
    plt.title('Percentage of Completely "No Signal" Trials per Participant', fontsize=16)
    plt.xlabel('Participant', fontsize=12)
    plt.ylabel('Percentage of Trials (%)', fontsize=12)
    
    # Rotate x-axis labels for readability
    plt.xticks(rotation=90, fontsize=9)
    
    # Add grid lines
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add percentage labels on top of bars
    for bar in bars:
        height = bar.get_height()
        if height > 0:  # Only label bars with data
            plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                     f'{height:.1f}%',
                     ha='center', va='bottom', fontsize=8, rotation=0)
    
    plt.tight_layout()
    
    # Save plot
    output_path = 'temp_analysis/percent_no_signal_trials.png'
    plt.savefig(output_path, dpi=300)
    print(f"\nPlot saved to {output_path}")

if __name__ == "__main__":
    analyze_no_signal_percentage()

