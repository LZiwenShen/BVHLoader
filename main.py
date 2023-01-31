from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from IPython import display
from scipy.spatial.transform import Rotation as R


def Read_Hier(list_obj, list_data, father_name, n, l):
    i = n
    s = len(list_data)
    list_pro = []
    position = []
    if i < l and list_obj[i] != '\n':
        list_temp = list_obj[i].split()
        if list_temp[0] == 'ROOT':
            list_pro = [list_temp[1], list_temp[1]]
            father_name = list_temp[1]
        elif list_temp[0] == 'JOINT':
            list_pro = [list_temp[1], father_name]
            father_name = list_temp[1]
        elif list_temp[0] == 'End':
            i = i + 2
            if i < l:
                list_temp = list_obj[i].split()
                position = [float(list_temp[1]), float(list_temp[2]), float(list_temp[3])]
                list_pro = ['End_Site', list_data[s - 1][0], position]
                list_data.append(list_pro)
                Read_Hier(list_obj, list_data, '', i + 1, l)
                return
        elif list_temp[0] == '}':
            m = 0
            while i + 1 < l:
                cb = list_obj[i + 1].split()
                if cb[0] == '}':
                    i = i + 1
                    m = m + 1
                else:
                    break
            if m < s:
                father_temp = list_data[s - 1][1]
                j = s - 2
                while list_data[j][0] != father_temp:
                    j = j - 1
                father_name = list_data[j - m + 1][1]
            else:
                return
            if list_obj[i + 1] != '\n':
                Read_Hier(list_obj, list_data, father_name, i + 1, l)
                return
        i = i + 2
        if i < l:
            list_temp = list_obj[i].split()
        if list_temp[0] == 'OFFSET':
            position = [float(list_temp[1]), float(list_temp[2]), float(list_temp[3])]
        list_pro.append(position)
        i = i + 1
        if i < l:
            list_temp = list_obj[i].split()
        if list_temp[0] == 'CHANNELS':
            j = int(list_temp[1])
            for k in range(2, 2 + j):
                list_pro.append(list_temp[k])
        list_data.append(list_pro)
        Read_Hier(list_obj, list_data, father_name, i + 1, l)
    else:
        return


def Calc_Pos(list_obj, list_data, list_pos, n, s_data):
    list_temp = list_obj[n].split()
    s_temp = len(list_temp)
    for i in range(0, s_temp):
        list_temp[i] = float(list_temp[i])
    list_mot = []
    k = 0
    for i in range(0, s_data):
        s_pro = len(list_data[i])
        pos_temp = ['', '', '']
        r, p, y = 0, 0, 0
        for j in range(0, s_pro - 3):
            if list_data[i][3 + j] == 'Xposition':
                pos_temp[0] = list_temp[k]
            elif list_data[i][3 + j] == 'Yposition':
                pos_temp[1] = list_temp[k]
            elif list_data[i][3 + j] == 'Zposition':
                pos_temp[2] = list_temp[k]
            elif list_data[i][3 + j] == 'Xrotation':
                r = list_temp[k]
            elif list_data[i][3 + j] == 'Yrotation':
                p = list_temp[k]
            elif list_data[i][3 + j] == 'Zrotation':
                y = list_temp[k]
            j = j + 1
            k = k + 1
        if pos_temp != ['', '', '']:
            list_pos.append(pos_temp)
        rot_temp = R.from_euler('ZXY', [y, r, p], degrees=True)
        rot_temp.as_matrix()
        if list_data[i][0] != list_data[i][1]:
            for m in range(0, i):
                if list_data[m][0] == list_data[i][1]:
                    break
            if m < len(list_mot):
                rot_temp = rot_temp * list_mot[m]
            list_mot.append(rot_temp)
        i = i + 1
    for i in range(1, s_data):
        for m in range(0, i):
            if list_data[m][0] == list_data[i][1]:
                break
        list_mot[m].as_rotvec()
        pos_temp = list_mot[m].apply(list_data[i][2])
        pos_pro = [float(pos_temp[0]) + list_pos[m][0], float(pos_temp[1]) + list_pos[m][1], float(pos_temp[2]) + list_pos[m][2]]
        list_pos.append(pos_pro)


def Draw(list_data, list_pos, l):
    x = []
    y = []
    z = []
    label = []
    for i in range(0, l):
        label.append(0)
    for i in range(0, l):
        x.append(list_pos[i][0])
        y.append(list_pos[i][1])
        z.append(list_pos[i][2])
    fig = plt.figure()
    ax = Axes3D(fig, auto_add_to_figure=False)
    fig.add_axes(ax)
    ax.scatter3D(x, y, z, cmap='Blues')
    i = l - 1
    while i >= 0:
        x = []
        y = []
        z = []
        m = i
        while label[m] == 0:
            x.append(list_pos[m][0])
            y.append(list_pos[m][1])
            z.append(list_pos[m][2])
            label[m] = 1
            n = m - 1
            while list_data[n][0] != list_data[m][1]:
                n = n - 1
            m = n
        ax.plot(x, y, z, 'grey')
        while label[i - 1] == 1 and i != 0:
            i = i - 1
        i = i - 1
    plt.show()


file_obj = open('running.txt', 'r', encoding='UTF-8')
list_obj = file_obj.readlines()
i = 0
while list_obj[i] != 'MOTION\n':
    i = i + 1
list_data = []
l = i
Read_Hier(list_obj, list_data, '', 1, l)
s_data = len(list_data)
list_temp = list_obj[l + 1].split()
s = int(list_temp[1])
list_temp = list_obj[l + 2].split()
t = float(list_temp[2])
for i in range(0, s):
    list_pos = []
    Calc_Pos(list_obj, list_data, list_pos, l + 3 + i, s_data)
    Draw(list_data, list_pos, s_data)
    plt.pause(t)
    display.clear_output(wait=True)
file_obj.close()