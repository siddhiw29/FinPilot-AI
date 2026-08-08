import streamlit as st


def show_savings_goal(savings, currency_symbol):

    st.header("Savings Goal Tracker")

    st.write(
        "Set a savings target and track your progress."
    )

    goal = st.number_input(
        "Savings Goal",
        min_value=0.0,
        value=10000.0,
        step=500.0
    )

    if goal <= 0:
        st.warning("Please enter a savings goal greater than zero.")
        return

    progress = min(max(savings / goal, 0), 1)

    percentage = progress * 100

    remaining = max(goal - savings, 0)

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Savings",
        f"{currency_symbol}{savings:.2f}"
    )

    col2.metric(
        "Goal",
        f"{currency_symbol}{goal:.2f}"
    )

    col3.metric(
        "Remaining",
        f"{currency_symbol}{remaining:.2f}"
    )

    st.subheader("Goal Progress")

    st.progress(progress)

    st.write(
        f"You have reached **{percentage:.1f}%** of your savings goal."
    )

    if savings >= goal:
        st.success(
            "Congratulations! You have reached your savings goal."
        )
    elif percentage >= 75:
        st.info(
            "You're very close to reaching your savings goal."
        )
    elif percentage >= 50:
        st.info(
            "You're halfway there. Keep going!"
        )
    else:
        st.warning(
            "Keep saving consistently to reach your goal."
        )