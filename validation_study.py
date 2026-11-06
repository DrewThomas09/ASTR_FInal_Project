"""Show a positive-control and noise-only BLS search using simulated data."""
from exoplanet_detector import run
if __name__ == "__main__":
    print("Injected planet:",run(planet=True, out="results/validation"))
    print("Noise-only control:",run(planet=False, out="results/validation"))
