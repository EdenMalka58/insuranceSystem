import random
import json
from datetime import datetime, timedelta
from uuid import uuid4

ALLOWED_AREAS = [
    "front","frontLeft","frontRight",
    "rear","rearRight","rearLeft",
    "rightSide","rightFrontSide","rightRearSide",
    "leftSide","leftFrontSide","leftRearSide"
]

ALLOWED_SEVERITIES = ["slight", "medium", "extensive"]

PRICE_TABLE = {
    "front":            {"slight": 700,  "medium": 2200, "extensive": 5200},
    "frontLeft":        {"slight": 600,  "medium": 2000, "extensive": 4800},
    "frontRight":       {"slight": 600,  "medium": 2000, "extensive": 4800},
    "rear":             {"slight": 800,  "medium": 2500, "extensive": 6000},
    "rearLeft":         {"slight": 700,  "medium": 2300, "extensive": 5600},
    "rearRight":        {"slight": 700,  "medium": 2300, "extensive": 5600},
    "rightSide":        {"slight": 900,  "medium": 2800, "extensive": 6500},
    "rightFrontSide":   {"slight": 850,  "medium": 2600, "extensive": 6200},
    "rightRearSide":    {"slight": 850,  "medium": 2600, "extensive": 6200},
    "leftSide":         {"slight": 900,  "medium": 2800, "extensive": 6500},
    "leftFrontSide":    {"slight": 850,  "medium": 2600, "extensive": 6200},
    "leftRearSide":     {"slight": 850,  "medium": 2600, "extensive": 6200}
}

NAMES = [
    "Eden Malka",
    "Daniel Cohen",
    "Noa Levi",
    "Amit Peretz",
    "Yael Katz",
    "Itay Mizrahi",
    "Shir Ben David",
    "Omer Rosenberg",
    "Tal Friedman",
    "Lior Shavit",
    "Nitzan Bar",
    "Rotem Azulay",
    "Yarden Biton",
    "Guy Ohayon",
    "Maya Nachum",
    "Yonatan Azulay",
    "Roni Sharabi",
    "Alon Dahan",
    "Hila Shapira",
    "Erez Vaknin",
    "Keren Levi",
    "Moshe Abutbul",
    "Dana Yitzhaki",
    "Nadav Goldstein",
    "Sapir Amram",
    "Eli Ben Ami",
    "Tamar Dayan",
    "Shlomi Chaim",
    "Adi Barak",
    "Yuval Kravitz"
]

MODELS = [
    "Mazda 3",
    "Toyota Corolla",
    "Hyundai i30",
    "Kia Picanto",
    "Skoda Octavia",
    "Hyundai Elantra",
    "Toyota Yaris",
    "Kia Sportage",
    "Nissan Qashqai",
    "Mitsubishi ASX",
    "Honda Civic",
    "Suzuki Swift",
    "Chevrolet Spark",
    "Ford Focus",
    "Seat Ibiza",
    "Seat Leon",
    "Volkswagen Golf",
    "Volkswagen Polo",
    "Peugeot 208",
    "Peugeot 3008",
    "Renault Clio",
    "Renault Captur",
    "Subaru XV",
    "Subaru Impreza",
    "Skoda Fabia",
    "Hyundai Tucson",
    "Toyota RAV4",
    "Kia Niro",
    "Mazda CX-5",
    "BMW 1 Series"
]

STATUSES = ["opened", "approved", "rejected"]
ACTIONS = ["initially", "waiting", "automatically", "manually"]

def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

def generate_damage_areas():
    areas = random.sample(ALLOWED_AREAS, random.randint(1, 12))
    result = []
    total = 0

    for area in areas:
        severity = random.choice(ALLOWED_SEVERITIES)
        cost = PRICE_TABLE[area][severity]
        total += cost
        result.append({
            "area": area,
            "severity": severity,
            "estimatedCost": cost
        })

    return result, total

def generate_claim(created_at):
    damage_areas, assessment = generate_damage_areas()
    status = random.choice(STATUSES)

    approved_value = assessment if status == "approved" else 0

    return {
        "claimNumber": f"CLM-{created_at.year}-{random.randint(100,999)}",
        "claimDate": random_date(created_at, datetime.utcnow()).date().isoformat(),
        "description": random.choice([
            "Front collision",
            "Parking damage",
            "Side impact",
            "Rear accident",
            "Minor scratch"
        ]),
        "status": status,
        "approvedAction": random.choice(ACTIONS),
        "assessmentValue": assessment,
        "approvedValue": approved_value,
        "damageAreas": damage_areas,
        "createdAt": created_at.isoformat(),
        "updatedAt": datetime.utcnow().isoformat()
    }

def generate_policy(i):
    created_at = random_date(
        datetime(2025, 1, 1),
        datetime.utcnow()
    )

    claims = [generate_claim(created_at) for _ in range(random.randint(0, 3))]

    return {
        "policyNumber": f"POL-{created_at.year}-{str(i).zfill(3)}",
        "insured": {
            "email": f"user{i}@mail.com",
            "idNumber": str(random.randint(20000000, 39999999)),
            "name": random.choice(NAMES),
            "phone": f"05{random.randint(0,9)}-{random.randint(1000000,9999999)}"
        },
        "vehicle": {
            "model": random.choice(MODELS),
            "plateNumber": f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(100,999)}",
            "year": random.randint(2019, 2025)
        },
        "validity": {
            "start": "2026-01-01",
            "end": "2026-12-31"
        },
        "insuredValue": random.randint(60000, 200000),
        "deductibleValue": random.randint(1000, 5000),
        "createdAt": created_at.isoformat(),
        "claims": claims
    }

policies = [generate_policy(i) for i in range(1, 101)]

print(json.dumps(policies, indent=2))
