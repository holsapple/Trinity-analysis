import re
from subprocess import Popen, PIPE


def call_process(command, new_dir=None):
    p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, cwd=new_dir)
    stdout, stderr = p.communicate()
    stdout = stdout.decode()
    return stdout


if __name__ == '__main__':
    subdirectory_list = ['pe_reads_01',
                         'pe_reads_02',
                         'pe_reads_03',
                         'pe_reads_04',
                         'pe_reads_05',
                         'pe_reads_06',
                         'pe_reads_07',
                         'pe_reads_08',
                         'pe_reads_09',
                         'pe_reads_10',
                         'pe_reads_11',
                         'pe_reads_12',
                         'pe_reads_13',
                         'pe_reads_14']
    for subdir in subdirectory_list:
        print('')
        print('Working in subdirectory {}'.format(subdir))

        call_process('touch tmp1.txt', subdir)
        call_process('touch tmp2.txt', subdir)

        print('Fixing headers for the forward reads')
        tmp1_file = open('{}/tmp1.txt'.format(subdir), 'w')
        with open('{}/subsamp-skewer-trimmed-pair1.fastq'.format(subdir), 'r') as f1:
            counter = 0
            for line in f1:
                if counter % 4 == 0:
                    # match = re.search('@.*\.\d* (.*)', line)
                    # new_header = match.group(1) + '\n'
                    new_header = '@' + line
                    tmp1_file.write(new_header)
                else:
                    tmp1_file.write(line)
                counter += 1
        tmp1_file.close()

        print('Fixing headers for the reverse reads')
        tmp2_file = open('{}/tmp2.txt'.format(subdir), 'w')
        with open('{}/subsamp-skewer-trimmed-pair2.fastq'.format(subdir), 'r') as f2:
            counter = 0
            for line in f2:
                if counter % 4 == 0:
                    # match = re.search('@.*\.\d* (.*)', line)
                    # new_header = match.group(1) + '\n'
                    new_header = '@' + line
                    tmp2_file.write(new_header)
                else:
                    tmp2_file.write(line)
                counter += 1
        tmp2_file.close()

        call_process('rm subsamp-skewer-trimmed-pair1.fastq subsamp-skewer-trimmed-pair2.fastq', subdir)
        call_process('mv tmp1.txt subsamp-skewer-trimmed-pair1.fastq', subdir)
        call_process('mv tmp2.txt subsamp-skewer-trimmed-pair2.fastq', subdir)
