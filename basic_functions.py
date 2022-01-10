import pyodbc
import PySimpleGUI as sg
import re

number_regex = re.compile("^\d+$")
date_regex = re.compile("^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$")


def show_phones(conn):
    cursor = conn.cursor()
    res = []
    cursor.execute(f"select * from dbo.getPhoneNumbers()")
    for row in cursor:
        res.append(str(row[0]))
    # res = ['241412421', '4124421', '51252152']  # placeholder
    phones_layout = [
        [sg.Text(f"Wszystkie telefony", size=(18, 1), font=("Arial", 11))],
    ]
    for i in res:
        phones_layout.append([sg.Text(i)])
    window_phones = sg.Window("Telefony", phones_layout)
    event, phones_values = window_phones.read()
    if event == sg.WIN_CLOSED:
        window_phones.close()


def delete_old_visits(conn):
    cursor = conn.cursor()
    cursor.execute(f"exec removeMadeVisits")
    conn.commit()


def get_ambulanses_id(conn):
    cursor = conn.cursor()
    cursor.execute(f"select id from ambulans")
    res = []
    for row in cursor:
        res.append([str(element) for element in row])
    return res


def get_patients_id(conn):
    cursor = conn.cursor()
    cursor.execute(f"select pesel from pacjent")
    res = []
    for row in cursor:
        res.append([str(element) for element in row])
    return res


def get_room_number_by_ward(conn, ward):
    ward = f"'{ward}'"
    cursor = conn.cursor()
    cursor.execute(f"select numer from sala where oddzial_nazwa = {ward}")
    res = []
    for row in cursor:
        res.append(row[0])
    return res


def get_room_ward(conn):
    cursor = conn.cursor()
    cursor.execute(f"select nazwa from oddzial")
    res = []
    for row in cursor:
        res.append(row[0])
    return res


def add_zgloszenie(conn):
    columns = list_columns(conn, "Zgloszenie", get_types=True)[1:-1]
    select_layout = [
        [sg.Text(f"Dodaj Zgloszenie", size=(18, 1), font=("Arial", 11))],
        [sg.Text("Zwroc uwage na typy wartosci (data w formacie YYYY-MM-DD)", font=("Arial", 11))],
        [sg.Text("Atrybur", size=(18, 1), font=("Arial", 11)), sg.Text("Typ", size=(18, 1))],
        zip(
            [sg.Text(column[0], size=(20, 1)) for column in columns],
            [sg.Text(column[1], size=(20, 1)) for column in columns],
            [sg.InputText() for i in range(len(columns))]
        ),
        [sg.Submit("Dodaj")]
    ]

    ambulans_layout = [
        [sg.Text(f"Wybierz ambulans", size=(18, 1), font=("Arial", 11))],
        [sg.Button(str(i[0])) for i in get_ambulanses_id(conn)]
    ]

    window_ambulans = sg.Window("Ambulans", ambulans_layout)
    ambulans, ambulans_values = window_ambulans.read()
    window_ambulans.close()
    if ambulans == sg.WIN_CLOSED:
        return

    window_create = sg.Window("Zgloszenie", select_layout)
    while 1:
        create_event, create_values = window_create.read()
        if create_event == sg.WIN_CLOSED:
            window_create.close()
            break
        if create_event == "Dodaj":
            types = [column[1] for column in columns]
            types.append('numeric')
            names = [column[0] for column in columns]
            names.append('ambulans_id')
            values = [create_values[i] for i in range(len(create_values))]
            values.append(ambulans)
            validation = True
            values_types = zip(values, types)
            for value_type in values_types:
                if value_type[0] == "" or (value_type[1] == 'date' and not date_regex.match(value_type[0])) \
                        or (value_type[1] == 'numeric' and not number_regex.match(value_type[0])):
                    validation = False
                    break
            if validation:
                create(
                    conn,
                    "Zgloszenie",
                    values,
                    names,
                    types
                )
                window_create.close()
                break


