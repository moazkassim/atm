from tkinter import *
from PIL import ImageTk, Image
import tkinter.messagebox
from tkinter import simpledialog
import os
import datetime
import re
import random
import sqlite3

def registration_table():
    db=sqlite3.connect("ATMdatabase.db")
    cr=db.cursor()
    cr.execute("""CREATE Table Registration_data(
        Name text,
        gender text,
        age text,
        dob integer,
        Mobile_No text,
        No_of_nothonal_card integer,
        username text,
        Account_number integer,
        PIN integer
    )""")
    db.commit()
    db.close()

def transation_table():
    db=sqlite3.connect("ATMdatabase.db")
    cr=db.cursor()
    cr.execute(""" CREATE TABLE Transactions_data(
    username text
    account_balance integer
    Transaction text
    )
    """)
    db.commit()
    db.close()

root = Tk()
root.geometry('700x500')
root.resizable(1, 1)

global account_userName
account_userName = StringVar()

def transaction_init():
    global account_userName
    username = account_userName.get()
    acBal = 0
    time_now = datetime.datetime.now().strftime("%Y/%m/%d %H-%M-%S")
    transactions = f"{time_now}: 0 Account Created|"
    con = sqlite3.connect("ATMdatabase.db")
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO transaction_data VALUES (?,?,?)", (username, acBal, transactions))
        # allready Created Table, data Added
    except sqlite3.OperationalError:
        # Not created!! Now Creating
        create_transation_table()
        cur.execute("INSERT INTO transaction_data VALUES (?,?,?)", (username, acBal, transactions))
    con.commit()
    con.close()


def check_user_exist(un):
    con = sqlite3.connect("ATMdatabase.db")
    cur = con.cursor()
    try:
        cur.execute("SELECT username from Registration_data")
        li = cur.fetchall()
        li = [i for i in li if i[0] == un]
        return len(li)
    except:
        pass

def get_balance(username):
    con = sqlite3.connect("ATMdatabase.db")
    cur = con.cursor()
    try:
        cur.execute("SELECT account_balance from transaction_data WHERE username=?", (username,))
        balance = cur.fetchone()

        return balance[0]
    except TypeError:
        pass


def balanceEnq():
    global account_userName
    bal = get_balance(account_userName.get())
    tkinter.messagebox.showinfo(title=f"Account Balance for {account_userName.get()}",
                                message=f"Your current Balance is egpound. {bal}")

    # accnum = Label( text=f'Balance is {bal} LE', bg="#0B3A97", fg="white", font='serif 14 bold')
    # accnum.place(x=25, y=320)



def get_PIN(username):
    con = sqlite3.connect("ATMdatabase.db")
    cur = con.cursor()
    try:
        cur.execute("SELECT PIN FROM Registration_data WHERE username=?", (username,))
        return cur.fetchone()[0]
    except sqlite3.OperationalError:
        pass
    con.close()


def changePIN():
    global account_userName
    username = account_userName.get()
    curPIN = simpledialog.askinteger(title="Change PIN STEP 1/2", prompt="Current PIN:")
    dbPIN = get_PIN(username)

    if curPIN != None:
        if curPIN == dbPIN:
            newPIN = simpledialog.askinteger(title="Change PIN STEP 2/2", prompt="New PIN:")

            con = sqlite3.connect("ATMdatabase.db")
            cur = con.cursor()

            cur.execute("UPDATE Registration_data set PIN = ?  WHERE username=?", (newPIN, username))

            con.commit()
            con.close()
            tkinter.messagebox.showinfo(title="Successful", message="PIN Changed Successfully")
        else:
            tkinter.messagebox.showwarning(title="Error", message="Entered PIN is Wrong")


