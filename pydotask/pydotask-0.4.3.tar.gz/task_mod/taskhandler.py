import sys, os
import csv
import task_mod.styles.termcolor
import task_mod.styles.text_style as text
import subprocess

# Global

colors = task_mod.styles.termcolor.colors

# This is the Task List
task = []

def update_program(taskobj):
    with open('./tasks.csv','r') as task_data:
        csv_reader = csv.reader(task_data)

        #if
        next(csv_reader)

        for line in csv_reader:

            if line in taskobj:
                pass
            else:
                taskobj.append(line)

    task_data.close()

def addTask():

    #Adds Task

    taskname = input(colors.fg.green + colors.bold + 'Add Task : ' + colors.reset)
    taskpri = input(colors.fg.green + colors.bold + 'Priority : ' + colors.reset)

    with open('./tasks.csv','a') as tasks_data:
        csv_append = csv.writer(tasks_data)
        adt = [taskname, taskpri.lower()]
        csv_append.writerow(adt)

    tasks_data.close()

    print(colors.fg.green + 'Task Added!' + colors.reset)

def delTask(taskobj):

    #Deletes Task

    det = input(colors.fg.lightred + colors.bold + 'Delete Task : ' + colors.reset)

    #Checks if there is Task in list

    for task in taskobj:

        taskindex = task[0] #This is the task
        priindex = task[1] #This is the Priority

        if str(det) != str(taskindex):
            print(colors.fg.lightred + '{} not in the list'.format(det) + colors.reset)
        else:
            ask = str(input('Are you sure? [Y/n] : '))
            if ask == 'Y' or ask == 'y':

                with open('./tasks.csv','r') as tasks_read, open('./new_tasks.csv','w') as tasks_del:
                    reads = csv.reader(tasks_read)
                    writes = csv.writer(tasks_del)

                    writes.writerow(['Task','Priority'])
                    next(reads)

                    #Checks if det is not in the list, it doesnt write it to the new file.

                    for line in reads:
                        if det not in line:
                            writes.writerow(line)

                os.remove('./tasks.csv')
                os.rename('./new_tasks.csv','./tasks.csv')
                tasks_read.close()
                tasks_del.close()

                task.remove(taskindex)
                task.remove(priindex)
                print(colors.fg.lightred + '{} is removed'.format(det) + colors.reset)
                break

            else:
                print('\a')


    #elif str(det) == '$allTask':

    #    if ask == 'Y' or ask == 'y':
    #        print(colors.fg.lightred + 'All Task Deleted' + colors.reset)

    #    else :
    #        print('\n')

    #else:
    #    print(colors.fg.lightred + '{} not in the list'.format(det) + colors.reset)

def showTask(taskobj):

    #Add Priority!

    #Shows the Task
    if len(taskobj) == 0 or [] in taskobj :
        print(colors.fg.darkgrey + 'No Available Task!' + colors.reset)

        if [] in taskobj:
            taskobj.remove([])
    else:
        print(colors.fg.lightgreen + colors.bold + 'Available Task :' + colors.reset)
        for task in taskobj:

            taskindex = task[0] #This is the task
            priindex = task[1] #This is the Priority

            current_task = '\a {}'.format(str(taskindex))
            current_pri = '{}'.format(str(priindex))

            if current_pri == 'high':
                red_priority = colors.fg.red + '\a +'
                print(red_priority + colors.reset + current_task)
            elif current_pri == 'medium' or priindex == 'med':
                med_priority = colors.fg.yellow + '\a +'
                print(med_priority + colors.reset + current_task)
            elif current_pri == 'low':
                low_priority = colors.fg.green + '\a +'
                print(low_priority + colors.reset + current_task)
            else:
                print(colors.fg.darkgrey + '\a +' + colors.reset + current_task)




            #print(colors.fg.darkgrey + '\a +' + colors.fg.lightcyan + '{}'.format(str(task)) + colors.reset)

def helpme():

    text.command_help()
