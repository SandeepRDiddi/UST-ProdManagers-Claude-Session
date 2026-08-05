#!/usr/bin/env python3
"""
escalation_audit.py -- the Escalation Path check Case 2 was missing, built after the fact.

Reads message-routing metadata (no message content -- routing flags only) and
finds every message that carried an escalation signal but was answered
directly instead of routed to a human, plus how long it actually took a
human to see it once the pattern was caught.

Usage:
    python3 escalation_audit.py patient_messages.csv
"""
import sys
import pandas as pd

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 escalation_audit.py <patient_messages_csv>")
        sys.exit(1)

    df = pd.read_csv(sys.argv[1])

    signal = df[df.escalation_signal_flag == 1]
    missed = signal[signal.routed_to_human == 0]
    routed = signal[signal.routed_to_human == 1]

    print(f"Loaded {len(df)} messages over the period")
    print(f"Messages carrying an escalation signal: {len(signal)}")
    print(f"\nESCALATION-PATH GAP -- signal present, but answered directly instead of routed: {len(missed)}")
    print(f"  Average time before a human actually saw one (caught later, in audit): "
          f"{missed.hours_to_human_response.mean():.1f}h (~{missed.hours_to_human_response.mean()/24:.1f} days)")
    print(f"\nFor comparison -- properly routed escalation-signal messages: {len(routed)}")
    print(f"  Average time to human response: {routed.hours_to_human_response.mean():.1f}h")

    print("\nRecommendation: any message carrying an escalation signal routes to a human by default. "
          "The agent may still draft a response, but a human sends it.")

if __name__ == "__main__":
    main()
