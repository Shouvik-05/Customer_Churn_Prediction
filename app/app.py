from flask import Flask, render_template, request
import os
import joblib
import pandas as pd
from datetime import date, datetime
from logger import log_prediction

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
MODELS_DIR = os.path.join(PROJECT_DIR, "models")


def load_model(filename):
    path = os.path.join(MODELS_DIR, filename)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Model not found: {path}")

    return joblib.load(path)


# ============================================================
# LOAD MODELS
# ============================================================

banking_model = load_model("bank_customer_churn_catboost.pkl")
telecom_model = load_model("telecom_best_catboost.pkl")
ecommerce_model = load_model("ecommerce_model.pkl")


# ============================================================
# HOME
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


# ============================================================
# FORMS
# ============================================================

@app.route("/form/banking")
def banking_form():
    return render_template("banking_form.html")


@app.route("/form/telecom")
def telecom_form():
    return render_template("telecom_form.html")


@app.route("/form/ecommerce")
def ecommerce_form():
    return render_template("ecommerce_form.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


# ============================================================
# BANKING PREDICTION
# ============================================================

@app.route("/predict/banking", methods=["POST"])
def predict_banking():
    f = request.form
    customer_reference = f.get("customer_reference", "").strip()

    # ---------------------------
    # Validate submitted values
    # ---------------------------
    allowed_gender = {"Female", "Male"}
    allowed_geography = {"France", "Germany", "Spain"}

    try:
        dob = datetime.strptime(f["DateOfBirth"], "%Y-%m-%d").date()
        today = date.today()
        age = today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )

        credit_score = float(f["CreditScore"])
        tenure = float(f["Tenure"])
        balance = float(f["Balance"])
        num_products = int(f["NumOfProducts"])
        has_card = int(f["HasCrCard"])
        active_member = int(f["IsActiveMember"])
        estimated_salary = float(f["EstimatedSalary"])
    except (KeyError, ValueError, TypeError):
        return render_template(
            "banking_form.html",
            error="Please enter valid values in all required fields."
        ), 400

    if not (18 <= age <= 100):
        return render_template(
            "banking_form.html",
            error="Customer age must be between 18 and 100 years."
        ), 400

    if not (300 <= credit_score <= 900):
        return render_template(
            "banking_form.html",
            error="Credit Score must be between 300 and 900."
        ), 400

    if not (0 <= tenure <= 20):
        return render_template(
            "banking_form.html",
            error="Tenure must be between 0 and 20 years."
        ), 400

    if balance < 0:
        return render_template(
            "banking_form.html",
            error="Account Balance cannot be negative."
        ), 400

    if num_products not in {1, 2, 3, 4}:
        return render_template(
            "banking_form.html",
            error="Number of Products must be between 1 and 4."
        ), 400

    if has_card not in {0, 1} or active_member not in {0, 1}:
        return render_template(
            "banking_form.html",
            error="Please select valid Yes/No values."
        ), 400

    if estimated_salary < 0:
        return render_template(
            "banking_form.html",
            error="Estimated Salary cannot be negative."
        ), 400

    geography = f.get("Geography", "")
    gender = f.get("Gender", "")

    if geography not in allowed_geography:
        return render_template(
            "banking_form.html",
            error="Please select a valid Geography."
        ), 400

    if gender not in allowed_gender:
        return render_template(
            "banking_form.html",
            error="Please select a valid Gender."
        ), 400

    # ---------------------------
    # Build exact model input
    # ---------------------------
    X = pd.DataFrame([{
        "CreditScore": credit_score,
        "Age": float(age),
        "Tenure": tenure,
        "Balance": balance,
        "NumOfProducts": float(num_products),
        "HasCrCard": float(has_card),
        "IsActiveMember": float(active_member),
        "EstimatedSalary": estimated_salary,
        "Geography_Germany": int(geography == "Germany"),
        "Geography_Spain": int(geography == "Spain"),
        "Gender_Male": int(gender == "Male")
    }])

    X = X[banking_model.feature_names_]

    pred = int(banking_model.predict(X)[0])
    proba = float(banking_model.predict_proba(X)[0][1])
    probability = round(proba * 100, 2)

    log_data = {
        "customer_reference": customer_reference,
        "CreditScore": credit_score,
        "Age": age,
        "Gender": gender,
        "Geography": geography,
        "Tenure": tenure,
        "Balance": balance,
        "NumOfProducts": num_products,
        "HasCrCard": has_card,
        "IsActiveMember": active_member,
        "EstimatedSalary": estimated_salary
    }

    log_prediction("banking", log_data, pred, probability)

    return render_template(
        "result.html",
        customer_reference=customer_reference,
        domain="Banking",
        churn=bool(pred),
        probability=probability
    )


