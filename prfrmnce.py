from DeterministicAnonymizer import DeterministicAnonymizer, config
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt

# Function to generate test data
def generate_test_data(size):
    return pd.DataFrame({
        'name': ['Test' + str(i) for i in range(size)],
        'age': np.random.randint(18, 80, size),
        'credit_card_number': ['4532' + str(i).zfill(12) for i in range(size)],
        'zip_code': ['1234' + str(i)[-1] for i in range(size)],
        'blood_sugar': np.random.normal(100, 10, size)
    })

# Performance measurement function
def measure_performance(sizes, num_trials=3):
    times_anonymize = []
    times_deanonymize = []
    anonymizer = DeterministicAnonymizer(key="mysecretkey")
    
    for size in sizes:
        anonymization_times = []
        deanonymization_times = []
        
        for _ in range(num_trials):
            df = generate_test_data(size)
            
            # Measure anonymization time
            start = time.time()
            anonymized = anonymizer.anonymize(df, config)
            anonymization_times.append(time.time() - start)
            
            # Measure deanonymization time
            start = time.time()
            original = anonymizer.deanonymize(anonymized, config)
            deanonymization_times.append(time.time() - start)
        
        # Record the average time for anonymization and deanonymization
        times_anonymize.append(np.mean(anonymization_times))
        times_deanonymize.append(np.mean(deanonymization_times))
    
    return times_anonymize, times_deanonymize

# Test with different sizes
sizes = [100, 1000, 5000, 10000, 50000, 100000]
times_anon, times_deanon = measure_performance(sizes)

# Plot results
plt.figure(figsize=(10, 6))
plt.plot(sizes, times_anon, 'b-', label='Anonymization')
plt.plot(sizes, times_deanon, 'r-', label='Deanonymization')
plt.xlabel('Dataset Size')
plt.ylabel('Time (seconds)')
plt.title('Performance Analysis')
plt.legend()
plt.grid(True)
# plt.yscale('log')  # Log scale for better visibility of performance trend
plt.savefig('performance_analysis_log_scale.png')

# Print time metrics and complexity analysis
print("\nTime Metrics:")
for size, time_anon, time_deanon in zip(sizes, times_anon, times_deanon):
    print(f"Size: {size} -> Anonymization Time (avg): {time_anon:.5f} s, Deanonymization Time (avg): {time_deanon:.5f} s")

print("\nComplexity Analysis:")
for i in range(1, len(sizes)):
    ratio_anon = times_anon[i] / times_anon[i-1]
    ratio_deanon = times_deanon[i] / times_deanon[i-1]
    size_ratio = sizes[i] / sizes[i-1]
    print(f"Size increase: {size_ratio}x, Anonymization Time increase: {ratio_anon:.2f}x, Deanonymization Time increase: {ratio_deanon:.2f}x")

    # Estimate Big O Complexity (linear, quadratic, etc.)
    if ratio_anon > size_ratio and ratio_deanon > size_ratio:
        complexity_anon = 'Superlinear/Quadratic'
        complexity_deanon = 'Superlinear/Quadratic'
    else:
        complexity_anon = 'Linear'
        complexity_deanon = 'Linear'
    
    print(f"Estimated complexity for Anonymization: {complexity_anon}, Deanonymization: {complexity_deanon}")
