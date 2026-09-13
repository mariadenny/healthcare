from ai_agent.schemas import (
    AppointmentContext,
    RiskFactor,
    RiskLevel,
    RiskResult,
)


class RiskEngine:
    """
    Calculates appointment no-show risk.

    The score is intentionally rule-based and explainable.
    """

    def evaluate(self, context: AppointmentContext) -> RiskResult:
        score = 0.0
        factors: list[RiskFactor] = []

        # Previous no-shows
        if context.previous_no_shows > 0:
            contribution = min(context.previous_no_shows * 20, 50)

            score += contribution

            factors.append(
                RiskFactor(
                    factor="previous_no_shows",
                    value=context.previous_no_shows,
                    contribution=contribution,
                )
            )

        # Previous cancellations
        if context.previous_cancellations > 0:
            contribution = min(context.previous_cancellations * 10, 30)

            score += contribution

            factors.append(
                RiskFactor(
                    factor="previous_cancellations",
                    value=context.previous_cancellations,
                    contribution=contribution,
                )
            )

        # Patient has not confirmed
        if not context.patient_confirmed:
            contribution = 20.0

            score += contribution

            factors.append(
                RiskFactor(
                    factor="patient_not_confirmed",
                    value=False,
                    contribution=contribution,
                )
            )

        # Chronic care appointments receive additional attention
        if context.chronic_care:
            contribution = 10.0

            score += contribution

            factors.append(
                RiskFactor(
                    factor="chronic_care",
                    value=True,
                    contribution=contribution,
                )
            )

        # Cap the score at 100
        score = min(score, 100.0)

        # Convert numerical score to risk level
        if score >= 60:
            risk_level = RiskLevel.HIGH
        elif score >= 30:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        return RiskResult(
            risk_score=score,
            risk_level=risk_level,
            risk_factors=factors,
        )