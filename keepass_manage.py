#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, re, sys, string, random
import platform, getopt
import pkg_resources
pkg_resources.require("pykeepass==4.0.1")
from datetime import datetime, timedelta
from dateutil import tz
from logging import error, logThreads, warn
from pykeepass import PyKeePass
import traceback

PROGRAM = 'keepass-manage.py'
MINIMAL_VERSION = 3.6 # of Python for Ansible
AUTHOR = 'Author1'
ROLE = 'Engineer'
DATE = '2021-08-13'
VERSION = 1.03

DEBUG = False
# DEBUG = True
verbose = True
special_char = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
programfile = sys.argv[0]
programfile = programfile.replace('.py', '')
programfile = programfile.replace('.pyc', '')
programfile = programfile.replace('.bin', '')
programfile = programfile.replace('.exe', '')

def help_lite():
    usage = ('''
    the basic command possibilities are generally used :
        Get activated entry :
            %s -m <master password> -f <file keepass.kdbx> -s <server> -u <user name> -c get_entry

        Add entry :
            %s -m <master password> -f <file keepass.kdbx> -s <server> -u <user name> -c add_entry

        Modify password activated entry :
            %s -m <master password> -f <file keepass.kdbx> -s <server> -u <user name> -c modify_pw_entry

        Deactivate entry with set expiration date :
            %s -m <master password> -f <file keepass.kdbx> -s <server> -u <user name> -c disable

        Reactivate the entry with the expiration date set for one year :
            %s -m <master password> -f <file keepass.kdbx> -s <server> -u <user name> -c enable

        Set the expiration date of the activated entry :
            %s -m <master password> -f <file keepass.kdbx> -s <server> -u <user name> -date <number of days>D -c change_date

    or more usage :
        %s --help

    ''') % (programfile, programfile, programfile, programfile, programfile, programfile, programfile)
    print(usage)

def usage():
    usage = ('''
  HELP:

    NAME : %s
    DATE : %s
    VERSION : %s
    MINIMAL PYTHON VERSION : %s

    SYNOPSIS:

    DESCRIPTION:
        This program can create a new entry user/password
            can modify a password of entry
            can lookup an entry
        Mandatory arguments :
        -m[aster] <master_password>
        -f[ile] <kdbx file V2.x of Keepass database>
        -s[server] <server_name entry>
        -u[sername] <username entry>
        -c[ommand] <add_entry>|<get_entry>|<modify_pw_entry>|<enable>|<disable>|<expiration_date>|<export>

        Optional arguments :
        -l[ength] <value, in default 16>
        -d[date] <expirtion date in format '2021-08-13T12:00[:00]'> or [nn]d number of days
        --special_char <special characters>, in default '%s'


        The commands of program are :
        - add_entry
        - get_entry
        - modify_pw_entry
        - enable
        - disable
        - expiration_date
        - export

        the optional arguments of program are :
        - special_characters
        - length of password
        -

        New feature in future:
        - drop_entry
        - batch

        in case sensistive

    KNOWN BUGS:


    AUTHOR:
        %s - %s

    COPYRIGHT:
        All rights reserved. ENTERPRISE - 2021

    ERROR LEVELS :
        0 : Success
        1 : Warning
        2 : Error
        3 : Fatal error

    SEE ALSO:


    ''') % (PROGRAM, DATE, VERSION, MINIMAL_VERSION, string.punctuation, AUTHOR, ROLE)
    print(usage)

def is_ansible():
    '''
    Check under Ansible Runtime with a minimal version of Python
    '''
    if DEBUG: return True ### <<< Must to delete this !
    return True ### <<< Must to delete this !
    # TODO : check human_value 3.6.8 to 3.6 !!
    # if os.getenv('ansible_python_version'):
    #     if float(os.getenv('ansible_python_version')) >= MINIMAL_VERSION :
    #         return True
    #     else:
    #         return False
    # else:
    #     return False

def check_args(nb, opts, args):
    '''
    Checking number of arguments
    '''
    if len(opts) <= nb: # number of mandatory arguments
        help_lite()
        return(True)
    else:
        return(False)

