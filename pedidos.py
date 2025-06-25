from datetime import datetime
import pandas as pd
import os

# Cria a pasta 'dados' se não existir
if not os.path.exists('dados'):
    os.makedirs('dados')

# Lista para armazenar os pedidos
pedidos = []

print("==== 🛍️ SISTEMA DE PEDIDOS VIA WHATSAPP ====")

# Lista para armazenar os pedidos
pedidos = []

while True:
    nome = input("👤 Nome do cliente: ")

    produtos = input("📦 Produto (separe por vírgula se forem vários): ")
    produtos_lista = [p.strip() for p in produtos.split(',')]

    quantidades = input("🔢 Quantidade (na mesma ordem, separados por vírgula): ")
    quantidades_lista = [int(q.strip()) for q in quantidades.split(',')]

    if len(produtos_lista) != len(quantidades_lista):
        print("❌ A quantidade de produtos e de quantidades não bate. Tente novamente.")
        continue

    # Adiciona cada produto com sua quantidade
    for produto, quantidade in zip(produtos_lista, quantidades_lista):
        pedidos.append({
            'cliente': nome,
            'produto': produto,
            'quantidade': quantidade
        })

    mais = input("➕ Deseja adicionar outro pedido? (s/n): ").lower()
    if mais != 's':
        break

# Exibe os pedidos
print("\n🧾 Lista de Pedidos:")
for pedido in pedidos:
    print(f"Cliente: {pedido['cliente']} - Produto: {pedido['produto']} - Quantidade: {pedido['quantidade']}")
