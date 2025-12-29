import asyncio
import sys
import io

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')

from agents.job_matcher import JobMatcher, Job, ReceiptData
from datetime import datetime

async def test_job_matching():
    """Test job matching with Home Depot receipt."""
    
    matcher = JobMatcher()
    
    # Your Home Depot receipt
    receipt = ReceiptData(
        vendor="THE HOME DEPOT",
        date=datetime(2023, 5, 12),
        total=645.20,
        tax=42.21,
        line_items=[
            {"description": "HALO KP SN <A>", "quantity": 1, "unit_price": 224.00},
            {"description": "KWIKSET HALO SN KEYPAD DBLT", "quantity": 1, "unit_price": 99.99},
            {"description": "NEST HUB <A>", "quantity": 1, "unit_price": 99.99},
            {"description": "GOOGLE NEST HUB CHARCOAL", "quantity": 1, "unit_price": 279.00}
        ],
        payment_method="debit",
        receipt_number="0160 00051 07354"
    )
    
    # Sample active jobs for an HVAC contractor
    jobs = [
        Job(
            job_id="job_001",
            job_number="HVAC-2023-042",
            customer_name="Johnson Residence - Smart Home Install",
            address="4521 Maple Drive, Los Angeles, CA",
            trade_type="HVAC",
            start_date=datetime(2023, 5, 10),
            end_date=datetime(2023, 5, 15),
            status="active",
            scope_keywords=["smart thermostat", "nest", "home automation", "HVAC upgrade"],
            estimated_material_cost=800.00
        ),
        Job(
            job_id="job_002",
            job_number="HVAC-2023-039",
            customer_name="Martinez Property - AC Replacement",
            address="890 Oak Street, Pasadena, CA",
            trade_type="HVAC",
            start_date=datetime(2023, 5, 1),
            end_date=datetime(2023, 5, 8),
            status="completed",
            scope_keywords=["AC unit", "3-ton", "condenser", "installation"],
            estimated_material_cost=2500.00
        ),
        Job(
            job_id="job_003",
            job_number="HVAC-2023-045",
            customer_name="Chen Residence - Ductwork Repair",
            address="234 Pine Ave, Glendale, CA",
            trade_type="HVAC",
            start_date=datetime(2023, 5, 18),
            end_date=datetime(2023, 5, 22),
            status="quoted",
            scope_keywords=["ductwork", "insulation", "repairs"],
            estimated_material_cost=450.00
        ),
        Job(
            job_id="job_004",
            job_number="PLB-2023-012",
            customer_name="Davis Home - Water Heater Install",
            address="567 Elm Street, Burbank, CA",
            trade_type="Plumbing",
            start_date=datetime(2023, 5, 11),
            end_date=datetime(2023, 5, 13),
            status="active",
            scope_keywords=["water heater", "tankless", "gas line"],
            estimated_material_cost=1200.00
        )
    ]
    
    # Find matches
    print("\n" + "="*80)
    print("JOB MATCHING TEST - Home Depot Receipt")
    print("="*80)
    print(f"\nReceipt Details:")
    print(f"  Vendor: {receipt.vendor}")
    print(f"  Date: {receipt.date.strftime('%Y-%m-%d')}")
    print(f"  Total: ${receipt.total:.2f}")
    print(f"  Items: NEST products, smart locks")
    print(f"\nActive Jobs: {len(jobs)}")
    print(f"  - {jobs[0].job_number}: {jobs[0].customer_name} (HVAC)")
    print(f"  - {jobs[1].job_number}: {jobs[1].customer_name} (HVAC)")
    print(f"  - {jobs[2].job_number}: {jobs[2].customer_name} (HVAC)")
    print(f"  - {jobs[3].job_number}: {jobs[3].customer_name} (Plumbing)")
    
    matches = await matcher.match_receipt_to_job(receipt, jobs)
    
    print(f"\n{'─'*80}")
    print("MATCHING RESULTS")
    print(f"{'─'*80}\n")
    
    if matches:
        for i, match in enumerate(matches, 1):
            confidence_bar = "█" * int(match.confidence * 20)
            print(f"{i}. {match.job_name}")
            print(f"   Confidence: {match.confidence*100:.0f}% {confidence_bar}")
            print(f"   Reasons:")
            for reason in match.reasons:
                print(f"     • {reason}")
            print()
    else:
        print("No matches found (all jobs below 30% confidence threshold)")
    
    print("="*80)
    print("\nMATCHING FACTORS EXPLAINED:")
    print(f"{'─'*80}")
    print("• Date Proximity (25%): Receipt date vs job timeline")
    print("• Vendor-Trade Alignment (20%): Home Depot supplies multiple trades")
    print("• Amount Matching (30%): Purchase amount vs job budget")
    print("• GPS Location (15%): Distance from job site (if available)")
    print("• Material Keywords (10%): Receipt items match job scope")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_job_matching())
