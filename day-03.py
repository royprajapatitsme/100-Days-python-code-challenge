import csv
import os
from datetime import datetime
from collections import defaultdict, namedtuple

Transaction = namedtuple("Transaction", ["date", "amount", "category", "note"])

class ExpenseTracker:
    def __init__(self, filename="expenses.csv"):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["date", "amount", "category", "note"])

    def add(self, amount, category, note=""):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.filename, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([now, f"{float(amount):.2f}", category.strip(), note.strip()])

    def _read_all(self):
        with open(self.filename, newline="") as f:
            reader = csv.DictReader(f)
            data = []
            for row in reader:
                try:
                    amt = float(row["amount"])
                except:
                    continue
                data.append(Transaction(date=row["date"], amount=amt, category=row["category"], note=row["note"]))
            return data

    def summary(self, days=None):
        data = self._read_all()
        if days is not None:
            cutoff = datetime.now().timestamp() - days * 24 * 3600
            data = [t for t in data if datetime.strptime(t.date, "%Y-%m-%d %H:%M:%S").timestamp() >= cutoff]
        total = sum(t.amount for t in data)
        by_cat = defaultdict(float)
        for t in data:
            by_cat[t.category] += t.amount
        top = sorted(by_cat.items(), key=lambda x: x[1], reverse=True)
        return {"total": total, "by_category": dict(by_cat), "top_categories": top[:5], "transactions": data}

    def list_transactions(self, limit=20):
        data = self._read_all()
        return sorted(data, key=lambda t: t.date, reverse=True)[:limit]

def human_menu():
    et = ExpenseTracker()
    menu = """\nSmart Expense Tracker
1. Add expense
2. Show last transactions
3. Show summary (all time)
4. Show summary (last N days)
5. Exit
Choose an option: """
    while True:
        choice = input(menu).strip()
        if choice == "1":
            amt = input("Amount: ").strip()
            cat = input("Category (e.g., Food, Travel): ").strip()
            note = input("Short note (optional): ").strip()
            try:
                et.add(float(amt), cat, note)
                print("Saved ✅")
            except Exception as e:
                print("Could not save. Make sure amount is a number.")
        elif choice == "2":
            tx = et.list_transactions()
            if not tx:
                print("No transactions yet.")
            else:
                for t in tx:
                    print(f"{t.date} | {t.category:12} | ₹{t.amount:8.2f} | {t.note}")
        elif choice == "3":
            s = et.summary()
            print(f"Total spent: ₹{s['total']:.2f}")
            print("Top categories:")
            for cat, amt in s["top_categories"]:
                print(f"  {cat:12} : ₹{amt:.2f}")
        elif choice == "4":
            n = input("How many days? ").strip()
            try:
                n = int(n)
                s = et.summary(days=n)
                print(f"Total spent in last {n} days: ₹{s['total']:.2f}")
                for cat, amt in s["top_categories"]:
                    print(f"  {cat:12} : ₹{amt:.2f}")
            except:
                print("Please enter a whole number.")
        elif choice == "5":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    human_menu()
