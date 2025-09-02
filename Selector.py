from aqt.qt import QDialog, QLabel, QHBoxLayout, QVBoxLayout, QCheckBox, QPushButton
from aqt import QScrollArea, QWidget, mw
from aqt.sound import play
import os

class Selector(QDialog):
    def __init__(self, audio_list=None, text_list=None, collection_audio_file_path=None, parent=None):
        super().__init__(parent or mw)
        self.setWindowTitle("Checkbox selection")
        self.setFixedWidth(500)

        # Main layout (contains the label and then the scroll area)
        self.main_layout = QVBoxLayout(self)
        
        # Instructions for user
        self.label = QLabel("Select all audio to add:")
        self.main_layout.addWidget(self.label)

        # Create a scrollable area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)
        self.main_layout.addWidget(self.scroll_area)
        self.setLayout(self.main_layout)

        # Creating list of horizontal row widgets to hold embeds and strings
        self.rows = []
        self.checkboxes = []
        self.text_list = text_list
        self.collection_audio_file_path = collection_audio_file_path
        for file_path, text in zip(audio_list, text_list):
            if file_path == "":  # don't create row for any audio not found
                continue
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)

            checkbox = QCheckBox(text)
            play_button = QPushButton("▶")

            play_button.clicked.connect(lambda _, p=file_path: play(p))

            row_layout.addWidget(checkbox)
            row_layout.addWidget(play_button)

            self.scroll_layout.addWidget(row_widget)
            self.checkboxes.append((checkbox, file_path))

        # Add the "Continue" button
        self.continue_btn = QPushButton("Continue")
        self.continue_btn.clicked.connect(self.on_continue)
        self.main_layout.addWidget(self.continue_btn)

    def on_continue(self):
        """Collect the selected checkbox contents when the button is clicked."""
        self.selected_items = [cb_tuple[0].text() for cb_tuple in self.checkboxes if cb_tuple[0].isChecked()]
        self.selected_items = []
        to_delete = []
        for i, cb_tuple in enumerate(self.checkboxes):
            if cb_tuple[0].isChecked():
                self.selected_items.append(cb_tuple[0].text())
            else:
                to_delete.append(self.collection_audio_file_path[i])

        for td in to_delete:
            if os.path.isfile(td):
                os.remove(td)

        self.accept()  # Close the dialog
        return self.selected_items

    def exec(self):
        """Override exec to return the list of selected items."""
        result = super().exec()  # This shows the dialog
        if self.selected_items:
            return self.selected_items
