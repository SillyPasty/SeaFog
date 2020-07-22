from matplotlib import pyplot as plt
from datetime import datetime

def anal_error_data(test_X, predicted_Y, test_Y):
    clock_cnt = [0 for x in range(48)]

    for i, single_X in enumerate(test_X):
        timestamp = single_X[-1]
        dt = datetime.fromtimestamp(timestamp)

        if predicted_Y[i] != test_Y[i]:
            hour = dt.hour
            minute = dt.minute
            shift = 0
            if minute < 15: shift = 0
            elif minute > 45: shift = 2
            else: shift = 1
            clock_cnt[(2 * hour + shift) % 48] += 1

    return clock_cnt
    
    


def plot_error_time(clock_cnt):

    x_axis_labels = ['0:00', '0:30', '1:00', '1:30', '2:00', '2:30', '3:00', '3:30', 
                        '4:00', '4:30', '5:00', '5:30', '6:00', '6:30', '7:00', '7:30',
                        '8:00', '8:30', '9:00', '9:30', '10:00', '10:30', '11:00', '11:30',
                        '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30',
                        '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30',
                        '20:00', '20:30', '21:00', '21:30', '22:00', '22:30', '23:00', '23:30']
    plt.title('Analysis')
    plt.bar(x_axis_labels, clock_cnt)
    plt.xticks(rotation=270)
    plt.show()