def add_wizyta(conn):
    columns = list_columns(conn, "Wizyta", get_types=True)[1:-3]
    select_layout = [
        [sg.Text(f"Dodaj Wizyte", size=(18, 1), font=("Arial", 11))],
        [sg.Text("Zwroc uwage na typy wartosci (data w formacie YYYY-MM-DD)", font=("Arial", 11))],
        [sg.Text("Atrybur", size=(18, 1), font=("Arial", 11)), sg.Text("Typ", size=(18, 1))],
        zip(
            [sg.Text(column[0], size=(20, 1)) for column in columns],
            [sg.Text(column[1], size=(20, 1)) for column in columns],
            [sg.InputText() for i in range(len(columns))]
        ),
        [sg.Submit("Dodaj")]
    ]

    patient_layout = [
        [sg.Text(f"Wybierz pacjenta", size=(18, 1), font=("Arial", 11))],
        [sg.Button(str(i[0])) for i in get_patients_id(conn)]
    ]

    window_patient = sg.Window("Pacjent", patient_layout)
    patient, patient_values = window_patient.read()
    window_patient.close()
    if patient == sg.WIN_CLOSED:
        return

    ward_layout = [
        [sg.Text(f"Wybierz oddzial", size=(18, 1), font=("Arial", 11))],
        [sg.Button(str(i)) for i in get_room_ward(conn)]
    ]

    window_ward = sg.Window("Oddzial", ward_layout)
    ward, ward_values = window_ward.read()
    window_ward.close()
    if ward == sg.WIN_CLOSED:
        return

    room_layout = [
        [sg.Text(f"Wybierz sale", size=(18, 1), font=("Arial", 11))],
        [sg.Button(str(i)) for i in get_room_number_by_ward(conn, ward)]
    ]

    window_room = sg.Window("Oddzial", room_layout)
    room, room_values = window_room.read()
    window_room.close()
    if room == sg.WIN_CLOSED:
        return

    window_create = sg.Window("Wizyta", select_layout)
    while 1:
        create_event, create_values = window_create.read()
        if create_event == sg.WIN_CLOSED:
            window_create.close()
            break
        if create_event == "Dodaj":
            types = [column[1] for column in columns]
            types.append('varchar')
            types.append('varchar')
            types.append('varchar')
            names = [column[0] for column in columns]
            names.append('sala_numer')
            names.append('sala_oddzial_nazwa')
            names.append('pacjent_pesel')
            values = [create_values[i] for i in range(len(create_values))]
            values.append(room)
            values.append(ward)
            values.append(patient)
            validation = True
            values_types = zip(values, types)
            for value_type in values_types:
                if value_type[0] == "" or (value_type[1] == 'date' and not date_regex.match(value_type[0])) \
                        or (value_type[1] == 'numeric' and not number_regex.match(value_type[0])):
                    validation = False
                    break
            if validation:
                create(
                    conn,
                    "Wizyta",
                    values,
                    names,
                    types
                )
                window_create.close()
                break


def search(conn, event):
    print(search)
    table_name = event
    search_layout_before = [
        [sg.Text("Wyszukaj po", size=(18, 1), font=("Arial", 11))],
        [sg.Button(column_name) for column_name in
         list_columns(conn, event)],
    ]
    columns_types = list_columns(conn, event, True)
    search_layout_after = [
        [sg.Input()],
        [sg.Submit("Wyszukaj")]
    ]
    search_layout = [[sg.Column(search_layout_before, key='s1'),
                      sg.Column(search_layout_after, visible=False, key='s2')]]
    window_search = sg.Window(event, search_layout)
    search_event, search_values = window_search.read()
    if search_event != None:
        window_search['s1'].update(visible=False)
        window_search['s2'].update(visible=True)
    column_name = search_event
    while 1:
        search_event, search_values = window_search.read()
        if search_event == sg.WIN_CLOSED:
            window_search.close()
            break
        print(search_event)
        if search_event == 'Wyszukaj':
            column_type = 'numeric'
            for column_value in columns_types:
                if column_value[0] == column_name:
                    column_type = column_value[1]
                    break
            if (column_type == 'varchar' or column_type == 'date') and search_values[0] != '':
                search_value = f"'{search_values[0]}'"
            else:
                search_value = search_values[0]

            if search_value != "" and (
                    column_type == 'varchar' or (column_type == 'numeric' and number_regex.match(search_value)) or (
                    column_type == 'date' and date_regex.match(search_value[1:-1]))):
                cursor = conn.cursor()
                cursor.execute(f"select * from {table_name} where {column_name} = {search_value}")
                res = []
                for row in cursor:
                    res.append([str(element) for element in row])
                for row in res:
                    i = 0
                    while i < len(row):
                        row[i] = sg.Text(row[i], size=(20, 1))
                        i += 1
                res_layout = [
                                 [sg.Text(f"Wyniki wyszukiwania", size=(18, 1), font=("Arial", 11))],
                                 [sg.Text(column_name, size=(18, 1), font=("Arial", 11))
                                  for column_name in
                                  list_columns(conn, event)]
                             ] + res
                window_search.close()
                window_res = sg.Window("Wyniki", res_layout)
                res_event, res_values = window_res.read()
                break


