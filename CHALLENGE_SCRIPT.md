# ScholarScore — Congressional App Challenge Script

Hi, my name is Aarna, and I created ScholarScore, a college-planning application designed to help high school students organize and understand their college-readiness profile.

College planning can be overwhelming because students are thinking about academics, course rigor, extracurricular activities, leadership, community service, awards, essays, and college research at the same time. I wanted to bring those pieces into one understandable dashboard.

ScholarScore first lets a student build a profile. The app uses a transparent scoring system to organize academics, involvement, achievements, and a basic text analysis of the student's short personal statement. The result is a readiness score out of 100. It is not an admission probability; it is a planning tool that helps a student see the different parts of their profile together.

I also added a machine-learning component. ScholarScore connects to the U.S. Department of Education College Scorecard API and downloads real public college data. I use Pandas to clean and organize that data. Then I split it into training and testing sets and train a Decision Tree classifier with scikit-learn.

For the classroom model, reported acceptance rate is used to create broad selectivity labels. Because acceptance rate creates the correct label, I intentionally do not give acceptance rate to the model as an input feature. Instead, the model studies average SAT score and student population. This avoids giving the model the answer directly, which is an example of preventing data leakage.

On the website, a student can search a college. The Flask backend requests its public College Scorecard information and sends the appropriate features to the trained model. The page then displays the college's public data and the model's broad selectivity classification.

Technically, I built ScholarScore using Python and Flask for the backend, HTML, CSS, and JavaScript for the frontend, the College Scorecard API for public data, Pandas for data processing, and scikit-learn for machine learning.

One of the biggest things I learned from this project is that responsible AI is not only about getting a prediction. You need to understand where the data comes from, clean it, separate training data from testing data, avoid data leakage, measure model performance, and clearly explain the limitations of the result.

In the future, I would like to add saved profiles, side-by-side college comparisons, intended-major information, more College Scorecard features, stronger model evaluation, and a larger dataset.

ScholarScore's goal is to make college planning feel more organized, understandable, and useful for students.

## Demo order
1. Show the homepage.
2. Enter a student profile.
3. Add sample colleges and generate ScholarScore.
4. Explain the readiness score is not an admission probability.
5. Scroll to the Machine Learning section.
6. Search a real college.
7. Show the API data and Decision Tree classification.
8. Explain: College Scorecard API → Pandas → clean data → train/test split → Decision Tree → classification.
9. End with what Aarna learned and future improvements.
