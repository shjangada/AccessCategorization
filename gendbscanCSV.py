import pandas as pd
from sklearn.cluster import DBSCAN
from collections import defaultdict

# Read data from CSV file
df = pd.read_csv('data/user_access.csv')
grouped_data = df.groupby(["username","department", "jobTitle"])["access"].apply(",".join).reset_index()
#print(grouped_data)
# Separate access values into multiple columns
col_list = pd.Series(df['access'].unique()).str.split(',')
dfcollist = col_list .explode()
access_cols = dfcollist.unique()
# Split access column into separate columns
access_values = grouped_data["access"].str.split(",")
#print(access_values)
for value in access_cols:
    grouped_data[f"{value.strip()}"] = False
#print(grouped_data)
grouped_data.drop("access", axis=1, inplace=True)
for i in range(len(grouped_data)):
    for value in access_values.iloc[i]:
        grouped_data.loc[i, [value]] = True
#print(grouped_data)


# Print the result
#print(combined_df[:,0:2])

#print(grouped_df.mean())  # Example: calculate group means
# Prepare categorical features for clustering
encoded_features = pd.get_dummies(grouped_data[['department', 'jobTitle']])

# Define DBSCAN parameters
eps = 0.5  # Experiment with different values
min_samples = int(0.2 * grouped_data.shape[0])  # Adjust for density

# Create and fit DBSCAN model
dbscan = DBSCAN(eps=eps, min_samples=min_samples)
dbscan.fit(encoded_features)

# Analyze clusters
#for i in range(-1, len(set(dbscan.labels_)) - 1):  # Include noise (-1)
for i in range(-1, len(set(dbscan.labels_)) ):  # Include noise (-1)
    cluster_users = grouped_data.loc[dbscan.labels_ == i]
    #print (cluster_users)
    if cluster_users.shape[0] >= 5:  # Apply 80% threshold -- Minimum 3 records in the cluster
        common_accesses = []
        for col in access_cols:
            #print(cluster_users[col])
            #print(cluster_users[col].mean())
            if cluster_users[col].mean() >= 0.8:
                common_accesses.append(col)

        if common_accesses:
            #print(f"Cluster {i+1} (Noise if -1): {common_accesses}")
            cluster_info = pd.concat([pd.DataFrame(cluster_users['department'].unique(), columns=['department']),
                                     pd.DataFrame(cluster_users['jobTitle'].unique(), columns=['jobTitle'])], axis=1)
            # Print formatted cluster information
            print(f"Cluster {i+1} (Noise if -1):")
            for index, row in cluster_info.iterrows():
                print(f"  - Department: {row['department']}, Job Title: {row['jobTitle']}")
            print(f"    Common Accesses: {common_accesses}")
"""  
            """