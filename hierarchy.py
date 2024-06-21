import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import GridSearchCV

# Load the dataset
df = pd.read_csv('data/employees.csv')
df['App_Role'] = df['Application Name'] + ' - ' + df['Role or Permission']

# One-Hot Encoding for each unique access (App_Role) per Username
df_access = df[['Username', 'App_Role']].drop_duplicates()
df_access['access'] = 1
df_pivot = df_access.pivot_table(index='Username', columns='App_Role', values='access', fill_value=0)
df_pivot = df_pivot.reset_index()

# Identify common accesses and their percentages
access_columns = df_pivot.columns[1:]  # Exclude 'Username' from access columns
mean_access = df_pivot[access_columns].mean()
threshold = mean_access.mean() + 1.5 * mean_access.std()

# Get common accesses above a certain threshold
def get_common_accesses(df, access_columns, threshold):
    common_accesses = []
    mean_access = df[access_columns].mean()
    for col in mean_access.index:
        access_percentage = mean_access[col]
        if access_percentage >= threshold:
            common_accesses.append(col)
    return common_accesses

cluster_recommendations = []
written_accesses = set()
recommended_common = set()
recommended_employee_type = set()
recommended_department = set()

# Check for common accesses across all users
common_accesses_all = get_common_accesses(df_pivot, access_columns, threshold)

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
        recommended_common.add((app_name, role))

# Recommendations based on department (all employees and job titles)
for department in df['Department'].unique():
    dept_users = df_pivot[df_pivot['Username'].isin(df[df['Department'] == department]['Username'])]
    common_accesses = get_common_accesses(dept_users, access_columns, threshold)
    if common_accesses:
        for access in common_accesses:
            app_name, role = access.split(' - ')
            if (department, app_name, role) not in written_accesses and (app_name, role) not in recommended_common:
                cluster_recommendations.append({
                    'Hierarchy': 'Department',
                    'Employee Type': 'All',
                    'Department': department,
                    'Job Title': 'All',
                    'Common Accesses': [access]
                })
                written_accesses.add((department, app_name, role))
                recommended_department.add((department, app_name, role))  # Mark as recommended at department level

# Recommendations based on employee type (all departments and job titles)
for employee_type in df['EmployeeType'].unique():
    type_users = df_pivot[df_pivot['Username'].isin(df[df['EmployeeType'] == employee_type]['Username'])]
    common_accesses = get_common_accesses(type_users, access_columns, threshold)
    if common_accesses:
        for access in common_accesses:
            app_name, role = access.split(' - ')
            if (employee_type, app_name, role) not in written_accesses and (app_name, role) not in recommended_common:
                cluster_recommendations.append({
                    'Hierarchy': 'Employee Type',
                    'Employee Type': employee_type,
                    'Department': 'All',
                    'Job Title': 'All',
                    'Common Accesses': [access]
                })
                written_accesses.add((employee_type, app_name, role))
                recommended_employee_type.add((employee_type, app_name, role))  # Mark as recommended at employee type level

