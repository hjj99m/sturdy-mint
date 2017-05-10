import configparser
################################################
config = configparser.ConfigParser()
config.read('cond2.txt')

tags = config['CONDITION']['tags'].split(',')
rtags = config['CONDITION']['required_tags'].split(',')
target_file   = config['CONDITION']['target_file']
################################################
match = list()
nomatch = list()

try:
    f = open(target_file, 'r')
    for line in f:
        chk = True
        for r in rtags:
            if r not in line:
                chk = False

        if chk and any(tag in line for tag in tags):
            match.append(line)
        else:
            nomatch.append(line)
except:
    print('cannot open file:' + target_file)

################################################

ff = open(target_file + '.match.txt', mode='w')
for m in match:
    ff.write(str(m))

ff.close()

ff = open(target_file + '.nomatch.txt', mode='w')
for nm in nomatch:
    ff.write(str(nm))

ff.close()