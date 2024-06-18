import pandas as pd
from sklearn.cluster import KMeans
import csv

# Load the dataset
df = pd.read_csv('data/role_mining_data.csv')

# Create a combined column for Application Name + Role or Permission
df['App_Role'] = df['Application Name'] + ' - ' + df['Role or Permission']

# One-Hot Encoding for each unique access (App_Role)
df_access = df[['Username', 'App_Role']].drop_duplicates()
df_access['access'] = 1
df_pivot = df_access.pivot(index='Username', columns='App_Role', values='access').fillna(0)

# Merge access data back to the main dataframe
df = df.merge(df_pivot, on='Username', how='left')

# Identify common accesses and their percentages
access_columns = df_pivot.columns
mean_access = df[access_columns].mean()

# Determine the threshold
threshold = mean_access.mean() + mean_access.std()

# Function to get common accesses above a certain threshold
def get_common_accesses(df, access_columns, threshold):
    common_accesses = []
    mean_access = df[access_columns].mean()
    for col in mean_access.index:
        access_percentage = mean_access[col]
        if access_percentage >= threshold:
            common_accesses.append(col)
    return common_accesses

# Check if we have enough data to perform clustering
if len(df) >= 10:
    # Prepare features for clustering
    encoded_dept = pd.get_dummies(df['Department'], prefix='dept_')
    encoded_job = pd.get_dummies(df['Job Title'], prefix='job_')
    encoded_type = pd.get_dummies(df['EmployeeType'], prefix='type_')
    features = pd.concat([encoded_dept, encoded_job, encoded_type, df[access_columns]], axis=1)

    # Determine optimal number of clusters using the Elbow Method
    def find_optimal_clusters(data, max_clusters=10):
        sse = []
        for k in range(1, max_clusters + 1):
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(data)
            sse.append(kmeans.inertia_)
        return sse.index(min(sse[1:])) + 1

    try:
        optimal_clusters = find_optimal_clusters(features)
    except ValueError as e:
        print(f"Clustering failed: {str(e)}")
        optimal_clusters = 1  # Default to 1 cluster if clustering fails

    # Adjust number of clusters if less than the specified minimum (4)
    if optimal_clusters < 4:
        print(f"Warning: Number of clusters found ({optimal_clusters}) is less than expected (4). Adjusting to 4 clusters.")
        optimal_clusters = 4

    # Create and fit KMeans model with optimal number of clusters
    try:
        kmeans = KMeans(n_clusters=optimal_clusters, random_state=42)
        kmeans.fit(features)
        df['Cluster'] = kmeans.labels_
    except ValueError as e:
        print(f"Clustering failed: {str(e)}")
        df['Cluster'] = 0  # Default to 0 cluster if clustering fails

else:
    df['Cluster'] = 0  # Default to 0 cluster if data size is less than 10

# Analyze clusters and provide access recommendations
cluster_recommendations = []

# Track written accesses to avoid duplicates
written_accesses = set()

# Initialize sets to track which accesses have been recommended at higher hierarchy levels
recommended_employee_type = set()
recommended_department = set()

# Check for common accesses across all users
common_accesses_all = get_common_accesses(df, access_columns, threshold)

if common_accesses_all:
    for access in common_accesses_all:
        app_name, role = access.split(' - ')
        cluster_recommendations.append({
            'Hierarchy': 'Common Access',
            'Employee Type': 'All',
            'Department': 'All',
            'Job Title': 'All',
            'Common Accesses': [access]
        })
        written_accesses.add((app_name, role))

# Loop through each cluster and generate recommendations
for cluster in range(df['Cluster'].nunique()):
    cluster_users = df[df['Cluster'] == cluster]
    
    # Step 1: Recommendations based on department (all employees and job titles)
    for department in cluster_users['Department'].unique():
        dept_users = cluster_users[cluster_users['Department'] == department]
        common_accesses = get_common_accesses(dept_users, access_columns, threshold)
        if common_accesses:
            for access in common_accesses:
                app_name, role = access.split(' - ')
                if (department, app_name, role) not in written_accesses:
                    cluster_recommendations.append({
                        'Hierarchy': 'Department',
                        'Employee Type': 'All',
                        'Department': department,
                        'Job Title': 'All',
                        'Common Accesses': [access]
                    })
                    written_accesses.add((department, app_name, role))
                    recommended_department.add((department, app_name, role))  # Mark as recommended at department level
    
    # Step 2: Recommendations based on employee type (all departments and job titles)
    for employee_type in cluster_users['EmployeeType'].unique():
        type_users = cluster_users[cluster_users['EmployeeType'] == employee_type]
        common_accesses = get_common_accesses(type_users, access_columns, threshold)
        if common_accesses:
            for access in common_accesses:
                app_name, role = access.split(' - ')
                if (employee_type, app_name, role) not in written_accesses:
                    cluster_recommendations.append({
                        'Hierarchy': 'Employee Type',
                        'Employee Type': employee_type,
                        'Department': 'All',
                        'Job Title': 'All',
                        'Common Accesses': [access]
                    })
                    written_accesses.add((employee_type, app_name, role))
                    recommended_employee_type.add((employee_type, app_name, role))  # Mark as recommended at employee type level
    
    # Step 3: Recommendations based on department + employee type (but not already covered by step 1 or 2)
    for department in cluster_users['Department'].unique():
        dept_users = cluster_users[cluster_users['Department'] == department]
        for employee_type in dept_users['EmployeeType'].unique():
            type_dept_users = dept_users[dept_users['EmployeeType'] == employee_type]
            common_accesses = get_common_accesses(type_dept_users, access_columns, threshold)
            if common_accesses:
                for access in common_accesses:
                    app_name, role = access.split(' - ')
                    if (employee_type, department, app_name, role) not in written_accesses:
                        # Check if this access has been recommended at Employee Type level
                        if (employee_type, app_name, role) not in recommended_employee_type:
                            cluster_recommendations.append({
                                'Hierarchy': 'Employee Type + Department',
                                'Employee Type': employee_type,
                                'Department': department,
                                'Job Title': 'All',
                                'Common Accesses': [access]
                            })
                            written_accesses.add((employee_type, department, app_name, role))
                            recommended_department.add((department, app_name, role))  # Mark as recommended at department level

# Write recommendations to CSV file
output_file = 'data/recommendations.csv'

try:
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['Hierarchy', 'Employee Type', 'Department', 'Job Title', 'App Name', 'Role']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        # Write unique recommendations
        for recommendation in cluster_recommendations:
            hierarchy = recommendation['Hierarchy']
            employee_type = recommendation['Employee Type']
            department = recommendation['Department']
            job_title = recommendation['Job Title']
            common_accesses = recommendation['Common Accesses']
            
            for access in common_accesses:
                app_name, role = access.split(' - ')
                writer.writerow({
                    'Hierarchy': hierarchy,
                    'Employee Type': employee_type,
                    'Department': department,
                    'Job Title': job_title,
                    'App Name': app_name,
                    'Role': role
                })

    print(f"Recommendations written to {output_file}.")
except IOError as e:
    print(f"Error writing recommendations to CSV: {str(e)}")

print("Exiting the program.")
