import json
import random
from datetime import datetime, timedelta

# South Indian names (Tamil, Telugu, Kannada, Malayalam)
first_names = [
    "Rajesh", "Priya", "Arjun", "Divya", "Arun", "Sneha", "Vikram", "Anusha",
    "Karthik", "Neha", "Suresh", "Pooja", "Ramesh", "Anjali", "Mohan", "Kavya",
    "Srinivas", "Deepika", "Ravi", "Ananya", "Prasad", "Swathi", "Ashok", "Nisha",
    "Venkat", "Bhavana", "Kumar", "Keerthi", "Sai", "Pragya", "Aditya", "Shruti",
    "Hari", "Padma", "Sandeep", "Lakshmi", "Naveen", "Anjum", "Ajay", "Shreya",
    "Balaji", "Isha", "Gopal", "Ritika", "Ganesh", "Shalini", "Rohan", "Harini",
    "Sanjay", "Seema", "Vikram", "Madhavi", "Nitin", "Divyasree", "Prabhakar", "Saranya",
    "Mahesh", "Usha", "Sameer", "Gowri", "Ravishankar", "Kaveri", "Anand", "Malini",
    "Rajkumar", "Yashaswini", "Sudeep", "Thananya", "Siddarth", "Ishita", "Naveen", "Meera"
]

last_names = [
    "Kumar", "Sharma", "Singh", "Reddy", "Rao", "Desai", "Iyer", "Menon",
    "Nair", "Chakraborty", "Gupta", "Verma", "Pandey", "Chaurasia", "Malhotra",
    "Bhat", "Kadam", "Joshi", "Krishnan", "Murthy", "Sinha", "Srivastava",
    "Gowda", "Yadav", "Kulkarni", "Hegde", "Shetty", "Thakur", "Bhatnagar",
    "Trivedi", "Saxena", "Chopra", "Arora", "Rawat", "Misra", "Banerjee",
    "Das", "Dutta", "Agarwal", "Sethi", "Patel", "Jain", "Majumdar",
    "Roy", "Ghosh", "Bhattacharya", "Mukherjee", "Prasad", "Nambiar", "Pillai"
]

# Hyderabad area coordinates with clustering
hyderabad_areas = {
    "Hitech City": (17.3551, 78.3725, 0.02),
    "HITEC": (17.4439, 78.4432, 0.02),
    "Secunderabad": (17.3647, 78.4950, 0.02),
    "Banjara Hills": (17.3905, 78.4639, 0.02),
    "Jubilee Hills": (17.4064, 78.3925, 0.02),
    "Madhapur": (17.4434, 78.4278, 0.02),
    "Gachibowli": (17.4439, 78.3542, 0.02),
    "Whitefield": (17.3561, 78.3486, 0.02),
    "Kondapur": (17.4539, 78.3347, 0.02),
    "Chanda Nagar": (17.3800, 78.4800, 0.02),
    "Bannerghatta": (17.3298, 78.4100, 0.02),
    "Begumpet": (17.3833, 78.4572, 0.02),
    "Shamshabad": (17.2380, 78.5925, 0.02),
    "Kukatpally": (17.4696, 78.4254, 0.02),
    "Kachiguda": (17.3833, 78.5067, 0.02),
}

base_timestamp = 1593866130  # June 4, 2020
synthetic_data = []

# Create 100 unique people
unique_people = []
for i in range(100):
    person_name = f"{random.choice(first_names)} {random.choice(last_names)}"
    unique_people.append(person_name)

# Create contact clusters - realistic scenario where groups of people meet
clusters = {}
for i in range(8):
    cluster_size = random.randint(8, 15)
    cluster_people = random.sample(unique_people, cluster_size)
    cluster_area = random.choice(list(hyderabad_areas.keys()))
    clusters[f"Cluster_{i}"] = {
        "people": cluster_people,
        "area": cluster_area,
        "base_time": base_timestamp + (i * 21600)  # 6 hours apart
    }

def generate_location(area_name, variation=1.0):
    """Generate realistic location within area"""
    center_lat, center_lon, radius = hyderabad_areas[area_name]
    lat = center_lat + random.uniform(-radius * variation, radius * variation)
    lon = center_lon + random.uniform(-radius * variation, radius * variation)
    return round(lat, 7), round(lon, 7)

