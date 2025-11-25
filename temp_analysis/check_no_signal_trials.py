import pandas as pd
import glob
import os
import matplotlib.pyplot as plt

def check_no_signal_trials():
    # specific path as requested
    path = "data/csvs_human_verified_vv/child/*.csv"
    files = glob.glob(path)
    
    results = []
    
    print(f"Found {len(files)} participant files.")
    
    for f in files:
        try:
            df = pd.read_csv(f)
            participant_id = os.path.basename(f).replace('.csv', '')
            
            # Ensure columns exist
            if 'trial_number_global' not in df.columns:
                print(f"Skipping {participant_id}: 'trial_number_global' not found.")
                continue
                
            # Group by trial
            grouped = df.groupby('trial_number_global')
            
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
            
            results.append({
                'Participant': participant_id,
                'Total_Trials': total_trials,
                'No_Signal_Trials': no_signal_trials,
                'Percent_No_Signal': (no_signal_trials / total_trials * 100) if total_trials > 0 else 0
            })
            
        except Exception as e:
            print(f"Error processing {f}: {e}")

    # Create DataFrame
    results_df = pd.DataFrame(results)
    
    # Sort by No_Signal_Trials descending
    results_df = results_df.sort_values('No_Signal_Trials', ascending=False)
    
    # Print text report
    print("\n--- Analysis Results ---")
    print(results_df.to_string(index=False))
    
    # Filter for plot: only show participants with > 0 no signal trials
    plot_df = results_df[results_df['No_Signal_Trials'] > 0]
    
    if not plot_df.empty:
        plt.figure(figsize=(12, 8))
        plt.bar(plot_df['Participant'], plot_df['No_Signal_Trials'], color='salmon')
        plt.xticks(rotation=90)
        plt.ylabel('Number of Fully "No Signal" Trials')
        plt.title('Participants with Trials Consisting Entirely of "No Signal"')
        plt.tight_layout()
        plt.savefig('temp_analysis/no_signal_trials_plot.png')
        print("\nPlot saved to temp_analysis/no_signal_trials_plot.png")
    else:
        print("\nNo participants found with completely empty trials.")

if __name__ == "__main__":
    check_no_signal_trials()