def mini_statement():
    global account_userName
    username = account_userName.get()
    con = sqlite3.connect("ATMdatabase.db")
    cur = con.cursor()
    cur.execute("SELECT transactions FROM transaction_data WHERE username=?", (username,))
    transactions = cur.fetchone()[0]

    transaction_list = transactions.split('|')  # element for list split by |
    transaction_list = transaction_list[:-1]  # removing last empty Element

    mini_state = f"Mini Statement of {username}:\n"
    for item in transaction_list:
        mini_state += item + "\n"
    time_now = datetime.datetime.now().strftime("%Y/%m/%d %H-%M-%S")
    mini_state += f"Clear Balance egpound.{get_balance(username)}-as on {time_now}"
    tkinter.messagebox.showinfo(title="Mini Statement", message=mini_state)


def cash_depo():
    global account_userName
    username = account_userName.get()

    amount_to_add = simpledialog.askinteger(title="Cash Deposit", prompt="Enter Amount:")

    if amount_to_add != None:
        con = sqlite3.connect("ATMdatabase.db")
        cur = con.cursor()
        # get current account balance
        cur_bal = get_balance(account_userName.get())

        # update account balance
        updated_bal = cur_bal + amount_to_add
        cur.execute("UPDATE transaction_data set account_balance = ?  WHERE username=?", (updated_bal, username))

        ##Create Transaction Detail###################
        time_now = datetime.datetime.now().strftime("%Y/%m/%d %H-%M-%S")
        current_transaction = f"{time_now}: {amount_to_add} Cr|"
        cur.execute("SELECT transactions FROM transaction_data WHERE username = ?", (username,))
        past_transaction = cur.fetchone()  # fetching old transactions
        updated_transaction = past_transaction[0] + current_transaction
        cur.execute("UPDATE transaction_data SET transactions = ? WHERE username = ?", (updated_transaction, username))
        #####################

        con.commit()
        con.close()
        # tkinter.messagebox.showinfo(title="Successful", message="Amount added Successfully")


        accnum = Label(text=f'{updated_bal} LE', bg="#0B3A97", fg="white", font='serif 14 bold')
        accnum.place(x=25, y=220)


def cach_withdrawl():
    global account_userName
    username = account_userName.get()
    amount_to_withdrawl = simpledialog.askinteger(title="Cash Withdrawl", prompt="Enter Amount:")
    con = sqlite3.connect("ATMdatabase.db")
    cur = con.cursor()
    # get current account balance
    cur_bal = get_balance(account_userName.get())
    # update account balance
    try:
        if cur_bal < amount_to_withdrawl:
            tkinter.messagebox.showwarning(title="Error", message="insufficient Balance")
        else:
            updated_bal = cur_bal - amount_to_withdrawl
            cur.execute("UPDATE transaction_data set account_balance = ?  WHERE username=?", (updated_bal, username))
            ##Create Transaction Detail###################
            time_now = datetime.datetime.now().strftime("%Y/%m/%d %H-%M-%S")
            current_transaction = f"{time_now}: {amount_to_withdrawl} Dr|"
            cur.execute("SELECT transactions FROM transaction_data WHERE username = ?", (username,))
            past_transaction = cur.fetchone()  # fetching old transactions
            updated_transaction = past_transaction[0] + current_transaction
            cur.execute("UPDATE transaction_data SET transactions = ? WHERE username = ?",
                        (updated_transaction, username))
            #####################
            con.commit()
            con.close()
            accnum = Label(text=f'{updated_bal} LE', bg="#0B3A97", fg="white", font='serif 14 ')
            accnum.place(x=25, y=220)

    except TypeError:
        pass


