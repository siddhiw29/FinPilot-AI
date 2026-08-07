def generate_recommendations(savings, category_spending):
    recommendations = []

    if savings > 5000:
        recommendations.append(" Excellent savings! Keep maintaining your financial discipline.")
    else:
        recommendations.append(" Try to increase your monthly savings.")

    top_category = category_spending.idxmax()
    top_amount = category_spending.max()

    recommendations.append(
        f"📌 Highest spending category: {top_category} (€{top_amount:.2f})"
    )

    if top_category == "Food & Dining":
        recommendations.append(" Reduce restaurant spending by planning meals.")
    elif top_category == "Shopping":
        recommendations.append(" Set a monthly shopping budget.")
    elif top_category == "Subscription":
        recommendations.append(" Review and cancel unused subscriptions.")
    elif top_category == "Transportation":
        recommendations.append(" Consider public transport to reduce costs.")
    elif top_category == "Rent":
        recommendations.append(" Rent is your biggest expense. Balance the rest of your budget carefully.")

    return recommendations