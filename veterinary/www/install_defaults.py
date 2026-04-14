import frappe


def insert_pet_colours():
    # List of pet colours
    pet_colours = [
        "Black", "White", "Brown", "Golden", "Cream", "Grey", "Spotted",
        "Brindle", "Tan", "Fawn", "Red", "Blue", "Chocolate", "Sable",
        "Merle", "Cinnamon", "Silver", "Apricot", "Buff", "Tri-colour"
    ]

    for colour in pet_colours:
        # Check if it already exists
        if not frappe.db.exists("Pet Colour", colour):
            doc = frappe.get_doc({
                "doctype": "Pet Colour",
                "pet_colour": colour
            })
            doc.insert(ignore_permissions=True)
            print(f"Inserted: {colour}")
        else:
            print(f"Already exists: {colour}")

def insert_pet_breeds():
    pet_breeds = [
        # Dogs
        "Labrador Retriever", "Golden Retriever", "Beagle", "German Shepherd", "Bulldog",
        "Poodle", "Rottweiler", "Corgi", "Dachshund", "Shih Tzu",
        # Cats
        "Persian", "Siamese", "Maine Coon", "Bengal", "Ragdoll",
        "Sphynx", "British Shorthair", "Scottish Fold", "Abyssinian", "Oriental Shorthair",
        # Birds
        "Parakeet", "Cockatiel", "Canary", "African Grey", "Lovebird",
        "Budgerigar", "Macaw", "Finch", "Pionus", "Conure",
        # Fish
        "Goldfish", "Betta", "Guppy", "Angelfish", "Molly",
        "Platy", "Neon Tetra", "Cichlid", "Koi", "Swordtail",
        # Rodents / small mammals
        "Hamster", "Syrian Hamster", "Guinea Pig", "Rabbit", "Chinchilla",
        "Rat", "Mouse", "Gerbil", "Ferret", "Degus",
        # Reptiles / amphibians
        "Leopard Gecko", "Bearded Dragon", "Corn Snake", "Ball Python", "Frog",
        "Chameleon", "Turtle", "Iguana", "Salamander", "Gecko"
    ]

    for breed in pet_breeds:
        if not frappe.db.exists("Pet Breed", {"pet_breed": breed}):
            doc = frappe.get_doc({
                "doctype": "Pet Breed",
                "pet_breed": breed
            })
            doc.insert(ignore_permissions=True)
            print(f"Inserted: {breed}")
        else:
            print(f"Already exists: {breed}")

def insert_pet_species():
    species_list = [
        "Dog",
        "Cat",
        "Bird",
        "Fish",
        "Rabbit",
        "Rodent",
        "Reptile",
        "Amphibian",
        "Ferret",
        "Guinea Pig",
        "Hamster",
        "Chinchilla",
        "Turtle",
        "Snake",
        "Lizard",
        "Parrot",
        "Canary",
        "Budgerigar",
        "Horse",
        "Goat",
        "Pig",
        "Sheep",
        "Mouse",
        "Rat",
        "Frog",
        "Salamander"
    ]

    for species in species_list:
        if not frappe.db.exists("Species", {"species": species}):
            doc = frappe.get_doc({
                "doctype": "Species",
                "species": species
            })
            doc.insert(ignore_permissions=True)
            print(f"Inserted: {species}")
        else:
            print(f"Already exists: {species}")

def insert_pet_sex():
    sex_list = [
        "Male",
        "Female",
        "Unknown",
        "Hermaphrodite",
        "Neutered Male",
        "Spayed Female"
    ]

    for sex in sex_list:
        # Check if already exists
        if not frappe.db.exists("Pet Sex", {"sex": sex}):
            doc = frappe.get_doc({
                "doctype": "Pet Sex",
                "sex": sex
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"Inserted: {sex}")
        else:
            print(f"Already exists: {sex}")


def install_all():
    insert_pet_colours()
    insert_pet_breeds()
    insert_pet_species()
    insert_pet_sex()