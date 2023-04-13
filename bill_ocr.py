"""
Author: Sarthak Pradhan
Date: 04/04/2023
Description: function to scan and bill and create elements that can be put into buckets for the convenience of splitting
"""
import argparse
from tkinter.ttk import Combobox
import pandas as pd
import cv2
import numpy as np
import pytesseract
import uuid
import nltk
import imutils
from imutils.perspective import four_point_transform
import re
from nltk import word_tokenize, pos_tag, ne_chunk
from tkinter import *
from tkinter import messagebox, filedialog

# Load the Tesseract OCR engine
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Replace with the path to your Tesseract OCR executable


def process_image(image):
    # Perform image processing on the uploaded image
    image = ~image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Rest of the image processing code

    # Perform OCR using Tesseract
    my_config = r"--psm 6 oem 3"
    text = pytesseract.image_to_string(gray, config=my_config)

    # Extract text and return the result as a dictionary
    lines = text.split('\n')
    pricePattern = r'([0-9]+\.[0-9]+)'

    # Loop through each line of text and filter out line items
    for row in text.split('\n'):
        if re.search(pricePattern, row) is not None:
            break
        else:
            lines.remove(row)
    lines = list(filter(None, lines))
    pattern = r"^(.*?)\s+\$?([\d.]+)"

    # Initialize dictionary to store results
    result_dict = {}

    # Loop through input list
    for item in lines:
        # Search for pattern in item
        try:
            match = re.search(pattern, item)
            if match:
                text = match.group(1)
                if "." in match.group(2):
                    # If the string contains a dot, it's a float
                    number = float(match.group(2))
                else:
                    # If the string doesn't contain a dot, it's an integer
                    number = int(match.group(2)) / 100
                result_dict[text] = number
        except Exception:
            pass

    # Return the resulting dictionary
    print(result_dict)
    result_dict = pd.DataFrame(list(result_dict.items()), columns=['Item', 'Price'])
    result_dict['copy_index'] = result_dict.index
    print(result_dict)
    return result_dict


