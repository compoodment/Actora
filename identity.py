import random

MOTHER_FIRST_NAME_POOL = [
    "Aisha", "Anja", "Chiyo", "Elena", "Fatima", "Gabriela", "Hana", "Indira",
    "Jian", "Kailani", "Leila", "Mina", "Nia", "Renata", "Sofia", "Yara"
]

FATHER_FIRST_NAME_POOL = [
    "Arjun", "Bashir", "Carlos", "Daiki", "Ethan", "Felix", "Gao", "Haruki",
    "Javier", "Kwame", "Liam", "Musa", "Nikhil", "Omar", "Pablo", "Ravi"
]

FALLBACK_LAST_NAME_POOL = [
    "Abdullah", "Chen", "Díaz", "Eriksson", "Fernandez", "Gupta", "Hoffmann",
    "Ibrahim", "Kim", "Kovač", "Lee", "Müller", "Nakamura", "O'Sullivan",
    "Pereira", "Rossi", "Schmidt", "Silva", "Singh", "Smirnov", "Tan",
    "Wang", "Williams", "Zafar"
]

CULTURE_NAME_POOLS = {
    "American": {
        "mother_first_names": [
            "Abigail", "Addison", "Alyssa", "Ashley", "Ava", "Brianna", "Brooke", "Chloe",
            "Emily", "Emma", "Grace", "Hannah", "Harper", "Jessica", "Lauren", "Madison",
            "Megan", "Olivia", "Rachel", "Samantha",
        ],
        "father_first_names": [
            "Alexander", "Andrew", "Anthony", "Benjamin", "Brandon", "Christopher", "Daniel", "David",
            "Ethan", "Jacob", "James", "Joseph", "Joshua", "Logan", "Matthew", "Michael",
            "Nicholas", "Ryan", "Tyler", "William",
        ],
        "last_names": ["Anderson", "Brown", "Davis", "Garcia", "Harris", "Jackson", "Johnson", "Miller", "Smith", "Taylor"],
    },
    "Brazilian": {
        "mother_first_names": [
            "Adriana", "Aline", "Amanda", "Ana", "Beatriz", "Bianca", "Camila", "Carolina",
            "Daniela", "Fernanda", "Gabriela", "Isabela", "Juliana", "Larissa", "Leticia", "Mariana",
            "Patricia", "Rafaela", "Renata", "Sabrina",
        ],
        "father_first_names": [
            "Andre", "Bruno", "Caio", "Carlos", "Daniel", "Diego", "Eduardo", "Felipe",
            "Gabriel", "Gustavo", "Henrique", "Joao", "Leonardo", "Lucas", "Marcelo", "Mateus",
            "Pedro", "Rafael", "Rodrigo", "Tiago",
        ],
        "last_names": ["Alves", "Barbosa", "Cardoso", "Costa", "Ferreira", "Gomes", "Lima", "Oliveira", "Pereira", "Silva"],
    },
    "British": {
        "mother_first_names": [
            "Amelia", "Charlotte", "Chloe", "Eleanor", "Ella", "Emily", "Evie", "Freya",
            "Georgia", "Grace", "Holly", "Imogen", "Isla", "Jessica", "Lily", "Lucy",
            "Matilda", "Megan", "Poppy", "Sophie",
        ],
        "father_first_names": [
            "Alfie", "Arthur", "Charlie", "Daniel", "Edward", "Freddie", "George", "Harry",
            "Henry", "Jack", "Jacob", "James", "Joseph", "Leo", "Lewis", "Mohammed",
            "Oliver", "Oscar", "Thomas", "William",
        ],
        "last_names": ["Brown", "Clarke", "Davies", "Evans", "Hughes", "Johnson", "Jones", "Patel", "Smith", "Taylor"],
    },
    "Dutch": {
        "mother_first_names": [
            "Anna", "Anouk", "Anne", "Britt", "Eva", "Femke", "Fleur", "Isa",
            "Julia", "Lieke", "Linda", "Lisa", "Lotte", "Maud", "Nina", "Noa",
            "Roos", "Sanne", "Sara", "Sophie",
        ],
        "father_first_names": [
            "Bas", "Bram", "Cas", "Daan", "Finn", "Floris", "Jasper", "Jesse",
            "Joost", "Lars", "Levi", "Luuk", "Mats", "Milan", "Niels", "Ruben",
            "Sem", "Stijn", "Thijs", "Wouter",
        ],
        "last_names": ["Bakker", "De Boer", "De Jong", "De Vries", "Jansen", "Mulder", "Prins", "Smit", "Van Dijk", "Visser"],
    },
    "German": {
        "mother_first_names": [
            "Anna", "Charlotte", "Clara", "Elena", "Ella", "Emilia", "Emma", "Hannah",
            "Johanna", "Julia", "Lara", "Laura", "Lea", "Lena", "Lina", "Mia",
            "Paula", "Sarah", "Sofia", "Theresa",
        ],
        "father_first_names": [
            "Ben", "David", "Elias", "Emil", "Felix", "Finn", "Jan", "Jonas",
            "Julian", "Kai", "Leon", "Luca", "Luis", "Matteo", "Max", "Moritz",
            "Noah", "Paul", "Tim", "Tom",
        ],
        "last_names": ["Becker", "Fischer", "Hoffmann", "Klein", "Koch", "Meyer", "Muller", "Neumann", "Schmidt", "Schneider"],
    },
    "Kenyan": {
        "mother_first_names": [
            "Achieng", "Akinyi", "Akoth", "Atieno", "Caroline", "Faith", "Grace", "Joyce",
            "Linet", "Mary", "Mercy", "Monica", "Naomi", "Njeri", "Nyambura", "Purity",
            "Rose", "Stella", "Wanjiku", "Yvonne",
        ],
        "father_first_names": [
            "Brian", "Collins", "Daniel", "David", "Eric", "Evans", "George", "John",
            "Joseph", "Kevin", "Martin", "Michael", "Moses", "Patrick", "Peter", "Samuel",
            "Stephen", "Victor", "Vincent", "William",
        ],
        "last_names": ["Chebet", "Kamau", "Kariuki", "Kibet", "Kimani", "Mwangi", "Njeri", "Odhiambo", "Otieno", "Wanjala"],
    },
    "Colombian": {
        "mother_first_names": [
            "Alejandra", "Ana", "Andrea", "Camila", "Carolina", "Catalina", "Daniela", "Diana",
            "Gabriela", "Isabella", "Jimena", "Juliana", "Laura", "Luisa", "Manuela", "Maria",
            "Natalia", "Paola", "Sara", "Valentina",
        ],
        "father_first_names": [
            "Alejandro", "Andres", "Camilo", "Carlos", "Cristian", "Daniel", "David", "Diego",
            "Felipe", "Gabriel", "Javier", "Juan", "Kevin", "Luis", "Mateo", "Nicolas",
            "Santiago", "Sebastian", "Steven", "William",
        ],
        "last_names": ["Arias", "Cardenas", "Castro", "Gomez", "Gonzalez", "Lopez", "Martinez", "Perez", "Rodriguez", "Torres"],
    },
    "Japanese": {
        "mother_first_names": [
            "Aiko", "Akari", "Aya", "Emi", "Hana", "Haruka", "Hina", "Kaede",
            "Mai", "Mei", "Mika", "Misaki", "Miyu", "Nao", "Nanami", "Rina",
            "Sakura", "Yui", "Yuka", "Yuna",
        ],
        "father_first_names": [
            "Daichi", "Haruto", "Hayato", "Hiroto", "Itsuki", "Kaito", "Kenta", "Minato",
            "Ren", "Riku", "Rin", "Ryota", "Sota", "Takumi", "Yamato", "Yudai",
            "Yuki", "Yuma", "Yuto", "Yuya",
        ],
        "last_names": ["Ito", "Kobayashi", "Kato", "Nakamura", "Saito", "Sasaki", "Suzuki", "Takahashi", "Tanaka", "Yamamoto"],
    },
    "Indian": {
        "mother_first_names": [
            "Aditi", "Ananya", "Anika", "Anjali", "Deepa", "Divya", "Isha", "Kavya",
            "Meera", "Neha", "Nisha", "Pooja", "Priya", "Rani", "Riya", "Shreya",
            "Sonal", "Sunita", "Tanvi", "Vidya",
        ],
        "father_first_names": [
            "Aditya", "Aman", "Ankit", "Arjun", "Deepak", "Karan", "Manish", "Mohit",
            "Nikhil", "Pranav", "Rahul", "Raj", "Rohan", "Sanjay", "Saurabh", "Shubham",
            "Vikram", "Vijay", "Virat", "Yash",
        ],
        "last_names": ["Agarwal", "Gupta", "Iyer", "Joshi", "Kapoor", "Patel", "Reddy", "Shah", "Sharma", "Singh"],
    },
    "Indonesian": {
        "mother_first_names": [
            "Ayu", "Citra", "Dewi", "Dian", "Fitri", "Intan", "Lestari", "Maya",
            "Nadia", "Nanda", "Nur", "Putri", "Rani", "Ratna", "Rina", "Sari",
            "Shinta", "Tari", "Tiara", "Wulan",
        ],
        "father_first_names": [
            "Agus", "Andi", "Bima", "Dedi", "Eka", "Fajar", "Hendra", "Iqbal",
            "Rangga", "Rian", "Rizky", "Taufik", "Wahyu", "Yoga", "Yudi", "Yusuf",
            "Zaki", "Zulfan", "Bayu", "Arif",
        ],
        "last_names": ["Gunawan", "Hidayat", "Kusuma", "Lesmana", "Mahendra", "Nugroho", "Permana", "Pratama", "Saputra", "Wijaya"],
    },
    "Filipino": {
        "mother_first_names": [
            "Andrea", "Angela", "Bea", "Camille", "Carmela", "Cristina", "Erika", "Hannah",
            "Janelle", "Jasmine", "Joy", "Kathleen", "Kimberly", "Lara", "Mae", "Maria",
            "Nicole", "Patricia", "Shiela", "Trisha",
        ],
        "father_first_names": [
            "Adrian", "Alden", "Allen", "Carlo", "Christian", "Daniel", "Gabriel", "James",
            "Jerome", "Joshua", "Justin", "Kenneth", "Kevin", "Mark", "Miguel", "Paolo",
            "Rafael", "Ryan", "Vincent", "Xavier",
        ],
        "last_names": ["Aquino", "Bautista", "Cruz", "Dela Cruz", "Garcia", "Mendoza", "Reyes", "Rizal", "Santos", "Torres"],
    },
    "Australian": {
        "mother_first_names": [
            "Abigail", "Alice", "Amelia", "Brooke", "Charlotte", "Chloe", "Ella", "Emily",
            "Georgia", "Grace", "Holly", "Isabelle", "Jessica", "Lily", "Maddison", "Matilda",
            "Olivia", "Ruby", "Sienna", "Zoe",
        ],
        "father_first_names": [
            "Archie", "Bailey", "Benjamin", "Cooper", "Daniel", "Ethan", "Harry", "Henry",
            "Jack", "Jacob", "James", "Joshua", "Lachlan", "Liam", "Lucas", "Mason",
            "Noah", "Oliver", "Thomas", "William",
        ],
        "last_names": ["Anderson", "Brown", "Campbell", "Collins", "Davies", "Evans", "Kelly", "Martin", "Smith", "Wilson"],
    },
}


