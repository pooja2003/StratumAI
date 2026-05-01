from dotenv import load_dotenv
from email_sender import send_intelligence_report
import schedule
import time
import os

load_dotenv(override=True)

# ─────────────────────────────────────────
# CONFIGURE YOUR WATCHLIST HERE
# Add or remove companies anytime
# ─────────────────────────────────────────
WATCHLIST = [
    "Zepto",
    "Razorpay",
    "Flipkart",
    "CRED",
    "Salesforce"
]

# ─────────────────────────────────────────
# RECIPIENT EMAIL
# ─────────────────────────────────────────
RECIPIENT = os.getenv("GMAIL_ADDRESS")  # sends to yourself by default
# To send to someone else:
# RECIPIENT = "someone@gmail.com"


# ─────────────────────────────────────────
# JOB — runs for every company in watchlist
# ─────────────────────────────────────────
def run_weekly_reports():
    print("\n" + "="*60)
    print(f"📅 WEEKLY STRATUMAI RUN — {time.strftime('%B %d, %Y %H:%M')}")
    print("="*60)
    print(f"Companies to analyze: {', '.join(WATCHLIST)}")
    print(f"Sending reports to:   {RECIPIENT}")
    print("="*60 + "\n")

    success_count = 0
    fail_count    = 0

    for company in WATCHLIST:
        try:
            print(f"\n[{WATCHLIST.index(company)+1}/{len(WATCHLIST)}] Processing: {company}")
            send_intelligence_report(company, RECIPIENT)
            success_count += 1

            # Wait 10 seconds between companies
            # so we don't hit API rate limits
            if company != WATCHLIST[-1]:
                print(f"  ⏳ Waiting 10s before next company...")
                time.sleep(10)

        except Exception as e:
            print(f"  ❌ Failed for {company}: {str(e)}")
            fail_count += 1
            continue

    print("\n" + "="*60)
    print(f"✅ Run complete — {success_count} sent, {fail_count} failed")
    print(f"⏰ Next run: {schedule.next_run()}")
    print("="*60 + "\n")


# ─────────────────────────────────────────
# SCHEDULE
# ─────────────────────────────────────────
def start_scheduler():
    print("\n🧠 StratumAI Scheduler Started")
    print(f"📋 Watchlist: {', '.join(WATCHLIST)}")
    print(f"📧 Recipient: {RECIPIENT}")
    print(f"⏰ Schedule:  Every Monday at 09:00 AM")
    print("\nPress Ctrl+C to stop.\n")

    # Run every Monday at 9am
    schedule.every().monday.at("09:00").do(run_weekly_reports)

    # Shows when the next run is
    print(f"⏳ Next scheduled run: {schedule.next_run()}\n")

    # Keep the script alive, checking every minute
    while True:
        schedule.run_pending()
        time.sleep(60)


# ─────────────────────────────────────────
# RUN OPTIONS
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("\n🧠 StratumAI Scheduler")
    print("─" * 40)
    print("1. Start weekly scheduler (runs every Monday 9am)")
    print("2. Run reports RIGHT NOW (test mode)")
    print("─" * 40)

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        start_scheduler()
    elif choice == "2":
        print("\n🚀 Running all reports now in test mode...\n")
        run_weekly_reports()
    else:
        print("Invalid choice. Please enter 1 or 2.")