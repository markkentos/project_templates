from dataclasses import dataclass


@dataclass(frozen=True)
class TrendResult:
    slope: float
    intercept: float
    forecast: float
    direction: str
    points_count: int


class SalesTrendModel:
    """Линейная модель прогноза продаж y = ax + b по недельным точкам."""

    def calculate(self, sales_points):
        points = [(point.week_number, point.units_sold) for point in sales_points]
        if len(points) < 2:
            value = float(points[0][1]) if points else 0.0
            return TrendResult(0.0, value, value, "недостаточно данных", len(points))

        n = len(points)
        sum_x = sum(x for x, _ in points)
        sum_y = sum(y for _, y in points)
        sum_xy = sum(x * y for x, y in points)
        sum_x2 = sum(x * x for x, _ in points)
        denominator = n * sum_x2 - sum_x * sum_x

        slope = 0.0 if denominator == 0 else (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n
        next_week = max(x for x, _ in points) + 1
        forecast = max(0.0, slope * next_week + intercept)

        if slope > 0.25:
            direction = "растущий спрос"
        elif slope < -0.25:
            direction = "падающий спрос"
        else:
            direction = "стабильный спрос"

        return TrendResult(
            slope=round(slope, 2),
            intercept=round(intercept, 2),
            forecast=round(forecast, 1),
            direction=direction,
            points_count=n,
        )
