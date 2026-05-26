from dataclasses import dataclass


@dataclass(frozen=True)
class TrendResult:
    slope: float
    intercept: float
    forecast: float
    direction: str
    points_count: int
    demand_forecast: float
    supply_slope: float
    supply_intercept: float
    supply_forecast: float
    supply_direction: str
    stock_gap: float


class SalesTrendModel:
    """Линейная модель спроса и предложения по недельным точкам продаж."""

    def calculate(self, sales_points, supply_units=None):
        sales_points = list(sales_points)
        points = [(point.week_number, point.units_sold) for point in sales_points]
        supply_units = self._resolve_supply_units(sales_points, supply_units)
        if len(points) < 2:
            value = float(points[0][1]) if points else 0.0
            return self._build_result(
                slope=0.0,
                intercept=value,
                demand_forecast=value,
                direction="недостаточно данных",
                points_count=len(points),
                supply_units=supply_units,
            )

        n = len(points)
        sum_x = sum(x for x, _ in points)
        sum_y = sum(y for _, y in points)
        sum_xy = sum(x * y for x, y in points)
        sum_x2 = sum(x * x for x, _ in points)
        denominator = n * sum_x2 - sum_x * sum_x

        slope = 0.0 if denominator == 0 else (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n
        next_week = max(x for x, _ in points) + 1
        demand_forecast = max(0.0, slope * next_week + intercept)

        if slope > 0.25:
            direction = "растущий спрос"
        elif slope < -0.25:
            direction = "падающий спрос"
        else:
            direction = "стабильный спрос"

        return self._build_result(
            slope=slope,
            intercept=intercept,
            demand_forecast=demand_forecast,
            direction=direction,
            points_count=n,
            supply_units=supply_units,
        )

    def _resolve_supply_units(self, sales_points, supply_units):
        if supply_units is not None:
            return float(supply_units)
        if not sales_points:
            return 0.0
        return float(sales_points[0].product.stock)

    def _build_result(self, slope, intercept, demand_forecast, direction, points_count, supply_units):
        supply_forecast = max(0.0, supply_units)
        sales_forecast = min(demand_forecast, supply_forecast)
        stock_gap = supply_forecast - demand_forecast

        if supply_forecast <= 0:
            supply_direction = "товара нет в наличии"
        elif stock_gap < 0:
            supply_direction = "предложение ниже спроса"
        elif demand_forecast == 0:
            supply_direction = "предложение есть, спрос не выражен"
        else:
            supply_direction = "предложения хватает"

        return TrendResult(
            slope=round(slope, 2),
            intercept=round(intercept, 2),
            forecast=round(sales_forecast, 1),
            direction=direction,
            points_count=points_count,
            demand_forecast=round(demand_forecast, 1),
            supply_slope=0.0,
            supply_intercept=round(supply_units, 2),
            supply_forecast=round(supply_forecast, 1),
            supply_direction=supply_direction,
            stock_gap=round(stock_gap, 1),
        )
