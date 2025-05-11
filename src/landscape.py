"""
Simple landscape module for testing.
"""

def describe_landscape():
    return ["Mountains", "Valleys", "Rivers", "Plains"]

if __name__ == "__main__":
    for feature in describe_landscape():
        print(f"- {feature}")
