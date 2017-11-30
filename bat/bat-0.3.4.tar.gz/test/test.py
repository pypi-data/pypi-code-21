from bat import bro_log_reader

reader = bro_log_reader.BroLogReader('ssh.log')
for row in reader.readrows():
    print(row)