def delete(conn, event):
    print("delete")
    table_name = event
    selected_data = read(conn, event)
    for row in selected_data:
        name = row[0]
        i = 0
        while i < len(row):
            row[i] = sg.Text(row[i], size=(20, 1))
            i += 1
        row.append(sg.Button(f"Usun {name}"))
    columns = list_columns(conn, event, True)
    pk_name = columns[0][0]
    pk_type = columns[0][1]
    delete_layout = [
                        [sg.Text(f"Dane dla {event}", size=(18, 1), font=("Arial", 11))],
                        [sg.Text(column_name[0], size=(18, 1), font=("Arial", 11)) for column_name in columns]
                    ] + selected_data
    window_delete = sg.Window(event, delete_layout)
    delete_event, delete_values = window_delete.read()
    if delete_event != None:
        searched_value = delete_event.split()[1]
        if pk_type == 'varchar':
            searched_value = (f"'{searched_value}'")
        cursor = conn.cursor()
        print(f"delete from {table_name} where {pk_name} = {searched_value}")
        cursor.execute(f"delete from {table_name} where {pk_name} = {searched_value}")
        conn.commit()
        window_delete.close()


def update(conn, event):
    print("update")
    read_data = read(conn, event)
    tmp = read(conn, event)
    selected_data = [i[1:] for i in tmp]
    row_num = 0
    for row in selected_data:
        i = 0
        while i < len(row):
            row[i] = sg.Button(f"{row_num + 1} -> {row[i]}", size=(20, 1))
            i += 1
        row_num += 1
    columns = list_columns(conn, event, True)
    update_layout_1 = [
                          [sg.Text(f"Dane dla {event}", size=(18, 1), font=("Arial", 11))],
                          [sg.Text(column_name[0], size=(18, 1), font=("Arial", 11)) for column_name in columns[1:]]
                      ] + selected_data
    update_layout_2 = [[sg.Text(f"Nowa wartosc", size=(18, 1), font=("Arial", 11))],
                       [sg.Text(f"Zwroc uwage na typy wartosci (data w formacie YYYY-MM-DD)", font=("Arial", 11))],
                       [sg.InputText()],
                       [sg.Submit("Modyfikuj")]
                       ]
    update_layout_3 = [[sg.Text(f"Nowa wartosc", size=(18, 1), font=("Arial", 11))],
                       [sg.Button(str(i[0])) for i in get_ambulanses_id(conn)]
                       ]
    update_layout_4 = [[sg.Text(f"Nowa wartosc", size=(18, 1), font=("Arial", 11))],
                       [sg.Button(str(i[0])) for i in get_patients_id(conn)]
                       ]
    update_layout = [[sg.Column(update_layout_1, key='u1'),
                      sg.Column(update_layout_2, visible=False, key='u2'),
                      sg.Column(update_layout_3, visible=False, key='u3'),
                      sg.Column(update_layout_4, visible=False, key='u4')]]

    window_update = sg.Window(event, update_layout)

    update_event, update_values = window_update.read()
    if update_event != None:
        update_event = update_event.split(" -> ")
        row_number = int(update_event[0]) - 1
        changed_value = update_event[1]
        condition = ""
        print(row_number, changed_value)
        changed_column = [0]
        for i in range(len(columns)):
            val = read_data[row_number][i]
            if val == changed_value or val == changed_value[:-1]:
                changed_column = columns[i]
                if changed_column[0] == 'Sala_numer':
                    ward = read_data[row_number][i + 1]
                    print(ward)
            if (columns[i][1] == 'varchar' or columns[i][1] == 'date') and val != '':
                val = f"'{val}'"
            condition += columns[i][0] + " = " + val + " and "
        condition = condition[:-5]
        print(condition)
        if changed_column[0] == 'Sala_numer':
            room_layout = [[sg.Text(f"Nowa wartosc", size=(18, 1), font=("Arial", 11))],
                           [sg.Button(str(i)) for i in get_room_number_by_ward(conn, ward)]
                           ]
            window_room = sg.Window(event, room_layout)
            while 1:
                room, room_values = window_room.read()
                if room == sg.WIN_CLOSED:
                    window_room.close()
                    window_update.close()
                    break
                elif room != None:
                    room = f"'{room}'"
                    command = f"update {event} set {changed_column[0]} = {room} where " + condition
                    print(command)
                    cursor = conn.cursor()
                    cursor.execute(command)
                    conn.commit()
                    window_update.close()
                    window_room.close()
                    break
            return
        if changed_column[0] == 'Sala_Oddzial_nazwa':
            ward_layout = [[sg.Text(f"Nowa wartosc", size=(18, 1), font=("Arial", 11))],
                           [sg.Button(str(i)) for i in get_room_ward(conn)]
                           ]

            window_ward = sg.Window(event, ward_layout)
            while 1:
                ward, ward_values = window_ward.read()
                if ward == sg.WIN_CLOSED:
                    window_ward.close()
                    window_update.close()
                    break
                elif ward != None:
                    room_layout = [[sg.Text(f"Wybierz pokoj", size=(18, 1), font=("Arial", 11))],
                                   [sg.Button(str(i)) for i in get_room_number_by_ward(conn, ward)]
                                   ]
                    window_room = sg.Window(event, room_layout)
                    while 1:
                        room, room_values = window_room.read()
                        if room == sg.WIN_CLOSED:
                            window_room.close()
                            window_ward.close()
                            window_update.close()
                            break
                        elif room != None:
                            ward = f"'{ward}'"
                            room = f"'{room}'"
                            command = f"update {event} set Sala_Oddzial_nazwa = {ward}, Sala_numer = {room} where " + condition
                            print(command)
                            cursor = conn.cursor()
                            cursor.execute(command)
                            conn.commit()
                            window_room.close()
                            window_ward.close()
                            window_update.close()
                            break
                    break
            return
        if event == 'Zgloszenie' and changed_column[0] == 'Ambulans_id':
            window_update['u1'].update(visible=False)
            window_update['u3'].update(visible=True)
            while 1:
                update_event, update_values = window_update.read()
                if update_event == sg.WIN_CLOSED:
                    window_update.close()
                    break
                elif update_event != None:
                    command = f"update {event} set {changed_column[0]} = {update_event} where " + condition
                    print(command)
                    cursor = conn.cursor()
                    cursor.execute(command)
                    conn.commit()
                    window_update.close()
                    break
            return
        if event == 'Wizyta' and changed_column[0] == 'Pacjent_pesel':
            window_update['u1'].update(visible=False)
            window_update['u4'].update(visible=True)
            while 1:
                update_event, update_values = window_update.read()
                if update_event == sg.WIN_CLOSED:
                    window_update.close()
                    break
                elif update_event != None:
                    update_event = f"'{update_event}'"
                    command = f"update {event} set {changed_column[0]} = {update_event} where " + condition
                    print(command)
                    cursor = conn.cursor()
                    cursor.execute(command)
                    conn.commit()
                    window_update.close()
                    break
        else:
            window_update['u1'].update(visible=False)
            window_update['u2'].update(visible=True)
            while 1:
                update_event, update_values = window_update.read()
                if update_event == sg.WIN_CLOSED:
                    window_update.close()
                    break
                elif update_event == "Modyfikuj":
                    val = update_values[0]
                    if val != "" and (
                            changed_column[1] == 'varchar' or (
                            changed_column[1] == 'numeric' and number_regex.match(val)) or (
                                    changed_column[1] == 'date' and date_regex.match(val))):
                        if changed_column[1] == 'varchar' or changed_column[1] == 'date':
                            val = f"'{val}'"
                        command = f"update {event} set {changed_column[0]} = {val} where " + condition
                        print(command)
                        cursor = conn.cursor()
                        cursor.execute(command)
                        conn.commit()
                        window_update.close()
                        break


