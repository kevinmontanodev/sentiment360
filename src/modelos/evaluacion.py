"""Evaluacion de umbrales de decision mediante una matriz de costos"""

from dataclasses import dataclass

@dataclass(frozen=True)
class CostScenario:

    """Supuestos del escenario de simulacion (US Dollars)"""
    monthly_salary: float = 750.0
    employer_cost_rate: float = 0.259
    weekly_hours: float = 44.0
    shrinkage: float = 0.3
    review_minutes: float = 5.0
    contact_minutes: float = 10.0
    customer_value: float = 100.0
    churn_without_contact: float = 0.35
    churn_with_contact: float = 0.25

    @property
    def cost_per_minute(self) -> float:
        """Costo de un minuto productivo de un agente"""
        monthly_cost = self.monthly_salary * (1 + self.employer_cost_rate)
        monthly_hours = self.weekly_hours * 52 / 12
        productive_hours = monthly_hours * (1 - self.shrinkage)
        return monthly_cost / productive_hours / 60
    
    @property
    def fp_cost(self) -> float:
        """Falso positivo: el agente lee una reseña que no necesitaba atencion"""
        return self.review_minutes * self.cost_per_minute
    
    @property
    def tp_cost(self) -> float:
        """Verdadero positivo: el agente contacta al cliente y baja la probabilidad de abandono"""
        handling = (self.review_minutes + self.contact_minutes) * self.cost_per_minute
        return self.churn_with_contact * self.customer_value + handling
    
    @property
    def fn_cost(self) -> float:
        """Falso negativo: nadie contacta al cliente insatisfecho"""
        return self.churn_without_contact * self.customer_value