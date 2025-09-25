# Diretório de Uploads

Este diretório armazena todos os arquivos CSV enviados pelos usuários.

## Estrutura

Os arquivos são organizados por data de upload:
```
uploads/
├── 2024/
│   ├── 01/
│   │   ├── uuid_arquivo1.csv
│   │   └── uuid_arquivo2.csv
│   └── 02/
│       └── uuid_arquivo3.csv
└── 2025/
    └── 01/
        └── uuid_arquivo4.csv
```

## Segurança

- Arquivos são renomeados com UUID para evitar conflitos
- Apenas arquivos .csv são aceitos
- Tamanho máximo configurável (padrão: 20MB)
- Validação de nome de arquivo para segurança

## Limpeza

Para limpar arquivos órfãos (sem registro no banco):
1. Identifique arquivos sem referência na tabela `uploads`
2. Remova manualmente ou crie script de limpeza
3. **Cuidado**: Esta operação é irreversível

## Backup

Recomenda-se fazer backup regular deste diretório junto com o banco de dados.
