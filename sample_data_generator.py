"""Generate sample provider data using Faker."""
from typing import List
from faker import Faker
from random import choice, randint
from models import Provider, Location, Specialty, Credential, Affiliation
from datetime import datetime, timedelta

fake = Faker()

SPECIALTIES = [
    ("207R00000X", "Internal Medicine"),
    ("207Q00000X", "Family Medicine"),
    ("208D00000X", "General Practice"),
]

CREDENTIAL_TYPES = ["MD", "DO", "NP", "PA"]


def random_phone():
    return f"+1{randint(2000000000, 9999999999)}"


def generate_provider(npi: str | None = None) -> Provider:
    first = fake.first_name()
    last = fake.last_name()
    return Provider(
        npi=npi or str(randint(1000000000, 9999999999)),
        first_name=first,
        last_name=last,
        email=f"{first}.{last}@example.com".lower(),
        phone=random_phone(),
        gender=choice(["M", "F", "U"]),
        source_system="faker",
    )


def generate_location(i: int) -> Location:
    return Location(
        location_id=f"LOC-{i}-{randint(1000,9999)}",
        address=fake.street_address(),
        city=fake.city(),
        state=fake.state_abbr(),
        zip_code=fake.postcode()[:5],
        country="USA",
        location_type=choice(["practice", "hospital", "clinic"]),
    )


def generate_specialty() -> Specialty:
    code, name = choice(SPECIALTIES)
    return Specialty(
        specialty_code=code,
        specialty_name=name,
        specialty_type=choice(["primary", "secondary"]),
        board_certified=choice([True, False]),
    )


def generate_credential(i: int) -> Credential:
    issue = datetime.now() - timedelta(days=randint(365, 3650))
    exp = issue + timedelta(days=randint(365, 3650))
    return Credential(
        credential_id=f"CRD-{i}-{randint(1000,9999)}",
        license_number=f"LIC{randint(10000, 999999)}",
        license_type=choice(CREDENTIAL_TYPES),
        license_state=fake.state_abbr(),
        issue_date=issue,
        expiration_date=exp,
        status=choice(["active", "expired", "suspended"]),
    )


def generate_affiliation(i: int) -> Affiliation:
    start = datetime.now() - timedelta(days=randint(100, 2000))
    return Affiliation(
        affiliation_id=f"AFF-{i}-{randint(1000,9999)}",
        organization_name=fake.company(),
        organization_type=choice(["hospital", "medical_group", "insurance"]),
        relationship_type=choice(["employed", "affiliated", "contracted"]),
        start_date=start,
        is_active=True,
    )


def generate_dataset(n: int = 10) -> List[Provider]:
    providers: List[Provider] = []
    for i in range(n):
        p = generate_provider()
        providers.append(p)
    return providers
