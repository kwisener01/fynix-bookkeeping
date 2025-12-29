"""
Fynix Systems - Job Matching Agent
===================================
Intelligently matches receipts and expenses to active jobs.

Blue Ocean Insight: Traditional contractors manually allocate expenses to jobs.
This agent does it automatically using AI pattern recognition.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import re


@dataclass
class Job:
    """Active contractor job."""
    job_id: str
    job_number: str
    customer_name: str
    address: Optional[str]
    trade_type: str  # HVAC, Plumbing, Roofing, Electrical
    start_date: datetime
    end_date: Optional[datetime]
    status: str  # quoted, active, completed, billed
    scope_keywords: List[str]  # Materials/work expected
    estimated_material_cost: float
    gps_location: Optional[Tuple[float, float]] = None


@dataclass
class ReceiptData:
    """Extracted receipt information."""
    vendor: str
    date: datetime
    total: float
    tax: float
    line_items: List[dict]
    payment_method: Optional[str] = None
    gps_location: Optional[Tuple[float, float]] = None
    receipt_number: Optional[str] = None


@dataclass
class JobMatch:
    """A potential job match with confidence score."""
    job_id: str
    job_number: str
    job_name: str
    confidence: float
    reasons: List[str]


class JobMatcher:
    """
    AI-powered job matching engine.

    Matches receipts to jobs using:
    - Date proximity
    - Vendor patterns
    - Amount matching
    - Location data
    - Material keywords
    - Historical patterns
    """

    def __init__(self):
        self.vendor_trade_mapping = self._load_vendor_patterns()
        self.historical_patterns = {}

    async def match_receipt_to_job(
        self,
        receipt: ReceiptData,
        active_jobs: List[Job],
        manual_job_code: Optional[str] = None
    ) -> List[JobMatch]:
        """
        Returns ranked list of potential job matches.

        Args:
            receipt: Extracted receipt data
            active_jobs: List of jobs to match against
            manual_job_code: If provided, returns 100% confidence for this job

        Returns:
            List of JobMatch objects sorted by confidence (highest first)
        """

        # If manual job code provided, validate and return immediately
        if manual_job_code:
            for job in active_jobs:
                if job.job_number == manual_job_code or job.job_id == manual_job_code:
                    return [JobMatch(
                        job_id=job.job_id,
                        job_number=job.job_number,
                        job_name=job.customer_name,
                        confidence=1.0,
                        reasons=["Manually specified by user"]
                    )]

        matches = []

        for job in active_jobs:
            score, reasons = self._calculate_match_score(receipt, job)

            # Only suggest jobs with meaningful confidence
            if score > 0.3:
                matches.append(JobMatch(
                    job_id=job.job_id,
                    job_number=job.job_number,
                    job_name=f"{job.customer_name} - {job.job_number}",
                    confidence=round(score, 2),
                    reasons=reasons
                ))

        # Sort by confidence (highest first)
        return sorted(matches, key=lambda x: x.confidence, reverse=True)

    def _calculate_match_score(
        self,
        receipt: ReceiptData,
        job: Job
    ) -> Tuple[float, List[str]]:
        """
        Calculate match confidence score between receipt and job.

        Returns:
            (score, reasons) tuple where score is 0.0-1.0
        """
        score = 0.0
        reasons = []

        # 1. Date Proximity (25% weight)
        if self._is_date_in_job_window(receipt.date, job):
            score += 0.25
            reasons.append(f"Date falls within job timeline")
        elif self._is_date_near_job(receipt.date, job):
            score += 0.15
            reasons.append(f"Date close to job dates")

        # 2. Vendor-Trade Alignment (20% weight)
        if self._vendor_supplies_trade(receipt.vendor, job.trade_type):
            score += 0.20
            reasons.append(f"{receipt.vendor} typically supplies {job.trade_type} materials")

        # 3. Amount Matching (30% weight)
        amount_match = self._check_amount_fit(receipt.total, job)
        if amount_match:
            score += 0.30
            reasons.append(amount_match)

        # 4. GPS Location Proximity (15% weight)
        if receipt.gps_location and job.gps_location:
            distance_km = self._haversine_distance(receipt.gps_location, job.gps_location)
            if distance_km < 0.5:  # Within 500 meters
                score += 0.15
                reasons.append(f"Captured {int(distance_km * 1000)}m from job site")
            elif distance_km < 5:  # Within 5km
                score += 0.08
                reasons.append(f"Captured {distance_km:.1f}km from job site")

        # 5. Material Keywords Match (10% weight)
        keyword_matches = self._match_keywords(receipt.line_items, job.scope_keywords)
        if keyword_matches:
            score += 0.10
            reasons.append(f"Materials match job scope: {', '.join(keyword_matches)}")

        return score, reasons

    def _is_date_in_job_window(self, receipt_date: datetime, job: Job) -> bool:
        """Check if receipt date falls within job timeline."""
        if job.end_date:
            return job.start_date <= receipt_date <= job.end_date
        else:
            # For ongoing jobs, check if after start and within 90 days
            return job.start_date <= receipt_date <= job.start_date + timedelta(days=90)

    def _is_date_near_job(self, receipt_date: datetime, job: Job) -> bool:
        """Check if receipt date is close to job dates (within 7 days)."""
        # Could be materials purchased before job starts
        start_buffer = job.start_date - timedelta(days=7)
        end_buffer = (job.end_date or datetime.now()) + timedelta(days=7)
        return start_buffer <= receipt_date <= end_buffer

    def _vendor_supplies_trade(self, vendor: str, trade: str) -> bool:
        """Check if vendor typically supplies materials for this trade."""
        vendor_upper = vendor.upper()

        # Check against known patterns
        trade_vendors = self.vendor_trade_mapping.get(trade, [])

        for pattern in trade_vendors:
            if pattern in vendor_upper:
                return True

        return False

    def _check_amount_fit(self, amount: float, job: Job) -> Optional[str]:
        """
        Check if receipt amount makes sense for this job.
        Returns reason string if match, None otherwise.
        """
        abs_amount = abs(amount)

        # Small purchases ($0-$100) could be any active job
        if abs_amount < 100:
            return "Small purchase amount - likely incidental materials"

        # Medium purchases ($100-$1000)
        elif abs_amount < 1000:
            # Check if within expected material budget
            if job.estimated_material_cost > 0:
                if abs_amount < job.estimated_material_cost * 0.5:
                    return f"Amount reasonable for job budget (${job.estimated_material_cost:,.0f})"
            else:
                return "Medium purchase - typical for active job"

        # Large purchases ($1000+) - likely equipment
        else:
            if job.estimated_material_cost > 0:
                if abs_amount < job.estimated_material_cost * 1.2:
                    return f"Large purchase consistent with job budget"
            return "Major equipment/materials purchase"

        return None

    def _match_keywords(
        self,
        line_items: List[dict],
        job_keywords: List[str]
    ) -> List[str]:
        """
        Find matching keywords between receipt items and job scope.

        Returns:
            List of matched keywords
        """
        matches = []

        # Combine all line item descriptions
        receipt_text = ' '.join([
            item.get('description', '').upper()
            for item in line_items
        ])

        for keyword in job_keywords:
            if keyword.upper() in receipt_text:
                matches.append(keyword)

        return matches

    def _haversine_distance(
        self,
        loc1: Tuple[float, float],
        loc2: Tuple[float, float]
    ) -> float:
        """
        Calculate distance between two GPS coordinates in kilometers.

        Args:
            loc1: (latitude, longitude) tuple
            loc2: (latitude, longitude) tuple

        Returns:
            Distance in kilometers
        """
        from math import radians, sin, cos, sqrt, atan2

        lat1, lon1 = map(radians, loc1)
        lat2, lon2 = map(radians, loc2)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        # Earth's radius in kilometers
        R = 6371

        return R * c

    def _load_vendor_patterns(self) -> dict:
        """
        Load vendor-to-trade mappings.

        In production, this would be ML-trained and continuously updated.
        """
        return {
            "HVAC": [
                "JOHNSTONE", "CARRIER", "TRANE", "LENNOX", "FERGUSON HVAC",
                "REFRIGERANT", "HVAC", "AIR CONDITIONING", "HEATING"
            ],
            "Plumbing": [
                "FERGUSON PLUMB", "HD SUPPLY PLUMB", "PLUMBING", "PIPE",
                "KOHLER", "MOEN", "DELTA FAUCET", "WATER HEATER"
            ],
            "Roofing": [
                "ABC ROOFING", "BEACON BUILDING", "ROOFING SUPPLY",
                "SHINGLE", "GAF", "CERTAINTEED", "OWENS CORNING"
            ],
            "Electrical": [
                "GRAYBAR", "REXEL", "ELECTRICAL SUPPLY", "WIRE", "CONDUIT",
                "SCHNEIDER ELECTRIC", "LEVITON", "LUTRON"
            ],
            "General": [
                "HOME DEPOT", "LOWES", "HARBOR FREIGHT", "ACE HARDWARE",
                "FASTENAL", "GRAINGER"
            ]
        }

    def learn_from_assignment(
        self,
        receipt: ReceiptData,
        job: Job,
        was_correct: bool
    ):
        """
        Learn from user corrections to improve future matching.

        This builds historical patterns:
        - Vendor X → usually Job Type Y
        - Amount range → job size correlation
        - Day of week patterns
        """
        pattern_key = f"{receipt.vendor}_{job.trade_type}"

        if pattern_key not in self.historical_patterns:
            self.historical_patterns[pattern_key] = {
                'count': 0,
                'correct': 0
            }

        self.historical_patterns[pattern_key]['count'] += 1
        if was_correct:
            self.historical_patterns[pattern_key]['correct'] += 1

        # In production: Store in database for ML training


# Example usage
if __name__ == "__main__":
    import asyncio

    async def demo():
        matcher = JobMatcher()

        # Sample receipt
        receipt = ReceiptData(
            vendor="Johnstone Supply",
            date=datetime(2025, 12, 27),
            total=-245.67,
            tax=-19.65,
            line_items=[
                {"description": "R-410A Refrigerant", "quantity": 1, "price": 225.00},
                {"description": "Filter", "quantity": 2, "price": 10.34}
            ]
        )

        # Sample active jobs
        jobs = [
            Job(
                job_id="job_001",
                job_number="JOB2024-001",
                customer_name="Smith Residence",
                address="123 Main St",
                trade_type="HVAC",
                start_date=datetime(2025, 12, 26),
                end_date=datetime(2025, 12, 28),
                status="active",
                scope_keywords=["refrigerant", "AC unit", "3-ton"],
                estimated_material_cost=500.00
            ),
            Job(
                job_id="job_002",
                job_number="JOB2024-002",
                customer_name="Johnson Property",
                address="456 Oak Ave",
                trade_type="Plumbing",
                start_date=datetime(2025, 12, 25),
                end_date=datetime(2025, 12, 30),
                status="active",
                scope_keywords=["water heater", "pipes"],
                estimated_material_cost=800.00
            )
        ]

        # Find matches
        matches = await matcher.match_receipt_to_job(receipt, jobs)

        print("Job Matching Results:")
        print("=" * 60)
        for match in matches:
            print(f"\n{match.job_name}")
            print(f"Confidence: {match.confidence * 100:.0f}%")
            print(f"Reasons:")
            for reason in match.reasons:
                print(f"  - {reason}")

    asyncio.run(demo())