@app.route("/predict/telecom", methods=["POST"])
def predict_telecom():
    f = request.form
    customer_reference = f.get("customer_reference", "").strip()

    allowed = {
        "Gender": {"Female", "Male"},
        "SeniorCitizen": {"Yes", "No"},
        "Partner": {"Yes", "No"},
        "Dependents": {"Yes", "No"},
        "PhoneService": {"Yes", "No"},
        "MultipleLines": {"No", "Yes", "No phone service"},
        "InternetService": {"DSL", "Fiber optic", "No"},
        "OnlineSecurity": {"No", "Yes", "No internet service"},
        "OnlineBackup": {"No", "Yes", "No internet service"},
        "DeviceProtection": {"No", "Yes", "No internet service"},
        "TechSupport": {"No", "Yes", "No internet service"},
        "StreamingTV": {"No", "Yes", "No internet service"},
        "StreamingMovies": {"No", "Yes", "No internet service"},
        "Contract": {"Month-to-month", "One year", "Two year"},
        "PaperlessBilling": {"Yes", "No"},
        "PaymentMethod": {
            "Bank transfer (automatic)",
            "Credit card (automatic)",
            "Electronic check",
            "Mailed check"
        }
    }

    for field, values in allowed.items():
        if f.get(field) not in values:
            return render_template(
                "telecom_form.html",
                error=f"Please select a valid value for {field}."
            ), 400

    try:
        tenure_months = float(f["TenureMonths"])
        monthly_charges = float(f["MonthlyCharges"])
        total_charges = float(f["TotalCharges"])
        cltv = float(f["CLTV"])
    except (KeyError, ValueError, TypeError):
        return render_template(
            "telecom_form.html",
            error="Please enter valid numeric values in all required fields."
        ), 400

    if not (0 <= tenure_months <= 72):
        return render_template(
            "telecom_form.html",
            error="Tenure must be between 0 and 72 months."
        ), 400

    if not (0 <= monthly_charges <= 200):
        return render_template(
            "telecom_form.html",
            error="Monthly Charges must be between $0 and $200."
        ), 400

    if total_charges < 0:
        return render_template(
            "telecom_form.html",
            error="Total Charges cannot be negative."
        ), 400

    if cltv < 0:
        return render_template(
            "telecom_form.html",
            error="Customer Lifetime Value cannot be negative."
        ), 400

    X = pd.DataFrame([{
        "Gender": f["Gender"],
        "Senior Citizen": f["SeniorCitizen"],
        "Partner": f["Partner"],
        "Dependents": f["Dependents"],
        "Tenure Months": tenure_months,
        "Phone Service": f["PhoneService"],
        "Multiple Lines": f["MultipleLines"],
        "Internet Service": f["InternetService"],
        "Online Security": f["OnlineSecurity"],
        "Online Backup": f["OnlineBackup"],
        "Device Protection": f["DeviceProtection"],
        "Tech Support": f["TechSupport"],
        "Streaming TV": f["StreamingTV"],
        "Streaming Movies": f["StreamingMovies"],
        "Contract": f["Contract"],
        "Paperless Billing": f["PaperlessBilling"],
        "Payment Method": f["PaymentMethod"],
        "Monthly Charges": monthly_charges,
        "Total Charges": total_charges,
        "CLTV": cltv
    }])

    X = X[telecom_model.feature_names_]

    pred = int(telecom_model.predict(X)[0])
    proba = float(telecom_model.predict_proba(X)[0][1])
    probability = round(proba * 100, 2)

    log_data = {
        "customer_reference": customer_reference,
        "Gender": f["Gender"],
        "SeniorCitizen": f["SeniorCitizen"],
        "Partner": f["Partner"],
        "Dependents": f["Dependents"],
        "TenureMonths": tenure_months,
        "PhoneService": f["PhoneService"],
        "MultipleLines": f["MultipleLines"],
        "InternetService": f["InternetService"],
        "OnlineSecurity": f["OnlineSecurity"],
        "OnlineBackup": f["OnlineBackup"],
        "DeviceProtection": f["DeviceProtection"],
        "TechSupport": f["TechSupport"],
        "StreamingTV": f["StreamingTV"],
        "StreamingMovies": f["StreamingMovies"],
        "Contract": f["Contract"],
        "PaperlessBilling": f["PaperlessBilling"],
        "PaymentMethod": f["PaymentMethod"],
        "MonthlyCharges": monthly_charges,
        "TotalCharges": total_charges,
        "CLTV": cltv
    }

    log_prediction("telecom", log_data, pred, probability)

    return render_template(
        "result.html",
        customer_reference=customer_reference,
        domain="Telecom",
        churn=bool(pred),
        probability=probability
    )


