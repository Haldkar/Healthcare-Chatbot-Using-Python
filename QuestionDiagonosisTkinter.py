from tkinter import *
from tkinter import messagebox
import webbrowser
import os
import numpy as np
import pandas as pd
import spacy
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import _tree

# Import spaCy and load English model
nlp = spacy.load('en_core_web_sm')

# Load datasets
training_dataset = pd.read_csv('Testing.csv')
training_dataset = pd.read_csv('Training.csv')
doc_dataset = pd.read_csv('doctors_dataset.csv', names=['Name', 'Description'])
symptoms_info = pd.read_csv('symptoms_present.csv')
symptom_synonyms = pd.read_csv('symptom_synonym.csv')

# Data Preprocessing
X = training_dataset.iloc[:, 0:132].values
Y = training_dataset.iloc[:, -1].values
labelencoder = LabelEncoder()
y = labelencoder.fit_transform(Y)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)

classifier = DecisionTreeClassifier()
classifier.fit(X_train, y_train)

cols = training_dataset.columns[:-1]
diseases = training_dataset['prognosis'].unique()
doctors = pd.DataFrame({
    'name': doc_dataset['Name'],
    'link': doc_dataset['Description'],
    'disease': diseases
})

def print_disease(node):
    node = node[0]
    val = node.nonzero()
    disease = labelencoder.inverse_transform(val[0])
    return disease

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

def recurse(node, depth):
    global val, ans
    global tree_, feature_name, symptoms_present
    indent = " " * depth
    if tree_.feature[node] != _tree.TREE_UNDEFINED:
        name = feature_name[node]
        threshold = tree_.threshold[node]
        yield name + "?"

        ans = ans.lower()
        if ans == 'yes':
            val = 1
        else:
            val = 0
        if val <= threshold:
            yield from recurse(tree_.children_left[node], depth + 1)
        else:
            symptoms_present.append(name)
            yield from recurse(tree_.children_right[node], depth + 1)
    else:
        present_disease = print_disease(tree_.value[node])
        
        strData = "You may have: " + str(present_disease)
        QuestionDigonosis.objRef.txtDiagnosis.insert(END, str(strData) + '\n')
        
        red_cols = training_dataset.columns[:-1]
        symptoms_given = red_cols[np.mean(X_test[y_test == labelencoder.transform(present_disease)[0]], axis=0) > 0]
        
        strData = "Symptoms present: " + str(list(symptoms_present))
        QuestionDigonosis.objRef.txtDiagnosis.insert(END, str(strData) + '\n')
        
        strData = "Symptoms given: " + str(list(symptoms_given))
        QuestionDigonosis.objRef.txtDiagnosis.insert(END, str(strData) + '\n')
        
        for symptom in symptoms_present:
            duration, intensity = get_symptom_details(symptom)
            if duration:
                    strData=f"The duration of {symptom} is {duration}"
                    QuestionDigonosis.objRef.txtDiagnosis.insert(END, str(strData) + '\n')
            if intensity:
                    strData=f"The intensity of {symptom} is {intensity}"
                    QuestionDigonosis.objRef.txtDiagnosis.insert(END, str(strData) + '\n')
        
        confidence_level = (1.0 * len(symptoms_present)) / len(symptoms_given)
        
        strData = "Confidence level is: " + str(confidence_level)
        QuestionDigonosis.objRef.txtDiagnosis.insert(END, str(strData) + '\n')
        
        strData = 'The model suggests:'
        QuestionDigonosis.objRef.txtDiagnosis.insert(END, str(strData) + '\n')
        
        row = doctors[doctors['disease'] == present_disease[0]]
        strData = 'Consult ' + str(row['name'].values)
        QuestionDigonosis.objRef.txtDiagnosis.insert(END, str(strData) + '\n')
        
        hyperlink = HyperlinkManager(QuestionDigonosis.objRef.txtDiagnosis)
        strData = 'Visit ' + str(row['link'].values[0])
        def click1():
            webbrowser.open_new(str(row['link'].values[0]))
        QuestionDigonosis.objRef.txtDiagnosis.insert(INSERT, strData, hyperlink.add(click1))

        yield strData

def tree_to_code(tree, feature_names):
    global tree_, feature_name, symptoms_present
    tree_ = tree.tree_
    feature_name = [feature_names[i] for i in tree_.feature]
    symptoms_present = []
    return recurse(0, 1)

class HyperlinkManager:
    def __init__(self, text):
        self.text = text
        self.text.tag_config("hyper", foreground="blue", underline=1)
        self.text.tag_bind("hyper", "<Enter>", self._enter)
        self.text.tag_bind("hyper", "<Leave>", self._leave)
        self.text.tag_bind("hyper", "<Button-1>", self._click)
        self.reset()

    def reset(self):
        self.links = {}

    def add(self, action):
        tag = "hyper-%d" % len(self.links)
        self.links[tag] = action
        return "hyper", tag

    def _enter(self, event):
        self.text.config(cursor="hand2")

    def _leave(self, event):
        self.text.config(cursor="")

    def _click(self, event):
        for tag in self.text.tag_names(CURRENT):
            if tag[:6] == "hyper-":
                self.links[tag]()
                return

