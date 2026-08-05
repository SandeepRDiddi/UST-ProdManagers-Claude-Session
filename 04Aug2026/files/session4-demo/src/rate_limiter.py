"""
rate_limiter.py -- loads the enforced rate limit directly from config/rate_limit_config.yaml.
This is the actual value applied to every client at runtime. There is no code path
that uses 100 req/s -- that number only ever appears in README.md.
"""
import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config" / "rate_limit_config.yaml"


class RateLimiter:
    def __init__(self, config_path=CONFIG_PATH):
        with open(config_path) as f:
            cfg = yaml.safe_load(f)["rate_limit"]
        self.requests_per_second = cfg["requests_per_second"]
        self.scope = cfg["scope"]
        self.burst_allowance = cfg["burst_allowance"]

    def limit_for(self, client_id: str) -> int:
        """Returns the enforced requests-per-second limit for a given client."""
        return self.requests_per_second  # scope is per_client; every client gets the same enforced limit today

    def describe(self) -> str:
        return (f"{self.requests_per_second} req/s per client "
                f"(burst allowance: {self.burst_allowance})")


if __name__ == "__main__":
    rl = RateLimiter()
    print("Enforced rate limit:", rl.describe())
