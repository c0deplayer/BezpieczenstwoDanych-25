"""Performance testing module for various anonymization methods."""

import argparse
import time
from typing import Any, Callable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from BitwiseDualKeyAnonymizer.anonymizer import TypeAwareDualKeyAnonymizer
from DeterministicAnonymizer import DeterministicAnonymizer, config
from Shuffling.anonymizer import anonimizacja as shuffle_anonymize
from Shuffling.anonymizer import deanonimizacja as shuffle_deanonymize


# Function to generate test data
def generate_test_data(size):
    return pd.DataFrame(
        {
            "name": ["Test" + str(i) for i in range(size)],
            "age": np.random.randint(18, 80, size),
            "credit_card_number": [
                "4532" + str(i).zfill(12) for i in range(size)
            ],
            "zip_code": ["1234" + str(i)[-1] for i in range(size)],
            "blood_sugar": np.random.normal(100, 10, size),
        },
    )


def get_anonymizer(method: str) -> tuple[Callable, Callable, Any]:
    """Get anonymization and deanonymization functions based on method.

    Args:
        method: Name of the anonymization method ('deterministic', 'shuffle', 'bitwise')

    Returns:
        Tuple of (anonymize_fn, deanonymize_fn, config_or_key_or_None)

    """
    match method:
        case "deterministic":
            anonymizer = DeterministicAnonymizer(key="SecretKey#123")
            return anonymizer.anonymize, anonymizer.deanonymize, config
        case "shuffle":
            return shuffle_anonymize, shuffle_deanonymize, [7, 13]
        case "bitwise":
            anonymizer = TypeAwareDualKeyAnonymizer(
                primary_key="SecretKey#123",
                secondary_key="SecretKet@987",
            )
            return anonymizer.anonymize, anonymizer.deanonymize, None
        case _:
            raise ValueError(f"Unknown anonymization method: {method}")


def measure_performance(
    sizes: list[int],
    anonymize_fn: Callable,
    deanonymize_fn: Callable,
    config: Any,
    num_trials: int = 3,
    anon_method: str = "deterministic",
) -> tuple[list[float], list[float]]:
    """Measure performance of anonymization functions.

    Args:
        sizes: List of dataset sizes to test
        anonymize_fn: Anonymization function
        deanonymize_fn: Deanonymization function
        config: Configuration for the anonymization method
        num_trials: Number of trials for each size
        anon_method: Name of the anonymization method being tested

    Returns:
        Tuple of (anonymization_times, deanonymization_times)

    """
    times_anonymize: list[float] = []
    times_deanonymize: list[float] = []

    for size in sizes:
        anonymization_times: list[float] = []
        deanonymization_times: list[float] = []

        for _ in range(num_trials):
            df = generate_test_data(size)

            if anon_method.lower() == "bitwise":
                # For bitwise, we need to handle each column separately and convert to string
                start = time.time()
                anonymized = df.map(anonymize_fn)

                anonymization_times.append(time.time() - start)

                start = time.time()
                original = anonymized.map(deanonymize_fn)

                deanonymization_times.append(time.time() - start)
            else:
                start = time.time()
                anonymized = anonymize_fn(df, config)
                anonymization_times.append(time.time() - start)

                start = time.time()
                original = deanonymize_fn(anonymized, config)
                deanonymization_times.append(time.time() - start)

        times_anonymize.append(np.mean(anonymization_times))
        times_deanonymize.append(np.mean(deanonymization_times))

    return times_anonymize, times_deanonymize


def plot_results(
    sizes: list[int],
    times_anon: list[float],
    times_deanon: list[float],
    method: str,
) -> None:
    """Plot performance results and save to file."""
    plt.figure(figsize=(10, 6))
    plt.plot(sizes, times_anon, "b-", label="Anonymization")
    plt.plot(sizes, times_deanon, "r-", label="Deanonymization")
    plt.xlabel("Dataset Size")
    plt.ylabel("Time (milliseconds)")
    plt.title(f"Performance Analysis - {method.title()} Method")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"performance_analysis_{method}.png")


def main() -> None:
    """Main function for performance testing."""
    parser = argparse.ArgumentParser(
        description="Test anonymization performance",
    )
    parser.add_argument(
        "--method",
        "-m",
        choices=["deterministic", "shuffle", "bitwise"],
        default="deterministic",
        help="Anonymization method to test",
    )
    parser.add_argument(
        "--sizes",
        "-s",
        nargs="+",
        type=int,
        default=[100, 1000, 5000, 10000, 50000, 100000],
        help="Dataset sizes to test",
    )
    args = parser.parse_args()

    anonymize_fn, deanonymize_fn, config = get_anonymizer(args.method)
    times_anon, times_deanon = measure_performance(
        args.sizes,
        anonymize_fn,
        deanonymize_fn,
        config,
        num_trials=3,
        anon_method=args.method,
    )

    plot_results(args.sizes, times_anon, times_deanon, args.method)

    # Print performance metrics
    print(f"\nPerformance Analysis for {args.method.title()} Method:")
    for size, time_anon, time_deanon in zip(
        args.sizes,
        times_anon,
        times_deanon,
    ):
        print(
            f"Size: {size} -> Anonymization: {time_anon:.5f}s, Deanonymization: {time_deanon:.5f}s",
        )


if __name__ == "__main__":
    main()
