import csv
f = open("output.csv", 'r', encoding='utf-8')
rdr = csv.reader(f)
vulnerabilities_list = list()
for line in rdr:
    vulnerabilities_list.append(line)
f.close()

vulnerabilities_dict_list = list()
for vulnerability_list in vulnerabilities_list:
    vulnerability_dict = dict()
    vulnerability_dict['name'] = vulnerability_list[0]
    vulnerability_dict['description'] = vulnerability_list[1]
    vulnerability_dict['severity'] = vulnerability_list[2]
    vulnerability_dict['message'] = vulnerability_list[3]
    vulnerability_dict['path'] = vulnerability_list[4]
    vulnerability_dict['start_line'] = int(vulnerability_list[5])
    vulnerability_dict['start_column'] = int(vulnerability_list[6])
    vulnerability_dict['end_line'] = int(vulnerability_list[7])
    vulnerability_dict['end_column'] = int(vulnerability_list[8])

    vulnerabilities_dict_list.append(vulnerability_dict)

print(vulnerabilities_dict_list)