# Generate data with clusters (creates higher contact risk)
for cluster_name, cluster_data in clusters.items():
    cluster_time = cluster_data["base_time"]
    
    # Each person in cluster visits multiple times in the cluster's time window
    for person in cluster_data["people"]:
        # Generate 3-8 visits per person in the cluster
        num_visits = random.randint(3, 8)
        
        for visit in range(num_visits):
            # Time variation: people in same cluster overlap in time
            time_offset = random.randint(-7200, 7200)  # ±2 hours
            
            # Slight location variation within area
            lat, lon = generate_location(cluster_data["area"], variation=random.uniform(0.3, 1.2))
            
            timestamp = cluster_time + time_offset + (visit * 1800)  # 30 min apart
            
            record = {
                "id": person,
                "timestamp": int(timestamp),
                "latitude": str(lat),
                "longitude": str(lon)
            }
            synthetic_data.append(record)

# Add some individual movements (people not in heavy contact scenarios)
remaining_people = [p for p in unique_people if not any(p in cluster_data["people"] for cluster_data in clusters.values())]

for person in remaining_people:
    num_visits = random.randint(4, 12)
    
    for visit in range(num_visits):
        area = random.choice(list(hyderabad_areas.keys()))
        lat, lon = generate_location(area)
        
        timestamp = base_timestamp + random.randint(0, 604800)  # Random time in week
        
        record = {
            "id": person,
            "timestamp": int(timestamp),
            "latitude": str(lat),
            "longitude": str(lon)
        }
        synthetic_data.append(record)

# Add high-risk scenario: super-spreader event (15+ people in same place/time)
spreader_event_time = base_timestamp + 259200  # Day 3
spreader_people = random.sample(unique_people, random.randint(15, 25))
spreader_area = random.choice(list(hyderabad_areas.keys()))

for person in spreader_people:
    for i in range(random.randint(2, 4)):
        lat, lon = generate_location(spreader_area, variation=0.5)
        
        time_offset = random.randint(-3600, 3600)  # ±1 hour
        timestamp = spreader_event_time + time_offset
        
        record = {
            "id": person,
            "timestamp": int(timestamp),
            "latitude": str(lat),
            "longitude": str(lon)
        }
        synthetic_data.append(record)

# Sort by timestamp
synthetic_data.sort(key=lambda x: x['timestamp'])

# Remove duplicates (same person, same time, same location)
unique_records = []
seen = set()
for record in synthetic_data:
    key = (record['id'], record['timestamp'], record['latitude'], record['longitude'])
    if key not in seen:
        seen.add(key)
        unique_records.append(record)

# Write to JSON file
with open('hyderabad_sample_100_records.json', 'w', encoding='utf-8') as f:
    json.dump(unique_records, f, indent=2, ensure_ascii=False)

print(f"✅ Generated {len(unique_records)} realistic contact tracing records")
print(f"📍 Unique people: {len(set([r['id'] for r in unique_records]))}")
print(f"🏙️ Hyderabad areas covered: {len(hyderabad_areas)}")
print(f"🤝 Contact clusters created: {len(clusters)}")
print(f"📊 Total records: {len(unique_records)}")

# Calculate statistics
from collections import defaultdict
person_counts = defaultdict(int)
for record in unique_records:
    person_counts[record['id']] += 1

print(f"\n📈 Record Distribution:")
print(f"  Average records per person: {len(unique_records) / len(person_counts):.1f}")
print(f"  Max records for one person: {max(person_counts.values())}")
print(f"  Min records for one person: {min(person_counts.values())}")

# Show clustering effect
print(f"\n👥 Contact Scenario Analysis:")
print(f"  People in clusters: {sum(len(c['people']) for c in clusters.values())}")
print(f"  People in super-spreader event: {len(spreader_people)}")
print(f"  Independent individuals: {len(remaining_people)}")

# Sample records
print("\n📋 Sample Records (first 10):")
for i, record in enumerate(unique_records[:10]):
    dt = datetime.utcfromtimestamp(record['timestamp'])
    print(f"\n{i+1}. {record['id']}")
    print(f"   Time: {dt}")
    print(f"   Location: ({record['latitude']}, {record['longitude']})")

print("\n✅ File saved as: hyderabad_sample_100_records.json")
print("⚠️ This data includes high-risk contact scenarios for realistic testing!")
