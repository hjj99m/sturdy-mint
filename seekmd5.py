from os import walk
import fnmatch, os.path, configparser, hashlib
################################################
def my_check_ext(filename, extnames):
    ''' haha '''
    flag = False
    for ext in extnames:
        if fnmatch.fnmatch(filename, ext):
            flag = True
    return flag
################################################
config = configparser.ConfigParser()
config.read('condmd5.txt')

log = config['CONDITION']['log_file']
begin_tag = config['CONDITION']['begin_tag']
end_tag = config['CONDITION']['end_tag']
exts = config['CONDITION']['exts'].split(',')
tpl_dir = config['CONDITION']['template_dir']
real_dir = config['CONDITION']['real_dir']
################################################
try:
    l = open(log, 'r')
    err_dict = dict()
    mm_dict = dict()
    err_msg = ''

    for line in l:
        if begin_tag in line and end_tag in line:
            t_line = str(line)
            bt = t_line.find(begin_tag) + len(begin_tag)
            et = t_line.find(end_tag)
            tt = t_line.find('[error]')
            yt = t_line.find(' in /')
            ut = t_line.find('Undefined index:')
            md5_str = t_line[bt:et]
            uindex = t_line[ut+len('Undefined index:'):yt].strip()
            #print(uindex)
            err_msg = t_line[tt+len('[error]'):yt].strip() + ' [line ' + t_line[et+len(end_tag):].strip() + ']'
            if md5_str in list(mm_dict.keys()):
                mm_dict[md5_str]['err_msg'].add(err_msg)
                mm_dict[md5_str]['uindex'].add(uindex)
            else:
                mm_dict[md5_str] = {'err_msg':set([err_msg]), 'md5': md5_str, 'file':'', 'uindex': set([uindex])}
except:
    print('cannot open file:' + log)
################################################
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
################################################
ff = open('md5result.txt', mode='w')
ff.write('Total: ' + str(len(mm_dict.keys())) + ' file(s)\n')
ff.write('------------------------------------\n')
for m in list(mm_dict.keys()):
    ff.write("md5: " + m + "\nfile: " + mm_dict[m]['file'] + "\nuindex: " + ",".join(mm_dict[m]['uindex']) + "\n==Error Msg== \n" +  "\n".join(mm_dict[m]['err_msg']) + "\n-----------------------------\n")
ff.close()