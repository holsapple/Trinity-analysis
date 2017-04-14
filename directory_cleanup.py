from subprocess import Popen, PIPE


def call_process(command, new_dir=None):
    p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, cwd=new_dir)
    stdout, stderr = p.communicate()
    stdout = stdout.decode()
    return stdout


if __name__ == '__main__':
    subdirectory_list = ['pe_reads_01', 'pe_reads_02', 'pe_reads_03', 'pe_reads_04', 'pe_reads_05', 'pe_reads_06', 'pe_reads_07',
                         'pe_reads_08', 'pe_reads_09', 'pe_reads_10', 'pe_reads_11', 'pe_reads_12', 'pe_reads_13', 'pe_reads_14']
    for subdir in subdirectory_list:
        call_process('rm analysis.done trinity.log', subdir)
        call_process('rm -rf trinity_assembly/', subdir)