def resolve_family_last_name(player_last_name, culture_group=None):
    if player_last_name:
        return player_last_name

    culture_pool = CULTURE_NAME_POOLS.get(culture_group or "")
    if culture_pool:
        return random.choice(culture_pool["last_names"])

    return random.choice(FALLBACK_LAST_NAME_POOL)


def prepare_parent_identity_context(
    role,
    player_last_name=None,
    family_last_name=None,
    species="Human",
    world=None,
    place_id=None,
    culture_group=None,
    culture_key=None,
    era_key=None,
):
    """Builds the current structured identity-generation seam for startup parent generation.

    The returned context intentionally accepts future-facing fields, but the current
    implementation still resolves names through placeholder global pools.
    """
    resolved_family_last_name = family_last_name
    if resolved_family_last_name is None:
        resolved_family_last_name = resolve_family_last_name(
            player_last_name,
            culture_group=culture_group or culture_key,
        )

    return {
        "role": role,
        "species": species,
        "family_last_name": resolved_family_last_name,
        "player_last_name": player_last_name,
        "world": world,
        "place_id": place_id,
        "culture_group": culture_group or culture_key,
        "culture_key": culture_key,
        "era_key": era_key,
        "generation_mode": (
            "culture_name_pools"
            if (culture_group or culture_key) in CULTURE_NAME_POOLS
            else "placeholder_global_pools"
        ),
    }