def open_kdbx(file, pwd):
    '''
    Open database KDBX v2
    '''
    try:
        if verbose: print('>>> Openning Database KDBX V2 ...')
        return(PyKeePass(file, password = pwd))
    except:
        if verbose: error(">>> Sorry, database not found !")
        sys.exit(2)

def generator_pwd(length = 16, special_char = string.punctuation, mandatory_spec = 0):
    '''
    Generator password random with length password or/and specials characcters basing security rule
        so in default are : '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    '''
    # TODO: checking for one or more character to do
    password = string.ascii_letters + string.digits + special_char
    random.seed = (os.urandom(1024))
    return(''.join(random.choice(password) for i in range(length)))

def convert_datetime(self):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = self
    utc = utc.replace(tzinfo=from_zone)
    cet = utc.astimezone(to_zone)
    return (cet.strftime('%Y-%m-%d %H:%M:%S'))

def check_format_date(self):
    try:
        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        # cet = datetime.strptime(self,'%Y.%m.%dT%H:%M:%S')
        # cet = cet.replace(tzinfo=from_zone)
        # utc = cet.astimezone(to_zone)
        # return (utc.strftime('%Y-%m-%d %H:%M:%S'))
        return(self)
    except:
        traceback.print_exc(file=sys.stdout)
        msg = '>>> Sorry, the date must be use format yyyy-mm-ddTHH:MM[:00] or (number of day)d !'
        warn(msg)
        help_lite()
        return(2)

def Wprint(file, self):
    with open(file, 'a') as f:
        f.write(self + '\n')
        f.close()