def transfer():
    global account_userName
    receiver_username = simpledialog.askstring(title="Cash Transfer STEP 1/2", prompt="Username of receiver:")
    if receiver_username != None:

        if check_user_exist(receiver_username) == 0:
            tkinter.messagebox.showwarning(title="Error", message="Account Not Found")

        else:
            sending_amount = simpledialog.askinteger(title="Cash Transfer STEP 1/2",
                                                     prompt="Enter Amount to be transfer:")

            SenderUserName = account_userName.get()
            sender_cur_bal = get_balance(account_userName.get())
            receiver_cur_bal = get_balance(receiver_username)

            try:
                if sending_amount > sender_cur_bal:
                    tkinter.messagebox.showwarning(title="Error", message="insufficient Balance")
                else:
                    sender_updated_amount = sender_cur_bal - sending_amount
                    receiver_updated_amount = receiver_cur_bal + sending_amount

                    con = sqlite3.connect("ATMdatabase.db")
                    cur = con.cursor()
                    cur.execute("UPDATE transaction_data set account_balance = ?  WHERE username=?",
                                (sender_updated_amount, SenderUserName))
                    cur.execute("UPDATE transaction_data set account_balance = ?  WHERE username=?",
                                (receiver_updated_amount, receiver_username))
                    ##########################################################
                    ##Sender Transaction Detail###################
                    time_now = datetime.datetime.now().strftime("%Y/%m/%d %H-%M-%S")
                    sender_current_transaction = f"{time_now}: {sending_amount} Dr Transferred To {receiver_username}|"
                    cur.execute("SELECT transactions FROM transaction_data WHERE username = ?", (SenderUserName,))
                    sender_past_transaction = cur.fetchone()  # fetching old transactions
                    sender_updated_transaction = sender_past_transaction[0] + sender_current_transaction
                    cur.execute("UPDATE transaction_data SET transactions = ? WHERE username = ?",
                                (sender_updated_transaction, SenderUserName))
                    #####################
                    ##Receiver Transaction Detail###################
                    receiver_current_transaction = f"{time_now}: {sending_amount} Cr Transaferred From {SenderUserName}|"
                    cur.execute("SELECT transactions FROM transaction_data WHERE username = ?", (receiver_username,))
                    receiver_past_transaction = cur.fetchone()  # fetching old transactions
                    receiver_updated_transaction = receiver_past_transaction[0] + receiver_current_transaction
                    cur.execute("UPDATE transaction_data SET transactions = ? WHERE username = ?",
                                (receiver_updated_transaction, receiver_username))
                    #####################
                    ##########################################################
                    con.commit()
                    con.close()
                    tkinter.messagebox.showinfo(title="Successful", message="Amount Transferred Successfully")
            except TypeError:
                pass


def generateAcNo(e):
    acNo = random.randint(11111111, 99999999)
    e.delete(0, END)
    e.insert(0, acNo)


def check_acNo_exist(un):
    con = sqlite3.connect("ATMdatabase.db")
    cur = con.cursor()
    try:
        cur.execute("SELECT Account_number from Registration_data")
        li = cur.fetchall()

        un = int(un)
        li = [i for i in li if i[0] == un]
        return len(li)
    except:
        pass


def login(e1, e2):
    global account_userName
    username = e1.get()
    password = e2.get()

    if "" in (username, password):
        tkinter.messagebox.showerror('Error Message', 'Missing fields')
    else:
        try:
            dbPass = get_PIN(username)
            if password == str(dbPass):
                # tkinter.messagebox.showinfo('Successful', 'Login Successfully')
                account_userName.set(username)
                main_window()
            else:
                tkinter.messagebox.showerror('Error Message', 'Invalid Username/PIN')
        except:
            tkinter.messagebox.showerror('Error Message', 'Invalid Username/PIN')


