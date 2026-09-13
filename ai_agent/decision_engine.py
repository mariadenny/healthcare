from ai_agent.schemas import (
    AppointmentContext,
    Decision,
    RiskResult,
    TriggeredRule,
)


class DecisionEngine:
    """
    Converts risk and hospital rules into an operational decision.
    """

    def decide(
        self,
        context: AppointmentContext,
        risk_result: RiskResult,
        triggered_rules: list[TriggeredRule],
    ) -> Decision:

        # Critical or high-priority cases always go to staff.
        if (
            context.urgency.value == "critical"
            or context.patient_category.value == "high_priority"
        ):
            return Decision.ESCALATE_TO_STAFF

        # High-risk patients with alternatives should be offered
        # a different appointment slot.
        if (
            risk_result.risk_level.value == "HIGH"
            and len(context.alternative_slots) > 0
        ):
            return Decision.OFFER_RESCHEDULE

        # An unconfirmed appointment should receive a reminder.
        if not context.patient_confirmed:
            return Decision.SEND_REMINDER

        # Nothing requires intervention.
        return Decision.NO_ACTION