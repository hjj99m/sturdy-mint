from os import walk
from distutils.util import strtobool
import fnmatch, os.path, configparser, hashlib, re

################################################
config = configparser.ConfigParser()
config.read('conf.txt')

log = config['CONDITION']['log']
tpl_dir = config['CONDITION']['tpl_dir']
real_dir = config['CONDITION']['real_dir']
target_fexts = config['CONDITION']['target_fexts'].split(',')
target_dir = config['CONDITION']['target_dir']
#strict = strtobool(config['CONDITION']['strict'])
accurate = strtobool(config['CONDITION']['accurate'])
result_dir = config['CONDITION']['result_dir']
result_file = config['CONDITION']['result_file']


################################################
def my_check_ext(filename, extnames):
    ''' haha '''
    flag = False
    for ext in extnames:
        if fnmatch.fnmatch(filename, ext):
            flag = True
    return flag
################################################
def find_whole_word(word, text, accurate=False):
    result = False
    if accurate:
        if re.search(r'\b' + word + r'\b', text):
            result = True
    else:
        if word in text:
            result = True
    return result
################################################
def analyze_log(log_name='', tpl_dir='', real_dir='', res_dir='./'):
    ''' '''
    try:
        l = open(log_name, 'r')
        err_dict = dict()
        mm_dict = dict()
        err_msg = ''
        begin_tag = 'compiled/c_'
        end_tag = '.php on line'
        exts = ['*.php','*.tpl']
        nomatch = set()

        for line in l.readlines():
            if begin_tag in line and end_tag in line:
                t_line = str(line)
                bt = t_line.find(begin_tag) + len(begin_tag)
                et = t_line.find(end_tag)
                tt = t_line.find('[error]')
                yt = t_line.find(' in /')
                ut = t_line.find('Undefined index:')
                md5_str = t_line[bt:et]
                uindex = t_line[ut+len('Undefined index:'):yt].strip()
                err_msg = t_line[tt+len('[error]'):yt].strip() + \
                          ' [line ' + t_line[et+len(end_tag):].strip() + ']'
                if md5_str in list(mm_dict.keys()):
                    mm_dict[md5_str]['err_msg'].add(err_msg)
                    mm_dict[md5_str]['uindex'].add(uindex)
                else:
                    mm_dict[md5_str] = {'err_msg':set([err_msg]), 'md5': md5_str,
                                        'file':'', 'uindex': set([uindex])}
            else:
                nomatch.add(line[27:])

        ff = open(res_dir + os.path.basename(log_name) + '.nomatch.txt', mode='w')
        ff.write("".join(sorted(nomatch)))
        ff.close()
        nomatch = None

    except:
        print('[Analyze Log] cannot open file:' + log)

    fn = ''
    tp_fn = ''
    for (dirpath, dirnames, filenames) in walk(real_dir):
        num = len(filenames)
        for i in range(0, num):
            fn = str(dirpath) + "/" + str(filenames[i])
            tp_fn = tpl_dir  + dirpath[len(real_dir):] + '/' + str(filenames[i])
            if my_check_ext(fn, exts) and os.path.exists(fn):
                tmp_md5 = hashlib.md5(tp_fn.encode('utf-8')).hexdigest()
                if tmp_md5 in list(mm_dict.keys()):
                    mm_dict[tmp_md5]['file'] = tp_fn
            else:
                pass

    return mm_dict
################################################
def write_analyze_log(mm_dict, res_file='md5result.txt'):
    ff = open( result_file +'_Test.txt', mode='w')
    ff.write('Total: ' + str(len(mm_dict.keys())) + ' file(s)\n')
    ff.write('------------------------------------\n')
    for m in list(mm_dict.keys()):
        ff.write("md5: " + m + "\nfile: " + mm_dict[m]['file'] + "\nUndefined index: " + ",".join(mm_dict[m]['uindex']) + "\n==Error Msg== \n" +  "\n".join(mm_dict[m]['err_msg']) + "\n-----------------------------\n")
    ff.close()
################################################
def seek_tags(tdict, fexts=[], target_dir='', accuracy=True):
    ''' hooray '''
    fdict = dict()
    fn = ''
    tags = tdict['uindex']
    tpl = os.path.basename(tdict['file'])
    cannot_open_msg = ''
    for (dirpath, dirnames, filenames) in walk(target_dir):
        num = len(filenames)

        for i in range(0, num):
            fn = str(dirpath) + "/" + str(filenames[i])
            if my_check_ext(fn, fexts) and os.path.exists(fn):
                try:
                    f = open(fn, 'r')
                    tmp = set()

                    for line in f.readlines():
                        if find_whole_word(tpl, line, accuracy):
                            tmp.add(tpl)
                        for tag in tags:
                            if find_whole_word(tag, line, accuracy) and tag not in tmp:
                                tmp.add(tag)
                                fdict[fn] = tmp
                except:
                    cannot_open_msg += '[Seek Tag] ' + fn + "\n"

        else:
            pass

    else:
        return fdict, cannot_open_msg
################################################
def write_dict_to_file(fdict,fname='md5result.txt'):
    ''' hooray '''
    try:
        ff = open(fname, mode='w')
        ff.write('Total: ' + str(len(mm_dict.keys())) + ' file(s)\n')
        ff.write('------------------------------------\n')
        for m in list(mm_dict.keys()):
            ff.write("md5: " + m + ".php\nfile: " + mm_dict[m]['file'] + 
            "\nUndefined index: " + ",".join(mm_dict[m]['uindex']) + 
            "\n== Error Msg == \n" +  "\n".join(mm_dict[m]['err_msg']) + 
            "\n== Maybe Relatived File(s) ==\n")
            for mm in list(mm_dict[m]['search'].keys()):
                ff.write(mm +  " ##### (" +
                ",".join(mm_dict[m]['search'][mm]) + ")\n")
            ff.write("\n-------------------------------------------\n")
        ff.close()
        return True
    except:
        return False
################################################
mm_dict = analyze_log(log, tpl_dir, real_dir)
##### Test
#write_analyze_log(mm_dict, result_file)
######
except_msg = ''
for m in list(mm_dict.keys()):
    mm_dict[m]['search'], tmp_msg = seek_tags(mm_dict[m], target_fexts, target_dir)
    except_msg += tmp_msg
write_dict_to_file(mm_dict, result_file)

ff = open(result_dir + result_file + '.cannot_open.txt', mode='w')
ff.write(except_msg)
ff.close()
except_msg = None