# Recommendations based on department + employee type
for department in df['Department'].unique():
    dept_users = df_pivot[df_pivot['Username'].isin(df[df['Department'] == department]['Username'])]
    for employee_type in df[df['Department'] == department]['EmployeeType'].unique():
        type_dept_users = dept_users[dept_users['Username'].isin(df[(df['Department'] == department) & (df['EmployeeType'] == employee_type)]['Username'])]
        common_accesses = get_common_accesses(type_dept_users, access_columns, threshold)
        if common_accesses:
            for access in common_accesses:
                app_name, role = access.split(' - ')
                if (employee_type, department, app_name, role) not in written_accesses and (employee_type, app_name, role) not in recommended_employee_type and (department, app_name, role) not in recommended_department:
                    if (app_name, role) not in recommended_common:
                        cluster_recommendations.append({
                            'Hierarchy': 'Employee Type + Department',
                            'Employee Type': employee_type,
                            'Department': department,
                            'Job Title': 'All',
                            'Common Accesses': [access]
                        })
                        written_accesses.add((employee_type, department, app_name, role))
                        recommended_department.add((department, app_name, role))
        for job_title in df[(df['Department'] == department) & (df['EmployeeType'] == employee_type)]['Job Title'].unique():
            job_users = type_dept_users[type_dept_users['Username'].isin(df[(df['Department'] == department) & (df['EmployeeType'] == employee_type) & (df['Job Title'] == job_title)]['Username'])]
            common_accesses = get_common_accesses(job_users, access_columns, threshold)
            if common_accesses:
                for access in common_accesses:
                    app_name, role = access.split(' - ')
                    if (employee_type, job_title, department, app_name, role) not in written_accesses and (employee_type, app_name, role) not in recommended_employee_type and (department, app_name, role) not in recommended_department and (app_name, role) not in recommended_common:
                        cluster_recommendations.append({
                            'Hierarchy': 'Employee Type + Job Title + Department',
                            'Employee Type': employee_type,
                            'Department': department,
                            'Job Title': job_title,
                            'Common Accesses': [access]
                        })
                        written_accesses.add((employee_type, job_title, department, app_name, role))

# Create DataFrame from recommendations
recommendations_df = pd.DataFrame(cluster_recommendations)

recommendations_df.to_csv('data/recommendations.csv', index=False)
print("Recommendations written to CSV: data/recommendations.csv")


# One-Hot Encoding for Department, Employee Type, and Job Title
onehot_encoder = OneHotEncoder(sparse_output=False)
encoded_features = onehot_encoder.fit_transform(df[['Department', 'EmployeeType', 'Job Title']])
encoded_df = pd.DataFrame(encoded_features, columns=onehot_encoder.get_feature_names_out(['Department', 'EmployeeType', 'Job Title']))

df_combined = pd.concat([df, encoded_df], axis=1)
df_access = df_combined[['Username', 'App_Role']].drop_duplicates()
df_access['access'] = 1
df_pivot = df_access.pivot_table(index='Username', columns='App_Role', values='access', fill_value=0).reset_index()
df_pivot = df_pivot.merge(df_combined[['Username'] + list(encoded_df.columns)].drop_duplicates(), on='Username')

# Define feature columns and access columns
feature_columns = list(encoded_df.columns)
access_columns = df_pivot.columns.difference(['Username'] + feature_columns)

# Parameters for GridSearchCV
param_grid = {
    'contamination': [0.001, 0.005, 0.01, 0.02, 0.05]  # Example values, adjust as needed
}

isolation_forest = IsolationForest(random_state=42)

# Perform GridSearchCV to find optimal contamination
grid_search = GridSearchCV(estimator=isolation_forest, param_grid=param_grid, scoring='neg_mean_squared_error')
grid_search.fit(df_pivot[feature_columns + list(access_columns)])
best_contamination = grid_search.best_params_['contamination']
print(f"Best contamination parameter found: {best_contamination}")

# Fit IsolationForest with the best contamination parameter
isolation_forest_best = IsolationForest(contamination=best_contamination, random_state=42)
df_pivot['Anomaly'] = isolation_forest_best.fit_predict(df_pivot[feature_columns + list(access_columns)])
df_pivot['Anomaly_Score'] = isolation_forest_best.decision_function(df_pivot[feature_columns + list(access_columns)])

# Determine dynamic threshold
anomaly_scores = df_pivot['Anomaly_Score']
threshold = np.percentile(anomaly_scores, 1)

# Identify anomalous users
df_pivot['Anomaly'] = df_pivot['Anomaly_Score'] < threshold
anomalies = df_pivot[df_pivot['Anomaly'] == True]['Username']

for user in anomalies:
    user_info = df[df['Username'] == user]
    user_info.to_csv('data/anomalies.csv', index=False)
    
print("Recommendations written to CSV: data/anomalies.csv")