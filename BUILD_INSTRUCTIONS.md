# Instruções para construir o executável

Para compilar a aplicação no Windows perfeitamente fechada em um executável (.exe) standalone com a biblioteca CustomTkinter, você precisa do pacote `pyinstaller`.

1. Ative seu ambiente virtual (se aplicável):
`.\.venv\Scripts\Activate.ps1`

2. Instale dependências para release com versões travadas:
`pip install -r requirements-lock.txt`

3. O projeto já possui o arquivo `build.spec` versionado para builds reproduzíveis.

4. Gere o executável com:
`pyinstaller build.spec`

O executável final estará dentro da nova pasta `dist/` com o nome `DolceNeves.exe`.

5. Validação recomendada após build em máquina limpa:
- Abrir `dist/DolceNeves.exe`
- Validar criação do `confeitaria.db` ao lado do executável
- Validar abertura do manual PDF em Configurações

- **Banco de Dados (Importante):** Graças à refatoração feita no `connection.py` com o `sys.frozen`, ao abrir o executável em qualquer lugar, o `confeitaria.db` será criado **ao lado** do executável (na mesma pasta de fora), permitindo acesso fácil pelo usuário para Backup ou deleção, sem ficar escondido na pasta temporária do MEIPASS.
