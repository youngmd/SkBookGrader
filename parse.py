#!/usr/bin/env python

import os, sys
import pandas
import math
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
subjects = []
subjects_short = []
for idx, val in enumerate(data.columns.values):
    if idx not in reserved and not val.startswith('What do you'):
        subjects.append(val)
        if '.' in val:
            subshort = val[0]+val[-1]
        else:
            subshort = val[0]
        subjects_short.append(subshort)

gradeset = {
    'Done with Gusto - Wow.. they obviously put some work into that' : 4,
    'Done' : 3.66,
    'Done - Ish, Not quite, but sort of.' : 3,
    'Not done/Can\'t find' : 0,
}

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
            if r[whog].strip() == r[who].strip():
                continue
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
    print "Showing grades for %s  (%s)\n\n" % (s, cls)
    if len(v['graders']) == 0:
        print "%s was not graded by anyone" % s
        return
    # print "\t\t\t Graders\n\t\t\t=========="
    # print "\t\t\t%s" % '\t\t\t'.join(v['graders'])
    subgrades = {}
    feedback = {}
    elsewhere = {}
    notdone = {}

    for a in v['graders']:
        subgrades[a] = []
        feedback[a] = ""
        elsewhere[a] = []
        notdone[a] = []

    print "\n\nGrade Matrix\n============"
    print '%25s\t\t%s' % ('Name','\t'.join(subjects_short))

    for grader,val in v['grades'].iteritems():
        printout = "%25s\t" % grader
        for g,c in val.iteritems():
            grade = c
            if g.startswith('What do you'):
                feedback[grader] = grade
                continue
            if grade not in gradeset:
                elsewhere[grader].append(g)
                printout += "\tSE"
            else:
                subgrades[grader].append(gradeset[grade])
                if not gradeset[grade]:
                    notdone[grader].append(g)
                printout += "\t%s" % gradeset[grade]
        print printout

    print "\n\n\n=================\nHit enter to see grade averages",
    raw_input()
    os.system('clear')
    print "Showing grades for %s  (%s)\n\n" % (s, cls)

    for a in v['graders']:
        print "%25s:\t%2.2f (%s)" % (a, sum(subgrades[a])/len(subgrades[a]), len(subgrades[a]))

    print "\n\n\n=================\nHit enter to see feedbacks given/received",
    raw_input()
    os.system('clear')
    print "Showing grades for %s  (%s)\n\n" % (s, cls)

    print "\n\nFeedback received\n============"
    for a in v['graders']:
        print "%25s:\t%s" % (a, feedback[a])


    while(True):
        fgiven = 0
        print "\n\nFeedback given\n============"
        if len(v['gradees']) == 0:
            print "%s did not grade anyone" % s
        else:
            for graded, val in v['ggrades'].iteritems():
                for g, c in val.iteritems():
                    if g.startswith('What do you'):
                        if len(c.strip()) != 0:
                            fgiven += 1
                            print "%20s:\t%s" % (graded, c)

        print "\n\n\n=================\nEnter point value for feedbacks given (0-14): ",
        fgrade = raw_input()
        try:
            fgrade = float(fgrade)
            if fgrade <= 14.0 and fgrade >= 0:
                break
        except:
            pass
        os.system('clear')
        print "Invalid entry!  Please enter a number between 0 and 14.\n"

    print "\n\n\n=================\nHit enter to see any mismatches in Submitted Elsewhere grades",
    raw_input()
    os.system('clear')
    print "Showing grades for %s  (%s)\n\n" % (s, cls)

    noentries = True
    for sub in subjects:
        if sub.startswith('What do you'):
            continue
        present = []
        notpresent = []
        for a in v['graders']:
            if sub in elsewhere[a]:
                present.append(a)
            else:
                notpresent.append(a)

        if len(present) < len(v['graders']) and len(notpresent) < len(v['graders']):
            noentries = False
            print 'Assignment: %s' % sub
            print '\tReported as submitted elsewhere: %s' % ', '.join(present)
            print '\tGraded: %s\n\n' % ', '.join(notpresent)

    if noentries:
        print 'There are no mismatches in the grades given to this user'

    print "\n\n\n=================\nHit enter to see any mismatches in not done (0) grades",
    raw_input()
    os.system('clear')
    print "Showing grades for %s  (%s)\n\n" % (s, cls)

    noentries = True
    for sub in subjects:
        if sub.startswith('What do you'):
            continue
        present = []
        notpresent = []
        for a in v['graders']:
            if sub in notdone[a]:
                present.append(a)
            else:
                notpresent.append(a)

        if len(present) < len(v['graders']) and len(notpresent) < len(v['graders']):
            noentries = False
            print 'Assignment: %s' % sub
            print '\tReported as not done: %s' % ', '.join(present)
            print '\tGraded: %s\n\n' % ','.join(notpresent)

    if noentries:
        print 'There are no mismatches in the grades given to this user'


    print "\n\n\n=================\nHit enter to see results",
    raw_input()
    header = "Showing grades for %s  (%s)\n\n" % (s, cls)
    finalgrade = print_summary(header, v['graders'], subgrades, fgiven, fgrade, [])
    # os.system('clear')
    # print "Showing grades for %s  (%s)\n\n" % (s, cls)
    #
    # print "Summary\n===========\n"
    # totalgrades = 0
    # numgrades = 0
    # for a in v['graders']:
    #     totalgrades += sum(subgrades[a])
    #     numgrades += len(subgrades[a])
    #
    # print "Average grade is %2.2f based on %s grades from %s graders" % (totalgrades/numgrades, numgrades, len(v['graders']))
    # print "Student gave %s evaluations\n\n" % (fgiven)

    return finalgrade

