import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt

# Sample data (replace with your actual data)
data = {
    'department': ['finance', 'marketing', 'finance', 'sales', 'IT', 'IT', 'marketing'],
    'job_title': ['accountant', 'manager', 'analyst', 'representative', 'developer', 'security', 'manager'],
    'emloyee_type': ['employee', 'contractor', 'vendor', 'volunteer', 'intern', 'director', 'visitor'],
    'access_1': [True, True, False, True, False, True, False],
    'access_2': [True, False, True, False, True, False, True],
    'access_3': [True, False, True, True, False, True, False],
    'access_4': [True, False, False, True, True, False, False],
    'access_5': [True, True, True, False, True, True, False],
}
df = pd.DataFrame(data)

# Prepare categorical features for clustering
encoded_dept = pd.get_dummies(df['department'], prefix='dept_')
encoded_job = pd.get_dummies(df['job_title'], prefix='job_')
features = pd.concat([encoded_dept, encoded_job, df[['access_1', 'access_2', 'access_3', 'access_4', 'access_5']]], axis=1)

# Determine optimal number of clusters using the Elbow Method and Silhouette Score
def find_optimal_clusters(data, max_clusters=10):
    n_samples = data.shape[0]
    max_clusters = min(max_clusters, n_samples - 1)
    iters = range(2, max_clusters + 1)
    sse = []
    silhouette_scores = []

    for k in iters:
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(data)
        sse.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(data, kmeans.labels_))
    
    f, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    ax1.plot(iters, sse, marker='o')
    ax1.set_xlabel('Number of clusters')
    ax1.set_ylabel('SSE')
    ax1.set_title('Elbow Method')

    ax2.plot(iters, silhouette_scores, marker='o')
    ax2.set_xlabel('Number of clusters')
    ax2.set_ylabel('Silhouette Score')
    ax2.set_title('Silhouette Score Method')

    plt.show()

    best_k = iters[silhouette_scores.index(max(silhouette_scores))]
    return best_k

optimal_clusters = find_optimal_clusters(features)

# Create and fit KMeans model with optimal number of clusters
kmeans = KMeans(n_clusters=optimal_clusters)
kmeans.fit(features)

# Calculate dynamic threshold for common accesses
access_columns = ['access_1', 'access_2', 'access_3', 'access_4', 'access_5']
mean_access = df[access_columns].mean()
threshold = mean_access.mean()

# Analyze clusters
for i in range(kmeans.n_clusters):
    cluster_users = df.loc[kmeans.labels_ == i]
    cluster_dept = cluster_users['department'].mode()[0]
    cluster_job = cluster_users['job_title'].mode()[0]
    common_accesses = []
    for col in access_columns:
        if cluster_users[col].mean() >= threshold:
            common_accesses.append(col)
    print(f"Cluster {i+1}: Department: {cluster_dept}, Job Title: {cluster_job}, Common Accesses: {common_accesses}")
