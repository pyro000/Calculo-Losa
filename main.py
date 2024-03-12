import PySimpleGUI as sg
from PIL import Image as PILImage
from io import BytesIO

sg.theme('Black')

def get_img_data(f, maxsize=(1200, 850), var="PNG"):
    img = PILImage.open(f)
    img.thumbnail(maxsize)
    bio = BytesIO()
    img.save(bio, format=var)
    return bio.getvalue()


def c_table(data):
    return [[data[0][i], data[1][i], data[2][i]] for i, _ in enumerate(data[0])]


def operate_af(data, inter=True):
    bE = min(data[0] + 8 * data[1], data[0] + 2 * (data[2] - data[1])) if inter else min(data[0] + 4 * data[1],
                                                                                         data[0] + data[2] - data[1])
    bEbW = bE / data[0]
    th = data[1] / data[2]
    k = (1 + (bEbW - 1) * th * (4 - 6 * th + 4 * th ** 2 + (bEbW - 1) * th ** 3)) / (1 + (bEbW - 1) * th)
    Ib = (data[0] * data[2] ** 3) / 12 * k
    Is = ((data[3] * 100) * data[1] ** 3) / 12 if inter else (((data[3] * 100) / 2 + data[0] / 2) * data[1] ** 3) / 12
    afr = Ib / Is
    return {'bE': round(bE, 2), 'bEbW': round(bEbW, 2), 'th': round(th, 2), 'k': round(k, 2), 'Ib': round(Ib, 2),
            'Is': round(Is, 2), 'afr': round(afr, 2)}


def operate_h(data, baf=False):
    if baf:
        return '-', round(data[1] / data[2], 3)
    b = data[1] / data[2]
    result = (data[1] * (0.8 + 4200 / 14000)) / (36 + 5 * b * (data[0] - 0.2)) if data[0] < 2 else (data[1] * (
                0.8 + (4200 / 14000))) / (36 + 9 * b)
    return b, round(result * 100, 3)


def ed_ln(window, visible=True, bfy=False):
    window['-tlnl-'].update(visible=visible)
    window['-lnL-'].update(visible=visible)
    window['-tlnc-'].update(visible=visible if not bfy else False)
    window['-lnC-'].update(visible=visible if not bfy else False)
    window['Calcular h'].update(visible=visible)


def ed_fy(window, visible=True):
    window['-tfy-'].update(visible=visible)
    window['-fy-'].update(visible=visible)


def ex_afs_num(val):
    t_sep = []
    t_sep[:0] = val['-afs-']
    return int(t_sep[2])


def check_afs(afs):
    af = 0
    j = 0
    for i in afs:
        if isinstance(i, (float, int)):
            af += i
            j += 1
    return af, j


