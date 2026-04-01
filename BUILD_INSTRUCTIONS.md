# Instruções para construir o executável

Para compilar a aplicação no Windows perfeitamente fechada em um executável (.exe) standalone com a biblioteca CustomTkinter, você precisa do pacote `pyinstaller`.

1. Ative seu ambiente virtual (se aplicável):
`.\.venv\Scripts\Activate.ps1`

2. Certifique-se de que o PyInstaller está instalado:
`pip install pyinstaller`

3. O comando mais fácil, utilizando o script SPEC gerado nesta raiz, é:
`pyinstaller build.spec`

O executável final estará dentro da nova pasta `dist/` com o nome `DolceNeves.exe`.

- **Banco de Dados (Importante):** Graças à refatoração feita no `connection.py` com o `sys.frozen`, ao abrir o executável em qualquer lugar, o `confeitaria.db` será criado **ao lado** do executável (na mesma pasta de fora), permitindo acesso fácil pelo usuário para Backup ou deleção, sem ficar escondido na pasta temporária do MEIPASS.
