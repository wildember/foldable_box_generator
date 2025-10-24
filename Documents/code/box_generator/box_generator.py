import tkinter as tk
from tkinter import ttk, filedialog
import drawsvg as draw
import math
import webbrowser

class InputGUI:
    labels = ['x', 'y', 'z']
    filename = ''

    def __init__(self, root, labels=labels):
        self.root = root
        self.root.title('Foldable box generator V1.0')
        self.root.resizable(False, False)
        row = 0

        for i in range(3):
            ttk.Label(root, text=f"{labels[i]}:").grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(root)
            entry.grid(row=i, column=1, columnspan=2, padx=5, pady=5)
            if i == 0:
                entry.focus()
            setattr(self, f'{labels[i]}', entry)
            ttk.Label(root, text='mm').grid(row=i, column=3, padx=5, pady=5)
            row = i

        row += 1

        ttk.Button(root, text='Save as', command=self.browse).grid(row=row, column=0, padx=5, pady=5)
        self.pathEntry = ttk.Entry(root, state='readonly')
        self.pathEntry.grid(row=row, column=1, columnspan=2, pady=5)
        row += 1

        showPerforation = ttk.Checkbutton(root, text='Dashed fold lines', variable=tk.IntVar(value=1))
        showPerforation.grid(row=row, column=0, columnspan=4, padx=5, pady=5)
        setattr(self, 'showPerforation', showPerforation)
        row += 1

        useColors = ttk.Checkbutton(root, text='Use different colors for fold and cut', variable=tk.IntVar(value=1))
        useColors.grid(row=row, column=0, columnspan=4, padx=5, pady=5)
        setattr(self, 'useColors', useColors)
        row += 1

        open = ttk.Checkbutton(root, text='Open result in browser', variable=tk.IntVar(value=0))
        open.grid(row=row, column=0, columnspan=4, padx=5, pady=5)
        setattr(self, 'open', open)
        row += 1

        self.resultMessage = tk.StringVar(value='')
        ttk.Label(self.root, textvariable=self.resultMessage).grid(row=row, column=0, columnspan=4, padx=5, pady=5)
        row += 1

        ttk.Button(root, text='Generate', command=self.get_values).grid(row=row, column=1, columnspan=1, pady=10, padx=5)
        ttk.Button(root, text='Close', command=exit).grid(row=row, column=2, columnspan=1)

    def showMessage(self, message):
        self.resultMessage.set(message)

    def browse(self):
            path = filedialog.asksaveasfilename(initialfile='box', defaultextension='.svg', filetypes=[('SVG files', '*.svg'), ('All files', '*.*')])
            setattr(self, 'path', path)
            self.pathEntry.config(state='normal')
            self.pathEntry.delete(0, tk.END)
            self.pathEntry.insert(0, path)

    def get_values(self, labels=labels):
        try:
            values = [int(getattr(self, f'{labels[i]}').get()) for i in range(3)]
            x = values[0]
            y = values[1]
            z = values[2]
            self.generate_svg(x, y, z)

        except ValueError:
            self.showMessage('Some of the entered values are not natural numbers')

    def generate_svg(self, x, y, z):
        path = getattr(self, 'path') if hasattr(self, 'path') else ''
        if path.rfind('.') == -1:
            self.showMessage('Please select a path to save the file')
            return

        useColors = 'selected' in getattr(self, 'useColors').state()
        showPerforation = 'selected' in getattr(self, 'showPerforation').state()
        open = 'selected' in getattr(self, 'open').state()
        foldColor = 'blue' if useColors else 'black';
        cutColor = 'red' if useColors else 'black';

        dashArray = '2,4' if showPerforation else '0';
        zFoldIncline = math.ceil(z / 4) if z > 2 else 0;
        yFoldIncline = math.ceil(y / 8) if y > 4 else 0;
        mainPaddingLeft = 2 * z
        mainPaddingRight = mainPaddingLeft + x
        innerWallFoldWidth = min(mainPaddingLeft, math.ceil(y / 3))
        fullHeight = (3 * z) + (2 * y)
        fullWidth = (4 * z) + x

        d = draw.Drawing(x + (4 * z), (2 * y) + (3 * z), origin=(0 , 0)) # foldable sides + closeable cap

        if showPerforation or useColors:
            d.append(draw.Lines(mainPaddingLeft, 0, mainPaddingLeft, fullHeight, close=False, stroke=foldColor, fill='none', stroke_dasharray=dashArray)) # big vertical 1
            d.append(draw.Lines(mainPaddingRight, 0, mainPaddingRight, fullHeight, close=False, stroke=foldColor, fill='none', stroke_dasharray=dashArray)) # big vertical 2
            d.append(draw.Lines(z, (2 * z) + y, z, 2 * (z + y), close=False, stroke=foldColor, fill='none', stroke_dasharray=dashArray)) # foldable wall 1
            d.append(draw.Lines((3 * z) + x, (2 * z) + y, (3 * z) + x, 2 * (z + y), close=False, stroke=foldColor, fill='none', stroke_dasharray=dashArray)) # foldable wall 2
            
            currentAppend = z
            totalAppend = currentAppend
            for i in range(4):
                d.append(draw.Lines(mainPaddingLeft, totalAppend, mainPaddingRight, totalAppend, close=False, stroke=foldColor, fill='none', stroke_dasharray=dashArray)) # inner horizontal fold
                currentAppend = y if currentAppend == z else z
                totalAppend += currentAppend
            
        d.append(draw.Lines(mainPaddingLeft, 0, mainPaddingRight, 0, close=False, stroke=cutColor, fill='none')) # general cap cut line
        d.append(draw.Lines(mainPaddingLeft, fullHeight, mainPaddingRight, fullHeight, close=False, stroke=cutColor, fill='none')) # general bottom cut line

        d.append(draw.Lines(mainPaddingLeft, (2 * z) + y, 0, mainPaddingLeft + y, 0, 2 * (z + y), mainPaddingLeft, 2 * (z + y), close=False, stroke=cutColor, fill='none')) # foldable narrow wall left
        d.append(draw.Lines(mainPaddingRight, (2 * z) + y, (4 * z) + x, mainPaddingLeft + y, (4 * z) + x, 2 * (z + y), mainPaddingRight, 2 * (z + y), close=False, stroke=cutColor, fill='none')) # foldable narrow wall right

        d.append(draw.Lines(mainPaddingLeft, 0, z, zFoldIncline, z, z - zFoldIncline, mainPaddingLeft, z, close=False, stroke=cutColor, fill='none')) # narrow foldable cap part 1
        d.append(draw.Lines(mainPaddingRight, 0, (3 * z) + x, zFoldIncline, (3 * z) + x, z - zFoldIncline, mainPaddingRight, z, close=False, stroke=cutColor, fill='none')) # narrow foldable cap part 2
        d.append(draw.Lines(mainPaddingLeft, z, z, z + yFoldIncline, z, z + y - yFoldIncline, mainPaddingLeft, z + y, close=False, stroke=cutColor, fill='none')) # wide foldable cap part 1
        d.append(draw.Lines(mainPaddingRight, z, (3 * z) + x, z + yFoldIncline, (3 * z) + x, z + y - yFoldIncline, mainPaddingRight, z + y, close=False, stroke=cutColor, fill='none')) # wide foldable cap part 2

        innerFoldLeft = z if mainPaddingLeft - innerWallFoldWidth < z else mainPaddingLeft
        innerFoldRight = mainPaddingRight + z if mainPaddingRight + innerWallFoldWidth > mainPaddingRight + z else mainPaddingRight
        d.append(draw.Lines(mainPaddingLeft, z + y, mainPaddingLeft - innerWallFoldWidth, z + y, mainPaddingLeft - innerWallFoldWidth, (2 * z) + y - zFoldIncline, innerFoldLeft, (2 * z) + y, mainPaddingLeft, mainPaddingLeft + y, close=False, stroke=cutColor, fill='none')) # wall inner fold left 1
        d.append(draw.Lines(mainPaddingRight, z + y, mainPaddingRight + innerWallFoldWidth, z + y, mainPaddingRight + innerWallFoldWidth, (2 * z) + y - zFoldIncline, innerFoldRight, (2 * z) + y, mainPaddingRight, (2 * z) + y, close=False, stroke=cutColor, fill='none')) # wall inner fold right 1
        d.append(draw.Lines(mainPaddingLeft, 2 * (z + y), innerFoldLeft, 2 * (z + y), mainPaddingLeft - innerWallFoldWidth, 2 * (z + y) + zFoldIncline, mainPaddingLeft - innerWallFoldWidth, fullHeight, mainPaddingLeft, fullHeight, close=False, stroke=cutColor, fill='none')) # wall inner fold left 2
        d.append(draw.Lines(mainPaddingRight, 2 * (z + y), innerFoldRight, 2 * (z + y), mainPaddingRight + innerWallFoldWidth, 2 * (z + y) + zFoldIncline, mainPaddingRight + innerWallFoldWidth, fullHeight, mainPaddingRight, fullHeight, close=False, stroke=cutColor, fill='none')) # wall inner fold right 2

        extensionIndex = path.rfind('.')
        dimensionPostfix = f'_{fullWidth}x{fullHeight}'
        path = path[:extensionIndex] + dimensionPostfix + path[extensionIndex:]
        d.save_svg(path)
        self.showMessage(f'Saved as {path}')

        if open:
            webbrowser.open(f'file://{path}')

if __name__ == '__main__':
    root = tk.Tk()
    app = InputGUI(root)
    root.mainloop()