class QuestionDigonosis(Frame):
    objIter = None
    objRef = None
    
    def __init__(self, master=None):
        master.title("Question")
        master.state("z")
        QuestionDigonosis.objRef = self
        super().__init__(master)  # Corrected this line
        self["bg"] = "light grey"
        self.createWidget()
        self.iterObj = None

    def createWidget(self):
        bg_color = "light grey"
        label_bg = "dark grey"
        button_bg = "sky blue"
        button_fg = "black"
        font = ("Arial", 12)
        
        
        self.lblQuestion = Label(self, text="Question", width=12, bg=label_bg, font=font)
        self.lblQuestion.grid(row=0, column=0, rowspan=4, pady=10)

        self.lblDigonosis = Label(self, text="Diagnosis", width=12, bg=label_bg, font=font)
        self.lblDigonosis.grid(row=4, column=0, sticky="n", pady=5)

        self.txtQuestion = Text(self, width=100, height=4, bg=bg_color, font=font, bd=3)
        self.txtQuestion.grid(row=0, column=1, rowspan=4, columnspan=20, pady=10)

        self.txtDiagnosis = Text(self, width=100, height=14, bg=bg_color, font=font, bd=3)
        self.txtDiagnosis.grid(row=4, column=1, columnspan=20, rowspan=20, pady=5)
        
        self.btnNo = Button(self, text="No", width=12, bg=button_bg, fg=button_fg, font=font, relief=RAISED, bd=3, command=self.btnNo_Click)
        self.btnNo.grid(row=25, column=0, pady=10)
        
        self.btnYes = Button(self, text="Yes", width=12, bg=button_bg, fg=button_fg, font=font, relief=RAISED, bd=3, command=self.btnYes_Click)
        self.btnYes.grid(row=25, column=1, columnspan=20, sticky="e", pady=10)
        
        self.btnClear = Button(self, text="Clear", width=12, bg=button_bg, fg=button_fg, font=font, relief=RAISED, bd=3, command=self.btnClear_Click)
        self.btnClear.grid(row=27, column=0, pady=10)
        
        self.btnStart = Button(self, text="Start", width=12, bg=button_bg, fg=button_fg, font=font, relief=RAISED, bd=3, command=self.btnStart_Click)
        self.btnStart.grid(row=27, column=1, columnspan=20, sticky="e", pady=10)

    def btnYes_Click(self):
        global val, ans
        ans = 'yes'
        str1 = next(QuestionDigonosis.objIter, None)
        if str1 is not None:
            self.txtQuestion.delete(0.0, END)
            self.txtQuestion.insert(END, str1 + "\n")

    def btnNo_Click(self):
        global val, ans
        ans = 'no'
        str1 = next(QuestionDigonosis.objIter, None)
        if str1 is not None:
            self.txtQuestion.delete(0.0, END)
            self.txtQuestion.insert(END, str1 + "\n")

    def btnClear_Click(self):
        self.txtDiagnosis.delete(0.0, END)
        self.txtQuestion.delete(0.0, END)

    def btnStart_Click(self):
        global ans
        ans = ""
        self.txtDiagnosis.delete(0.0, END)
        self.txtQuestion.delete(0.0, END)
        self.txtDiagnosis.insert(END, "Please Click on Yes or No for the Above symptoms in Question\n")
        QuestionDigonosis.objIter = tree_to_code(classifier, cols)
        str1 = QuestionDigonosis.objIter.__next__()
        self.txtQuestion.insert(END, str1 + "\n")

class MainForm(Frame):
    main_Root = None
    def destroyPackWidget(self, parent):
        for e in parent.pack_slaves():
            e.destroy()
    
    def __init__(self, master=None):
        MainForm.main_Root = master
        super().__init__(master=master)
        master.geometry("300x250")
        master.title("Account Login")
        self.createWidget()
    
    def createWidget(self):
        self.lblMsg = Label(self, text="Health Care Chatbot", bg="sky blue", fg="white", width="300", height="2", font=("Arial", 13))
        self.lblMsg.pack(pady=10)
        
        self.btnLogin = Button(self, text="Login", height="2", width="30", bg="light grey", fg="black", font=("Arial", 12), relief=RAISED, bd=3, command=self.lblLogin_Click)
        self.btnLogin.pack(pady=10)
        
        self.btnRegister = Button(self, text="Register", height="2", width="30", bg="light grey", fg="black", font=("Arial", 12), relief=RAISED, bd=3, command=self.btnRegister_Click)
        self.btnRegister.pack(pady=10)
        
    def lblLogin_Click(self):
        self.destroyPackWidget(MainForm.main_Root)
        frmLogin = Login(MainForm.main_Root)
        frmLogin.pack()
    
    def btnRegister_Click(self):
        self.destroyPackWidget(MainForm.main_Root)
        frmSignUp = SignUp(MainForm.main_Root)
        frmSignUp.pack()