def registration_data(en1, en2, en3, en4, en5, en6, en7, en8):
    global account_userName
    pin = random.randint(1111, 9999)
    name = en1.get()

    gender = en2.get()
    if gender == 1:
        gender = "Male"
    elif gender == 2:
        gender = "Female"


    age = en3.get()
    dob = en4.get()
    cNo = en5.get()
    AdharNo = en6.get()
    Username = en7.get()
    acNo = en8.get()

    if "" in (name, gender, age, dob, cNo, AdharNo, Username, acNo):
        tkinter.messagebox.showerror(title="error", message="Missing Fields")
    else:
        try:
            age = int(age)
            if age < 10:
                tkinter.messagebox.showerror(title="Error", message=f"You are Underage! Wait for {10 - age} years.")
                return
            else:
                if len(cNo) == 11:
                    try:
                        cNo = int(cNo)
                    except ValueError:
                        tkinter.messagebox.showerror(title="Error", message="Mobile Number is invalid")

                    if len(AdharNo) == 14:
                        try:
                            cNo = int(cNo)
                        except ValueError:
                            tkinter.messagebox.showerror(title="Error", message="NIC Number is invalid")
                            return

                        if check_user_exist(Username) == 1:
                            tkinter.messagebox.showerror(title="Error", message="Username is already Exist. Try New!")
                            return
                        if check_acNo_exist(acNo) == 1:
                            tkinter.messagebox.showerror(title="Error",
                                                         message="Account Number already Exist. Try New!")
                            return

                        else:
                            account_userName.set(Username)
                            # Database
                            con = sqlite3.connect("ATMdatabase.db")
                            cur = con.cursor()
                            try:
                                cur.execute("INSERT INTO Registration_data VALUES (?,?,?,?,?,?,?,?,?)",
                                            (name, gender, age, dob, cNo, AdharNo, Username, acNo, pin))
                                # allready Created Table, data Added
                            except sqlite3.OperationalError:
                                # Not created!! Now Creating
                                create_registration_table()
                                cur.execute("INSERT INTO Registration_data VALUES (?,?,?,?,?,?,?,?,?)",
                                            (name, gender, age, dob, cNo, AdharNo, Username, acNo, pin))
                            con.commit()
                            con.close()
                            tkinter.messagebox.showinfo(title="Successful",
                                                        message=f"Account has been created. You PIN is {pin}")
                            transaction_init()
                            Home()

                    else:
                        tkinter.messagebox.showerror(title="Error", message="NIC Number is invalid")
                        return
                else:
                    tkinter.messagebox.showerror(title="Error", message="Mobile Number is invalid")

        except ValueError:
            tkinter.messagebox.showerror(title="Error", message="Age is invalid")



