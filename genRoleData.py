import pandas as pd
import random

# Data lists (filled in with examples)
first_names = ["John", "Emily", "Michael", "Olivia", "William", "Sophia", "James", "Ava", "Benjamin", "Isabella"]
last_names = ["Smith", "Johnson", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez"]
departments = ["IT", "Finance", "Marketing", "HR", "Sales", "Operations", "Engineering", "Legal", "Customer Service"]
job_titles = ["Manager", "Analyst", "Engineer", "Director", "Coordinator", "Specialist", "Consultant", "Associate"]
counties = ["Essex", "Middlesex", "Union", "Bergen", "Hudson", "Monmouth", "Ocean", "Morris", "Passaic", "Somerset"]
applications = [f"App{i+1}" for i in range(50)]  # Creates App1, App2, ..., App50
roles = ["Admin", "User", "Read-Only", "Power User", "Guest"]


# Create empty DataFrame
data = {
    "First Name": [],
    "Last Name": [],
    "Username": [],
    "Department": [],
    "Job Title": [],
    "County": [],
    "Application Name": [],
    "Account Name": [],  # We'll combine first and last names for this
    "Role or Permission": [],
}

# Generate data
for _ in range(100000):  # 100,000 records
    data["First Name"].append(random.choice(first_names))
    data["Last Name"].append(random.choice(last_names))
    username = f"{data['First Name'][-1][0].lower()}{data['Last Name'][-1].lower()}{random.randint(100, 999)}"  # e.g., jsmith123
    data["Username"].append(username)
    data["Department"].append(random.choice(departments))
    data["Job Title"].append(random.choice(job_titles))
    data["County"].append(random.choice(counties))
    data["Application Name"].append(random.choice(applications))
    data["Account Name"].append(f"{data['First Name'][-1]} {data['Last Name'][-1]}")
    data["Role or Permission"].append(random.choice(roles))

# Create DataFrame
df = pd.DataFrame(data)

# Export to CSV
df.to_csv("data/role_mining_data.csv", index=False)  # index=False to remove row numbers

