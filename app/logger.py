import csv
import os
from datetime import datetime


LOG_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "data",
    "logs"
)

os.makedirs(LOG_DIR, exist_ok=True)


def log_prediction(domain, input_dict, prediction, probability):
    """
    Store a churn prediction and the relevant business/model inputs.

    Personal identifying information such as customer name and DOB
    should never be stored in the prediction logs.
    """

    log_file = os.path.join(
        LOG_DIR,
        f"{domain}_logs.csv"
    )

    file_exists = os.path.isfile(log_file)

    # Explicitly remove identity fields if they are ever passed
    # accidentally in the future.
    sensitive_fields = {
        "name",
        "Name",
        "dob",
        "DOB",
        "date_of_birth",
        "DateOfBirth"
    }

    row = {
        key: value
        for key, value in input_dict.items()
        if key not in sensitive_fields
    }

    row["predicted_churn"] = prediction
    row["churn_probability"] = probability
    row["actual_outcome"] = ""
    row["timestamp"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(
        log_file,
        mode="a",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=row.keys()
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)