import pandas as pd
from pathlib import Path


def load_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    return df


def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["revenue_mom_pct"] = df["revenue"].pct_change() * 100
    df["orders_mom_pct"] = df["orders"].pct_change() * 100
    df["customers_mom_pct"] = df["customers"].pct_change() * 100
    df["ad_spend_mom_pct"] = df["ad_spend"].pct_change() * 100
    df["support_tickets_mom_pct"] = df["support_tickets"].pct_change() * 100

    df["avg_order_value"] = df["revenue"] / df["orders"]
    df["customer_value"] = df["revenue"] / df["customers"]
    df["ad_spend_ratio"] = df["ad_spend"] / df["revenue"]

    return df


def generate_flags(current: pd.Series, previous: pd.Series) -> list:
    flags = []

    revenue_change = ((current["revenue"] - previous["revenue"]) / previous["revenue"]) * 100
    orders_change = ((current["orders"] - previous["orders"]) / previous["orders"]) * 100
    customers_change = ((current["customers"] - previous["customers"]) / previous["customers"]) * 100
    ad_spend_change = ((current["ad_spend"] - previous["ad_spend"]) / previous["ad_spend"]) * 100
    ticket_change = ((current["support_tickets"] - previous["support_tickets"]) / previous["support_tickets"]) * 100

    if revenue_change > 5:
        flags.append("Revenue shows strong month-over-month growth.")
    elif revenue_change < 0:
        flags.append("Revenue declined compared with the previous month.")

    if ad_spend_change > revenue_change:
        flags.append("Marketing spend grew faster than revenue, suggesting lower spend efficiency.")

    if customers_change < 2:
        flags.append("Customer growth is slowing and should be monitored.")

    if ticket_change > 8:
        flags.append("Support ticket volume increased materially, which may indicate service pressure.")

    if orders_change > 0 and revenue_change <= orders_change:
        flags.append("Order growth is positive, but revenue growth is not keeping pace, suggesting weaker monetization.")

    return flags


def build_management_summary(current: pd.Series, previous: pd.Series, flags: list) -> str:
    revenue_change = ((current["revenue"] - previous["revenue"]) / previous["revenue"]) * 100
    orders_change = ((current["orders"] - previous["orders"]) / previous["orders"]) * 100
    customers_change = ((current["customers"] - previous["customers"]) / previous["customers"]) * 100

    summary = []
    summary.append(f"Monthly Performance Summary for {current['month']}")
    summary.append("-" * 50)
    summary.append(f"Revenue: ${current['revenue']:,} ({revenue_change:.1f}% MoM)")
    summary.append(f"Orders: {current['orders']:,} ({orders_change:.1f}% MoM)")
    summary.append(f"Customers: {current['customers']:,} ({customers_change:.1f}% MoM)")
    summary.append(f"Average Order Value: ${current['avg_order_value']:.2f}")
    summary.append(f"Ad Spend as % of Revenue: {current['ad_spend_ratio']:.2%}")
    summary.append("")

    summary.append("Key Insights:")
    if flags:
        for item in flags:
            summary.append(f"- {item}")
    else:
        summary.append("- Performance remained broadly stable with no major warning signals.")

    summary.append("")
    summary.append("Suggested Actions:")
    if any("spend efficiency" in f.lower() for f in flags):
        summary.append("- Review paid acquisition channel efficiency and reallocate budget to higher-ROI campaigns.")
    if any("customer growth" in f.lower() for f in flags):
        summary.append("- Investigate acquisition funnel conversion and retention initiatives.")
    if any("support ticket" in f.lower() for f in flags):
        summary.append("- Assess customer support operations and recent service issues.")
    if not flags:
        summary.append("- Maintain current operating cadence and continue monitoring trend consistency.")

    return "\n".join(summary)


def save_report(report_text: str, output_path: str) -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)


def main():
    data_path = "data/business_metrics.csv"
    output_path = "outputs/sample_report.txt"

    df = load_data(data_path)
    df = calculate_metrics(df)

    current = df.iloc[-1]
    previous = df.iloc[-2]

    flags = generate_flags(current, previous)
    report = build_management_summary(current, previous, flags)
    save_report(report, output_path)

    print(report)


if __name__ == "__main__":
    main()