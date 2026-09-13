from ai_agent.schemas import (
    AppointmentContext,
    RiskResult,
    TriggeredRule,
)


class HospitalRuleEngine:
    """
    Applies hospital policy rules to an appointment.

    RiskEngine determines risk.
    HospitalRuleEngine determines which policies are triggered.
    """

    def evaluate(
        self,
        context: AppointmentContext,
        risk_result: RiskResult,
    ) -> list[TriggeredRule]:
        triggered_rules: list[TriggeredRule] = []

        # Rule 1: High no-show risk requires attention.
        if risk_result.risk_level.value == "HIGH":
            triggered_rules.append(
                TriggeredRule(
                    rule_id="RISK_HIGH",
                    description="High appointment no-show risk requires intervention.",
                    priority=90,
                )
            )

        # Rule 2: Unconfirmed appointment should receive a reminder.
        if not context.patient_confirmed:
            triggered_rules.append(
                TriggeredRule(
                    rule_id="PATIENT_UNCONFIRMED",
                    description="Patient has not confirmed the appointment.",
                    priority=70,
                )
            )

        # Rule 3: Chronic-care appointments need continuity of care.
        if context.chronic_care:
            triggered_rules.append(
                TriggeredRule(
                    rule_id="CHRONIC_CARE",
                    description="Chronic-care appointment requires continuity-of-care consideration.",
                    priority=80,
                )
            )

        # Rule 4: High-priority or critical appointments may require staff review.
        if context.patient_category.value == "high_priority" or (
            context.urgency.value == "critical"
        ):
            triggered_rules.append(
                TriggeredRule(
                    rule_id="STAFF_REVIEW_PRIORITY",
                    description="High-priority or critical appointment requires staff review.",
                    priority=100,
                )
            )

        # Rule 5: Rescheduling is only useful when alternative slots exist.
        if (
            risk_result.risk_level.value == "HIGH"
            and len(context.alternative_slots) > 0
        ):
            triggered_rules.append(
                TriggeredRule(
                    rule_id="RESCHEDULE_AVAILABLE",
                    description="Alternative appointment slots are available.",
                    priority=85,
                )
            )

        return sorted(
            triggered_rules,
            key=lambda rule: rule.priority,
            reverse=True,
        )