def main():
    headings = ['Dato', 'Respuesta', 'Medida']

    data = [['bW =', 't =', 'h =', 'l2 =', 'bE =', 'bE/bW', 't/h', 'k =', 'Ib =', 'Is =', '', 'αf1 =', 'αf2 =', 'αf3 =',
             'αf4 =', '', 'αf =', 'B =', 'h ='], ['' for _ in range(19)],
            ['cm', 'cm', 'cm', 'm', 'cm', 'cm', 'cm', '', 'cm^4', 'cm^4', '', '', '', '', '', '', '', '', 'cm']]
    table = c_table(data)

    afs = [None, None, None, None]

    col1 = [[sg.Column([[sg.Image(data=get_img_data('data/exterior.png', maxsize=(380, 356), var="PNG"),
                                  size=(380, 356), key='-IMG-')]], size=(380, 356))],
            [sg.Combo([f'αf{i + 1}' for i in range(4)], default_value='αf1', key='-afs-', readonly=True,
                      enable_events=True), sg.Text(f'= {afs[0]}', key='-afans-')],
            [sg.Text('bW (cm):'), sg.Input(key='-bW-', size=(6, 1)), sg.Text('t (cm):'),
             sg.Input(key='-t-', size=(6, 1))],
            [sg.Text('h (cm):'), sg.Input(key='-h-', size=(6, 1)), sg.Text('l2 (m):'),
             sg.Input(key='-l2-', size=(6, 1))],
            [sg.Button('Calcular αf')]]

    col2 = [[sg.Table(table, key='-TABLE-', headings=headings, max_col_width=65, auto_size_columns=False,
                      justification='c', num_rows=19)],
            [sg.Text('ln Largo :', visible=False, key='-tlnl-'), sg.Input(key='-lnL-', size=(6, 1), visible=False),
             sg.Text('ln Corto :', visible=False, key='-tlnc-'),
             sg.Input(key='-lnC-', size=(6, 1), visible=False)],
            [sg.Text('fy :', visible=False, key='-tfy-'),
             sg.Combo(['280', '420', '550'], default_value='280', key='-fy-', readonly=True, visible=False)],
            [sg.Button('Calcular h', visible=False)]]

    layout = [[sg.Text('Losa: '),
               sg.Combo(['Exterior', 'Interior', 'Lateral'], default_value='Exterior', key='-exin-', readonly=True,
                        enable_events=True)],
              [sg.Column(col1, element_justification='c'), sg.Column(col2, element_justification='c')]]

    window = sg.Window('Beam', layout, element_justification='c')

    while True:
        ev, val = window.read(timeout=5)

        if ev == sg.WIN_CLOSED:
            break

        window['-TABLE-'].update(select_rows=(18,))

        af, j = check_afs(afs)

        if j == 4:
            if af / j <= 0.2:
                ed_ln(window, bfy=True)
                ed_fy(window)
            else:
                ed_ln(window)
                ed_fy(window, visible=False)

        if ev == '-afs-':
            in_afs = ex_afs_num(val)
            if val['-exin-'] == 'Exterior' and in_afs < 3:
                window['-IMG-'].update(data=get_img_data('data/exterior.png', maxsize=(380, 356), var="PNG"))
            elif val['-exin-'] == 'Lateral' and in_afs == 4:
                window['-IMG-'].update(data=get_img_data('data/exterior.png', maxsize=(380, 356), var="PNG"))
            else:
                window['-IMG-'].update(data=get_img_data('data/interior.png', maxsize=(380, 356), var="PNG"))
            window['-afans-'].update(f'= {afs[in_afs - 1]}')
            table[6][0] = f'{val["-afs-"]} ='
            window['-TABLE-'].update(table)

        elif ev == '-exin-':
            window['-IMG-'].update(data=get_img_data('data/interior.png', maxsize=(380, 356), var="PNG"))
            if val['-exin-'] == 'Exterior':
                in_afs = ex_afs_num(val)
                if in_afs < 3:
                    window['-IMG-'].update(data=get_img_data('data/exterior.png', maxsize=(380, 356), var="PNG"))

        elif ev == 'Calcular αf':
            if val['-bW-'] and val['-t-'] and val['-h-'] and val['-l2-']:
                try:
                    inputs = [float(val['-bW-']), float(val['-t-']), float(val['-h-']), float(val['-l2-'])]
                    in_afs = ex_afs_num(val) - 1

                    if val['-exin-'] == 'Exterior' and in_afs < 2:
                        result = operate_af(inputs, inter=False)
                    elif val['-exin-'] == 'Lateral' and in_afs == 4:
                        result = operate_af(inputs, inter=False)
                    else:
                        result = operate_af(inputs)

                    afs[in_afs] = result['afr']

                    af, j = check_afs(afs)
                    af = round(af / j, 4)

                    data[1] = inputs + [result['bE'], result['bEbW'], result['th'], result['k'], result['Ib'],
                                        result['Is'], '', '' if not afs[0] else afs[0], '' if not afs[1] else afs[1],
                                        '' if not afs[2] else afs[2], '' if not afs[3] else afs[3], '', af, '', '']
                    table = c_table(data)

                    window['-afans-'].update(f'= {afs[in_afs]}')
                    window["-TABLE-"].update(table)

                except ValueError:
                    sg.popup_error('Todos los campos deben ser números.')

            else:
                sg.popup_error('Todos los campos deben estar llenos.')

        elif ev == 'Calcular h':
            af, j = check_afs(afs)
            if (af / j <= 0.2 and val['-lnL-']) or (val['-lnL-'] and val['-lnC-']):
                t_lnc = val['-lnC-'] if af / j > 0.2 else 0
                try:
                    inputs = [af / j, float(val['-lnL-']), float(t_lnc)]
                    if af / j <= 0.2:
                        if val['-exin-'] == 'Exterior':
                            divisor = 33 if val['-fy-'] == '280' else 30 if val['-fy-'] == '420' else 27
                        else:
                            divisor = 36 if val['-fy-'] == '280' else 33 if val['-fy-'] == '420' else 30
                        inputs = [af / j, inputs[1], divisor]
                        result = operate_h(inputs, baf=True)
                    else:
                        result = operate_h(inputs)
                    data[1][17] = result[0]
                    data[1][18] = result[1]
                    table = c_table(data)
                    window["-TABLE-"].update(table)

                except ValueError:
                    sg.popup_error('Ln Largo y Corto deben ser números.')
            else:
                sg.popup_error('Debe llenar ln Largo y/o Corto para continuar.')

    window.close()


if __name__ == '__main__':
    main()
