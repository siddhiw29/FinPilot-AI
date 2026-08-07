def assign_category(description):
    """
    Classify a transaction into an expense category.
    """

    description = str(description).lower()

    if "tesco" in description:
        return "Groceries"

    elif "rent" in description:
        return "Rent"

    elif "spotify" in description:
        return "Subscription"

    elif "taxi" in description:
        return "Transportation"

    elif "restaurant" in description or "bistro" in description:
        return "Food & Dining"

    elif "consulting" in description:
        return "Salary"

    else:
        return "Miscellaneous"