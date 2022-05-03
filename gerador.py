import csv

with open('estoque_conf.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=',')
    for row in reader:
        produto = row['Produto']
        rep = row['Reposicao']
        ea = int(row['Estoque antigo']) - int(rep)
        vendas = row['Vendas']
        en = row['Estoque novo']

        print('Produto: {} \n Estoque antigo: {} \n Reposicao: {} \n Vendas: {} \n Estoque novo: {} \n\n XXXX \n\n'.format(produto, ea, rep, vendas, en))