import pyodbc
import PySimpleGUI as sg

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
    search_event, search_values = window_search.read()
    print(search_event)
    if search_event == 'Wyszukaj':
        column_type = 'numeric'
        for column_value in columns_types:
            if column_value[0] == column_name:
                column_type = column_value[1]
                break
        if column_type == 'varchar':
            search_value = (f"'{search_values[0]}'")
        else:
            search_value = search_values[0]
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
                     ] + res
        window_search.close()
        window_res = sg.Window("Wyniki", res_layout)
        res_event, res_values = window_res.read()


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


def update(conn, event):
    print("update")
    read_data = read(conn, event)
    selected_data = read(conn, event)
    row_num = 0
    for row in selected_data:
        i = 0
        while i < len(row):
            row[i] = sg.Button(f"{row_num + 1}-{row[i]}", size=(20, 1))
            i += 1
        row_num += 1
    columns = list_columns(conn, event, True)
    update_layout_1 = [
                        [sg.Text(f"Dane dla {event}", size=(18, 1), font=("Arial", 11))],
                        [sg.Text(column_name[0], size=(18, 1), font=("Arial", 11)) for column_name in columns]
                    ] + selected_data
    update_layout_2 = [[sg.Text(f"Nowa wartosc", size=(18, 1), font=("Arial", 11))],
                       [sg.InputText()],
                       [sg.Submit("Modyfikuj")]
                       ]
    update_layout = [[sg.Column(update_layout_1, key='u1'),
                      sg.Column(update_layout_2, visible=False, key='u2')]]
    window_update = sg.Window(event, update_layout)
    update_event, update_values = window_update.read()
    if update_event != None:
        window_update['u1'].update(visible=False)
        window_update['u2'].update(visible=True)
        update_event = update_event.split("-")
        row_number = int(update_event[0]) - 1
        changed_value = update_event[1]
        condition = ""
        print(row_number, changed_value)
        for i in range(len(columns)):
            val = read_data[row_number][i]
            if val == changed_value:
                changed_column = columns[i]
            if columns[i][1] == 'varchar':
                val = f"'{val}'"
            condition += columns[i][0] + " = " + val + " and "
        condition = condition[:-5]
        print(condition)
        update_event, update_values = window_update.read()
        if update_event == sg.WIN_CLOSED:
            window_update.close()
        elif update_event == "Modyfikuj":
            val = update_values[0]
            if changed_column[1] == 'varchar':
                val = f"'{val}'"
            command = f"update {event} set {changed_column[0]} = {val} where " + condition
            print(command)
            cursor = conn.cursor()
            cursor.execute(command)
            conn.commit()
            window_update.close()


def create(conn, table_name, values, columns, types):
    print("create")
    values_types = zip(values, types)
    res_values = []
    for value_type in values_types:
        if value_type[1] == 'varchar':
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
     sg.Button("Usuwaj dane")]
]

choose_table_layout = [
    [sg.Text("Wybierz rodzaj danych")],
    [sg.Button(f"{table}") for table in tables],
    [sg.Button("Powrot")]
]

layout = [[sg.Column(main_menu_layout, key='1'), sg.Column(choose_table_layout, visible=False, key='2')]]

window = sg.Window("Szpital", layout)

cur_layout = 1
chosen_option = "Glowne menu"
while 1:
    event, values = window.read()
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
            columns = list_columns(connection, event, get_types=True)
            select_layout = [
                [sg.Text(f"Dodaj {event}", size=(18, 1), font=("Arial", 11))],
                [sg.Text("Atrybur", size=(18, 1), font=("Arial", 11)), sg.Text("Typ", size=(18, 1))],
                zip(
                    [sg.Text(column[0], size=(20, 1)) for column in columns],
                    [sg.Text(column[1], size=(20, 1)) for column in columns],
                    [sg.InputText() for i in range(len(columns))]
                ),
                [sg.Submit("Dodaj")]
            ]
            window_create = sg.Window(event, select_layout)
            create_event, create_values = window_create.read()

            if create_event == sg.WIN_CLOSED:
                window_create.close()
            elif create_event == "Dodaj":
                create(
                    connection,
                    table_name,
                    [create_values[i] for i in range(len(create_values))],
                    [column[0] for column in columns],
                    [column[1] for column in columns]
                )
                window_create.close()
            event = "Dodaj dane"
        if chosen_option == "Modyfikuj dane":
            update(connection, event)
        if chosen_option == "Usuwaj dane":
            delete(connection, event)

    if event == "Przegladaj dane" or \
            event == "Wyszukaj dane" or \
            event == "Dodaj dane" or \
            event == "Modyfikuj dane" or \
            event == "Usuwaj dane":
        window['1'].update(visible=False)
        window['2'].update(visible=True)
        cur_layout = 2
        chosen_option = event
    if event == "Powrot":
        window['2'].update(visible=False)
        window['1'].update(visible=True)
        cur_layout = 1
    if event == sg.WIN_CLOSED:
        break

window.close()
connection.close()