def print_summary(header, graders, subgrades, fgiven, fgrade, ignored = []):
    os.system('clear')
    print header
    totalgrades = 0
    numgrades = 0
    for a in graders:
        if a in ignored:
            continue
        totalgrades += sum(subgrades[a])
        numgrades += len(subgrades[a])


    for idx, a in enumerate(graders):
        if a in ignored:
            ignore_string = "(ignored)"
        else:
            ignore_string = ""
        print "(%s) - %-25s %2.2f (%s) %s" % (idx, a, sum(subgrades[a])/len(subgrades[a]), len(subgrades[a]), ignore_string)

    overall_avg = totalgrades / numgrades
    print "\n\nAverage grade is %2.2f based on %s grades from %s graders" % (overall_avg, numgrades, len(graders) - len(ignored))
    print "Student gave %s evaluations and earned %2.2f points\n\n" % (fgiven, fgrade)

    finalgrade = (math.ceil(overall_avg * 9) + fgrade)
    print "Total Points: %2.2f/50" % finalgrade

    print "\n============\nSelect student to ignore/include and recalculate, or hit enter to finish: ",
    choice = raw_input()
    try:
        choice = int(choice)
        if choice <= len(graders):
            chosen = graders[choice]
            try:
                idx = ignored.index(chosen)
                ignored.pop(idx)
            except:
                ignored.append(chosen)
        else:
            return finalgrade
    except:
        return finalgrade
    finalgrade = print_summary(header, graders, subgrades, fgiven, fgrade, ignored)
    return finalgrade







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


def student_menu(cls, class_chosen, finalgrades):
    stds = cls.keys()
    print "\n\n%s\n===================\n" % class_chosen
    for s in range(len(stds)):
        if stds[s] in finalgrades.keys():
            grade_out = finalgrades[stds[s]]
        else:
            grade_out = ''
        print "(%s) - %-25s\t%s" % (s, stds[s], grade_out)
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

finalgrades = {}

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
        if class_chosen not in finalgrades.keys():
            finalgrades[class_chosen] = {}
    except:
        continue

    while loop2 == 1:
        os.system('clear')
        student_options = student_menu(full_grades[class_chosen], class_chosen, finalgrades[class_chosen])
        tempin = raw_input()
        if tempin == 'c':
            loop2 = 0
            continue
        if tempin == 'q':
            sys.exit()
        try:
            choice = int(tempin)
            std_chosen = student_options[choice]
            os.system('clear')
            stdgrade = print_student_grades(full_grades, class_chosen, std_chosen)
            finalgrades[class_chosen][std_chosen] = stdgrade
            # print "\n\n\n=================\nHit enter to return to grade selection...",
            # raw_input()
        except Exception, e:
            print e
            raw_input()
            continue

        # while loop3 == 1:
        #     os.system('clear')
        #     print_options = print_menu(std_chosen)
        #     tempin = raw_input()
        #     if tempin == 'c':
        #         loop3 = 0
        #         continue
        #     if tempin == 'q':
        #         sys.exit()
        #     try:
        #         os.system('clear')
        #         choice = int(tempin)
        #         if choice:
        #             print_student_gradees(full_grades, class_chosen, std_chosen)
        #             print "\n\n\n=================\nHit enter to return to grade selection...",
        #             raw_input()
        #         else:
        #             print_student_grades(full_grades, class_chosen, std_chosen)
        #             print "\n\n\n=================\nHit enter to return to grade selection...",
        #             raw_input()
        #     except:
        #         continue


