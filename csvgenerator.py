import csv
import random
import uuid

# Define the header and example departments, job titles, and counties
header = ["First Name", "Last Name", "Username", "Department", "Job Title", "County", "Application Name", "Account Name", "Role or Permission", "EmployeeType"]

first_names = ["Ava", "Liam", "Emma", "Noah", "Olivia", "Elijah", "Sophia", "Lucas", "Amelia", "Mason"]
last_names = ["Brown", "Smith", "Johnson", "Williams", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]

departments = ["Sales", "Operations", "Legal", "Customer Service", "HR", "Finance", "Engineering", "Marketing"]
job_titles = ["Director", "Manager", "Consultant", "Associate", "Analyst", "Specialist", "Coordinator"]
counties = ["Monmouth", "Hudson", "Morris", "Somerset", "Passaic", "Ocean", "Essex", "Bergen"]
applications = ["App1", "App2", "App3", "App4", "App5", "App6", "App7", "App8", "App9", "App10"]
roles = ["Admin", "Power User", "User", "Read-Only", "Guest"]
employee_types = ["Employee", "Contractor", "Intern"]

# Generate unique employees with consistent attributes
def generate_unique_employees(num_employees):
    employees = []
    for _ in range(num_employees):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        department = random.choice(departments)
        job_title = random.choice(job_titles)
        county = random.choice(counties)
        employee_type = random.choice(employee_types)
        username = (first_name[0] + last_name + str(random.randint(100, 999))).lower()

        employee = {
            "First Name": first_name,
            "Last Name": last_name,
            "Username": username,
            "Department": department,
            "Job Title": job_title,
            "County": county,
            "EmployeeType": employee_type
        }
        employees.append(employee)
    return employees

# Create a function to generate random entries
def generate_entries(unique_employees, applications, roles, num_entries):
    entries = []
    while len(entries) < num_entries:
        for employee in unique_employees:
            num_employee_entries = random.randint(1, 10)  # Generate 1 to 10 entries per employee
            for _ in range(num_employee_entries):
                entry = {
                    "First Name": employee["First Name"],
                    "Last Name": employee["Last Name"],
                    "Username": employee["Username"],
                    "Department": employee["Department"],
                    "Job Title": employee["Job Title"],
                    "County": employee["County"],
                    "Application Name": random.choice(applications),
                    "Account Name": f"{employee['First Name']} {employee['Last Name']}",
                    "Role or Permission": random.choice(roles),
                    "EmployeeType": employee["EmployeeType"]
                }
                entries.append(entry)
                if len(entries) >= num_entries:
                    break
            if len(entries) >= num_entries:
                break
    return entries

# Generate 3,000 unique employees
num_unique_employees = 3000
unique_employees = generate_unique_employees(num_unique_employees)

# Generate 30,000 entries
num_entries = 30000
entries = generate_entries(unique_employees, applications, roles, num_entries)

# Write to CSV
with open('employees.csv', 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=header)
    writer.writeheader()
    writer.writerows(entries)