def generate_parent_identity_from_context(identity_context):
    """Generates a parent identity from a structured context seam.

    Current behavior remains intentionally narrow and human-only: role selection and
    placeholder/global name pools are the only active generation inputs today.
    """
    role = identity_context.get("role")
    family_last_name = identity_context.get("family_last_name")
    culture_group = identity_context.get("culture_group") or identity_context.get("culture_key")

    if family_last_name is None:
        family_last_name = resolve_family_last_name(
            identity_context.get("player_last_name"),
            culture_group=culture_group,
        )

    culture_pool = CULTURE_NAME_POOLS.get(culture_group, {})
    mother_first_names = culture_pool.get("mother_first_names", MOTHER_FIRST_NAME_POOL)
    father_first_names = culture_pool.get("father_first_names", FATHER_FIRST_NAME_POOL)

    if role == "mother":
        return {
            "first_name": random.choice(mother_first_names),
            "last_name": family_last_name,
            "sex": "Female",
            "gender": "Female",
        }

    if role == "father":
        return {
            "first_name": random.choice(father_first_names),
            "last_name": family_last_name,
            "sex": "Male",
            "gender": "Male",
        }

    raise ValueError("role must be 'mother' or 'father'")


def generate_parent_identity(role, family_last_name, generation_context=None):
    context = prepare_parent_identity_context(
        role=role,
        family_last_name=family_last_name,
        player_last_name=(generation_context or {}).get("player_last_name") if generation_context else None,
        species=(generation_context or {}).get("species", "Human") if generation_context else "Human",
        world=(generation_context or {}).get("world") if generation_context else None,
        place_id=(generation_context or {}).get("place_id") if generation_context else None,
        culture_group=(
            (generation_context or {}).get("culture_group")
            if generation_context
            else None
        ),
        culture_key=(generation_context or {}).get("culture_key") if generation_context else None,
        era_key=(generation_context or {}).get("era_key") if generation_context else None,
    )
    return generate_parent_identity_from_context(context)
