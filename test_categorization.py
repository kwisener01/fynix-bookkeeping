import asyncio
import sys
import io

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, '.')

from agents.categorization_agent import CategorizationAgent
from agents.orchestrator import ClientProfile

async def test_categorization():
    """Test categorizing the Home Depot receipt items."""
    
    # Create agent
    agent = CategorizationAgent()
    
    # Create a test client profile (HVAC contractor)
    client = ClientProfile(
        client_id="test-hvac-001",
        business_name="Test HVAC Services",
        trade="HVAC",
        state="CA",
        chart_of_accounts={},
        tax_classification="S-Corp",
        payroll_frequency="bi-weekly"
    )
    
    # Test transactions from the Home Depot receipt
    transactions = [
        {
            "external_id": "txn_001",
            "vendor_payee": "THE HOME DEPOT",
            "description": "KWIKSET HALO SN KEYPAD DBLT",
            "amount": 99.99,
            "date": "2023-05-12"
        },
        {
            "external_id": "txn_002",
            "vendor_payee": "THE HOME DEPOT",
            "description": "GOOGLE NEST HUB CHARCOAL",
            "amount": 279.00,
            "date": "2023-05-12"
        },
        {
            "external_id": "txn_003",
            "vendor_payee": "THE HOME DEPOT",
            "description": "NEST THERMOSTAT",
            "amount": 224.00,
            "date": "2023-05-12"
        }
    ]
    
    print("\n" + "="*70)
    print("CATEGORIZATION TEST - Home Depot Receipt Items")
    print("="*70)
    print(f"Client: {client.business_name} ({client.trade})")
    print()
    
    for txn in transactions:
        result = await agent._categorize_transaction(txn, client)
        
        print(f"\n{'-'*70}")
        print(f"Item: {txn['description']}")
        print(f"Amount: ${txn['amount']:.2f}")
        print(f"\nCategory: {result.category}")
        if result.subcategory:
            print(f"Subcategory: {result.subcategory}")
        print(f"Confidence: {result.confidence*100:.0f}%")
        print(f"Auto-approved: {'✓' if result.auto_approved else '✗ (needs review)'}")
        print(f"Reasoning: {result.reasoning}")
        
        if result.tax_flags:
            print(f"Tax Flags: {', '.join(result.tax_flags)}")
        
        if result.alternative_categories:
            print("\nAlternative categories:")
            for alt_cat, conf in result.alternative_categories[:2]:
                print(f"  - {alt_cat} ({conf*100:.0f}%)")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    asyncio.run(test_categorization())