@app.route("/predict/ecommerce", methods=["POST"])
def predict_ecommerce():
    f = request.form
    customer_reference = f.get("customer_reference", "").strip()

    try:
        days_since_last_purchase = float(f["days_since_last_purchase"])
        total_orders = float(f["total_orders"])
        total_spending = float(f["total_spending"])
        average_review_score = float(f["average_review_score"])
        average_delivery_days = float(f["average_delivery_days"])
        late_delivery_count = float(f["late_delivery_count"])
        number_of_reviews = float(f["number_of_reviews"])
    except (KeyError, ValueError, TypeError):
        return render_template(
            "ecommerce_form.html",
            error="Please enter valid values in all required fields."
        ), 400

    if days_since_last_purchase < 0:
        return render_template(
            "ecommerce_form.html",
            error="Days Since Last Purchase cannot be negative."
        ), 400

    if total_orders < 0:
        return render_template(
            "ecommerce_form.html",
            error="Total Orders cannot be negative."
        ), 400

    if total_spending < 0:
        return render_template(
            "ecommerce_form.html",
            error="Total Spending cannot be negative."
        ), 400

    if not (1 <= average_review_score <= 5):
        return render_template(
            "ecommerce_form.html",
            error="Average Review Score must be between 1 and 5."
        ), 400

    if average_delivery_days < 0:
        return render_template(
            "ecommerce_form.html",
            error="Average Delivery Time cannot be negative."
        ), 400

    if late_delivery_count < 0:
        return render_template(
            "ecommerce_form.html",
            error="Late Delivery Count cannot be negative."
        ), 400

    if late_delivery_count > total_orders:
        return render_template(
            "ecommerce_form.html",
            error="Late Deliveries cannot exceed Total Orders."
        ), 400

    if number_of_reviews < 0:
        return render_template(
            "ecommerce_form.html",
            error="Number of Reviews cannot be negative."
        ), 400

    # Derived features required by the trained E-commerce model
    total_items = total_orders
    average_order_value = (
        total_spending / total_orders if total_orders > 0 else 0.0
    )
    total_seller_connections = 1.0
    total_products = 1.0
    total_category_connections = 1.0
    low_review_count = (
        number_of_reviews if average_review_score <= 2 else 0.0
    )
    average_installments = 2.0
    total_payment_value = total_spending
    purchase_frequency = 1.0
    customer_lifetime_days = max(days_since_last_purchase, 1.0)

    X = pd.DataFrame([{
        "total_orders": total_orders,
        "total_items": total_items,
        "total_spending": total_spending,
        "average_order_value": average_order_value,
        "total_seller_connections": total_seller_connections,
        "total_products": total_products,
        "total_category_connections": total_category_connections,
        "average_review_score": average_review_score,
        "number_of_reviews": number_of_reviews,
        "low_review_count": low_review_count,
        "average_delivery_days": average_delivery_days,
        "late_delivery_count": late_delivery_count,
        "average_installments": average_installments,
        "total_payment_value": total_payment_value,
        "days_since_last_purchase": days_since_last_purchase,
        "purchase_frequency": purchase_frequency,
        "customer_lifetime_days": customer_lifetime_days
    }])

    X = X[ecommerce_model.feature_names_]

    pred = int(ecommerce_model.predict(X)[0])
    proba = float(ecommerce_model.predict_proba(X)[0][1])
    probability = round(proba * 100, 2)

    log_data = {
        "customer_reference": customer_reference,
        "days_since_last_purchase": days_since_last_purchase,
        "total_orders": total_orders,
        "total_spending": total_spending,
        "average_review_score": average_review_score,
        "average_delivery_days": average_delivery_days,
        "late_delivery_count": late_delivery_count,
        "number_of_reviews": number_of_reviews
    }

    log_prediction("ecommerce", log_data, pred, probability)

    return render_template(
        "result.html",
        customer_reference=customer_reference,
        domain="E-commerce",
        churn=bool(pred),
        probability=probability
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)