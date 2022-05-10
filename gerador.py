import csv

with open('estoque_conf.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=',')
    for row in reader:
        produto = row['Produto']
        rep = row['Reposicao']
        ea = 0 if int(row['Estoque 03/05']) == 0 else int(row['Estoque 03/05']) - int(rep)
        vendas = row['Vendas']
        en = row['Estoque novo']

        print('Produto: {} \n Estoque 03/05: {} \n Reposicao: {} \n Vendas: {} \n Estoque novo: {} \n\n XXXX \n\n'.format(produto, int(row['Estoque 03/05']), rep, vendas, en))