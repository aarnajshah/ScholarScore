# IMPORT THE TOOLS WE NEED

# os lets Python read environment variables, including our private API key.
import os

# requests lets Python communicate with websites and APIs.
import requests

# pandas lets us organize information into tables.
import pandas as pd

# Path helps Python find our .env file.
from pathlib import Path

# dotenv lets Python read variables stored in .env.
from dotenv import load_dotenv

# This lets us divide our data into training data and testing data.
from sklearn.model_selection import train_test_split

# This is the actual machine learning algorithm we are going to train.
from sklearn.tree import DecisionTreeClassifier

# This lets us calculate how accurate our model is.
from sklearn.metrics import accuracy_score



# LOAD OUR COLLEGE SCORECARD API KEY

# Find the folder containing THIS Python file.
current_folder = Path(__file__).resolve().parent

# Look for a file called ".env" in that folder.
env_path = current_folder / ".env"

# Load everything inside the .env file.
load_dotenv(dotenv_path=env_path)

# Get our College Scorecard API key.
API_KEY = os.getenv(
    "COLLEGE_SCORECARD_API_KEY"
)

# Check whether Python actually found the API key.
if not API_KEY:

    raise ValueError(
        "College Scorecard API key was not found. "
        "Make sure .env is in the same folder as this file."
    )

print(
    "\nAPI key successfully loaded!"
)



# SET UP THE COLLEGE SCORECARD API

# This is the address of the College Scorecard API.
API_URL = (
    "https://api.data.gov/ed/collegescorecard/v1/schools.json"
)


# These are the pieces of information we want the API to give us.
params = {

    # Give the API our private key.
    "api_key": API_KEY,

    # Ask for 100 colleges.
    "per_page": 100,

    # Only request the information we need.
    "fields": (
        "id,"
        "school.name,"
        "latest.admissions.admission_rate.overall,"
        "latest.admissions.sat_scores.average.overall,"
        "latest.student.size"
    )
}



# 4. DOWNLOAD REAL COLLEGE DATA

print(
    "\nConnecting to the College Scorecard API..."
)


# Send an HTTP GET request to the API.
response = requests.get(
    API_URL,
    params=params,
    timeout=20
)


# Print the status code.

# 200 = success
# 403 = forbidden
# 404 = not found
# 500 = server problem
print(
    "API Status Code:",
    response.status_code
)


# If something went wrong, stop the program and show the error.
response.raise_for_status()

print(
    "Successfully connected!"
)



# CONVERT THE API RESPONSE INTO PYTHON

# response.json() converts the JSON into something Python can understand.
data = response.json()

# The actual colleges are stored inside "results".
college_data = data.get(
    "results",
    []
)

print(
    "\nDownloaded",
    len(college_data),
    "real colleges!"
)



# TURN THE DATA INTO A PANDAS DATAFRAME

# A DataFrame is basically a spreadsheet inside Python.
df = pd.DataFrame(
    college_data
)

print(
    "\n--- RAW API DATA ---"
)

# Show the first five colleges.
print(
    df.head()
)



# RENAME THE COLUMNS

# The API gives us very long column names. Renames them so they're easier to work with.
df = df.rename(

    columns={
        "school.name":
            "college_name",

        "latest.admissions.admission_rate.overall":
            "acceptance_rate",

        "latest.admissions.sat_scores.average.overall":
            "sat_average",

        "latest.student.size":
            "student_size"
    }
)



# CLEAN THE DATA

# Some colleges might not report: SAT scores, acceptance rates, student population, etc.
df = df.dropna(

    subset=[
        "acceptance_rate",
        "sat_average",
        "student_size"
    ]
)


# College Scorecard gives acceptance rates as decimals, so multiply by 100.
df["acceptance_rate"] = (df["acceptance_rate"] * 100)

print(
    "\nUsable colleges after cleaning:",
    len(df)
)



# CREATE OUR TRAINING LABELS

# Create four broad categories using each college's reported acceptance rate.
def create_selectivity_group(acceptance_rate):

    """
    Turn an acceptance rate into
    a broad selectivity category.
    """

    # Less than 10%
    if acceptance_rate < 10:
        return "Highly Selective"

    # 10% - 29.9%
    elif acceptance_rate < 30:
        return "Selective"
    # 30% - 69.9%
    elif acceptance_rate < 70:
        return "Moderately Selective"

    # 70%+
    else:
        return "Broad Access"

