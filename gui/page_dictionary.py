from add_words_dialog import AddWordsDialog
from db_manager import DatabaseManager
from db_query_thread import DatabaseQueryThread
from multiword_dialog import MultiWordDialog
from nosents_inclvl_dialog import IncreaseLvlsDialog
from PySide6.QtCore import QRect, Signal, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTableView,
    QVBoxLayout,
    QWidget,
)
from sents_table_model import SentenceTableModel
from word_scrape_thread import WordScraperThread
from word_table_model import WordTableModel


class PageDictionary(QWidget):
    md_multi_selection_sig = Signal(int)
    use_cpod_def_sig = Signal(bool)
    updated_sents_levels_sig = Signal(bool, list)

    def __init__(self):
        super().__init__()

        self.setObjectName("dictionary_page")
        with open("./gui/styles/main_screen_widget.css", "r") as ss:
            self.setStyleSheet(ss.read())
        self.label_6 = QLabel()
        self.label_6.setObjectName("label_6")
        self.label_6.setGeometry(QRect(280, 330, 221, 81))
        self.label_6.setText("words page")
        font1 = QFont()

        font1.setPointSize(25)
        self.label_6.setFont(font1)

        self.addwords_btn = QPushButton("Add words")

        self.dictionary_page_vlayout = QVBoxLayout(self)

        self.dictionary_page_vlayout.addWidget(self.label_6)

        self.horizontal_btn_layout = QHBoxLayout()
        self.words_table_btn = QPushButton("Words")
        self.words_table_btn.setObjectName("words_table_btn")
        self.sents_table_btn = QPushButton("Sents")
        self.sents_table_btn.setObjectName("sents_table_btn")
        self.horizontal_btn_layout.addWidget(self.words_table_btn)
        self.horizontal_btn_layout.addWidget(self.sents_table_btn)

        self.dictionary_page_vlayout.addLayout(self.horizontal_btn_layout)
        # Stacked Widget
        self.stacked_widget = QStackedWidget()

        # WordsTable
        self.words_table = QWidget()
        self.save_btn_words = QPushButton("Save Selected")
        self.select_all_w = QPushButton("Select All")
        self.words_table_vlayout = QVBoxLayout(self.words_table)
        self.words_table_vlayout.addWidget(self.save_btn_words)
        self.words_table_vlayout.addWidget(self.select_all_w)
        self.table_wordmodel = WordTableModel()
        self.table_view_w = QTableView()
        self.table_view_w.setSelectionBehavior(QTableView.SelectRows)
        self.table_view_w.setModel(self.table_wordmodel)
        self.table_view_w.show()
        self.words_table_vlayout.addWidget(self.table_view_w)
        self.stacked_widget.addWidget(self.words_table)

        # SentenceTable
        self.sents_table = QWidget()
        self.label = QLabel("dsd")
        self.save_btn_sents = QPushButton("Save Selected")
        self.select_all_s = QPushButton("Select All")

        self.sents_table_vlayout = QVBoxLayout(self.sents_table)
        self.sents_table_vlayout.addWidget(self.save_btn_sents)
        self.sents_table_vlayout.addWidget(self.select_all_s)
        self.table_sentmodel = SentenceTableModel()
        self.table_view_s = QTableView()
        self.table_view_s.setSelectionBehavior(QTableView.SelectRows)
        self.table_view_s.setModel(self.table_sentmodel)
        self.table_view_s.show()
        self.sents_table_vlayout.addWidget(self.label)
        self.sents_table_vlayout.addWidget(self.table_view_s)
        self.stacked_widget.addWidget(self.sents_table)

        self.dictionary_page_vlayout.addWidget(self.stacked_widget)

        self.stacked_widget.setCurrentIndex(0)

        self.words_table_btn.clicked.connect(self.change_table)
        self.sents_table_btn.clicked.connect(self.change_table)
        self.save_btn_words.clicked.connect(self.save_selected_words)
        self.save_btn_sents.clicked.connect(self.save_selected_sents)
        self.select_all_w.clicked.connect(self.select_all_words)
        self.select_all_s.clicked.connect(self.select_all_sents)

        self.db = DatabaseManager("chineseDict.db")
        self.get_page_words(1, 3)

    def select_all_words(self):
        self.table_view_w.selectAll()

    def select_all_sents(self):
        self.table_view_s.selectAll()

    def save_selected_words(self):
        selection_model = self.table_view_w.selectionModel()
        selected_rows = selection_model.selectedRows()
        words = [
            self.table_wordmodel.get_row_data(index.row()) for index in selected_rows
        ]
        self.save_selwords = DatabaseQueryThread(self.db, "insert_words", words=words)
        self.save_selwords.start()
        print(words)

    def save_selected_sents(self):
        selection_model = self.table_view_s.selectionModel()
        selected_rows = selection_model.selectedRows()
        print(selected_rows)

    def change_table(self):
        btn_name = self.sender().objectName()

        if btn_name == "words_table_btn":
            self.stacked_widget.setCurrentIndex(0)
        else:
            self.stacked_widget.setCurrentIndex(1)

    def get_page_words(self, page, limit):
        print("fn ran")
        self.threader = DatabaseQueryThread(
            self.db, "get_pagination_words", page=page, limit=limit
        )
        self.threader.start()
        self.threader.result_ready[object].connect(self.load_words_page)

    @Slot(object)
    def load_words_page(self, result):
        self.table_wordmodel.update_data(result)
        for item in result:
            print(item.id)