def main():
    # Create the GUI window
    root = Tk()
    root.title("Bill Split root")
    root.geometry('700x350')

    bill_elements = {}
    each_user_items = []

    def open_image():
        # Open a file dialog to choose an image file
        file_path = filedialog.askopenfilename()
        if file_path:
            image = cv2.imread(file_path)
            result_dict = process_image(image)
            # Display the result in a message box or update the UI with the extracted text
            # For example:
            global bill_elements
            bill_elements = result_dict

    def open_bill_split_window():
        global bill_elements
        # print(bill_elements)

        no_users = int(combobox.get())

        global each_user_items
        each_user_items = []
        for j in range(no_users):
            each_user_items.append(pd.DataFrame(columns=['Item', 'Price', 'copy_index']))

        '''All GUI elements of bill split window start'''
        page2_window = Toplevel(root)
        # Parts List (Listbox)

        def update_bill_gui():
            global bill_elements
            bill_elements_list_box.delete(0, END)
            for index, row in bill_elements.iterrows():
                bill_elements_list_box.insert(index, str(index) + ") " + str(row["Item"]) + "-$" + str(row["Price"]))
        def update_user_bill_gui():
            global each_user_items
            for j in range(no_users):
                each_user_items_listbox[j].delete(0, END)
                for index, row in each_user_items[j].iterrows():
                    each_user_items_listbox[j].insert(END, str(row["Item"]) + "-$" + str(row["Price"]))
                each_user_items_label_total[j]["text"] = "Total $" + str(sum(each_user_items[j]["Price"].values))

        bill_elements_list_box = Listbox(page2_window, border=3)
        update_bill_gui()
        bill_elements_list_box.pack()

        def on_main_listbox_select(event):
            # Function to handle Listbox selection
            show_checkboxes()

        def on_user_listbox_select(event):
            global each_user_items

            # Function to handle Listbox selection
            index = event.widget.curselection()[0]
            item = event.widget.get(index)
            print(index)
            print(int(str(event.widget)[-1]) - 2)
            index_df = int(str(event.widget)[-1]) - 2  # index of the list of user dataframes
            org_index = each_user_items[index_df].iloc[[index]]["copy_index"].values[0]
            print('org_index', org_index)
            for j in range(len(each_user_items)):
                each_user_items[j] = each_user_items[j][each_user_items[j]["copy_index"] != org_index]
            update_user_bill_gui()
            update_bill_gui()




        bill_elements_list_box.bind("<<ListboxSelect>>", on_main_listbox_select)

        each_user_items_listbox = [None] * no_users
        each_user_items_label_total = [None] * no_users
        for i in range(no_users):
            each_user_items_listbox[i] = Listbox(page2_window, border=1)
            each_user_items_listbox[i].bind("<<ListboxSelect>>", on_user_listbox_select)
            each_user_items_label_total[i] = Label(page2_window, text="$")
            # parts_list.grid(row=3, column=0, columnspan=3, rowspan=6, pady=20, padx=20)
            each_user_items_listbox[i].pack(padx=5, pady=15, side=LEFT)
            each_user_items_label_total[i].place(in_=each_user_items_listbox[i], relx=0, x=0, rely=1)
        page2_window.title("Page 2")
        page2_window.geometry('1000x500')
        '''All GUI elements of bill split window end'''

        def show_checkboxes():
            selected_list_index = bill_elements_list_box.curselection()

            selected_list_element = bill_elements_list_box.get(selected_list_index)
            print(selected_list_element)
            print(selected_list_index)
            # Create four checkboxes
            checkbox_window = Toplevel(root)
            checkbox_window.title(f"Checkboxes for {selected_list_element}")
            no_users = int(combobox.get())
            chkbox = [None] * no_users
            chk_var = [None] * no_users
            for i in range(no_users):
                chk_var[i] = IntVar()

                chkbox[i] = Checkbutton(checkbox_window, text="User" + str(i + 1), variable=chk_var[i])

                chkbox[i].pack()

            def submit():
                global bill_elements
                print(bill_elements)
                # Function to retrieve selected checkboxes' values
                selected_checkboxes = []
                print(bill_elements.loc[[selected_list_index[0]]])
                for i in range(no_users):
                    if chk_var[i].get() == 1:
                        selected_checkboxes.append(i)

                # Show messagebox with selected checkboxes' values
                global each_user_items
                for i in selected_checkboxes:
                    each_user_items[i] = each_user_items[i].append(
                        {'Item': bill_elements.loc[[selected_list_index[0]]]["Item"].values[0],
                         'Price': bill_elements.loc[[selected_list_index[0]]]["Price"].values[0] / len(
                             selected_checkboxes),
                         'copy_index': bill_elements.loc[[selected_list_index[0]]]["copy_index"].values[0]},
                        ignore_index=True)

                    # each_user_items_listbox[i].insert(END, str(
                    #     bill_elements.loc[[selected_list_index[0]]]["Item"].values[0]) + "-$" + str(
                    #     bill_elements.loc[[selected_list_index[0]]]["Price"].values[0] / len(selected_checkboxes)))


                update_user_bill_gui()

                print(selected_checkboxes)
                print("0 frame")
                print(each_user_items[0])
                print("1 frame")
                print(each_user_items[1])
                checkbox_window.destroy()

            submit_button = Button(checkbox_window, text="Submit", command=submit)
            submit_button.pack()

        page2_label = Label(page2_window, text="Bill Split")
        page2_label.pack()
        page2_btn = Button(page2_window, text="Back", command=page2_window.destroy)
        page2_btn.pack()

    # Create UI elements for root window
    # Add a label and a button to the GUI window
    label = Label(root, text="Click the button to upload an image", font=('bold', 12), pady=20)
    label.grid(row=0, column=0, sticky=W)

    button = Button(root, text="Upload Image", command=open_image)
    button.grid(row=1, column=0, sticky=W)

    # Create a StringVar to store the selected value
    selected_value_no_users = StringVar()
    # Create a Combobox with some values
    combobox = Combobox(root, textvariable=selected_value_no_users, values=["2", "3", "4"])
    combobox.grid(row=2, column=0, sticky=W)
    # Set the default value
    combobox.set("2")

    # Function to handle selection change
    def on_combobox_select(event):
        selected_option = combobox.get()
        print("Selected option:", selected_option)

    # Bind the event for selection change
    combobox.bind("<<ComboboxSelected>>", on_combobox_select)

    # Number of users

    billsplitbutton = Button(root, text="Split", command=open_bill_split_window)
    billsplitbutton.grid(row=3, column=0, sticky=W)
    # button.pack()

    # Start the GUI event loop
    root.mainloop()


''''''

if __name__ == "__main__":
    main()
