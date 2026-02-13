"""
Widget for displaying batch history and cure status.
"""

import base64
import io
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QTextDocument
from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Optional QR Code support
try:
    import qrcode

    _HAS_QRCODE = True
except ImportError:
    _HAS_QRCODE = False


# --- Dialogs ---


class BatchNotesDialog(QDialog):
    """Dialog for editing batch notes with a larger view"""

    def __init__(self, title, notes, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(500, 400)

        layout = QVBoxLayout()

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlainText(notes)
        layout.addWidget(self.notes_edit)

        btn_layout = QHBoxLayout()

        ts_btn = QPushButton("Add Timestamp")
        ts_btn.clicked.connect(self.add_timestamp)
        btn_layout.addWidget(ts_btn)

        btn_layout.addStretch()

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def add_timestamp(self):
        ts = datetime.now().strftime("[%Y-%m-%d %H:%M] ")
        self.notes_edit.append(ts)
        self.notes_edit.setFocus()

    def get_notes(self):
        return self.notes_edit.toPlainText()


# --- Main Widget ---


class BatchHistoryWidget(QWidget):
    def __init__(self, batch_manager):
        super().__init__()
        self.batch_manager = batch_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("<b>Production Log & Cure Tracker</b>"))
        header_layout.addStretch()

        edit_notes_btn = QPushButton("Edit Notes")
        edit_notes_btn.clicked.connect(self.open_notes_dialog)
        header_layout.addWidget(edit_notes_btn)

        print_btn = QPushButton("Print Bin Label")
        print_btn.clicked.connect(self.print_label)
        header_layout.addWidget(print_btn)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_table)
        header_layout.addWidget(refresh_btn)
        layout.addLayout(header_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Date Made", "Lot #", "Recipe", "Cure Date", "Status"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.doubleClicked.connect(self.open_notes_dialog)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.refresh_table()

    def refresh_table(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        batches = self.batch_manager.batches
        self.table.setRowCount(len(batches))

        today = datetime.now().strftime("%Y-%m-%d")

        for row, batch in enumerate(batches):
            # Make read-only columns
            for col, key in enumerate(["date_made", "lot_number", "recipe_name"]):
                item = QTableWidgetItem(batch.get(key, ""))
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col, item)

            cure_date = batch.get("cure_date", "")
            cure_item = QTableWidgetItem(cure_date)
            cure_item.setFlags(cure_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            # Highlight if ready
            if batch.get("status") == "Curing" and cure_date <= today:
                cure_item.setBackground(QColor("#e8f5e9"))  # Light green
                cure_item.setForeground(QColor("#2e7d32"))
            self.table.setItem(row, 3, cure_item)

            status_item = QTableWidgetItem(batch.get("status", "Curing"))
            status_item.setFlags(status_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 4, status_item)

            # Store ID in first item
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, batch.get("id"))
        self.table.blockSignals(False)

    def open_notes_dialog(self):
        """Open dialog to edit notes for selected batch"""
        row = self.table.currentRow()
        if row < 0:
            return

        batch_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        lot = self.table.item(row, 1).text()

        # Find batch data
        batch = next(
            (b for b in self.batch_manager.batches if b["id"] == batch_id), None
        )

        if batch:
            dialog = BatchNotesDialog(
                f"Notes for Lot {lot}", batch.get("notes", ""), self
            )
            if dialog.exec():
                new_notes = dialog.get_notes()
                self.batch_manager.update_notes(batch_id, new_notes)
                self.refresh_table()

    def show_context_menu(self, position):
        menu = QMenu()
        mark_ready = menu.addAction("Mark as Ready")
        mark_sold = menu.addAction("Mark as Sold Out")
        print_label = menu.addAction("Print Bin Label")
        menu.addSeparator()
        delete_action = menu.addAction("Delete Batch Log")

        action = menu.exec(self.table.viewport().mapToGlobal(position))

        row = self.table.currentRow()
        if row < 0:
            return

        item = self.table.item(row, 0)
        if not item:
            return
        batch_id = item.data(Qt.ItemDataRole.UserRole)

        if action == mark_ready:
            self.batch_manager.update_status(batch_id, "Ready")
            self.refresh_table()
        elif action == mark_sold:
            self.batch_manager.update_status(batch_id, "Sold Out")
            self.refresh_table()
        elif action == print_label:
            self.print_label()
        elif action == delete_action:
            confirm = QMessageBox.question(
                self,
                "Confirm",
                "Delete this batch record?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if confirm == QMessageBox.StandardButton.Yes:
                self.batch_manager.delete_batch(batch_id)
                self.refresh_table()

    def print_label(self):
        """Generate and print a bin label for the selected batch"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(
                self, "Select Batch", "Please select a batch to print a label for."
            )
            return

        batch_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        batch = next(
            (b for b in self.batch_manager.batches if b["id"] == batch_id), None
        )

        if not batch:
            return

        # Generate QR Code
        qr_html = ""
        if _HAS_QRCODE:
            try:
                # Create QR code instance
                qr = qrcode.QRCode(box_size=10, border=1)

                # Create rich data so scanning with a phone shows details
                # Start with a plain header to prevent "Recipe:" from being interpreted as a URL scheme
                qr_data = (
                    f"Batch Record\n"
                    f"Recipe: {batch.get('recipe_name', 'Unknown')}\n"
                    f"Lot: {batch.get('lot_number', '')}\n"
                    f"Made: {batch.get('date_made', '')}\n"
                    f"Ready: {batch.get('cure_date', '')}"
                )
                qr.add_data(qr_data)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")

                # Convert to base64 for HTML embedding
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                qr_b64 = base64.b64encode(buffer.getvalue()).decode()
                qr_html = f'<img src="data:image/png;base64,{qr_b64}" width="100" height="100">'
            except (ValueError, RuntimeError) as e:
                print(f"QR Generation failed: {e}")
                qr_html = "<div style='border:1px solid #ccc; width:100px; height:100px; text-align:center;'>No QR Lib</div>"
        else:
            qr_html = "<div style='font-size:12px; color:red; text-align:center; border:1px dashed red; padding:5px;'>QR Code requires<br>'pip install qrcode[pil]'</div>"

        # Label HTML Template
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: sans-serif; margin: 0; padding: 10px; }}
                .label-container {{
                    border: 2px solid #000;
                    padding: 15px;
                    width: 350px;
                    display: flex;
                    flex-direction: row;
                }}
                .info {{ float: left; width: 220px; }}
                .qr {{ float: right; width: 110px; text-align: center; }}
                h1 {{ font-size: 18px; margin: 0 0 5px 0; font-weight: bold; }}
                .lot {{ font-size: 14px; font-weight: bold; margin-bottom: 10px; }}
                .dates {{ font-size: 12px; line-height: 1.4; }}
                .status {{ margin-top: 10px; font-weight: bold; font-size: 14px; border: 1px solid #333; padding: 2px 5px; display: inline-block; }}
            </style>
        </head>
        <body>
            <div class="label-container">
                <div class="info">
                    <h1>{batch.get("recipe_name", "Unknown Recipe")}</h1>
                    <div class="lot">LOT: {batch.get("lot_number", "")}</div>
                    <div class="dates">
                        <b>Made:</b> {batch.get("date_made", "")}<br>
                        <b>Cure Ready:</b> {batch.get("cure_date", "")}
                    </div>
                    <div class="status">{batch.get("status", "").upper()}</div>
                </div>
                <div class="qr">
                    {qr_html}
                </div>
                <div style="clear:both;"></div>
            </div>
        </body>
        </html>
        """

        self._print_document(html)

    def _print_document(self, html):
        printer = QPrinter(QPrinter.PrinterMode.ScreenResolution)
        # Default to a label-ish size if possible, or let user choose in dialog
        # printer.setPageSize(QPageSize(QSizeF(100, 60), QPageSize.Unit.Millimeter))

        preview = QPrintPreviewDialog(printer, self)
        preview.setMinimumSize(800, 600)

        def handle_print(p):
            doc = QTextDocument()
            doc.setHtml(html)
            doc.print(p)

        preview.paintRequested.connect(handle_print)
        preview.exec()
