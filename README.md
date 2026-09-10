# Customer Churn Prediction

A multi-domain machine learning application for predicting customer churn across **Banking, Telecom, and E-commerce** industries.

The project combines machine learning models with a Flask-based web application that allows users to enter customer information and receive a churn prediction together with the estimated probability of churn.

---

## 📌 Project Overview

Customer churn is a major challenge across subscription-based and customer-centric businesses. Identifying customers who are likely to leave allows organizations to take proactive retention measures.

This project develops and deploys machine learning models for three different business domains:

- 🏦 **Banking Customer Churn**
- 📱 **Telecom Customer Churn**
- 🛒 **E-commerce Customer Churn**

The trained models are integrated into a Flask web application where users can select a domain, enter customer information, and receive an immediate prediction.

---

## ✨ Key Features

- Multi-domain customer churn prediction
- Banking churn prediction
- Telecom churn prediction
- E-commerce churn prediction
- Machine learning models trained using real-world datasets
- CatBoost-based prediction models
- Probability-based churn prediction
- Web-based prediction forms
- Input validation
- Prediction logging
- Separate trained models for each business domain
- Model evaluation and comparison
- Training notebooks and experiment results
- Confusion matrices, ROC curves, and feature-importance visualizations

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │    Web Browser      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Flask Web App     │
                    │      app.py         │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌───────────┐    ┌───────────┐    ┌────────────┐
        │  Banking  │    │  Telecom  │    │ E-commerce │
        │   Model   │    │   Model   │    │   Model    │
        └─────┬─────┘    └─────┬─────┘    └──────┬─────┘
              │                │                 │
              └────────────────┼─────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Churn Prediction +  │
                    │ Probability Score   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Prediction Logging  │
                    └─────────────────────┘
