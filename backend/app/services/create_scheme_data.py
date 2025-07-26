import json
import csv

# --- Predefined Data for Various Schemes ---
schemes_data = [
    {
        "name": "LIFE Mission",
        "summary": "Provides free housing for homeless families in Kerala.",
        "eligibility": "Landless and homeless families, families with unsafe housing.",
        "official_link": "lifemission.kerala.gov.in"
    },
    {
        "name": "Karunya Arogya Suraksha Padhathi (KASP)",
        "summary": "Offers health coverage worth INR 5 lakhs per family per year.",
        "eligibility": "Over 42 lakh families identified as underprivileged.",
        "official_link": "sha.kerala.gov.in/karunya-arogya-suraksha-padhathi"
    },
    {
        "name": "K-FON (Kerala Fiber Optic Network)",
        "summary": "Aims to provide free or subsidized high-speed internet access to all citizens and government offices.",
        "eligibility": "All citizens, with a focus on providing free access to Below Poverty Line (BPL) families.",
        "official_link": "kfon.in"
    },
    {
        "name": "Vayomadhuram Scheme",
        "summary": "Provides free glucometers to senior citizens from BPL families who are diabetic.",
        "eligibility": "Diabetic senior citizens (aged 60+) from Below Poverty Line (BPL) families.",
        "official_link": "sjd.kerala.gov.in"
    }
]

# --- Main Program ---
if __name__ == "__main__":
    
    # --- Save data to a JSON file ---
    json_filepath = "schemes.json"
    with open(json_filepath, 'w', encoding='utf-8') as f:
        json.dump(schemes_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Data for {len(schemes_data)} schemes saved to {json_filepath}")

    # --- Save data to a CSV file ---
    csv_filepath = "schemes.csv"
    headers = ['name', 'summary', 'eligibility', 'official_link']
    with open(csv_filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(schemes_data)
    print(f"✅ Data for {len(schemes_data)} schemes saved to {csv_filepath}")