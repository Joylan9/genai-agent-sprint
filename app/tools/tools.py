class SimpleSearchTool:
    def search(self, query):
        # Dummy search logic (can expand later)
        fake_database = {
            "machine learning example": "Email spam filtering is a common example of machine learning.",
            "ai example": "Self-driving cars are an example of AI."
        }

        return fake_database.get(query.lower(), "No results found.")