def RegistrationWindow():
    varGen = IntVar()  # Gender Variable

    # ______FRAME___________
    signUpFrame = Frame(root, width=700, height=500)
    signUpFrame.place(x=0, y=0)
    root.title("Registration")

    # ______Putting image on label_______________
    img = ImageTk.PhotoImage(Image.open('D:/programming/myWork/python/kandilAtm/s.jpeg'))
    lbImg = Label(signUpFrame, bg='#01b4f5', width=700, height=500, image=img)
    lbImg.place(x=0, y=0)
    # ____Welcome Message Label___________
    lbIntr = Label(signUpFrame, width=20, text='Registration Form', fg="white", font='Helvetica 18 ', bg="#01b4f5")
    lbIntr.place(x=150, y=20)

    # # ____LABELS________________________

    enAcNo = Entry(width=14, font='Helvetica 12', bd=0)
    enAcNo.place(x=300, y=370)

    ##change Ac number Button
    getNewAcNo = Button(text="Get New", width=7,bg='#01b4f5',bd=0,fg='white', font="arial 8 bold", command=lambda: generateAcNo(enAcNo))
    getNewAcNo.place(x=440, y=370)

    lbName = Label(signUpFrame, width=11, text='Name', fg="white", font='Helvetica 12 bold',bg = "#051c51")
    lbName.place(x=110, y=90)

    lbGen = Label(signUpFrame, width=11, text='Gender', fg="white", font='Helvetica 12 bold',bg = "#051c51")
    lbGen.place(x=110, y=130)

    lbAge = Label(signUpFrame, width=11, text='Age', fg="white", font='Helvetica 12 bold',bg = "#051c51")
    lbAge.place(x=110 , y=170)

    lbDob = Label(signUpFrame, width=11, text='Date of Birth', fg="white", font='Helvetica 12 bold',bg = "#051c51")
    lbDob.place(x=110, y=210)

    lbCont = Label(signUpFrame, width=11, text="Mobile No", fg="white", font='Helvetica 12 bold',bg = "#051c51")
    lbCont.place(x=110, y=250)

    lbAdhar = Label(signUpFrame, width=11, text="NIC No", fg="white", font='Helvetica 12 bold',bg = "#051c51")
    lbAdhar.place(x=110, y=290)

    lblUsername = Label(signUpFrame, width=11, text="User Name", fg="white", font='Helvetica 12 bold',bg = "#051c51")
    lblUsername.place(x=110, y=330)

    lblAcNumber = Label(signUpFrame, width=11, text="Account No", fg="white", font='Helvetica 12 bold', bg="#051c51")
    lblAcNumber.place(x=110, y=370)

    # # ______Entries_______
    enName = Entry(width=21, font='Helvetica 12', bd=0)
    enName.place(x=300, y=90)

    ##REDIO Buttons_____________________________________________

    genRadioMale = Radiobutton(text="Male", font='Helvetica 8', variable=varGen, value=1)
    genRadioMale.place(x=300, y=130)

    genRadioFemale = Radiobutton(text="Female", font='Helvetica 8', variable=varGen, value=2)
    genRadioFemale.place(x=360, y=130)


    # ######################_________________________________

    enAge = Entry(width=21, font='Helvetica 12', bd=0)
    enAge.place(x=300, y=170)

    enDob = Entry(width=21, font='Helvetica 12', bd=0)
    enDob.place(x=300, y=210)

    enCno = Entry(width=21, font='Helvetica 12', bd=0)
    enCno.place(x=300, y=250)

    enAdhar = Entry(width=21, font='Helvetica 12', bd=0)
    enAdhar.place(x=300, y=290)

    enUsername = Entry(width=21, font='Helvetica 12', bd=0)
    enUsername.place(x=300, y=330)

    #  __Button___________
    # Submit Button

    submitButton = Button(text="Submit", width=10,bg='#01b4f5',bd=0,fg='white', font="arial 10 bold",
                          command=lambda: registration_data(enName, varGen, enAge, enDob, enCno, enAdhar, enUsername,
                                                            enAcNo))
    submitButton.place(x=150, y=440)

    # Reset Button
    resetButton = Button(text="Reset", width=10,bg='#01b4f5',bd=0,fg='white', font="arial 10 bold", command=RegistrationWindow)
    resetButton.place(x=250, y=440)

    BackButton = Button(text="Back", width=10,bg='#01b4f5',bd=0,fg='white', font="arial 10 bold", command=Home)
    BackButton.place(x=350, y=440)

    signUpFrame.mainloop()


