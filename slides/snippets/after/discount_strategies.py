# after/app/domain/packages/discount_policy.py — OCP cure
class DiscountPolicy(Protocol):
    def apply(self, package: TravelPackage) -> Decimal: ...


class NoDiscount:
    def apply(self, p): return p.base_price

class SeasonalDiscount:
    def apply(self, p): return (p.base_price * Decimal("0.85")).quantize(...)

class BlackFridayDiscount:
    def apply(self, p): return (p.base_price * Decimal("0.70")).quantize(...)

class CorporateDiscount:
    def apply(self, p): return max(Decimal("0"), p.base_price - Decimal("200"))

class CyberMondayDiscount:
    THRESHOLD = Decimal("5000")
    def apply(self, p):
        factor = Decimal("0.75") if p.base_price > self.THRESHOLD else Decimal("0.90")
        return (p.base_price * factor).quantize(...)


# Nova promoção = nova classe. Zero edição nas existentes.
