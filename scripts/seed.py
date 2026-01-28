from app.core.repository import SQLiteRepository
import json


def seed():
    # Initialize your repository pointing to your db file
    repo = SQLiteRepository("sqlite.db")

    # Define some common reusable mappings
    mappings = {
        "Salesforce_Export": {
            "username": "Full_Name",
            "email": "Primary_Email",
            "phone": "Mobile_Phone",
        },
        "Legacy_System_v2": {
            "username": "user_identifier",
            "email": "email_address",
            "phone": "tel_no",
        },
        "Dummy": {
            "username": "userName",
            "email": "eMail",
            "phone": "phone_id",
        },
    }

    for name, mapping_dict in mappings.items():
        print(f"Inserting mapping: {name}...")
        repo.save_mapping(name, mapping_dict)

    print("Done! Your UI dropdown should now be populated.")


if __name__ == "__main__":
    seed()
