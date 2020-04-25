import pandas

import logging
logging.basicConfig(level=logging.DEBUG)


#r = s.get("https://afd.sphosting.ch/DES/_api/web/lists/GetByTitle('Personen')/Items")

# import gender_guesser.detector as gender
# d = gender.Detector()
#
# def getGender(first_name):
#     for char in " ","-": ## If name is split by space or dash, split using this character and return gender of component if found.
#         if char in first_name:
#             for name_split in first_name.split(char):
#                 gender_of_split = getGender(name_split)
#                 if gender_of_split != "":
#                     return(gender_of_split)
#
#     geschlecht_dict = {"male":"SEX_MALE","female":"SEX_FEMALE","andy":"","unknown":""}
#     gender_en = d.get_gender(first_name,country="germany")
#     if gender_en == "unknown":
#         gender_en = d.get_gender(first_name) ## Try default country (English names)
#     return(geschlecht_dict[gender_en])
def export_excel(dict_list,columns=False,doc_name="excel_file"):
    ''' Take list of dicts with person data and exports it as doc name
Docs https://xlsxwriter.readthedocs.io/working_with_pandas.html#ewx-pandas'''


    data = {}
    if not columns:
        columns = list(dict_list[0].keys())
        for row in dict_list:
            for cell in row:
                if cell not in columns:
                    columns.append(cell)
    
    columns = ["No"] + columns
    for counter,row_dict in enumerate(dict_list):
        row_dict["No"] = counter +1
    ## Creates dic with col names as values and cell values in column as lists
    for column in columns:
        for person in dict_list:
            if column in person:
                data[column] = person[column]
            else:
                data[column] = person[column] = ""
        data[column] = [person[column] for person in dict_list] ## Empty list to be filled with specific values

    df = pandas.DataFrame(data)
    # from django.conf import settings
    ## automatically saves to /app/data/media/filename.xlsx (without custom settings)
    file_path = f"/data/{doc_name}.xlsx"
    writer = pandas.ExcelWriter(file_path, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1',index=False)
    writer.save()
    return(file_path)
import copy
def eventExcel(formentries,
doc_name,
columns=["Titel","Familienname","Vorname","Einladungscode","Status","E_Mail"]):
    '''Convert an array of FormEntry records for a Seminar
    into an Excel spreadsheet'''
    if len(formentries) == 0: ## If length of array is zero
        return(False)
    else:
        # columns = [column for column in formentries[0].__dict__ if column in columns]
        dict_list = []
        for formentry in formentries:
            if formentry.Status not in ("Papierkorb","Teilnehmer storniert","abgesagt"):
                row_dict = {column:getattr(formentry,column) for column in columns}
                row_dict_ = copy.copy(row_dict)
                for key,value in row_dict_.items():
                    if value == "None": ## Should stop text "None" bug from propagating
                        setattr(formentry,key,None)
                        formentry.save()
                        row_dict[value] = ""
                ## Duplicate recognition: loop breaks if person is already in list
                for existing_entry in dict_list:
                    if row_dict == existing_entry:
                        break
                    ## Matching logic for discovering duplicates is reproduced with ORM/database in function Veranstaltung.valid_form_entries
                    elif row_dict["Familienname"] == existing_entry["Familienname"] and row_dict["Vorname"] == existing_entry["Vorname"] and row_dict["E_Mail"] == existing_entry["E_Mail"]:
                        break
                else:
                    dict_list.append(row_dict)

        dict_list = sorted(dict_list, key=lambda k: k['Familienname'])
        file_path = export_excel(dict_list,columns=columns,doc_name=doc_name)
        return(file_path)
from collections import OrderedDict
import copy
def seminarExcel(formentries,doc_name,columns=["Anrede","Titel","Familienname",
"Vorname","roomtype_abbreviation",
"Zi.-Anzahl","Zimmerpartner","Rolle",
"Anzahl_ÜN","von_bis",
"E_Mail","Mobiltelefon"],export_statuses=("bestätigt",)):
    '''Convert an array of FormEntry records for a Seminar
    into an Excel spreadsheet'''
    if len(formentries) == 0: ## If length of array is zero
        return(False)
    else:
        # formentries = formentries.sorted()
        dict_list = []
        ## Number is incremented for ever booked room
        room_no = 0
        for formentry in formentries:
            if formentry.Status in export_statuses:
                row_dict = OrderedDict()
                
                ## Number of occupants in room associated with related status
                occupants = False
                
                try:
                    occupants = formentry.bookingoption.roomtype.occupants
                    if occupants:
                        room_no += 1 / occupants
                except Exception as e:
                    pass
                
                for column in columns:
                    if column != "Zi.-Anzahl":
                        row_dict[column] = getattr(formentry,column)
                    else: ## Logic for listing count of rooms
                        if not occupants:
                            row_dict[column] = ""
                        elif not room_no % 1:
                            row_dict[column] = room_no
                        else:
                            row_dict[column] = room_no + room_no % 1
                        
                # row_dict = {column : getattr(formentry,column) for column in columns}
                dict_list.append(row_dict)
        file_path = export_excel(dict_list,columns=columns,doc_name=doc_name)
        return(file_path)

def personsToExcel(persons,doc_name,plz_sorting=False,
exclude_columns=["_state","ausschließen","Mailinfo","Priorität_id","Bundesland_id","Quelle"],
additional_columns=["anrede","an_name"]):
    '''Convert an array of Person records
    into an Excel spreadsheet'''
    if len(persons) == 0: ## If length of array is zero
        return(False)
    else:
#        additional_columns = ["anrede","an_name"] ## Add calculated attributes
        columns = [column for column in persons[0].__dict__ if column != '' and column not in exclude_columns] + additional_columns
        dict_list = []
        for person in persons:
            row_dict = person.__dict__
            for x in additional_columns:
                row_dict[x] = getattr(person,x)
            dict_list.append(row_dict)

        if plz_sorting:
            dict_list = sorted(dict_list, key=lambda k: k['PLZ'])
        file_path = export_excel(dict_list,columns=columns,doc_name=doc_name)
        # from django.core.files import File
        # with open(file_path, 'w') as f:
        #     myfile = File(f)
        return(file_path)

def writeUnicodetxt(dict_list,columns,file_name="writeUnicodetxt"):
    '''Write data as tab-separated .txt file
    for use in InDesign mail merge'''
    import csv
    from bs4 import UnicodeDammit
#   with open(f'{file_name}.csv', 'w', newline='',encoding="utf-8") as csvfile:
    with open(f'{file_name}.txt', 'w', newline='',encoding="utf-16") as csvfile:

        writer = csv.DictWriter(csvfile, fieldnames=columns,
        quoting=csv.QUOTE_NONE,delimiter="	",escapechar=' ')
        writer.writeheader()

        for row_dict in dict_list:
            row_dict = {key:UnicodeDammit(value).unicode_markup for key,value in row_dict.items()}
            writer.writerow(row_dict)

def writeCSV(dict_list,columns=False,file_name="writeCSV",divider=","):
    '''Assume there is no .csv ending on file name
    columns can provide order and limit output
    return full file path'''
    from bs4 import UnicodeDammit
    import csv

    if not columns:
        columns = dict_list[0].keys()
    full_path = f"/data/{file_name}.csv"
    file = open(full_path, "w",encoding="utf-16")

    write_content = divider.join(columns)#.unicode_markup# + ";"
    file.write(write_content)
    for row_dict in dict_list:
        if columns: ## Only write data for the listed columns in the order given
            if type(row_dict) != str:
                write_list = [row_dict[column] for column in columns]
            else:
                write_list = ("row_dict was string!",row_dict)
        else:
            write_list = row_dict.values() ## Relies on dictionary ordering!
#        write_row = UnicodeDammit("\n" + divider.join(write_list)).unicode_markup.replace('""',"")# + ";"
        write_row = divider.join(write_list) + "\n"
        file.write(write_row)
    file.close()
    return(full_path)

import datetime
def Einladungscodes_CSV(invitees,file_name=f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Invitation Codes'):
    '''Accept list of Person objects, create CSV file with codes for import into Gravity plugin'''
    # from sharepy.excel_utils import writeCSV ## Custom library, German characters appear wrong when uploading
    columns = ('invitation_code_text', 'invitation_count', 'invitation_code_name')
    ## .csv added by  writeCSV
    writeCSV([x.gravity_csv_dict for x in invitees],columns=columns,file_name=file_name)

def xlsxToDictList(path):
    '''Convert xlsx file to list of dictionaries, no content parsing.'''
    ## https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_excel.html
    file = pandas.read_excel(path,
                             keep_default_na=False) ## Turns NaN into "" instead of float object

    columns = list(file.columns.values) # List of strings

    ## https://pandas.pydata.org/pandas-docs/stable/generated/pandas.ExcelFile.parse.html
    iterator = file.iterrows()
    row_list = []

    while True:
        try:
            _,row = next(iterator)
        except StopIteration as si:
            break
        row_dict = dict(zip(columns, row.tolist()))
        row_list.append(row_dict)

    return(row_list)