def create(conn, table_name, values, columns, types):
    print("create")
    values_types = zip(values, types)
    res_values = []
    for value_type in values_types:
        if value_type[1] == 'varchar' or value_type[1] == 'date':
            res_values.append(f"'{value_type[0]}'")
        else:
            res_values.append(value_type[0])
    command = "insert into " + table_name + "(" + ", ".join(columns) + ") values(" + ', '.join(res_values) + ")"
    cursor = conn.cursor()
    cursor.execute(command)
    conn.commit()


def read(conn, table_name):
    print("read")
    cursor = conn.cursor()
    cursor.execute(f"select * from {table_name}")
    res = []
    for row in cursor:
        res.append([str(element) for element in row])
    return res


def list_columns(conn, table_name, get_types=False):
    print("list_columns")
    cursor = conn.cursor()
    cursor.execute(f"SELECT column_name, data_type FROM szpital.information_schema.columns WHERE TABLE_NAME = ?",
                   f"{table_name}")
    if get_types:
        return [row for row in cursor]
    return [row[0] for row in cursor]


def list_tables(conn):
    print("list_tables")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM szpital.information_schema.tables"
    )
    row = cursor.fetchone()
    res = []
    while row:
        if '_' not in row[2]:  # we assume many to many relation names have _ in name (and only them)
            res.append(row[2])
        row = cursor.fetchone()
    return res