class Login(Frame):
    main_Root = None
    def destroyPackWidget(self, parent):
        for e in parent.pack_slaves():
            e.destroy()
    
    def __init__(self, master=None):
        Login.main_Root = master
        super().__init__(master=master)
        master.title("Login")
        master.geometry("300x250")
        self.createWidget()
    
    def createWidget(self):
        self.lblMsg = Label(self, text="Please enter details below to login", bg="sky blue", fg="white", font=("Arial", 12))
        self.lblMsg.pack(pady=10)
        
        self.username = Label(self, text="Username * ", bg="sky blue", fg="white", font=("Arial", 12))
        self.username.pack()
        self.username_verify = StringVar()
        self.username_login_entry = Entry(self, textvariable=self.username_verify, bg="light grey", font=("Arial", 12))
        self.username_login_entry.pack(pady=10)
        
        self.password = Label(self, text="Password * ", bg="sky blue", fg="white", font=("Arial", 12))
        self.password.pack()
        self.password_verify = StringVar()
        self.password_login_entry = Entry(self, textvariable=self.password_verify, show='*', bg="light grey", font=("Arial", 12))
        self.password_login_entry.pack(pady=10)
        
        self.btnLogin = Button(self, text="Login", width=10, height=1, bg="sky blue", fg="white", font=("Arial", 12), relief=RAISED, bd=3, command=self.btnLogin_Click)
        self.btnLogin.pack()

    def btnLogin_Click(self):
        username1 = self.username_login_entry.get()
        password1 = self.password_login_entry.get()
        
        list_of_files = os.listdir()
        if username1 in list_of_files:
           
        
            file1 = open(username1, "r")
            verify = file1.read().splitlines()
            if password1 in verify:
                messagebox.showinfo("Success", "Login Successful")
                self.destroyPackWidget(Login.main_Root)
                frmQuestion = QuestionDigonosis(Login.main_Root)
                frmQuestion.pack()
            else:
                messagebox.showinfo("Failure", "Login Details are wrong, try again")
        else:
            messagebox.showinfo("Failure", "User not found, try from another user or sign up for a new user")

class SignUp(Frame):
    main_Root = None
    print("SignUp Class")
    
    def destroyPackWidget(self, parent):
        for e in parent.pack_slaves():
            e.destroy()
    
    def __init__(self, master=None):
        SignUp.main_Root = master
        master.title("Register")
        super().__init__(master=master)
        master.geometry("300x250")
        self.createWidget()
    
    def createWidget(self):
        self.lblMsg = Label(self, text="Please enter details below", bg="sky blue", fg="white", font=("Arial", 12))
        self.lblMsg.pack(pady=10)
        
        self.username_lable = Label(self, text="Username * ", bg="sky blue", fg="white", font=("Arial", 12))
        self.username_lable.pack()
        self.username = StringVar()
        self.username_entry = Entry(self, textvariable=self.username, bg="light grey", font=("Arial", 12))
        self.username_entry.pack(pady=10)
        
        self.password_lable = Label(self, text="Password * ", bg="sky blue", fg="white", font=("Arial", 12))
        self.password_lable.pack()
        self.password = StringVar()
        self.password_entry = Entry(self, textvariable=self.password, show='*', bg="light grey", font=("Arial", 12))
        self.password_entry.pack(pady=10)
        
        self.btnRegister = Button(self, text="Register", width=10, height=1, bg="sky blue", fg="white", font=("Arial", 12), relief=RAISED, bd=3, command=self.register_user)
        self.btnRegister.pack(pady=10)
        
    def register_user(self):
        file = open(self.username_entry.get(), "w")
        file.write(self.username_entry.get() + "\n")
        file.write(self.password_entry.get())
        file.close()
        
        self.destroyPackWidget(SignUp.main_Root)
        
        self.lblSuccess = Label(root, text="Registration Success", fg="green", font=("Arial", 11))
        self.lblSuccess.pack()
        
        self.btnSuccess = Button(root, text="Click Here to proceed", command=self.btnSuccess_Click)
        self.btnSuccess.pack()
    
    def btnSuccess_Click(self):
        self.destroyPackWidget(SignUp.main_Root)
        frmQuestion = QuestionDigonosis(SignUp.main_Root)
        frmQuestion.pack()

# Main code to start the GUI
root = Tk()
frmMainForm = MainForm(root)
frmMainForm.pack()
root.mainloop()
