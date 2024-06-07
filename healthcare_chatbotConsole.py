

import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Import datasets
training_dataset = pd.read_csv('Training.csv')
test_dataset = pd.read_csv('Testing.csv')
doc_dataset = pd.read_csv('doctors_dataset.csv', names=['Name', 'Description'])

# Load symptom details and synonyms data
symptoms_info = pd.read_csv('symptoms_present.csv')
symptom_synonyms = pd.read_csv('symptom_synonym.csv')

# Separate features and target variable
X = training_dataset.iloc[:, 0:132].values
y = training_dataset.iloc[:, -1].values

# Dimensionality Reduction
dimensionality_reduction = training_dataset.groupby(training_dataset['prognosis']).max()

# Encode target variable
labelencoder = LabelEncoder()
y = labelencoder.fit_transform(y)

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

# Decision Tree Classifier
classifier = DecisionTreeClassifier()
classifier.fit(X_train, y_train)

# Important features
cols = training_dataset.columns[:-1]
importances = classifier.feature_importances_

# Load doctor information
diseases = dimensionality_reduction.index
doctors = pd.DataFrame({
    'name': doc_dataset['Name'],
    'link': doc_dataset['Description'],
    'disease': diseases
})

def get_symptom_details(symptom):
    details = symptoms_info[symptoms_info['Symptom'] == symptom]
    
    if details.empty:
        synonyms = symptom_synonyms[symptom_synonyms['Synonym'] == symptom]
        
        if not synonyms.empty:
            main_symptom = synonyms['Main_Symptom'].values[0]
            details = symptoms_info[symptoms_info['Symptom'] == main_symptom]
    
    if not details.empty:
        duration = details['Duration'].values[0]
        intensity = details['Intensity'].values[0]
        return duration, intensity
    return None, None

# Execute Bot
def execute_bot():
    print("Please reply with yes/Yes or no/No for the following symptoms")

def print_disease(node):
    node = node[0]
    val = node.nonzero()
    disease = labelencoder.inverse_transform(val[0])
    return disease

def tree_to_code(tree, feature_names):
    global tree_, feature_name, symptoms_present
    tree_ = tree.tree_
    feature_name = [feature_names[i]  for i in tree_.feature]
    symptoms_present = []
    return recurse(0, 1) 

symptoms_present = []

def recurse(node, depth):
    global symptoms_present
    indent = "  " * depth
    if tree_.feature[node] != -2:  # Check if not leaf node
        name = feature_name[node]
        threshold = tree_.threshold[node]
        print(name + " ?")
        ans = input().lower()
        val = 1 if ans == 'yes' else 0

        if val <= threshold:
            recurse(tree_.children_left[node], depth + 1)
        else:
            symptoms_present.append(name)
            recurse(tree_.children_right[node], depth + 1)
    else:
        present_disease = print_disease(tree_.value[node])
        print("You may have " + present_disease[0])
        print()

        red_cols = dimensionality_reduction.columns
        symptoms_given = red_cols[dimensionality_reduction.loc[present_disease].values[0].nonzero()]
        print("Symptoms present: " + str(list(symptoms_present)))
        print("Symptoms given: " + str(list(symptoms_given)))
        print()

        confidence_level = (1.0 * len(symptoms_present)) / len(symptoms_given)
        print("Confidence level is " + str(confidence_level))
        print()

        print('The model suggests:')
        print()

        row = doctors[doctors['disease'] == present_disease[0]]
        print('Consult ', str(row['name'].values))
        print('Visit ', str(row['link'].values))

        # Additional functionality for duration or intensity
        for symptom in symptoms_present:
            duration, intensity = get_symptom_details(symptom)  
            if duration:
                print(f"The duration of {symptom} is {duration}")
            if intensity:
                print(f"The intensity of {symptom} is {intensity}")

tree_to_code(classifier, cols)
execute_bot()
