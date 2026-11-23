"""Create demo_project/: a tiny shop app whose report crashed last night.

Dates are based on the report's last run (02:14 every night), so "last night" is true at any hour.
Run it again to reset the demo.
"""
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

APP = '''"""Nightly report: average order value for yesterday."""
import csv
from datetime import datetime, timedelta


def load_orders(day):
    with open(f"orders/orders_{day}.csv", newline="") as f:
        return [float(row["amount"]) for row in csv.DictReader(f)]


def average_order_value(day):
    orders = load_orders(day)
    total = sum(orders)
    return total / len(orders)


if __name__ == "__main__":
    last_run_day = (datetime.now() - timedelta(hours=2, minutes=14)).date()
    day = last_run_day - timedelta(days=1)
    print(f"Average order value for {day}: {average_order_value(day):.2f}")
'''

README = """# Shop report

Runs every night at 02:14 and prints yesterday's average order value.
Orders come from orders/orders_YYYY-MM-DD.csv. The server's scheduler runs it, writes logs/ (start, disk check, the report's output, Done), and logs "Report failed" if it crashes.

TODO: send the report by email.
"""

ORDERS = ["order_id,amount\n1001,35.50\n1002,48.00\n1003,40.10\n", "order_id,amount\n1004,22.00\n1005,61.40\n", "order_id,amount\n"]
AVERAGES = ["41.20", "41.70"]


def at(day, hhmm):
    return datetime.combine(day, datetime.strptime(hhmm, "%H:%M").time())


def write(path, text, when):
    path.write_text(text)
    stamp = when.timestamp()
    os.utime(path, (stamp, stamp))


def main():
    root = Path("demo_project")
    if root.exists():
        shutil.rmtree(root)
    (root / "logs").mkdir(parents=True)
    (root / "orders").mkdir()
    last_run = (datetime.now() - timedelta(hours=2, minutes=14)).date()
    write(root / "app.py", APP, at(last_run - timedelta(days=20), "10:00"))
    write(root / "README.md", README, at(last_run - timedelta(days=20), "10:00"))
    for i, text in enumerate(ORDERS):
        day = last_run - timedelta(days=3 - i)
        write(root / "orders" / f"orders_{day}.csv", text, at(day, "23:59"))
    for i in range(3):
        run_day = last_run - timedelta(days=2 - i)
        report_day = run_day - timedelta(days=1)
        stamp = f"{run_day} 02:14:0{i + 1}"
        lines = [f"{stamp} INFO Nightly report started for {report_day}"]
        if i < 2:
            if i == 0:
                lines.append(f"{stamp} WARNING Disk usage at 85%")
            lines += [f"{stamp} INFO Average order value for {report_day}: {AVERAGES[i]}",
                      f"{stamp} INFO Done"]
        else:
            lines += [f"{stamp} ERROR Report failed",
                      "Traceback (most recent call last):",
                      '  File "/srv/shop/app.py", line 20, in <module>',
                      '    print(f"Average order value for {day}: {average_order_value(day):.2f}")',
                      '  File "/srv/shop/app.py", line 14, in average_order_value',
                      "    return total / len(orders)",
                      "ZeroDivisionError: division by zero"]
        write(root / "logs" / f"app-{run_day}.log", "\n".join(lines) + "\n", at(run_day, "02:14") + timedelta(seconds=i + 1))
    print(f"demo_project/ created: the report crashed last night ({last_run} 02:14).")


main()
