#!/usr/bin/env python

import os, sys
import pandas
from collections import OrderedDict

infile = sys.argv[1]
data = pandas.read_csv(infile)

classes = {}
for i in range(len(data['Who Are You'])):
    student = data['Who Are You'][i].strip()
    tmpclass = data['What class are you in'][i]
    if not tmpclass in classes:
        classes[tmpclass] = []

    if not student in classes[tmpclass]:
        classes[tmpclass].append(student)

# for key,value in classes.iteritems():
#     print key, len(value)
who = data.columns.get_loc('Who Are You')
whog = data.columns.get_loc('Whose work are you grading?')
classname = data.columns.get_loc('What class are you in')
timestamp = data.columns.get_loc('Timestamp')

reserved = [who, whog, classname, timestamp]

full_grades = {}
for cls,std in classes.iteritems():
    full_grades[cls] = {}
    #print 'Working on Class %s' % cls
    for s in std:
        full_grades[cls][s] = {}
        full_grades[cls][s]['graders'] = []
        full_grades[cls][s]['grades'] = {}
        full_grades[cls][s]['gradees'] = []
        full_grades[cls][s]['ggrades'] = {}
        for index, r in data.iterrows():
            if r[classname] != cls:
                continue
            #print "working on row %s" % index
            if r[whog].strip() == s:
                #print r[whog].strip()
                grade_dict = OrderedDict()
                for idx,val in r.iteritems():
                    #print data.columns.get_loc(idx)
                    if data.columns.get_loc(idx) in reserved:
                        #print "Removing reserved keyword %s" % idx
                        continue
                    grade_dict[idx] = val
                full_grades[cls][s]['graders'].append(r[who])
                full_grades[cls][s]['grades'][r[who]] = grade_dict

            if r[who].strip() == s:
                #print r[whog].strip()
                grade_dict = OrderedDict()
                for idx,val in r.iteritems():
                    #print data.columns.get_loc(idx)
                    if data.columns.get_loc(idx) in reserved:
                        #print "Removing reserved keyword %s" % idx
                        continue
                    grade_dict[idx] = val
                full_grades[cls][s]['gradees'].append(r[whog])
                full_grades[cls][s]['ggrades'][r[whog]] = grade_dict


def print_student_grades(full_grades, cls, s):
    v = full_grades[cls][s]
    print "Showing grades for %s  (%s)" % (s, cls)
    if len(v['graders']) == 0:
        print "%s was not graded by anyone" % s
        return
    # print "\t\t\t Graders\n\t\t\t=========="
    # print "\t\t\t%s" % '\t\t\t'.join(v['graders'])
    print "Assignment\n=========="
    for key,val in v['grades'].iteritems():
        for g,c in val.iteritems():
            print "%s\n=========" % g
            for a in v['graders']:
                print "%s\t\t\t%s" % (a, v['grades'][a][g])
            print ""
        return

def print_student_gradees(full_grades, cls, s):
    v = full_grades[cls][s]
    print "Showing grades given by %s  (%s)" % (s, cls)
    if len(v['gradees']) == 0:
        print "%s did not grade anyone" % s
        return
    # print "\t\t\t Graders\n\t\t\t=========="
    # print "\t\t\t%s" % '\t\t\t'.join(v['graders'])
    print "Assignment\n=========="
    for key,val in v['ggrades'].iteritems():
        for g,c in val.iteritems():
            print "%s\n=========" % g
            for a in v['gradees']:
                print "%s\t\t\t%s" % (a, v['ggrades'][a][g])
            print ""
        return


def class_menu(fg):
    classes = fg.keys()
    print "\n\nChoose from the following:\n===================\n"
    for c in range(len(classes)):
        print "(%s) - %s" % (c,classes[c])

    print "----------"
    print "(q) - Quit"
    print "==========\n"
    print "\n============\nSelect class: ",
    return classes


def student_menu(cls, class_chosen):
    stds = cls.keys()
    print "\n\n%s\n===================\n" % class_chosen
    for s in range(len(stds)):
        print "(%s) - %s" % (s, stds[s])
    print "----------"
    print "(c) - Return to class selection"
    print "(q) - Quit"
    print "==========\n"
    stds.append('c')
    stds.append('q')
    print "\n============\nSelect student: ",
    return stds

def print_menu(std):
    print "\n\n%s\n===================\n" % std
    print "(0) - See Grades Received"
    print "(1) - See Grades Given"
    print "----------"
    print "(c) - Return to student selection"
    print "(q) - Quit"
    print "==========\n"
    print "\n============\nSelect Grade Type: ",
    return [0,1,'c','q']

loop = 1
loop2 = 1
while loop == 1:
    os.system('clear')
    choice = None
    loop2 = 1
    class_options = class_menu(full_grades)
    tempin = raw_input()
    if tempin == 'q':
        os.system('clear')
        sys.exit(0)
    try:
        choice = int(tempin)
        class_chosen = class_options[choice]
    except:
        continue

    while loop2 == 1:
        loop3 = 1
        os.system('clear')
        student_options = student_menu(full_grades[class_chosen], class_chosen)
        tempin = raw_input()
        if tempin == 'c':
            loop2 = 0
            continue
        if tempin == 'q':
            sys.exit()
        try:
            choice = int(tempin)
            std_chosen = student_options[choice]
        except:
            continue

        while loop3 == 1:
            os.system('clear')
            print_options = print_menu(std_chosen)
            tempin = raw_input()
            if tempin == 'c':
                loop3 = 0
                continue
            if tempin == 'q':
                sys.exit()
            try:
                os.system('clear')
                choice = int(tempin)
                if choice:
                    print_student_gradees(full_grades, class_chosen, std_chosen)
                    print "\n\n\n=================\nHit enter to return to grade selection...",
                    raw_input()
                else:
                    print_student_grades(full_grades, class_chosen, std_chosen)
                    print "\n\n\n=================\nHit enter to return to grade selection...",
                    raw_input()
            except:
                continue