###
def main(argv):
    '''
    Main program
    '''

    DEBUG = False
    # DEBUG = True
    verbose = True
    output = ''
    command_used = ['get_entry', 'add_entry', 'modify_pw_entry', 'enable', 'disable', 'expiration_date', 'export']
    length_pwd = 16 # characters length of generated password in default
    # special_char = ''
    master_password = servername = file_kdbx = username = command = ldate = ''


    try:
        optlist, args = getopt.getopt(argv, "ho:m:f:s:u:l:c:",
                    [
                        "master=",
                        "file=",
                        "server=",
                        "username=",
                        "length=",
                        "date=",
                        # "special_char=",
                        # "special_characters=",
                        "command=",
                        "output=",
                        "silence",
                        "DEBUG",
                        "help"
                    ])
        if DEBUG: ### <<< Must to delete this !
            print("n2 arguments number found\narg# : %s\n\n" % len(optlist))
            print("opts:%s" % (optlist))
            print("args:%s" % (args))

    except getopt.GetoptError as err:
        if DEBUG: ### <<< Must to delete this !
            print("n1 arguments number found\narg# : %s\n\n" % len(sys.argv))
            print("Args found : %s\n\n" % (sys.argv))
        warn(err)  # will print something like "option --example not recognized"
        help_lite()
        return(2)

    if optlist == '' and len(args) > 0:
        optlist = args
        args = ''

    for opt, arg in optlist:
        opt.encode('ascii', 'ignore')
        arg.encode('ascii', 'ignore')
        if opt in ("-h", "--help"):
            usage()
            return(0)
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt == "--silence":
            verbose = False
        elif opt == "--DEBUG":
            DEBUG = True
            verbose = True
        elif opt in ("-m", "--master"):
            master_password = arg
        elif opt in ("-f", "--file"):
            file_kdbx = arg
        elif opt in ("-s", "--server"):
            servername = arg
        elif opt in ("-u", "--username"):
            username = arg
        elif opt in ("-c", "--command"):
            command = arg
        elif opt in ("-l", "--length"):
            length_pwd = int(arg)
        elif opt in ("-l", "--date"):
            ldate = arg
        # elif opt in ("--special_char", "--special_characters"):
        #     special_char = str(arg)
        elif opt in ("-o", "--output"):
            output = str(arg)
        else:
            assert False, "unhandled option"

    if command == '':
        msg = '>>> Sorry, command missing from the prompt !'
        warn(msg)
        help_lite()
        return(2)

    if not command in command_used:
        msg = ('>>> Sorry, the {%s} command is not recognized !') % (command)
        warn(msg)
        help_lite()
        return(2)

    if command == "get_entry":
        if master_password == '' or file_kdbx == '' or servername == '' or username == '':
            if verbose: warn('>>> Sorry, arguments are missing !')
            help_lite()
            return(1)
        else:
            if check_args(4, optlist, args):
                help_lite()
                return(1)
            kdbx = open_kdbx(file_kdbx, master_password)
            try:
                entry = kdbx.find_entries(title = servername, first = False)
                count = 0
                for srv in range(len(entry)):
                    if username == entry[srv].username and entry[srv].expired == False:
                        count += 1
                        if verbose: print("Server: %s, Username: %s, Password: \'%s\', Notes: \'%s\'"
                                % (entry[srv].title, entry[srv].username, entry[srv].password, entry[srv].notes))
                if count == 0:
                    if verbose:
                        msg = ('>>> Sorry, this %s user does not exist') %(username)
                        warn(msg)
                    return(1)
                else:
                    return(0)
            except:
                if verbose:
                    msg = ('>>> Sorry, this %s servername does not exist') %(servername)
                    warn(msg)
                return(1)

    elif command == "export":
        if master_password == '' or file_kdbx == '':
            if verbose: warn('>>> Sorry, arguments are missing !')
            help_lite()
            return(1)
        else:
            if check_args(2, optlist, args):
                help_lite()
                return(1)
            warn('>>> Be careful, you have sensitive data such as the clear password, do you want to continue exporting all the data ?')
            if DEBUG:
                req = 'YES'
            else:
                req = input('[No]/YES >>> ')

            if req == 'YES':
                kdbx = open_kdbx(file_kdbx, master_password)
                if output == '':
                    logfile = programfile + '.log'
                else:
                    logfile = output

                # if os.path.exists(logfile) : #and os.access(logfile, os.W_OK):
                #     os.unlink(logfile)
                # else:
                #     msg = ('>>> Sorry, cannot remove %s file') % (logfile)
                #     warn(msg)
                #     return(2)

                try:
                    entry = kdbx.entries
                    count = 0
                    for srv in range(len(entry)):
                        if entry[srv].group.is_root_group:
                            count += 1
                            expiration = convert_datetime(entry[srv].expiry_time)
                            if entry[srv].expires:
                                if entry[srv].expired:
                                    expiration = '***' + expiration + '***'
                            else:
                                expiration = 'None'
                            if DEBUG: print("Server: %s, Username: %s, Password: \'%s\', Expiration: \'%s\', Notes: \'%s\'"
                                    % (entry[srv].title, entry[srv].username, entry[srv].password, expiration, entry[srv].notes))
                            if verbose: Wprint(logfile, "Server: %s, Username: %s, Password: \'%s\', Expiration: \'%s\', Notes: \'%s\'"
                                    % (entry[srv].title, entry[srv].username, entry[srv].password, expiration, entry[srv].notes))
                    if count == 0:
                        if verbose: warn('>>> Sorry, the database seems empty or they are out of the root folder !')
                        return(1)
                    else:
                        print('>>> %s entries found.' % (count))
                        return(0)
                except:
                    if verbose: warn('>>> Sorry, no entry exists !')
                    return(1)
            else:
                print('>>> Sorry, operation canceled !')

    # TODO : set expiration date one year in default
    elif command == "add_entry":
        if master_password == '' or file_kdbx == '' or servername == '' or username == '':
            if verbose: warn('>>> Sorry, arguments are missing !')
            help_lite()
            return(1)
        else:
            if check_args(4, optlist, args):
                help_lite()
                return(1)
            kdbx = open_kdbx(file_kdbx, master_password)
            try:
                entry = kdbx.find_entries(title = servername, first = False)
                count = 0
                for srv in range(len(entry)):
                    if username == entry[srv].username and entry[srv].expired == False:
                        count += 1
                        if DEBUG: print("Server: %s, Username: %s, Password: \'%s\', Notes: \'%s\'"
                                % (entry[srv].title, entry[srv].username, entry[srv].password, entry[srv].notes))
                if count == 0:
                    password = generator_pwd(length_pwd) #, special_char)
                    entry = kdbx.add_entry(kdbx.root_group, servername, username, password)
                    entry.password = password
                    entry.notes = 'this account has been created by automate.'
                    if DEBUG: print("Server: %s, Username: %s, Password: \'%s\', Notes: \'%s\'"
                            % (entry.title, entry.username, entry.password, entry.notes))
                    kdbx.save()
                    if verbose: print(">>> Done.")
                    return(0)
                else:
                    if verbose: warn('>>> Sorry, this entry already exists')
                    return(1)
            except:
                if verbose: warn('>>> Sorry, it already exists!')
                return(1)

    elif command == "modify_pw_entry":
        if master_password == '' or file_kdbx == '' or servername == '' or username == '':
            if verbose: warn('>>> Sorry, arguments are missing !')
            help_lite()
            return(1)
        else:
            if check_args(4, optlist, args):
                help_lite()
                return(1)
            kdbx = open_kdbx(file_kdbx, master_password)
            try:
                entry = kdbx.find_entries(title = servername, first = False)
                count = 0
                password = generator_pwd(length_pwd) #, special_char)
                for srv in range(len(entry)):
                    if username == entry[srv].username and entry[srv].expired == False:
                        count += 1
                        entry[srv].save_history()
                        entry[srv].mtime = datetime.today()
                        entry[srv].password = password
                        if DEBUG: print("Server: %s, Username: %s, Password: \'%s\', Notes: \'%s\'"
                                % (entry[srv].title, entry[srv].username, entry[srv].password, entry[srv].notes))
                        entry[srv].notes = 'this password has been changed by automate see in history folder of entry.'
                        kdbx.save()
                        if verbose: print(">>> Done.")
                if count == 0:
                    if verbose:
                        msg = ('>>> Sorry, this %s user does not exist') %(username)
                        warn(msg)
                    return(1)
                else:
                    return(0)
            except:
                if verbose:
                    msg = ('>>> Sorry, this %s servername does not exist') %(servername)
                    warn(msg)
                return(1)

    elif command == "disable":
        if master_password == '' or file_kdbx == '' or servername == '' or username == '':
            if verbose: warn('>>> Sorry, arguments are missing !')
            help_lite()
            return(1)
        else:
            if check_args(4, optlist, args):
                help_lite()
                return(1)
            kdbx = open_kdbx(file_kdbx, master_password)
            try:
                entry = kdbx.find_entries(title = servername, first = False)
                count = 0
                for srv in range(len(entry)):
                    if username == entry[srv].username and entry[srv].expired == False:
                        count += 1
                        entry[srv].save_history()
                        entry[srv].mtime = datetime.today()
                        entry[srv].expires = True
                        entry[srv].expiry_time = past_time = datetime.now() - timedelta(days=1)
                        if DEBUG: print("Server: %s, Username: %s, Notes: \'%s\'"
                                % (entry[srv].title, entry[srv].username, entry[srv].notes))
                        entry[srv].notes = 'this entry has been set expired by automate see in history folder of entry.'
                        kdbx.save()
                        if verbose: print(">>> Done.")
                if count == 0:
                    if verbose:
                        msg = ('>>> Sorry, this %s user does not exist') %(username)
                        warn(msg)
                    return(1)
                else:
                    return(0)
            except:
                if verbose:
                    msg = ('>>> Sorry, this %s servername does not exist or disable') %(servername)
                    warn(msg)
                return(1)

    elif command == "enable":
        if master_password == '' or file_kdbx == '' or servername == '' or username == '':
            if verbose: warn('>>> Sorry, arguments are missing !')
            help_lite()
            return(1)
        else:
            if check_args(4, optlist, args):
                help_lite()
                return(1)
            kdbx = open_kdbx(file_kdbx, master_password)
            try:
                entry = kdbx.find_entries(title = servername, first = False)
                count = 0
                for srv in range(len(entry)):
                    if username == entry[srv].username and entry[srv].expired == True:
                        count += 1
                        entry[srv].save_history()
                        entry[srv].mtime = datetime.today()
                        entry[srv].expiry_time = entry[srv].mtime.replace(year=(entry[srv].mtime.year + 1))
                        entry[srv].expires = True
                        if DEBUG: print("Server: %s, Username: %s, Notes: \'%s\'"
                                % (entry[srv].title, entry[srv].username, entry[srv].notes))
                        entry[srv].notes = 'this entry has been set unexpired for one year by automate see in history folder of entry.'
                        kdbx.save()
                        if verbose: print(">>> Done.")
                if count == 0:
                    if verbose:
                        msg = ('>>> Sorry, this %s user is already enable') %(username)
                        warn(msg)
                    return(1)
                else:
                    return(0)
            except:
                if verbose:
                    msg = ('>>> Sorry, this %s servername does not exist') %(servername)
                    warn(msg)
                return(1)

    elif command == "expiration_date":
        if master_password == '' or file_kdbx == '' or servername == '' or username == '' or ldate == '':
            if verbose: warn('>>> Sorry, arguments are missing !')
            help_lite()
            return(1)
        else:
            if check_args(5, optlist, args):
                help_lite()
                return(1)
            kdbx = open_kdbx(file_kdbx, master_password)
            if re.search('T', ldate):
                ldate = ldate.replace('T', ' ')
                # ldate = check_format_date(ldate)
                ldate = datetime.strptime(ldate, '%Y-%m-%d %H:%M:%S')
            elif re.search('D', ldate):
                ldate = re.search(r'\d+', ldate)
                ldate = int(ldate.group())
                print(ldate)
                ldate = datetime.now() + timedelta(days=ldate)
                print(ldate)
            else:
                msg = '>>> Sorry, Wrong format date !'
                warn(msg)
                help_lite()
                return(1)
            if ldate < datetime.today():
                msg = '>>> Sorry, this date must be over of today !'
                warn(msg)
                return(1)
            try:
                entry = kdbx.find_entries(title = servername, first = False)
                count = 0
                for srv in range(len(entry)):
                    if username == entry[srv].username and entry[srv].expired == False:
                        count += 1
                        entry[srv].save_history()
                        entry[srv].mtime = datetime.today()
                        entry[srv].expires = True
                        entry[srv].expiry_time = ldate
                        if DEBUG: print("Server: %s, Username: %s, Notes: \'%s\'"
                                % (entry[srv].title, entry[srv].username, entry[srv].notes))
                        entry[srv].notes = 'this entry has been set a new expiration date by automate see in history folder of entry.'
                        kdbx.save()
                        if verbose: print(">>> Done.")
                if count == 0:
                    if verbose:
                        msg = ('>>> Sorry, this %s user does not exist') %(username)
                        warn(msg)
                    return(1)
                else:
                    return(0)
            except:
                if verbose:
                    msg = ('>>> Sorry, this %s servername does not exist or disable') %(servername)
                    warn(msg)
                return(1)

    # Disabled at this moment due weak security
    elif command == "delete_entry" and False: # if need to delete before rewrite a new account
        try:
            entry = kdbx.find_entries(title = servername, first = True)
            kdbx.delete_entry(entry)
        except:
            if verbose: warn('>>> Sorry,it does not exist')

    else:
        warn(">>> Noting to do ;) !")
        return(1)

    return(0)


rc = 0
print(">>> Starting...")
if __name__ == '__main__':
    if platform.system() != "Windows":
        if is_ansible():
            argv = sys.argv[1:]
            argv = ' '.join(map(str, argv))
            argv = re.sub(r'\s+' ,' ', argv)
            argv = list(argv.split(" "))
            rc = main(argv)
        else:
            msg = '>>> Sorry, must be to execute under Ansible runtime with a minimal version of Python !' + str(MINIMAL_VERSION)
            warn(msg)
            rc = 1
    else:
        msg = '>>> Sorry, this program cannot run on Windows !'
        warn(msg)
        rc = 3

print(">>> End.")
sys.exit(rc)
