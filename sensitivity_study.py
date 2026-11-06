"""Convenience runner for the existing controlled injection-recovery simulation."""
from exoplanet_detector import sensitivity_study
if __name__ == "__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--output", default="results/sensitivity")
    p.add_argument("--trials", type=int, default=12)
    a=p.parse_args()
    print(sensitivity_study(out=a.output, trials=a.trials))