# Window after login
def main_window():
    global account_userName

    root.geometry('700x500')
    f1 = Frame(root, width=700, height=500, bg="#0B3A97")
    f1.place(x=0, y=0)
    root.title("ATM")


    # # ______Putting image on label_______________


    atmlab = Label(text='ATM',fg="white", width=3,bg = "#0B3A97", font='Amasis 20 bold')
    atmlab.place(x=20, y=20)

    cardlab = Label(text='Card Return <>',fg="white", width=20,bg = "#0B3A97", font='serif 10 bold')
    cardlab.place(x=525, y=20)

                    # welcome message
    wellab = Label(f1,text='Welcome', bg="#0B3A97", fg="#01B4F5", font='serif 10 ')
    wellab.place(x=20, y=130)

    lblWel = Label(f1, text=f'{account_userName.get()}', bg="#0B3A97", fg="white", font='serif 12 bold')
    lblWel.place(x=25, y=150)

                                # account balance

    acclab = Label(text='Account Balance',fg="#01B4F5",bg = "#0B3A97", font='serif 10 ')
    acclab.place(x=20, y=190)
    accnum = Label(text=f'{get_balance(account_userName.get())} LE', bg="#0B3A97", fg="white", font='serif 14 bold')
    accnum.place(x=25, y=220)
                                            # operations buttons


    btnBal = Button(f1, width=18, height=3,text='Balance Enquiry', highlightthickness = 0, borderwidth=0,  bg="#01B4F5", fg="white", font='serif 14 ',
               command=balanceEnq)
    btnBal.place(x=240, y=120)

    btnMiniStat = Button(f1, width=18,height=3, text='Mini Statement',highlightthickness = 0, borderwidth=0, fg="white", font='serif 14 ', bg="#01B4F5",
                          command=mini_statement)
    btnMiniStat.place(x=460, y=120)

    btnPINChange = Button(f1, width=18,height=3, text='Change PIN',highlightthickness = 0, borderwidth=0, fg="white", font='serif 14 ', bg="#01B4F5",
                          command=changePIN)
    btnPINChange.place(x=240, y=210)

    btnWithdral = Button(f1, width=18,height=3, text='Cash Withdrawl',highlightthickness = 0, borderwidth=0,fg="white", font='serif 14 ', bg="#01B4F5",
                          command=cach_withdrawl)
    btnWithdral.place(x=460, y=210)

    btnDeposit = Button(f1, width=18,height=3, text='Cash Deposit',highlightthickness = 0, borderwidth=0, fg="white", font='serif 14 ', bg="#01B4F5",
                         command=cash_depo)
    btnDeposit.place(x=240, y=300)

    btnTrans = Button(f1, width=18,height=3, text='Cash Transfer',highlightthickness = 0, borderwidth=0, fg="white", font='serif 14 ', bg="#01B4F5",
                      command=transfer)
    btnTrans.place(x=460, y=300)

    LogoutBTN = Button(f1, width=35,height=2, text='Logout', fg="white",highlightthickness = 0 , borderwidth=0,font='serif 14 bold ', bg="#F6006B",
                       command=Home)
    LogoutBTN.place(x=240, y=400)

    f1.mainloop()
# _ Home window ____________________________________________________
def Home():
    # Creating main window Frame
    mainFrame = Frame(root, height=500, width=700)
    mainFrame.place(x=0, y=0)
    # image Labeling
    img = ImageTk.PhotoImage(Image.open("D:/programming/myWork/python/kandilAtm/home.jpg"))
    labelForImage = Label(mainFrame, height=500, width=700,image=img)
    labelForImage.place(x=0, y=0)
    lblIntro = Label(mainFrame, text='Welcome To MFK ATM',fg="white", width=17, height=1, bg = "#030D88", font='serif 18 bold')
    lblIntro.place(x=160, y=80)
    atmlb = Label(mainFrame, text='ATM',fg="white", width=3, height=0, bg = "#030D88", font='serif 18 bold')
    atmlb.place(x=30, y=20)

    # LABELS
    # label for AC Number
    lblAcNo = Label(mainFrame, text='User Name',fg="white", width=8,bg = "#030D88", font='serif 14')
    lblAcNo.place(x=140, y=190)
    # label for PIN
    lblPIN = Label(mainFrame, text='PIN',fg="white", width=3,bg = "#030D88", font='serif 14')
    lblPIN.place(x=140, y=250)
    enUser = Entry(width=20, font='serif 12', bd=0)
    enUser.place(x=270, y=190)
    # Entry For password
    enPass = Entry(width=20, font='serif 12', bd=0, show="*")
    enPass.place(x=270, y=250)
    # _____Buttons_________________________________
    # login Button
    loginButton = Button(text="Login", width=10,fg="white",bg="#04aa6d",bd=0, font="serif 10 bold", command=lambda: login(enUser, enPass))
    loginButton.place(x=180, y=340)
    # SignUp Button
    signupButton = Button(text="Register New User",fg="white",bg="#04aa6d", bd=0,width=15, font="serif 10 bold",command=RegistrationWindow)
    signupButton.place(x=280, y=340)
    mainFrame.mainloop()
Home()
