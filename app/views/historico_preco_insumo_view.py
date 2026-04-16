import customtkinter as ctk
from tkinter import ttk
from datetime import datetime

from app.services.insumo_service import InsumoService


class HistoricoPrecoInsumoView(ctk.CTkToplevel):
	def __init__(self, master, service: InsumoService | None = None):
		super().__init__(master)
		self.title("Historico de Preco de Insumos")
		self.geometry("1080x640")
		self.minsize(920, 560)

		self.service = service or InsumoService()
		self.insumo_map: dict[int, str] = {}

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(2, weight=1)

		self._build_header()
		self._build_filtros()
		self._build_conteudo()

		self._carregar_filtro_insumos()
		self._carregar_historico()

		self.grab_set()

	def _build_header(self):
		header = ctk.CTkFrame(self)
		header.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

		titulo = ctk.CTkLabel(header, text="Historico de Preco de Insumos", font=("Roboto", 20, "bold"))
		titulo.pack(side="left", padx=12, pady=10)

		btn_fechar = ctk.CTkButton(header, text="Fechar", width=90, command=self.destroy)
		btn_fechar.pack(side="right", padx=12, pady=10)

	def _build_filtros(self):
		filtros = ctk.CTkFrame(self)
		filtros.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

		ctk.CTkLabel(filtros, text="Insumo:").pack(side="left", padx=(10, 6), pady=10)

		self.combo_insumo = ctk.CTkComboBox(filtros, values=["Todos"], width=320)
		self.combo_insumo.pack(side="left", padx=6, pady=10)
		self.combo_insumo.set("Todos")

		btn_aplicar = ctk.CTkButton(filtros, text="Aplicar", width=100, command=self._carregar_historico)
		btn_aplicar.pack(side="left", padx=(12, 6), pady=10)

	def _build_conteudo(self):
		conteudo = ctk.CTkFrame(self, fg_color="transparent")
		conteudo.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
		conteudo.grid_columnconfigure(0, weight=3)
		conteudo.grid_columnconfigure(1, weight=2)
		conteudo.grid_rowconfigure(0, weight=1)

		frame_tabela = ctk.CTkFrame(conteudo)
		frame_tabela.grid(row=0, column=0, padx=(0, 6), pady=0, sticky="nsew")

		style = ttk.Style()
		style.theme_use("default")
		style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=25, fieldbackground="#2b2b2b", borderwidth=0)
		style.map("Treeview", background=[("selected", "#1f538d")])
		style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")

		columns = ("data", "insumo", "preco_anterior", "preco_novo", "variacao", "observacao")
		self.tree = ttk.Treeview(frame_tabela, columns=columns, show="headings")

		self.tree.heading("data", text="Data/Hora")
		self.tree.heading("insumo", text="Insumo")
		self.tree.heading("preco_anterior", text="Preco Anterior")
		self.tree.heading("preco_novo", text="Preco Novo")
		self.tree.heading("variacao", text="Variacao")
		self.tree.heading("observacao", text="Observacao")

		self.tree.column("data", width=150, anchor="center")
		self.tree.column("insumo", width=190, anchor="w")
		self.tree.column("preco_anterior", width=120, anchor="e")
		self.tree.column("preco_novo", width=120, anchor="e")
		self.tree.column("variacao", width=90, anchor="center")
		self.tree.column("observacao", width=230, anchor="w")

		self.tree.pack(side="left", fill="both", expand=True)

		scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tree.yview)
		scrollbar.pack(side="right", fill="y")
		self.tree.configure(yscrollcommand=scrollbar.set)

		frame_timeline = ctk.CTkFrame(conteudo)
		frame_timeline.grid(row=0, column=1, padx=(6, 0), pady=0, sticky="nsew")
		frame_timeline.grid_rowconfigure(1, weight=1)
		frame_timeline.grid_columnconfigure(0, weight=1)

		ctk.CTkLabel(frame_timeline, text="Linha do Tempo", font=("Roboto", 16, "bold")).grid(
			row=0, column=0, padx=10, pady=(10, 6), sticky="w"
		)

		self.timeline_text = ctk.CTkTextbox(frame_timeline, wrap="word")
		self.timeline_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
		self.timeline_text.configure(state="disabled")

	def _carregar_filtro_insumos(self):
		self.insumo_map.clear()
		valores = ["Todos"]

		for insumo in self.service.listar():
			if insumo.id is None:
				continue
			label = f"{insumo.id} - {insumo.nome}"
			self.insumo_map[int(insumo.id)] = label
			valores.append(label)

		self.combo_insumo.configure(values=valores)
		self.combo_insumo.set("Todos")

	def _carregar_historico(self):
		for item in self.tree.get_children():
			self.tree.delete(item)

		insumo_id = self._insumo_id_filtro()
		historico = self.service.listar_historico_preco(insumo_id=insumo_id)

		for registro in historico:
			data_fmt = self._formatar_data_hora(registro.get("data_alteracao", ""))
			preco_anterior = float(registro.get("preco_anterior") or 0.0)
			preco_novo = float(registro.get("preco_novo") or 0.0)

			self.tree.insert(
				"",
				"end",
				values=(
					data_fmt,
					registro.get("insumo_nome", ""),
					self._formatar_moeda(preco_anterior),
					self._formatar_moeda(preco_novo),
					self._formatar_variacao(preco_anterior, preco_novo),
					registro.get("observacao") or "",
				),
			)

		self._render_linha_tempo(historico)

	def _render_linha_tempo(self, historico: list[dict]):
		linhas = []
		for registro in reversed(historico):
			data_fmt = self._formatar_data_hora(registro.get("data_alteracao", ""))
			nome = registro.get("insumo_nome", "Insumo")
			anterior = float(registro.get("preco_anterior") or 0.0)
			novo = float(registro.get("preco_novo") or 0.0)
			variacao = self._formatar_variacao(anterior, novo)

			linhas.append(
				f"{data_fmt} | {nome}: {self._formatar_moeda(anterior)} -> {self._formatar_moeda(novo)} ({variacao})"
			)

		if not linhas:
			linhas = ["Sem alteracoes de preco para o filtro selecionado."]

		self.timeline_text.configure(state="normal")
		self.timeline_text.delete("1.0", "end")
		self.timeline_text.insert("1.0", "\n\n".join(linhas))
		self.timeline_text.configure(state="disabled")

	def _insumo_id_filtro(self) -> int | None:
		selecionado = self.combo_insumo.get().strip()
		if selecionado == "Todos" or " - " not in selecionado:
			return None
		return int(selecionado.split(" - ", 1)[0])

	def _formatar_data_hora(self, valor: str) -> str:
		if not valor:
			return ""
		try:
			return datetime.strptime(valor, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
		except ValueError:
			return valor

	def _formatar_moeda(self, valor: float) -> str:
		return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

	def _formatar_variacao(self, anterior: float, novo: float) -> str:
		if anterior == 0:
			if novo == 0:
				return "0,00%"
			return "Novo"
		variacao = ((novo - anterior) / anterior) * 100
		return f"{variacao:+.2f}%".replace(".", ",")
