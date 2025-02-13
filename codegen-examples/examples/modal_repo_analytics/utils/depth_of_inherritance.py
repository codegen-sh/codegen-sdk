import codegen
from codegen import Codebase


def calculate_doi(cls):
    """Calculate the depth of inheritance for a given class."""
    return len(cls.superclasses)


@codegen.function("depth-of-inheritance")
def run(codebase: Codebase):
    """Analyze depth of inheritance for all classes in the codebase."""
    results = []
    total_doi = 0

    for cls in codebase.classes:
        doi = calculate_doi(cls)
        results.append({"name": cls.name, "doi": doi})
        total_doi += doi

    results.sort(key=lambda x: x["doi"], reverse=True)

    if results:
        print("\nClasses by Depth of Inheritance:")
        # Find the highest DOI value
        max_doi = results[0]["doi"]
        # Print classes with highest DOI first, then the rest
        print("\n🏆 Classes with highest DOI:")
        for result in results:
            if result["doi"] == max_doi:
                print(f"Class: {result['name']}, DOI: {result['doi']}")

        print("\nOther classes:")
        for result in results:
            if result["doi"] < max_doi:
                print(f"Class: {result['name']}, DOI: {result['doi']}")
    else:
        print("❌ No classes found in the codebase to analyze.")


if __name__ == "__main__":
    codebase = Codebase.from_repo("modal-labs/modal-client")
    run(codebase)
