import tkinter as tk

class SelectColumnsWindow(tk.Toplevel):
    def __init__(self, parent, columns, columns_per_row=4):
        super().__init__(parent)
        self.columns = columns
        self.selected_columns = []
        self.checkbuttons = {}
        self.columns_per_row = columns_per_row
        self.create_widgets()

    def create_widgets(self):
        self.title("Select Columns for Analysis")
        
        for idx, column in enumerate(self.columns):
            row = idx // self.columns_per_row
            col = idx % self.columns_per_row

            var = tk.BooleanVar()  # Create a BooleanVar to store the state of the checkbutton
            checkbutton = tk.Checkbutton(self, text=column, variable=var,
                                         command=lambda c=column, v=var: self.toggle_selection(c, v))
            checkbutton.grid(row=row, column=col, padx=5, pady=5)

            self.checkbuttons[column] = var

        # "Done" button under all checkbuttons, spanning all columns
        tk.Button(self, text="Done", command=self.on_done).grid(row=row + 1, column=0, columnspan=self.columns_per_row, pady=10)

    def toggle_selection(self, column, var):
        if var.get():
            if column not in self.selected_columns:
                self.selected_columns.append(column)
        else:
            if column in self.selected_columns:
                self.selected_columns.remove(column)

    def on_done(self):
        self.destroy()


