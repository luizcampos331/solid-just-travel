"""StdoutWelcomeNotifier — prints to stdout, fake-SMTP style.

Real systems would swap this for an email service adapter that implements
the same `WelcomeNotifier` Protocol. That is the DIP payoff: one config
line in the composition root, no code change anywhere else.
"""

from after.app.domain.travelers.traveler import Traveler


class StdoutWelcomeNotifier:
    def notify_welcome(self, traveler: Traveler) -> None:
        print(f"[FAKE SMTP] Welcome email sent to {traveler.email}")