# Run our function on every college.
df["selectivity_group"] = (

    df["acceptance_rate"].apply(
        create_selectivity_group
    )

)



# LOOK AT OUR CLEAN TRAINING DATA

print("\n--- CLEAN TRAINING DATA ---")

print(
    df[
        [
            "college_name",
            "acceptance_rate",
            "sat_average",
            "student_size",
            "selectivity_group"
        ]
    ].head(20)
)



# CHOOSE OUR FEATURES

# We will give the model SAT average and student population. We will NOT give it acceptance_rate because it was used to create our correct answers.
X = df[
    [
        "sat_average",
        "student_size"
    ]
]



# CHOOSE OUR TARGET

# y = TARGET
# This is the answer we want the model to learn to predict.
y = df["selectivity_group"]



# CHECK THAT WE HAVE ENOUGH DATA

if len(df) < 10:
    raise ValueError(
        "Not enough usable colleges were returned. "
        "Try requesting more data from the API."
    )



# SPLIT THE DATA

# We should NOT train and test a model using exactly the same examples. 75% = training and 25% = testing.
X_train, X_test, y_train, y_test = (
    train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42
    )
)

print(
    "\nTraining examples:",
    len(X_train)
)

print(
    "Testing examples:",
    len(X_test)
)



# CREATE OUR MACHINE LEARNING MODEL

# We are using a Decision Tree. A Decision Tree learns rules from data, we don't manually give it those rules. The model learns the splits from the training data.
model = DecisionTreeClassifier(
    # Prevent the tree from becoming unnecessarily complicated.
    max_depth=5,

    # Makes our experiment repeatable.
    random_state=42
)



# TRAIN THE MODEL

print("\nTraining the machine learning model...")

# .fit() means: LEARN FROM THE TRAINING DATA.

# X_train = information
# y_train = correct answers
model.fit(X_train, y_train)

print(
    "MODEL TRAINING COMPLETE!"
)



# TEST THE MODEL

# Give the model college information that it did NOT train on.
predictions = model.predict(X_test)

# Compare model's answers vs actual answers.
accuracy = accuracy_score(y_test, predictions)

print("\n--- MODEL TEST ---")

print(
    "Model Accuracy:",

    round(
        accuracy * 100,
        1
    ),

    "%"
)



# SHOW SOME MODEL PREDICTIONS

# Create a small table to see actual answer vs model prediction.
results = X_test.copy()

results["Actual"] = (y_test)

results["Prediction"] = (predictions)

print("\n--- SOME TEST RESULTS ---")

print(results.head(10))



# LET AARNA TEST A NEW COLLEGE

print(
    "\n=============================="
)


print(
    "      TRY YOUR OWN COLLEGE"
)


print(
    "=============================="
)


# Ask the user for the college's name.
college_name = input(

    "\nCollege name: "

)


# Ask for SAT information.
sat_average = float(

    input(
        "Average SAT score: "
    )

)


# Ask for population.
student_size = float(

    input(
        "Student population: "
    )

)



# FORMAT THE NEW COLLEGE

# The model expects the SAME features that it saw during training.
new_college = pd.DataFrame(
    [
        {
            "sat_average":
                sat_average,

            "student_size":
                student_size
        }
    ]
)



# ASK THE MODEL TO MAKE A PREDICTION

prediction = model.predict(new_college)[0]



# SHOW THE RESULT

print("\n--- AI MODEL RESULT ---")

print(college_name, "was classified as:", prediction)



# WHAT JUST HAPPENED?

print(

    """

-----------------------------------------
WHAT JUST HAPPENED?
-----------------------------------------

1. Python contacted the College Scorecard API.

2. The API sent us REAL college data.

3. Pandas organized the data.

4. We cleaned missing information.

5. We created selectivity categories.

6. We separated training and testing data.

7. Our Decision Tree learned patterns
   from the training colleges.

8. We tested it using colleges it
   had not trained on.

9. We gave it new information.

10. The trained model made a prediction.

-----------------------------------------

IMPORTANT:

This model predicts a broad COLLEGE
SELECTIVITY CATEGORY.

It does NOT predict whether an individual
student will be admitted.

-----------------------------------------
"""

)