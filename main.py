debug_mode = False

from basic_functions import *
import re


number_regex = re.compile("^\d+$")
date_regex = re.compile("^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$")


connection = pyodbc.connect(
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=DESKTOP-3I1CRBC;"
    "Database=szpital;"
    "Trusted_Connection=yes;"
)

tables = list_tables(connection)

main_menu_layout = [
    [sg.Text("Co chcesz zrobic?")],
    [sg.Button("Przegladaj dane"),
     sg.Button("Wyszukaj dane"),
     sg.Button("Dodaj dane"),
     sg.Button("Modyfikuj dane"),
     sg.Button("Usuwaj dane")],
    [sg.Button("Usun zalegle wizyty"),
     sg.Button("Wyswietl numery telefonow")]
]

choose_table_layout = [
    [sg.Text("Wybierz rodzaj danych")],
    [sg.Button(f"{table}") for table in tables if table != 'sysdiagrams'],
    [sg.Button("Powrot")]
]

editable = ["Wizyta", "Pacjent", "Zgloszenie"]

editable_table_layout = [
    [sg.Text("Wybierz rodzaj danych")],
    [sg.Button(f"{table}") for table in tables if table in editable],
    [sg.Button("Powrot")]
]

layout = [[sg.Column(main_menu_layout, key='1'), sg.Column(choose_table_layout, visible=False, key='2'), sg.Column(editable_table_layout, visible=False, key='3')]]

window = sg.Window("Szpital", layout)

cur_layout = 1
chosen_option = "Glowne menu"
while 1:
    event, values = window.read()
    if event is not None and event[-1] in [str(i) for i in range(10)]:
        event = event[:-1]
    if cur_layout == 2 and event in tables:
        if chosen_option == "Przegladaj dane":
            selected_data = read(connection, event)
            for row in selected_data:
                i = 0
                while i < len(row):
                    row[i] = sg.Text(row[i], size=(20, 1))
                    i += 1
            select_layout = [
                                [sg.Text(f"Dane dla {event}", size=(18, 1), font=("Arial", 11))],
                                [sg.Text(column_name, size=(18, 1), font=("Arial", 11)) for column_name in
                                 list_columns(connection, event)],
                            ] + selected_data
            window_select = sg.Window(event, select_layout)
            select_event, select_values = window_select.read()
        if chosen_option == "Wyszukaj dane":
            search(connection, event)
        if chosen_option == "Dodaj dane":
            table_name = event
            if table_name == "Wizyta":
                add_wizyta(connection)
            elif table_name == "Zgloszenie":
                add_zgloszenie(connection)
            else:
                columns = list_columns(connection, event, get_types=True)
                select_layout = [
                    [sg.Text(f"Dodaj {event}", size=(18, 1), font=("Arial", 11))],
                    [sg.Text("Zwroc uwage na typy wartosci i sens relacji", font=("Arial", 11))],
                    [sg.Text("Atrybur", size=(18, 1), font=("Arial", 11)), sg.Text("Typ", size=(18, 1))],
                    zip(
                        [sg.Text(column[0], size=(20, 1)) for column in columns],
                        [sg.Text(column[1], size=(20, 1)) for column in columns],
                        [sg.InputText() for i in range(len(columns))]
                    ),
                    [sg.Submit("Dodaj")]
                ]
                window_create = sg.Window(event, select_layout)
                while 1:
                    create_event, create_values = window_create.read()
                    if create_event == sg.WIN_CLOSED:
                        window_create.close()
                        break
                    if create_event == "Dodaj":
                        types = [column[1] for column in columns]
                        names = [column[0] for column in columns]
                        values = [create_values[i] for i in range(len(create_values))]
                        validation = True
                        values_types = zip(values, types, names)

                        for value_type in values_types:
                            if value_type[2] == 'pesel':
                            if value_type[0] == "" or (value_type[1] == 'date' and not date_regex.match(value_type[0]))\
                                    or (value_type[1] == 'numeric' and not number_regex.match(value_type[0]))\
                                    or (value_type[2] == 'pesel' and value_type[0] in [i[0] for i in get_patients_id(connection)]):
                                validation = False
                                break
                        if validation:
                            create(
                                connection,
                                table_name,
                                values,
                                names,
                                types
                            )
                            window_create.close()
                            break
            event = "Dodaj dane"
        if chosen_option == "Modyfikuj dane":
            update(connection, event)
        if chosen_option == "Usuwaj dane":
            delete(connection, event)

    if event == "Przegladaj dane" or \
            event == "Wyszukaj dane":
        window['1'].update(visible=False)
        window['2'].update(visible=True)
        cur_layout = 2
        chosen_option = event
    if event == "Dodaj dane" or \
            event == "Modyfikuj dane" or \
            event == "Usuwaj dane":
        window['1'].update(visible=False)
        if debug_mode:
            window['2'].update(visible=True)
        else:
            window['3'].update(visible=True)

        cur_layout = 2
        chosen_option = event
    if event == "Powrot":
        window['2'].update(visible=False)
        window['3'].update(visible=False)
        window['1'].update(visible=True)
        cur_layout = 1
    if event == "Wyswietl numery telefonow":
        show_phones(connection)
        print("hehe pokazuje telefony")
    if event == "Usun zalegle wizyty":
        delete_old_visits(connection)
    if event == sg.WIN_CLOSED:
        break

window.close()
connection.close()
